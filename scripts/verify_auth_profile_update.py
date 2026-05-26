from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import webapp
from cloudpan_sync.auth_store import build_updated_profile
from cloudpan_sync.models import AuthProfile
from fastapi.testclient import TestClient


@contextmanager
def patched_attr(target: object, name: str, value: object):
    original = getattr(target, name)
    setattr(target, name, value)
    try:
        yield
    finally:
        setattr(target, name, original)


def main() -> None:
    existing = AuthProfile(
        profileId="gy-edit-1",
        providerKey="guangya",
        authMode="manual_token",
        displayName="gy-old",
        token="tok-original",
        cookie="",
        extra={},
        status="invalid",
        lastError="missing_parent_id",
        createdAt="2026-05-23T00:00:00+00:00",
        updatedAt="2026-05-23T00:00:00+00:00",
    )
    saved = {"profile": None}

    def fake_get_profile(profile_id: str):
        return existing if profile_id == existing.profileId else None

    def fake_update_profile(profile: AuthProfile):
        saved["profile"] = profile

    def fake_validate_profile_object(profile: AuthProfile):
        return {
            "ok": True,
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "providerDisplayName": profile.displayName,
            "mode": "live",
            "status": 200,
            "error": "",
            "summary": "updated validation ok",
            "checkedAt": "2026-05-23T00:00:00+00:00",
            "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}],
            "parentId": profile.extra.get("parentId", ""),
            "fileId": profile.extra.get("fileId", ""),
            "riskHint": "",
            "requiredFieldHints": [],
        }

    def fake_auth_profile_view(profile: AuthProfile):
        return {
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "authMode": profile.authMode,
            "displayName": profile.displayName,
            "token": "tok-***",
            "cookie": "",
            "extra": dict(profile.extra),
            "status": profile.status,
            "lastError": profile.lastError,
            "resolvedParentId": profile.extra.get("parentId", ""),
            "resolvedFileId": profile.extra.get("fileId", ""),
            "missingFieldHints": [],
            "profileReady": True,
        }

    with patched_attr(webapp, "ADMIN_PASSWORD", "admin123"):
        with patched_attr(webapp, "get_profile", fake_get_profile):
            with patched_attr(webapp, "build_updated_profile", build_updated_profile):
                with patched_attr(webapp, "update_profile", fake_update_profile):
                    with patched_attr(webapp, "validate_profile_object", fake_validate_profile_object):
                        with patched_attr(webapp, "append_live_validation", lambda row: row):
                            with patched_attr(webapp, "_auth_profile_view", fake_auth_profile_view):
                                app = webapp.create_app()
                                client = TestClient(app)
                                client.post("/api/login", json={"password": "admin123"})
                                response = client.put(
                                    f"/api/auth/profiles/{existing.profileId}",
                                    json={
                                        "providerKey": "guangya",
                                        "authMode": "manual_token",
                                        "displayName": "gy-updated",
                                        "token": "",
                                        "cookie": "",
                                        "extra": {"parentId": "dir-100"},
                                    },
                                ).json()

    updated = saved["profile"]
    print(
        json.dumps(
            {
                "savedProfile": {
                    "displayName": getattr(updated, "displayName", ""),
                    "tokenPreserved": getattr(updated, "token", "") == "tok-original",
                    "parentId": (getattr(updated, "extra", {}) or {}).get("parentId", ""),
                    "status": getattr(updated, "status", ""),
                },
                "response": {
                    "profileReady": (response.get("item") or {}).get("profileReady"),
                    "resolvedParentId": (response.get("item") or {}).get("resolvedParentId"),
                    "validationOk": (response.get("validation") or {}).get("ok"),
                },
                "authProfileUpdateFlowMatchesExpectedPersistence": (
                    getattr(updated, "displayName", "") == "gy-updated"
                    and getattr(updated, "token", "") == "tok-original"
                    and (getattr(updated, "extra", {}) or {}).get("parentId", "") == "dir-100"
                    and getattr(updated, "status", "") == "verified"
                    and (response.get("item") or {}).get("profileReady") is True
                    and (response.get("item") or {}).get("resolvedParentId") == "dir-100"
                    and (response.get("validation") or {}).get("ok") is True
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
