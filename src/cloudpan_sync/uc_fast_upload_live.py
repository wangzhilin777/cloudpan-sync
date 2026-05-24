from __future__ import annotations

import base64
import json
import mimetypes
from dataclasses import dataclass
from email.utils import formatdate
from hashlib import md5, sha1
from pathlib import Path, PurePosixPath
from time import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from .auth_store import get_profile
from .uc_live import _build_drive_file_url, _headers, _is_success, _request_json, _text, fetch_uc_live_list


@dataclass
class UcFastUploadResult:
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


def _upload_auth_url() -> str:
    return _build_drive_file_url().replace("/file?", "/file/upload/auth?")


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


def _pick_int(data: dict[str, object], *keys: str) -> int:
    for key in keys:
        value = data.get(key)
        try:
            resolved = int(value or 0)
        except Exception:
            continue
        if resolved > 0:
            return resolved
    return 0


def _split_name(name: str) -> tuple[str, str]:
    pure = PurePosixPath(_text(name) or "file")
    suffix = pure.suffix
    stem = pure.name[: -len(suffix)] if suffix else pure.name
    return stem or "file", suffix


def _build_renamed_candidate(name: str, index: int) -> str:
    stem, suffix = _split_name(name)
    return f"{stem} ({index}){suffix}"


def _resolve_upload_target_name(
    *,
    profile_id: str,
    parent_id: str,
    target_name: str,
    conflict_policy: str,
) -> tuple[str, str, str]:
    list_result = fetch_uc_live_list(profile_id=profile_id, parent_id=parent_id or "0", page_size=200)
    if not list_result.ok:
        return target_name, "conflict_check_unavailable", "Could not verify same-name conflicts before UC upload, so the original file name was kept."

    existing_names = {
        _text(item.get("name"))
        for item in list((list_result.payload or {}).get("items") or [])
        if isinstance(item, dict) and _text(item.get("name"))
    }
    if target_name not in existing_names:
        return target_name, "no_conflict", ""

    index = 1
    candidate = _build_renamed_candidate(target_name, index)
    while candidate in existing_names:
        index += 1
        candidate = _build_renamed_candidate(target_name, index)
    if conflict_policy == "auto_rename_new":
        return candidate, "auto_rename_new", "A same-name file already exists under the target path, so UC auto-renamed the new file."
    return (
        candidate,
        "overwrite_downgraded_to_auto_rename",
        "The requested overwrite policy was downgraded because the current UC upload path does not support verified in-place overwrite.",
    )


def _guess_content_type(file_path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(file_path))
    return _text(mime) or "application/octet-stream"


def _normalize_upload_host(upload_url: str, bucket: str) -> str:
    parsed = urlparse(_text(upload_url))
    host = parsed.netloc or _text(upload_url).replace("https://", "").replace("http://", "").strip("/")
    if host.startswith(f"{bucket}."):
        return host
    return f"{bucket}.{host}"


def _extract_upload_session(pre_data: dict[str, object]) -> dict[str, object]:
    metadata = pre_data.get("metadata")
    meta = metadata if isinstance(metadata, dict) else {}
    return {
        "authInfo": pre_data.get("auth_info") if isinstance(pre_data.get("auth_info"), dict) else meta.get("auth_info") if isinstance(meta.get("auth_info"), dict) else {},
        "bucket": _pick_text(pre_data, "bucket") or _pick_text(meta, "bucket"),
        "objKey": _pick_text(pre_data, "obj_key", "objKey") or _pick_text(meta, "obj_key", "objKey"),
        "uploadId": _pick_text(pre_data, "upload_id", "uploadId") or _pick_text(meta, "upload_id", "uploadId"),
        "uploadUrl": _pick_text(pre_data, "upload_url", "uploadUrl") or _pick_text(meta, "upload_url", "uploadUrl"),
        "callback": pre_data.get("callback") if isinstance(pre_data.get("callback"), dict) else meta.get("callback") if isinstance(meta.get("callback"), dict) else {},
        "partSize": _pick_int(pre_data, "part_size", "partSize") or _pick_int(meta, "part_size", "partSize"),
    }


def _build_part_auth_meta(content_type: str, oss_date: str, bucket: str, obj_key: str, part_number: int, upload_id: str) -> str:
    return (
        "PUT\n\n"
        f"{content_type}\n"
        f"{oss_date}\n"
        f"x-oss-date:{oss_date}\n"
        "x-oss-user-agent:aliyun-sdk-js/6.6.1 Chrome 98.0.4758.80 on Windows 10 64-bit\n"
        f"/{bucket}/{obj_key}?partNumber={part_number}&uploadId={upload_id}"
    )


def _build_commit_xml(part_etags: list[str]) -> str:
    body = ['<?xml version="1.0" encoding="UTF-8"?>', "<CompleteMultipartUpload>"]
    for index, etag in enumerate(part_etags, start=1):
        body.extend(
            [
                "<Part>",
                f"<PartNumber>{index}</PartNumber>",
                f"<ETag>{etag}</ETag>",
                "</Part>",
            ]
        )
    body.append("</CompleteMultipartUpload>")
    return "\n".join(body)


def _build_commit_auth_meta(content_md5: str, callback_b64: str, oss_date: str, bucket: str, obj_key: str, upload_id: str) -> str:
    return (
        "POST\n"
        f"{content_md5}\n"
        "application/xml\n"
        f"{oss_date}\n"
        f"x-oss-callback:{callback_b64}\n"
        f"x-oss-date:{oss_date}\n"
        "x-oss-user-agent:aliyun-sdk-js/6.6.1 Chrome 98.0.4758.80 on Windows 10 64-bit\n"
        f"/{bucket}/{obj_key}?uploadId={upload_id}"
    )


def _request_upload_auth(
    cookie: str,
    auth_info: dict[str, object],
    auth_meta: str,
    task_id: str,
) -> tuple[int, dict[str, object]]:
    return _request_json(
        _upload_auth_url(),
        "POST",
        _headers(cookie),
        {
            "auth_info": auth_info,
            "auth_meta": auth_meta,
            "task_id": task_id,
        },
    )


def _put_oss_part(
    upload_host: str,
    obj_key: str,
    upload_id: str,
    part_number: int,
    authorization: str,
    content_type: str,
    oss_date: str,
    part_bytes: bytes,
) -> str:
    request = Request(
        url=f"https://{upload_host}/{obj_key.lstrip('/')}?{urlencode({'partNumber': part_number, 'uploadId': upload_id})}",
        data=part_bytes,
        headers={
            "Authorization": authorization,
            "Content-Type": content_type,
            "Referer": "https://drive.uc.cn/",
            "x-oss-date": oss_date,
            "x-oss-user-agent": "aliyun-sdk-js/6.6.1 Chrome 98.0.4758.80 on Windows 10 64-bit",
        },
        method="PUT",
    )
    with urlopen(request, timeout=30) as response:
        etag = _text(response.headers.get("Etag") or response.headers.get("ETag"))
        response.read()
        return etag


def _post_oss_commit(
    upload_host: str,
    obj_key: str,
    upload_id: str,
    authorization: str,
    content_md5: str,
    callback_b64: str,
    oss_date: str,
    body: str,
) -> int:
    request = Request(
        url=f"https://{upload_host}/{obj_key.lstrip('/')}?{urlencode({'uploadId': upload_id})}",
        data=body.encode("utf-8"),
        headers={
            "Authorization": authorization,
            "Content-MD5": content_md5,
            "Content-Type": "application/xml",
            "Referer": "https://drive.uc.cn/",
            "x-oss-callback": callback_b64,
            "x-oss-date": oss_date,
            "x-oss-user-agent": "aliyun-sdk-js/6.6.1 Chrome 98.0.4758.80 on Windows 10 64-bit",
        },
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        status = int(getattr(response, "status", 0) or 0)
        response.read()
        return status


def _complete_binary_upload(
    *,
    cookie: str,
    file_path: Path,
    pre_data: dict[str, object],
    task_id: str,
) -> tuple[int, str, dict[str, object]]:
    session = _extract_upload_session(pre_data)
    auth_info = session.get("authInfo")
    bucket = _text(session.get("bucket"))
    obj_key = _text(session.get("objKey"))
    upload_id = _text(session.get("uploadId"))
    upload_url = _text(session.get("uploadUrl"))
    callback = session.get("callback")
    part_size = int(session.get("partSize") or 0)
    if not isinstance(auth_info, dict) or not auth_info or not bucket or not obj_key or not upload_id or not upload_url or not isinstance(callback, dict) or not callback:
        return 0, "missing_upload_session", {"uploadSession": session}

    upload_host = _normalize_upload_host(upload_url, bucket)
    content_type = _guess_content_type(file_path)
    file_size = int(file_path.stat().st_size)
    resolved_part_size = part_size if part_size > 0 else file_size
    etags: list[str] = []
    with file_path.open("rb") as handle:
        part_number = 1
        while True:
            part_bytes = handle.read(resolved_part_size)
            if not part_bytes:
                break
            oss_date = formatdate(usegmt=True)
            auth_status, auth_payload = _request_upload_auth(
                cookie,
                auth_info,
                _build_part_auth_meta(content_type, oss_date, bucket, obj_key, part_number, upload_id),
                task_id,
            )
            if not _is_success(auth_payload):
                return auth_status, f"part_upload_failed:auth:{part_number}", {"uploadSession": session, "authResponse": auth_payload, "partNumber": part_number}
            auth_data = _extract_data(auth_payload)
            authorization = _pick_text(auth_data, "auth_key", "authKey")
            if not authorization:
                return auth_status, f"part_upload_failed:missing_auth_key:{part_number}", {"uploadSession": session, "authResponse": auth_payload, "partNumber": part_number}
            etag = _put_oss_part(
                upload_host,
                obj_key,
                upload_id,
                part_number,
                authorization,
                content_type,
                oss_date,
                part_bytes,
            )
            if not etag:
                return 200, "missing_part_etag", {"uploadSession": session, "partNumber": part_number}
            etags.append(etag)
            part_number += 1

    commit_xml = _build_commit_xml(etags)
    content_md5 = base64.b64encode(md5(commit_xml.encode("utf-8")).digest()).decode("ascii")
    callback_b64 = base64.b64encode(json.dumps(callback, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).decode("ascii")
    commit_date = formatdate(usegmt=True)
    commit_auth_status, commit_auth_payload = _request_upload_auth(
        cookie,
        auth_info,
        _build_commit_auth_meta(content_md5, callback_b64, commit_date, bucket, obj_key, upload_id),
        task_id,
    )
    if not _is_success(commit_auth_payload):
        return commit_auth_status, "commit_failed:auth", {"uploadSession": session, "commitAuthResponse": commit_auth_payload}
    commit_auth_data = _extract_data(commit_auth_payload)
    commit_authorization = _pick_text(commit_auth_data, "auth_key", "authKey")
    if not commit_authorization:
        return commit_auth_status, "commit_failed:missing_auth_key", {"uploadSession": session, "commitAuthResponse": commit_auth_payload}
    commit_status = _post_oss_commit(
        upload_host,
        obj_key,
        upload_id,
        commit_authorization,
        content_md5,
        callback_b64,
        commit_date,
        commit_xml,
    )
    payload = {
        "uploadSession": session,
        "partCount": len(etags),
        "partEtags": etags,
        "commitAuthResponse": commit_auth_payload,
        "commitStatus": commit_status,
    }
    if commit_status < 200 or commit_status >= 300:
        return commit_status, "commit_failed:oss_post", payload
    return commit_status, "", payload


def _classify_issue(status: int, error: str) -> tuple[str, str]:
    if error == "profile_not_found":
        return ("input", "targetProfileId 对应的 UC Drive 授权档案不存在。")
    if error == "missing_cookie":
        return ("auth", "补 cookie 或 extra.cookie_header 后再试 UC 秒传。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续做 UC 秒传。")
    if error == "local_hash_mismatch":
        return ("input", "本地文件的 md5/sha1 与任务条目不一致，先校验来源文件。")
    if error == "missing_task_id":
        return ("provider", "UC upload/pre 未返回 task_id，当前无法继续提交 hash。")
    if error == "missing_obj_key":
        return ("provider", "UC upload/pre 未返回 obj_key，当前无法继续 finish。")
    if error == "hash_not_accepted":
        return ("provider", "UC update/hash 未确认秒传完成，当前仍缺可复用的 rapid-upload 成功响应。")
    if error == "missing_upload_session":
        return ("provider", "UC upload/pre 未返回完整上传会话，当前无法继续走二进制上传兜底。")
    if error == "missing_part_etag":
        return ("provider", "UC 分片上传未返回 ETag，当前无法继续 commit。")
    if error.startswith("part_upload_failed"):
        return ("provider", "UC 分片上传被拒绝，当前二进制上传兜底未完成。")
    if error.startswith("commit_failed"):
        return ("provider", "UC multipart commit 被拒绝，当前无法完成文件落盘。")
    if error.startswith("http_error:401"):
        return ("auth", "秒传请求被 401 拒绝，授权很可能已失效。")
    if error.startswith("http_error:403"):
        return ("risk", "秒传请求被 403 拒绝，可能命中风控或缺必要权限。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "秒传请求过快，建议稍后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "UC provider 侧接口异常，建议稍后重试。")
    if error.startswith("unexpected:"):
        return ("unexpected", "UC 秒传过程异常中断，建议保留错误文本继续排查。")
    return ("", "")


def upload_uc_fast_file(
    *,
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_id: str = "0",
    expected_md5: str = "",
    expected_sha1: str = "",
    conflict_policy: str = "auto_rename_new",
) -> UcFastUploadResult:
    profile, cookie = _load_profile_requirements(profile_id)
    resolved_parent_id = _text(parent_id or "0") or "0"
    if profile is None:
        risk_level, risk_hint = _classify_issue(0, "profile_not_found")
        return UcFastUploadResult(False, "profile_missing", False, profile_id, resolved_parent_id, 0, "profile_not_found", "Saved UC Drive auth profile was not found.", risk_level, risk_hint)
    if not cookie:
        risk_level, risk_hint = _classify_issue(0, "missing_cookie")
        return UcFastUploadResult(False, "profile_incomplete", True, profile.profileId, resolved_parent_id, 0, "missing_cookie", "UC fast upload requires cookie or extra.cookie_header.", risk_level, risk_hint)

    file_path = Path(str(local_path or "").strip())
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_issue(0, "local_file_missing")
        return UcFastUploadResult(False, "local_file_missing", True, profile.profileId, resolved_parent_id, 0, "local_file_missing", "UC fast upload requires an existing local file.", risk_level, risk_hint)

    hashes_ok, actual_md5, actual_sha1 = _verify_local_hashes(file_path, expected_md5, expected_sha1)
    if not hashes_ok:
        risk_level, risk_hint = _classify_issue(0, "local_hash_mismatch")
        return UcFastUploadResult(
            False,
            "local_hash_mismatch",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            "local_hash_mismatch",
            "UC fast upload aborted because local md5/sha1 does not match the task entry.",
            risk_level,
            risk_hint,
            payload={"actualMd5": actual_md5, "actualSha1": actual_sha1},
        )

    now = int(time())
    resolved_target_name, conflict_action, conflict_note = _resolve_upload_target_name(
        profile_id=profile.profileId,
        parent_id=resolved_parent_id,
        target_name=_text(target_name or file_path.name) or file_path.name,
        conflict_policy=conflict_policy,
    )

    pre_body = {
        "ccp_hash_update": True,
        "dir_path": "",
        "file_name": resolved_target_name,
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
    upload_payload: dict[str, object] = {}

    try:
        pre_status, pre_payload = _request_json(_upload_pre_url(), "POST", _headers(cookie), pre_body)
        if not _is_success(pre_payload):
            risk_level, risk_hint = _classify_issue(pre_status, f"http_error:{pre_status}" if pre_status >= 400 else "pre_upload_failed")
            return UcFastUploadResult(
                False,
                "rapid_upload_pre_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                pre_status,
                "pre_upload_failed",
                "UC fast upload pre-flight request was rejected.",
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
            return UcFastUploadResult(False, "rapid_upload_pre_failed", True, profile.profileId, resolved_parent_id, pre_status, "missing_task_id", "UC upload/pre did not return task_id.", risk_level, risk_hint, payload={"preUploadResponse": pre_payload})
        if not obj_key:
            risk_level, risk_hint = _classify_issue(pre_status, "missing_obj_key")
            return UcFastUploadResult(False, "rapid_upload_pre_failed", True, profile.profileId, resolved_parent_id, pre_status, "missing_obj_key", "UC upload/pre did not return obj_key.", risk_level, risk_hint, payload={"preUploadResponse": pre_payload})

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
            return UcFastUploadResult(
                False,
                "rapid_upload_hash_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                hash_status,
                "hash_not_accepted",
                "UC update/hash request was rejected before rapid-upload completion.",
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
            upload_status, upload_error, upload_payload = _complete_binary_upload(
                cookie=cookie,
                file_path=file_path,
                pre_data=pre_data,
                task_id=task_id,
            )
            if upload_error:
                risk_level, risk_hint = _classify_issue(upload_status, upload_error)
                return UcFastUploadResult(
                    False,
                    "binary_upload_fallback_failed",
                    True,
                    profile.profileId,
                    resolved_parent_id,
                    upload_status or hash_status,
                    upload_error,
                    "UC update/hash did not hit rapid upload, and the binary upload fallback did not complete.",
                    risk_level,
                    risk_hint,
                    payload={
                        "preUploadResponse": pre_payload,
                        "hashResponse": hash_payload,
                        "uploadFallback": upload_payload,
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
            return UcFastUploadResult(
                False,
                "rapid_upload_finish_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                finish_status,
                "finish_failed",
                "UC upload/finish request was rejected after hash confirmation.",
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
        used_binary_fallback = not upload_finished
        payload = {
            "fileId": file_id,
            "taskId": task_id,
            "objKey": obj_key,
            "resolvedTargetName": resolved_name,
            "conflictAction": conflict_action,
            "preUploadResponse": pre_payload,
            "hashResponse": hash_payload,
            "finishResponse": finish_payload,
        }
        if used_binary_fallback:
            payload["uploadFallback"] = upload_payload
        return UcFastUploadResult(
            True,
            "binary_upload_after_hash_miss" if used_binary_fallback else "rapid_upload_by_hash",
            True,
            profile.profileId,
            resolved_parent_id,
            finish_status,
            "",
            (
                "UC fast upload completed through upload/pre + update/hash + binary multipart upload + upload/finish."
                if used_binary_fallback
                else "UC fast upload completed through upload/pre + update/hash + upload/finish."
            )
            + (f" {conflict_note}" if conflict_note else ""),
            payload=payload,
            verifyOk=True,
            verifyMode="finish_response_after_binary_upload" if used_binary_fallback else "finish_response",
            verifyNote="UC binary upload fallback was confirmed by the provider finish response."
            if used_binary_fallback
            else "UC rapid-upload success was confirmed by the provider finish response.",
            verifyPayload={
                "fileId": file_id,
                "taskId": task_id,
                "objKey": obj_key,
                "usedBinaryFallback": used_binary_fallback,
            },
        )
    except HTTPError as exc:
        risk_level, risk_hint = _classify_issue(int(exc.code or 0), f"http_error:{exc.code}")
        return UcFastUploadResult(False, "live_error", True, profile.profileId, resolved_parent_id, int(exc.code or 0), f"http_error:{exc.code}", "UC fast upload reached the API but was rejected.", risk_level, risk_hint, payload={"preUploadResponse": pre_payload, "hashResponse": hash_payload, "finishResponse": finish_payload})
    except URLError as exc:
        return UcFastUploadResult(False, "live_error", True, profile.profileId, resolved_parent_id, 0, f"url_error:{exc.reason}", "UC fast upload could not reach the API endpoint.", "network", "网络不可达，无法继续 UC 秒传。")
    except json.JSONDecodeError:
        return UcFastUploadResult(False, "live_error", True, profile.profileId, resolved_parent_id, 200, "invalid_json", "UC fast upload returned non-JSON content.", "provider", "Provider 返回了非 JSON 内容，当前无法继续判断秒传结果。", payload={"preUploadResponse": pre_payload, "hashResponse": hash_payload, "finishResponse": finish_payload})
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_issue(0, f"unexpected:{exc}")
        return UcFastUploadResult(False, "live_error", True, profile.profileId, resolved_parent_id, 0, f"unexpected:{exc}", "UC fast upload failed unexpectedly.", risk_level, risk_hint, payload={"preUploadResponse": pre_payload, "hashResponse": hash_payload, "finishResponse": finish_payload})
