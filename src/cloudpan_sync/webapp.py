from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .auth_store import (
    delete_profile,
    get_profile,
    list_profiles,
    masked_profile,
    save_profile,
    update_profile,
)
from .auth_live_validate import list_live_validations, run_profile_live_validation
from .auth import build_session_token, verify_session_token
from .config import ADMIN_PASSWORD, SESSION_COOKIE
from .i18n import MESSAGES, messages_for
from .models import AuthLiveValidateRequest, AuthProfileInput, SourceEntry
from .models import TaskActionRequest, TaskCreateRequest
from .guangya import guangya_fast_check, guangya_mock_list
from .planner import build_transfer_plan
from .provider_mock import provider_mock_list, provider_mock_metadata
from .provider_research import build_provider_research_index
from .provider_registry import build_provider_registry
from .plan_audit import run_plan_audit, to_markdown
from .live_probe import run_live_probe, probe_to_markdown
from .task_runtime import create_task, get_task, list_tasks, pause_task, resume_task, retry_task, run_task


WEB_DIR = Path(__file__).parent / "web"


class LoginRequest(BaseModel):
    password: str


class MockPlanRequest(BaseModel):
    sourceProvider: str
    targetProvider: str
    thresholdMB: int = 0
    selectedRoots: list[str] = []
    entries: list[SourceEntry]


class CaptureStartRequest(BaseModel):
    providerKey: str


class GuangyaListRequest(BaseModel):
    path: str = "/"


class GuangyaFastCheckRequest(BaseModel):
    entries: list[SourceEntry]


class ProviderPathRequest(BaseModel):
    path: str = "/"


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

    @app.get("/api/auth/profiles")
    def auth_profiles(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return {"items": [masked_profile(p) for p in list_profiles()]}

    @app.post("/api/auth/profiles")
    def auth_profile_create(payload: AuthProfileInput, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        profile = save_profile(payload)
        return {"item": masked_profile(profile)}

    @app.delete("/api/auth/profiles/{profile_id}")
    def auth_profile_delete(profile_id: str, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        ok = delete_profile(profile_id)
        if not ok:
            raise HTTPException(status_code=404, detail="profile_not_found")
        return {"ok": True}

    @app.post("/api/auth/capture/start")
    def auth_capture_start(payload: CaptureStartRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        # M3 keeps capture flow as guided placeholder. Real browser capture will be added in later milestone.
        return {
            "providerKey": payload.providerKey,
            "status": "capture_pending",
            "loginUrlHint": f"https://{payload.providerKey}.example.com/login",
            "message": "Open provider login page and paste token/cookie from session into auth form.",
        }

    @app.post("/api/auth/profiles/{profile_id}/validate")
    def auth_profile_validate(profile_id: str, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        profile = get_profile(profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="profile_not_found")
        if profile.token or profile.cookie:
            profile.status = "verified"
            profile.lastError = ""
        else:
            profile.status = "invalid"
            profile.lastError = "missing_token_or_cookie"
        profile.updatedAt = datetime.now(timezone.utc).isoformat()
        update_profile(profile)
        return {"item": masked_profile(profile)}

    @app.get("/api/auth/live_validations")
    def auth_live_validations(request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return {"items": list_live_validations()}

    @app.post("/api/auth/live_validate")
    def auth_live_validate(payload: AuthLiveValidateRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        row = run_profile_live_validation(payload.profileId)
        return {"item": row}

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
            selected_roots=payload.selectedRoots,
        )
        return plan.model_dump()

    @app.post("/api/providers/guangya/list")
    def guangya_list(payload: GuangyaListRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return {
            "providerKey": "guangya",
            "path": payload.path,
            "items": guangya_mock_list(payload.path),
            "mode": "mock",
            "note": "This is a local mock list in M4. Real Guangya listing will be wired in later milestones.",
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

    @app.post("/api/providers/{provider_key}/list")
    def provider_list(provider_key: str, payload: ProviderPathRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
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
        return {"items": list_tasks()}

    @app.post("/api/tasks")
    def task_create(payload: TaskCreateRequest, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        return {"item": create_task(payload)}

    @app.get("/api/tasks/{task_id}")
    def task_get(task_id: str, request: Request) -> dict[str, object]:
        if not _is_logged_in(request):
            raise HTTPException(status_code=401, detail="please_login_first")
        task = get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="task_not_found")
        return {"item": task}

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
        elif action == "pause":
            task = pause_task(task_id)
        elif action == "resume":
            task = resume_task(task_id)
        elif action == "retry":
            task = retry_task(task_id)
        else:
            raise HTTPException(status_code=400, detail="unsupported_action")
        return {"item": task}

    return app
