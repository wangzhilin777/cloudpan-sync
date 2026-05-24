from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import md5
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .auth_store import get_profile
from .baidu_netdisk_live import (
    _headers,
    _join_path,
    _load_profile_requirements,
    _normalize_dir_path,
    _post_form,
    _text,
    fetch_baidu_live_list,
    fetch_baidu_live_metadata,
)


@dataclass
class BaiduNetdiskUploadResult:
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


BAIDU_PCS_UPLOAD_HOST = "https://d.pcs.baidu.com"
BAIDU_PCS_UPLOAD_PATH = "/rest/2.0/pcs/superfile2"


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
    parent_dir: str,
    target_name: str,
    conflict_policy: str,
) -> tuple[str, str, str]:
    list_result = fetch_baidu_live_list(profile_id=profile_id, dir_path=parent_dir, limit=200)
    if not list_result.ok:
        return target_name, "conflict_check_unavailable", "Could not verify same-name conflicts before Baidu Netdisk upload, so the original file name was kept."

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
        return candidate, "auto_rename_new", "A same-name file already exists under the target path, so Baidu Netdisk upload auto-renamed the new file."
    return candidate, "overwrite_downgraded_to_auto_rename", "The requested overwrite policy was downgraded because the current Baidu Netdisk upload path does not support verified in-place overwrite."


def _classify_upload_issue(status: int, error: str) -> tuple[str, str]:
    if error == "profile_not_found":
        return ("input", "targetProfileId 对应的百度网盘授权档案不存在。")
    if error == "missing_access":
        return ("auth", "补 access token 或 cookie 后再试百度网盘上传。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续上传。")
    if error == "local_md5_mismatch":
        return ("input", "本地文件 MD5 与任务条目不一致，先校验来源文件。")
    if error == "missing_uploadid":
        return ("provider", "Baidu Netdisk precreate 未返回 uploadid，当前无法继续上传。")
    if error == "missing_md5":
        return ("input", "Baidu Netdisk precreate 需要 md5，当前文件指纹不足。")
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


def _post_multipart_tmpfile(
    *,
    access_token: str,
    cookie: str,
    remote_path: str,
    upload_id: str,
    file_path: Path,
) -> tuple[int, dict[str, object]]:
    boundary = "----CloudPanSyncBaiduBoundary7MA4YWxkTrZu0gW"
    file_bytes = file_path.read_bytes()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            b'Content-Disposition: form-data; name="file"; filename="blob"\r\n',
            b"Content-Type: application/octet-stream\r\n\r\n",
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    query = {
        "method": "upload",
        "type": "tmpfile",
        "path": remote_path,
        "partseq": "0",
        "uploadid": upload_id,
    }
    if access_token:
        query["access_token"] = access_token
    request = Request(
        url=f"{BAIDU_PCS_UPLOAD_HOST}{BAIDU_PCS_UPLOAD_PATH}?{urlencode(query)}",
        data=body,
        headers={
            **_headers(cookie),
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    with urlopen(request, timeout=60) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text) if text else {}
    return status, payload if isinstance(payload, dict) else {}


def _verify_uploaded_file(
    *,
    profile_id: str,
    parent_dir: str,
    remote_path: str,
    file_id: str,
) -> tuple[bool, str, str, dict[str, object]]:
    resolved_file_id = _text(file_id)
    if resolved_file_id:
        metadata_result = fetch_baidu_live_metadata(profile_id=profile_id, file_id=resolved_file_id, path=remote_path)
        if metadata_result.ok:
            return (
                True,
                "metadata_by_file_id",
                "Upload result was verified by Baidu Netdisk live metadata using the returned fs_id.",
                {
                    "fileId": resolved_file_id,
                    "entry": dict((metadata_result.payload or {}).get("entry") or {}),
                    "status": metadata_result.status,
                },
            )
    list_result = fetch_baidu_live_list(profile_id=profile_id, dir_path=parent_dir, limit=200)
    items = list((list_result.payload or {}).get("items") or []) if list_result.ok else []
    if list_result.ok:
        matched = next((item for item in items if _text(item.get("path")) == remote_path), None)
        if matched is not None:
            return (
                True,
                "list_by_parent_name",
                "Upload result was verified by Baidu Netdisk live list using parent dir + file name.",
                {
                    "matchedItem": matched,
                    "status": list_result.status,
                },
            )
        return (
            False,
            "list_by_parent_name",
            "Upload request succeeded, but Baidu Netdisk live list did not find the uploaded file under the target directory yet.",
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


def upload_baidu_local_file(
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_dir: str = "/",
    expected_md5: str = "",
    conflict_policy: str = "auto_rename_new",
) -> BaiduNetdiskUploadResult:
    profile, access_token, cookie = _load_profile_requirements(profile_id)
    if profile is None:
        risk_level, risk_hint = _classify_upload_issue(0, "profile_not_found")
        return BaiduNetdiskUploadResult(
            ok=False,
            mode="profile_missing",
            usedProfile=False,
            profileId=profile_id,
            parentId="",
            status=0,
            error="profile_not_found",
            note="Saved Baidu Netdisk auth profile was not found.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    if not access_token and not cookie:
        risk_level, risk_hint = _classify_upload_issue(0, "missing_access")
        return BaiduNetdiskUploadResult(
            ok=False,
            mode="profile_incomplete",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_access",
            note="Baidu Netdisk binary upload requires access token or cookie.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    file_path = Path(local_path)
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_upload_issue(0, "local_file_missing")
        return BaiduNetdiskUploadResult(
            ok=False,
            mode="local_missing",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="local_file_missing",
            note="Local file for Baidu Netdisk binary upload does not exist.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    if not _verify_local_md5(file_path, expected_md5):
        risk_level, risk_hint = _classify_upload_issue(0, "local_md5_mismatch")
        return BaiduNetdiskUploadResult(
            ok=False,
            mode="input_mismatch",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=_normalize_dir_path(parent_dir),
            status=0,
            error="local_md5_mismatch",
            note="Local file content does not match the expected md5 fingerprint.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    resolved_parent_dir = _normalize_dir_path(parent_dir or profile.extra.get("dir") or profile.extra.get("pathPrefix") or "/")
    local_md5 = expected_md5.lower() if _text(expected_md5) else md5(file_path.read_bytes()).hexdigest().lower()
    if not local_md5:
        risk_level, risk_hint = _classify_upload_issue(0, "missing_md5")
        return BaiduNetdiskUploadResult(
            ok=False,
            mode="input_incomplete",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_dir,
            status=0,
            error="missing_md5",
            note="Baidu Netdisk upload requires md5 for precreate.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    resolved_target_name, conflict_action, conflict_note = _resolve_upload_target_name(
        profile_id=profile.profileId,
        parent_dir=resolved_parent_dir,
        target_name=_text(target_name) or file_path.name,
        conflict_policy=conflict_policy,
    )
    remote_path = _join_path(resolved_parent_dir, resolved_target_name)
    precreate_payload: dict[str, object] = {}
    tmpfile_payload: dict[str, object] = {}
    create_payload: dict[str, object] = {}
    upload_id = ""
    file_id = ""
    try:
        precreate_status, precreate_payload = _post_form(
            "precreate",
            {
                "path": remote_path,
                "size": str(file_path.stat().st_size),
                "isdir": "0",
                "autoinit": "1",
                "rtype": "1",
                "block_list": json.dumps([local_md5], ensure_ascii=False),
                "content-md5": local_md5,
                "slice-md5": local_md5,
            },
            access_token,
            cookie,
        )
        upload_id = _text(precreate_payload.get("uploadid"))
        if not upload_id:
            risk_level, risk_hint = _classify_upload_issue(precreate_status, "missing_uploadid")
            return BaiduNetdiskUploadResult(
                ok=False,
                mode="precreate_failed",
                usedProfile=True,
                profileId=profile.profileId,
                parentId=resolved_parent_dir,
                status=precreate_status,
                error="missing_uploadid",
                note="Baidu Netdisk precreate succeeded but did not return uploadid.",
                riskLevel=risk_level,
                riskHint=risk_hint,
                payload={
                    "precreateResponse": precreate_payload,
                    "resolvedTargetName": resolved_target_name,
                    "conflictAction": conflict_action,
                },
            )
        tmpfile_status, tmpfile_payload = _post_multipart_tmpfile(
            access_token=access_token,
            cookie=cookie,
            remote_path=remote_path,
            upload_id=upload_id,
            file_path=file_path,
        )
        create_status, create_payload = _post_form(
            "create",
            {
                "path": remote_path,
                "size": str(file_path.stat().st_size),
                "isdir": "0",
                "rtype": "1",
                "uploadid": upload_id,
                "block_list": json.dumps([local_md5], ensure_ascii=False),
            },
            access_token,
            cookie,
        )
        file_id = _text(create_payload.get("fs_id") or create_payload.get("fsid"))
        verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
            profile_id=profile.profileId,
            parent_dir=resolved_parent_dir,
            remote_path=remote_path,
            file_id=file_id,
        )
        return BaiduNetdiskUploadResult(
            ok=True,
            mode="binary_upload_single_part",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_dir,
            status=create_status or tmpfile_status or precreate_status,
            error="",
            note=f"Baidu Netdisk binary upload completed through precreate + superfile2 tmpfile + create.{(' ' + conflict_note) if conflict_note else ''}",
            payload={
                "precreateResponse": precreate_payload,
                "tmpfileResponse": tmpfile_payload,
                "createResponse": create_payload,
                "uploadId": upload_id,
                "fileId": file_id,
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
        return BaiduNetdiskUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_dir,
            status=status,
            error=error,
            note="Baidu Netdisk binary upload request reached the API but was rejected.",
            riskLevel=risk_level,
            riskHint=risk_hint,
            payload={
                "precreateResponse": precreate_payload,
                "tmpfileResponse": tmpfile_payload,
                "createResponse": create_payload,
                "uploadId": upload_id,
                "fileId": file_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
    except URLError as exc:
        return BaiduNetdiskUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_dir,
            status=0,
            error=f"url_error:{exc.reason}",
            note="Baidu Netdisk binary upload could not reach the API endpoint.",
            riskLevel="provider",
            riskHint="上传请求未能连通百度网盘接口，请检查网络、代理或目标域名。",
            payload={
                "precreateResponse": precreate_payload,
                "tmpfileResponse": tmpfile_payload,
                "createResponse": create_payload,
                "uploadId": upload_id,
                "fileId": file_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
    except json.JSONDecodeError:
        return BaiduNetdiskUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_dir,
            status=200,
            error="invalid_json",
            note="Baidu Netdisk upload returned non-JSON content during the precreate/upload/create flow.",
            riskLevel="provider",
            riskHint="Provider 返回内容格式异常，建议保留原始响应继续排查。",
            payload={
                "precreateResponse": precreate_payload,
                "tmpfileResponse": tmpfile_payload,
                "createResponse": create_payload,
                "uploadId": upload_id,
                "fileId": file_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
    except Exception as exc:  # pragma: no cover
        error = f"unexpected:{exc}"
        risk_level, risk_hint = _classify_upload_issue(0, error)
        return BaiduNetdiskUploadResult(
            ok=False,
            mode="unexpected_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_dir,
            status=0,
            error=error,
            note="Baidu Netdisk binary upload failed unexpectedly.",
            riskLevel=risk_level,
            riskHint=risk_hint,
            payload={
                "precreateResponse": precreate_payload,
                "tmpfileResponse": tmpfile_payload,
                "createResponse": create_payload,
                "uploadId": upload_id,
                "fileId": file_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
