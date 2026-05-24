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

from cloudpan_sync import provider_status_matrix, real_evidence_report, task_runtime, task_runtime_evidence_store


def main() -> None:
    original_tasks = dict(task_runtime._TASKS)
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE
    original_create_dir = task_runtime.fetch_tianyi_create_folder
    original_list_profiles = real_evidence_report.list_profiles
    original_latest_validations = real_evidence_report.latest_live_validations
    original_latest_probes = real_evidence_report.latest_provider_live_probes
    original_registry = real_evidence_report.build_provider_registry
    original_research = real_evidence_report.build_provider_research_index

    task_runtime._TASKS.clear()

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = tmp_path / "task_runtime_evidence.json"
        file_path = tmp_path / "demo.bin"
        file_path.write_bytes(b"demo")

        def fake_create_dir(profile_id: str, parent_id: str = "", dir_name: str = ""):
            return SimpleNamespace(
                ok=False,
                mode="unsupported_readonly_share_auth",
                profileId=profile_id,
                note="189Cloud create folder is not available on the current shareCode/accessCode read-only probe path; official createFolder.action requires account-level OAuth headers.",
                error="share_auth_readonly",
                payload={
                    "parentId": parent_id,
                    "dirName": dir_name,
                    "requiredAuth": ["AccessToken", "Signature", "Date"],
                },
            )

        task_runtime.fetch_tianyi_create_folder = fake_create_dir
        try:
            task_id = "task-189-runtime-probe"
            task_runtime._TASKS[task_id] = {
                "taskId": task_id,
                "sourceProvider": "quark",
                "targetProvider": "189cloud",
                "targetProfileId": "189-1",
                "targetParentId": "root-file",
                "thresholdMB": 200,
                "conflictPolicy": "auto_rename_new",
                "state": "ready",
                "createdAt": "2026-05-24T00:00:00+00:00",
                "updatedAt": "2026-05-24T00:00:00+00:00",
                "progress": {"done": 0, "failed": 0},
                "risk": {"paused": False, "reason": ""},
                "guard": {"hardBlocked": False, "requiresAcknowledgement": {}, "acknowledged": {}},
                "summary": {},
                "results": [],
                "plan": {
                    "items": [
                        {
                            "path": "/demo.bin",
                            "size": 4,
                            "strategy": "download_upload",
                            "conflictPolicy": "auto_rename_new",
                        }
                    ],
                    "summary": {
                        "strategyCounts": {
                            "download_upload": 1,
                            "pending_manual": 0,
                            "fast_upload": 0,
                        }
                    },
                },
                "sourceEntries": [
                    {
                        "path": "/demo.bin",
                        "size": 4,
                        "md5": "",
                        "localPath": str(file_path),
                    }
                ],
            }

            run_result = task_runtime.run_task(task_id)
            results = list(run_result.get("results") or [])
            rows = task_runtime_evidence_store.latest_task_runtime_evidence()
            runtime_payload = task_runtime_evidence_store.build_task_runtime_evidence_payload()

            real_evidence_report.list_profiles = lambda: [
                SimpleNamespace(profileId="189-1", displayName="189 Smoke", providerKey="189cloud")
            ]
            real_evidence_report.latest_live_validations = lambda: []
            real_evidence_report.latest_provider_live_probes = lambda: []
            real_evidence_report.build_provider_registry = lambda: [
                SimpleNamespace(profile=SimpleNamespace(providerKey="189cloud", displayName="Tianyi 189Cloud"))
            ]
            real_evidence_report.build_provider_research_index = lambda: [
                {"providerKey": "189cloud", "displayName": "Tianyi 189Cloud", "notes": "189 note"}
            ]
            report = real_evidence_report.build_real_evidence_report()
            matrix = provider_status_matrix.build_status_matrix()
        finally:
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file
            task_runtime.fetch_tianyi_create_folder = original_create_dir
            real_evidence_report.list_profiles = original_list_profiles
            real_evidence_report.latest_live_validations = original_latest_validations
            real_evidence_report.latest_provider_live_probes = original_latest_probes
            real_evidence_report.build_provider_registry = original_registry
            real_evidence_report.build_provider_research_index = original_research

    provider_row = next((item for item in report.get("items", []) if item.get("providerKey") == "189cloud"), {})
    matrix_row = next((item for item in (matrix.get("items") or []) if item.get("providerKey") == "189cloud"), {})
    print(
        json.dumps(
            {
                "runtimeEvidenceCount": len(rows),
                "firstResult": results[0] if results else {},
                "firstRuntimeRow": rows[0] if rows else {},
                "runtimeMarkdownHasRequiredAuth": "requiredAuth=AccessToken,Signature,Date"
                in task_runtime_evidence_store.task_runtime_evidence_to_markdown(runtime_payload),
                "reportTaskRuntimeEvidence": provider_row.get("taskRuntimeEvidence"),
                "matrixTaskRuntimeTrack": matrix_row.get("task_runtime_track"),
                "matrixTaskRuntimeFailed": matrix_row.get("task_runtime_failed"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
