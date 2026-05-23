from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .auth_store import get_profile


@dataclass
class TianyiLiveResult:
    ok: bool
    mode: str
    usedProfile: bool
    profileId: str
    status: int
    error: str
    note: str
    payload: dict[str, object]


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _headers(share_code: str, form: bool = False) -> dict[str, str]:
    headers = {
        "Accept": "application/json;charset=UTF-8",
        "Referer": f"https://cloud.189.cn/web/share?code={share_code}" if share_code else "https://cloud.189.cn/web/",
        "Origin": "https://cloud.189.cn",
        "Sign-Type": "1",
        "User-Agent": "CloudPanSync/0.1",
    }
    if form:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    return headers


def _request_json(url: str, method: str = "GET", headers: dict[str, str] | None = None, body: str = "") -> tuple[int, dict[str, object]]:
    request = Request(
        url=url,
        headers=headers or {},
        data=body.encode("utf-8") if method == "POST" else None,
        method=method,
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _assert_success(payload: dict[str, object]) -> tuple[bool, str]:
    code = _text(payload.get("res_code") or payload.get("resCode") or payload.get("code") or "0")
    if code != "0":
        return False, code
    return True, code


def _normalize_item_name(item: dict[str, object]) -> str:
    for key in ["name", "fileName", "filename", "file_name"]:
        value = _text(item.get(key))
        if value:
            return value
    return ""


def _normalize_item_id(item: dict[str, object]) -> str:
    for key in ["id", "fileId", "fileID", "file_id"]:
        value = _text(item.get(key))
        if value:
            return value
    return ""


def _normalize_item_size(item: dict[str, object]) -> int:
    for key in ["size", "fileSize", "file_size", "bytes"]:
        raw = item.get(key)
        try:
            return int(raw or 0)
        except Exception:
            continue
    return 0


def _normalize_md5(item: dict[str, object]) -> str:
    for key in ["md5", "fileMd5", "file_md5", "etag"]:
        value = _text(item.get(key)).lower()
        if len(value) == 32 and all(ch in "0123456789abcdef" for ch in value):
            return value
    return ""


def _fetch_share_info(share_code: str) -> tuple[int, dict[str, object]]:
    return _request_json(
        "https://cloud.189.cn/api/open/share/getShareInfoByCodeV2.action",
        method="POST",
        headers=_headers(share_code, form=True),
        body=urlencode({"shareCode": share_code}),
    )


def _fetch_share_id(share_code: str, access_code: str, share_info: dict[str, object]) -> tuple[int, str]:
    direct = _text(share_info.get("shareId") or share_info.get("shareID") or (share_info.get("data") or {}).get("shareId"))
    if direct:
        return 200, direct
    query = urlencode({"shareCode": share_code, "accessCode": access_code})
    status, payload = _request_json(
        f"https://cloud.189.cn/api/open/share/checkAccessCode.action?{query}",
        headers=_headers(share_code),
    )
    ok, _ = _assert_success(payload)
    if not ok:
        return status, ""
    share_id = _text(payload.get("shareId") or payload.get("shareID") or (payload.get("data") or {}).get("shareId"))
    return status, share_id


def _fetch_dir_page(share_code: str, share_id: str, share_mode: int, file_id: str, page_num: int = 1, page_size: int = 100, access_code: str = "") -> tuple[int, dict[str, object]]:
    params = {
        "pageNum": page_num,
        "pageSize": page_size,
        "fileId": file_id,
        "shareDirFileId": file_id,
        "isFolder": "true",
        "shareId": share_id,
        "shareMode": share_mode or 1,
        "iconOption": 5,
        "orderBy": "lastOpTime",
        "descending": "true",
        "accessCode": access_code,
    }
    query = urlencode({k: v for k, v in params.items() if _text(v)})
    return _request_json(
        f"https://cloud.189.cn/api/open/share/listShareDir.action?{query}",
        headers=_headers(share_code),
    )


def _extract_file_list_ao(payload: dict[str, object]) -> dict[str, object]:
    root = payload.get("fileListAO") or (payload.get("data") or {}).get("fileListAO") or payload.get("data") or payload
    return root if isinstance(root, dict) else {}


def _build_rows_from_page(file_list_ao: dict[str, object], parent_path: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for folder in file_list_ao.get("folderList") or []:
        if not isinstance(folder, dict):
            continue
        name = _normalize_item_name(folder)
        file_id = _normalize_item_id(folder)
        if not name or not file_id:
            continue
        rows.append(
            {
                "fileId": file_id,
                "parentId": parent_path,
                "name": name,
                "path": f"{parent_path}/{name}".replace("//", "/"),
                "type": "dir",
                "isDir": True,
                "size": 0,
                "md5": "",
                "etag": "",
                "raw": folder,
            }
        )
    for file in file_list_ao.get("fileList") or []:
        if not isinstance(file, dict):
            continue
        name = _normalize_item_name(file)
        file_id = _normalize_item_id(file)
        if not name or not file_id:
            continue
        md5 = _normalize_md5(file)
        rows.append(
            {
                "fileId": file_id,
                "parentId": parent_path,
                "name": name,
                "path": f"{parent_path}/{name}".replace("//", "/"),
                "type": "file",
                "isDir": False,
                "size": _normalize_item_size(file),
                "md5": md5,
                "etag": md5,
                "raw": file,
            }
        )
    return rows


def fetch_tianyi_live_list(profile_id: str, file_id: str = "", page_size: int = 100) -> TianyiLiveResult:
    profile = get_profile(profile_id)
    if profile is None:
        return TianyiLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved 189Cloud auth profile was not found.", {})

    share_code = _text(profile.extra.get("shareCode"))
    access_code = _text(profile.extra.get("accessCode") or profile.extra.get("passcode"))
    if not share_code:
        return TianyiLiveResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_share_code", "189Cloud live list requires extra.shareCode.", {})

    try:
        info_status, info_payload = _fetch_share_info(share_code)
        ok, _ = _assert_success(info_payload)
        if not ok:
            return TianyiLiveResult(False, "live_error", True, profile.profileId, info_status, "share_info_failed", "189Cloud share info request was rejected.", {})
        info = info_payload.get("data") if isinstance(info_payload.get("data"), dict) else info_payload
        share_mode = int(info.get("shareMode", info.get("share_mode", 1)) or 1)
        root_file_id = _text(file_id or profile.extra.get("fileId") or info.get("fileId") or info.get("id"))
        if not root_file_id:
            return TianyiLiveResult(False, "profile_incomplete", True, profile.profileId, info_status, "missing_root_file_id", "189Cloud live list requires fileId in request, extra.fileId, or share root fileId.", {})
        share_id_status, share_id = _fetch_share_id(share_code, access_code, info)
        if not share_id:
            return TianyiLiveResult(False, "live_error", True, profile.profileId, share_id_status, "share_id_failed", "189Cloud access code validation did not return shareId.", {})
        list_status, list_payload = _fetch_dir_page(share_code, share_id, share_mode, root_file_id, page_num=1, page_size=page_size, access_code=access_code)
        ok, _ = _assert_success(list_payload)
        if not ok:
            return TianyiLiveResult(False, "live_error", True, profile.profileId, list_status, "list_failed", "189Cloud live list request was rejected.", {})
        file_list_ao = _extract_file_list_ao(list_payload)
        rows = _build_rows_from_page(file_list_ao, profile.extra.get("pathPrefix") or "/189cloud-share")
        return TianyiLiveResult(True, "live", True, profile.profileId, list_status, "", "189Cloud live list succeeded using share APIs.", {"items": rows, "raw": list_payload, "shareCode": share_code})
    except HTTPError as exc:
        return TianyiLiveResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "189Cloud live list reached the API but was rejected.", {})
    except URLError as exc:
        return TianyiLiveResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "189Cloud live list could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return TianyiLiveResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "189Cloud live list returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return TianyiLiveResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "189Cloud live list failed unexpectedly.", {})


def fetch_tianyi_live_metadata(profile_id: str, file_id: str = "") -> TianyiLiveResult:
    list_result = fetch_tianyi_live_list(profile_id=profile_id, file_id=file_id, page_size=100)
    if not list_result.ok:
        return TianyiLiveResult(
            ok=False,
            mode=list_result.mode,
            usedProfile=list_result.usedProfile,
            profileId=list_result.profileId,
            status=list_result.status,
            error=list_result.error,
            note=list_result.note,
            payload={},
        )
    target_file_id = _text(file_id or get_profile(profile_id).extra.get("fileId"))
    items = list_result.payload.get("items") or []
    chosen = None
    for item in items:
        if isinstance(item, dict) and _text(item.get("fileId")) == target_file_id:
            chosen = item
            break
    if chosen is None:
        chosen = next((item for item in items if isinstance(item, dict) and not item.get("isDir")), None)
    if chosen is None:
        return TianyiLiveResult(False, "live_error", True, list_result.profileId, list_result.status, "metadata_not_found", "189Cloud metadata probe did not find a file entry in the current directory page.", {})
    entry = {
        "path": _text(chosen.get("path")),
        "size": int(chosen.get("size", 0) or 0),
        "md5": _text(chosen.get("md5")),
        "sha1": "",
        "sha256": "",
        "gcid": "",
        "etag": _text(chosen.get("etag")),
        "raw": chosen.get("raw") or chosen,
    }
    return TianyiLiveResult(True, "live", True, list_result.profileId, list_result.status, "", "189Cloud live metadata succeeded using the current directory page payload.", {"entry": entry, "raw": chosen})


def fetch_tianyi_create_folder(profile_id: str, parent_id: str = "", dir_name: str = "") -> TianyiLiveResult:
    profile = get_profile(profile_id)
    if profile is None:
        return TianyiLiveResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved 189Cloud auth profile was not found.", {})

    share_code = _text(profile.extra.get("shareCode"))
    if share_code:
        return TianyiLiveResult(
            False,
            "unsupported_readonly_share_auth",
            True,
            profile.profileId,
            0,
            "share_auth_readonly",
            "189Cloud create folder is not available on the current shareCode/accessCode read-only probe path; official createFolder.action requires account-level OAuth headers.",
            {
                "parentId": _text(parent_id),
                "dirName": _text(dir_name),
                "requiredAuth": ["AccessToken", "Signature", "Date"],
            },
        )

    return TianyiLiveResult(
        False,
        "unsupported_auth_missing",
        True,
        profile.profileId,
        0,
        "missing_account_level_auth",
        "189Cloud create folder still needs account-level OAuth auth wiring before createFolder.action can be called.",
        {
            "parentId": _text(parent_id),
            "dirName": _text(dir_name),
            "requiredAuth": ["AccessToken", "Signature", "Date"],
        },
    )
