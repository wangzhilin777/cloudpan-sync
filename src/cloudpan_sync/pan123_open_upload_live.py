from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import md5
from pathlib import Path, PurePosixPath
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .auth_store import get_profile
from .pan123_open_live import fetch_123_open_live_list, fetch_123_open_live_metadata


@dataclass
class Pan123OpenUploadResult:
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


PAN123_OPEN_UPLOAD_CREATE_PATH = "/upload/v1/oss/file/create"
PAN123_OPEN_UPLOAD_URL_PATH = "/upload/v1/oss/file/get_upload_url"
PAN123_OPEN_UPLOAD_COMPLETE_PATH = "/upload/v1/oss/file/upload_complete"
PAN123_OPEN_UPLOAD_ASYNC_RESULT_PATH = "/upload/v1/oss/file/upload_async_result"
PAN123_OPEN_HOST = "https://open-api.123pan.com"


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


def _post_json(path: str, body: dict[str, object], auth: str) -> tuple[int, dict[str, object]]:
    request = Request(
        url=f"{PAN123_OPEN_HOST}{path}",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={**_headers(auth), "Content-Type": "application/json;charset=UTF-8"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text) if text else {}
    return status, payload if isinstance(payload, dict) else {}


def _put_file(upload_url: str, file_path: Path) -> int:
    request = Request(
        url=upload_url,
        data=file_path.read_bytes(),
        headers={
            "User-Agent": "CloudPanSync/0.1",
            "Content-Type": "application/octet-stream",
        },
        method="PUT",
    )
    with urlopen(request, timeout=60) as response:
        return int(getattr(response, "status", 0) or 0)


def _verify_local_md5(local_path: Path, expected_md5: str) -> bool:
    expected = _text(expected_md5).lower()
    if not expected:
        return True
    hasher = md5()
    with local_path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest().lower() == expected


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
    parent_file_id: str,
    target_name: str,
    conflict_policy: str,
) -> tuple[str, str, str]:
    list_result = fetch_123_open_live_list(profile_id=profile_id, parent_file_id=parent_file_id or "0", limit=200)
    if not list_result.ok:
        return target_name, "conflict_check_unavailable", "Could not verify same-name conflicts before 123Pan Open upload, so the original file name was kept."

    existing_names = {
        _text(item.get("name"))
        for item in list((list_result.payload or {}).get("items") or [])
        if _text(item.get("name"))
    }
    if target_name not in existing_names:
        return target_name, "no_conflict", ""

    index = 1
    candidate = _build_renamed_candidate(target_name, index)
    while candidate in existing_names:
        index += 1
        candidate = _build_renamed_candidate(target_name, index)
    if conflict_policy == "auto_rename_new":
        return candidate, "auto_rename_new", "A same-name file already exists under the target path, so 123Pan Open upload auto-renamed the new file."
    return candidate, "overwrite_downgraded_to_auto_rename", "The requested overwrite policy was downgraded because the current 123Pan Open upload path does not support verified in-place overwrite."


def _classify_upload_issue(status: int, error: str) -> tuple[str, str]:
    if error == "profile_not_found":
        return ("input", "targetProfileId 对应的 123Pan Open 授权档案不存在。")
    if error == "missing_access_token":
        return ("auth", "补 token 或 extra.authorization 后再试 123Pan Open 上传。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续上传。")
    if error == "local_md5_mismatch":
        return ("input", "本地文件 MD5 与任务条目不一致，先校验来源文件。")
    if error == "missing_preupload_id":
        return ("provider", "123Pan Open 创建文件未返回 preuploadID，当前无法继续上传。")
    if error == "missing_presigned_url":
        return ("provider", "123Pan Open 获取上传地址未返回 presignedURL，当前无法继续上传。")
    if error.startswith("http_error:401"):
        return ("auth", "上传请求被 401 拒绝，授权很可能已失效。")
    if error.startswith("http_error:403"):
        return ("risk", "上传请求被 403 拒绝，可能命中风控或缺必要权限。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "上传请求过快，建议降并发稍后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "Provider 侧上传接口异常，建议稍后重试。")
    if error.startswith("unexpected:"):
        return ("unexpected", "上传过程异常中断，建议保留错误文本继续排查。")
    return ("", "")


def _poll_upload_result(auth: str, preupload_id: str, attempts: int = 4) -> tuple[int, dict[str, object]]:
    latest_status = 0
    latest_payload: dict[str, object] = {}
    for index in range(max(1, attempts)):
        latest_status, latest_payload = _post_json(
            PAN123_OPEN_UPLOAD_ASYNC_RESULT_PATH,
            {"preuploadID": preupload_id},
            auth,
        )
        data = latest_payload.get("data") if isinstance(latest_payload.get("data"), dict) else {}
        if bool((data or {}).get("completed")):
            break
        if index + 1 < attempts:
            sleep(1)
    return latest_status, latest_payload


def _verify_uploaded_file(
    *,
    profile_id: str,
    parent_file_id: str,
    target_name: str,
    file_id: str,
) -> tuple[bool, str, str, dict[str, object]]:
    resolved_parent_id = _text(parent_file_id) or "0"
    resolved_file_id = _text(file_id)
    if resolved_file_id:
        metadata_result = fetch_123_open_live_metadata(
            profile_id=profile_id,
            file_id=resolved_file_id,
            parent_file_id=resolved_parent_id,
        )
        if metadata_result.ok:
            return (
                True,
                "metadata_by_file_id",
                "Upload result was verified by 123Pan Open live metadata using the returned fileId.",
                {
                    "fileId": resolved_file_id,
                    "entry": dict((metadata_result.payload or {}).get("entry") or {}),
                    "status": metadata_result.status,
                },
            )

    list_result = fetch_123_open_live_list(profile_id=profile_id, parent_file_id=resolved_parent_id, limit=200)
    items = list((list_result.payload or {}).get("items") or []) if list_result.ok else []
    if list_result.ok:
        matched = next((item for item in items if _text(item.get("name")) == target_name), None)
        if matched is not None:
            return (
                True,
                "list_by_parent_name",
                "Upload result was verified by 123Pan Open live list using parentFileId + file name.",
                {
                    "matchedItem": matched,
                    "status": list_result.status,
                },
            )
        return (
            False,
            "list_by_parent_name",
            "Upload request succeeded, but 123Pan Open live list did not find the uploaded file name under the target parent yet.",
            {
                "status": list_result.status,
                "matched": False,
            },
        )
    return (
        False,
        "verify_unavailable",
        "Upload request succeeded, but post-upload verification could not confirm the file through metadata or list.",
        {
            "fileId": resolved_file_id,
            "listError": list_result.error,
            "listStatus": list_result.status,
        },
    )


def upload_123_open_local_file(
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_file_id: str = "0",
    expected_md5: str = "",
    conflict_policy: str = "auto_rename_new",
) -> Pan123OpenUploadResult:
    profile, auth = _load_profile_requirements(profile_id)
    if profile is None:
        risk_level, risk_hint = _classify_upload_issue(0, "profile_not_found")
        return Pan123OpenUploadResult(
            ok=False,
            mode="profile_missing",
            usedProfile=False,
            profileId=profile_id,
            parentId="",
            status=0,
            error="profile_not_found",
            note="Saved 123Pan Open auth profile was not found.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    if not auth:
        risk_level, risk_hint = _classify_upload_issue(0, "missing_access_token")
        return Pan123OpenUploadResult(
            ok=False,
            mode="profile_incomplete",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_access_token",
            note="123Pan Open binary upload requires token or extra.authorization.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    file_path = Path(local_path)
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_upload_issue(0, "local_file_missing")
        return Pan123OpenUploadResult(
            ok=False,
            mode="local_missing",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="local_file_missing",
            note="Local file for 123Pan Open binary upload does not exist.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    if not _verify_local_md5(file_path, expected_md5):
        risk_level, risk_hint = _classify_upload_issue(0, "local_md5_mismatch")
        return Pan123OpenUploadResult(
            ok=False,
            mode="input_mismatch",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=_text(parent_file_id) or "0",
            status=0,
            error="local_md5_mismatch",
            note="Local file content does not match the expected md5 fingerprint.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    resolved_parent_id = _text(parent_file_id or profile.extra.get("parentFileId") or profile.extra.get("parentId") or "0")
    resolved_target_name, conflict_action, conflict_note = _resolve_upload_target_name(
        profile_id=profile.profileId,
        parent_file_id=resolved_parent_id,
        target_name=_text(target_name) or file_path.name,
        conflict_policy=conflict_policy,
    )
    create_payload: dict[str, object] = {}
    get_upload_payload: dict[str, object] = {}
    complete_payload: dict[str, object] = {}
    async_payload: dict[str, object] = {}
    preupload_id = ""
    file_id = ""
    try:
        create_status, create_payload = _post_json(
            PAN123_OPEN_UPLOAD_CREATE_PATH,
            {
                "parentFileID": resolved_parent_id,
                "filename": resolved_target_name,
                "etag": _verify_local_md5(file_path, "") and md5(file_path.read_bytes()).hexdigest(),
                "size": int(file_path.stat().st_size),
                "type": 1,
            },
            auth,
        )
        create_data = create_payload.get("data") if isinstance(create_payload.get("data"), dict) else {}
        preupload_id = _text((create_data or {}).get("preuploadID"))
        file_id = _text((create_data or {}).get("fileID"))
        if bool((create_data or {}).get("reuse")) and file_id:
            verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
                profile_id=profile.profileId,
                parent_file_id=resolved_parent_id,
                target_name=resolved_target_name,
                file_id=file_id,
            )
            return Pan123OpenUploadResult(
                ok=True,
                mode="binary_upload_reuse_hit",
                usedProfile=True,
                profileId=profile.profileId,
                parentId=resolved_parent_id,
                status=create_status,
                error="",
                note=f"123Pan Open create file reported a provider-side reuse hit.{(' ' + conflict_note) if conflict_note else ''}",
                payload={
                    "createResponse": create_payload,
                    "fileId": file_id,
                    "preuploadID": preupload_id,
                    "resolvedTargetName": resolved_target_name,
                    "conflictAction": conflict_action,
                },
                verifyOk=verify_ok,
                verifyMode=verify_mode,
                verifyNote=verify_note,
                verifyPayload=verify_payload,
            )
        if not preupload_id:
            risk_level, risk_hint = _classify_upload_issue(create_status, "missing_preupload_id")
            return Pan123OpenUploadResult(
                ok=False,
                mode="create_failed",
                usedProfile=True,
                profileId=profile.profileId,
                parentId=resolved_parent_id,
                status=create_status,
                error="missing_preupload_id",
                note="123Pan Open create file succeeded but did not return preuploadID.",
                riskLevel=risk_level,
                riskHint=risk_hint,
                payload={
                    "createResponse": create_payload,
                    "resolvedTargetName": resolved_target_name,
                    "conflictAction": conflict_action,
                },
            )

        upload_status, get_upload_payload = _post_json(
            PAN123_OPEN_UPLOAD_URL_PATH,
            {"preuploadID": preupload_id, "sliceNo": 1},
            auth,
        )
        upload_data = get_upload_payload.get("data") if isinstance(get_upload_payload.get("data"), dict) else {}
        presigned_url = _text((upload_data or {}).get("presignedURL"))
        if not presigned_url:
            risk_level, risk_hint = _classify_upload_issue(upload_status, "missing_presigned_url")
            return Pan123OpenUploadResult(
                ok=False,
                mode="upload_url_missing",
                usedProfile=True,
                profileId=profile.profileId,
                parentId=resolved_parent_id,
                status=upload_status,
                error="missing_presigned_url",
                note="123Pan Open get_upload_url did not return presignedURL.",
                riskLevel=risk_level,
                riskHint=risk_hint,
                payload={
                    "createResponse": create_payload,
                    "getUploadUrlResponse": get_upload_payload,
                    "preuploadID": preupload_id,
                    "resolvedTargetName": resolved_target_name,
                    "conflictAction": conflict_action,
                },
            )

        put_status = _put_file(presigned_url, file_path)
        complete_status, complete_payload = _post_json(
            PAN123_OPEN_UPLOAD_COMPLETE_PATH,
            {"preuploadID": preupload_id},
            auth,
        )
        complete_data = complete_payload.get("data") if isinstance(complete_payload.get("data"), dict) else {}
        async_status = complete_status
        if bool((complete_data or {}).get("async")) and not bool((complete_data or {}).get("completed")):
            async_status, async_payload = _poll_upload_result(auth, preupload_id)
        async_data = async_payload.get("data") if isinstance(async_payload.get("data"), dict) else {}
        resolved_file_id = _text((async_data or {}).get("fileID") or (complete_data or {}).get("fileID") or file_id)
        verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
            profile_id=profile.profileId,
            parent_file_id=resolved_parent_id,
            target_name=resolved_target_name,
            file_id=resolved_file_id,
        )
        return Pan123OpenUploadResult(
            ok=True,
            mode="binary_upload_single_part",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=async_status,
            error="",
            note=f"123Pan Open binary upload completed through create + get_upload_url + single-part PUT + upload_complete.{(' ' + conflict_note) if conflict_note else ''}",
            payload={
                "createResponse": create_payload,
                "getUploadUrlResponse": get_upload_payload,
                "uploadCompleteResponse": complete_payload,
                "uploadAsyncResultResponse": async_payload,
                "preuploadID": preupload_id,
                "fileId": resolved_file_id,
                "putStatus": put_status,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
            verifyOk=verify_ok,
            verifyMode=verify_mode,
            verifyNote=verify_note,
            verifyPayload=verify_payload,
        )
    except HTTPError as exc:
        status = int(exc.code or 0)
        error = f"http_error:{status}"
        risk_level, risk_hint = _classify_upload_issue(status, error)
        return Pan123OpenUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=status,
            error=error,
            note="123Pan Open binary upload request reached the API but was rejected.",
            riskLevel=risk_level,
            riskHint=risk_hint,
            payload={
                "createResponse": create_payload,
                "getUploadUrlResponse": get_upload_payload,
                "uploadCompleteResponse": complete_payload,
                "uploadAsyncResultResponse": async_payload,
                "preuploadID": preupload_id,
                "fileId": file_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
    except URLError as exc:
        return Pan123OpenUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error=f"url_error:{exc.reason}",
            note="123Pan Open binary upload could not reach the API endpoint.",
            riskLevel="provider",
            riskHint="上传请求未能连通 123Pan Open 接口，请检查网络、域名或代理设置。",
            payload={
                "createResponse": create_payload,
                "getUploadUrlResponse": get_upload_payload,
                "uploadCompleteResponse": complete_payload,
                "uploadAsyncResultResponse": async_payload,
                "preuploadID": preupload_id,
                "fileId": file_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
    except json.JSONDecodeError:
        return Pan123OpenUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=200,
            error="invalid_json",
            note="123Pan Open upload returned non-JSON content during the create/complete flow.",
            riskLevel="provider",
            riskHint="Provider 返回内容格式异常，建议保留原始响应继续排查。",
            payload={
                "createResponse": create_payload,
                "getUploadUrlResponse": get_upload_payload,
                "uploadCompleteResponse": complete_payload,
                "uploadAsyncResultResponse": async_payload,
                "preuploadID": preupload_id,
                "fileId": file_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
    except Exception as exc:  # pragma: no cover
        error = f"unexpected:{exc}"
        risk_level, risk_hint = _classify_upload_issue(0, error)
        return Pan123OpenUploadResult(
            ok=False,
            mode="unexpected_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error=error,
            note="123Pan Open binary upload failed unexpectedly.",
            riskLevel=risk_level,
            riskHint=risk_hint,
            payload={
                "createResponse": create_payload,
                "getUploadUrlResponse": get_upload_payload,
                "uploadCompleteResponse": complete_payload,
                "uploadAsyncResultResponse": async_payload,
                "preuploadID": preupload_id,
                "fileId": file_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
