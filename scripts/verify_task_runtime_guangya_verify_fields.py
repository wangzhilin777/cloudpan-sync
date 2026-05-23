from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import task_runtime
from cloudpan_sync.guangya_upload_live import GuangyaUploadResult
from cloudpan_sync.models import SourceEntry, TaskCreateRequest


def main() -> None:
    original_fast_check = task_runtime.fetch_guangya_live_fast_check
    original_upload = task_runtime.upload_guangya_local_file
    original_tasks = dict(task_runtime._TASKS)
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

        def fake_upload(profile_id: str, local_path: str, target_name: str, parent_id: str = "", expected_md5: str = "", conflict_policy: str = "auto_rename_new"):
            return GuangyaUploadResult(
                ok=True,
                mode="binary_upload_multipart",
                usedProfile=True,
                profileId=profile_id,
                parentId=parent_id or "dir-100",
                status=200,
                error="",
                note="upload ok",
                payload={"taskId": "task-1"},
                verifyOk=True,
                verifyMode="list_by_parent_name",
                verifyNote="verified by list",
                verifyPayload={"matchedItem": {"fileId": "f-1", "name": target_name}},
            )

        task_runtime.fetch_guangya_live_fast_check = fake_fast_check
        task_runtime.upload_guangya_local_file = fake_upload
        try:
            task = task_runtime.create_task(
                TaskCreateRequest(
                    sourceProvider="quark",
                    targetProvider="guangya",
                    targetProfileId="gy-1",
                    targetParentId="dir-100",
                    thresholdMB=200,
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

    row = (result.get("results") or [{}])[0]
    live_attempt = row.get("liveAttempt") or {}
    print(
        json.dumps(
            {
                "taskState": result.get("state"),
                "rowStatus": row.get("status"),
                "liveMode": live_attempt.get("mode"),
                "verifyOk": live_attempt.get("verifyOk"),
                "verifyMode": live_attempt.get("verifyMode"),
                "verifyNote": live_attempt.get("verifyNote"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
