from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import webapp
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
    profiles = [
        SimpleNamespace(
            profileId="gy-1",
            providerKey="guangya",
            authMode="manual_token",
            displayName="gy-smoke",
            token="tok-demo",
            cookie="",
            extra={},
            status="invalid",
            lastError="missing_parent_id",
            createdAt="2026-05-23T00:00:00+00:00",
            updatedAt="2026-05-23T00:00:00+00:00",
            model_dump=lambda: {},
        ),
        SimpleNamespace(
            profileId="ali-1",
            providerKey="aliyundrive_open",
            authMode="official_oauth",
            displayName="ali-ready",
            token="ali-token",
            cookie="",
            extra={"domainId": "domain-1", "driveId": "drive-1"},
            status="verified",
            lastError="",
            createdAt="2026-05-23T00:00:00+00:00",
            updatedAt="2026-05-23T00:00:00+00:00",
            model_dump=lambda: {},
        ),
    ]

    def fake_masked_profile(profile: object):
        return {
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "authMode": profile.authMode,
            "displayName": profile.displayName,
            "token": profile.token[:4] + "***" if profile.token else "",
            "cookie": "",
            "extra": dict(profile.extra),
            "status": profile.status,
            "lastError": profile.lastError,
            "createdAt": profile.createdAt,
            "updatedAt": profile.updatedAt,
        }

    with patched_attr(webapp, "ADMIN_PASSWORD", "admin123"):
        with patched_attr(webapp, "list_profiles", lambda: profiles):
            with patched_attr(webapp, "masked_profile", fake_masked_profile):
                app = webapp.create_app()
                client = TestClient(app)
                client.post("/api/login", json={"password": "admin123"})
                payload = client.get("/api/auth/profiles").json()

    items = payload.get("items") or []
    gy = next(item for item in items if item.get("providerKey") == "guangya")
    ali = next(item for item in items if item.get("providerKey") == "aliyundrive_open")

    print(
        json.dumps(
            {
                "guangya": {
                    "profileReady": gy.get("profileReady"),
                    "missingFieldHints": gy.get("missingFieldHints"),
                },
                "aliyundrive_open": {
                    "profileReady": ali.get("profileReady"),
                    "missingFieldHints": ali.get("missingFieldHints"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
