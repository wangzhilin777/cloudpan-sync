from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_profile_remediation import auth_remediation_bundle_to_markdown, build_auth_remediation_bundle
from cloudpan_sync.auth_store import list_profiles
from cloudpan_sync import webapp
from cloudpan_sync.webapp import _auth_profile_view
from fastapi.testclient import TestClient


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "gy-rem-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "smoke-guangya",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {},
                        "status": "invalid",
                        "lastError": "missing_parent_id",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                    {
                        "profileId": "ali-rem-1",
                        "providerKey": "aliyundrive_open",
                        "authMode": "manual_token",
                        "displayName": "ali-ready",
                        "token": "tok_ali",
                        "cookie": "",
                        "extra": {"domainId": "d-1", "driveId": "drive-1"},
                        "status": "verified",
                        "lastError": "",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                    {
                        "profileId": "189-rem-1",
                        "providerKey": "189cloud",
                        "authMode": "manual_cookie",
                        "displayName": "189-readonly-share",
                        "token": "",
                        "cookie": "",
                        "extra": {"shareCode": "share-demo"},
                        "status": "verified",
                        "lastError": "",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        configure_data_dir(data_dir)
        bundle = build_auth_remediation_bundle(profile_views=[_auth_profile_view(profile) for profile in list_profiles()])
        markdown = auth_remediation_bundle_to_markdown(bundle)

        original_password = webapp.ADMIN_PASSWORD
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            api_bundle = client.get("/api/auth/remediation_bundle").json()
            api_markdown = client.get("/api/auth/remediation_bundle_markdown").json()
        finally:
            webapp.ADMIN_PASSWORD = original_password

        print(
            json.dumps(
                {
                    "profileCount": ((bundle.get("summary") or {}).get("profileCount")),
                    "needsFixCount": ((bundle.get("summary") or {}).get("needsFixCount")),
                    "writeNeedsFixCount": ((bundle.get("summary") or {}).get("writeNeedsFixCount")),
                    "markdownHasCommand": "patch_auth_profile_extra.py" in markdown,
                    "markdownHasWriteBlocker": "writeBlockerNote" in markdown,
                    "apiReadyCount": ((api_bundle.get("summary") or {}).get("readyCount")),
                    "apiWriteReadyCount": ((api_bundle.get("summary") or {}).get("writeReadyCount")),
                    "apiMarkdownHasTitle": "# 授权补救指南 / Auth Remediation Guide" in str(api_markdown.get("markdown", "")),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
