from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .auth_store import get_profile


@dataclass
class Pan115OpenResult:
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


PAN115_LIST_URL = "https://webapi.115.com/files"
PAN115_INFO_URL = "https://webapi.115.com/files/get_info"
PAN115_MKDIR_URL = "https://webapi.115.com/files/add"


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _cookie_header(profile: object) -> str:
    cookie = _text(getattr(profile, "cookie", ""))
    if cookie:
        return cookie
    extra = getattr(profile, "extra", {}) or {}
    return _text(extra.get("cookie") or extra.get("cookie_header"))


def _load_profile_requirements(profile_id: str) -> tuple[object | None, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, ""
    return profile, _cookie_header(profile)


def _headers(cookie: str) -> dict[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 115Browser/27.0.5.7",
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://115.com/",
    }
    if cookie:
        headers["Cookie"] = cookie
    return headers


def _get_json(url: str, params: dict[str, object], cookie: str) -> tuple[int, dict[str, object]]:
    query = urlencode({k: v for k, v in params.items() if v is not None})
    request = Request(
        url=f"{url}?{query}",
        headers=_headers(cookie),
        method="GET",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _post_form(url: str, form: dict[str, object], cookie: str) -> tuple[int, dict[str, object]]:
    request = Request(
        url=url,
        data=urlencode({k: v for k, v in form.items() if v is not None}).encode("utf-8"),
        headers={
            **_headers(cookie),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _pick_bool(item: dict[str, object], *keys: str) -> bool:
    for key in keys:
        if key in item:
            value = item.get(key)
            if isinstance(value, bool):
                return value
            text = _text(value).lower()
            if text in {"1", "true", "dir", "folder"}:
                return True
    return False


def _pick_file_list(payload: dict[str, object]) -> list[dict[str, object]]:
    for key in ("data", "files", "list"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("data", "list", "files"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _normalize_file_item(item: dict[str, object]) -> dict[str, object]:
    file_id = _text(item.get("fid") or item.get("file_id") or item.get("fileId") or item.get("cid") or item.get("id"))
    parent_id = _text(item.get("cid") or item.get("pid") or item.get("parent_id") or item.get("parentId") or "0")
    name = _text(item.get("n") or item.get("file_name") or item.get("name"))
    is_dir = _pick_bool(item, "is_dir", "isfolder", "isFolder") or bool(_text(item.get("cid")) and not _text(item.get("fid")))
    sha1 = _text(item.get("sha") or item.get("sha1"))
    return {
        "fileId": file_id,
        "parentId": parent_id,
        "name": name or file_id,
        "path": name or file_id,
        "type": "dir" if is_dir else "file",
        "isDir": is_dir,
        "size": int(item.get("s", 0) or item.get("size", 0) or 0),
        "sha1": sha1,
        "md5": "",
        "etag": _text(item.get("pc") or item.get("pick_code")),
        "pickcode": _text(item.get("pc") or item.get("pick_code")),
        "raw": item,
    }


def fetch_115_open_live_list(profile_id: str, cid: str = "0", limit: int = 100, offset: int = 0) -> Pan115OpenResult:
    profile, cookie = _load_profile_requirements(profile_id)
    if profile is None:
        return Pan115OpenResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved 115 auth profile was not found.", {})
    if not cookie:
        return Pan115OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_cookie", "115 live list requires cookie or extra.cookie_header.", {})

    params = {
        "aid": 1,
        "cid": int(_text(cid) or "0"),
        "offset": max(0, int(offset or 0)),
        "limit": max(1, min(1150, int(limit or 100))),
        "show_dir": 1,
        "format": "json",
        "natsort": 1,
    }
    try:
        status, payload = _get_json(PAN115_LIST_URL, params, cookie)
        items = [_normalize_file_item(item) for item in _pick_file_list(payload)]
        return Pan115OpenResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "115 live list succeeded with saved cookie.",
            {"items": items, "raw": payload, "cid": str(params["cid"])},
        )
    except HTTPError as exc:
        return Pan115OpenResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "115 live list reached the API but was rejected.", {})
    except URLError as exc:
        return Pan115OpenResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "115 live list could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return Pan115OpenResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "115 live list returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return Pan115OpenResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "115 live list failed unexpectedly.", {})


def fetch_115_open_live_metadata(profile_id: str, file_id: str) -> Pan115OpenResult:
    profile, cookie = _load_profile_requirements(profile_id)
    if profile is None:
        return Pan115OpenResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved 115 auth profile was not found.", {})
    if not cookie:
        return Pan115OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_cookie", "115 live metadata requires cookie or extra.cookie_header.", {})
    resolved_file_id = _text(file_id or profile.extra.get("fileId"))
    if not resolved_file_id:
        return Pan115OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_file_id", "115 live metadata requires fileId.", {})

    try:
        status, payload = _get_json(PAN115_INFO_URL, {"file_id": resolved_file_id}, cookie)
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        if not isinstance(data, dict):
            return Pan115OpenResult(False, "live_error", True, profile.profileId, status, "metadata_invalid", "115 live metadata returned an unexpected payload.", {"raw": payload})
        entry = _normalize_file_item(data)
        normalized = {
            "path": _text(data.get("n") or data.get("file_name") or data.get("name")) or resolved_file_id,
            "size": int(data.get("s", 0) or data.get("size", 0) or 0),
            "md5": "",
            "sha1": _text(data.get("sha") or data.get("sha1")),
            "sha256": "",
            "gcid": "",
            "etag": _text(data.get("pc") or data.get("pick_code")),
            "raw": entry.get("raw", data),
        }
        return Pan115OpenResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "115 live metadata succeeded with saved cookie.",
            {"entry": normalized, "raw": payload},
        )
    except HTTPError as exc:
        return Pan115OpenResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "115 live metadata reached the API but was rejected.", {})
    except URLError as exc:
        return Pan115OpenResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "115 live metadata could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return Pan115OpenResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "115 live metadata returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return Pan115OpenResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "115 live metadata failed unexpectedly.", {})


def fetch_115_open_create_folder(profile_id: str, parent_id: str, dir_name: str) -> Pan115OpenResult:
    profile, cookie = _load_profile_requirements(profile_id)
    if profile is None:
        return Pan115OpenResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved 115 auth profile was not found.", {})
    if not cookie:
        return Pan115OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_cookie", "115 create folder requires cookie or extra.cookie_header.", {})
    resolved_parent_id = _text(parent_id or profile.extra.get("parentId") or profile.extra.get("cid") or "0")
    resolved_dir_name = _text(dir_name)
    if not resolved_dir_name:
        return Pan115OpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_dir_name", "115 create folder requires dirName.", {})

    try:
        status, payload = _post_form(
            PAN115_MKDIR_URL,
            {
                "cname": resolved_dir_name,
                "pid": resolved_parent_id or "0",
            },
            cookie,
        )
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        item = {
            "fileId": _text((data or {}).get("cid") or (data or {}).get("file_id") or (data or {}).get("id")),
            "parentId": resolved_parent_id,
            "name": resolved_dir_name,
            "path": resolved_dir_name,
            "type": "dir",
            "isDir": True,
            "size": 0,
            "raw": payload,
        }
        return Pan115OpenResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "115 create folder succeeded with saved cookie.",
            {"item": item, "raw": payload, "parentId": resolved_parent_id},
        )
    except HTTPError as exc:
        return Pan115OpenResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "115 create folder reached the API but was rejected.", {})
    except URLError as exc:
        return Pan115OpenResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "115 create folder could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return Pan115OpenResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "115 create folder returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return Pan115OpenResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "115 create folder failed unexpectedly.", {})
