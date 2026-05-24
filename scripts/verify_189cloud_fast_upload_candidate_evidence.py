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

from cloudpan_sync import real_evidence_report, task_runtime, task_runtime_evidence_store


def main() -> None:
    original_tasks = dict(task_runtime._TASKS)
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE
    original_get_profile = task_runtime.get_profile
    original_list_profiles = real_evidence_report.list_profiles
    original_latest_validations = real_evidence_report.latest_live_validations
    original_latest_probes = real_evidence_report.latest_provider_live_probes
    original_registry = real_evidence_report.build_provider_registry
    original_research = real_evidence_report.build_provider_research_index

    task_runtime._TASKS.clear()

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = tmp_path / "task_runtime_evidence.json"
        task_runtime.get_profile = lambda profile_id: SimpleNamespace(
            profileId=profile_id,
            token="access-token-demo",
            extra={
                "signature": "sig-demo",
                "date": "Sat, 24 May 2026 00:00:00 GMT",
            },
        )

        try:
            task_id = "task-189-fast-candidate"
            task_runtime._TASKS[task_id] = {
                "taskId": task_id,
                "sourceProvider": "baidu_netdisk",
                "targetProvider": "189cloud",
                "targetProfileId": "189-fast-1",
                "targetParentId": "root-file",
                "thresholdMB": 0,
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
                            "path": "/movie.mkv",
                            "size": 4096,
                            "strategy": "fast_upload",
                            "conflictPolicy": "auto_rename_new",
                            "conflictSupportStatus": "probe_only_runtime_write_check",
                            "conflictNote": "189Cloud task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet.",
                            "normalizedFingerprints": {"md5": "0123456789abcdef0123456789abcdef", "etag": "", "sha1": "", "gcid": ""},
                        }
                    ],
                    "summary": {
                        "strategyCounts": {
                            "download_upload": 0,
                            "pending_manual": 0,
                            "fast_upload": 1,
                        }
                    },
                },
                "sourceEntries": [
                    {
                        "path": "/movie.mkv",
                        "size": 4096,
                        "md5": "0123456789abcdef0123456789abcdef",
                    }
                ],
            }

            run_result = task_runtime.run_task(task_id)
            results = list(run_result.get("results") or [])
            rows = task_runtime_evidence_store.latest_task_runtime_evidence()

            real_evidence_report.list_profiles = lambda: [
                SimpleNamespace(profileId="189-fast-1", displayName="189 Fast Candidate", providerKey="189cloud")
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
        finally:
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file
            task_runtime.get_profile = original_get_profile
            real_evidence_report.list_profiles = original_list_profiles
            real_evidence_report.latest_live_validations = original_latest_validations
            real_evidence_report.latest_provider_live_probes = original_latest_probes
            real_evidence_report.build_provider_registry = original_registry
            real_evidence_report.build_provider_research_index = original_research

    provider_row = next((item for item in report.get("items", []) if item.get("providerKey") == "189cloud"), {})
    print(
        json.dumps(
            {
                "runtimeEvidenceCount": len(rows),
                "firstResult": results[0] if results else {},
                "firstRuntimeRow": rows[0] if rows else {},
                "reportTaskRuntimeEvidence": provider_row.get("taskRuntimeEvidence"),
                "reportSummary": report.get("summary"),
                "candidateDoesNotCountAsRuntimeSuccess": not bool(((provider_row.get("taskRuntimeEvidence") or {}).get("ok"))),
                "candidateCountPreserved": int(((provider_row.get("taskRuntimeEvidence") or {}).get("candidateCount", 0)) or 0) == 1,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
