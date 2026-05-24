from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import task_guard, task_runtime, task_runtime_evidence_store
from cloudpan_sync.models import SourceEntry, TaskCreateRequest


def _build_local_file(name: str, content: bytes) -> tuple[TemporaryDirectory, str]:
    temp_dir = TemporaryDirectory()
    file_path = Path(temp_dir.name) / name
    file_path.write_bytes(content)
    return temp_dir, str(file_path)


def main() -> None:
    original_tasks = dict(task_runtime._TASKS)
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE
    original_quark = task_runtime.upload_quark_fast_file
    original_guard_get_profile = task_guard.get_profile
    original_guard_auth_view = task_guard.auth_profile_view

    temp_dir, local_path = _build_local_file("quark.bin", b"quark-payload")
    runtime_tmp = TemporaryDirectory()
    task_runtime._TASKS.clear()
    task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = Path(runtime_tmp.name) / "task_runtime_evidence.json"

    calls: list[dict[str, object]] = []

    def fake_upload(*, profile_id: str, local_path: str, target_name: str, parent_id: str = "", expected_md5: str = "", expected_sha1: str = "", conflict_policy: str = "auto_rename_new"):
        calls.append(
            {
                "profileId": profile_id,
                "localPath": local_path,
                "targetName": target_name,
                "parentId": parent_id,
                "expectedMd5": expected_md5,
                "expectedSha1": expected_sha1,
                "conflictPolicy": conflict_policy,
            }
        )
        return type(
            "UploadResult",
            (),
            {
                "ok": True,
                "mode": "binary_upload_after_hash_miss",
                "parentId": parent_id,
                "riskHint": "",
                "payload": {
                    "resolvedTargetName": f"{Path(target_name).stem} (1){Path(target_name).suffix}",
                    "conflictAction": "overwrite_downgraded_to_auto_rename",
                    "fileId": "quark-file-1",
                },
                "verifyOk": True,
                "verifyMode": "finish_response_after_binary_upload",
                "verifyNote": "quark verified",
                "verifyPayload": {"usedBinaryFallback": True},
                "note": "quark direct local upload completed.",
                "error": "",
            },
        )()

    task_runtime.upload_quark_fast_file = fake_upload
    task_guard.get_profile = lambda profile_id: object() if profile_id == "quark-profile-1" else None
    task_guard.auth_profile_view = lambda profile: {"profileReady": True, "writeReady": True}

    try:
        task = task_runtime.create_task(
            TaskCreateRequest(
                sourceProvider="xunlei",
                targetProvider="quark",
                targetProfileId="quark-profile-1",
                targetParentId="quark-root",
                thresholdMB=200,
                conflictPolicy="overwrite_existing",
                selectedRoots=["/demo.bin"],
                entries=[SourceEntry(path="/demo.bin", size=16, md5="", sha1="", localPath=local_path)],
            )
        )
        task = task_runtime.acknowledge_task_risk(str(task.get("taskId") or ""))
        run_result = task_runtime.run_task(str(task.get("taskId") or ""))
        detail = task_runtime.get_task(str(task.get("taskId") or "")) or {}
        runtime_payload = task_runtime_evidence_store.build_task_runtime_evidence_payload()
        print(
            json.dumps(
                {
                    "taskState": run_result.get("state"),
                    "summary": copy.deepcopy((detail.get("summary") or {})),
                    "result": copy.deepcopy(((detail.get("results") or [None])[0] or {})),
                    "uploadCalls": calls,
                    "runtimeSummary": runtime_payload.get("summary"),
                    "latestRuntimeItem": copy.deepcopy(((runtime_payload.get("latestItems") or [None])[0] or {})),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        task_runtime.upload_quark_fast_file = original_quark
        task_guard.get_profile = original_guard_get_profile
        task_guard.auth_profile_view = original_guard_auth_view
        task_runtime._TASKS.clear()
        task_runtime._TASKS.update(original_tasks)
        task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file
        temp_dir.cleanup()
        runtime_tmp.cleanup()


if __name__ == "__main__":
    main()
