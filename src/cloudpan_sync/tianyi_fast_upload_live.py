from __future__ import annotations

import hashlib
import hmac
import json
import random
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from .auth_store import get_profile
from .tianyi_live import _text


TIANYI_AUTH_API_URL = "https://api.cloud.189.cn/getSessionForPC.action"
TIANYI_CREATE_UPLOAD_URL = "https://api.cloud.189.cn/createUploadFile.action"
TIANYI_UPLOAD_STATUS_URL = "https://api.cloud.189.cn/getUploadFileStatus.action"
TIANYI_APP_ID = "8025431004"
TIANYI_PC_CLIENT_TYPE = "TELEPC"
TIANYI_PC_VERSION = "6.2"
TIANYI_PC_CHANNEL_ID = "web_cloud.189.cn"


@dataclass
class TianyiFastUploadResult:
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


def _load_profile_requirements(profile_id: str) -> tuple[object | None, str, str, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, "", "", ""
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
    signature = _text(extra.get("signature") or extra.get("Signature"))
    date_value = _text(extra.get("date") or extra.get("Date"))
    return profile, access_token, signature, date_value


def _client_suffix() -> dict[str, str]:
    return {
        "clientType": TIANYI_PC_CLIENT_TYPE,
        "version": TIANYI_PC_VERSION,
        "channelId": TIANYI_PC_CHANNEL_ID,
        "rand": f"{random.randint(0, 99999)}_{random.randint(0, 9999999999)}",
    }


def _http_date() -> str:
    from email.utils import formatdate

    return formatdate(usegmt=True)


def _signature_of_hmac(session_secret: str, session_key: str, method: str, full_url: str, date_of_gmt: str, param: str = "") -> str:
    url_path = urlsplit(full_url).path or "/"
    data = f"SessionKey={session_key}&Operate={method}&RequestURI={url_path}&Date={date_of_gmt}"
    if param:
        data += f"&params={param}"
    digest = hmac.new(session_secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha1).hexdigest()
    return digest.upper()


def _request_json(url: str, *, method: str = "GET", query: dict[str, str] | None = None, headers: dict[str, str] | None = None, form: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
    query_text = urlencode(query or {})
    full_url = url if not query_text else f"{url}?{query_text}"
    body = None
    request_headers = dict(headers or {})
    if form is not None:
        body = urlencode({k: v for k, v in form.items() if v is not None}).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    request = Request(full_url, data=body, headers=request_headers, method=method)
    with urlopen(request, timeout=20) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text) if text else {}
    return status, payload if isinstance(payload, dict) else {}


def _request_xml(url: str, *, method: str = "POST", query: dict[str, str] | None = None, headers: dict[str, str] | None = None, form: dict[str, object] | None = None) -> tuple[int, str]:
    query_text = urlencode(query or {})
    full_url = url if not query_text else f"{url}?{query_text}"
    body = None
    request_headers = dict(headers or {})
    if form is not None:
        body = urlencode({k: v for k, v in form.items() if v is not None}).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    request = Request(full_url, data=body, headers=request_headers, method=method)
    with urlopen(request, timeout=20) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    return status, text


def _extract_http_error_payload(exc: HTTPError) -> tuple[int, str]:
    try:
        text = exc.read().decode("utf-8", errors="replace")
    except Exception:
        text = ""
    return int(exc.code or 0), text


def _get_user_session(access_token: str) -> tuple[int, dict[str, object]]:
    query = {
        **_client_suffix(),
        "appId": TIANYI_APP_ID,
        "accessToken": access_token,
    }
    return _request_json(
        TIANYI_AUTH_API_URL,
        method="GET",
        query=query,
        headers={"X-Request-ID": str(uuid.uuid4())},
    )


def _signed_headers(session_key: str, session_secret: str, method: str, url: str) -> dict[str, str]:
    date_of_gmt = _http_date()
    return {
        "Date": date_of_gmt,
        "SessionKey": session_key,
        "X-Request-ID": str(uuid.uuid4()),
        "Signature": _signature_of_hmac(session_secret, session_key, method, url, date_of_gmt),
        "Accept": "application/json;charset=UTF-8",
        "Referer": "https://cloud.189.cn/",
        "User-Agent": "CloudPanSync/0.1",
    }


def _request_signed_json(url: str, *, form: dict[str, object], session_key: str, session_secret: str) -> tuple[int, dict[str, object]]:
    return _request_json(
        url,
        method="POST",
        query=_client_suffix(),
        headers=_signed_headers(session_key, session_secret, "POST", url),
        form=form,
    )


def _request_signed_json_get(url: str, *, query: dict[str, str], session_key: str, session_secret: str) -> tuple[int, dict[str, object]]:
    return _request_json(
        url,
        method="GET",
        query={**query, **_client_suffix()},
        headers=_signed_headers(session_key, session_secret, "GET", url),
    )


def _request_signed_xml(url: str, *, form: dict[str, object], session_key: str, session_secret: str) -> tuple[int, str]:
    return _request_xml(
        url,
        method="POST",
        query=_client_suffix(),
        headers=_signed_headers(session_key, session_secret, "POST", url),
        form=form,
    )


def _compute_local_md5(file_path: Path) -> str:
    hasher = hashlib.md5()
    with file_path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def _verify_local_md5(file_path: Path, expected_md5: str) -> tuple[bool, str]:
    actual_md5 = _compute_local_md5(file_path)
    normalized_expected = _text(expected_md5).lower() or actual_md5
    return normalized_expected == actual_md5, actual_md5


def _classify_issue(status: int, error: str) -> tuple[str, str]:
    if error == "profile_not_found":
        return ("input", "targetProfileId 对应的 189Cloud 授权档案不存在。")
    if error == "missing_access_token":
        return ("auth", "补 access token 后再试 189Cloud 秒传。")
    if error == "local_file_missing":
        return ("input", "localPath 对应本地文件不存在，无法继续做 189Cloud 秒传。")
    if error == "local_md5_mismatch":
        return ("input", "本地文件计算出的 md5 与任务条目不一致，先校验来源文件。")
    if error == "rapid_upload_not_hit":
        return ("provider", "189Cloud 已到达 createUploadFile，但当前没有命中秒传，后续仍需真实二进制上传 fallback。")
    if error.startswith("http_error:401"):
        return ("auth", "189Cloud 秒传请求被 401 拒绝，access token 很可能已失效。")
    if error.startswith("http_error:403"):
        return ("risk", "189Cloud 秒传请求被 403 拒绝，可能命中风控或权限不足。")
    if error.startswith("http_error:429"):
        return ("rate_limit", "189Cloud 秒传请求过快，建议稍后再试。")
    if status >= 500 or error.startswith("http_error:5"):
        return ("provider", "189Cloud provider 侧接口异常，建议稍后重试。")
    if error.startswith("url_error:"):
        return ("network", "189Cloud 秒传请求未能连通接口，请检查网络。")
    if error.startswith("unexpected:"):
        return ("unexpected", "189Cloud 秒传过程异常中断，建议保留错误文本继续排查。")
    return ("", "")


def _parse_commit_xml(text: str) -> dict[str, object]:
    root = ET.fromstring(text)
    return {
        "fileId": _text(root.findtext("id")),
        "name": _text(root.findtext("name")),
        "size": int(_text(root.findtext("size")) or "0"),
        "md5": _text(root.findtext("md5")).lower(),
        "createDate": _text(root.findtext("createDate")),
        "rawXml": text,
    }


def _upload_binary_to_file_upload_url(file_path: Path, file_upload_url: str, upload_file_id: int) -> tuple[int, dict[str, object]]:
    request = Request(
        file_upload_url,
        data=file_path.read_bytes(),
        headers={
            "ResumePolicy": "1",
            "Expect": "100-continue",
            "Edrive-UploadFileId": str(upload_file_id),
            "User-Agent": "CloudPanSync/0.1",
        },
        method="PUT",
    )
    with urlopen(request, timeout=60) as response:
        return int(getattr(response, "status", 0) or 0), {
            "status": int(getattr(response, "status", 0) or 0),
            "headers": dict(getattr(response, "headers", {}) or {}),
        }


def _extract_status_view(payload: dict[str, object], upload_file_id: int, fallback_upload_url: str, fallback_commit_url: str) -> dict[str, object]:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    if not isinstance(data, dict):
        data = {}
    data_size = int(data.get("dataSize", data.get("data_size", 0)) or 0)
    size = int(data.get("size", 0) or 0)
    file_data_exists = int(data.get("fileDataExists", payload.get("fileDataExists", 0)) or 0)
    resolved_upload_file_id = int(data.get("uploadFileId", payload.get("uploadFileId", upload_file_id)) or upload_file_id or 0)
    file_upload_url = _text(data.get("fileUploadUrl") or payload.get("fileUploadUrl") or fallback_upload_url)
    file_commit_url = _text(data.get("fileCommitUrl") or payload.get("fileCommitUrl") or fallback_commit_url)
    return {
        "uploadFileId": resolved_upload_file_id,
        "fileUploadUrl": file_upload_url,
        "fileCommitUrl": file_commit_url,
        "fileDataExists": file_data_exists,
        "dataSize": data_size,
        "size": size,
        "uploadedBytes": data_size + size,
        "raw": payload,
    }


def upload_tianyi_fast_file(
    *,
    profile_id: str,
    local_path: str,
    target_name: str,
    parent_id: str = "",
    expected_md5: str = "",
) -> TianyiFastUploadResult:
    profile, access_token, signature, date_value = _load_profile_requirements(profile_id)
    resolved_parent_id = _text(parent_id)
    if profile is None:
        risk_level, risk_hint = _classify_issue(0, "profile_not_found")
        return TianyiFastUploadResult(False, "profile_missing", False, profile_id, resolved_parent_id, 0, "profile_not_found", "Saved 189Cloud auth profile was not found.", risk_level, risk_hint)
    if not access_token:
        risk_level, risk_hint = _classify_issue(0, "missing_access_token")
        return TianyiFastUploadResult(False, "profile_incomplete", True, profile.profileId, resolved_parent_id, 0, "missing_access_token", "189Cloud fast upload requires token or extra.accessToken.", risk_level, risk_hint, payload={"requiredAuth": ["AccessToken"]})

    file_path = Path(str(local_path or "").strip())
    if not file_path.exists() or not file_path.is_file():
        risk_level, risk_hint = _classify_issue(0, "local_file_missing")
        return TianyiFastUploadResult(False, "local_file_missing", True, profile.profileId, resolved_parent_id, 0, "local_file_missing", "189Cloud fast upload requires an existing local file.", risk_level, risk_hint)

    md5_ok, actual_md5 = _verify_local_md5(file_path, expected_md5)
    if not md5_ok:
        risk_level, risk_hint = _classify_issue(0, "local_md5_mismatch")
        return TianyiFastUploadResult(
            False,
            "local_md5_mismatch",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            "local_md5_mismatch",
            "189Cloud fast upload aborted because local md5 does not match the task entry.",
            risk_level,
            risk_hint,
            payload={"actualMd5": actual_md5},
        )

    try:
        session_status, session_payload = _get_user_session(access_token)
        session_key = _text(session_payload.get("sessionKey"))
        session_secret = _text(session_payload.get("sessionSecret"))
        if not session_key or not session_secret:
            risk_level, risk_hint = _classify_issue(session_status, "unexpected:missing_session")
            return TianyiFastUploadResult(
                False,
                "rapid_upload_request_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                session_status,
                "unexpected:missing_session",
                "189Cloud access token refresh did not return sessionKey/sessionSecret for the upload request.",
                risk_level,
                risk_hint,
                payload={
                    "sessionResponse": session_payload,
                    "requiredAuth": ["AccessToken", "Signature", "Date"],
                    "providedWriteHeaders": bool(signature and date_value),
                },
            )

        create_status, create_payload = _request_signed_json(
            TIANYI_CREATE_UPLOAD_URL,
            form={
                "parentFolderId": resolved_parent_id,
                "fileName": _text(target_name or file_path.name) or file_path.name,
                "size": int(file_path.stat().st_size),
                "md5": actual_md5,
                "opertype": "3",
                "flag": "1",
                "resumePolicy": "1",
                "isLog": "0",
            },
            session_key=session_key,
            session_secret=session_secret,
        )
        upload_file_id = int(create_payload.get("uploadFileId", 0) or 0)
        file_upload_url = _text(create_payload.get("fileUploadUrl"))
        commit_url = _text(create_payload.get("fileCommitUrl"))
        file_data_exists = int(create_payload.get("fileDataExists", 0) or 0)
        common_payload = {
            "sessionResponse": session_payload,
            "createResponse": create_payload,
            "uploadFileId": upload_file_id,
            "fileUploadUrl": file_upload_url,
            "fileCommitUrl": commit_url,
            "fileDataExists": file_data_exists,
            "resolvedTargetName": _text(target_name or file_path.name) or file_path.name,
            "conflictAction": "",
            "md5": actual_md5,
            "providedWriteHeaders": bool(signature and date_value),
        }

        if file_data_exists != 1:
            if not file_upload_url or upload_file_id <= 0 or not commit_url:
                risk_level, risk_hint = _classify_issue(create_status, "rapid_upload_not_hit")
                return TianyiFastUploadResult(
                    False,
                    "rapid_upload_not_hit",
                    True,
                    profile.profileId,
                    resolved_parent_id,
                    create_status,
                    "rapid_upload_not_hit",
                    "189Cloud createUploadFile reached the live API, but the provider did not confirm a direct file reuse hit.",
                    risk_level,
                    risk_hint,
                    payload=common_payload,
                    verifyOk=False,
                    verifyMode="create_upload_response",
                    verifyNote="The live createUploadFile request reached 189Cloud, but fileDataExists did not indicate a rapid-upload hit.",
                    verifyPayload={"fileDataExists": file_data_exists},
                )

            put_status, put_payload = _upload_binary_to_file_upload_url(file_path, file_upload_url, upload_file_id)
            status_status, status_payload = _request_signed_json_get(
                TIANYI_UPLOAD_STATUS_URL,
                query={
                    "uploadFileId": str(upload_file_id),
                    "resumePolicy": "1",
                },
                session_key=session_key,
                session_secret=session_secret,
            )
            status_view = _extract_status_view(status_payload, upload_file_id, file_upload_url, commit_url)
            common_payload["binaryUploadResponse"] = put_payload
            common_payload["statusResponse"] = status_payload
            common_payload["statusView"] = status_view
            common_payload["uploadPutStatus"] = put_status
            commit_status, commit_text = _request_signed_xml(
                status_view["fileCommitUrl"] or commit_url,
                form={
                    "opertype": "3",
                    "resumePolicy": "1",
                    "uploadFileId": str(status_view["uploadFileId"] or upload_file_id),
                    "isLog": "0",
                },
                session_key=session_key,
                session_secret=session_secret,
            )
            commit_payload = _parse_commit_xml(commit_text)
            common_payload["commitResponse"] = commit_payload
            verify_ok = _text(commit_payload.get("md5")).lower() in {"", actual_md5}
            return TianyiFastUploadResult(
                True,
                "binary_upload_put_then_commit",
                True,
                profile.profileId,
                resolved_parent_id,
                commit_status or status_status or put_status or create_status,
                "",
                "189Cloud createUploadFile hash miss fell back to binary upload, and the provider commit response confirmed the file.",
                payload=common_payload,
                verifyOk=verify_ok,
                verifyMode="commit_response_xml_after_binary_put",
                verifyNote="189Cloud hash miss fallback was verified by fileUploadUrl PUT, status polling, and the final commit response XML.",
                verifyPayload={
                    **commit_payload,
                    "statusView": status_view,
                },
            )

        if not commit_url or upload_file_id <= 0:
            risk_level, risk_hint = _classify_issue(create_status, "unexpected:missing_commit_info")
            return TianyiFastUploadResult(
                False,
                "rapid_upload_request_failed",
                True,
                profile.profileId,
                resolved_parent_id,
                create_status,
                "unexpected:missing_commit_info",
                "189Cloud createUploadFile reported a reuse hit, but did not provide enough commit information.",
                risk_level,
                risk_hint,
                payload=common_payload,
            )

        commit_status, commit_text = _request_signed_xml(
            commit_url,
            form={
                "opertype": "3",
                "resumePolicy": "1",
                "uploadFileId": str(upload_file_id),
                "isLog": "0",
            },
            session_key=session_key,
            session_secret=session_secret,
        )
        commit_payload = _parse_commit_xml(commit_text)
        common_payload["commitResponse"] = commit_payload
        return TianyiFastUploadResult(
            True,
            "rapid_upload_by_hash",
            True,
            profile.profileId,
            resolved_parent_id,
            commit_status,
            "",
            "189Cloud rapid-upload request succeeded and was confirmed by the provider commit response.",
            payload=common_payload,
            verifyOk=True,
            verifyMode="commit_response_xml",
            verifyNote="189Cloud rapid-upload success was confirmed by the createUploadFile + fileCommitUrl response chain.",
            verifyPayload=commit_payload,
        )
    except HTTPError as exc:
        status, error_payload = _extract_http_error_payload(exc)
        risk_level, risk_hint = _classify_issue(status, f"http_error:{status}")
        return TianyiFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            status,
            f"http_error:{status}",
            "189Cloud rapid-upload request reached the API but was rejected.",
            risk_level,
            risk_hint,
            payload={"errorResponse": error_payload, "md5": actual_md5},
        )
    except URLError as exc:
        risk_level, risk_hint = _classify_issue(0, f"url_error:{exc.reason}")
        return TianyiFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            f"url_error:{exc.reason}",
            "189Cloud rapid-upload request could not reach the API endpoint.",
            risk_level,
            risk_hint,
            payload={"md5": actual_md5},
        )
    except json.JSONDecodeError:
        risk_level, risk_hint = _classify_issue(200, "unexpected:invalid_json")
        return TianyiFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            200,
            "unexpected:invalid_json",
            "189Cloud rapid-upload request returned non-JSON content.",
            risk_level,
            risk_hint,
            payload={"md5": actual_md5},
        )
    except ET.ParseError:
        risk_level, risk_hint = _classify_issue(200, "unexpected:invalid_xml")
        return TianyiFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            200,
            "unexpected:invalid_xml",
            "189Cloud rapid-upload commit request returned non-XML content.",
            risk_level,
            risk_hint,
            payload={"md5": actual_md5},
        )
    except Exception as exc:  # pragma: no cover
        risk_level, risk_hint = _classify_issue(0, f"unexpected:{exc}")
        return TianyiFastUploadResult(
            False,
            "rapid_upload_request_failed",
            True,
            profile.profileId,
            resolved_parent_id,
            0,
            f"unexpected:{exc}",
            "189Cloud rapid-upload request failed unexpectedly.",
            risk_level,
            risk_hint,
            payload={"md5": actual_md5},
        )
