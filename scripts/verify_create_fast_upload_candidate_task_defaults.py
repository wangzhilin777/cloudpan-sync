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
    original_refresh_auth_evidence = fast_candidate_script.refresh_auth_profile_evidence
    original_remediation_builder = fast_candidate_script.build_real_evidence_remediation_bundle
    create_payloads: list[dict[str, object]] = []

    def fake_create_task(payload: object) -> dict[str, object]:
        create_payloads.append(
            {
                "sourceProvider": getattr(payload, "sourceProvider", ""),
                "targetProvider": getattr(payload, "targetProvider", ""),
                "targetProfileId": getattr(payload, "targetProfileId", ""),
                "targetParentId": getattr(payload, "targetParentId", ""),
                "conflictPolicy": getattr(payload, "conflictPolicy", ""),
                "sourceEntries": [entry.model_dump() for entry in getattr(payload, "entries", [])],
            }
        )
        return {
            "taskId": "task-fast-defaults-1",
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
            "state": "completed_candidate_only",
            "targetProvider": "115_open",
            "targetProfileId": "115-fast-defaults-1",
            "sourceEntries": [
                {
                    "path": "/cloudpan-sync-fast-candidate.bin",
                    "size": 28,
                    "sha1": "96b06f478886641050f54f5504c05dbf1e0f0711",
                    "localPath": "temp-default.bin",
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
            "summary": {"state": "completed_candidate_only", "completionKind": "candidate_only", "candidateOnlyCount": 1},
        }

    def fake_get_profile(profile_id: str) -> AuthProfile | None:
        if profile_id != "115-fast-defaults-1":
            return None
        return AuthProfile(
            profileId="115-fast-defaults-1",
            providerKey="115_open",
            authMode="manual_cookie",
            displayName="115-fast-defaults",
            token="",
            cookie="UID=1; CID=2",
            extra={"cid": "115-root-default"},
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
    fast_candidate_script.task_runtime.create_task = fake_create_task
    fast_candidate_script.task_runtime.run_task = fake_run_task
    fast_candidate_script.get_profile = fake_get_profile
    fast_candidate_script.refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
    fast_candidate_script.build_real_evidence_remediation_bundle = lambda: {
        "summary": {},
        "items": [
            {
                "providerKey": "115_open",
                "profileIds": ["115-fast-defaults-1"],
                "recommendedFastCandidateCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-fast-defaults-1 --target-parent-id 115-root-default --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-fast-candidate-evidence",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-fast-defaults-1 --target-parent-id 115-root-default --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-fast-candidate-evidence",
            }
        ],
    }
    try:
        first_stdout = io.StringIO()
        with contextlib.redirect_stdout(first_stdout):
            first_result = fast_candidate_script.main(
                [
                    "--from-remediation-provider",
                    "115_open",
                ]
            )

        second_stdout = io.StringIO()
        with contextlib.redirect_stdout(second_stdout):
            second_result = fast_candidate_script.main(
                [
                    "--from-remediation-provider",
                    "115_open",
                    "--target-parent-id",
                    "manual-fast-parent",
                    "--conflict-policy",
                    "overwrite_existing",
                    "--sha1",
                    "manual-sha1",
                ]
            )

        missing_target_error = ""
        try:
            fast_candidate_script.main(["--from-remediation-provider", "missing-provider"])
        except SystemExit as exc:
            missing_target_error = str(exc)
    finally:
        task_runtime.create_task = original_create_task
        task_runtime.run_task = original_run_task
        fast_candidate_script.task_runtime.create_task = original_create_task
        fast_candidate_script.task_runtime.run_task = original_run_task
        fast_candidate_script.get_profile = original_get_profile
        fast_candidate_script.refresh_auth_profile_evidence = original_refresh_auth_evidence
        fast_candidate_script.build_real_evidence_remediation_bundle = original_remediation_builder

    first_output = json.loads(first_stdout.getvalue())
    second_output = json.loads(second_stdout.getvalue())
    first_payload = create_payloads[0] if len(create_payloads) >= 1 else {}
    second_payload = create_payloads[1] if len(create_payloads) >= 2 else {}
    first_entry = (first_payload.get("sourceEntries") or [{}])[0] if (first_payload.get("sourceEntries") or []) else {}
    second_entry = (second_payload.get("sourceEntries") or [{}])[0] if (second_payload.get("sourceEntries") or []) else {}
    first_evidence_dir_relative = Path(r"tmp\115_open-fast-candidate-evidence")
    first_evidence_dir = ROOT / "tmp" / "115_open-fast-candidate-evidence"
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
                "defaultsSourceApplied": first_output.get("defaultsSource") == "remediation:recommendedFastCandidateCommand",
                "defaultTargetResolved": first_output.get("targetProvider") == "115_open" and first_output.get("targetProfileId") == "115-fast-defaults-1",
                "defaultParentResolved": first_output.get("resolvedTargetParentId") == "115-root-default" and first_payload.get("targetParentId") == "115-root-default",
                "defaultAutoTempAndEvidenceDirApplied": first_output.get("usedTempFile") is True
                and Path(str(first_output.get("evidenceDir") or "")) == first_evidence_dir_relative
                and first_bundle_ok,
                "defaultSha1Applied": str(first_entry.get("sha1") or "").strip() != "",
                "defaultConflictApplied": first_payload.get("conflictPolicy") == "auto_rename_new",
                "explicitOverrideStillWins": second_output.get("resolvedTargetParentId") == "manual-fast-parent"
                and second_payload.get("targetParentId") == "manual-fast-parent"
                and second_payload.get("conflictPolicy") == "overwrite_existing"
                and second_entry.get("sha1") == "manual-sha1",
                "sourceProviderFallsBackToTarget": first_payload.get("sourceProvider") == "115_open",
                "missingProviderStillNeedsTargets": missing_target_error == "target_provider_required",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
