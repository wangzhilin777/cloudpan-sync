from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_view import auth_profile_view


def main() -> None:
    def _dump(profile_id: str, provider_key: str, auth_mode: str, display_name: str, token: str, cookie: str, extra: dict[str, str], status: str, last_error: str) -> dict[str, object]:
        return {
            "profileId": profile_id,
            "providerKey": provider_key,
            "authMode": auth_mode,
            "displayName": display_name,
            "token": token,
            "cookie": cookie,
            "extra": extra,
            "status": status,
            "lastError": last_error,
            "createdAt": "2026-05-23T00:00:00+00:00",
            "updatedAt": "2026-05-23T00:00:00+00:00",
        }

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
            model_dump=lambda: _dump("gy-1", "guangya", "manual_token", "gy-smoke", "tok-demo", "", {}, "invalid", "missing_parent_id"),
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
            model_dump=lambda: _dump("ali-1", "aliyundrive_open", "official_oauth", "ali-ready", "ali-token", "", {"domainId": "domain-1", "driveId": "drive-1"}, "verified", ""),
        ),
        SimpleNamespace(
            profileId="ali-placeholder",
            providerKey="aliyundrive_open",
            authMode="official_oauth",
            displayName="ali-placeholder",
            token="tok-demo",
            cookie="",
            extra={"domainId": "domain-demo", "driveId": "drive-demo"},
            status="invalid",
            lastError="http_error:404",
            createdAt="2026-05-23T00:00:00+00:00",
            updatedAt="2026-05-23T00:00:00+00:00",
            model_dump=lambda: _dump("ali-placeholder", "aliyundrive_open", "official_oauth", "ali-placeholder", "tok-demo", "", {"domainId": "domain-demo", "driveId": "drive-demo"}, "invalid", "http_error:404"),
        ),
    ]

    rows = [auth_profile_view(profile) for profile in profiles]
    gy = next(item for item in rows if item.get("profileId") == "gy-1")
    ali = next(item for item in rows if item.get("profileId") == "ali-1")
    ali_placeholder = next(item for item in rows if item.get("profileId") == "ali-placeholder")

    print(
        json.dumps(
            {
                "guangyaPlaceholderBlocksReadiness": gy.get("profileReady") is False
                and "extra.parentId (aliases: parent_id/parentFileId/dirId/pid)" in (gy.get("missingFieldHints") or [])
                and "token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token" in (gy.get("placeholderFieldHints") or []),
                "aliyunRealFieldsStayReady": ali.get("profileReady") is True
                and not (ali.get("placeholderFieldHints") or [])
                and ali.get("resolvedParentId") == "root",
                "aliyunPlaceholderFieldsBlockReadiness": ali_placeholder.get("profileReady") is False
                and "token looks like placeholder data; replace tok-demo with a real Aliyun OAuth token" in (ali_placeholder.get("placeholderFieldHints") or [])
                and "extra.domainId still uses placeholder data; replace domain-demo with a real domainId" in (ali_placeholder.get("placeholderFieldHints") or [])
                and "extra.driveId still uses placeholder data; replace drive-demo with a real driveId" in (ali_placeholder.get("placeholderFieldHints") or []),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
