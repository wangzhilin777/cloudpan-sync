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
from cloudpan_sync.aliyun_open_upload_live import AliyunOpenUploadResult


def main() -> None:
    original_tasks = dict(task_runtime._TASKS)
    original_password = webapp.ADMIN_PASSWORD
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE
    original_upload = task_runtime.upload_aliyun_open_local_file
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

        def fake_upload(
            profile_id: str,
            local_path: str,
            target_name: str,
            parent_file_id: str = "root",
            expected_md5: str = "",
            conflict_policy: str = "auto_rename_new",
        ) -> AliyunOpenUploadResult:
            return AliyunOpenUploadResult(
                ok=True,
                mode="binary_upload_single_part",
                usedProfile=True,
                profileId=profile_id,
                parentId=parent_file_id or "root",
                status=200,
                error="",
                note="Aliyun upload ok",
                payload={
                    "resolvedTargetName": "demo (1).bin",
                    "conflictAction": "auto_rename_new",
                    "fileId": "ali-file-1",
                },
                verifyOk=True,
                verifyMode="metadata_by_file_id",
                verifyNote="verified by metadata",
                verifyPayload={"fileId": "ali-file-1"},
            )

        task_runtime.upload_aliyun_open_local_file = fake_upload
        webapp.ADMIN_PASSWORD = "admin123"

        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})

            created = client.post(
                "/api/tasks",
                json={
                    "sourceProvider": "quark",
                    "targetProvider": "aliyundrive_open",
                    "targetProfileId": "ali-1",
                    "targetParentId": "root",
                    "thresholdMB": 200,
                    "conflictPolicy": "auto_rename_new",
                    "acknowledgePendingManual": True,
                    "acknowledgeDownloadUpload": True,
                    "selectedRoots": ["/demo.bin"],
                    "entries": [
                        {
                            "path": "/demo.bin",
                            "size": 4,
                            "md5": "",
                            "localPath": str(file_path),
                        }
                    ],
                },
            ).json()

            task_id = str((created.get("item") or {}).get("taskId") or "")
            client.post(f"/api/tasks/{task_id}/action", json={"action": "acknowledge_risk"})
            run_result = client.post(f"/api/tasks/{task_id}/action", json={"action": "run"}).json()
            detail_view = dict(run_result.get("detailView") or {})
            results = list(detail_view.get("results") or [])
            rows = task_runtime_evidence_store.latest_task_runtime_evidence()

            real_evidence_report.list_profiles = lambda: [
                type("Profile", (), {"profileId": "ali-1", "displayName": "Aliyun Smoke", "providerKey": "aliyundrive_open"})()
            ]
            real_evidence_report.latest_live_validations = lambda: []
            real_evidence_report.latest_provider_live_probes = lambda: []
            real_evidence_report.build_provider_registry = lambda: [
                type("RegistryItem", (), {"profile": type("Profile", (), {"providerKey": "aliyundrive_open", "displayName": "Aliyun Drive Open"})()})()
            ]
            real_evidence_report.build_provider_research_index = lambda: [
                {"providerKey": "aliyundrive_open", "displayName": "Aliyun Drive Open", "notes": "Aliyun note"}
            ]
            report = real_evidence_report.build_real_evidence_report()
        finally:
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            webapp.ADMIN_PASSWORD = original_password
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file
            task_runtime.upload_aliyun_open_local_file = original_upload
            real_evidence_report.list_profiles = original_list_profiles
            real_evidence_report.latest_live_validations = original_latest_validations
            real_evidence_report.latest_provider_live_probes = original_latest_probes
            real_evidence_report.build_provider_registry = original_registry
            real_evidence_report.build_provider_research_index = original_research

    provider_row = next((item for item in report.get("items", []) if item.get("providerKey") == "aliyundrive_open"), {})
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
