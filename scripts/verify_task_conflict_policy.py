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

from cloudpan_sync import task_runtime, webapp
from cloudpan_sync.guangya_upload_live import GuangyaUploadResult
from cloudpan_sync.models import SourceEntry, TaskCreateRequest


def main() -> None:
    original_fast_check = task_runtime.fetch_guangya_live_fast_check
    original_upload = task_runtime.upload_guangya_local_file
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
            resolved_name = target_name if conflict_policy == "auto_rename_new" else "demo (1).bin"
            conflict_action = "auto_rename_new" if conflict_policy == "auto_rename_new" else "overwrite_downgraded_to_auto_rename"
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
                    "resolvedTargetName": resolved_name,
                    "conflictAction": conflict_action,
                },
                verifyOk=True,
                verifyMode="list_by_parent_name",
                verifyNote="verified by list",
                verifyPayload={"matchedItem": {"fileId": "f-1", "name": resolved_name}},
            )

        task_runtime.fetch_guangya_live_fast_check = fake_fast_check
        task_runtime.upload_guangya_local_file = fake_upload

        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            api_plan = client.post(
                "/api/plan/mock",
                json={
                    "sourceProvider": "quark",
                    "targetProvider": "guangya",
                    "thresholdMB": 200,
                    "conflictPolicy": "overwrite_existing",
                    "selectedRoots": ["/demo.bin"],
                    "entries": [{"path": "/demo.bin", "size": 4, "md5": ""}],
                },
            ).json()

            task = task_runtime.create_task(
                TaskCreateRequest(
                    sourceProvider="quark",
                    targetProvider="guangya",
                    targetProfileId="gy-1",
                    targetParentId="dir-100",
                    thresholdMB=200,
                    conflictPolicy="overwrite_existing",
                    selectedRoots=["/demo.bin"],
                    entries=[
                        SourceEntry(
                            path="/demo.bin",
                            size=4,
                            md5="",
                            localPath=str(file_path),
                        )
                    ],
                )
            )
            result = task_runtime.run_task(str(task.get("taskId")))
        finally:
            task_runtime.fetch_guangya_live_fast_check = original_fast_check
            task_runtime.upload_guangya_local_file = original_upload
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            webapp.ADMIN_PASSWORD = original_password

    row = (result.get("results") or [{}])[0]
    live_attempt = row.get("liveAttempt") or {}
    print(
        json.dumps(
            {
                "apiPlanConflictPolicy": api_plan.get("conflictPolicy"),
                "apiPlanItemConflictPolicy": ((api_plan.get("items") or [{}])[0]).get("conflictPolicy"),
                "taskConflictPolicy": task.get("conflictPolicy"),
                "rowConflictPolicy": row.get("conflictPolicy"),
                "conflictAction": live_attempt.get("conflictAction"),
                "resolvedTargetName": live_attempt.get("resolvedTargetName"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
