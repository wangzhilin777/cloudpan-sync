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

from cloudpan_sync import task_runtime, task_runtime_evidence_store, webapp
from cloudpan_sync.models import SourceEntry


def main() -> None:
    original_fast_check = task_runtime.fetch_guangya_live_fast_check
    original_upload = task_runtime.upload_guangya_local_file
    original_tasks = dict(task_runtime._TASKS)
    original_password = webapp.ADMIN_PASSWORD
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE

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
                            "error": "inventory_miss",
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
            from cloudpan_sync.guangya_upload_live import GuangyaUploadResult

            return GuangyaUploadResult(
                ok=False,
                mode="binary_upload_multipart",
                usedProfile=True,
                profileId=profile_id,
                parentId=parent_id or "dir-100",
                status=500,
                error="upload_failed",
                note="upload failed",
                riskHint="provider rejected upload",
                payload={},
                verifyOk=False,
                verifyMode="",
                verifyNote="",
                verifyPayload={},
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
            latest = task_runtime_evidence_store.latest_task_runtime_evidence()
            summary = task_runtime_evidence_store.task_runtime_evidence_summary()
        finally:
            task_runtime.fetch_guangya_live_fast_check = original_fast_check
            task_runtime.upload_guangya_local_file = original_upload
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            webapp.ADMIN_PASSWORD = original_password
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file

    row = latest[0] if latest else {}
    print(
        json.dumps(
            {
                "liveFailureEvidencePersisted": (
                    len(latest) == 1
                    and row.get("providerKey") == "guangya"
                    and row.get("profileId") == "gy-1"
                    and row.get("mode") == "binary_upload_multipart"
                    and row.get("executionMode") == "live"
                    and row.get("success") is False
                    and row.get("status") == "failed"
                    and row.get("verifyOk") is False
                    and row.get("error") == "upload_failed"
                    and row.get("riskHint") == "provider rejected upload"
                    and row.get("note") == "upload failed"
                    and summary.get("failedProviderCount") == 1
                    and summary.get("failedCount") == 1
                    and summary.get("profileCount") == 1
                    and summary.get("runtimeOrphanProviderCount") == 1
                    and summary.get("runtimeOrphanProfileCount") == 1
                    and summary.get("failedProfiles") == ["gy-1"]
                    and summary.get("runtimeOrphanProfiles") == ["gy-1"]
                ),
                "runtimeEvidenceCount": len(latest),
                "firstRuntimeRow": row,
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
