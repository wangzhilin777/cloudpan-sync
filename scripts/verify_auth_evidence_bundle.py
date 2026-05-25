from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_live_validate import append_live_validation
from cloudpan_sync.auth_profile_evidence import auth_evidence_bundle_to_markdown, build_auth_evidence_bundle
from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_store import list_profiles
from cloudpan_sync.provider_live_probe_store import save_provider_live_probe
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
                        "profileId": "gy-bundle-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "gy-ok",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {"parentId": "dir-100", "fileId": "file-9"},
                        "status": "verified",
                        "lastError": "",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                    {
                        "profileId": "gy-bundle-2",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "gy-missing",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {},
                        "status": "invalid",
                        "lastError": "missing_parent_id",
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
        append_live_validation(
            {
                "ok": True,
                "profileId": "gy-bundle-1",
                "providerKey": "guangya",
                "providerDisplayName": "gy-ok",
                "mode": "live",
                "status": 200,
                "error": "",
                "summary": "validation ok",
                "checkedAt": "2026-05-23T00:00:00+00:00",
                "checks": [],
                "parentId": "dir-100",
                "fileId": "file-9",
                "riskHint": "",
                "requiredFieldHints": [],
            }
        )
        append_live_validation(
            {
                "ok": False,
                "profileId": "gy-bundle-2",
                "providerKey": "guangya",
                "providerDisplayName": "gy-missing",
                "mode": "profile_incomplete",
                "status": 0,
                "error": "missing_parent_id",
                "summary": "validation missing parent",
                "checkedAt": "2026-05-23T00:00:00+00:00",
                "checks": [],
                "parentId": "",
                "fileId": "",
                "riskHint": "need parent",
                "requiredFieldHints": ["extra.parentId"],
            }
        )
        save_provider_live_probe(
            {
                "ok": True,
                "profileId": "gy-bundle-1",
                "providerKey": "guangya",
                "mode": "live",
                "summary": "probe ok",
                "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}],
            }
        )
        save_provider_live_probe(
            {
                "ok": False,
                "profileId": "gy-bundle-2",
                "providerKey": "guangya",
                "mode": "profile_incomplete",
                "summary": "probe missing parent",
                "checks": [{"kind": "list", "ok": False, "status": 0, "error": "missing_parent_id", "note": "need parent"}],
            }
        )

        bundle = build_auth_evidence_bundle(profiles=list_profiles(), profile_view_builder=_auth_profile_view)
        markdown = auth_evidence_bundle_to_markdown(bundle)

        original_password = webapp.ADMIN_PASSWORD
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            api_bundle = client.get("/api/auth/evidence_bundle").json()
            api_markdown = client.get("/api/auth/evidence_bundle_markdown").json()
        finally:
            webapp.ADMIN_PASSWORD = original_password

        print(
            json.dumps(
                {
                    "summary": bundle.get("summary", {}),
                    "apiProfileCount": ((api_bundle.get("summary") or {}).get("profileCount")),
                    "apiProfileSummaryReadyProfiles": (api_bundle.get("summary") or {}).get("profileReadyProfiles"),
                    "apiProfileSummaryWriteReadyProfiles": (api_bundle.get("summary") or {}).get("writeReadyProfiles"),
                    "apiProfileSummaryValidationOkProfiles": (api_bundle.get("summary") or {}).get("validationOkProfiles"),
                    "apiProfileSummaryProbeOkProfiles": (api_bundle.get("summary") or {}).get("probeOkProfiles"),
                    "apiMarkdownHasTitle": "# Auth Evidence Bundle" in str(api_markdown.get("markdown", "")),
                    "apiMarkdownHasProfileSummary": "profileSummary:" in str(api_markdown.get("markdown", "")) and "`writeReady=gy-missing, gy-ok`" in str(api_markdown.get("markdown", "")),
                    "markdownHasMissingProfile": "gy-missing" in markdown,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
