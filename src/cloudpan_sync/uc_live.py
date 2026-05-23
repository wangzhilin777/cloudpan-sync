from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .auth_store import get_profile


@dataclass
class UcLiveResult:
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


UC_API_BASE = "https://pc-api.uc.cn"
UC_PC_USER_AGENT = "Mozilla/5.0 UcCloudDrivePC/1.0"
UC_REFERER = "https://drive.uc.cn/"
UC_ORIGIN = "https://drive.uc.cn"


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _headers(cookie: str, json_body: bool = True) -> dict[str, str]:
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": UC_REFERER,
        "Origin": UC_ORIGIN,
        "User-Agent": UC_PC_USER_AGENT,
    }
    if json_body:
        headers["Content-Type"] = "application/json;charset=utf-8"
    if cookie:
        headers["Cookie"] = cookie
    return headers


def _load_profile_requirements(profile_id: str) -> tuple[object | None, str, str, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, "", "", ""
    extra = profile.extra or {}
    cookie = _text(profile.cookie or extra.get("cookie") or extra.get("cookie_header"))
    pwd_id = _text(extra.get("pwdId") or extra.get("sharePwdId") or extra.get("share_id"))
    passcode = _text(extra.get("passcode") or extra.get("accessCode") or extra.get("share_passcode"))
    return profile, cookie, pwd_id, passcode


def _request_json(url: str, method: str, headers: dict[str, str], body: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
    request = Request(
        url=url,
        data=None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method=method.upper(),
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _is_success(payload: dict[str, object]) -> bool:
    if not payload:
        return False
    code = payload.get("code")
    status = payload.get("status")
    if code in (0, "0", 200, "200"):
        return True
    if status in (0, "0", 200, "200"):
        return True
    return False


def _extract_stoken(payload: dict[str, object]) -> str:
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("stoken", "share_token", "shareToken", "token"):
            value = _text(data.get(key))
            if value:
                return value
    for key in ("stoken", "share_token", "shareToken", "token"):
        value = _text(payload.get(key))
        if value:
            return value
    return ""


def _get_share_token(pwd_id: str, passcode: str, cookie: str) -> tuple[int, dict[str, object], str]:
    status, payload = _request_json(
        f"{UC_API_BASE}/1/clouddrive/share/sharepage/token",
        "POST",
        _headers(cookie),
        {"pwd_id": pwd_id, "passcode": passcode or ""},
    )
    return status, payload, _extract_stoken(payload)


def _build_detail_url(pwd_id: str, stoken: str, pdir_fid: str, page: int, size: int) -> str:
    params = {
        "pwd_id": pwd_id,
        "stoken": stoken,
        "pdir_fid": pdir_fid or "0",
        "force": 0,
        "_page": page,
        "_size": size,
        "_fetch_banner": 0,
        "_fetch_share": 0,
        "_fetch_total": 1,
        "sort": "file_type:asc,file_name:asc",
        "pr": "ucpro",
        "fr": "pc",
    }
    return f"{UC_API_BASE}/1/clouddrive/share/sharepage/detail?{urlencode(params)}"


def _build_drive_file_url() -> str:
    return f"{UC_API_BASE}/1/clouddrive/file?{urlencode({'pr': 'ucpro', 'fr': 'pc', 'uc_param_str': ''})}"


def _extract_list(payload: dict[str, object]) -> list[dict[str, object]]:
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("list", "file_list", "fileList", "items", "records"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    for key in ("list", "file_list", "fileList", "items", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _extract_total(payload: dict[str, object]) -> int:
    data = payload.get("data")
    candidates: list[object] = []
    if isinstance(data, dict):
        candidates.extend([data.get("total"), data.get("totalCount"), data.get("total_count"), data.get("count")])
    candidates.extend([payload.get("total"), payload.get("totalCount"), payload.get("total_count"), payload.get("count")])
    for value in candidates:
        text = _text(value)
        if text.isdigit():
            return int(text)
    return 0


def _item_name(item: dict[str, object]) -> str:
    for key in ("file_name", "fileName", "name", "title", "server_filename", "filename"):
        value = _text(item.get(key))
        if value:
            return value
    return ""


def _item_fid(item: dict[str, object]) -> str:
    for key in ("fid", "file_id", "fileId", "share_fid", "shareFileId", "id"):
        value = _text(item.get(key))
        if value:
            return value
    return ""


def _item_fid_token(item: dict[str, object]) -> str:
    for key in ("share_fid_token", "fid_token", "fidToken", "file_token", "fileToken", "token"):
        value = _text(item.get(key))
        if value:
            return value
    return ""


def _item_size(item: dict[str, object]) -> int:
    for key in ("size", "file_size", "fileSize", "bytes"):
        value = item.get(key)
        try:
            return int(value or 0)
        except Exception:
            continue
    return 0


def _is_dir(item: dict[str, object]) -> bool:
    for key in ("dir", "isdir", "is_dir", "isDir", "folder", "is_folder", "isFolder"):
        value = item.get(key)
        if isinstance(value, bool):
            return value
        text = _text(value).lower()
        if text in {"1", "true"}:
            return True
        if text in {"0", "false"}:
            return False
    type_text = _text(item.get("type") or item.get("kind") or item.get("file_type") or item.get("fileType") or item.get("obj_category") or item.get("category")).lower()
    if any(flag in type_text for flag in ("dir", "folder", "directory")):
        return True
    if any(flag in type_text for flag in ("file", "video", "audio", "image", "doc")):
        return False
    return False


def _normalize_item(item: dict[str, object], parent_id: str) -> dict[str, object]:
    return {
        "fileId": _item_fid(item),
        "fidToken": _item_fid_token(item),
        "parentId": parent_id or "0",
        "name": _item_name(item) or _item_fid(item),
        "path": _item_name(item) or _item_fid(item),
        "type": "dir" if _is_dir(item) else "file",
        "isDir": _is_dir(item),
        "size": _item_size(item),
        "md5": "",
        "etag": "",
        "raw": item,
    }


def _collect_download_info_objects(node: object, out: list[dict[str, object]], depth: int = 0) -> None:
    if node is None or depth > 8:
        return
    if isinstance(node, list):
        for item in node:
            _collect_download_info_objects(item, out, depth + 1)
        return
    if not isinstance(node, dict):
        return
    has_fid = any(_text(node.get(key)) for key in ("fid", "file_id", "fileId", "share_fid", "shareFileId", "id"))
    has_hash = any(_text(node.get(key)) for key in ("md5", "file_md5", "fileMd5", "hash", "etag", "content_hash", "contentHash"))
    if has_fid or has_hash:
        out.append(node)
    for value in node.values():
        if isinstance(value, (dict, list)):
            _collect_download_info_objects(value, out, depth + 1)


def _download_info_fid(item: dict[str, object]) -> str:
    return _item_fid(item)


def _download_info_md5(item: dict[str, object]) -> str:
    for key in ("md5", "file_md5", "fileMd5", "hash", "etag", "content_hash", "contentHash"):
        value = _text(item.get(key)).lower()
        if len(value) == 32 and all(ch in "0123456789abcdef" for ch in value):
            return value
    return ""


def _fetch_md5_map(items: list[dict[str, object]], pwd_id: str, stoken: str, cookie: str) -> tuple[int, dict[str, str], dict[str, object]]:
    file_items = [item for item in items if not bool(item.get("isDir")) and _text(item.get("fileId"))]
    if not file_items:
        return 200, {}, {}
    body = {
        "fids": [_text(item.get("fileId")) for item in file_items],
        "pwd_id": pwd_id,
        "stoken": stoken,
        "fids_token": [_text(item.get("fidToken")) for item in file_items],
    }
    status, payload = _request_json(
        f"{UC_API_BASE}/1/clouddrive/file/download?{urlencode({'pr': 'ucpro', 'fr': 'pc', 'uc_param_str': ''})}",
        "POST",
        _headers(cookie),
        body,
    )
    found_nodes: list[dict[str, object]] = []
    _collect_download_info_objects(payload, found_nodes)
    md5_map: dict[str, str] = {}
    for node in found_nodes:
        md5_value = _download_info_md5(node)
        if not md5_value:
            continue
        fid = _download_info_fid(node)
        if fid:
            md5_map[fid] = md5_value
    return status, md5_map, payload


def fetch_uc_live_list(profile_id: str, parent_id: str = "0", page_size: int = 200) -> UcLiveResult:
    profile, cookie, pwd_id, passcode = _load_profile_requirements(profile_id)
    if profile is None:
        return UcLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved UC Drive auth profile was not found.", {})
    if not cookie:
        return UcLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_cookie", "UC Drive live list requires cookie or extra.cookie_header.", {})
    if not pwd_id:
        return UcLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_pwd_id", "UC Drive live list requires extra.pwdId or extra.sharePwdId.", {})

    try:
        token_status, token_payload, stoken = _get_share_token(pwd_id, passcode, cookie)
        if token_status < 200 or token_status >= 300 or not stoken:
            return UcLiveResult(False, "live_error", True, profile.profileId, token_status, "share_token_failed", "UC Drive share token request did not return a usable stoken.", {"raw": token_payload})
        status, payload = _request_json(
            _build_detail_url(pwd_id, stoken, parent_id or "0", 1, max(1, min(200, int(page_size or 200)))),
            "GET",
            _headers(cookie, json_body=False),
        )
        if not _is_success(payload):
            return UcLiveResult(False, "live_error", True, profile.profileId, status, "detail_failed", "UC Drive live list request was rejected.", {"raw": payload})
        items = [_normalize_item(item, parent_id or "0") for item in _extract_list(payload)]
        return UcLiveResult(
            True,
            "live",
            True,
            profile.profileId,
            status,
            "",
            "UC Drive share-based live list succeeded with saved cookie and pwdId.",
            {"items": items, "raw": payload, "pwdId": pwd_id, "parentId": parent_id or "0", "stoken": stoken, "total": _extract_total(payload)},
        )
    except HTTPError as exc:
        return UcLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "UC Drive live list reached the API but was rejected.", {})
    except URLError as exc:
        return UcLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "UC Drive live list could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return UcLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "UC Drive live list returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return UcLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "UC Drive live list failed unexpectedly.", {})


def fetch_uc_live_metadata(profile_id: str, file_id: str, parent_id: str = "0") -> UcLiveResult:
    profile, cookie, pwd_id, passcode = _load_profile_requirements(profile_id)
    if profile is None:
        return UcLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved UC Drive auth profile was not found.", {})
    if not cookie:
        return UcLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_cookie", "UC Drive live metadata requires cookie or extra.cookie_header.", {})
    if not pwd_id:
        return UcLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_pwd_id", "UC Drive live metadata requires extra.pwdId or extra.sharePwdId.", {})
    resolved_file_id = _text(file_id or profile.extra.get("fileId"))
    if not resolved_file_id:
        return UcLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_file_id", "UC Drive live metadata requires fileId.", {})

    list_result = fetch_uc_live_list(profile.profileId, parent_id=parent_id or "0")
    if not list_result.ok:
        return UcLiveResult(
            False,
            list_result.mode,
            True,
            profile.profileId,
            list_result.status,
            list_result.error,
            f"UC Drive live metadata failed because parent page listing did not succeed: {list_result.note}",
            list_result.payload,
        )
    items = list_result.payload.get("items")
    matched = next((item for item in items if isinstance(item, dict) and _text(item.get("fileId")) == resolved_file_id), None) if isinstance(items, list) else None
    if matched is None:
        return UcLiveResult(False, "live_error", True, profile.profileId, list_result.status, "metadata_not_found", "UC Drive live metadata did not find the file under the provided parentId page.", list_result.payload)

    md5_status, md5_map, md5_payload = _fetch_md5_map([matched], pwd_id, _text(list_result.payload.get("stoken")), cookie)
    if md5_status < 200 or md5_status >= 300:
        return UcLiveResult(False, "live_error", True, profile.profileId, md5_status, "download_info_failed", "UC Drive metadata MD5 request was rejected.", {"raw": md5_payload})
    entry = {
        "path": _text(matched.get("name") or resolved_file_id),
        "size": int(matched.get("size", 0) or 0),
        "md5": md5_map.get(resolved_file_id, ""),
        "sha1": "",
        "sha256": "",
        "gcid": "",
        "etag": md5_map.get(resolved_file_id, ""),
        "raw": matched.get("raw") or matched,
    }
    return UcLiveResult(
        True,
        "live",
        True,
        profile.profileId,
        list_result.status,
        "",
        "UC Drive live metadata succeeded through share detail + file/download MD5 lookup.",
        {"entry": entry, "raw": {"detail": list_result.payload.get("raw", {}), "download": md5_payload}, "parentId": parent_id or "0", "pwdId": pwd_id},
    )


def fetch_uc_create_folder(profile_id: str, parent_id: str = "0", dir_name: str = "") -> UcLiveResult:
    profile, cookie, _, _ = _load_profile_requirements(profile_id)
    if profile is None:
        return UcLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved UC Drive auth profile was not found.", {})
    if not cookie:
        return UcLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_cookie", "UC Drive create folder requires cookie or extra.cookie_header.", {})
    resolved_dir_name = _text(dir_name or (profile.extra or {}).get("dirName"))
    if not resolved_dir_name:
        return UcLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_dir_name", "UC Drive create folder requires dirName.", {})
    resolved_parent_id = _text(parent_id or (profile.extra or {}).get("parentId") or "0") or "0"

    try:
        status, payload = _request_json(
            _build_drive_file_url(),
            "POST",
            _headers(cookie),
            {
                "pdir_fid": resolved_parent_id,
                "file_name": resolved_dir_name,
                "dir_path": "",
                "dir_init_lock": False,
            },
        )
        if not _is_success(payload):
            return UcLiveResult(False, "live_error", True, profile.profileId, status, "create_dir_failed", "UC Drive create folder request was rejected.", {"raw": payload})
        raw_item = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        item = {
            "fileId": _text((raw_item or {}).get("fid") or (raw_item or {}).get("file_id") or (raw_item or {}).get("fileId")),
            "parentId": resolved_parent_id,
            "name": resolved_dir_name,
            "path": resolved_dir_name,
            "type": "dir",
            "isDir": True,
            "size": 0,
            "md5": "",
            "etag": "",
            "raw": raw_item or payload,
        }
        return UcLiveResult(True, "live", True, profile.profileId, status, "", "UC Drive live create folder succeeded with saved cookie.", {"item": item, "parentId": resolved_parent_id, "raw": payload})
    except HTTPError as exc:
        return UcLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "UC Drive create folder reached the API but was rejected.", {})
    except URLError as exc:
        return UcLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "UC Drive create folder could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return UcLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "UC Drive create folder returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return UcLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "UC Drive create folder failed unexpectedly.", {})
