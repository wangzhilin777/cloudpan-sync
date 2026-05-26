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
from cloudpan_sync import auth_profile_view as auth_profile_view_module
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
            profileId="gy-alias-1",
            providerKey="guangya",
            authMode="manual_token",
            displayName="gy-alias",
            token="tok-demo",
            cookie="",
            extra={"parentFileId": "parent-alias", "file_id": "file-alias"},
            status="saved",
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
            "token": "tok-***",
            "cookie": "",
            "extra": dict(profile.extra),
            "status": profile.status,
            "lastError": profile.lastError,
            "createdAt": profile.createdAt,
            "updatedAt": profile.updatedAt,
        }

    with patched_attr(webapp, "ADMIN_PASSWORD", "admin123"):
        with patched_attr(webapp, "list_profiles", lambda: profiles):
            with patched_attr(auth_profile_view_module, "masked_profile", fake_masked_profile):
                app = webapp.create_app()
                client = TestClient(app)
                client.post("/api/login", json={"password": "admin123"})
                payload = client.get("/api/auth/profiles").json()

    item = (payload.get("items") or [])[0]
    auth_profile_resolved_defaults_flow_matches_expected_aliases = (
        item.get("profileId") == "gy-alias-1"
        and item.get("resolvedParentId") == "parent-alias"
        and item.get("resolvedFileId") == "file-alias"
        and item.get("profileReady") is False
        and item.get("missingFieldHints") == [
            "token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token"
        ]
    )
    print(
        json.dumps(
            {
                "profileId": item.get("profileId"),
                "resolvedParentId": item.get("resolvedParentId"),
                "resolvedFileId": item.get("resolvedFileId"),
                "profileReady": item.get("profileReady"),
                "missingFieldHints": item.get("missingFieldHints"),
                "authProfileResolvedDefaultsFlowMatchesExpectedAliases": auth_profile_resolved_defaults_flow_matches_expected_aliases,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
