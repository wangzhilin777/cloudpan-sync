from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

from .auth_store import get_profile


@dataclass
class BaiduNetdiskLiveResult:
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


BAIDU_XPAN_HOST = "https://pan.baidu.com"
BAIDU_XPAN_FILE_PATH = "/rest/2.0/xpan/file"


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_access_token(value: str) -> str:
    token = _text(value)
    if not token:
        return ""
    lowered = token.lower()
    if lowered.startswith("bearer "):
        return token[7:].strip()
    return token


def _normalize_dir_path(path: str) -> str:
    text = _text(path)
    if not text or text == "/":
        return "/"
    if not text.startswith("/"):
        text = f"/{text}"
    return text.rstrip("/") or "/"


def _join_path(parent: str, name: str) -> str:
    parent_dir = _normalize_dir_path(parent)
    child = _text(name).strip("/")
    if parent_dir == "/":
        return f"/{child}" if child else "/"
    return f"{parent_dir}/{child}" if child else parent_dir


def _load_profile_requirements(profile_id: str) -> tuple[object | None, str, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, "", ""
    extra = profile.extra or {}
    access_token = _normalize_access_token(profile.token or extra.get("authorization", "") or extra.get("access_token", ""))
    cookie = _text(profile.cookie or extra.get("cookie") or extra.get("cookie_header"))
    return profile, access_token, cookie


def _headers(cookie: str, form_body: bool = False) -> dict[str, str]:
    headers = {
        "User-Agent": "CloudPanSync/0.1",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://pan.baidu.com/",
        "Origin": "https://pan.baidu.com",
    }
    if cookie:
        headers["Cookie"] = cookie
    if form_body:
        headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
    return headers


def _request_json(method_name: str, params: dict[str, object], access_token: str, cookie: str) -> tuple[int, dict[str, object]]:
    query_params = {"method": method_name}
    if access_token:
        query_params["access_token"] = access_token
    query_params.update({k: v for k, v in params.items() if v is not None and _text(v) != ""})
    request = Request(
        url=f"{BAIDU_XPAN_HOST}{BAIDU_XPAN_FILE_PATH}?{urlencode(query_params)}",
        headers=_headers(cookie),
        method="GET",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _post_form(method_name: str, body: dict[str, object], access_token: str, cookie: str) -> tuple[int, dict[str, object]]:
    query_params = {"method": method_name}
    if access_token:
        query_params["access_token"] = access_token
    encoded_body = urlencode({k: v for k, v in body.items() if v is not None}).encode("utf-8")
    request = Request(
        url=f"{BAIDU_XPAN_HOST}{BAIDU_XPAN_FILE_PATH}?{urlencode(query_params)}",
        data=encoded_body,
        headers=_headers(cookie, form_body=True),
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _extract_list_items(payload: dict[str, object], parent_path: str) -> list[dict[str, object]]:
    items = payload.get("list")
    if not isinstance(items, list):
        return []
    rows: list[dict[str, object]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        path = _text(item.get("path"))
        name = _text(item.get("server_filename") or item.get("filename") or path.rsplit("/", 1)[-1])
        fsid = _text(item.get("fs_id") or item.get("fsid"))
        is_dir = int(item.get("isdir", 0) or 0) == 1
        md5 = _text(item.get("md5")).lower()
        rows.append(
            {
                "fileId": fsid,
                "parentId": parent_path,
                "name": name or fsid,
                "path": path or _join_path(parent_path, name or fsid),
                "type": "dir" if is_dir else "file",
                "isDir": is_dir,
                "size": int(item.get("size", 0) or 0),
                "md5": md5 if len(md5) == 32 else "",
                "etag": md5 if len(md5) == 32 else "",
                "gcid": "",
                "raw": item,
            }
        )
    return rows


def _normalize_metadata_entry(item: dict[str, object]) -> dict[str, object]:
    path = _text(item.get("path"))
    md5 = _text(item.get("md5")).lower()
    return {
        "path": path or _text(item.get("server_filename") or item.get("filename") or item.get("fs_id") or item.get("fsid")),
        "size": int(item.get("size", 0) or 0),
        "md5": md5 if len(md5) == 32 else "",
        "sha1": "",
        "sha256": "",
        "gcid": "",
        "etag": md5 if len(md5) == 32 else "",
        "raw": item,
    }


def fetch_baidu_live_list(profile_id: str, dir_path: str = "/", limit: int = 100) -> BaiduNetdiskLiveResult:
    profile, access_token, cookie = _load_profile_requirements(profile_id)
    if profile is None:
        return BaiduNetdiskLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved Baidu Netdisk auth profile was not found.", {})
    if not access_token and not cookie:
        return BaiduNetdiskLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_access", "Baidu Netdisk live list requires access token or cookie.", {})

    resolved_dir = _normalize_dir_path(dir_path or profile.extra.get("dir") or profile.extra.get("pathPrefix") or "/")
    params = {
        "dir": resolved_dir,
        "folder": "0",
        "order": "name",
        "desc": "0",
        "limit": f"0,{max(1, min(200, int(limit or 100)))}",
        "web": "1",
        "clienttype": "0",
    }
    try:
        status, payload = _request_json("list", params, access_token, cookie)
        return BaiduNetdiskLiveResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "Baidu Netdisk live list succeeded with saved access credentials.",
            {"items": _extract_list_items(payload, resolved_dir), "raw": payload, "dir": resolved_dir},
        )
    except HTTPError as exc:
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "Baidu Netdisk live list reached the API but was rejected.", {})
    except URLError as exc:
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "Baidu Netdisk live list could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "Baidu Netdisk live list returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "Baidu Netdisk live list failed unexpectedly.", {})


def fetch_baidu_live_metadata(profile_id: str, file_id: str = "", path: str = "") -> BaiduNetdiskLiveResult:
    profile, access_token, cookie = _load_profile_requirements(profile_id)
    if profile is None:
        return BaiduNetdiskLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved Baidu Netdisk auth profile was not found.", {})
    if not access_token and not cookie:
        return BaiduNetdiskLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_access", "Baidu Netdisk live metadata requires access token or cookie.", {})

    resolved_file_id = _text(file_id or profile.extra.get("fileId") or profile.extra.get("fsid"))
    resolved_path = _text(path or profile.extra.get("path"))
    if not resolved_file_id and not resolved_path:
        return BaiduNetdiskLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_file_selector", "Baidu Netdisk live metadata requires fileId or path.", {})

    params = {
        "dlink": "0",
        "thumb": "1",
        "web": "1",
        "clienttype": "0",
    }
    if resolved_file_id:
        params["fsids"] = json.dumps([int(resolved_file_id)], ensure_ascii=False)
    else:
        params["path"] = resolved_path
    try:
        status, payload = _request_json("filemetas", params, access_token, cookie)
        info = payload.get("info")
        item = info[0] if isinstance(info, list) and info and isinstance(info[0], dict) else None
        if item is None and resolved_path:
            list_result = fetch_baidu_live_list(profile.profileId, dir_path=_normalize_dir_path(resolved_path.rsplit("/", 1)[0] or "/"), limit=200)
            if not list_result.ok:
                return BaiduNetdiskLiveResult(False, list_result.mode, True, profile.profileId, list_result.status, list_result.error, f"Baidu Netdisk live metadata failed because parent listing did not succeed: {list_result.note}", list_result.payload)
            match = next((row for row in list_result.payload.get("items", []) if isinstance(row, dict) and _text(row.get("path")) == resolved_path), None)
            if match is None:
                return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, list_result.status, "metadata_not_found", "Baidu Netdisk live metadata did not find the file under the provided path.", list_result.payload)
            item = dict(match.get("raw") or {})
        if item is None:
            return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, status, "metadata_not_found", "Baidu Netdisk live metadata did not return a usable file entry.", {"raw": payload})
        return BaiduNetdiskLiveResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "Baidu Netdisk live metadata succeeded with saved access credentials.",
            {"entry": _normalize_metadata_entry(item), "raw": payload},
        )
    except HTTPError as exc:
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "Baidu Netdisk live metadata reached the API but was rejected.", {})
    except URLError as exc:
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "Baidu Netdisk live metadata could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "Baidu Netdisk live metadata returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "Baidu Netdisk live metadata failed unexpectedly.", {})


def fetch_baidu_create_dir(profile_id: str, parent_dir: str = "/", dir_name: str = "") -> BaiduNetdiskLiveResult:
    profile, access_token, cookie = _load_profile_requirements(profile_id)
    if profile is None:
        return BaiduNetdiskLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved Baidu Netdisk auth profile was not found.", {})
    if not access_token and not cookie:
        return BaiduNetdiskLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_access", "Baidu Netdisk create folder requires access token or cookie.", {})

    resolved_parent = _normalize_dir_path(parent_dir or profile.extra.get("dir") or profile.extra.get("pathPrefix") or "/")
    resolved_name = _text(dir_name)
    if not resolved_name:
        return BaiduNetdiskLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_dir_name", "Baidu Netdisk create folder requires dirName.", {})

    full_path = _join_path(resolved_parent, resolved_name)
    body = {
        "path": full_path,
        "isdir": "1",
        "size": "0",
        "block_list": quote("[]", safe="[]"),
        "rtype": "1",
        "web": "1",
        "clienttype": "0",
    }
    try:
        status, payload = _post_form("create", body, access_token, cookie)
        item = {
            "fileId": _text(payload.get("fs_id") or payload.get("fsid")),
            "parentId": resolved_parent,
            "name": resolved_name,
            "path": full_path,
            "type": "dir",
            "isDir": True,
            "size": 0,
            "raw": payload,
        }
        return BaiduNetdiskLiveResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "Baidu Netdisk live create folder succeeded with saved access credentials.",
            {"item": item, "raw": payload, "dir": resolved_parent},
        )
    except HTTPError as exc:
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "Baidu Netdisk create folder reached the API but was rejected.", {})
    except URLError as exc:
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "Baidu Netdisk create folder could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "Baidu Netdisk create folder returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return BaiduNetdiskLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "Baidu Netdisk create folder failed unexpectedly.", {})
