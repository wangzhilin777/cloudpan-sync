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
    original_refresh_auth_evidence = runtime_probe_script.refresh_auth_profile_evidence
    refresh_calls: list[dict[str, object]] = []

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

    def fake_refresh_auth_profile_evidence(
        *,
        profile: object,
        page_size: int = 100,
        dir_name: str = "",
        persist: bool = True,
        profile_view_builder=None,
    ) -> dict[str, object]:
        refresh_calls.append({"profileId": getattr(profile, "profileId", ""), "persist": persist})
        profile_view = profile_view_builder(profile) if callable(profile_view_builder) else {}
        return {
            "profile": profile_view,
            "latestValidation": {"ok": True, "summary": "validation ok"},
            "latestProbe": {"ok": True, "summary": "probe ok"},
            "summary": {
                "profileReady": bool(profile_view.get("profileReady", True)),
                "writeReady": bool(profile_view.get("writeReady", True)),
                "validationOk": True,
                "probeOk": True,
                "resolvedParentId": str(profile_view.get("resolvedParentId") or ""),
                "resolvedFileId": str(profile_view.get("resolvedFileId") or ""),
            },
        }

    task_runtime.create_task = fake_create_task
    task_runtime.run_task = fake_run_task
    runtime_probe_script.task_runtime.create_task = fake_create_task
    runtime_probe_script.task_runtime.run_task = fake_run_task
    runtime_probe_script.get_profile = fake_get_profile
    runtime_probe_script.refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
    try:
        evidence_dir = ROOT / "tmp" / "verify-runtime-probe-evidence"
        if evidence_dir.exists():
            for child in evidence_dir.iterdir():
                if child.is_file():
                    child.unlink()
            evidence_dir.rmdir()
        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            result = runtime_probe_script.main(
                [
                    "--target-provider",
                    "aliyundrive_open",
                    "--target-profile-id",
                    "ali-runtime-1",
                    "--auto-temp-file",
                    "--evidence-dir",
                    str(evidence_dir),
                ]
            )
    finally:
        task_runtime.create_task = original_create_task
        task_runtime.run_task = original_run_task
        runtime_probe_script.task_runtime.create_task = original_create_task
        runtime_probe_script.task_runtime.run_task = original_run_task
        runtime_probe_script.get_profile = original_get_profile
        runtime_probe_script.refresh_auth_profile_evidence = original_refresh_auth_evidence

    output = json.loads(stdout_buffer.getvalue())
    task_json = evidence_dir / "task.json"
    task_markdown = evidence_dir / "task.md"
    auth_evidence = evidence_dir / "auth_evidence.md"
    runtime_evidence = evidence_dir / "runtime_evidence.md"
    real_evidence = evidence_dir / "real_evidence.md"
    remediation = evidence_dir / "remediation.md"
    evidence_titles_ok = all(
        [
            task_json.exists(),
            task_markdown.exists(),
            auth_evidence.exists(),
            runtime_evidence.exists(),
            real_evidence.exists(),
            remediation.exists(),
        ]
    )
    if evidence_dir.exists():
        for child in evidence_dir.iterdir():
            if child.is_file():
                child.unlink()
        evidence_dir.rmdir()

    print(
        json.dumps(
            {
                "exitCode": result,
                "scriptEmittedTaskJson": output.get("taskId") == "task-runtime-1",
                "scriptResolvedTargetParentId": output.get("resolvedTargetParentId") == "folder-demo",
                "scriptEvidenceDirOutput": output.get("evidenceDir") == str(evidence_dir),
                "scriptAuthEvidenceRefreshed": len(refresh_calls) == 1 and refresh_calls[0].get("profileId") == "ali-runtime-1",
                "scriptEvidenceBundleCreated": evidence_titles_ok,
                "scriptHasAutoTempFile": "--auto-temp-file" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasThresholdDefault": "--threshold-mb" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasTargetProfileArg": "--target-profile-id" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasEvidenceDirArg": "--evidence-dir" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptProbeOnlyState": output.get("state") == "completed_probe_only" and ((output.get("summary") or {}).get("completionKind") == "probe_only"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
