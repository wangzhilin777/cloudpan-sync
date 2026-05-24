from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import md5
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .aliyun_open_live import fetch_aliyun_open_live_list, fetch_aliyun_open_live_metadata
from .auth_store import get_profile


@dataclass
class AliyunOpenUploadResult:
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


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _auth_header(value: str) -> str:
    token = _text(value)
    if not token:
        return ""
    return token if token.lower().startswith("bearer ") else f"Bearer {token}"


def _domain_host(domain_id: str) -> str:
    return f"https://{domain_id}.api.aliyunpds.com"


def _load_profile_requirements(profile_id: str) -> tuple[object | None, str, str, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, "", "", ""
    auth = _auth_header(profile.token or profile.extra.get("authorization", ""))
    domain_id = _text(profile.extra.get("domainId") or profile.extra.get("domain_id"))
    drive_id = _text(profile.extra.get("driveId") or profile.extra.get("drive_id"))
    return profile, auth, domain_id, drive_id


def _post_json(url: str, body: dict[str, object], auth: str) -> tuple[int, dict[str, object]]:
    request = Request(
        url=url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "User-Agent": "CloudPanSync/0.1",
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": auth,
        },
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


def _classify_upload_issue(status: int, error: str) -> tuple[str, str]:
    if error == "profile_not_found":
        return ("input", "targetProfileId 对应的 Aliyun Drive Open 授权档案不存在。")
    if error == "missing_access_token":
        return ("auth", "补 token 或 extra.authorization 后再试 Aliyun 上传。")
    if error == "missing_domain_or_drive_id":
        return ("input", "先补 extra.domainId 和 extra.driveId，再做 Aliyun 上传。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续上传。")
    if error == "local_md5_mismatch":
        return ("input", "本地文件 MD5 与任务条目不一致，先校验来源文件。")
    if error == "missing_file_id":
        return ("provider", "Aliyun create file 未返回 fileId，当前无法继续确认上传。")
    if error == "missing_upload_url":
        return ("provider", "Aliyun create file 未返回 upload_url，当前无法继续上传分片。")
    if error.startswith("http_error:401"):
        return ("auth", "上传请求被 401 拒绝，授权很可能已失效。")
    if error.startswith("http_error:403"):
        return ("risk", "上传请求被 403 拒绝，可能命中风控或缺必要权限。")
    if error.startswith("http_error:409"):
        return ("conflict", "Aliyun 同名文件处理被拒绝，建议改用 auto_rename_new 或检查 overwrite 能力。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "上传请求过快，建议降并发稍后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "Provider 侧上传接口异常，建议稍后重试。")
    if error.startswith("unexpected:"):
        return ("unexpected", "上传过程异常中断，建议保留错误文本继续排查。")
    return ("", "")


def _extract_upload_url(payload: dict[str, object]) -> str:
    rows = payload.get("part_info_list")
    if not isinstance(rows, list):
        return ""
    for item in rows:
        if not isinstance(item, dict):
            continue
        upload_url = _text(item.get("upload_url"))
        if upload_url:
            return upload_url
    return ""


def _resolve_conflict_action(conflict_policy: str, requested_name: str, resolved_name: str) -> str:
    if resolved_name and resolved_name != requested_name:
        return "auto_rename_new"
    if conflict_policy == "overwrite_existing":
        return "overwrite_existing"
    return "no_conflict"


def _verify_uploaded_file(
    *,
    profile_id: str,
    parent_id: str,
    target_name: str,
    file_id: str,
) -> tuple[bool, str, str, dict[str, object]]:
    resolved_file_id = _text(file_id)
    if resolved_file_id:
        metadata_result = fetch_aliyun_open_live_metadata(profile_id=profile_id, file_id=resolved_file_id)
        if metadata_result.ok:
            return (
                True,
                "metadata_by_file_id",
                "Upload result was verified by Aliyun Drive Open live metadata using the returned fileId.",
                {
                    "fileId": resolved_file_id,
                    "entry": dict((metadata_result.payload or {}).get("entry") or {}),
                    "status": metadata_result.status,
                },
            )

    list_result = fetch_aliyun_open_live_list(profile_id=profile_id, parent_file_id=parent_id or "root", limit=200)
    items = list((list_result.payload or {}).get("items") or []) if list_result.ok else []
    if list_result.ok:
        matched = next((item for item in items if _text(item.get("name")) == target_name), None)
        if matched is not None:
            return (
                True,
                "list_by_parent_name",
                "Upload result was verified by Aliyun Drive Open live list using parent_file_id + file name.",
                {
                    "matchedItem": matched,
                    "status": list_result.status,
                },
            )
        return (
            False,
            "list_by_parent_name",
            "Upload request succeeded, but Aliyun Drive Open live list did not find the uploaded file name under the target parent yet.",
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


def upload_aliyun_open_local_file(
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_file_id: str = "root",
    expected_md5: str = "",
    conflict_policy: str = "auto_rename_new",
) -> AliyunOpenUploadResult:
    profile, auth, domain_id, drive_id = _load_profile_requirements(profile_id)
    if profile is None:
        risk_level, risk_hint = _classify_upload_issue(0, "profile_not_found")
        return AliyunOpenUploadResult(
            ok=False,
            mode="profile_missing",
            usedProfile=False,
            profileId=profile_id,
            parentId="",
            status=0,
            error="profile_not_found",
            note="Saved Aliyun Drive Open auth profile was not found.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    if not auth:
        risk_level, risk_hint = _classify_upload_issue(0, "missing_access_token")
        return AliyunOpenUploadResult(
            ok=False,
            mode="profile_incomplete",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_access_token",
            note="Aliyun Drive Open binary upload requires token or extra.authorization.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    if not domain_id or not drive_id:
        risk_level, risk_hint = _classify_upload_issue(0, "missing_domain_or_drive_id")
        return AliyunOpenUploadResult(
            ok=False,
            mode="profile_incomplete",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_domain_or_drive_id",
            note="Aliyun Drive Open binary upload requires extra.domainId and extra.driveId.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    file_path = Path(local_path)
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_upload_issue(0, "local_file_missing")
        return AliyunOpenUploadResult(
            ok=False,
            mode="local_missing",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="local_file_missing",
            note="Local file for Aliyun Drive Open binary upload does not exist.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    if not _verify_local_md5(file_path, expected_md5):
        risk_level, risk_hint = _classify_upload_issue(0, "local_md5_mismatch")
        return AliyunOpenUploadResult(
            ok=False,
            mode="input_mismatch",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=_text(parent_file_id) or "root",
            status=0,
            error="local_md5_mismatch",
            note="Local file content does not match the expected md5 fingerprint.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    resolved_parent_id = _text(parent_file_id) or "root"
    check_name_mode = "overwrite" if conflict_policy == "overwrite_existing" else "auto_rename"
    create_body = {
        "drive_id": drive_id,
        "parent_file_id": resolved_parent_id,
        "name": _text(target_name) or file_path.name,
        "type": "file",
        "size": int(file_path.stat().st_size),
        "check_name_mode": check_name_mode,
        "part_info_list": [{"part_number": 1}],
    }

    create_payload: dict[str, object] = {}
    resolved_target_name = create_body["name"]
    conflict_action = ""
    file_id = ""
    upload_id = ""
    try:
        create_status, create_payload = _post_json(f"{_domain_host(domain_id)}/v2/file/create", create_body, auth)
        file_id = _text(create_payload.get("file_id"))
        upload_id = _text(create_payload.get("upload_id"))
        resolved_target_name = _text(create_payload.get("name")) or str(create_body["name"])
        conflict_action = _resolve_conflict_action(conflict_policy, str(create_body["name"]), resolved_target_name)
        if not file_id:
            risk_level, risk_hint = _classify_upload_issue(create_status, "missing_file_id")
            return AliyunOpenUploadResult(
                ok=False,
                mode="create_failed",
                usedProfile=True,
                profileId=profile.profileId,
                parentId=resolved_parent_id,
                status=create_status,
                error="missing_file_id",
                note="Aliyun Drive Open create file succeeded but did not return fileId.",
                riskLevel=risk_level,
                riskHint=risk_hint,
                payload={
                    "createResponse": create_payload,
                    "resolvedTargetName": resolved_target_name,
                    "conflictAction": conflict_action,
                },
            )

        if not bool(create_payload.get("rapid_upload")):
            upload_url = _extract_upload_url(create_payload)
            if not upload_url:
                risk_level, risk_hint = _classify_upload_issue(create_status, "missing_upload_url")
                return AliyunOpenUploadResult(
                    ok=False,
                    mode="create_failed",
                    usedProfile=True,
                    profileId=profile.profileId,
                    parentId=resolved_parent_id,
                    status=create_status,
                    error="missing_upload_url",
                    note="Aliyun Drive Open create file did not return upload_url for the current part.",
                    riskLevel=risk_level,
                    riskHint=risk_hint,
                    payload={
                        "createResponse": create_payload,
                        "fileId": file_id,
                        "uploadId": upload_id,
                        "resolvedTargetName": resolved_target_name,
                        "conflictAction": conflict_action,
                    },
                )
            put_status = _put_file(upload_url, file_path)
            complete_status, complete_payload = _post_json(
                f"{_domain_host(domain_id)}/v2/file/complete",
                {
                    "drive_id": drive_id,
                    "file_id": file_id,
                    "upload_id": upload_id,
                },
                auth,
            )
            verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
                profile_id=profile.profileId,
                parent_id=resolved_parent_id,
                target_name=resolved_target_name,
                file_id=file_id,
            )
            payload = {
                "createResponse": create_payload,
                "completeResponse": complete_payload,
                "fileId": file_id,
                "uploadId": upload_id,
                "putStatus": put_status,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            }
            return AliyunOpenUploadResult(
                ok=True,
                mode="binary_upload_single_part",
                usedProfile=True,
                profileId=profile.profileId,
                parentId=resolved_parent_id,
                status=complete_status,
                error="",
                note="Aliyun Drive Open binary upload completed through create file + single-part upload + complete.",
                payload=payload,
                verifyOk=verify_ok,
                verifyMode=verify_mode,
                verifyNote=verify_note,
                verifyPayload=verify_payload,
            )

        verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
            profile_id=profile.profileId,
            parent_id=resolved_parent_id,
            target_name=resolved_target_name,
            file_id=file_id,
        )
        return AliyunOpenUploadResult(
            ok=True,
            mode="binary_upload_rapid_hit",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=create_status,
            error="",
            note="Aliyun Drive Open create file reported a provider-side rapid upload hit.",
            payload={
                "createResponse": create_payload,
                "fileId": file_id,
                "uploadId": upload_id,
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
        return AliyunOpenUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=status,
            error=error,
            note="Aliyun Drive Open binary upload request reached the API but was rejected.",
            riskLevel=risk_level,
            riskHint=risk_hint,
            payload={
                "createResponse": create_payload,
                "fileId": file_id,
                "uploadId": upload_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
    except URLError as exc:
        error = f"url_error:{exc.reason}"
        return AliyunOpenUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error=error,
            note="Aliyun Drive Open binary upload could not reach the API endpoint.",
            riskLevel="provider",
            riskHint="上传请求未能连通 Aliyun 接口，请检查网络、域名或代理设置。",
            payload={
                "createResponse": create_payload,
                "fileId": file_id,
                "uploadId": upload_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
    except json.JSONDecodeError:
        return AliyunOpenUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=200,
            error="invalid_json",
            note="Aliyun Drive Open upload returned non-JSON content during the create/complete flow.",
            riskLevel="provider",
            riskHint="Provider 返回内容格式异常，建议保留原始响应继续排查。",
            payload={
                "createResponse": create_payload,
                "fileId": file_id,
                "uploadId": upload_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
    except Exception as exc:  # pragma: no cover
        error = f"unexpected:{exc}"
        risk_level, risk_hint = _classify_upload_issue(0, error)
        return AliyunOpenUploadResult(
            ok=False,
            mode="unexpected_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error=error,
            note="Aliyun Drive Open binary upload failed unexpectedly.",
            riskLevel=risk_level,
            riskHint=risk_hint,
            payload={
                "createResponse": create_payload,
                "fileId": file_id,
                "uploadId": upload_id,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            },
        )
