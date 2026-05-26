from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import webapp
from cloudpan_sync.auth_profile_view import auth_profile_view
from cloudpan_sync.auth_store import masked_profile
from cloudpan_sync.models import AuthProfile


@contextmanager
def patched_attr(target: object, name: str, value: object):
    original = getattr(target, name)
    setattr(target, name, value)
    try:
        yield
    finally:
        setattr(target, name, original)


def main() -> None:
    guangya_profile = AuthProfile(
        profileId="gy-mask-1",
        providerKey="guangya",
        authMode="manual_token",
        displayName="gy-mask",
        token="abcd1234ef",
        cookie="cookie-123456789",
        extra={"parentFileId": "dir-alias", "file_id": "file-alias"},
        status="saved",
        lastError="",
        createdAt="2026-05-26T00:00:00+00:00",
        updatedAt="2026-05-26T00:00:00+00:00",
    )
    short_token_profile = AuthProfile(
        profileId="gy-mask-2",
        providerKey="guangya",
        authMode="manual_token",
        displayName="gy-short",
        token="short",
        cookie="tiny",
        extra={"parentId": "dir-2"},
        status="saved",
        lastError="",
        createdAt="2026-05-26T00:00:00+00:00",
        updatedAt="2026-05-26T00:00:00+00:00",
    )
    placeholder_profile = AuthProfile(
        profileId="ali-mask-1",
        providerKey="aliyundrive_open",
        authMode="official_oauth",
        displayName="aliyun-demo",
        token="tok-demo",
        cookie="",
        extra={"domainId": "domain-demo", "driveId": "drive-demo"},
        status="saved",
        lastError="",
        createdAt="2026-05-26T00:00:00+00:00",
        updatedAt="2026-05-26T00:00:00+00:00",
    )

    masked_long = masked_profile(guangya_profile)
    masked_short = masked_profile(short_token_profile)
    placeholder_view = auth_profile_view(placeholder_profile)

    with patched_attr(webapp, "ADMIN_PASSWORD", "admin123"):
        with patched_attr(webapp, "list_profiles", lambda: [guangya_profile, placeholder_profile]):
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            payload = client.get("/api/auth/profiles").json()

    items = list(payload.get("items") or [])
    by_id = {str(item.get("profileId") or ""): dict(item) for item in items}
    guangya_item = by_id.get("gy-mask-1", {})
    placeholder_item = by_id.get("ali-mask-1", {})

    print(
        json.dumps(
            {
                "maskedLongTokenKeepsPrefixAndSuffix": masked_long.get("token") == "abcd***ef",
                "maskedLongCookieKeepsPrefix": masked_long.get("cookie") == "cookie***",
                "shortSecretsCollapseToStars": masked_short.get("token") == "***" and masked_short.get("cookie") == "***",
                "apiListMasksSecrets": (
                    guangya_item.get("token") == "abcd***ef"
                    and guangya_item.get("cookie") == "cookie***"
                    and guangya_item.get("token") != guangya_profile.token
                    and guangya_item.get("cookie") != guangya_profile.cookie
                ),
                "apiListKeepsResolvedDefaults": (
                    guangya_item.get("resolvedParentId") == "dir-alias"
                    and guangya_item.get("resolvedFileId") == "file-alias"
                    and guangya_item.get("profileReady") is True
                ),
                "placeholderProfileSignalsSecretRefresh": (
                    placeholder_view.get("profileReady") is False
                    and placeholder_view.get("needsSecretRefresh") is True
                    and "token" in list(placeholder_view.get("placeholderSecretFieldHints") or [])
                    and bool(placeholder_view.get("placeholderFieldHints"))
                ),
                "apiListReturnsPlaceholderHints": (
                    placeholder_item.get("needsSecretRefresh") is True
                    and "token" in list(placeholder_item.get("placeholderSecretFieldHints") or [])
                    and bool(placeholder_item.get("placeholderFieldHints"))
                ),
                "authProfileMaskingFlowMatchesExpectedViews": (
                    masked_long.get("token") == "abcd***ef"
                    and masked_long.get("cookie") == "cookie***"
                    and masked_short.get("token") == "***"
                    and masked_short.get("cookie") == "***"
                    and guangya_item.get("token") == "abcd***ef"
                    and guangya_item.get("cookie") == "cookie***"
                    and guangya_item.get("token") != guangya_profile.token
                    and guangya_item.get("cookie") != guangya_profile.cookie
                    and guangya_item.get("resolvedParentId") == "dir-alias"
                    and guangya_item.get("resolvedFileId") == "file-alias"
                    and guangya_item.get("profileReady") is True
                    and placeholder_view.get("profileReady") is False
                    and placeholder_view.get("needsSecretRefresh") is True
                    and "token" in list(placeholder_view.get("placeholderSecretFieldHints") or [])
                    and bool(placeholder_view.get("placeholderFieldHints"))
                    and placeholder_item.get("needsSecretRefresh") is True
                    and "token" in list(placeholder_item.get("placeholderSecretFieldHints") or [])
                    and bool(placeholder_item.get("placeholderFieldHints"))
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
