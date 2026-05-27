from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import real_evidence_report, task_runtime, task_runtime_evidence_store, webapp


def main() -> None:
    original_tasks = dict(task_runtime._TASKS)
    original_password = webapp.ADMIN_PASSWORD
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE
    original_list_profiles = real_evidence_report.list_profiles
    original_latest_validations = real_evidence_report.latest_live_validations
    original_latest_probes = real_evidence_report.latest_provider_live_probes
    original_registry = real_evidence_report.build_provider_registry
    original_research = real_evidence_report.build_provider_research_index

    task_runtime._TASKS.clear()

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = tmp_path / "task_runtime_evidence.json"
        webapp.ADMIN_PASSWORD = "admin123"

        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})

            created = client.post(
                "/api/tasks",
                json={
                    "sourceProvider": "xunlei",
                    "targetProvider": "pikpak",
                    "targetProfileId": "pikpak-fast-1",
                    "targetParentId": "root",
                    "thresholdMB": 0,
                    "conflictPolicy": "auto_rename_new",
                    "acknowledgePendingManual": True,
                    "acknowledgeDownloadUpload": True,
                    "selectedRoots": ["/movie.mkv"],
                    "entries": [
                        {
                            "path": "/movie.mkv",
                            "size": 4096,
                            "gcid": "abcdef0123456789abcdef0123456789abcdef01",
                        }
                    ],
                },
            ).json()

            task_id = str((created.get("item") or {}).get("taskId") or "")
            run_result = client.post(f"/api/tasks/{task_id}/action", json={"action": "run"}).json()
            detail_view = dict(run_result.get("detailView") or {})
            results = list(detail_view.get("results") or [])
            rows = task_runtime_evidence_store.latest_task_runtime_evidence()

            real_evidence_report.list_profiles = lambda: [
                SimpleNamespace(profileId="pikpak-fast-1", displayName="PikPak Fast Candidate", providerKey="pikpak")
            ]
            real_evidence_report.latest_live_validations = lambda: []
            real_evidence_report.latest_provider_live_probes = lambda: []
            real_evidence_report.build_provider_registry = lambda: [
                SimpleNamespace(profile=SimpleNamespace(providerKey="pikpak", displayName="PikPak"))
            ]
            real_evidence_report.build_provider_research_index = lambda: [
                {"providerKey": "pikpak", "displayName": "PikPak", "notes": "PikPak note"}
            ]
            report = real_evidence_report.build_real_evidence_report()
        finally:
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            webapp.ADMIN_PASSWORD = original_password
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file
            real_evidence_report.list_profiles = original_list_profiles
            real_evidence_report.latest_live_validations = original_latest_validations
            real_evidence_report.latest_provider_live_probes = original_latest_probes
            real_evidence_report.build_provider_registry = original_registry
            real_evidence_report.build_provider_research_index = original_research

    provider_row = next((item for item in report.get("items", []) if item.get("providerKey") == "pikpak"), {})
    print(
        json.dumps(
            {
                "runtimeEvidenceCount": len(rows),
                "firstResult": results[0] if results else {},
                "firstRuntimeRow": rows[0] if rows else {},
                "reportTaskRuntimeEvidence": provider_row.get("taskRuntimeEvidence"),
                "reportSummary": report.get("summary"),
                "pikpakFastUploadCandidateEvidenceFlowMatchesExpectedProbeOnlyReport": (
                    len(rows) == 1
                    and (results[0] if results else {}).get("executionMode") == "probe"
                    and ((results[0] if results else {}).get("liveAttempt") or {}).get("mode") == "pikpak_fast_upload_candidate"
                    and ((results[0] if results else {}).get("liveAttempt") or {}).get("hashKind") == "gcid"
                    and (rows[0] if rows else {}).get("providerKey") == "pikpak"
                    and (rows[0] if rows else {}).get("executionMode") == "probe"
                    and (rows[0] if rows else {}).get("mode") == "pikpak_fast_upload_candidate"
                    and (rows[0] if rows else {}).get("verifyMode") == "fingerprint_candidate"
                    and ((provider_row.get("taskRuntimeEvidence") or {}).get("ok")) is False
                    and ((provider_row.get("taskRuntimeEvidence") or {}).get("sampleCount")) == 1
                    and ((provider_row.get("taskRuntimeEvidence") or {}).get("candidateCount")) == 1
                    and ((provider_row.get("taskRuntimeEvidence") or {}).get("candidateProfiles")) == ["PikPak Fast Candidate"]
                    and (report.get("summary") or {}).get("taskRuntimeEvidenceProviderCount") == 0
                    and (report.get("summary") or {}).get("taskRuntimeCandidateProviderCount") == 1
                    and (report.get("summary") or {}).get("taskRuntimeCandidateCount") == 1
                    and (report.get("summary") or {}).get("taskRuntimeCandidateProviders") == ["pikpak"]
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
