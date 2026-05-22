from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .auth import build_session_token, verify_session_token
from .config import ADMIN_PASSWORD, SESSION_COOKIE
from .i18n import MESSAGES, messages_for
from .models import SourceEntry
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

    return app
