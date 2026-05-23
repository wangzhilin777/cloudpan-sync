from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5
from pathlib import Path
from pathlib import PurePosixPath
from time import sleep

from .auth_store import get_profile
from .guangya_live import fetch_guangya_live_list, fetch_guangya_live_metadata

try:
    from httpx import HTTPStatusError
    from guangyaclient import GuangyaClient
except Exception:  # pragma: no cover
    HTTPStatusError = None  # type: ignore[assignment]
    GuangyaClient = None  # type: ignore[assignment]


@dataclass
class GuangyaUploadResult:
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


def _pick_string(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _extract_access_token(value: str) -> str:
    text = _pick_string(value)
    if not text:
        return ""
    if text.lower().startswith("bearer "):
        return text[7:].strip()
    return text


def _classify_upload_issue(status: int, error: str) -> tuple[str, str]:
    if error == "missing_dependency":
        return ("dependency", "当前环境缺少 guangyaclient，无法执行 Guangya 真上传。")
    if error == "profile_not_found":
        return ("input", "targetProfileId 对应的 Guangya 授权档案不存在。")
    if error == "missing_authorization":
        return ("auth", "补 token 或 extra.authorization 后再试 Guangya 上传。")
    if error == "missing_parent_id":
        return ("input", "当前二进制上传需要 targetParentId 或 auth profile extra.parentId。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续上传。")
    if error == "local_md5_mismatch":
        return ("input", "本地文件 MD5 与任务条目不一致，先校验来源文件。")
    if error.startswith("http_error:401"):
        return ("auth", "上传请求被 401 拒绝，授权很可能已失效。")
    if error.startswith("http_error:403"):
        return ("risk", "上传请求被 403 拒绝，可能命中风控或缺必要设备字段。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "上传请求过快，建议降并发稍后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "Provider 侧上传接口异常，建议稍后重试。")
    if error.startswith("unexpected:"):
        return ("unexpected", "上传过程异常中断，建议保留错误文本继续排查。")
    return ("", "")


def _verify_local_md5(local_path: Path, expected_md5: str) -> bool:
    expected = _pick_string(expected_md5).lower()
    if not expected:
        return True
    hasher = md5()
    with local_path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest().lower() == expected


def _split_name(name: str) -> tuple[str, str]:
    pure = PurePosixPath(_pick_string(name) or "file")
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
    list_result = fetch_guangya_live_list(profile_id=profile_id, parent_id=parent_id, page_size=200)
    if not list_result.ok:
        return target_name, "conflict_check_unavailable", "Could not verify same-name conflicts before Guangya upload, so the original file name was kept."

    existing_names = {
        _pick_string(item.get("name"))
        for item in list_result.items
        if _pick_string(item.get("name"))
    }
    if target_name not in existing_names:
        return target_name, "no_conflict", ""

    if conflict_policy == "auto_rename_new":
        index = 1
        candidate = _build_renamed_candidate(target_name, index)
        while candidate in existing_names:
            index += 1
            candidate = _build_renamed_candidate(target_name, index)
        return candidate, "auto_rename_new", "A same-name file already exists under the target path, so Guangya upload auto-renamed the new file."

    index = 1
    candidate = _build_renamed_candidate(target_name, index)
    while candidate in existing_names:
        index += 1
        candidate = _build_renamed_candidate(target_name, index)
    return candidate, "overwrite_downgraded_to_auto_rename", "The requested overwrite policy was downgraded because the current Guangya upload path does not support verified in-place overwrite."


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


def _extract_uploaded_file_id(payload: dict[str, object]) -> str:
    return _find_first_text(payload, ["fileid", "file_id", "resid", "res_id", "id"])


def _verify_uploaded_file(
    *,
    profile_id: str,
    parent_id: str,
    target_name: str,
    upload_payload: dict[str, object] | None,
) -> tuple[bool, str, str, dict[str, object]]:
    payload = upload_payload or {}
    uploaded_file_id = _extract_uploaded_file_id(payload)
    if uploaded_file_id:
        metadata_result = fetch_guangya_live_metadata(profile_id=profile_id, file_id=uploaded_file_id)
        if metadata_result.ok and metadata_result.items:
            return (
                True,
                "metadata_by_file_id",
                "Upload result was verified by Guangya live metadata using the returned fileId.",
                {
                    "fileId": uploaded_file_id,
                    "entry": metadata_result.items[0],
                    "status": metadata_result.status,
                },
            )

    list_result = fetch_guangya_live_list(profile_id=profile_id, parent_id=parent_id, page_size=200)
    if list_result.ok:
        matched = next((item for item in list_result.items if _pick_string(item.get("name")) == target_name), None)
        if matched is not None:
            return (
                True,
                "list_by_parent_name",
                "Upload result was verified by Guangya live list using parentId + file name.",
                {
                    "matchedItem": matched,
                    "status": list_result.status,
                },
            )
        return (
            False,
            "list_by_parent_name",
            "Upload request succeeded, but Guangya live list did not find the uploaded file name under the target parentId yet.",
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
            "uploadedFileId": uploaded_file_id,
            "listError": list_result.error,
            "listStatus": list_result.status,
            "listRiskHint": list_result.riskHint,
        },
    )


def upload_guangya_local_file(
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_id: str = "",
    expected_md5: str = "",
    conflict_policy: str = "auto_rename_new",
) -> GuangyaUploadResult:
    if GuangyaClient is None or HTTPStatusError is None:
        risk_level, risk_hint = _classify_upload_issue(0, "missing_dependency")
        return GuangyaUploadResult(
            ok=False,
            mode="dependency_missing",
            usedProfile=False,
            profileId=profile_id,
            parentId="",
            status=0,
            error="missing_dependency",
            note="guangyaclient is not installed, so Guangya binary upload is unavailable.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    profile = get_profile(profile_id)
    if profile is None:
        risk_level, risk_hint = _classify_upload_issue(0, "profile_not_found")
        return GuangyaUploadResult(
            ok=False,
            mode="profile_missing",
            usedProfile=False,
            profileId=profile_id,
            parentId="",
            status=0,
            error="profile_not_found",
            note="Saved Guangya auth profile was not found.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    access_token = _extract_access_token(profile.token or profile.extra.get("authorization", ""))
    if not access_token:
        risk_level, risk_hint = _classify_upload_issue(0, "missing_authorization")
        return GuangyaUploadResult(
            ok=False,
            mode="profile_incomplete",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_authorization",
            note="Guangya binary upload requires token or extra.authorization.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    resolved_parent_id = _pick_string(parent_id) or _pick_string(profile.extra.get("parentId"))
    if not resolved_parent_id:
        risk_level, risk_hint = _classify_upload_issue(0, "missing_parent_id")
        return GuangyaUploadResult(
            ok=False,
            mode="profile_incomplete",
            usedProfile=True,
            profileId=profile.profileId,
            parentId="",
            status=0,
            error="missing_parent_id",
            note="Guangya binary upload requires targetParentId or auth profile extra.parentId.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    file_path = Path(local_path)
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_upload_issue(0, "local_file_missing")
        return GuangyaUploadResult(
            ok=False,
            mode="local_missing",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error="local_file_missing",
            note="Local file for Guangya binary upload does not exist.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    if not _verify_local_md5(file_path, expected_md5):
        risk_level, risk_hint = _classify_upload_issue(0, "local_md5_mismatch")
        return GuangyaUploadResult(
            ok=False,
            mode="local_invalid",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=resolved_parent_id,
            status=0,
            error="local_md5_mismatch",
            note="Local file MD5 does not match the task entry.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )

    device_id = _pick_string(profile.extra.get("deviceId") or profile.extra.get("did"))
    client = GuangyaClient(
        access_token=access_token or None,
        refresh_token=_pick_string(profile.extra.get("refreshToken")) or None,
        device_id=device_id or None,
    )
    normalized_parent_id = str(resolved_parent_id)
    normalized_target_name = _pick_string(target_name) or file_path.name
    resolved_target_name, conflict_action, conflict_note = _resolve_upload_target_name(
        profile_id=profile.profileId,
        parent_id=normalized_parent_id,
        target_name=normalized_target_name,
        conflict_policy=str(conflict_policy or "auto_rename_new"),
    )
    try:
        try:
            payload = client.file_upload(
                str(file_path),
                name=resolved_target_name,
                parent_id=normalized_parent_id,
            )
            normalized_payload = payload if isinstance(payload, dict) else {"raw": payload}
            normalized_payload["requestedTargetName"] = normalized_target_name
            normalized_payload["resolvedTargetName"] = resolved_target_name
            normalized_payload["conflictAction"] = conflict_action
            verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
                profile_id=profile.profileId,
                parent_id=normalized_parent_id,
                target_name=resolved_target_name,
                upload_payload=normalized_payload,
            )
            return GuangyaUploadResult(
                ok=True,
                mode="binary_upload",
                usedProfile=True,
                profileId=profile.profileId,
                parentId=normalized_parent_id,
                status=200,
                error="",
                note=f"Guangya binary upload completed through guangyaclient.file_upload.{(' ' + conflict_note) if conflict_note else ''}",
                payload=normalized_payload,
                verifyOk=verify_ok,
                verifyMode=verify_mode,
                verifyNote=verify_note,
                verifyPayload=verify_payload,
            )
        except HTTPStatusError as exc:
            if int(exc.response.status_code) != 400:
                risk_level, risk_hint = _classify_upload_issue(int(exc.response.status_code), f"http_error:{exc.response.status_code}")
                return GuangyaUploadResult(
                    ok=False,
                    mode="live_error",
                    usedProfile=True,
                    profileId=profile.profileId,
                    parentId=normalized_parent_id,
                    status=int(exc.response.status_code),
                    error=f"http_error:{exc.response.status_code}",
                    note="Guangya binary upload request was rejected before multipart fallback.",
                    riskLevel=risk_level,
                    riskHint=risk_hint,
                    payload={"responseText": exc.response.text[:500]},
                )

        token_resp = client.upload_token(resolved_target_name, int(file_path.stat().st_size), normalized_parent_id)
        token_data = dict((token_resp or {}).get("data") or {})
        task_id = _pick_string(token_data.get("taskId"))
        flash_resp = client.check_can_flash_upload(task_id, file_path)
        if bool(((flash_resp or {}).get("data") or {}).get("canFlashUpload")):
            info_resp = client.upload_info(task_id)
            payload = {
                "taskId": task_id,
                "uploadInfo": info_resp,
                "requestedTargetName": normalized_target_name,
                "resolvedTargetName": resolved_target_name,
                "conflictAction": conflict_action,
            }
            verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
                profile_id=profile.profileId,
                parent_id=normalized_parent_id,
                target_name=resolved_target_name,
                upload_payload=payload,
            )
            return GuangyaUploadResult(
                ok=True,
                mode="binary_upload_fast_hit",
                usedProfile=True,
                profileId=profile.profileId,
                parentId=normalized_parent_id,
                status=200,
                error="",
                note=f"Guangya multipart fallback found a provider-side instant hit before CDN upload.{(' ' + conflict_note) if conflict_note else ''}",
                payload=payload,
                verifyOk=verify_ok,
                verifyMode=verify_mode,
                verifyNote=verify_note,
                verifyPayload=verify_payload,
            )

        client.cdn_upload(file_path, token_data, content_type="application/octet-stream")
        info_resp: dict[str, object] = {}
        for _ in range(5):
            current = client.upload_info(task_id)
            info_resp = current if isinstance(current, dict) else {"raw": current}
            if str(info_resp.get("msg") or "") == "文件上传中":
                sleep(2)
                continue
            break
        payload = {
            "taskId": task_id,
            "uploadInfo": info_resp,
            "requestedTargetName": normalized_target_name,
            "resolvedTargetName": resolved_target_name,
            "conflictAction": conflict_action,
        }
        verify_ok, verify_mode, verify_note, verify_payload = _verify_uploaded_file(
            profile_id=profile.profileId,
            parent_id=normalized_parent_id,
            target_name=resolved_target_name,
            upload_payload=payload,
        )
        return GuangyaUploadResult(
            ok=True,
            mode="binary_upload_multipart",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=normalized_parent_id,
            status=200,
            error="",
            note=f"Guangya binary upload completed through upload_token + cdn_upload fallback.{(' ' + conflict_note) if conflict_note else ''}",
            payload=payload,
            verifyOk=verify_ok,
            verifyMode=verify_mode,
            verifyNote=verify_note,
            verifyPayload=verify_payload,
        )
    except HTTPStatusError as exc:
        risk_level, risk_hint = _classify_upload_issue(int(exc.response.status_code or 0), f"http_error:{exc.response.status_code}")
        return GuangyaUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=normalized_parent_id,
            status=int(exc.response.status_code or 0),
            error=f"http_error:{exc.response.status_code}",
            note="Guangya binary upload failed during multipart upload flow.",
            riskLevel=risk_level,
            riskHint=risk_hint,
            payload={"responseText": exc.response.text[:500]},
        )
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_upload_issue(0, f"unexpected:{exc}")
        return GuangyaUploadResult(
            ok=False,
            mode="live_error",
            usedProfile=True,
            profileId=profile.profileId,
            parentId=normalized_parent_id,
            status=0,
            error=f"unexpected:{exc}",
            note="Guangya binary upload failed unexpectedly.",
            riskLevel=risk_level,
            riskHint=risk_hint,
        )
    finally:
        try:
            client.close()
        except Exception:
            pass
