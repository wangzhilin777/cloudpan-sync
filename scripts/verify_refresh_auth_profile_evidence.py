from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import webapp
from cloudpan_sync.auth_profile_patch import configure_data_dir
from fastapi.testclient import TestClient


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "gy-refresh-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "gy-refresh",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {"parentId": "dir-100", "fileId": "file-9"},
                        "status": "saved",
                        "lastError": "",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    }
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        configure_data_dir(data_dir)

        original_refresh = webapp.refresh_auth_profile_evidence
        original_password = webapp.ADMIN_PASSWORD

        def fake_refresh_auth_profile_evidence(*, profile: object, page_size: int = 100, dir_name: str = "", persist: bool = True, profile_view_builder=None):
            profile_view = profile_view_builder(profile) if callable(profile_view_builder) else {
                "profileId": getattr(profile, "profileId", ""),
                "providerKey": getattr(profile, "providerKey", ""),
            }
            return {
                "profile": profile_view,
                "latestValidation": {"ok": True, "summary": "validation ok", "status": 200},
                "latestProbe": {"ok": True, "summary": "probe ok", "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}]},
                "summary": {
                    "profileReady": True,
                    "validationOk": True,
                    "probeOk": True,
                    "resolvedParentId": str(profile_view.get("resolvedParentId") or ""),
                    "resolvedFileId": str(profile_view.get("resolvedFileId") or ""),
                },
                "requestEcho": {"pageSize": page_size, "dirName": dir_name, "persist": persist},
            }

        webapp.refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            payload = client.post(
                "/api/auth/profiles/gy-refresh-1/refresh_evidence",
                json={"pageSize": 55, "dirName": "verify-dir"},
            ).json()
        finally:
            webapp.refresh_auth_profile_evidence = original_refresh
            webapp.ADMIN_PASSWORD = original_password

        print(
            json.dumps(
                {
                    "validationOk": ((payload.get("evidence") or {}).get("summary") or {}).get("validationOk"),
                    "probeOk": ((payload.get("evidence") or {}).get("summary") or {}).get("probeOk"),
                    "markdownHasTitle": "# Auth Profile Evidence" in str(payload.get("markdown", "")),
                    "markdownHasProfileId": "`gy-refresh-1`" in str(payload.get("markdown", "")),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
