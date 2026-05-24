from __future__ import annotations

import contextlib
import io
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import task_runtime
from cloudpan_sync.models import AuthProfile

SCRIPT_PATH = ROOT / "scripts" / "create_fast_upload_candidate_task.py"
SPEC = importlib.util.spec_from_file_location("create_fast_upload_candidate_task", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
fast_candidate_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fast_candidate_script)


def main() -> None:
    original_create_task = task_runtime.create_task
    original_run_task = task_runtime.run_task
    original_get_profile = fast_candidate_script.get_profile

    def fake_create_task(payload: object) -> dict[str, object]:
        return {
            "taskId": "task-fast-candidate-1",
            "state": "ready",
            "targetProvider": getattr(payload, "targetProvider", ""),
            "targetProfileId": getattr(payload, "targetProfileId", ""),
            "sourceEntries": [entry.model_dump() for entry in getattr(payload, "entries", [])],
            "summary": {"state": "ready"},
            "results": [],
        }

    def fake_run_task(task_id: str) -> dict[str, object]:
        return {
            "taskId": task_id,
            "state": "completed",
            "targetProvider": "115_open",
            "targetProfileId": "115-fast-1",
            "sourceEntries": [
                {
                    "path": "/cloudpan-sync-fast-candidate.bin",
                    "size": 28,
                    "sha1": "96b06f478886641050f54f5504c05dbf1e0f0711",
                    "localPath": "temp.bin",
                }
            ],
            "results": [
                {
                    "path": "/cloudpan-sync-fast-candidate.bin",
                    "status": "done",
                    "executionMode": "probe",
                    "liveAttempt": {"mode": "115_open_fast_upload_candidate", "candidate": True},
                }
            ],
            "summary": {"state": "completed"},
        }

    def fake_get_profile(profile_id: str) -> AuthProfile | None:
        if profile_id != "115-fast-1":
            return None
        return AuthProfile(
            profileId="115-fast-1",
            providerKey="115_open",
            authMode="manual_cookie",
            displayName="115-fast",
            token="",
            cookie="UID=1; CID=2",
            extra={"cid": "115-root"},
            status="saved",
            lastError="",
            createdAt="2026-05-25T00:00:00+00:00",
            updatedAt="2026-05-25T00:00:00+00:00",
        )

    task_runtime.create_task = fake_create_task
    task_runtime.run_task = fake_run_task
    fast_candidate_script.task_runtime.create_task = fake_create_task
    fast_candidate_script.task_runtime.run_task = fake_run_task
    fast_candidate_script.get_profile = fake_get_profile
    try:
        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            result = fast_candidate_script.main(
                [
                    "--target-provider",
                    "115_open",
                    "--target-profile-id",
                    "115-fast-1",
                    "--auto-temp-file",
                    "--sha1",
                    "auto",
                ]
            )
    finally:
        task_runtime.create_task = original_create_task
        task_runtime.run_task = original_run_task
        fast_candidate_script.task_runtime.create_task = original_create_task
        fast_candidate_script.task_runtime.run_task = original_run_task
        fast_candidate_script.get_profile = original_get_profile

    output = json.loads(stdout_buffer.getvalue())
    source_entry = ((output.get("sourceEntries") or [{}])[0]) if output.get("sourceEntries") else {}

    print(
        json.dumps(
            {
                "exitCode": result,
                "scriptEmittedTaskJson": output.get("taskId") == "task-fast-candidate-1",
                "scriptResolvedTargetParentId": output.get("resolvedTargetParentId") == "115-root",
                "scriptRequiredFastInputs": output.get("requiredFastInputs") == ["sha1", "size"],
                "scriptAutoComputedSha1": bool(source_entry.get("sha1")),
                "scriptHasAutoTempFile": "--auto-temp-file" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasSha1Arg": "--sha1" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasGcidArg": "--gcid" in SCRIPT_PATH.read_text(encoding="utf-8"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
