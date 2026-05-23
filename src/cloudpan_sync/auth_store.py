from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import AuthProfile, AuthProfileInput


DATA_DIR = Path(".cloudpan_sync_data")
AUTH_FILE = DATA_DIR / "auth_profiles.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_rows() -> list[dict]:
    _ensure_data_dir()
    if not AUTH_FILE.exists():
        return []
    text = AUTH_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        rows = json.loads(text)
    except json.JSONDecodeError:
        return []
    return rows if isinstance(rows, list) else []


def _write_rows(rows: list[dict]) -> None:
    _ensure_data_dir()
    AUTH_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def list_profiles() -> list[AuthProfile]:
    return [AuthProfile.model_validate(row) for row in _read_rows()]


def build_profile(payload: AuthProfileInput) -> AuthProfile:
    now = _now_iso()
    return AuthProfile(
        profileId=str(uuid4()),
        providerKey=payload.providerKey,
        authMode=payload.authMode,
        displayName=payload.displayName,
        token=payload.token.strip(),
        cookie=payload.cookie.strip(),
        extra={k: str(v) for k, v in payload.extra.items()},
        status="saved",
        lastError="",
        createdAt=now,
        updatedAt=now,
    )


def build_updated_profile(existing: AuthProfile, payload: AuthProfileInput) -> AuthProfile:
    now = _now_iso()
    merged_extra = dict(existing.extra or {})
    for key, value in payload.extra.items():
        text = str(value or "").strip()
        if text:
            merged_extra[key] = text
    token = payload.token.strip() or existing.token
    cookie = payload.cookie.strip() or existing.cookie
    return AuthProfile(
        profileId=existing.profileId,
        providerKey=payload.providerKey,
        authMode=payload.authMode,
        displayName=payload.displayName,
        token=token,
        cookie=cookie,
        extra=merged_extra,
        status=existing.status,
        lastError=existing.lastError,
        createdAt=existing.createdAt,
        updatedAt=now,
    )


def save_profile(payload: AuthProfileInput) -> AuthProfile:
    rows = _read_rows()
    profile = build_profile(payload)
    rows.append(profile.model_dump())
    _write_rows(rows)
    return profile


def update_profile(profile: AuthProfile) -> None:
    rows = _read_rows()
    for i, row in enumerate(rows):
        if row.get("profileId") == profile.profileId:
            rows[i] = profile.model_dump()
            _write_rows(rows)
            return
    rows.append(profile.model_dump())
    _write_rows(rows)


def delete_profile(profile_id: str) -> bool:
    rows = _read_rows()
    kept = [row for row in rows if row.get("profileId") != profile_id]
    if len(kept) == len(rows):
        return False
    _write_rows(kept)
    return True


def get_profile(profile_id: str) -> AuthProfile | None:
    for profile in list_profiles():
        if profile.profileId == profile_id:
            return profile
    return None


def masked_profile(profile: AuthProfile) -> dict[str, object]:
    token_masked = ""
    cookie_masked = ""
    if profile.token:
        token_masked = f"{profile.token[:4]}***{profile.token[-2:]}" if len(profile.token) > 6 else "***"
    if profile.cookie:
        cookie_masked = f"{profile.cookie[:6]}***" if len(profile.cookie) > 8 else "***"
    data = profile.model_dump()
    data["token"] = token_masked
    data["cookie"] = cookie_masked
    return data
