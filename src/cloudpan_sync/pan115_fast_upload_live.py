from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from hashlib import sha1
from importlib import import_module
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .auth_store import get_profile
from .pan115_open_live import _cookie_header, _text, fetch_115_open_live_list, fetch_115_open_live_metadata


PAN115_OPEN_UPLOAD_INIT_URL = "https://proapi.115.com/open/upload/init"
PAN115_OPEN_UPLOAD_GET_TOKEN_URL = "https://proapi.115.com/open/upload/get_token"


@dataclass
class Pan115FastUploadResult:
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


def _normalize_access_token(value: str) -> str:
    token = _text(value)
    if token.lower().startswith("bearer "):
        return token[7:].strip()
    return token


def _load_profile_requirements(profile_id: str) -> tuple[object | None, str, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, "", ""
    extra = getattr(profile, "extra", {}) or {}
    access_token = _normalize_access_token(
        _text(
            getattr(profile, "token", "")
            or extra.get("authorization")
            or extra.get("Authorization")
            or extra.get("accessToken")
            or extra.get("access_token")
        )
    )
    return profile, access_token, _cookie_header(profile)


def _headers(access_token: str, cookie: str) -> dict[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 115Browser/27.0.5.7",
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://115.com/",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    if cookie:
        headers["Cookie"] = cookie
    return headers


def _target_value(parent_id: str) -> str:
    resolved = _text(parent_id) or "0"
    if resolved.startswith("U_"):
        return resolved
    return f"U_1_{resolved}"


def _compute_local_sha1s(file_path: Path) -> tuple[str, str]:
    outer = sha1()
    pre_hasher = sha1()
    remaining_pre_bytes = 128 * 1024
    with file_path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            outer.update(chunk)
            if remaining_pre_bytes > 0:
                pre_chunk = chunk[:remaining_pre_bytes]
                pre_hasher.update(pre_chunk)
                remaining_pre_bytes -= len(pre_chunk)
    return outer.hexdigest().upper(), pre_hasher.hexdigest().upper()


def _verify_local_sha1(file_path: Path, expected_sha1: str) -> tuple[bool, str, str]:
    actual_sha1, actual_preid = _compute_local_sha1s(file_path)
    normalized_expected = _text(expected_sha1).upper() or actual_sha1
    return normalized_expected == actual_sha1, actual_sha1, actual_preid


def _sign_check_sha1(file_path: Path, sign_check: str) -> str:
    start_text, end_text = _text(sign_check).split("-", 1)
    start = int(start_text)
    end = int(end_text)
    if start < 0 or end < start:
        raise ValueError(f"invalid_sign_check:{sign_check}")
    remaining = end - start + 1
    hasher = sha1()
    with file_path.open("rb") as handle:
        handle.seek(start)
        while remaining > 0:
            chunk = handle.read(min(remaining, 1024 * 1024))
            if not chunk:
                break
            hasher.update(chunk)
            remaining -= len(chunk)
    if remaining > 0:
        raise ValueError(f"incomplete_sign_check_range:{sign_check}")
    return hasher.hexdigest().upper()


def _post_form(url: str, form: dict[str, object], access_token: str, cookie: str) -> tuple[int, dict[str, object]]:
    request = Request(
        url=url,
        data=urlencode({k: v for k, v in form.items() if v is not None and v != ""}).encode("utf-8"),
        headers={
            **_headers(access_token, cookie),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text) if text else {}
    return status, payload if isinstance(payload, dict) else {}


def _extract_http_error_payload(exc: HTTPError) -> tuple[int, dict[str, object]]:
    try:
        text = exc.read().decode("utf-8", errors="replace")
    except Exception:
        text = ""
    try:
        payload = json.loads(text) if text else {}
    except json.JSONDecodeError:
        payload = {}
    return int(exc.code or 0), payload if isinstance(payload, dict) else {}


def _unwrap_response(payload: dict[str, object]) -> tuple[bool, dict[str, object], str, int]:
    if "state" in payload:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        return bool(payload.get("state")), data, _text(payload.get("message") or payload.get("msg")), int(payload.get("code", 0) or 0)
    return True, payload, "", 0


def _pick_text(data: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = _text(data.get(key))
        if value:
            return value
    return ""


def _classify_issue(status: int, error: str) -> tuple[str, str]:
    if error == "profile_not_found":
        return ("input", "targetProfileId 对应的 115 Open 授权档案不存在。")
    if error == "missing_auth":
        return ("auth", "补 access token 或 cookie 后再试 115 Open 秒传。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续做 115 Open 秒传。")
    if error == "local_sha1_mismatch":
        return ("input", "本地文件计算出的 sha1 与任务条目不一致，先校验来源文件。")
    if error == "rapid_upload_not_hit":
        return ("provider", "115 Open 已到达 upload/init，但当前没有命中秒传，后续仍需真实二进制上传 fallback。")
    if error == "missing_sign_check":
        return ("provider", "115 Open 返回了 sign_check 状态，但响应缺少可继续计算的字段。")
    if error == "missing_upload_token":
        return ("provider", "115 Open 未返回可用的 OSS 上传 token，当前无法继续二进制上传。")
    if error == "missing_upload_session":
        return ("provider", "115 Open upload/init 已返回 hash miss，但缺少完整 OSS 上传会话字段。")
    if error == "missing_oss2_dependency":
        return ("environment", "当前环境缺少 oss2，无法继续 115 Open 的 OSS 二进制上传。")
    if error == "binary_upload_failed":
        return ("provider", "115 Open OSS 二进制上传已开始，但上传过程中失败。")
    if error.startswith("http_error:401"):
        return ("auth", "115 Open 秒传请求被 401 拒绝，授权很可能已失效。")
    if error.startswith("http_error:403"):
        return ("risk", "115 Open 秒传请求被 403 拒绝，可能命中风控或权限不足。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "115 Open 秒传请求过快，建议稍后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "115 Open provider 侧接口异常，建议稍后重试。")
    if error.startswith("url_error:"):
        return ("network", "115 Open 秒传请求未能连通接口，请检查网络。")
    if error.startswith("unexpected:"):
        return ("unexpected", "115 Open 秒传过程异常中断，建议保留错误文本继续排查。")
    return ("", "")


def _request_upload_token(access_token: str, cookie: str) -> tuple[int, dict[str, object]]:
    request = Request(
        url=PAN115_OPEN_UPLOAD_GET_TOKEN_URL,
        headers=_headers(access_token, cookie),
        method="GET",
    )
    with urlopen(request, timeout=20) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text) if text else {}
    return status, payload if isinstance(payload, dict) else {}


def _normalize_endpoint(endpoint: str) -> str:
    resolved = _text(endpoint)
    if not resolved:
        return ""
    if resolved.startswith("http://") or resolved.startswith("https://"):
        return resolved
    return f"https://{resolved}"


def _extract_callback_payload(data: dict[str, object]) -> tuple[str, str]:
    callback = data.get("callback")
    if isinstance(callback, dict):
        value = callback.get("value") if isinstance(callback.get("value"), dict) else callback
        return (
            _text(value.get("callback")),
            _text(value.get("callback_var") or value.get("callbackVar")),
        )
    return "", ""


def _extract_upload_session(data: dict[str, object], token_payload: dict[str, object]) -> dict[str, object]:
    token_data = token_payload.get("data") if isinstance(token_payload.get("data"), dict) else token_payload
    if not isinstance(token_data, dict):
        token_data = {}
    callback_text, callback_var_text = _extract_callback_payload(data)
    return {
        "bucket": _pick_text(data, "bucket", "Bucket"),
        "object": _pick_text(data, "object", "Object"),
        "callback": callback_text,
        "callbackVar": callback_var_text,
        "endpoint": _normalize_endpoint(_pick_text(token_data, "endpoint", "Endpoint")),
        "accessKeyId": _pick_text(token_data, "access_key_id", "accessKeyId", "AccessKeyId"),
        "accessKeySecret": _pick_text(token_data, "access_key_secret", "accessKeySecret", "AccessKeySecret"),
        "securityToken": _pick_text(token_data, "security_token", "securityToken", "SecurityToken"),
    }


def _multipart_part_size(file_size: int) -> int:
    part_size = 20 * 1024 * 1024
    if file_size > part_size:
        if file_size > 1024**4:
            part_size = 5 * 1024**3
        elif file_size > 768 * 1024**3:
            part_size = 109951163
        elif file_size > 512 * 1024**3:
            part_size = 82463373
        elif file_size > 384 * 1024**3:
            part_size = 54975582
        elif file_size > 256 * 1024**3:
            part_size = 41231687
        elif file_size > 128 * 1024**3:
            part_size = 27487791
    return part_size


def _callback_headers(session: dict[str, object]) -> dict[str, str]:
    headers: dict[str, str] = {}
    callback_text = _text(session.get("callback"))
    callback_var_text = _text(session.get("callbackVar"))
    if callback_text:
        headers["x-oss-callback"] = base64.b64encode(callback_text.encode("utf-8")).decode("ascii")
    if callback_var_text:
        headers["x-oss-callback-var"] = base64.b64encode(callback_var_text.encode("utf-8")).decode("ascii")
    return headers


def _upload_binary_to_115_oss(file_path: Path, session: dict[str, object]) -> tuple[str, str, dict[str, object]]:
    bucket_name = _text(session.get("bucket"))
    object_key = _text(session.get("object"))
    endpoint = _text(session.get("endpoint"))
    access_key_id = _text(session.get("accessKeyId"))
    access_key_secret = _text(session.get("accessKeySecret"))
    security_token = _text(session.get("securityToken"))
    if not bucket_name or not object_key or not endpoint or not access_key_id or not access_key_secret or not security_token:
        return (
            "missing_upload_session",
            "115 Open hash-miss response did not include a complete OSS upload session.",
            {"session": session},
        )

    try:
        oss2 = import_module("oss2")
    except Exception as exc:  # pragma: no cover
        return (
            "missing_oss2_dependency",
            f"115 Open binary upload requires oss2 in the runtime environment: {exc}",
            {"session": session},
        )

    auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    callback_headers = _callback_headers(session)
    file_size = int(file_path.stat().st_size)
    part_size = _multipart_part_size(file_size)

    if file_size <= part_size:
        with file_path.open("rb") as handle:
            result = bucket.put_object(object_key, handle, headers=callback_headers or None)
        return (
            "",
            "",
            {
                "uploadKind": "single_part",
                "bucket": bucket_name,
                "object": object_key,
                "endpoint": endpoint,
                "status": int(getattr(result, "status", 0) or 0),
            },
        )

    upload = bucket.init_multipart_upload(object_key, headers=callback_headers or None)
    upload_id = _text(getattr(upload, "upload_id", ""))
    parts: list[object] = []
    part_number = 1
    with file_path.open("rb") as handle:
        while True:
            chunk = handle.read(part_size)
            if not chunk:
                break
            part = bucket.upload_part(object_key, upload_id, part_number, chunk)
            parts.append(oss2.models.PartInfo(part_number, getattr(part, "etag", ""), size=len(chunk)))
            part_number += 1
    result = bucket.complete_multipart_upload(object_key, upload_id, parts)
    return (
        "",
        "",
        {
            "uploadKind": "multipart",
            "bucket": bucket_name,
            "object": object_key,
            "endpoint": endpoint,
            "uploadId": upload_id,
            "partCount": len(parts),
            "status": int(getattr(result, "status", 0) or 0),
        },
    )


def _verify_uploaded_file(
    *,
    profile_id: str,
    parent_id: str,
    target_name: str,
    file_id: str,
    expected_sha1: str,
) -> tuple[bool, str, str, dict[str, object]]:
    resolved_file_id = _text(file_id)
    normalized_sha1 = _text(expected_sha1).upper()
    if resolved_file_id:
        metadata_result = fetch_115_open_live_metadata(profile_id=profile_id, file_id=resolved_file_id)
        if metadata_result.ok:
            entry = dict((metadata_result.payload or {}).get("entry") or {})
            entry_sha1 = _text(entry.get("sha1")).upper()
            verify_ok = not normalized_sha1 or not entry_sha1 or entry_sha1 == normalized_sha1
            return (
                verify_ok,
                "metadata_by_file_id",
                "Rapid-upload result was verified by 115 Open live metadata using the returned fileId.",
                {
                    "fileId": resolved_file_id,
                    "entry": entry,
                    "status": metadata_result.status,
                },
            )

    list_result = fetch_115_open_live_list(profile_id=profile_id, cid=parent_id or "0", limit=200)
    items = list((list_result.payload or {}).get("items") or []) if list_result.ok else []
    if list_result.ok:
        matched = next((item for item in items if _text(item.get("name")) == target_name), None)
        if matched is not None:
            matched_sha1 = _text(matched.get("sha1")).upper()
            verify_ok = not normalized_sha1 or not matched_sha1 or matched_sha1 == normalized_sha1
            return (
                verify_ok,
                "list_by_parent_name",
                "Rapid-upload result was verified by 115 Open live list using parentId + file name.",
                {
                    "matchedItem": matched,
                    "status": list_result.status,
                },
            )
        return (
            False,
            "list_by_parent_name",
            "Rapid-upload request succeeded, but 115 Open live list did not find the uploaded file name under the target parent yet.",
            {
                "status": list_result.status,
                "matched": False,
            },
        )

    return (
        False,
        "verify_unavailable",
        "Rapid-upload request succeeded, but post-upload verification could not confirm the file through metadata or list.",
        {
            "fileId": resolved_file_id,
            "listError": list_result.error,
            "listStatus": list_result.status,
        },
    )


def upload_115_open_fast_file(
    *,
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_id: str = "",
    expected_sha1: str = "",
) -> Pan115FastUploadResult:
    profile, access_token, cookie = _load_profile_requirements(profile_id)
    resolved_parent_id = _text(parent_id) or "0"
    if profile is None:
        risk_level, risk_hint = _classify_issue(0, "profile_not_found")
        return Pan115FastUploadResult(False, "profile_missing", False, profile_id, resolved_parent_id, 0, "profile_not_found", "Saved 115 Open auth profile was not found.", risk_level, risk_hint)
    if not access_token and not cookie:
        risk_level, risk_hint = _classify_issue(0, "missing_auth")
        return Pan115FastUploadResult(False, "profile_incomplete", True, profile.profileId, resolved_parent_id, 0, "missing_auth", "115 Open fast upload requires access token or cookie.", risk_level, risk_hint)

    file_path = Path(str(local_path or "").strip())
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_issue(0, "local_file_missing")
        return Pan115FastUploadResult(False, "local_file_missing", True, profile.profileId, resolved_parent_id, 0, "local_file_missing", "115 Open fast upload requires an existing local file.", risk_level, risk_hint)

    sha1_ok, actual_sha1, actual_preid = _verify_local_sha1(file_path, expected_sha1)
    if not sha1_ok:
        risk_level, risk_hint = _classify_issue(0, "local_sha1_mismatch")
        return Pan115FastUploadResult(
            False,
            "local_sha1_mismatch",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            "local_sha1_mismatch",
            "115 Open fast upload aborted because local sha1 does not match the task entry.",
            risk_level,
            risk_hint,
            payload={"actualSha1": actual_sha1, "preid": actual_preid},
        )

    base_form = {
        "file_name": _text(target_name or file_path.name) or file_path.name,
        "file_size": int(file_path.stat().st_size),
        "target": _target_value(resolved_parent_id),
        "fileid": actual_sha1,
        "preid": actual_preid,
        "topupload": 1,
        "pick_code": "",
        "sign_key": "",
        "sign_val": "",
    }

    try:
        status, initial_payload = _post_form(PAN115_OPEN_UPLOAD_INIT_URL, base_form, access_token, cookie)
        initial_state, initial_data, initial_message, initial_code = _unwrap_response(initial_payload)
        if not initial_state:
            risk_level, risk_hint = _classify_issue(status, f"http_error:{status}" if status else "unexpected:state_false")
            return Pan115FastUploadResult(
                False,
                "rapid_upload_request_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                status,
                f"open_state_false:{initial_code or status}",
                "115 Open rapid-upload init request reached the API but was rejected.",
                risk_level,
                risk_hint or initial_message,
                payload={"errorResponse": initial_payload, "sha1": actual_sha1, "preid": actual_preid},
            )

        final_payload = initial_payload
        final_data = initial_data
        second_attempt_payload: dict[str, object] | None = None
        second_sign_check = ""
        response_status = int(final_data.get("status", 0) or 0)

        if response_status in {6, 7, 8}:
            sign_key = _pick_text(final_data, "sign_key")
            second_sign_check = _pick_text(final_data, "sign_check")
            if not sign_key or not second_sign_check:
                risk_level, risk_hint = _classify_issue(status, "missing_sign_check")
                return Pan115FastUploadResult(
                    False,
                    "rapid_upload_not_hit",
                    True,
                    profile.profileId,
                    resolved_parent_id,
                    status,
                    "missing_sign_check",
                    "115 Open returned a sign-check status, but the response did not contain enough data for the follow-up verification request.",
                    risk_level,
                    risk_hint,
                    payload={
                        "initResponse": initial_payload,
                        "sha1": actual_sha1,
                        "preid": actual_preid,
                        "target": base_form["target"],
                    },
                    verifyOk=False,
                    verifyMode="create_response_status",
                    verifyNote="The live upload/init call reached 115 Open, but sign_check follow-up could not be completed from the returned payload.",
                    verifyPayload={"status": response_status},
                )
            sign_val = _sign_check_sha1(file_path, second_sign_check)
            followup_form = dict(base_form)
            followup_form["sign_key"] = sign_key
            followup_form["sign_val"] = sign_val
            second_attempt_payload = {
                "signKey": sign_key,
                "signCheck": second_sign_check,
                "signVal": sign_val,
            }
            status, final_payload = _post_form(PAN115_OPEN_UPLOAD_INIT_URL, followup_form, access_token, cookie)
            final_state, final_data, final_message, final_code = _unwrap_response(final_payload)
            if not final_state:
                risk_level, risk_hint = _classify_issue(status, f"http_error:{status}" if status else "unexpected:state_false")
                return Pan115FastUploadResult(
                    False,
                    "rapid_upload_request_failed",
                    True,
                    profile.profileId,
                    resolved_parent_id,
                    status,
                    f"open_state_false:{final_code or status}",
                    "115 Open rapid-upload sign-check follow-up reached the API but was rejected.",
                    risk_level,
                    risk_hint or final_message,
                    payload={
                        "initResponse": initial_payload,
                        "followupResponse": final_payload,
                        "secondAttempt": second_attempt_payload,
                        "sha1": actual_sha1,
                        "preid": actual_preid,
                    },
                )
            response_status = int(final_data.get("status", 0) or 0)

        file_id = _pick_text(final_data, "file_id", "fileId")
        pick_code = _pick_text(final_data, "pick_code", "pickCode")
        resolved_name = _text(base_form["file_name"])
        common_payload = {
            "initResponse": initial_payload,
            "followupResponse": final_payload if second_attempt_payload else {},
            "secondAttempt": second_attempt_payload or {},
            "fileId": file_id,
            "pickCode": pick_code,
            "resolvedTargetName": resolved_name,
            "conflictAction": "",
            "target": base_form["target"],
            "sha1": actual_sha1,
            "preid": actual_preid,
            "responseStatus": response_status,
        }

        if response_status == 2:
            verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
                profile_id=profile.profileId,
                parent_id=resolved_parent_id,
                target_name=resolved_name,
                file_id=file_id,
                expected_sha1=actual_sha1,
            )
            return Pan115FastUploadResult(
                True,
                "rapid_upload_by_hash",
                True,
                profile.profileId,
                resolved_parent_id,
                status,
                "",
                "115 Open rapid-upload init request succeeded and confirmed a hash-based reuse hit.",
                payload=common_payload,
                verifyOk=verify_ok,
                verifyMode=verify_mode,
                verifyNote=verify_note,
                verifyPayload=verify_payload,
            )

        token_status, token_payload = _request_upload_token(access_token, cookie)
        token_state, token_data, _, _ = _unwrap_response(token_payload)
        if not token_state:
            risk_level, risk_hint = _classify_issue(token_status, "missing_upload_token")
            return Pan115FastUploadResult(
                False,
                "rapid_upload_not_hit",
                True,
                profile.profileId,
                resolved_parent_id,
                token_status or status,
                "missing_upload_token",
                "115 Open upload/init reached the live API, but OSS upload token retrieval did not succeed.",
                risk_level,
                risk_hint,
                payload={
                    **common_payload,
                    "uploadTokenResponse": token_payload,
                },
                verifyOk=False,
                verifyMode="create_response_status",
                verifyNote="The live upload/init request reached 115 Open, but the follow-up OSS upload token was unavailable.",
                verifyPayload={"status": response_status, "signCheck": second_sign_check},
            )

        upload_session = _extract_upload_session(final_data, token_data)
        binary_error, binary_note, binary_payload = _upload_binary_to_115_oss(file_path, upload_session)
        payload = {
            **common_payload,
            "uploadTokenResponse": token_payload,
            "uploadSession": upload_session,
            "binaryUpload": binary_payload,
        }
        if binary_error:
            risk_level, risk_hint = _classify_issue(token_status or status, binary_error)
            return Pan115FastUploadResult(
                False,
                "binary_upload_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                token_status or status,
                binary_error,
                binary_note or "115 Open OSS binary upload failed.",
                risk_level,
                risk_hint,
                payload=payload,
                verifyOk=False,
                verifyMode="oss_upload_session",
                verifyNote="The live upload/init request reached 115 Open, but the OSS binary upload fallback did not complete.",
                verifyPayload={"status": response_status, "signCheck": second_sign_check},
            )

        verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
            profile_id=profile.profileId,
            parent_id=resolved_parent_id,
            target_name=resolved_name,
            file_id="",
            expected_sha1=actual_sha1,
        )
        return Pan115FastUploadResult(
            True,
            "binary_upload_after_hash_miss",
            True,
            profile.profileId,
            resolved_parent_id,
            token_status or status,
            "",
            "115 Open upload/init hash miss fell back to OSS binary upload and the uploaded file was verified afterwards.",
            payload=payload,
            verifyOk=verify_ok,
            verifyMode=verify_mode,
            verifyNote=verify_note,
            verifyPayload=verify_payload,
        )
    except HTTPError as exc:
        status, error_payload = _extract_http_error_payload(exc)
        risk_level, risk_hint = _classify_issue(status, f"http_error:{status}")
        return Pan115FastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            status,
            f"http_error:{status}",
            "115 Open rapid-upload init request reached the API but was rejected.",
            risk_level,
            risk_hint,
            payload={"errorResponse": error_payload, "sha1": actual_sha1, "preid": actual_preid},
        )
    except URLError as exc:
        risk_level, risk_hint = _classify_issue(0, f"url_error:{exc.reason}")
        return Pan115FastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            f"url_error:{exc.reason}",
            "115 Open rapid-upload init request could not reach the API endpoint.",
            risk_level,
            risk_hint,
            payload={"sha1": actual_sha1, "preid": actual_preid},
        )
    except json.JSONDecodeError:
        risk_level, risk_hint = _classify_issue(200, "unexpected:invalid_json")
        return Pan115FastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            200,
            "unexpected:invalid_json",
            "115 Open rapid-upload init request returned non-JSON content.",
            risk_level,
            risk_hint,
            payload={"sha1": actual_sha1, "preid": actual_preid},
        )
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_issue(0, f"unexpected:{exc}")
        return Pan115FastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            f"unexpected:{exc}",
            "115 Open rapid-upload init request failed unexpectedly.",
            risk_level,
            risk_hint,
            payload={"sha1": actual_sha1, "preid": actual_preid},
        )
