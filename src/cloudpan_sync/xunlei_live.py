from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .auth_store import get_profile


@dataclass
class XunleiLiveResult:
    ok: bool
    mode: str
    usedProfile: bool
    profileId: str
    status: int
    error: str
    note: str
    payload: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "mode": self.mode,
            "usedProfile": self.usedProfile,
            "profileId": self.profileId,
            "status": self.status,
            "error": self.error,
            "note": self.note,
            "payload": self.payload,
        }


XUNLEI_API_BASE = "https://api-pan.xunlei.com"
XUNLEI_CLIENT_ID = "Xqp0kJBXWhwaTpB6"


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _auth_header(value: str) -> str:
    token = _text(value)
    if not token:
        return ""
    return token if token.lower().startswith("bearer ") else f"Bearer {token}"


def _load_profile_requirements(profile_id: str) -> tuple[object | None, dict[str, str]]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, {}
    extra = profile.extra or {}
    headers = {
        "authorization": _auth_header(profile.token or extra.get("authorization", "")),
        "x-device-id": _text(extra.get("deviceId") or extra.get("device_id") or extra.get("x-device-id")),
        "x-captcha-token": _text(extra.get("captchaToken") or extra.get("captcha_token") or extra.get("x-captcha-token")),
        "x-client-id": _text(extra.get("clientId") or extra.get("client_id") or extra.get("x-client-id")) or XUNLEI_CLIENT_ID,
    }
    return profile, headers


def _request_headers(auth_headers: dict[str, str]) -> dict[str, str]:
    headers = {
        "User-Agent": "CloudPanSync/0.1",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://pan.xunlei.com/",
        "Content-Type": "application/json",
        "x-client-id": auth_headers.get("x-client-id") or XUNLEI_CLIENT_ID,
    }
    if auth_headers.get("authorization"):
        headers["Authorization"] = auth_headers["authorization"]
    if auth_headers.get("x-device-id"):
        headers["x-device-id"] = auth_headers["x-device-id"]
    if auth_headers.get("x-captcha-token"):
        headers["x-captcha-token"] = auth_headers["x-captcha-token"]
    return headers


def _get_json(path: str, params: dict[str, object], auth_headers: dict[str, str]) -> tuple[int, dict[str, object]]:
    query = urlencode({k: v for k, v in params.items() if v is not None})
    request = Request(
        url=f"{XUNLEI_API_BASE}{path}?{query}",
        headers=_request_headers(auth_headers),
        method="GET",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _post_json(path: str, body: dict[str, object], auth_headers: dict[str, str]) -> tuple[int, dict[str, object]]:
    request = Request(
        url=f"{XUNLEI_API_BASE}{path}",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=_request_headers(auth_headers),
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _normalize_xunlei_item(item: dict[str, object], parent_id: str) -> dict[str, object]:
    file_id = _text(item.get("id"))
    name = _text(item.get("name") or item.get("file_name"))
    kind = _text(item.get("kind")).lower()
    gcid = _text(item.get("hash") or item.get("gcid")).upper()
    return {
        "fileId": file_id,
        "parentId": _text(item.get("parent_id") or parent_id),
        "name": name or file_id,
        "path": name or file_id,
        "type": "dir" if kind == "drive#folder" else "file",
        "isDir": kind == "drive#folder",
        "size": int(item.get("size", 0) or 0),
        "gcid": gcid,
        "md5": "",
        "etag": "",
        "raw": item,
    }


def fetch_xunlei_live_list(profile_id: str, parent_id: str = "", limit: int = 100, page_token: str = "") -> XunleiLiveResult:
    profile, auth_headers = _load_profile_requirements(profile_id)
    if profile is None:
        return XunleiLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved Xunlei auth profile was not found.", {})
    if not auth_headers.get("authorization"):
        return XunleiLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_authorization", "Xunlei live list requires token or extra.authorization.", {})

    filters = json.dumps(
        {
            "phase": {"eq": "PHASE_TYPE_COMPLETE"},
            "trashed": {"eq": False},
        },
        ensure_ascii=False,
    )
    params = {
        "parent_id": _text(parent_id),
        "usage": "DISPLAY",
        "filters": filters,
        "with_audit": "true",
        "thumbnail_size": "SIZE_SMALL",
        "limit": max(1, min(100, int(limit or 100))),
        "page_token": _text(page_token),
    }
    try:
        status, payload = _get_json("/drive/v1/files", params, auth_headers)
        files = payload.get("files")
        rows = [_normalize_xunlei_item(item, _text(parent_id)) for item in files if isinstance(item, dict)] if isinstance(files, list) else []
        return XunleiLiveResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "Xunlei live list succeeded with saved auth headers.",
            {
                "items": rows,
                "raw": payload,
                "parentId": _text(parent_id),
                "nextPageToken": _text(payload.get("next_page_token")),
            },
        )
    except HTTPError as exc:
        return XunleiLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "Xunlei live list reached the API but was rejected.", {})
    except URLError as exc:
        return XunleiLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "Xunlei live list could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return XunleiLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "Xunlei live list returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return XunleiLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "Xunlei live list failed unexpectedly.", {})


def fetch_xunlei_live_metadata(profile_id: str, file_id: str, parent_id: str = "") -> XunleiLiveResult:
    profile, auth_headers = _load_profile_requirements(profile_id)
    if profile is None:
        return XunleiLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved Xunlei auth profile was not found.", {})
    if not auth_headers.get("authorization"):
        return XunleiLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_authorization", "Xunlei live metadata requires token or extra.authorization.", {})
    resolved_file_id = _text(file_id or profile.extra.get("fileId"))
    if not resolved_file_id:
        return XunleiLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_file_id", "Xunlei live metadata requires fileId.", {})

    list_result = fetch_xunlei_live_list(profile_id=profile.profileId, parent_id=parent_id, limit=100)
    if not list_result.ok:
        return XunleiLiveResult(
            False,
            list_result.mode,
            True,
            profile.profileId,
            list_result.status,
            list_result.error,
            f"Xunlei live metadata failed because parent directory listing did not succeed: {list_result.note}",
            list_result.payload,
        )
    items = list_result.payload.get("items")
    matched = next((item for item in items if isinstance(item, dict) and _text(item.get("fileId")) == resolved_file_id), None) if isinstance(items, list) else None
    if matched is None:
        return XunleiLiveResult(False, "live_error", True, profile.profileId, list_result.status, "metadata_not_found", "Xunlei live metadata did not find the file under the provided parentId page.", list_result.payload)

    entry = {
        "path": _text(matched.get("name") or resolved_file_id),
        "size": int(matched.get("size", 0) or 0),
        "md5": "",
        "sha1": "",
        "sha256": "",
        "gcid": _text(matched.get("gcid")).upper(),
        "etag": "",
        "raw": matched.get("raw") or matched,
    }
    return XunleiLiveResult(
        True,
        "live",
        True,
        profile.profileId,
        list_result.status,
        "",
        "Xunlei live metadata succeeded by locating the file in the current parent directory page.",
        {"entry": entry, "raw": list_result.payload.get("raw", {}), "parentId": _text(parent_id)},
    )


def fetch_xunlei_create_folder(profile_id: str, parent_id: str = "", dir_name: str = "") -> XunleiLiveResult:
    profile, auth_headers = _load_profile_requirements(profile_id)
    if profile is None:
        return XunleiLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved Xunlei auth profile was not found.", {})
    if not auth_headers.get("authorization"):
        return XunleiLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_authorization", "Xunlei create folder requires token or extra.authorization.", {})
    resolved_dir_name = _text(dir_name)
    if not resolved_dir_name:
        return XunleiLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_dir_name", "Xunlei create folder requires dirName.", {})

    body = {
        "kind": "drive#folder",
        "name": resolved_dir_name,
        "parent_id": _text(parent_id),
    }
    try:
        status, payload = _post_json("/drive/v1/files", body, auth_headers)
        item = _normalize_xunlei_item(payload if isinstance(payload, dict) else {}, _text(parent_id))
        return XunleiLiveResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "Xunlei live create folder succeeded with saved auth headers.",
            {"item": item, "raw": payload, "parentId": _text(parent_id)},
        )
    except HTTPError as exc:
        return XunleiLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "Xunlei create folder reached the API but was rejected.", {})
    except URLError as exc:
        return XunleiLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "Xunlei create folder could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return XunleiLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "Xunlei create folder returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return XunleiLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "Xunlei create folder failed unexpectedly.", {})
