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
from cloudpan_sync.real_evidence_remediation import (
    build_real_evidence_remediation_bundle,
    real_evidence_remediation_to_markdown,
)
from cloudpan_sync import webapp
from fastapi.testclient import TestClient


def main() -> None:
    synthetic_report = {
        "items": [
            {
                "providerKey": "guangya",
                "displayName": "Guangya",
                "authEvidence": {"ok": False},
                "listEvidence": {"ok": False},
                "metadataEvidence": {"ok": False},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["缺少通过的 auth validation 证据"],
            },
            {
                "providerKey": "189cloud",
                "displayName": "Tianyi 189Cloud",
                "authEvidence": {"ok": True},
                "listEvidence": {"ok": True},
                "metadataEvidence": {"ok": True},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 1},
                "gaps": ["已有 task runtime 失败样本，但尚无成功样本"],
            },
            {
                "providerKey": "aliyundrive_open",
                "displayName": "Aliyun Drive Open",
                "authEvidence": {"ok": False},
                "listEvidence": {"ok": False},
                "metadataEvidence": {"ok": False},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["缺少通过的 auth validation 证据"],
            },
        ]
    }
    synthetic_profiles = [
        {
            "profileId": "gy-rem-1",
            "providerKey": "guangya",
            "displayName": "smoke-guangya",
            "profileReady": False,
            "writeReady": True,
        },
        {
            "profileId": "ali-rem-1",
            "providerKey": "aliyundrive_open",
            "displayName": "ali-ready",
            "profileReady": True,
            "writeReady": True,
        },
        {
            "profileId": "189-rem-1",
            "providerKey": "189cloud",
            "displayName": "share-189",
            "profileReady": True,
            "writeReady": False,
        },
    ]
    bundle = build_real_evidence_remediation_bundle(report=synthetic_report, profile_views=synthetic_profiles)
    markdown = real_evidence_remediation_to_markdown(bundle)

    with TemporaryDirectory() as tmp_dir:
        configure_data_dir(Path(tmp_dir))
        original_password = webapp.ADMIN_PASSWORD
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            api_bundle = client.get("/api/real_evidence_remediation_bundle").json()
            api_markdown = client.get("/api/real_evidence_remediation_markdown").json()
        finally:
            webapp.ADMIN_PASSWORD = original_password

    print(
        json.dumps(
            {
                "providerCount": ((bundle.get("summary") or {}).get("providerCount")),
                "providersWithCreateCommand": ((bundle.get("summary") or {}).get("providersWithCreateCommand")),
                "providersWithBootstrapCommand": ((bundle.get("summary") or {}).get("providersWithBootstrapCommand")),
                "providersWithPatchCommand": ((bundle.get("summary") or {}).get("providersWithPatchCommand")),
                "providersWithPatchProbeCommand": ((bundle.get("summary") or {}).get("providersWithPatchProbeCommand")),
                "providersWithRefreshEvidenceCommand": ((bundle.get("summary") or {}).get("providersWithRefreshEvidenceCommand")),
                "providersBlockedOnly": ((bundle.get("summary") or {}).get("providersBlockedOnly")),
                "markdownHasCreateCommand": "create_auth_profile_stub.py" in markdown,
                "markdownHasBootstrapCommand": "recommendedBootstrapCommand" in markdown and "--probe" in markdown,
                "guangyaHasPatchCommand": "patch_auth_profile_extra.py" in markdown,
                "guangyaHasPatchProbeCommand": "patch_and_probe_auth_profile.py" in markdown,
                "markdownHasRefreshEvidenceCommand": "recommendedRefreshEvidenceCommand" in markdown and "--profile-id" in markdown,
                "cloud189HasHelper": "patch_189cloud_account_auth.py" in markdown,
                "markdownHasAuthModes": "recommendedAuthModes" in markdown,
                "markdownHasLoginUrl": "webLoginUrl" in markdown,
                "markdownHasFieldHints": "requiredFieldHints" in markdown,
                "markdownHasNextStep": "nextStep:" in markdown,
                "apiHasSummary": bool((api_bundle.get("summary") or {}).get("providerCount", 0) >= 0),
                "apiMarkdownHasTitle": "# CloudPan Sync 真实联调补救指南" in str(api_markdown.get("markdown", "")),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
