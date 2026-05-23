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
from cloudpan_sync.auth_store import get_profile
from cloudpan_sync.auth_profile_evidence import auth_profile_evidence_to_markdown
from cloudpan_sync.webapp import _auth_profile_evidence, _auth_profile_view
from cloudpan_sync import webapp
from fastapi.testclient import TestClient


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "189-write-1",
                        "providerKey": "189cloud",
                        "authMode": "manual_cookie",
                        "displayName": "189-readonly-share",
                        "token": "",
                        "cookie": "",
                        "extra": {"shareCode": "share-demo", "fileId": "root-file"},
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
        profile = get_profile("189-write-1")
        profile_view = _auth_profile_view(profile)
        evidence = _auth_profile_evidence(profile)
        markdown = auth_profile_evidence_to_markdown(evidence)

        original_password = webapp.ADMIN_PASSWORD
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            list_payload = client.get("/api/auth/profiles").json()
            evidence_payload = client.get("/api/auth/profiles/189-write-1/evidence").json()
        finally:
            webapp.ADMIN_PASSWORD = original_password

        api_row = next((item for item in (list_payload.get("items") or []) if item.get("profileId") == "189-write-1"), {})
        print(
            json.dumps(
                {
                    "profileReady": profile_view.get("profileReady"),
                    "writeReady": profile_view.get("writeReady"),
                    "writeMissingFieldHints": profile_view.get("writeMissingFieldHints"),
                    "writeBlockerNoteHasReadonly": "只读" in str(profile_view.get("writeBlockerNote", "")),
                    "apiWriteReady": api_row.get("writeReady"),
                    "apiEvidenceWriteReady": ((evidence_payload.get("summary") or {}).get("writeReady")),
                    "markdownHasWriteBlocker": "writeBlockerNote" in markdown,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
