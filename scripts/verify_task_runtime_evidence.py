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
from cloudpan_sync.guangya_upload_live import GuangyaUploadResult
from cloudpan_sync.models import SourceEntry


def main() -> None:
    original_fast_check = task_runtime.fetch_guangya_live_fast_check
    original_upload = task_runtime.upload_guangya_local_file
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
        file_path = tmp_path / "demo.bin"
        file_path.write_bytes(b"demo")

        def fake_fast_check(profile_id: str, entries: list[SourceEntry], parent_id: str = ""):
            return type(
                "FastCheckResult",
                (),
                {
                    "note": "no instant hit",
                    "error": "",
                    "riskHint": "",
                    "items": [
                        {
                            "path": entry.path,
                            "hashKind": "md5",
                            "canFastUpload": False,
                            "error": "",
                            "riskHint": "fallback upload required",
                            "note": "no hit",
                        }
                        for entry in entries
                    ],
                },
            )()

        def fake_upload(
            profile_id: str,
            local_path: str,
            target_name: str,
            parent_id: str = "",
            expected_md5: str = "",
            conflict_policy: str = "auto_rename_new",
        ):
            return GuangyaUploadResult(
                ok=True,
                mode="binary_upload_multipart",
                usedProfile=True,
                profileId=profile_id,
                parentId=parent_id or "dir-100",
                status=200,
                error="",
                note="upload ok",
                payload={
                    "taskId": "task-1",
                    "requestedTargetName": target_name,
                    "resolvedTargetName": "demo (1).bin",
                    "conflictAction": "overwrite_downgraded_to_auto_rename",
                },
                verifyOk=True,
                verifyMode="list_by_parent_name",
                verifyNote="verified by list",
                verifyPayload={"matchedItem": {"fileId": "f-1", "name": "demo (1).bin"}},
            )

        task_runtime.fetch_guangya_live_fast_check = fake_fast_check
        task_runtime.upload_guangya_local_file = fake_upload
        webapp.ADMIN_PASSWORD = "admin123"

        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})

            created = client.post(
                "/api/tasks",
                json={
                    "sourceProvider": "quark",
                    "targetProvider": "guangya",
                    "targetProfileId": "gy-1",
                    "targetParentId": "dir-100",
                    "thresholdMB": 200,
                    "conflictPolicy": "overwrite_existing",
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
            client.post(f"/api/tasks/{task_id}/action", json={"action": "run"})

            rows = task_runtime_evidence_store.latest_task_runtime_evidence()

            real_evidence_report.list_profiles = lambda: [
                SimpleNamespace(profileId="gy-1", displayName="Guangya Smoke", providerKey="guangya")
            ]
            real_evidence_report.latest_live_validations = lambda: []
            real_evidence_report.latest_provider_live_probes = lambda: []
            real_evidence_report.build_provider_registry = lambda: [
                SimpleNamespace(profile=SimpleNamespace(providerKey="guangya", displayName="光鸭网盘"))
            ]
            real_evidence_report.build_provider_research_index = lambda: [
                {"providerKey": "guangya", "displayName": "光鸭网盘", "notes": "Guangya note"}
            ]
            report = real_evidence_report.build_real_evidence_report()
        finally:
            task_runtime.fetch_guangya_live_fast_check = original_fast_check
            task_runtime.upload_guangya_local_file = original_upload
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            webapp.ADMIN_PASSWORD = original_password
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file
            real_evidence_report.list_profiles = original_list_profiles
            real_evidence_report.latest_live_validations = original_latest_validations
            real_evidence_report.latest_provider_live_probes = original_latest_probes
            real_evidence_report.build_provider_registry = original_registry
            real_evidence_report.build_provider_research_index = original_research

    row = rows[0] if rows else {}
    provider_row = next((item for item in report.get("items", []) if item.get("providerKey") == "guangya"), {})
    print(
        json.dumps(
            {
                "taskRuntimeEvidenceFlowsIntoReport": (
                    len(rows) == 1
                    and row.get("providerKey") == "guangya"
                    and row.get("profileId") == "gy-1"
                    and row.get("mode") == "binary_upload_multipart"
                    and row.get("executionMode") == "live"
                    and row.get("success") is True
                    and row.get("status") == "done"
                    and row.get("verifyOk") is True
                    and row.get("verifyMode") == "list_by_parent_name"
                    and row.get("verifyNote") == "verified by list"
                    and row.get("conflictAction") == "overwrite_downgraded_to_auto_rename"
                    and row.get("resolvedTargetName") == "demo (1).bin"
                    and dict(provider_row.get("taskRuntimeEvidence") or {}).get("ok") is True
                    and dict(provider_row.get("taskRuntimeEvidence") or {}).get("sampleCount") == 1
                    and dict(provider_row.get("taskRuntimeEvidence") or {}).get("successCount") == 1
                    and dict(provider_row.get("taskRuntimeEvidence") or {}).get("conflictHandledCount") == 1
                    and dict(provider_row.get("taskRuntimeEvidence") or {}).get("profiles") == ["Guangya Smoke"]
                    and report.get("summary", {}).get("taskRuntimeEvidenceProviderCount") == 1
                    and report.get("summary", {}).get("taskRuntimeSuccessCount") == 1
                    and report.get("summary", {}).get("taskRuntimeConflictHandledCount") == 1
                    and report.get("summary", {}).get("taskRuntimeOrphanProviderCount") == 0
                ),
                "runtimeEvidenceCount": len(rows),
                "firstRuntimeRow": row,
                "reportTaskRuntimeEvidence": provider_row.get("taskRuntimeEvidence"),
                "reportSummary": report.get("summary"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
