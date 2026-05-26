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

from cloudpan_sync import task_guard, task_runtime, webapp
from cloudpan_sync.guangya_upload_live import GuangyaUploadResult
from cloudpan_sync.models import AuthProfile, SourceEntry


def main() -> None:
    original_fast_check = task_runtime.fetch_guangya_live_fast_check
    original_upload = task_runtime.upload_guangya_local_file
    original_task_guard_get_profile = task_guard.get_profile
    original_task_runtime_get_profile = task_runtime.get_profile
    original_tasks = dict(task_runtime._TASKS)
    original_password = webapp.ADMIN_PASSWORD
    task_runtime._TASKS.clear()

    with TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "demo.bin"
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
        mock_profile = AuthProfile(
            profileId="gy-1",
            providerKey="guangya",
            authMode="manual_token",
            displayName="mock-guangya",
            token="tok",
            cookie="",
            extra={"parentId": "dir-100"},
            status="verified",
            lastError="",
            createdAt="2026-05-27T00:00:00+00:00",
            updatedAt="2026-05-27T00:00:00+00:00",
        )

        def fake_get_profile(profile_id: str):
            if profile_id == "gy-1":
                return mock_profile
            return None

        task_guard.get_profile = fake_get_profile
        task_runtime.get_profile = fake_get_profile
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
            after_run = client.post(
                f"/api/tasks/{task_id}/action",
                json={"action": "run"},
            ).json()
        finally:
            task_runtime.fetch_guangya_live_fast_check = original_fast_check
            task_runtime.upload_guangya_local_file = original_upload
            task_guard.get_profile = original_task_guard_get_profile
            task_runtime.get_profile = original_task_runtime_get_profile
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            webapp.ADMIN_PASSWORD = original_password

    created_plan_item = ((((created.get("item") or {}).get("plan") or {}).get("items") or [{}])[0])
    detail_row = ((((after_run.get("detailView") or {}).get("results") or [{}]))[0])
    latest_row = ((((after_run.get("listView") or {}).get("latestResults") or [{}]))[0])
    detail_live_attempt = dict((detail_row or {}).get("liveAttempt") or {})
    latest_live_attempt = dict((latest_row or {}).get("liveAttempt") or {})
    print(
        json.dumps(
            {
                "planConflictSupportDowngradeIsRecorded": (
                    str(created_plan_item.get("conflictSupportStatus") or "") == "downgrade_to_auto_rename"
                    and "auto_rename_new" in str(created_plan_item.get("conflictNote") or "")
                ),
                "detailResultCarriesConflictRuntimeEvidence": (
                    str((detail_row or {}).get("status") or "") == "done"
                    and str((detail_row or {}).get("executionMode") or "") == "live"
                    and str((detail_row or {}).get("conflictSupportStatus") or "") == "downgrade_to_auto_rename"
                    and "auto_rename_new" in str((detail_row or {}).get("conflictNote") or "")
                    and detail_live_attempt.get("conflictAction") == "overwrite_downgraded_to_auto_rename"
                    and detail_live_attempt.get("resolvedTargetName") == "demo (1).bin"
                    and detail_live_attempt.get("verifyOk") is True
                    and detail_live_attempt.get("verifyMode") == "list_by_parent_name"
                ),
                "listLatestResultCarriesConflictRuntimeEvidence": (
                    str((latest_row or {}).get("status") or "") == "done"
                    and str((latest_row or {}).get("executionMode") or "") == "live"
                    and str((latest_row or {}).get("conflictSupportStatus") or "") == "downgrade_to_auto_rename"
                    and "auto_rename_new" in str((latest_row or {}).get("conflictNote") or "")
                    and latest_live_attempt.get("conflictAction") == "overwrite_downgraded_to_auto_rename"
                    and latest_live_attempt.get("resolvedTargetName") == "demo (1).bin"
                ),
                "planItemConflictSupportStatus": created_plan_item.get("conflictSupportStatus"),
                "planItemConflictNote": created_plan_item.get("conflictNote"),
                "detailResultConflictSupportStatus": (detail_row or {}).get("conflictSupportStatus"),
                "detailResultConflictNote": (detail_row or {}).get("conflictNote"),
                "detailResultConflictAction": detail_live_attempt.get("conflictAction"),
                "detailResultResolvedTargetName": detail_live_attempt.get("resolvedTargetName"),
                "listLatestConflictSupportStatus": (latest_row or {}).get("conflictSupportStatus"),
                "listLatestConflictNote": (latest_row or {}).get("conflictNote"),
                "listLatestConflictAction": latest_live_attempt.get("conflictAction"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
