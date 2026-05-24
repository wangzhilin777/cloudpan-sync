from __future__ import annotations

import json
from importlib import import_module
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .xunlei_live import (
    XUNLEI_API_BASE,
    _load_profile_requirements,
    _request_headers,
    _text,
    fetch_xunlei_live_list,
    fetch_xunlei_live_metadata,
)


@dataclass
class XunleiFastUploadResult:
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
    return f"{XUNLEI_API_BASE}/drive/v1/files"


def _compute_local_gcid(file_path: Path) -> str:
    def calc_block_size(size: int) -> int:
        block_size = 0x40000
        while size / block_size > 0x200 and block_size < 0x200000:
            block_size <<= 1
        return block_size

    outer = sha1()
    inner = sha1()
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


def _request_json(url: str, body: dict[str, object], auth_headers: dict[str, str]) -> tuple[int, dict[str, object]]:
    request = Request(
        url=url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=_request_headers(auth_headers),
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


def _pick_text(data: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = _text(data.get(key))
        if value:
            return value
    return ""


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
    list_result = fetch_xunlei_live_list(profile_id=profile_id, parent_id=parent_id, limit=200)
    if not list_result.ok:
        return target_name, "conflict_check_unavailable", "Could not verify same-name conflicts before Xunlei upload, so the original file name was kept."

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
        return candidate, "auto_rename_new", "A same-name file already exists under the target path, so Xunlei auto-renamed the new file."
    return (
        candidate,
        "overwrite_downgraded_to_auto_rename",
        "The requested overwrite policy was downgraded because the current Xunlei upload path does not support verified in-place overwrite.",
    )


def _trim_bucket_from_endpoint(endpoint: str, bucket: str) -> str:
    resolved = _text(endpoint).replace("https://", "").replace("http://", "").strip()
    prefix = f"{bucket}."
    if resolved.startswith(prefix):
        return resolved[len(prefix) :]
    return resolved


def _upload_resumable_binary(file_path: Path, resumable: dict[str, object]) -> tuple[str, str, dict[str, object]]:
    params = resumable.get("params") if isinstance(resumable.get("params"), dict) else {}
    if not isinstance(params, dict):
        return "missing_resumable_params", "Xunlei resumable payload did not include params.", {"resumable": resumable}

    access_key_id = _pick_text(params, "access_key_id", "accessKeyId")
    access_key_secret = _pick_text(params, "access_key_secret", "accessKeySecret")
    security_token = _pick_text(params, "security_token", "securityToken")
    bucket = _pick_text(params, "bucket")
    endpoint = _pick_text(params, "endpoint")
    key = _pick_text(params, "key")
    if not access_key_id or not access_key_secret or not security_token or not bucket or not endpoint or not key:
        return (
            "missing_resumable_params",
            "Xunlei resumable payload did not include a complete S3-compatible session.",
            {"resumable": resumable},
        )

    try:
        boto3 = import_module("boto3")
        botocore_config = import_module("botocore.config")
    except Exception as exc:  # pragma: no cover
        return (
            "missing_boto3_dependency",
            f"Xunlei resumable upload requires boto3/botocore in the runtime environment: {exc}",
            {"resumable": resumable},
        )

    endpoint_host = _trim_bucket_from_endpoint(endpoint, bucket)
    client = boto3.client(
        "s3",
        region_name="xunlei",
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
        return ("input", "targetProfileId 对应的迅雷授权档案不存在。")
    if error == "missing_authorization":
        return ("auth", "补 token 或 extra.authorization 后再试迅雷秒传。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续做迅雷秒传。")
    if error == "local_gcid_mismatch":
        return ("input", "本地文件计算出的 gcid 与任务条目不一致，先校验来源文件。")
    if error == "rapid_upload_not_hit":
        return ("provider", "迅雷已接受建上传任务请求，但没有命中秒传，当前仍需后续真实上传链路。")
    if error == "missing_boto3_dependency":
        return ("environment", "当前环境缺少 boto3/botocore，无法继续走迅雷 resumable 二进制上传。")
    if error == "missing_resumable_params":
        return ("provider", "迅雷返回了 resumable 会话，但缺少完整上传参数，当前无法继续。")
    if error == "resumable_upload_failed":
        return ("provider", "迅雷 resumable 二进制上传已开始，但上传过程中失败。")
    if error.startswith("http_error:401"):
        return ("auth", "迅雷秒传请求被 401 拒绝，授权很可能已失效。")
    if error.startswith("http_error:403"):
        return ("risk", "迅雷秒传请求被 403 拒绝，可能命中风控或缺必要设备头。")
    if error.startswith("http_error:409"):
        return ("provider", "迅雷返回了同名或状态冲突，建议换文件名或检查目标目录。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "迅雷秒传请求过快，建议稍后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "迅雷 provider 侧接口异常，建议稍后重试。")
    if error.startswith("url_error:"):
        return ("network", "迅雷秒传请求未能连通接口，请检查网络。")
    if error.startswith("unexpected:"):
        return ("unexpected", "迅雷秒传过程异常中断，建议保留错误文本继续排查。")
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
        metadata_result = fetch_xunlei_live_metadata(profile_id=profile_id, file_id=resolved_file_id, parent_id=parent_id)
        if metadata_result.ok:
            entry = dict((metadata_result.payload or {}).get("entry") or {})
            entry_gcid = _text(entry.get("gcid")).upper()
            verify_ok = not normalized_gcid or not entry_gcid or entry_gcid == normalized_gcid
            return (
                verify_ok,
                "metadata_by_file_id",
                "Rapid-upload result was verified by Xunlei live metadata using the returned fileId.",
                {
                    "fileId": resolved_file_id,
                    "entry": entry,
                    "status": metadata_result.status,
                },
            )

    list_result = fetch_xunlei_live_list(profile_id=profile_id, parent_id=parent_id, limit=200)
    items = list((list_result.payload or {}).get("items") or []) if list_result.ok else []
    if list_result.ok:
        matched = next((item for item in items if _text(item.get("name")) == target_name), None)
        if matched is not None:
            matched_gcid = _text(matched.get("gcid")).upper()
            verify_ok = not normalized_gcid or not matched_gcid or matched_gcid == normalized_gcid
            return (
                verify_ok,
                "list_by_parent_name",
                "Rapid-upload result was verified by Xunlei live list using parentId + file name.",
                {
                    "matchedItem": matched,
                    "status": list_result.status,
                },
            )
        return (
            False,
            "list_by_parent_name",
            "Rapid-upload request succeeded, but Xunlei live list did not find the uploaded file name under the target parent yet.",
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


def upload_xunlei_fast_file(
    *,
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_id: str = "",
    expected_gcid: str = "",
    conflict_policy: str = "auto_rename_new",
) -> XunleiFastUploadResult:
    profile, auth_headers = _load_profile_requirements(profile_id)
    resolved_parent_id = _text(parent_id)
    if profile is None:
        risk_level, risk_hint = _classify_issue(0, "profile_not_found")
        return XunleiFastUploadResult(False, "profile_missing", False, profile_id, resolved_parent_id, 0, "profile_not_found", "Saved Xunlei auth profile was not found.", risk_level, risk_hint)
    if not auth_headers.get("authorization"):
        risk_level, risk_hint = _classify_issue(0, "missing_authorization")
        return XunleiFastUploadResult(False, "profile_incomplete", True, profile.profileId, resolved_parent_id, 0, "missing_authorization", "Xunlei fast upload requires token or extra.authorization.", risk_level, risk_hint)

    file_path = Path(str(local_path or "").strip())
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_issue(0, "local_file_missing")
        return XunleiFastUploadResult(False, "local_file_missing", True, profile.profileId, resolved_parent_id, 0, "local_file_missing", "Xunlei fast upload requires an existing local file.", risk_level, risk_hint)

    gcid_ok, actual_gcid = _verify_local_gcid(file_path, expected_gcid)
    if not gcid_ok:
        risk_level, risk_hint = _classify_issue(0, "local_gcid_mismatch")
        return XunleiFastUploadResult(
            False,
            "local_gcid_mismatch",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            "local_gcid_mismatch",
            "Xunlei fast upload aborted because local gcid does not match the task entry.",
            risk_level,
            risk_hint,
            payload={"actualGcid": actual_gcid},
        )

    resolved_target_name, conflict_action, conflict_note = _resolve_upload_target_name(
        profile_id=profile.profileId,
        parent_id=resolved_parent_id,
        target_name=_text(target_name or file_path.name) or file_path.name,
        conflict_policy=conflict_policy,
    )

    request_body = {
        "kind": "drive#file",
        "name": resolved_target_name,
        "size": int(file_path.stat().st_size),
        "hash": actual_gcid,
        "upload_type": "UPLOAD_TYPE_RESUMABLE",
        "parent_id": resolved_parent_id,
    }

    try:
        status, payload = _request_json(_create_file_url(), request_body, auth_headers)
        upload_type = _text(payload.get("upload_type"))
        file_info = payload.get("file") if isinstance(payload.get("file"), dict) else {}
        resumable = payload.get("resumable") if isinstance(payload.get("resumable"), dict) else {}
        file_id = _pick_text(file_info, "id", "file_id", "fileId")
        resolved_name = _pick_text(file_info, "name", "file_name", "fileName") or request_body["name"]

        common_payload = {
            "createResponse": payload,
            "fileId": file_id,
            "resolvedTargetName": resolved_name,
            "conflictAction": conflict_action,
            "uploadType": upload_type,
            "gcid": actual_gcid,
        }

        if resumable:
            common_payload["resumable"] = resumable
            upload_error, upload_note, upload_payload = _upload_resumable_binary(file_path, resumable)
            if upload_error:
                risk_level, risk_hint = _classify_issue(status, upload_error)
                common_payload["resumableUpload"] = upload_payload
                return XunleiFastUploadResult(
                    False,
                    "resumable_upload_failed",
                    True,
                    profile.profileId,
                    resolved_parent_id,
                    status,
                    upload_error,
                    upload_note or "Xunlei resumable upload fallback failed.",
                    risk_level,
                    risk_hint,
                    payload=common_payload,
                    verifyOk=False,
                    verifyMode="create_response_resumable",
                    verifyNote="The live create call reached Xunlei, but the resumable upload fallback did not complete.",
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
        return XunleiFastUploadResult(
            True,
            "binary_upload_after_hash_miss" if resumable else "rapid_upload_by_hash",
            True,
            profile.profileId,
            resolved_parent_id,
            status,
            "",
            (
                "Xunlei resumed to binary upload fallback after hash miss and completed successfully."
                if resumable
                else "Xunlei rapid-upload request succeeded and did not require a follow-up resumable upload session."
            )
            + (f" {conflict_note}" if conflict_note else ""),
            payload=common_payload,
            verifyOk=verify_ok,
            verifyMode="metadata_after_resumable_upload" if resumable and verify_mode == "metadata_by_file_id" else "list_after_resumable_upload" if resumable and verify_mode == "list_by_parent_name" else verify_mode,
            verifyNote=verify_note,
            verifyPayload={**verify_payload, "usedBinaryFallback": bool(resumable)} if isinstance(verify_payload, dict) else {"usedBinaryFallback": bool(resumable)},
        )
    except HTTPError as exc:
        status, error_payload = _extract_http_error_payload(exc)
        risk_level, risk_hint = _classify_issue(status, f"http_error:{status}")
        return XunleiFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            status,
            f"http_error:{status}",
            "Xunlei rapid-upload create request reached the API but was rejected.",
            risk_level,
            risk_hint,
            payload={"errorResponse": error_payload, "gcid": actual_gcid},
        )
    except URLError as exc:
        risk_level, risk_hint = _classify_issue(0, f"url_error:{exc.reason}")
        return XunleiFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            f"url_error:{exc.reason}",
            "Xunlei rapid-upload request could not reach the API endpoint.",
            risk_level,
            risk_hint,
            payload={"gcid": actual_gcid},
        )
    except json.JSONDecodeError:
        risk_level, risk_hint = _classify_issue(200, "unexpected:invalid_json")
        return XunleiFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            200,
            "unexpected:invalid_json",
            "Xunlei rapid-upload request returned non-JSON content.",
            risk_level,
            risk_hint,
            payload={"gcid": actual_gcid},
        )
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_issue(0, f"unexpected:{exc}")
        return XunleiFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            f"unexpected:{exc}",
            "Xunlei rapid-upload request failed unexpectedly.",
            risk_level,
            risk_hint,
            payload={"gcid": actual_gcid},
        )
