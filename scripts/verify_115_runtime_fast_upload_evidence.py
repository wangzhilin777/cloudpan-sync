from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import real_evidence_report, task_runtime, task_runtime_evidence_store, webapp
from cloudpan_sync.pan115_fast_upload_live import Pan115FastUploadResult


def main() -> None:
    original_tasks = dict(task_runtime._TASKS)
    original_password = webapp.ADMIN_PASSWORD
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE
    original_upload = task_runtime.upload_115_open_fast_file
    original_list_profiles = real_evidence_report.list_profiles
    original_latest_validations = real_evidence_report.latest_live_validations
    original_latest_probes = real_evidence_report.latest_provider_live_probes
    original_registry = real_evidence_report.build_provider_registry
    original_research = real_evidence_report.build_provider_research_index

    task_runtime._TASKS.clear()

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = tmp_path / "task_runtime_evidence.json"
        file_path = tmp_path / "movie.mkv"
        file_path.write_bytes(b"115-fast-upload-demo")

        def fake_upload(
            *,
            profile_id: str,
            local_path: str,
            target_name: str,
            parent_id: str = "",
            expected_sha1: str = "",
        ) -> Pan115FastUploadResult:
            return Pan115FastUploadResult(
                ok=True,
                mode="rapid_upload_by_hash",
                usedProfile=True,
                profileId=profile_id,
                parentId=parent_id,
                status=200,
                error="",
                note="115 rapid upload ok",
                payload={
                    "resolvedTargetName": "movie.mkv",
                    "conflictAction": "",
                    "fileId": "115-file-1",
                    "pickCode": "pc115",
                    "target": "U_1_115-root",
                    "responseStatus": 2,
                },
                verifyOk=True,
                verifyMode="metadata_by_file_id",
                verifyNote="verified by metadata",
                verifyPayload={"fileId": "115-file-1"},
            )

        task_runtime.upload_115_open_fast_file = fake_upload
        webapp.ADMIN_PASSWORD = "admin123"

        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})

            created = client.post(
                "/api/tasks",
                json={
                    "sourceProvider": "baidu_netdisk",
                    "targetProvider": "115_open",
                    "targetProfileId": "115-1",
                    "targetParentId": "115-root",
                    "thresholdMB": 0,
                    "conflictPolicy": "auto_rename_new",
                    "acknowledgePendingManual": True,
                    "acknowledgeDownloadUpload": True,
                    "selectedRoots": ["/movie.mkv"],
                    "entries": [
                        {
                            "path": "/movie.mkv",
                            "size": file_path.stat().st_size,
                            "sha1": "abcdef0123456789abcdef0123456789abcdef01",
                            "localPath": str(file_path),
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
                type("Profile", (), {"profileId": "115-1", "displayName": "115 Fast Upload", "providerKey": "115_open"})()
            ]
            real_evidence_report.latest_live_validations = lambda: []
            real_evidence_report.latest_provider_live_probes = lambda: []
            real_evidence_report.build_provider_registry = lambda: [
                type("RegistryItem", (), {"profile": type("Profile", (), {"providerKey": "115_open", "displayName": "115 Open"})()})()
            ]
            real_evidence_report.build_provider_research_index = lambda: [
                {"providerKey": "115_open", "displayName": "115 Open", "notes": "115 note"}
            ]
            report = real_evidence_report.build_real_evidence_report()
        finally:
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            webapp.ADMIN_PASSWORD = original_password
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file
            task_runtime.upload_115_open_fast_file = original_upload
            real_evidence_report.list_profiles = original_list_profiles
            real_evidence_report.latest_live_validations = original_latest_validations
            real_evidence_report.latest_provider_live_probes = original_latest_probes
            real_evidence_report.build_provider_registry = original_registry
            real_evidence_report.build_provider_research_index = original_research

    provider_row = next((item for item in report.get("items", []) if item.get("providerKey") == "115_open"), {})
    print(
        json.dumps(
            {
                "runtimeEvidenceCount": len(rows),
                "firstResult": results[0] if results else {},
                "firstRuntimeRow": rows[0] if rows else {},
                "detailSummary": detail_view.get("summary"),
                "reportTaskRuntimeEvidence": provider_row.get("taskRuntimeEvidence"),
                "reportSummary": report.get("summary"),
                "runtimeSuccessSaved": bool((rows[0] if rows else {}).get("success")),
                "reportCountsRuntimeSuccess": bool(((provider_row.get("taskRuntimeEvidence") or {}).get("ok"))),
                "detailSummaryMarksRealTransfer": str(((detail_view.get("summary") or {}).get("completionKind") or "")) == "real_transfer",
                "taskStateIsCompleted": str((run_result.get("item") or {}).get("state") or detail_view.get("state") or "") == "completed",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
