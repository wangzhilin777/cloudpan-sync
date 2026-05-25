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
    original_remediation_builder = runtime_probe_script.build_real_evidence_remediation_bundle
    create_payloads: list[dict[str, object]] = []

    def fake_create_task(payload: object) -> dict[str, object]:
        create_payloads.append(
            {
                "sourceProvider": getattr(payload, "sourceProvider", ""),
                "targetProvider": getattr(payload, "targetProvider", ""),
                "targetProfileId": getattr(payload, "targetProfileId", ""),
                "targetParentId": getattr(payload, "targetParentId", ""),
                "thresholdMB": getattr(payload, "thresholdMB", 0),
                "conflictPolicy": getattr(payload, "conflictPolicy", ""),
                "sourceEntries": [entry.model_dump() for entry in getattr(payload, "entries", [])],
            }
        )
        return {
            "taskId": "task-runtime-defaults-1",
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
            "targetProfileId": "ali-runtime-defaults-1",
            "sourceEntries": [
                {
                    "path": "/probe-default.bin",
                    "size": 16,
                    "localPath": "temp-default.bin",
                }
            ],
            "results": [
                {
                    "path": "/probe-default.bin",
                    "status": "done",
                    "executionMode": "probe",
                    "liveAttempt": {"mode": "aliyundrive_open_create_dir_probe"},
                }
            ],
            "summary": {"state": "completed_probe_only", "completionKind": "probe_only", "probeOnlyCount": 1},
        }

    def fake_get_profile(profile_id: str) -> AuthProfile | None:
        if profile_id != "ali-runtime-defaults-1":
            return None
        return AuthProfile(
            profileId="ali-runtime-defaults-1",
            providerKey="aliyundrive_open",
            authMode="manual_token",
            displayName="ali-runtime-defaults",
            token="ali-token",
            cookie="",
            extra={"parentFileId": "folder-default", "domainId": "domain-default", "driveId": "drive-default"},
            status="saved",
            lastError="",
            createdAt="2026-05-26T00:00:00+00:00",
            updatedAt="2026-05-26T00:00:00+00:00",
        )

    def fake_refresh_auth_profile_evidence(
        *,
        profile: object,
        page_size: int = 100,
        dir_name: str = "",
        persist: bool = True,
        profile_view_builder=None,
    ) -> dict[str, object]:
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
    runtime_probe_script.build_real_evidence_remediation_bundle = lambda: {
        "summary": {},
        "items": [
            {
                "providerKey": "aliyundrive_open",
                "profileIds": ["ali-runtime-defaults-1"],
                "recommendedRuntimeProbeCommand": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --target-provider aliyundrive_open --target-profile-id ali-runtime-defaults-1 --target-parent-id folder-default --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\aliyundrive_open-runtime-probe-evidence",
            }
        ],
    }
    try:
        default_stdout = io.StringIO()
        with contextlib.redirect_stdout(default_stdout):
            first_result = runtime_probe_script.main(
                [
                    "--from-remediation-provider",
                    "aliyundrive_open",
                ]
            )

        explicit_stdout = io.StringIO()
        with contextlib.redirect_stdout(explicit_stdout):
            second_result = runtime_probe_script.main(
                [
                    "--from-remediation-provider",
                    "aliyundrive_open",
                    "--target-parent-id",
                    "manual-parent",
                    "--conflict-policy",
                    "overwrite_existing",
                ]
            )

        missing_target_error = ""
        try:
            runtime_probe_script.main(["--from-remediation-provider", "missing-provider"])
        except SystemExit as exc:
            missing_target_error = str(exc)
    finally:
        task_runtime.create_task = original_create_task
        task_runtime.run_task = original_run_task
        runtime_probe_script.task_runtime.create_task = original_create_task
        runtime_probe_script.task_runtime.run_task = original_run_task
        runtime_probe_script.get_profile = original_get_profile
        runtime_probe_script.refresh_auth_profile_evidence = original_refresh_auth_evidence
        runtime_probe_script.build_real_evidence_remediation_bundle = original_remediation_builder

    first_output = json.loads(default_stdout.getvalue())
    second_output = json.loads(explicit_stdout.getvalue())
    first_payload = create_payloads[0] if len(create_payloads) >= 1 else {}
    second_payload = create_payloads[1] if len(create_payloads) >= 2 else {}
    first_evidence_dir_relative = Path(r"tmp\aliyundrive_open-runtime-probe-evidence")
    first_evidence_dir = ROOT / "tmp" / "aliyundrive_open-runtime-probe-evidence"
    first_bundle_ok = all(
        [
            (first_evidence_dir / "task.json").exists(),
            (first_evidence_dir / "task.md").exists(),
            (first_evidence_dir / "auth_evidence.md").exists(),
            (first_evidence_dir / "runtime_evidence.md").exists(),
            (first_evidence_dir / "real_evidence.md").exists(),
            (first_evidence_dir / "remediation.md").exists(),
        ]
    )
    if first_evidence_dir.exists():
        for child in first_evidence_dir.iterdir():
            if child.is_file():
                child.unlink()
        first_evidence_dir.rmdir()

    print(
        json.dumps(
            {
                "firstExitCode": first_result,
                "secondExitCode": second_result,
                "defaultsSourceApplied": first_output.get("defaultsSource") == "remediation:recommendedRuntimeProbeCommand",
                "defaultTargetResolved": first_output.get("targetProvider") == "aliyundrive_open" and first_output.get("targetProfileId") == "ali-runtime-defaults-1",
                "defaultParentResolved": first_output.get("resolvedTargetParentId") == "folder-default" and first_payload.get("targetParentId") == "folder-default",
                "defaultAutoTempAndEvidenceDirApplied": first_output.get("usedTempFile") is True
                and Path(str(first_output.get("evidenceDir") or "")) == first_evidence_dir_relative
                and first_bundle_ok,
                "defaultThresholdAndConflictApplied": first_payload.get("thresholdMB") == 1 and first_payload.get("conflictPolicy") == "auto_rename_new",
                "explicitOverrideStillWins": second_output.get("resolvedTargetParentId") == "manual-parent"
                and second_payload.get("targetParentId") == "manual-parent"
                and second_payload.get("conflictPolicy") == "overwrite_existing",
                "sourceProviderFallsBackToTarget": first_payload.get("sourceProvider") == "aliyundrive_open",
                "missingProviderStillNeedsTargets": missing_target_error == "target_provider_required",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
