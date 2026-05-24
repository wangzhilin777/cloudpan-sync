from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import real_evidence_report, webapp


def main() -> None:
    original_password = webapp.ADMIN_PASSWORD
    original_list_profiles = real_evidence_report.list_profiles
    original_latest_validations = real_evidence_report.latest_live_validations
    original_latest_probes = real_evidence_report.latest_provider_live_probes
    original_latest_runtime = real_evidence_report.latest_task_runtime_evidence
    original_registry = real_evidence_report.build_provider_registry
    original_research = real_evidence_report.build_provider_research_index

    try:
        webapp.ADMIN_PASSWORD = "admin123"
        real_evidence_report.list_profiles = lambda: [
            SimpleNamespace(profileId="gy-1", displayName="Guangya Smoke", providerKey="guangya"),
            SimpleNamespace(profileId="189-1", displayName="189 Share", providerKey="189cloud"),
        ]
        real_evidence_report.latest_live_validations = lambda: [
            {"profileId": "gy-1", "providerKey": "guangya", "ok": True},
            {"profileId": "189-1", "providerKey": "189cloud", "ok": False},
        ]
        real_evidence_report.latest_provider_live_probes = lambda: [
            {
                "profileId": "gy-1",
                "providerKey": "guangya",
                "checks": [
                    {"kind": "list", "ok": True},
                    {"kind": "metadata", "ok": True},
                    {"kind": "create_dir", "ok": True},
                ],
            },
            {
                "profileId": "189-1",
                "providerKey": "189cloud",
                "checks": [
                    {"kind": "list", "ok": True},
                    {"kind": "metadata", "ok": True},
                    {"kind": "create_dir", "ok": False},
                ],
            },
        ]
        real_evidence_report.latest_task_runtime_evidence = lambda: [
            {"providerKey": "guangya", "profileId": "gy-1", "path": "/demo.bin", "mode": "binary_upload_multipart", "success": True},
            {"providerKey": "189cloud", "profileId": "189-1", "path": "/demo.bin", "mode": "share_upload_attempt", "success": False, "error": "readonly"},
        ]
        real_evidence_report.build_provider_registry = lambda: [
            SimpleNamespace(profile=SimpleNamespace(providerKey="guangya", displayName="光鸭网盘")),
            SimpleNamespace(profile=SimpleNamespace(providerKey="189cloud", displayName="天翼云盘")),
        ]
        real_evidence_report.build_provider_research_index = lambda: [
            {"providerKey": "guangya", "displayName": "光鸭网盘", "notes": "Guangya note"},
            {"providerKey": "189cloud", "displayName": "天翼云盘", "notes": "189 note"},
        ]

        payload = real_evidence_report.build_real_evidence_report()
        markdown = real_evidence_report.real_evidence_to_markdown(payload)

        app = webapp.create_app()
        client = TestClient(app)
        login = client.post("/api/login", json={"password": "admin123"})
        assert login.status_code == 200, login.text
        api_payload = client.get("/api/real_evidence").json()
        api_markdown = client.get("/api/real_evidence_markdown").json()

        print(
            json.dumps(
                {
                    "summary": payload.get("summary"),
                    "guangya": next((item for item in payload.get("items", []) if item.get("providerKey") == "guangya"), {}),
                    "tianyi": next((item for item in payload.get("items", []) if item.get("providerKey") == "189cloud"), {}),
                    "markdownHasTitle": "# CloudPan Sync 真实证据状态报告" in markdown,
                    "markdownHasRuntimeFailedSummary": "task_runtime_failed=1" in markdown,
                    "markdownHasRuntimeSampleSummary": "runtime_samples=2" in markdown and "runtime_success=1" in markdown and "runtime_failed=1" in markdown,
                    "markdownHasGuangya": "## guangya - 光鸭网盘" in markdown,
                    "apiSummary": api_payload.get("summary"),
                    "apiMarkdownHasTitle": "# CloudPan Sync 真实证据状态报告" in str(api_markdown.get("markdown") or ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        webapp.ADMIN_PASSWORD = original_password
        real_evidence_report.list_profiles = original_list_profiles
        real_evidence_report.latest_live_validations = original_latest_validations
        real_evidence_report.latest_provider_live_probes = original_latest_probes
        real_evidence_report.latest_task_runtime_evidence = original_latest_runtime
        real_evidence_report.build_provider_registry = original_registry
        real_evidence_report.build_provider_research_index = original_research


if __name__ == "__main__":
    main()
