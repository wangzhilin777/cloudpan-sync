from __future__ import annotations

import json
from importlib import import_module
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from urllib.error import HTTPError, URLError

from .pikpak_live import (
    PIKPAK_API_BASE,
    _load_profile_requirements,
    _post_json,
    _text,
    fetch_pikpak_live_list,
    fetch_pikpak_live_metadata,
)


@dataclass
class PikPakFastUploadResult:
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


def _create_file_url() -> str:
    return f"{PIKPAK_API_BASE}/drive/v1/files"


def _compute_local_gcid(file_path: Path) -> str:
    def calc_block_size(size: int) -> int:
        block_size = 0x40000
        while size / block_size > 0x200 and block_size < 0x200000:
            block_size <<= 1
        return block_size

    outer = sha1()
    read_size = calc_block_size(int(file_path.stat().st_size))
    with file_path.open("rb") as handle:
        while True:
            chunk = handle.read(read_size)
            if not chunk:
                break
            inner = sha1()
            inner.update(chunk)
            outer.update(inner.digest())
    return outer.hexdigest().upper()


def _verify_local_gcid(file_path: Path, expected_gcid: str) -> tuple[bool, str]:
    actual_gcid = _compute_local_gcid(file_path)
    normalized_expected = _text(expected_gcid).upper() or actual_gcid
    return normalized_expected == actual_gcid, actual_gcid


def _pick_text(data: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = _text(data.get(key))
        if value:
            return value
    return ""


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


def _trim_bucket_from_endpoint(endpoint: str, bucket: str) -> str:
    resolved = _text(endpoint).replace("https://", "").replace("http://", "").strip()
    prefix = f"{bucket}."
    if resolved.startswith(prefix):
        return resolved[len(prefix) :]
    return resolved


def _upload_resumable_binary(file_path: Path, resumable: dict[str, object]) -> tuple[str, str, dict[str, object]]:
    params = resumable.get("params") if isinstance(resumable.get("params"), dict) else {}
    if not isinstance(params, dict):
        return "missing_resumable_params", "PikPak resumable payload did not include params.", {"resumable": resumable}

    access_key_id = _pick_text(params, "access_key_id", "accessKeyId")
    access_key_secret = _pick_text(params, "access_key_secret", "accessKeySecret")
    security_token = _pick_text(params, "security_token", "securityToken")
    bucket = _pick_text(params, "bucket")
    endpoint = _pick_text(params, "endpoint")
    key = _pick_text(params, "key")
    if not access_key_id or not access_key_secret or not security_token or not bucket or not endpoint or not key:
        return (
            "missing_resumable_params",
            "PikPak resumable payload did not include a complete S3-compatible session.",
            {"resumable": resumable},
        )

    try:
        boto3 = import_module("boto3")
        botocore_config = import_module("botocore.config")
    except Exception as exc:  # pragma: no cover
        return (
            "missing_boto3_dependency",
            f"PikPak resumable upload requires boto3/botocore in the runtime environment: {exc}",
            {"resumable": resumable},
        )

    endpoint_host = _trim_bucket_from_endpoint(endpoint, bucket)
    client = boto3.client(
        "s3",
        region_name="pikpak",
        endpoint_url=f"https://{endpoint_host}",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key_secret,
        aws_session_token=security_token,
        config=botocore_config.Config(signature_version="s3v4"),
    )
    with file_path.open("rb") as handle:
        client.upload_fileobj(handle, bucket, key)
    return (
        "",
        "",
        {
            "provider": _pick_text(resumable, "provider"),
            "bucket": bucket,
            "endpoint": endpoint_host,
            "key": key,
        },
    )


def _classify_issue(status: int, error: str) -> tuple[str, str]:
    if error == "profile_not_found":
        return ("input", "targetProfileId 对应的 PikPak 授权档案不存在。")
    if error == "missing_authorization":
        return ("auth", "补 token 或 extra.authorization 后再试 PikPak 秒传。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续做 PikPak 秒传。")
    if error == "local_gcid_mismatch":
        return ("input", "本地文件计算出的 gcid 与任务条目不一致，先校验来源文件。")
    if error == "rapid_upload_not_hit":
        return ("provider", "PikPak 已接受建上传任务请求，但没有命中秒传，当前仍需后续真实上传链路。")
    if error == "missing_boto3_dependency":
        return ("environment", "当前环境缺少 boto3/botocore，无法继续走 PikPak resumable 二进制上传。")
    if error == "missing_resumable_params":
        return ("provider", "PikPak 返回了 resumable 会话，但缺少完整上传参数，当前无法继续。")
    if error == "resumable_upload_failed":
        return ("provider", "PikPak resumable 二进制上传已开始，但上传过程中失败。")
    if error.startswith("http_error:401"):
        return ("auth", "PikPak 秒传请求被 401 拒绝，授权很可能已失效。")
    if error.startswith("http_error:403"):
        return ("risk", "PikPak 秒传请求被 403 拒绝，可能命中风控或缺必要设备头。")
    if error.startswith("http_error:409"):
        return ("provider", "PikPak 返回了同名或状态冲突，建议换文件名或检查目标目录。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "PikPak 秒传请求过快，建议稍后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "PikPak provider 侧接口异常，建议稍后重试。")
    if error.startswith("url_error:"):
        return ("network", "PikPak 秒传请求未能连通接口，请检查网络。")
    if error.startswith("unexpected:"):
        return ("unexpected", "PikPak 秒传过程异常中断，建议保留错误文本继续排查。")
    return ("", "")


def _verify_uploaded_file(
    *,
    profile_id: str,
    parent_id: str,
    target_name: str,
    file_id: str,
    expected_gcid: str,
) -> tuple[bool, str, str, dict[str, object]]:
    resolved_file_id = _text(file_id)
    normalized_gcid = _text(expected_gcid).upper()
    if resolved_file_id:
        metadata_result = fetch_pikpak_live_metadata(profile_id=profile_id, file_id=resolved_file_id)
        if metadata_result.ok:
            entry = dict((metadata_result.payload or {}).get("entry") or {})
            entry_gcid = _text(entry.get("gcid")).upper()
            verify_ok = not normalized_gcid or not entry_gcid or entry_gcid == normalized_gcid
            return (
                verify_ok,
                "metadata_by_file_id",
                "Rapid-upload result was verified by PikPak live metadata using the returned fileId.",
                {
                    "fileId": resolved_file_id,
                    "entry": entry,
                    "status": metadata_result.status,
                },
            )

    list_result = fetch_pikpak_live_list(profile_id=profile_id, parent_id=parent_id, limit=200)
    items = list((list_result.payload or {}).get("items") or []) if list_result.ok else []
    if list_result.ok:
        matched = next((item for item in items if _text(item.get("name")) == target_name), None)
        if matched is not None:
            matched_gcid = _text(matched.get("gcid")).upper()
            verify_ok = not normalized_gcid or not matched_gcid or matched_gcid == normalized_gcid
            return (
                verify_ok,
                "list_by_parent_name",
                "Rapid-upload result was verified by PikPak live list using parentId + file name.",
                {
                    "matchedItem": matched,
                    "status": list_result.status,
                },
            )
        return (
            False,
            "list_by_parent_name",
            "Rapid-upload request succeeded, but PikPak live list did not find the uploaded file name under the target parent yet.",
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


def upload_pikpak_fast_file(
    *,
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_id: str = "",
    expected_gcid: str = "",
) -> PikPakFastUploadResult:
    profile, auth_headers = _load_profile_requirements(profile_id)
    resolved_parent_id = _text(parent_id)
    if profile is None:
        risk_level, risk_hint = _classify_issue(0, "profile_not_found")
        return PikPakFastUploadResult(False, "profile_missing", False, profile_id, resolved_parent_id, 0, "profile_not_found", "Saved PikPak auth profile was not found.", risk_level, risk_hint)
    if not auth_headers.get("authorization"):
        risk_level, risk_hint = _classify_issue(0, "missing_authorization")
        return PikPakFastUploadResult(False, "profile_incomplete", True, profile.profileId, resolved_parent_id, 0, "missing_authorization", "PikPak fast upload requires token or extra.authorization.", risk_level, risk_hint)

    file_path = Path(str(local_path or "").strip())
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_issue(0, "local_file_missing")
        return PikPakFastUploadResult(False, "local_file_missing", True, profile.profileId, resolved_parent_id, 0, "local_file_missing", "PikPak fast upload requires an existing local file.", risk_level, risk_hint)

    gcid_ok, actual_gcid = _verify_local_gcid(file_path, expected_gcid)
    if not gcid_ok:
        risk_level, risk_hint = _classify_issue(0, "local_gcid_mismatch")
        return PikPakFastUploadResult(
            False,
            "local_gcid_mismatch",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            "local_gcid_mismatch",
            "PikPak fast upload aborted because local gcid does not match the task entry.",
            risk_level,
            risk_hint,
            payload={"actualGcid": actual_gcid},
        )

    request_body = {
        "kind": "drive#file",
        "name": _text(target_name or file_path.name) or file_path.name,
        "size": int(file_path.stat().st_size),
        "hash": actual_gcid,
        "upload_type": "UPLOAD_TYPE_RESUMABLE",
        "objProvider": {"provider": "UPLOAD_TYPE_UNKNOWN"},
        "parent_id": resolved_parent_id,
        "folder_type": "NORMAL",
    }

    try:
        status, payload = _post_json("/drive/v1/files", request_body, auth_headers)
        upload_type = _pick_text(payload, "upload_type")
        file_info = payload.get("file") if isinstance(payload.get("file"), dict) else {}
        resumable = payload.get("resumable") if isinstance(payload.get("resumable"), dict) else {}
        file_id = _pick_text(file_info, "id", "file_id", "fileId")
        resolved_name = _pick_text(file_info, "name", "file_name", "fileName") or request_body["name"]

        common_payload = {
            "createResponse": payload,
            "fileId": file_id,
            "resolvedTargetName": resolved_name,
            "conflictAction": "",
            "uploadType": upload_type,
            "gcid": actual_gcid,
        }

        if resumable:
            common_payload["resumable"] = resumable
            upload_error, upload_note, upload_payload = _upload_resumable_binary(file_path, resumable)
            if upload_error:
                risk_level, risk_hint = _classify_issue(status, upload_error)
                common_payload["resumableUpload"] = upload_payload
                return PikPakFastUploadResult(
                    False,
                    "resumable_upload_failed",
                    True,
                    profile.profileId,
                    resolved_parent_id,
                    status,
                    upload_error,
                    upload_note or "PikPak resumable upload fallback failed.",
                    risk_level,
                    risk_hint,
                    payload=common_payload,
                    verifyOk=False,
                    verifyMode="create_response_resumable",
                    verifyNote="The live create call reached PikPak, but the resumable upload fallback did not complete.",
                    verifyPayload={"uploadType": upload_type},
                )
            common_payload["resumableUpload"] = upload_payload

        verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
            profile_id=profile.profileId,
            parent_id=resolved_parent_id,
            target_name=resolved_name,
            file_id=file_id,
            expected_gcid=actual_gcid,
        )
        return PikPakFastUploadResult(
            True,
            "binary_upload_after_hash_miss" if resumable else "rapid_upload_by_hash",
            True,
            profile.profileId,
            resolved_parent_id,
            status,
            "",
            "PikPak resumed to binary upload fallback after hash miss and completed successfully."
            if resumable
            else "PikPak rapid-upload request succeeded and did not require a follow-up resumable upload session.",
            payload=common_payload,
            verifyOk=verify_ok,
            verifyMode="metadata_after_resumable_upload" if resumable and verify_mode == "metadata_by_file_id" else "list_after_resumable_upload" if resumable and verify_mode == "list_by_parent_name" else verify_mode,
            verifyNote=verify_note,
            verifyPayload={**verify_payload, "usedBinaryFallback": bool(resumable)} if isinstance(verify_payload, dict) else {"usedBinaryFallback": bool(resumable)},
        )
    except HTTPError as exc:
        status, error_payload = _extract_http_error_payload(exc)
        risk_level, risk_hint = _classify_issue(status, f"http_error:{status}")
        return PikPakFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            status,
            f"http_error:{status}",
            "PikPak rapid-upload create request reached the API but was rejected.",
            risk_level,
            risk_hint,
            payload={"errorResponse": error_payload, "gcid": actual_gcid},
        )
    except URLError as exc:
        risk_level, risk_hint = _classify_issue(0, f"url_error:{exc.reason}")
        return PikPakFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            f"url_error:{exc.reason}",
            "PikPak rapid-upload request could not reach the API endpoint.",
            risk_level,
            risk_hint,
            payload={"gcid": actual_gcid},
        )
    except json.JSONDecodeError:
        risk_level, risk_hint = _classify_issue(200, "unexpected:invalid_json")
        return PikPakFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            200,
            "unexpected:invalid_json",
            "PikPak rapid-upload request returned non-JSON content.",
            risk_level,
            risk_hint,
            payload={"gcid": actual_gcid},
        )
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_issue(0, f"unexpected:{exc}")
        return PikPakFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            f"unexpected:{exc}",
            "PikPak rapid-upload request failed unexpectedly.",
            risk_level,
            risk_hint,
            payload={"gcid": actual_gcid},
        )
