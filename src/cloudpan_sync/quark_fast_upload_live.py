from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import md5, sha1
from pathlib import Path
from time import time
from urllib.error import HTTPError, URLError

from .auth_store import get_profile
from .quark_live import _build_drive_file_url, _headers, _is_success, _request_json, _text


@dataclass
class QuarkFastUploadResult:
    ok: bool
    mode: str
    usedProfile: bool
    profileId: str
    parentId: str
    status: int
    error: str
    note: str
    riskLevel: str = ""
    riskHint: str = ""
    payload: dict[str, object] | None = None
    verifyOk: bool = False
    verifyMode: str = ""
    verifyNote: str = ""
    verifyPayload: dict[str, object] | None = None

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
            "riskLevel": self.riskLevel,
            "riskHint": self.riskHint,
            "payload": self.payload or {},
            "verifyOk": self.verifyOk,
            "verifyMode": self.verifyMode,
            "verifyNote": self.verifyNote,
            "verifyPayload": self.verifyPayload or {},
        }


def _upload_pre_url() -> str:
    return _build_drive_file_url().replace("/file?", "/file/upload/pre?")


def _upload_hash_url() -> str:
    return _build_drive_file_url().replace("/file?", "/file/update/hash?")


def _upload_finish_url() -> str:
    return _build_drive_file_url().replace("/file?", "/file/upload/finish?")


def _format_type(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix in {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".m4v"}:
        return "video"
    if suffix in {".mp3", ".flac", ".wav", ".aac", ".m4a", ".ogg"}:
        return "audio"
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic"}:
        return "image"
    if suffix in {".txt", ".md", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}:
        return "doc"
    return "file"


def _compute_local_hashes(file_path: Path) -> tuple[str, str]:
    md5_hasher = md5()
    sha1_hasher = sha1()
    with file_path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            md5_hasher.update(chunk)
            sha1_hasher.update(chunk)
    return md5_hasher.hexdigest().lower(), sha1_hasher.hexdigest().lower()


def _verify_local_hashes(file_path: Path, expected_md5: str, expected_sha1: str) -> tuple[bool, str, str]:
    actual_md5, actual_sha1 = _compute_local_hashes(file_path)
    normalized_md5 = _text(expected_md5).lower() or actual_md5
    normalized_sha1 = _text(expected_sha1).lower() or actual_sha1
    if normalized_md5 != actual_md5:
        return False, actual_md5, actual_sha1
    if normalized_sha1 != actual_sha1:
        return False, actual_md5, actual_sha1
    return True, actual_md5, actual_sha1


def _load_profile_requirements(profile_id: str) -> tuple[object | None, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, ""
    extra = profile.extra or {}
    cookie = _text(profile.cookie or extra.get("cookie") or extra.get("cookie_header"))
    return profile, cookie


def _extract_data(payload: dict[str, object]) -> dict[str, object]:
    data = payload.get("data")
    return data if isinstance(data, dict) else {}


def _pick_text(data: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = _text(data.get(key))
        if value:
            return value
    return ""


def _classify_issue(status: int, error: str) -> tuple[str, str]:
    if error == "profile_not_found":
        return ("input", "targetProfileId 对应的 Quark 授权档案不存在。")
    if error == "missing_cookie":
        return ("auth", "补 cookie 或 extra.cookie_header 后再试 Quark 秒传。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续做 Quark 秒传。")
    if error == "local_hash_mismatch":
        return ("input", "本地文件的 md5/sha1 与任务条目不一致，先校验来源文件。")
    if error == "missing_task_id":
        return ("provider", "Quark upload/pre 未返回 task_id，当前无法继续提交 hash。")
    if error == "missing_obj_key":
        return ("provider", "Quark upload/pre 未返回 obj_key，当前无法继续 finish。")
    if error == "hash_not_accepted":
        return ("provider", "Quark update/hash 未确认秒传完成，当前仍缺可复用的 rapid-upload 成功响应。")
    if error.startswith("http_error:401"):
        return ("auth", "秒传请求被 401 拒绝，授权很可能已失效。")
    if error.startswith("http_error:403"):
        return ("risk", "秒传请求被 403 拒绝，可能命中风控或缺必要权限。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "秒传请求过快，建议稍后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "Quark provider 侧接口异常，建议稍后重试。")
    if error.startswith("unexpected:"):
        return ("unexpected", "Quark 秒传过程异常中断，建议保留错误文本继续排查。")
    return ("", "")


def upload_quark_fast_file(
    *,
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_id: str = "0",
    expected_md5: str = "",
    expected_sha1: str = "",
) -> QuarkFastUploadResult:
    profile, cookie = _load_profile_requirements(profile_id)
    resolved_parent_id = _text(parent_id or "0") or "0"
    if profile is None:
        risk_level, risk_hint = _classify_issue(0, "profile_not_found")
        return QuarkFastUploadResult(False, "profile_missing", False, profile_id, resolved_parent_id, 0, "profile_not_found", "Saved Quark auth profile was not found.", risk_level, risk_hint)
    if not cookie:
        risk_level, risk_hint = _classify_issue(0, "missing_cookie")
        return QuarkFastUploadResult(False, "profile_incomplete", True, profile.profileId, resolved_parent_id, 0, "missing_cookie", "Quark fast upload requires cookie or extra.cookie_header.", risk_level, risk_hint)

    file_path = Path(str(local_path or "").strip())
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_issue(0, "local_file_missing")
        return QuarkFastUploadResult(False, "local_file_missing", True, profile.profileId, resolved_parent_id, 0, "local_file_missing", "Quark fast upload requires an existing local file.", risk_level, risk_hint)

    hashes_ok, actual_md5, actual_sha1 = _verify_local_hashes(file_path, expected_md5, expected_sha1)
    if not hashes_ok:
        risk_level, risk_hint = _classify_issue(0, "local_hash_mismatch")
        return QuarkFastUploadResult(
            False,
            "local_hash_mismatch",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            "local_hash_mismatch",
            "Quark fast upload aborted because local md5/sha1 does not match the task entry.",
            risk_level,
            risk_hint,
            payload={"actualMd5": actual_md5, "actualSha1": actual_sha1},
        )

    now = int(time())
    pre_body = {
        "ccp_hash_update": True,
        "dir_path": "",
        "file_name": _text(target_name or file_path.name) or file_path.name,
        "format_type": _format_type(file_path),
        "l_created_at": now,
        "l_updated_at": now,
        "pdir_fid": resolved_parent_id,
        "size": int(file_path.stat().st_size),
    }

    pre_status = 0
    pre_payload: dict[str, object] = {}
    hash_status = 0
    hash_payload: dict[str, object] = {}
    finish_status = 0
    finish_payload: dict[str, object] = {}

    try:
        pre_status, pre_payload = _request_json(
            _upload_pre_url(),
            "POST",
            _headers(cookie),
            pre_body,
        )
        if not _is_success(pre_payload):
            risk_level, risk_hint = _classify_issue(pre_status, f"http_error:{pre_status}" if pre_status >= 400 else "pre_upload_failed")
            return QuarkFastUploadResult(
                False,
                "rapid_upload_pre_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                pre_status,
                "pre_upload_failed",
                "Quark fast upload pre-flight request was rejected.",
                risk_level,
                risk_hint,
                payload={"preUploadResponse": pre_payload},
            )

        pre_data = _extract_data(pre_payload)
        task_id = _pick_text(pre_data, "task_id", "taskId")
        obj_key = _pick_text(pre_data, "obj_key", "objKey")
        file_id = _pick_text(pre_data, "fid", "file_id", "fileId")
        if not task_id:
            risk_level, risk_hint = _classify_issue(pre_status, "missing_task_id")
            return QuarkFastUploadResult(False, "rapid_upload_pre_failed", True, profile.profileId, resolved_parent_id, pre_status, "missing_task_id", "Quark upload/pre did not return task_id.", risk_level, risk_hint, payload={"preUploadResponse": pre_payload})
        if not obj_key:
            risk_level, risk_hint = _classify_issue(pre_status, "missing_obj_key")
            return QuarkFastUploadResult(False, "rapid_upload_pre_failed", True, profile.profileId, resolved_parent_id, pre_status, "missing_obj_key", "Quark upload/pre did not return obj_key.", risk_level, risk_hint, payload={"preUploadResponse": pre_payload})

        hash_status, hash_payload = _request_json(
            _upload_hash_url(),
            "POST",
            _headers(cookie),
            {
                "md5": actual_md5,
                "sha1": actual_sha1,
                "task_id": task_id,
            },
        )
        if not _is_success(hash_payload):
            risk_level, risk_hint = _classify_issue(hash_status, f"http_error:{hash_status}" if hash_status >= 400 else "hash_not_accepted")
            return QuarkFastUploadResult(
                False,
                "rapid_upload_hash_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                hash_status,
                "hash_not_accepted",
                "Quark update/hash request was rejected before rapid-upload completion.",
                risk_level,
                risk_hint,
                payload={
                    "preUploadResponse": pre_payload,
                    "hashResponse": hash_payload,
                    "taskId": task_id,
                    "objKey": obj_key,
                },
            )

        hash_data = _extract_data(hash_payload)
        upload_finished = bool(hash_data.get("finish"))
        file_id = _pick_text(hash_data, "fid", "file_id", "fileId") or file_id
        if not upload_finished:
            risk_level, risk_hint = _classify_issue(hash_status, "hash_not_accepted")
            return QuarkFastUploadResult(
                False,
                "rapid_upload_hash_incomplete",
                True,
                profile.profileId,
                resolved_parent_id,
                hash_status,
                "hash_not_accepted",
                "Quark update/hash completed but did not confirm rapid-upload success.",
                risk_level,
                risk_hint,
                payload={
                    "preUploadResponse": pre_payload,
                    "hashResponse": hash_payload,
                    "taskId": task_id,
                    "objKey": obj_key,
                },
            )

        finish_status, finish_payload = _request_json(
            _upload_finish_url(),
            "POST",
            _headers(cookie),
            {
                "obj_key": obj_key,
                "task_id": task_id,
            },
        )
        if not _is_success(finish_payload):
            risk_level, risk_hint = _classify_issue(finish_status, f"http_error:{finish_status}" if finish_status >= 400 else "finish_failed")
            return QuarkFastUploadResult(
                False,
                "rapid_upload_finish_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                finish_status,
                "finish_failed",
                "Quark upload/finish request was rejected after hash confirmation.",
                risk_level,
                risk_hint,
                payload={
                    "preUploadResponse": pre_payload,
                    "hashResponse": hash_payload,
                    "finishResponse": finish_payload,
                    "taskId": task_id,
                    "objKey": obj_key,
                },
            )

        finish_data = _extract_data(finish_payload)
        file_id = _pick_text(finish_data, "fid", "file_id", "fileId") or file_id
        resolved_name = _pick_text(finish_data, "file_name", "fileName", "name") or pre_body["file_name"]
        payload = {
            "fileId": file_id,
            "taskId": task_id,
            "objKey": obj_key,
            "resolvedTargetName": resolved_name,
            "conflictAction": "",
            "preUploadResponse": pre_payload,
            "hashResponse": hash_payload,
            "finishResponse": finish_payload,
        }
        return QuarkFastUploadResult(
            True,
            "rapid_upload_by_hash",
            True,
            profile.profileId,
            resolved_parent_id,
            finish_status,
            "",
            "Quark fast upload completed through upload/pre + update/hash + upload/finish.",
            payload=payload,
            verifyOk=True,
            verifyMode="finish_response",
            verifyNote="Quark rapid-upload success was confirmed by the provider finish response.",
            verifyPayload={
                "fileId": file_id,
                "taskId": task_id,
                "objKey": obj_key,
            },
        )
    except HTTPError as exc:
        risk_level, risk_hint = _classify_issue(int(exc.code or 0), f"http_error:{exc.code}")
        return QuarkFastUploadResult(False, "live_error", True, profile.profileId, resolved_parent_id, int(exc.code or 0), f"http_error:{exc.code}", "Quark fast upload reached the API but was rejected.", risk_level, risk_hint, payload={"preUploadResponse": pre_payload, "hashResponse": hash_payload, "finishResponse": finish_payload})
    except URLError as exc:
        return QuarkFastUploadResult(False, "live_error", True, profile.profileId, resolved_parent_id, 0, f"url_error:{exc.reason}", "Quark fast upload could not reach the API endpoint.", "network", "网络不可达，无法继续 Quark 秒传。")
    except json.JSONDecodeError:
        return QuarkFastUploadResult(False, "live_error", True, profile.profileId, resolved_parent_id, 200, "invalid_json", "Quark fast upload returned non-JSON content.", "provider", "Provider 返回了非 JSON 内容，当前无法继续判断秒传结果。", payload={"preUploadResponse": pre_payload, "hashResponse": hash_payload, "finishResponse": finish_payload})
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_issue(0, f"unexpected:{exc}")
        return QuarkFastUploadResult(False, "live_error", True, profile.profileId, resolved_parent_id, 0, f"unexpected:{exc}", "Quark fast upload failed unexpectedly.", risk_level, risk_hint, payload={"preUploadResponse": pre_payload, "hashResponse": hash_payload, "finishResponse": finish_payload})
