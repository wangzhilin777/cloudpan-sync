from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .auth_store import get_profile


@dataclass
class Pan123OpenResult:
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


PAN123_OPEN_HOST = "https://open-api.123pan.com"
PAN123_OPEN_LIST_PATH = "/api/v2/file/list"
PAN123_OPEN_MKDIR_PATH = "/upload/v1/file/mkdir"


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _auth_header(value: str) -> str:
    token = _text(value)
    if not token:
        return ""
    return token if token.lower().startswith("bearer ") else f"Bearer {token}"


def _load_profile_requirements(profile_id: str) -> tuple[object | None, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, ""
    auth = _auth_header(profile.token or profile.extra.get("authorization", ""))
    return profile, auth


def _headers(auth: str) -> dict[str, str]:
    return {
        "User-Agent": "CloudPanSync/0.1",
        "Accept": "application/json",
        "Authorization": auth,
        "Platform": "open_platform",
    }


def _get_json(path: str, params: dict[str, object], auth: str) -> tuple[int, dict[str, object]]:
    query = urlencode({k: v for k, v in params.items() if v is not None})
    request = Request(
        url=f"{PAN123_OPEN_HOST}{path}?{query}",
        headers=_headers(auth),
        method="GET",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _post_json(path: str, body: dict[str, object], auth: str) -> tuple[int, dict[str, object]]:
    request = Request(
        url=f"{PAN123_OPEN_HOST}{path}",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={**_headers(auth), "Content-Type": "application/json;charset=UTF-8"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _normalize_file_list(payload: dict[str, object]) -> list[dict[str, object]]:
    data = payload.get("data")
    if not isinstance(data, dict):
        return []
    file_list = data.get("fileList")
    if not isinstance(file_list, list):
        return []
    rows: list[dict[str, object]] = []
    for item in file_list:
        if not isinstance(item, dict):
            continue
        file_id = _text(item.get("fileId") or item.get("fileID"))
        name = _text(item.get("filename") or item.get("fileName") or item.get("name"))
        if not file_id or not name:
            continue
        item_type = int(item.get("type", 0) or 0)
        rows.append(
            {
                "fileId": file_id,
                "parentId": _text(item.get("parentFileId") or item.get("parentFileID") or "0"),
                "name": name,
                "path": name,
                "type": "folder" if item_type == 1 else "file",
                "isDir": item_type == 1,
                "size": int(item.get("size", 0) or 0),
                "md5": _text(item.get("etag")),
                "etag": _text(item.get("etag")),
                "raw": item,
            }
        )
    return rows


def _normalize_metadata_entry(item: dict[str, object]) -> dict[str, object]:
    file_id = _text(item.get("fileId") or item.get("fileID"))
    name = _text(item.get("filename") or item.get("fileName") or item.get("name"))
    item_type = int(item.get("type", 0) or 0)
    return {
        "path": name or file_id,
        "size": int(item.get("size", 0) or 0),
        "md5": _text(item.get("etag")),
        "sha1": "",
        "sha256": "",
        "gcid": "",
        "etag": _text(item.get("etag")),
        "raw": {
            "fileId": file_id,
            "name": name,
            "type": item_type,
            "parentFileId": _text(item.get("parentFileId") or item.get("parentFileID") or "0"),
            "status": item.get("status", 0),
        },
    }


def fetch_123_open_live_list(profile_id: str, parent_file_id: str = "0", limit: int = 100, last_file_id: int = 0) -> Pan123OpenResult:
    profile, auth = _load_profile_requirements(profile_id)
    if profile is None:
        return Pan123OpenResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved 123Pan Open auth profile was not found.", {})
    if not auth:
        return Pan123OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_access_token", "123Pan Open live list requires token or extra.authorization.", {})

    params = {
        "parentFileId": int(_text(parent_file_id) or "0"),
        "limit": max(1, min(100, int(limit or 100))),
        "lastFileId": int(last_file_id or 0),
    }
    try:
        status, payload = _get_json(PAN123_OPEN_LIST_PATH, params, auth)
        return Pan123OpenResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "123Pan Open live list succeeded with saved access token.",
            {"items": _normalize_file_list(payload), "raw": payload, "parentFileId": str(params["parentFileId"])},
        )
    except HTTPError as exc:
        return Pan123OpenResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "123Pan Open live list reached the API but was rejected.", {})
    except URLError as exc:
        return Pan123OpenResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "123Pan Open live list could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return Pan123OpenResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "123Pan Open live list returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return Pan123OpenResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "123Pan Open live list failed unexpectedly.", {})


def fetch_123_open_live_metadata(profile_id: str, file_id: str, parent_file_id: str = "0") -> Pan123OpenResult:
    profile, auth = _load_profile_requirements(profile_id)
    if profile is None:
        return Pan123OpenResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved 123Pan Open auth profile was not found.", {})
    if not auth:
        return Pan123OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_access_token", "123Pan Open live metadata requires token or extra.authorization.", {})

    resolved_file_id = _text(file_id or profile.extra.get("fileId"))
    resolved_parent_id = _text(parent_file_id or profile.extra.get("parentFileId") or profile.extra.get("parentId") or "0")
    if not resolved_file_id:
        return Pan123OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_file_id", "123Pan Open live metadata requires fileId.", {})

    try:
        status, payload = _get_json(
            PAN123_OPEN_LIST_PATH,
            {
                "parentFileId": int(resolved_parent_id or "0"),
                "limit": 100,
                "lastFileId": 0,
            },
            auth,
        )
        items = _normalize_file_list(payload)
        matched = next((item for item in items if _text(item.get("fileId")) == resolved_file_id), None)
        if matched is None:
            return Pan123OpenResult(False, "live_error", True, profile.profileId, status, "metadata_not_found", "123Pan Open metadata probe did not find the file under the provided parentFileId.", {"items": items, "parentFileId": resolved_parent_id})
        return Pan123OpenResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "123Pan Open live metadata succeeded by locating the file in the current parent directory page.",
            {"entry": _normalize_metadata_entry(dict(matched.get("raw") or {})), "raw": payload, "parentFileId": resolved_parent_id},
        )
    except HTTPError as exc:
        return Pan123OpenResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "123Pan Open live metadata reached the API but was rejected.", {})
    except URLError as exc:
        return Pan123OpenResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "123Pan Open live metadata could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return Pan123OpenResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "123Pan Open live metadata returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return Pan123OpenResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "123Pan Open live metadata failed unexpectedly.", {})


def fetch_123_open_create_folder(profile_id: str, parent_file_id: str, dir_name: str) -> Pan123OpenResult:
    profile, auth = _load_profile_requirements(profile_id)
    if profile is None:
        return Pan123OpenResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved 123Pan Open auth profile was not found.", {})
    if not auth:
        return Pan123OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_access_token", "123Pan Open create folder requires token or extra.authorization.", {})

    resolved_parent_id = _text(parent_file_id or profile.extra.get("parentFileId") or profile.extra.get("parentId") or "0")
    resolved_dir_name = _text(dir_name)
    if not resolved_dir_name:
        return Pan123OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_dir_name", "123Pan Open create folder requires dirName.", {})

    body = {
        "name": resolved_dir_name,
        "parentID": int(resolved_parent_id or "0"),
    }
    try:
        status, payload = _post_json(PAN123_OPEN_MKDIR_PATH, body, auth)
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        item = {
            "fileId": _text((data or {}).get("dirID")),
            "parentId": resolved_parent_id,
            "name": resolved_dir_name,
            "path": resolved_dir_name,
            "type": "folder",
            "isDir": True,
            "size": 0,
            "raw": payload,
        }
        return Pan123OpenResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "123Pan Open live create folder succeeded with saved access token.",
            {"item": item, "raw": payload, "parentFileId": resolved_parent_id},
        )
    except HTTPError as exc:
        return Pan123OpenResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "123Pan Open create folder reached the API but was rejected.", {})
    except URLError as exc:
        return Pan123OpenResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "123Pan Open create folder could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return Pan123OpenResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "123Pan Open create folder returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return Pan123OpenResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "123Pan Open create folder failed unexpectedly.", {})
