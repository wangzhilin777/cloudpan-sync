from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .auth_store import get_profile


@dataclass
class PikPakLiveResult:
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


PIKPAK_API_BASE = "https://api-drive.mypikpak.com"


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
    }
    return profile, headers


def _request_headers(auth_headers: dict[str, str], json_body: bool = False) -> dict[str, str]:
    headers = {
        "User-Agent": "CloudPanSync/0.1",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://mypikpak.com/",
        "Origin": "https://mypikpak.com",
    }
    if auth_headers.get("authorization"):
        headers["Authorization"] = auth_headers["authorization"]
    if auth_headers.get("x-device-id"):
        headers["x-device-id"] = auth_headers["x-device-id"]
    if auth_headers.get("x-captcha-token"):
        headers["x-captcha-token"] = auth_headers["x-captcha-token"]
    if json_body:
        headers["Content-Type"] = "application/json;charset=utf-8"
    return headers


def _get_json(path: str, params: dict[str, object], auth_headers: dict[str, str]) -> tuple[int, dict[str, object]]:
    query = urlencode({k: v for k, v in params.items() if v is not None and _text(v) != ""})
    request = Request(
        url=f"{PIKPAK_API_BASE}{path}?{query}",
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
        url=f"{PIKPAK_API_BASE}{path}",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=_request_headers(auth_headers, json_body=True),
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _normalize_item(item: dict[str, object], parent_id: str) -> dict[str, object]:
    file_id = _text(item.get("id") or item.get("file_id") or item.get("fileId"))
    name = _text(item.get("name") or item.get("file_name"))
    kind = _text(item.get("kind")).lower()
    hash_value = _text(item.get("hash") or item.get("gcid")).upper()
    md5_value = hash_value if len(hash_value) == 32 else ""
    gcid_value = hash_value if len(hash_value) == 40 else ""
    return {
        "fileId": file_id,
        "parentId": _text(item.get("parent_id") or parent_id),
        "name": name or file_id,
        "path": name or file_id,
        "type": "dir" if kind == "drive#folder" else "file",
        "isDir": kind == "drive#folder",
        "size": int(item.get("size", 0) or 0),
        "md5": md5_value,
        "gcid": gcid_value,
        "etag": md5_value,
        "raw": item,
    }


def _normalize_metadata_entry(item: dict[str, object]) -> dict[str, object]:
    normalized = _normalize_item(item, _text(item.get("parent_id") or ""))
    return {
        "path": _text(normalized.get("path")),
        "size": int(normalized.get("size", 0) or 0),
        "md5": _text(normalized.get("md5")),
        "sha1": "",
        "sha256": "",
        "gcid": _text(normalized.get("gcid")),
        "etag": _text(normalized.get("etag")),
        "raw": normalized.get("raw") or item,
    }


def fetch_pikpak_live_list(profile_id: str, parent_id: str = "", limit: int = 100, page_token: str = "") -> PikPakLiveResult:
    profile, auth_headers = _load_profile_requirements(profile_id)
    if profile is None:
        return PikPakLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved PikPak auth profile was not found.", {})
    if not auth_headers.get("authorization"):
        return PikPakLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_authorization", "PikPak live list requires token or extra.authorization.", {})

    filters = json.dumps({"trashed": {"eq": False}}, ensure_ascii=False)
    params = {
        "parent_id": _text(parent_id),
        "with_audit": "true",
        "limit": max(1, min(100, int(limit or 100))),
        "page_token": _text(page_token),
        "filters": filters,
    }
    try:
        status, payload = _get_json("/drive/v1/files", params, auth_headers)
        files = payload.get("files")
        rows = [_normalize_item(item, _text(parent_id)) for item in files if isinstance(item, dict)] if isinstance(files, list) else []
        return PikPakLiveResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "PikPak live list succeeded with saved auth headers.",
            {"items": rows, "raw": payload, "parentId": _text(parent_id), "nextPageToken": _text(payload.get("next_page_token"))},
        )
    except HTTPError as exc:
        return PikPakLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "PikPak live list reached the API but was rejected.", {})
    except URLError as exc:
        return PikPakLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "PikPak live list could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return PikPakLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "PikPak live list returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return PikPakLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "PikPak live list failed unexpectedly.", {})


def fetch_pikpak_live_metadata(profile_id: str, file_id: str) -> PikPakLiveResult:
    profile, auth_headers = _load_profile_requirements(profile_id)
    if profile is None:
        return PikPakLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved PikPak auth profile was not found.", {})
    if not auth_headers.get("authorization"):
        return PikPakLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_authorization", "PikPak live metadata requires token or extra.authorization.", {})
    resolved_file_id = _text(file_id or profile.extra.get("fileId"))
    if not resolved_file_id:
        return PikPakLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_file_id", "PikPak live metadata requires fileId.", {})

    try:
        status, payload = _get_json(f"/drive/v1/files/{resolved_file_id}", {"thumbnail_size": "SIZE_MEDIUM"}, auth_headers)
        return PikPakLiveResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "PikPak live metadata succeeded with saved auth headers.",
            {"entry": _normalize_metadata_entry(payload), "raw": payload},
        )
    except HTTPError as exc:
        return PikPakLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "PikPak live metadata reached the API but was rejected.", {})
    except URLError as exc:
        return PikPakLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "PikPak live metadata could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return PikPakLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "PikPak live metadata returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return PikPakLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "PikPak live metadata failed unexpectedly.", {})


def fetch_pikpak_create_folder(profile_id: str, parent_id: str, dir_name: str) -> PikPakLiveResult:
    profile, auth_headers = _load_profile_requirements(profile_id)
    if profile is None:
        return PikPakLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved PikPak auth profile was not found.", {})
    if not auth_headers.get("authorization"):
        return PikPakLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_authorization", "PikPak create folder requires token or extra.authorization.", {})

    resolved_parent_id = _text(parent_id or profile.extra.get("parentId"))
    resolved_dir_name = _text(dir_name)
    if not resolved_dir_name:
        return PikPakLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_dir_name", "PikPak create folder requires dirName.", {})

    body = {
        "kind": "drive#folder",
        "name": resolved_dir_name,
        "parent_id": resolved_parent_id,
    }
    try:
        status, payload = _post_json("/drive/v1/files", body, auth_headers)
        item = _normalize_item(payload, resolved_parent_id)
        return PikPakLiveResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "PikPak live create folder succeeded with saved auth headers.",
            {"item": item, "raw": payload, "parentId": resolved_parent_id},
        )
    except HTTPError as exc:
        return PikPakLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "PikPak create folder reached the API but was rejected.", {})
    except URLError as exc:
        return PikPakLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "PikPak create folder could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return PikPakLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "PikPak create folder returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return PikPakLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "PikPak create folder failed unexpectedly.", {})
