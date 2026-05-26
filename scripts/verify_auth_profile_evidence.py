from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.provider_live_probe_store import save_provider_live_probe
from cloudpan_sync.auth_live_validate import append_live_validation
from fastapi.testclient import TestClient
from cloudpan_sync import webapp
from cloudpan_sync.auth_profile_evidence import auth_profile_evidence_to_markdown
from cloudpan_sync.webapp import _auth_profile_evidence
from cloudpan_sync.auth_store import get_profile

def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "gy-evidence-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "gy-evidence",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {"parentId": "dir-100", "fileId": "file-9"},
                        "status": "verified",
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
        append_live_validation(
            {
                "ok": True,
                "profileId": "gy-evidence-1",
                "providerKey": "guangya",
                "providerDisplayName": "gy-evidence",
                "mode": "live",
                "status": 200,
                "error": "",
                "summary": "validation ok",
                "checkedAt": "2026-05-23T00:00:00+00:00",
                "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}],
                "parentId": "dir-100",
                "fileId": "file-9",
                "riskHint": "",
                "requiredFieldHints": [],
            }
        )
        save_provider_live_probe(
            {
                "ok": True,
                "profileId": "gy-evidence-1",
                "providerKey": "guangya",
                "mode": "live",
                "summary": "probe ok",
                "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}],
            }
        )

        profile = get_profile("gy-evidence-1")
        evidence = _auth_profile_evidence(profile)
        markdown = auth_profile_evidence_to_markdown(evidence)

        original_password = webapp.ADMIN_PASSWORD
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            api_payload = client.get("/api/auth/profiles/gy-evidence-1/evidence").json()
            markdown_payload = client.get("/api/auth/profiles/gy-evidence-1/evidence_markdown").json()
        finally:
            webapp.ADMIN_PASSWORD = original_password

        summary = evidence.get("summary", {})
        api_markdown = str(markdown_payload.get("markdown", ""))
        auth_profile_evidence_flow_matches_expected_profile = (
            summary.get("profileReady") is False
            and summary.get("writeReady") is True
            and summary.get("validationOk") is True
            and summary.get("probeOk") is True
            and summary.get("resolvedParentId") == "dir-100"
            and summary.get("resolvedFileId") == "file-9"
            and (api_payload.get("latestValidation") or {}).get("ok") is True
            and (api_payload.get("latestProbe") or {}).get("ok") is True
            and "`gy-evidence-1`" in markdown
            and "probe ok" in markdown
            and "`gy-evidence-1`" in api_markdown
        )

        print(
            json.dumps(
                {
                    "summary": summary,
                    "apiValidationOk": (api_payload.get("latestValidation") or {}).get("ok"),
                    "apiProbeOk": (api_payload.get("latestProbe") or {}).get("ok"),
                    "markdownHasProfileId": "`gy-evidence-1`" in markdown,
                    "markdownHasProbeSummary": "probe ok" in markdown,
                    "apiMarkdownHasProfileId": "`gy-evidence-1`" in api_markdown,
                    "authProfileEvidenceFlowMatchesExpectedProfile": auth_profile_evidence_flow_matches_expected_profile,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
