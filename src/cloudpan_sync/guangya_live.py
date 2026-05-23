from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .auth_store import get_profile
from .guangya import guangya_fast_check
from .models import SourceEntry


GUANGYA_API_HOST = "https://api.guangyapan.com"
GUANGYA_LIST_PATH = "/nd.bizuserres.s/v1/file/get_file_list"
GUANGYA_DOWNLOAD_META_PATH = "/nd.bizuserres.s/v1/get_res_download_url"
GUANGYA_CREATE_DIR_PATH = "/nd.bizuserres.s/v1/file/create_dir"
GUANGYA_RES_CENTER_TOKEN_PATH = "/nd.bizuserres.s/v1/get_res_center_token"
GUANGYA_CHECK_CAN_FLASH_UPLOAD_PATH = "/nd.bizuserres.s/v1/check_can_flash_upload"
GUANGYA_DELETE_UPLOAD_TASK_PATH = "/nd.bizuserres.s/v1/file/delete_upload_task"
GUANGYA_CODE_RES_TOKEN_INSTANT = 156


@dataclass
class GuangyaLiveListResult:
    ok: bool
    mode: str
    items: list[dict[str, object]]
    usedProfile: bool
    profileId: str
    parentId: str
    status: int
    error: str
    note: str
    riskLevel: str = ""
    riskHint: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "mode": self.mode,
            "items": self.items,
            "usedProfile": self.usedProfile,
            "profileId": self.profileId,
            "parentId": self.parentId,
            "status": self.status,
            "error": self.error,
            "note": self.note,
            "riskLevel": self.riskLevel,
            "riskHint": self.riskHint,
        }


@dataclass
class GuangyaLiveFastCheckResult:
    ok: bool
    mode: str
    usedProfile: bool
    profileId: str
    parentId: str
    status: int
    error: str
    note: str
    items: list[dict[str, object]]
    riskLevel: str = ""
    riskHint: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "mode": self.mode,
            "usedProfile": self.usedProfile,
            "profileId": self.profileId,
            "parentId": self.parentId,
            "status": self.status,
            "error": self.error,
            "note": self.note,
            "items": self.items,
            "riskLevel": self.riskLevel,
            "riskHint": self.riskHint,
        }


def normalize_guangya_authorization(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text if text.lower().startswith("bearer ") else f"Bearer {text}"


def _pick_string(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _pick_first_extra(extra: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        value = _pick_string(extra.get(key))
        if value:
            return value
    return ""


def _pick_parent_id(profile_extra: dict[str, str], explicit_parent_id: str) -> str:
    return _pick_string(explicit_parent_id) or _pick_first_extra(
        profile_extra,
        ["parentId", "parent_id", "parentFileId", "parent_file_id", "dirId", "dir_id", "pid"],
    )


def _pick_file_id(profile_extra: dict[str, str], explicit_file_id: str) -> str:
    return _pick_string(explicit_file_id) or _pick_first_extra(
        profile_extra,
        ["fileId", "file_id", "resId", "res_id", "id"],
    )


def _pick_authorization(profile: object) -> str:
    extra = getattr(profile, "extra", {}) or {}
    raw = (
        getattr(profile, "token", "")
        or _pick_first_extra(extra, ["authorization", "Authorization", "token", "accessToken", "access_token"])
    )
    return normalize_guangya_authorization(raw)


def _pick_page_size(profile_extra: dict[str, str], explicit_page_size: int) -> int:
    if explicit_page_size > 0:
        return explicit_page_size
    raw = _pick_string(profile_extra.get("pageSize"))
    if raw.isdigit():
        return max(1, int(raw))
    return 100


def _scan_possible_items(node: object, out: list[dict[str, object]], seen: set[int], depth: int = 0) -> None:
    if node is None or depth > 6:
        return
    node_id = id(node)
    if node_id in seen:
        return
    seen.add(node_id)

    if isinstance(node, list):
        for item in node:
            _scan_possible_items(item, out, seen, depth + 1)
        return

    if not isinstance(node, dict):
        return

    file_id = _pick_string(
        node.get("fileId")
        or node.get("file_id")
        or node.get("resId")
        or node.get("res_id")
        or node.get("id")
    )
    name = _pick_string(
        node.get("fileName")
        or node.get("filename")
        or node.get("name")
        or node.get("resName")
        or node.get("title")
    )
    dir_markers = [
        node.get("isDir"),
        node.get("isFolder"),
        node.get("dirType"),
        node.get("fileType"),
        node.get("type"),
        node.get("kind"),
    ]
    is_dir = False
    for marker in dir_markers:
        text = _pick_string(marker).lower()
        if marker is True or text in {"1", "dir", "folder", "directory"}:
            is_dir = True
            break
    size_raw = node.get("fileSize", node.get("size", 0))
    try:
        size = int(size_raw or 0)
    except Exception:
        size = 0

    if file_id and name:
        out.append(
            {
                "fileId": file_id,
                "dirId": _pick_string(node.get("dirId") or node.get("parentId") or node.get("pid")),
                "parentId": _pick_string(node.get("parentId") or node.get("pid")),
                "name": name,
                "path": _pick_string(node.get("path")) or name,
                "type": "dir" if is_dir else "file",
                "isDir": is_dir,
                "size": size,
                "md5": _pick_string(node.get("md5") or node.get("etag")),
                "gcid": _pick_string(node.get("gcid")),
                "raw": node,
            }
        )

    for value in node.values():
        if isinstance(value, (dict, list)):
            _scan_possible_items(value, out, seen, depth + 1)


def extract_guangya_items(payload: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    _scan_possible_items(payload, rows, set())
    deduped: list[dict[str, object]] = []
    seen_keys: set[str] = set()
    for row in rows:
        key = f"{row.get('fileId','')}::{row.get('name','')}"
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(row)
    return deduped


def _find_first_text(node: object, keys: list[str], depth: int = 0) -> str:
    if node is None or depth > 6:
        return ""
    if isinstance(node, dict):
        lowered = {str(k).lower(): v for k, v in node.items()}
        for key in keys:
            if key in lowered:
                value = _pick_string(lowered[key])
                if value:
                    return value
        for value in node.values():
            found = _find_first_text(value, keys, depth + 1)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_first_text(item, keys, depth + 1)
            if found:
                return found
    return ""


def _build_guangya_headers(profile_extra: dict[str, str], authorization: str) -> dict[str, str]:
    did = _pick_string(profile_extra.get("did") or profile_extra.get("deviceId"))
    dt = _pick_string(profile_extra.get("dt"))
    headers = {
        "User-Agent": "CloudPanSync/0.1",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": authorization,
    }
    if did:
        headers["did"] = did
    if dt:
        headers["dt"] = dt
    for key, value in profile_extra.items():
        normalized = str(key or "").strip()
        if normalized.lower() in {"appid", "timestamp", "signature", "nonce"} and str(value or "").strip():
            headers[normalized] = str(value).strip()
    return headers


def _normalize_guangya_hash(value: str, kind: str) -> str:
    text = _pick_string(value).strip('"').lower()
    if not text:
        return ""
    if kind == "md5" and len(text) == 32 and all(ch in "0123456789abcdef" for ch in text):
        return text
    if kind == "gcid" and len(text) == 40 and all(ch in "0123456789abcdef" for ch in text):
        return text
    return ""


def _classify_guangya_live_issue(status: int, error: str) -> tuple[str, str]:
    if error == "missing_authorization":
        return ("auth", "补 token 或 extra.authorization 后再试。")
    if error in {"missing_parent_id", "missing_file_id", "missing_dir_name"}:
        return ("input", "先补齐 Guangya live 所需字段，再做真实请求。")
    if error.startswith("http_error:401"):
        return ("auth", "授权很可能失效或格式不对，先重新抓 token/header。")
    if error.startswith("http_error:403"):
        return ("risk", "接口已拒绝请求，可能命中风控或缺 did/dt 等必要头。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "请求过快，建议降并发、等待后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "Provider 侧接口异常，建议稍后重试并保留样本。")
    if error.startswith("url_error:"):
        return ("network", "当前环境未连通 Guangya API，先检查网络或代理。")
    if error == "invalid_json":
        return ("api_change", "返回内容不是预期 JSON，疑似接口结构变化。")
    if error.startswith("unexpected:"):
        return ("unexpected", "请求异常中断，建议保留错误文本继续排查。")
    return ("", "")


def extract_guangya_metadata_entry(file_id: str, payload: dict[str, object]) -> dict[str, object]:
    md5 = _normalize_guangya_hash(
        _find_first_text(payload, ["md5", "etag", "hash", "digest"]),
        "md5",
    )
    gcid = _normalize_guangya_hash(
        _find_first_text(payload, ["gcid", "resource_md5", "filehash", "reshash"]),
        "gcid",
    )
    size_text = _find_first_text(payload, ["filesize", "file_size", "size", "ressize", "resource_size", "bytes", "length"])
    try:
        size = int(size_text or 0)
    except Exception:
        size = 0
    name = _find_first_text(payload, ["filename", "file_name", "name", "resname", "title"])
    return {
        "path": name or file_id,
        "size": size,
        "md5": md5,
        "sha1": "",
        "sha256": "",
        "gcid": gcid,
        "etag": _find_first_text(payload, ["etag"]),
        "raw": {
            "fileId": file_id,
            "name": name,
            "payload": payload,
        },
    }


def fetch_guangya_live_list(profile_id: str, parent_id: str = "", page_size: int = 100) -> GuangyaLiveListResult:
    profile = get_profile(profile_id)
    if profile is None:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_missing",
            items=[],
            usedProfile=False,
            profileId=profile_id,
            parentId="",
            status=0,
            error="profile_not_found",
            note="Saved Guangya auth profile was not found.",
            riskLevel="input",
            riskHint="targetProfileId 对应的已保存 Guangya 档案不存在。",
        )

    auth = _pick_authorization(profile)
    resolved_parent_id = _pick_parent_id(profile.extra, parent_id)
    resolved_page_size = _pick_page_size(profile.extra, page_size)

    if not auth:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_incomplete",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error="missing_authorization",
            note="Guangya live list requires authorization in token or extra.authorization.",
            riskLevel="auth",
            riskHint="补 token 或 extra.authorization 后再试。",
        )

    if not resolved_parent_id:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_incomplete",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_parent_id",
            note="Guangya live list requires parentId in request or auth profile extra.parentId.",
            riskLevel="input",
            riskHint="先补 parentId，再做 Guangya live list。",
        )

    headers = _build_guangya_headers(profile.extra, auth)

    body = {
        "parentId": resolved_parent_id,
        "pageSize": resolved_page_size,
        "orderBy": 0,
        "sortType": 0,
    }
    request = Request(
        url=f"{GUANGYA_API_HOST}{GUANGYA_LIST_PATH}",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            status = int(getattr(response, "status", 0) or 0)
            text = response.read().decode("utf-8", errors="replace")
        payload = json.loads(text)
        items = extract_guangya_items(payload if isinstance(payload, dict) else {})
        return GuangyaLiveListResult(
            ok=True,
            mode="live",
            items=items,
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=status,
            error="",
            note="Live Guangya list request succeeded with saved auth profile.",
            riskLevel="",
            riskHint="",
        )
    except HTTPError as exc:
        risk_level, risk_hint = _classify_guangya_live_issue(int(exc.code or 0), f"http_error:{exc.code}")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=int(exc.code or 0),
            error=f"http_error:{exc.code}",
            note="Guangya live list request reached the API but was rejected.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except URLError as exc:
        risk_level, risk_hint = _classify_guangya_live_issue(0, f"url_error:{exc.reason}")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error=f"url_error:{exc.reason}",
            note="Guangya live list request could not reach the API endpoint.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except json.JSONDecodeError:
        risk_level, risk_hint = _classify_guangya_live_issue(200, "invalid_json")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=200,
            error="invalid_json",
            note="Guangya live list returned a non-JSON response.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_guangya_live_issue(0, f"unexpected:{exc}")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error=f"unexpected:{exc}",
            note="Guangya live list request failed unexpectedly.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )


def fetch_guangya_live_metadata(profile_id: str, file_id: str) -> GuangyaLiveListResult:
    profile = get_profile(profile_id)
    if profile is None:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_missing",
            items=[],
            usedProfile=False,
            profileId=profile_id,
            parentId="",
            status=0,
            error="profile_not_found",
            note="Saved Guangya auth profile was not found.",
            riskLevel="input",
            riskHint="fileId 对应请求找不到已保存 Guangya 档案。",
        )

    auth = _pick_authorization(profile)
    resolved_file_id = _pick_file_id(profile.extra, file_id)

    if not auth:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_incomplete",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_authorization",
            note="Guangya live metadata requires authorization in token or extra.authorization.",
            riskLevel="auth",
            riskHint="补 token 或 extra.authorization 后再试。",
        )
    if not resolved_file_id:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_incomplete",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_file_id",
            note="Guangya live metadata requires fileId in request or auth profile extra.fileId.",
            riskLevel="input",
            riskHint="先补 fileId，再做 Guangya live metadata。",
        )

    headers = _build_guangya_headers(profile.extra, auth)

    request = Request(
        url=f"{GUANGYA_API_HOST}{GUANGYA_DOWNLOAD_META_PATH}",
        data=json.dumps({"fileId": resolved_file_id}, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            status = int(getattr(response, "status", 0) or 0)
            text = response.read().decode("utf-8", errors="replace")
        payload = json.loads(text)
        entry = extract_guangya_metadata_entry(resolved_file_id, payload if isinstance(payload, dict) else {})
        return GuangyaLiveListResult(
            ok=True,
            mode="live",
            items=[entry],
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=status,
            error="",
            note="Live Guangya metadata request succeeded with saved auth profile.",
            riskLevel="",
            riskHint="",
        )
    except HTTPError as exc:
        risk_level, risk_hint = _classify_guangya_live_issue(int(exc.code or 0), f"http_error:{exc.code}")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=int(exc.code or 0),
            error=f"http_error:{exc.code}",
            note="Guangya live metadata request reached the API but was rejected.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except URLError as exc:
        risk_level, risk_hint = _classify_guangya_live_issue(0, f"url_error:{exc.reason}")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error=f"url_error:{exc.reason}",
            note="Guangya live metadata request could not reach the API endpoint.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except json.JSONDecodeError:
        risk_level, risk_hint = _classify_guangya_live_issue(200, "invalid_json")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=200,
            error="invalid_json",
            note="Guangya live metadata returned a non-JSON response.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_guangya_live_issue(0, f"unexpected:{exc}")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error=f"unexpected:{exc}",
            note="Guangya live metadata request failed unexpectedly.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )


def _extract_created_dir_id(payload: dict[str, object]) -> str:
    return _find_first_text(payload, ["dirid", "dir_id", "fileid", "file_id", "id"])


def fetch_guangya_create_dir(profile_id: str, parent_id: str, dir_name: str) -> GuangyaLiveListResult:
    profile = get_profile(profile_id)
    if profile is None:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_missing",
            items=[],
            usedProfile=False,
            profileId=profile_id,
            parentId="",
            status=0,
            error="profile_not_found",
            note="Saved Guangya auth profile was not found.",
            riskLevel="input",
            riskHint="create_dir 请求对应的已保存 Guangya 档案不存在。",
        )

    auth = _pick_authorization(profile)
    resolved_parent_id = _pick_parent_id(profile.extra, parent_id)
    resolved_dir_name = _pick_string(dir_name)

    if not auth:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_incomplete",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error="missing_authorization",
            note="Guangya create_dir requires authorization in token or extra.authorization.",
            riskLevel="auth",
            riskHint="补 token 或 extra.authorization 后再试。",
        )
    if not resolved_parent_id:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_incomplete",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_parent_id",
            note="Guangya create_dir requires parentId in request or auth profile extra.parentId.",
            riskLevel="input",
            riskHint="先补 parentId，再做 Guangya create_dir。",
        )
    if not resolved_dir_name:
        return GuangyaLiveListResult(
            ok=False,
            mode="profile_incomplete",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error="missing_dir_name",
            note="Guangya create_dir requires dirName in the request.",
            riskLevel="input",
            riskHint="先补 dirName，再做 Guangya create_dir。",
        )

    headers = _build_guangya_headers(profile.extra, auth)

    request = Request(
        url=f"{GUANGYA_API_HOST}{GUANGYA_CREATE_DIR_PATH}",
        data=json.dumps({"dirName": resolved_dir_name, "parentId": resolved_parent_id}, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            status = int(getattr(response, "status", 0) or 0)
            text = response.read().decode("utf-8", errors="replace")
        payload = json.loads(text)
        created_id = _extract_created_dir_id(payload if isinstance(payload, dict) else {})
        item = {
            "fileId": created_id,
            "parentId": resolved_parent_id,
            "name": resolved_dir_name,
            "path": resolved_dir_name,
            "type": "dir",
            "isDir": True,
            "size": 0,
            "raw": payload,
        }
        return GuangyaLiveListResult(
            ok=True,
            mode="live",
            items=[item],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=status,
            error="",
            note="Live Guangya create_dir request succeeded with saved auth profile.",
            riskLevel="",
            riskHint="",
        )
    except HTTPError as exc:
        risk_level, risk_hint = _classify_guangya_live_issue(int(exc.code or 0), f"http_error:{exc.code}")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=int(exc.code or 0),
            error=f"http_error:{exc.code}",
            note="Guangya create_dir request reached the API but was rejected.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except URLError as exc:
        risk_level, risk_hint = _classify_guangya_live_issue(0, f"url_error:{exc.reason}")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error=f"url_error:{exc.reason}",
            note="Guangya create_dir request could not reach the API endpoint.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except json.JSONDecodeError:
        risk_level, risk_hint = _classify_guangya_live_issue(200, "invalid_json")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=200,
            error="invalid_json",
            note="Guangya create_dir returned a non-JSON response.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_guangya_live_issue(0, f"unexpected:{exc}")
        return GuangyaLiveListResult(
            ok=False,
            mode="live_error",
            items=[],
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error=f"unexpected:{exc}",
            note="Guangya create_dir request failed unexpectedly.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )


def fetch_guangya_live_fast_check(profile_id: str, entries: list[SourceEntry], parent_id: str = "") -> GuangyaLiveFastCheckResult:
    profile = get_profile(profile_id)
    if profile is None:
        return GuangyaLiveFastCheckResult(
            ok=False,
            mode="profile_missing",
            usedProfile=False,
            profileId=profile_id,
            parentId="",
            status=0,
            error="profile_not_found",
            note="Saved Guangya auth profile was not found.",
            items=[],
            riskLevel="input",
            riskHint="targetProfileId 对应的已保存 Guangya 档案不存在。",
        )

    auth = _pick_authorization(profile)
    resolved_parent_id = _pick_parent_id(profile.extra, parent_id)
    if not auth:
        return GuangyaLiveFastCheckResult(
            ok=False,
            mode="profile_incomplete",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error="missing_authorization",
            note="Guangya live fast check requires authorization in token or extra.authorization.",
            items=[],
            riskLevel="auth",
            riskHint="补 token 或 extra.authorization 后再试。",
        )
    if not resolved_parent_id:
        return GuangyaLiveFastCheckResult(
            ok=False,
            mode="profile_incomplete",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_parent_id",
            note="Guangya live fast check requires parentId in request or auth profile extra.parentId.",
            items=[],
            riskLevel="input",
            riskHint="先补 parentId，再做 Guangya live fast check。",
        )

    headers = _build_guangya_headers(profile.extra, auth)
    rows: list[dict[str, object]] = []
    last_status = 200

    try:
        for entry in entries:
            local = guangya_fast_check(entry)
            row = {
                "path": entry.path,
                "size": int(entry.size),
                "supported": local.supported,
                "hashKind": local.hashKind,
                "normalizedHash": local.normalizedHash,
                "canFastUpload": False,
                "taskId": "",
                "status": 0,
                "error": "",
                "note": local.reason,
                "cleanupAttempted": False,
                "riskHint": local.riskHint,
            }
            if not local.supported:
                rows.append(row)
                continue

            target_name = PurePosixPath(entry.path or "/").name or "file"
            body: dict[str, object] = {
                "capacity": 1,
                "name": target_name,
                "parentId": str(resolved_parent_id),
                "res": {"fileSize": int(entry.size)},
            }
            if local.hashKind == "md5":
                body["res"]["md5"] = local.normalizedHash

            request = Request(
                url=f"{GUANGYA_API_HOST}{GUANGYA_RES_CENTER_TOKEN_PATH}",
                data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urlopen(request, timeout=15) as response:
                status = int(getattr(response, "status", 0) or 0)
                text = response.read().decode("utf-8", errors="replace")
            last_status = status
            payload = json.loads(text)
            code_text = _find_first_text(payload, ["code"])
            task_id = _find_first_text(payload, ["taskid", "task_id", "taskId"])
            row["status"] = status
            row["taskId"] = task_id

            try:
                code = int(code_text or 0)
            except Exception:
                code = 0

            if code == GUANGYA_CODE_RES_TOKEN_INSTANT:
                row["canFastUpload"] = True
                row["note"] = "Guangya fast-upload inventory hit succeeded via get_res_center_token."
                row["riskHint"] = ""
                rows.append(row)
                continue

            if local.hashKind == "gcid" and task_id:
                check_request = Request(
                    url=f"{GUANGYA_API_HOST}{GUANGYA_CHECK_CAN_FLASH_UPLOAD_PATH}",
                    data=json.dumps({"taskId": str(task_id), "gcid": local.normalizedHash}, ensure_ascii=False).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )
                with urlopen(check_request, timeout=15) as response:
                    check_status = int(getattr(response, "status", 0) or 0)
                    check_text = response.read().decode("utf-8", errors="replace")
                last_status = check_status
                check_payload = json.loads(check_text)
                can_flash = bool(((check_payload.get("data") or {}) if isinstance(check_payload.get("data"), dict) else {}).get("canFlashUpload"))
                row["status"] = check_status
                row["canFastUpload"] = can_flash
                row["note"] = (
                    "Guangya GCID flash-upload check succeeded."
                    if can_flash
                    else "Guangya GCID flash-upload check did not hit provider inventory."
                )
                if can_flash:
                    row["riskHint"] = ""

            if task_id and not row["canFastUpload"]:
                row["cleanupAttempted"] = True
                try:
                    cleanup_request = Request(
                        url=f"{GUANGYA_API_HOST}{GUANGYA_DELETE_UPLOAD_TASK_PATH}",
                        data=json.dumps({"taskIds": [str(task_id)]}, ensure_ascii=False).encode("utf-8"),
                        headers=headers,
                        method="POST",
                    )
                    with urlopen(cleanup_request, timeout=15) as response:
                        last_status = int(getattr(response, "status", 0) or 0) or last_status
                        response.read()
                except Exception:
                    pass

            if not row["canFastUpload"] and row["note"] == local.reason:
                row["note"] = "Guangya fast-upload inventory check did not report an available instant hit."
                row["riskHint"] = "没有命中库存时，不要假装已支持；后续要么走本地 fallback，要么保留人工确认。"
            rows.append(row)

        ok = any(bool(row.get("canFastUpload")) for row in rows)
        return GuangyaLiveFastCheckResult(
            ok=ok,
            mode="live_fast_check",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=last_status,
            error="",
            note="Guangya live fast check finished. Successful rows indicate a provider-side inventory hit, not a mock-only precheck.",
            items=rows,
            riskLevel="",
            riskHint="",
        )
    except HTTPError as exc:
        risk_level, risk_hint = _classify_guangya_live_issue(int(exc.code or 0), f"http_error:{exc.code}")
        return GuangyaLiveFastCheckResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=int(exc.code or 0),
            error=f"http_error:{exc.code}",
            note="Guangya live fast check reached the API but was rejected.",
            items=rows,
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except URLError as exc:
        risk_level, risk_hint = _classify_guangya_live_issue(0, f"url_error:{exc.reason}")
        return GuangyaLiveFastCheckResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error=f"url_error:{exc.reason}",
            note="Guangya live fast check could not reach the API endpoint.",
            items=rows,
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except json.JSONDecodeError:
        risk_level, risk_hint = _classify_guangya_live_issue(last_status, "invalid_json")
        return GuangyaLiveFastCheckResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=last_status,
            error="invalid_json",
            note="Guangya live fast check returned non-JSON content.",
            items=rows,
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_guangya_live_issue(last_status, f"unexpected:{exc}")
        return GuangyaLiveFastCheckResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=last_status,
            error=f"unexpected:{exc}",
            note="Guangya live fast check failed unexpectedly.",
            items=rows,
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
