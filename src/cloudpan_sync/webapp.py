from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .auth_store import (
    build_profile,
    build_updated_profile,
    delete_profile,
    get_profile,
    list_profiles,
    masked_profile,
    update_profile,
)
from .auth_profile_view import auth_profile_view
from .auth_live_validate import (
    append_live_validation,
    latest_live_validations,
    list_live_validations,
    live_validation_summary,
    run_all_profile_live_validations,
    run_profile_live_validation,
    validate_profile_object,
)
from .auth_profile_evidence import (
    build_auth_evidence_bundle,
    build_auth_profile_evidence,
    auth_evidence_bundle_to_markdown,
    auth_profile_evidence_to_markdown,
    refresh_auth_evidence_bundle,
    refresh_auth_profile_evidence,
)
from .auth_profile_remediation import build_auth_remediation_bundle, auth_remediation_bundle_to_markdown
from .aliyun_open_live import fetch_aliyun_open_live_list, fetch_aliyun_open_live_metadata, fetch_aliyun_open_create_folder
from .baidu_netdisk_live import fetch_baidu_create_dir, fetch_baidu_live_list, fetch_baidu_live_metadata
from .auth import build_session_token, verify_session_token
from .config import ADMIN_PASSWORD, SESSION_COOKIE
from .i18n import MESSAGES, messages_for
from .models import AuthLiveValidateRequest, AuthProfileInput, ConflictPolicy, SourceEntry
from .models import TaskActionRequest, TaskCreateRequest
from .pan115_open_live import fetch_115_open_create_folder, fetch_115_open_live_list, fetch_115_open_live_metadata
from .pan123_open_live import fetch_123_open_create_folder, fetch_123_open_live_list, fetch_123_open_live_metadata
from .pikpak_live import fetch_pikpak_create_folder, fetch_pikpak_live_list, fetch_pikpak_live_metadata
from .quark_live import fetch_quark_live_list, fetch_quark_live_metadata, fetch_quark_create_folder
from .uc_live import fetch_uc_live_list, fetch_uc_live_metadata, fetch_uc_create_folder
from .xunlei_live import fetch_xunlei_create_folder, fetch_xunlei_live_list, fetch_xunlei_live_metadata
from .guangya import guangya_fast_check, guangya_mock_list
from .guangya_live import fetch_guangya_live_list, fetch_guangya_live_metadata, fetch_guangya_create_dir, fetch_guangya_live_fast_check
from .planner import build_transfer_plan
from .provider_mock import provider_mock_list, provider_mock_metadata
from .provider_research import build_provider_research_index
from .provider_registry import build_provider_registry
from .plan_audit import run_plan_audit, to_markdown
from .live_probe import run_live_probe, probe_to_markdown
from .provider_status_matrix import build_status_matrix, matrix_to_markdown
from .real_evidence_report import build_real_evidence_report, real_evidence_to_markdown
from .provider_live_probe import run_provider_live_probe
from .provider_live_probe_store import (
    delete_provider_live_probe,
    latest_provider_live_probes,
    list_provider_live_probes,
    provider_live_probe_summary,
    save_provider_live_probe,
)
from .task_runtime_evidence_store import delete_task_runtime_evidence
from .task_runtime_evidence_store import (
    build_task_runtime_evidence_payload,
    task_runtime_evidence_to_markdown,
)
from .tianyi_live import fetch_tianyi_live_list, fetch_tianyi_live_metadata, fetch_tianyi_create_folder
from .task_runtime import (
    acknowledge_task_risk,
    build_task_detail_view,
    build_task_list_view,
    create_task,
    get_task,
    list_tasks,
    pause_task,
    resume_task,
    retry_task,
    run_task,
)


WEB_DIR = Path(__file__).parent / "web"


class LoginRequest(BaseModel):
    password: str


class MockPlanRequest(BaseModel):
    sourceProvider: str
    targetProvider: str
    thresholdMB: int = 0
    conflictPolicy: ConflictPolicy = "auto_rename_new"
    selectedRoots: list[str] = []
    entries: list[SourceEntry]


class CaptureStartRequest(BaseModel):
    providerKey: str


class RefreshEvidenceRequest(BaseModel):
    pageSize: int = 100
    dirName: str = ""


class RefreshEvidenceBundleRequest(BaseModel):
    pageSize: int = 100
    dirName: str = ""


class GuangyaListRequest(BaseModel):
    path: str = "/"
    profileId: str = ""
    parentId: str = ""
    pageSize: int = 100
    preferLive: bool = True


class GuangyaFastCheckRequest(BaseModel):
    entries: list[SourceEntry]


class GuangyaLiveFastCheckRequest(BaseModel):
    profileId: str
    parentId: str = ""
    entries: list[SourceEntry]


class ProviderPathRequest(BaseModel):
    path: str = "/"
    profileId: str = ""
    preferLive: bool = True
    parentId: str = ""
    pageSize: int = 100
    fileId: str = ""


class ProviderLiveProbeRequest(BaseModel):
    profileId: str
    parentId: str = ""
    fileId: str = ""
    pageSize: int = 100
    dirName: str = ""


class GuangyaCreateDirRequest(BaseModel):
    profileId: str
    parentId: str = ""
    dirName: str


class AliyunCreateDirRequest(BaseModel):
    profileId: str
    parentId: str = "root"
    dirName: str


class Pan123CreateDirRequest(BaseModel):
    profileId: str
    parentId: str = "0"
    dirName: str


class Pan115CreateDirRequest(BaseModel):
    profileId: str
    parentId: str = "0"
    dirName: str


class PikPakCreateDirRequest(BaseModel):
    profileId: str
    parentId: str = ""
    dirName: str


class BaiduCreateDirRequest(BaseModel):
    profileId: str
    parentId: str = "/"
    dirName: str


class XunleiCreateDirRequest(BaseModel):
    profileId: str
    parentId: str = ""
    dirName: str


class QuarkCreateDirRequest(BaseModel):
    profileId: str
    parentId: str = "0"
    dirName: str


class UcCreateDirRequest(BaseModel):
    profileId: str
    parentId: str = "0"
    dirName: str


class TianyiCreateDirRequest(BaseModel):
    profileId: str
    parentId: str = ""
    dirName: str


def _capture_login_url(provider_key: str) -> str:
    for item in build_provider_research_index():
        if str(item.get("providerKey") or "") == provider_key:
            url = str(item.get("webLoginUrl") or "").strip()
            if url:
                return url
    return ""


def _capture_field_hints(provider_key: str) -> list[str]:
    mapping = {
        "guangya": ["token or extra.authorization", "extra.parentId", "optional extra.did", "optional extra.dt"],
        "aliyundrive_open": ["token or extra.authorization", "extra.domainId", "extra.driveId"],
        "189cloud": [
            "share-read probe: extra.shareCode",
            "optional extra.accessCode",
            "account write auth: token or extra.accessToken",
            "account write auth: extra.signature",
            "account write auth: extra.date",
            "optional helper: patch_189cloud_account_auth.py from captured headers/curl",
            "optional extra.fileId",
        ],
        "baidu_netdisk": ["token or extra.authorization, or cookie", "optional extra.fileId", "optional extra.path"],
        "123_open": ["token or extra.authorization", "optional extra.parentFileId", "optional extra.fileId"],
        "115_open": ["cookie or extra.cookie_header", "optional extra.parentId or extra.cid", "optional extra.fileId"],
        "xunlei": ["token or extra.authorization", "extra.deviceId or extra.x-device-id", "optional extra.fileId"],
        "pikpak": ["token or extra.authorization", "optional extra.deviceId", "optional extra.fileId"],
        "quark": ["cookie or extra.cookie_header", "extra.pwdId or extra.sharePwdId", "optional extra.passcode", "optional extra.fileId"],
        "uc": ["cookie or extra.cookie_header", "extra.pwdId or extra.sharePwdId", "optional extra.passcode", "optional extra.fileId"],
    }
    return mapping.get(provider_key, [])


def _auth_profile_view(profile: object) -> dict[str, object]:
    return auth_profile_view(profile)


def _auth_profile_evidence(profile: object) -> dict[str, object]:
    profile_view = _auth_profile_view(profile)
    return build_auth_profile_evidence(profile=profile, profile_view=profile_view)


def _is_logged_in(request: Request) -> bool:
    token = request.cookies.get(SESSION_COOKIE, "")
    return verify_session_token(token)


def create_app() -> FastAPI:
    app = FastAPI(title="CloudPan Sync")
    app.mount("/assets", StaticFiles(directory=WEB_DIR / "assets"), name="assets")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB_DIR / "index.html")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/i18n")
    def i18n(lang: str = "zh-CN") -> dict[str, object]:
        return {
            "lang": lang if lang in MESSAGES else "zh-CN",
            "messages": messages_for(lang),
        }

    @app.get("/api/providers")
    def providers() -> dict[str, object]:
        rows = [adapter.profile.model_dump() for adapter in build_provider_registry()]
        return {"items": rows}

    @app.get("/api/providers/research")
    def provider_research(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return {"items": build_provider_research_index()}

    @app.get("/api/plan/audit")
    def plan_audit(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return run_plan_audit()

    @app.get("/api/plan/audit_markdown")
    def plan_audit_markdown(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        audit = run_plan_audit()
        return {"markdown": to_markdown(audit)}

    @app.get("/api/providers/live_probe")
    def providers_live_probe(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return run_live_probe()

    @app.get("/api/providers/live_probe_markdown")
    def providers_live_probe_markdown(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        data = run_live_probe()
        return {"markdown": probe_to_markdown(data)}

    @app.get("/api/providers/status_matrix")
    def providers_status_matrix(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return build_status_matrix()

    @app.get("/api/providers/status_matrix_markdown")
    def providers_status_matrix_markdown(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        data = build_status_matrix()
        return {"markdown": matrix_to_markdown(data)}

    @app.get("/api/real_evidence")
    def real_evidence_report(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return build_real_evidence_report()

    @app.get("/api/real_evidence_markdown")
    def real_evidence_report_markdown(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        data = build_real_evidence_report()
        return {"markdown": real_evidence_to_markdown(data)}

    @app.get("/api/task_runtime_evidence")
    def task_runtime_evidence(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return build_task_runtime_evidence_payload()

    @app.get("/api/task_runtime_evidence_markdown")
    def task_runtime_evidence_markdown(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        data = build_task_runtime_evidence_payload()
        return {"markdown": task_runtime_evidence_to_markdown(data)}

    @app.post("/api/providers/live_probe_profile")
    def provider_live_probe_profile(payload: ProviderLiveProbeRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        item = run_provider_live_probe(
            profile_id=payload.profileId,
            parent_id=payload.parentId,
            file_id=payload.fileId,
            page_size=payload.pageSize,
            dir_name=payload.dirName,
        )
        save_provider_live_probe(item)
        return {"item": item}

    @app.get("/api/providers/live_probe_results")
    def provider_live_probe_results(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return {
            "items": list_provider_live_probes(),
            "latestItems": latest_provider_live_probes(),
            "summary": provider_live_probe_summary(),
        }

    @app.get("/api/auth/profiles")
    def auth_profiles(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return {"items": [_auth_profile_view(p) for p in list_profiles()]}

    @app.get("/api/auth/remediation_bundle")
    def auth_remediation_bundle(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return build_auth_remediation_bundle(profile_views=[_auth_profile_view(p) for p in list_profiles()])

    @app.get("/api/auth/remediation_bundle_markdown")
    def auth_remediation_bundle_markdown(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        bundle = build_auth_remediation_bundle(profile_views=[_auth_profile_view(p) for p in list_profiles()])
        return {"markdown": auth_remediation_bundle_to_markdown(bundle)}

    @app.get("/api/auth/evidence_bundle")
    def auth_evidence_bundle(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return build_auth_evidence_bundle(profiles=list_profiles(), profile_view_builder=_auth_profile_view)

    @app.get("/api/auth/evidence_bundle_markdown")
    def auth_evidence_bundle_markdown(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        bundle = build_auth_evidence_bundle(profiles=list_profiles(), profile_view_builder=_auth_profile_view)
        return {"markdown": auth_evidence_bundle_to_markdown(bundle)}

    @app.post("/api/auth/refresh_evidence_bundle")
    def auth_refresh_evidence_bundle(payload: RefreshEvidenceBundleRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        bundle = refresh_auth_evidence_bundle(
            profiles=list_profiles(),
            profile_view_builder=_auth_profile_view,
            page_size=payload.pageSize,
            dir_name=payload.dirName,
            persist=True,
        )
        return {
            "bundle": bundle,
            "markdown": auth_evidence_bundle_to_markdown(bundle),
        }

    @app.get("/api/auth/profiles/{profile_id}/evidence")
    def auth_profile_evidence(profile_id: str, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        profile = get_profile(profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="profile_not_found")
        return _auth_profile_evidence(profile)

    @app.get("/api/auth/profiles/{profile_id}/evidence_markdown")
    def auth_profile_evidence_markdown(profile_id: str, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        profile = get_profile(profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="profile_not_found")
        return {"markdown": auth_profile_evidence_to_markdown(_auth_profile_evidence(profile))}

    @app.post("/api/auth/profiles/{profile_id}/refresh_evidence")
    def auth_profile_refresh_evidence(profile_id: str, payload: RefreshEvidenceRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        profile = get_profile(profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="profile_not_found")
        evidence = refresh_auth_profile_evidence(
            profile=profile,
            page_size=payload.pageSize,
            dir_name=payload.dirName,
            persist=True,
            profile_view_builder=_auth_profile_view,
        )
        return {
            "evidence": evidence,
            "markdown": auth_profile_evidence_to_markdown(evidence),
        }

    @app.post("/api/auth/profiles")
    def auth_profile_create(payload: AuthProfileInput, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        profile = build_profile(payload)
        validation = validate_profile_object(profile)
        if bool(validation.get("ok")):
            profile.status = "verified"
            profile.lastError = ""
        else:
            profile.status = "invalid"
            profile.lastError = str(validation.get("error") or validation.get("summary") or "live_validation_failed")
        profile.updatedAt = datetime.now(timezone.utc).isoformat()
        update_profile(profile)
        append_live_validation(validation)
        return {"item": _auth_profile_view(profile), "validation": validation}

    @app.put("/api/auth/profiles/{profile_id}")
    def auth_profile_update(profile_id: str, payload: AuthProfileInput, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        existing = get_profile(profile_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="profile_not_found")
        profile = build_updated_profile(existing, payload)
        validation = validate_profile_object(profile)
        if bool(validation.get("ok")):
            profile.status = "verified"
            profile.lastError = ""
        else:
            profile.status = "invalid"
            profile.lastError = str(validation.get("error") or validation.get("summary") or "live_validation_failed")
        profile.updatedAt = datetime.now(timezone.utc).isoformat()
        update_profile(profile)
        append_live_validation(validation)
        return {"item": _auth_profile_view(profile), "validation": validation}

    @app.delete("/api/auth/profiles/{profile_id}")
    def auth_profile_delete(profile_id: str, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        ok = delete_profile(profile_id)
        if not ok:
            raise HTTPException(status_code=404, detail="profile_not_found")
        delete_provider_live_probe(profile_id)
        delete_task_runtime_evidence(profile_id)
        return {"ok": True}

    @app.post("/api/auth/capture/start")
    def auth_capture_start(payload: CaptureStartRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        login_url = _capture_login_url(payload.providerKey)
        field_hints = _capture_field_hints(payload.providerKey)
        return {
            "providerKey": payload.providerKey,
            "status": "capture_pending",
            "loginUrlHint": login_url or f"https://{payload.providerKey}.example.com/login",
            "requiredFieldHints": field_hints,
            "message": "Open the provider login page, complete login in your browser, then paste token/cookie and any required extra fields into the auth form.",
        }

    @app.post("/api/auth/profiles/{profile_id}/validate")
    def auth_profile_validate(profile_id: str, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        profile = get_profile(profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="profile_not_found")
        row = run_profile_live_validation(profile_id)
        if bool(row.get("ok")):
            profile.status = "verified"
            profile.lastError = ""
        else:
            profile.status = "invalid"
            profile.lastError = str(row.get("error") or row.get("summary") or "live_validation_failed")
        profile.updatedAt = datetime.now(timezone.utc).isoformat()
        update_profile(profile)
        return {"item": _auth_profile_view(profile), "validation": row}

    @app.get("/api/auth/live_validations")
    def auth_live_validations(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return {
            "items": list_live_validations(),
            "latestItems": latest_live_validations(),
            "summary": live_validation_summary(),
        }

    @app.post("/api/auth/live_validate")
    def auth_live_validate(payload: AuthLiveValidateRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        row = run_profile_live_validation(payload.profileId)
        return {"item": row}

    @app.post("/api/auth/live_validate_all")
    def auth_live_validate_all(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return run_all_profile_live_validations()

    @app.get("/api/session")
    def session(request: Request) -> dict[str, bool]:
        return {"loggedIn": _is_logged_in(request)}

    @app.post("/api/login")
    def login(payload: LoginRequest, response: Response) -> JSONResponse:
        if payload.password != ADMIN_PASSWORD:
            raise HTTPException(status_code=401, detail="invalid_password")
        token = build_session_token("admin")
        response = JSONResponse({"ok": True})
        response.set_cookie(
            key=SESSION_COOKIE,
            value=token,
            httponly=True,
            samesite="lax",
        )
        return response

    @app.post("/api/logout")
    def logout(response: Response) -> JSONResponse:
        response = JSONResponse({"ok": True})
        response.delete_cookie(SESSION_COOKIE)
        return response

    @app.post("/api/plan/mock")
    def mock_plan(payload: MockPlanRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        plan = build_transfer_plan(
            source_provider=payload.sourceProvider,
            target_provider=payload.targetProvider,
            entries=payload.entries,
            threshold_mb=payload.thresholdMB,
            conflict_policy=payload.conflictPolicy,
            selected_roots=payload.selectedRoots,
        )
        return plan.model_dump()

    @app.post("/api/providers/guangya/list")
    def guangya_list(payload: GuangyaListRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = None
        if payload.preferLive and payload.profileId:
            live_result = fetch_guangya_live_list(
                profile_id=payload.profileId,
                parent_id=payload.parentId,
                page_size=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": "guangya",
                    "path": payload.path,
                    "parentId": live_result.parentId,
                    "items": live_result.items,
                    "mode": "live",
                    "usedProfile": live_result.usedProfile,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                }
        return {
            "providerKey": "guangya",
            "path": payload.path,
            "items": guangya_mock_list(payload.path),
            "mode": "mock",
            "usedProfile": bool(payload.profileId),
            "profileId": payload.profileId,
            "fallbackReason": live_result.error if live_result is not None else "",
            "note": (
                live_result.note
                if live_result is not None and not live_result.ok
                else "This is a local mock list in M4. Provide a Guangya auth profile with token and parentId to try live listing."
            ),
        }

    @app.post("/api/providers/guangya/fast_check")
    def guangya_fast_precheck(payload: GuangyaFastCheckRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        rows: list[dict[str, object]] = []
        for entry in payload.entries:
            result = guangya_fast_check(entry)
            rows.append(
                {
                    "path": entry.path,
                    "size": entry.size,
                    "supported": result.supported,
                    "hashKind": result.hashKind,
                    "normalizedHash": result.normalizedHash,
                    "reason": result.reason,
                    "riskHint": result.riskHint,
                }
            )
        return {
            "providerKey": "guangya",
            "mode": "local_precheck",
            "items": rows,
        }

    @app.post("/api/providers/guangya/live_fast_check")
    def guangya_live_fast_precheck(payload: GuangyaLiveFastCheckRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_guangya_live_fast_check(
            profile_id=payload.profileId,
            entries=payload.entries,
            parent_id=payload.parentId,
        )
        return live_result.to_dict()

    @app.post("/api/providers/guangya/create_dir")
    def guangya_create_dir(payload: GuangyaCreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_guangya_create_dir(
            profile_id=payload.profileId,
            parent_id=payload.parentId,
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "guangya",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": live_result.parentId,
                "item": live_result.items[0] if live_result.items else {},
                "note": live_result.note,
            }
        return {
            "providerKey": "guangya",
            "mode": "live_error",
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId,
            "fallbackReason": live_result.error,
            "note": live_result.note,
        }

    @app.post("/api/providers/aliyundrive_open/create_dir")
    def aliyun_create_dir(payload: AliyunCreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_aliyun_open_create_folder(
            profile_id=payload.profileId,
            parent_file_id=payload.parentId or "root",
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "aliyundrive_open",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": payload.parentId or "root",
                "item": live_result.payload.get("item", {}),
                "note": live_result.note,
                "domainId": live_result.payload.get("domainId", ""),
                "driveId": live_result.payload.get("driveId", ""),
            }
        return {
            "providerKey": "aliyundrive_open",
            "mode": "live_error",
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId or "root",
            "fallbackReason": live_result.error,
            "note": live_result.note,
        }

    @app.post("/api/providers/123_open/create_dir")
    def pan123_create_dir(payload: Pan123CreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_123_open_create_folder(
            profile_id=payload.profileId,
            parent_file_id=payload.parentId or "0",
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "123_open",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": payload.parentId or "0",
                "item": live_result.payload.get("item", {}),
                "note": live_result.note,
            }
        return {
            "providerKey": "123_open",
            "mode": "live_error",
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId or "0",
            "fallbackReason": live_result.error,
            "note": live_result.note,
        }

    @app.post("/api/providers/189cloud/create_dir")
    def tianyi_create_dir(payload: TianyiCreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_tianyi_create_folder(
            profile_id=payload.profileId,
            parent_id=payload.parentId,
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "189cloud",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": live_result.payload.get("parentId", payload.parentId),
                "item": live_result.payload.get("item", {}),
                "note": live_result.note,
            }
        return {
            "providerKey": "189cloud",
            "mode": live_result.mode,
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId,
            "fallbackReason": live_result.error,
            "note": live_result.note,
            "requiredAuth": live_result.payload.get("requiredAuth", []),
        }

    @app.post("/api/providers/115_open/create_dir")
    def pan115_create_dir(payload: Pan115CreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_115_open_create_folder(
            profile_id=payload.profileId,
            parent_id=payload.parentId or "0",
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "115_open",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": payload.parentId or "0",
                "item": live_result.payload.get("item", {}),
                "note": live_result.note,
            }
        return {
            "providerKey": "115_open",
            "mode": "live_error",
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId or "0",
            "fallbackReason": live_result.error,
            "note": live_result.note,
        }

    @app.post("/api/providers/pikpak/create_dir")
    def pikpak_create_dir(payload: PikPakCreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_pikpak_create_folder(
            profile_id=payload.profileId,
            parent_id=payload.parentId,
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "pikpak",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": live_result.payload.get("parentId", ""),
                "item": live_result.payload.get("item", {}),
                "note": live_result.note,
            }
        return {
            "providerKey": "pikpak",
            "mode": "live_error",
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId,
            "fallbackReason": live_result.error,
            "note": live_result.note,
        }

    @app.post("/api/providers/baidu_netdisk/create_dir")
    def baidu_create_dir(payload: BaiduCreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_baidu_create_dir(
            profile_id=payload.profileId,
            parent_dir=payload.parentId or "/",
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "baidu_netdisk",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": live_result.payload.get("dir", "/"),
                "item": live_result.payload.get("item", {}),
                "note": live_result.note,
            }
        return {
            "providerKey": "baidu_netdisk",
            "mode": "live_error",
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId or "/",
            "fallbackReason": live_result.error,
            "note": live_result.note,
        }

    @app.post("/api/providers/xunlei/create_dir")
    def xunlei_create_dir(payload: XunleiCreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_xunlei_create_folder(
            profile_id=payload.profileId,
            parent_id=payload.parentId,
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "xunlei",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": live_result.payload.get("parentId", ""),
                "item": live_result.payload.get("item", {}),
                "note": live_result.note,
            }
        return {
            "providerKey": "xunlei",
            "mode": "live_error",
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId,
            "fallbackReason": live_result.error,
            "note": live_result.note,
        }

    @app.post("/api/providers/quark/create_dir")
    def quark_create_dir(payload: QuarkCreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_quark_create_folder(
            profile_id=payload.profileId,
            parent_id=payload.parentId or "0",
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "quark",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": live_result.payload.get("parentId", payload.parentId or "0"),
                "item": live_result.payload.get("item", {}),
                "note": live_result.note,
            }
        return {
            "providerKey": "quark",
            "mode": "live_error",
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId or "0",
            "fallbackReason": live_result.error,
            "note": live_result.note,
        }

    @app.post("/api/providers/uc/create_dir")
    def uc_create_dir(payload: UcCreateDirRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        live_result = fetch_uc_create_folder(
            profile_id=payload.profileId,
            parent_id=payload.parentId or "0",
            dir_name=payload.dirName,
        )
        if live_result.ok:
            return {
                "providerKey": "uc",
                "mode": "live",
                "usedProfile": True,
                "profileId": live_result.profileId,
                "status": live_result.status,
                "parentId": live_result.payload.get("parentId", payload.parentId or "0"),
                "item": live_result.payload.get("item", {}),
                "note": live_result.note,
            }
        return {
            "providerKey": "uc",
            "mode": "live_error",
            "usedProfile": True,
            "profileId": payload.profileId,
            "parentId": payload.parentId or "0",
            "fallbackReason": live_result.error,
            "note": live_result.note,
        }

    @app.post("/api/providers/{provider_key}/list")
    def provider_list(provider_key: str, payload: ProviderPathRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        if provider_key == "189cloud" and payload.preferLive and payload.profileId:
            live_result = fetch_tianyi_live_list(
                profile_id=payload.profileId,
                file_id=payload.fileId,
                page_size=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "items": live_result.payload.get("items", []),
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                    "shareCode": live_result.payload.get("shareCode", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "items": provider_mock_list(provider_key, payload.path),
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "baidu_netdisk" and payload.preferLive and payload.profileId:
            live_result = fetch_baidu_live_list(
                profile_id=payload.profileId,
                dir_path=payload.parentId or payload.path or "/",
                limit=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "items": live_result.payload.get("items", []),
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                    "dir": live_result.payload.get("dir", "/"),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "items": provider_mock_list(provider_key, payload.path),
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "115_open" and payload.preferLive and payload.profileId:
            live_result = fetch_115_open_live_list(
                profile_id=payload.profileId,
                cid=payload.parentId or "0",
                limit=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "items": live_result.payload.get("items", []),
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                    "cid": live_result.payload.get("cid", "0"),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "items": provider_mock_list(provider_key, payload.path),
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "quark" and payload.preferLive and payload.profileId:
            live_result = fetch_quark_live_list(
                profile_id=payload.profileId,
                parent_id=payload.parentId or "0",
                page_size=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "items": live_result.payload.get("items", []),
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                    "parentId": live_result.payload.get("parentId", "0"),
                    "pwdId": live_result.payload.get("pwdId", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "items": provider_mock_list(provider_key, payload.path),
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "pikpak" and payload.preferLive and payload.profileId:
            live_result = fetch_pikpak_live_list(
                profile_id=payload.profileId,
                parent_id=payload.parentId,
                limit=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "items": live_result.payload.get("items", []),
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                    "parentId": live_result.payload.get("parentId", ""),
                    "nextPageToken": live_result.payload.get("nextPageToken", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "items": provider_mock_list(provider_key, payload.path),
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "uc" and payload.preferLive and payload.profileId:
            live_result = fetch_uc_live_list(
                profile_id=payload.profileId,
                parent_id=payload.parentId or "0",
                page_size=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "items": live_result.payload.get("items", []),
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                    "parentId": live_result.payload.get("parentId", "0"),
                    "pwdId": live_result.payload.get("pwdId", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "items": provider_mock_list(provider_key, payload.path),
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "xunlei" and payload.preferLive and payload.profileId:
            live_result = fetch_xunlei_live_list(
                profile_id=payload.profileId,
                parent_id=payload.parentId,
                limit=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "items": live_result.payload.get("items", []),
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                    "parentId": live_result.payload.get("parentId", ""),
                    "nextPageToken": live_result.payload.get("nextPageToken", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "items": provider_mock_list(provider_key, payload.path),
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "aliyundrive_open" and payload.preferLive and payload.profileId:
            live_result = fetch_aliyun_open_live_list(
                profile_id=payload.profileId,
                parent_file_id=payload.parentId or "root",
                limit=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "items": live_result.payload.get("items", []),
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                    "domainId": live_result.payload.get("domainId", ""),
                    "driveId": live_result.payload.get("driveId", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "items": provider_mock_list(provider_key, payload.path),
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "123_open" and payload.preferLive and payload.profileId:
            live_result = fetch_123_open_live_list(
                profile_id=payload.profileId,
                parent_file_id=payload.parentId or "0",
                limit=payload.pageSize,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "items": live_result.payload.get("items", []),
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "note": live_result.note,
                    "parentFileId": live_result.payload.get("parentFileId", "0"),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "items": provider_mock_list(provider_key, payload.path),
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "guangya":
            items = guangya_mock_list(payload.path)
        else:
            items = provider_mock_list(provider_key, payload.path)
        if not items:
            raise HTTPException(status_code=404, detail="provider_or_path_not_supported")
        return {
            "providerKey": provider_key,
            "path": payload.path,
            "items": items,
            "mode": "mock",
        }

    @app.post("/api/providers/{provider_key}/metadata")
    def provider_metadata(provider_key: str, payload: ProviderPathRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        if provider_key == "189cloud" and payload.preferLive and payload.profileId:
            live_result = fetch_tianyi_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.payload.get("entry", {}),
                    "note": live_result.note,
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "baidu_netdisk" and payload.preferLive and payload.profileId:
            live_result = fetch_baidu_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
                path=payload.path,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.payload.get("entry", {}),
                    "note": live_result.note,
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "115_open" and payload.preferLive and payload.profileId:
            live_result = fetch_115_open_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.payload.get("entry", {}),
                    "note": live_result.note,
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "quark" and payload.preferLive and payload.profileId:
            live_result = fetch_quark_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
                parent_id=payload.parentId or "0",
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.payload.get("entry", {}),
                    "note": live_result.note,
                    "parentId": live_result.payload.get("parentId", "0"),
                    "pwdId": live_result.payload.get("pwdId", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "pikpak" and payload.preferLive and payload.profileId:
            live_result = fetch_pikpak_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.payload.get("entry", {}),
                    "note": live_result.note,
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "uc" and payload.preferLive and payload.profileId:
            live_result = fetch_uc_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
                parent_id=payload.parentId or "0",
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.payload.get("entry", {}),
                    "note": live_result.note,
                    "parentId": live_result.payload.get("parentId", "0"),
                    "pwdId": live_result.payload.get("pwdId", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "xunlei" and payload.preferLive and payload.profileId:
            live_result = fetch_xunlei_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
                parent_id=payload.parentId,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.payload.get("entry", {}),
                    "note": live_result.note,
                    "parentId": live_result.payload.get("parentId", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "guangya" and payload.preferLive and payload.profileId:
            live_result = fetch_guangya_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.items[0] if live_result.items else {},
                    "note": live_result.note,
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "aliyundrive_open" and payload.preferLive and payload.profileId:
            live_result = fetch_aliyun_open_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.payload.get("entry", {}),
                    "note": live_result.note,
                    "domainId": live_result.payload.get("domainId", ""),
                    "driveId": live_result.payload.get("driveId", ""),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        if provider_key == "123_open" and payload.preferLive and payload.profileId:
            live_result = fetch_123_open_live_metadata(
                profile_id=payload.profileId,
                file_id=payload.fileId,
                parent_file_id=payload.parentId or "0",
            )
            if live_result.ok:
                return {
                    "providerKey": provider_key,
                    "path": payload.path,
                    "mode": "live",
                    "usedProfile": True,
                    "profileId": live_result.profileId,
                    "status": live_result.status,
                    "entry": live_result.payload.get("entry", {}),
                    "note": live_result.note,
                    "parentFileId": live_result.payload.get("parentFileId", "0"),
                }
            return {
                "providerKey": provider_key,
                "path": payload.path,
                "mode": "mock",
                "usedProfile": True,
                "profileId": payload.profileId,
                "entry": provider_mock_metadata(provider_key, payload.path).model_dump(),
                "fallbackReason": live_result.error,
                "note": live_result.note,
            }
        entry = provider_mock_metadata(provider_key, payload.path)
        return {
            "providerKey": provider_key,
            "path": payload.path,
            "mode": "mock",
            "entry": entry.model_dump(),
        }

    @app.get("/api/tasks")
    def tasks(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        items = list_tasks()
        return {"items": items, "listItems": [build_task_list_view(item) for item in items]}

    @app.post("/api/tasks")
    def task_create(payload: TaskCreateRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        item = create_task(payload)
        return {"item": item, "listView": build_task_list_view(item), "detailView": build_task_detail_view(item)}

    @app.get("/api/tasks/{task_id}")
    def task_get(task_id: str, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        task = get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="task_not_found")
        return {"item": task, "detailView": build_task_detail_view(task), "listView": build_task_list_view(task)}

    @app.post("/api/tasks/{task_id}/action")
    def task_action(task_id: str, payload: TaskActionRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        task = get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="task_not_found")
        action = payload.action.strip().lower()
        if action == "run":
            task = run_task(task_id)
        elif action == "acknowledge_risk":
            task = acknowledge_task_risk(task_id)
        elif action == "pause":
            task = pause_task(task_id)
        elif action == "resume":
            task = resume_task(task_id)
        elif action == "retry":
            task = retry_task(task_id)
        else:
            raise HTTPException(status_code=400, detail="unsupported_action")
        last_action_error = dict(task.get("lastActionError") or {})
        action_error = last_action_error if str(last_action_error.get("action") or "") == action else {}
        return {
            "item": task,
            "listView": build_task_list_view(task),
            "detailView": build_task_detail_view(task),
            "action": action,
            "actionApplied": not bool(action_error),
            "actionError": action_error,
            "allowedActions": ((task.get("summary") or {}).get("allowedActions") or []),
        }

    return app
