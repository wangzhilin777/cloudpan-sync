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

SCRIPT_PATH = ROOT / "scripts" / "create_runtime_probe_task.py"
SPEC = importlib.util.spec_from_file_location("create_runtime_probe_task", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
runtime_probe_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime_probe_script)


def main() -> None:
    original_create_task = task_runtime.create_task
    original_run_task = task_runtime.run_task
    original_get_profile = runtime_probe_script.get_profile

    def fake_create_task(payload: object) -> dict[str, object]:
        return {
            "taskId": "task-runtime-1",
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
            "state": "completed_probe_only",
            "targetProvider": "aliyundrive_open",
            "targetProfileId": "ali-runtime-1",
            "sourceEntries": [
                {
                    "path": "/cloudpan-sync-runtime-probe.bin",
                    "size": 16,
                    "localPath": "temp.bin",
                }
            ],
            "results": [
                {
                    "path": "/cloudpan-sync-runtime-probe.bin",
                    "status": "done",
                    "executionMode": "probe",
                    "liveAttempt": {"mode": "aliyundrive_open_create_dir_probe"},
                }
            ],
            "summary": {"state": "completed_probe_only", "completionKind": "probe_only", "probeOnlyCount": 1},
        }

    def fake_get_profile(profile_id: str) -> AuthProfile | None:
        if profile_id != "ali-runtime-1":
            return None
        return AuthProfile(
            profileId="ali-runtime-1",
            providerKey="aliyundrive_open",
            authMode="manual_token",
            displayName="ali-runtime",
            token="ali-token",
            cookie="",
            extra={"parentFileId": "folder-demo", "domainId": "domain-demo", "driveId": "drive-demo"},
            status="saved",
            lastError="",
            createdAt="2026-05-25T00:00:00+00:00",
            updatedAt="2026-05-25T00:00:00+00:00",
        )

    task_runtime.create_task = fake_create_task
    task_runtime.run_task = fake_run_task
    runtime_probe_script.task_runtime.create_task = fake_create_task
    runtime_probe_script.task_runtime.run_task = fake_run_task
    runtime_probe_script.get_profile = fake_get_profile
    try:
        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            result = runtime_probe_script.main(
                [
                    "--target-provider",
                    "aliyundrive_open",
                    "--target-profile-id",
                    "ali-runtime-1",
                    "--auto-temp-file",
                ]
            )
    finally:
        task_runtime.create_task = original_create_task
        task_runtime.run_task = original_run_task
        runtime_probe_script.task_runtime.create_task = original_create_task
        runtime_probe_script.task_runtime.run_task = original_run_task
        runtime_probe_script.get_profile = original_get_profile

    output = json.loads(stdout_buffer.getvalue())

    print(
        json.dumps(
            {
                "exitCode": result,
                "scriptEmittedTaskJson": output.get("taskId") == "task-runtime-1",
                "scriptResolvedTargetParentId": output.get("resolvedTargetParentId") == "folder-demo",
                "scriptHasAutoTempFile": "--auto-temp-file" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasThresholdDefault": "--threshold-mb" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasTargetProfileArg": "--target-profile-id" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptProbeOnlyState": output.get("state") == "completed_probe_only" and ((output.get("summary") or {}).get("completionKind") == "probe_only"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
