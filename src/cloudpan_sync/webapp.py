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
from .auth import build_session_token, verify_session_token
from .config import ADMIN_PASSWORD, SESSION_COOKIE
from .i18n import MESSAGES, messages_for
from .models import AuthProfileInput, SourceEntry
from .guangya import guangya_fast_check, guangya_mock_list
from .planner import build_transfer_plan
from .provider_registry import build_provider_registry


WEB_DIR = Path(__file__).parent / "web"


class LoginRequest(BaseModel):
    password: str


class MockPlanRequest(BaseModel):
    sourceProvider: str
    targetProvider: str
    thresholdMB: int = 0
    entries: list[SourceEntry]


class CaptureStartRequest(BaseModel):
    providerKey: str


class GuangyaListRequest(BaseModel):
    path: str = "/"


class GuangyaFastCheckRequest(BaseModel):
    entries: list[SourceEntry]


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

    return app
