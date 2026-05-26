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

        evidence = payload.get("evidence") or {}
        summary = evidence.get("summary") or {}
        request_echo = evidence.get("requestEcho") or {}
        markdown = str(payload.get("markdown", ""))
        auth_profile_evidence_refresh_flow_matches_expected_profile = (
            summary.get("profileReady") is True
            and summary.get("validationOk") is True
            and summary.get("probeOk") is True
            and summary.get("resolvedParentId") == "dir-100"
            and summary.get("resolvedFileId") == "file-9"
            and request_echo.get("pageSize") == 55
            and request_echo.get("dirName") == "verify-dir"
            and request_echo.get("persist") is True
            and "# Auth Profile Evidence" in markdown
            and "`gy-refresh-1`" in markdown
        )

        print(
            json.dumps(
                {
                    "validationOk": summary.get("validationOk"),
                    "probeOk": summary.get("probeOk"),
                    "profileReady": summary.get("profileReady"),
                    "markdownHasTitle": "# Auth Profile Evidence" in markdown,
                    "markdownHasProfileId": "`gy-refresh-1`" in markdown,
                    "authProfileEvidenceRefreshFlowMatchesExpectedProfile": auth_profile_evidence_refresh_flow_matches_expected_profile,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
