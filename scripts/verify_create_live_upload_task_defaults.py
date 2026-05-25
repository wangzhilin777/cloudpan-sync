from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import task_runtime
from cloudpan_sync.guangya_upload_live import GuangyaUploadResult
from cloudpan_sync.models import AuthProfile

SCRIPT_PATH = ROOT / "scripts" / "create_live_upload_task.py"
SPEC = importlib.util.spec_from_file_location("create_live_upload_task", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
live_upload_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(live_upload_script)


def main() -> None:
    original_get_profile = live_upload_script.get_profile
    original_refresh_auth_evidence = live_upload_script.refresh_auth_profile_evidence
    original_remediation_builder = live_upload_script.build_real_evidence_remediation_bundle
    original_fast_check = task_runtime.fetch_guangya_live_fast_check
    original_upload = task_runtime.upload_guangya_local_file
    create_payloads: list[dict[str, object]] = []

    def fake_get_profile(profile_id: str) -> AuthProfile | None:
        if profile_id != "gy-live-defaults-1":
            return None
        return AuthProfile(
            profileId="gy-live-defaults-1",
            providerKey="guangya",
            authMode="manual_token",
            displayName="gy-live-defaults",
            token="demo-token",
            cookie="",
            extra={"parentId": "folder-live-default"},
            status="saved",
            lastError="",
            createdAt="2026-05-26T00:00:00+00:00",
            updatedAt="2026-05-26T00:00:00+00:00",
        )

    class _FastCheckResult:
        ok = True
        note = "no inventory hit"
        error = ""
        riskHint = ""
        items = [
            {
                "path": "/cloudpan-sync-live-upload.bin",
                "canFastUpload": False,
                "hashKind": "md5",
                "note": "no instant hit",
                "error": "",
                "riskHint": "",
            }
        ]

    def fake_fast_check(profile_id: str, entries: list[object], parent_id: str = "") -> object:
        return _FastCheckResult()

    def fake_upload(
        profile_id: str,
        local_path: str,
        target_name: str,
        parent_id: str = "",
        expected_md5: str = "",
        conflict_policy: str = "auto_rename_new",
    ) -> GuangyaUploadResult:
        create_payloads.append(
            {
                "profileId": profile_id,
                "parentId": parent_id,
                "targetName": target_name,
                "localPath": local_path,
                "conflictPolicy": conflict_policy,
            }
        )
        return GuangyaUploadResult(
            ok=True,
            mode="binary_upload_multipart",
            usedProfile=True,
            profileId=profile_id,
            parentId=parent_id or "folder-live-default",
            status=200,
            error="",
            note="upload ok",
            riskHint="",
            payload={
                "resolvedTargetName": "cloudpan-sync-live-upload.bin",
                "conflictAction": "auto_rename_new",
                "fileId": "file-live-default-1",
            },
            verifyOk=True,
            verifyMode="list_by_parent_name",
            verifyNote="verified by list",
            verifyPayload={"matchedItem": {"name": "cloudpan-sync-live-upload.bin"}},
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

    live_upload_script.get_profile = fake_get_profile
    live_upload_script.refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
    live_upload_script.build_real_evidence_remediation_bundle = lambda: {
        "summary": {},
        "items": [
            {
                "providerKey": "guangya",
                "profileIds": ["gy-live-defaults-1"],
                "recommendedLiveUploadCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-live-defaults-1 --target-parent-id folder-live-default --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-live-defaults-1 --target-parent-id folder-live-default --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence",
            }
        ],
    }
    task_runtime.fetch_guangya_live_fast_check = fake_fast_check
    task_runtime.upload_guangya_local_file = fake_upload
    live_upload_script.task_runtime.fetch_guangya_live_fast_check = fake_fast_check
    live_upload_script.task_runtime.upload_guangya_local_file = fake_upload

    try:
        first_stdout = io.StringIO()
        with contextlib.redirect_stdout(first_stdout):
            first_result = live_upload_script.main(
                [
                    "--from-remediation-provider",
                    "guangya",
                ]
            )

        second_stdout = io.StringIO()
        with contextlib.redirect_stdout(second_stdout):
            second_result = live_upload_script.main(
                [
                    "--from-remediation-provider",
                    "guangya",
                    "--target-parent-id",
                    "manual-live-parent",
                    "--conflict-policy",
                    "overwrite_existing",
                    "--no-acknowledge-download-upload",
                ]
            )

        missing_target_error = ""
        try:
            live_upload_script.main(["--from-remediation-provider", "missing-provider"])
        except SystemExit as exc:
            missing_target_error = str(exc)
    finally:
        live_upload_script.get_profile = original_get_profile
        live_upload_script.refresh_auth_profile_evidence = original_refresh_auth_evidence
        live_upload_script.build_real_evidence_remediation_bundle = original_remediation_builder
        task_runtime.fetch_guangya_live_fast_check = original_fast_check
        task_runtime.upload_guangya_local_file = original_upload
        live_upload_script.task_runtime.fetch_guangya_live_fast_check = original_fast_check
        live_upload_script.task_runtime.upload_guangya_local_file = original_upload

    first_output = json.loads(first_stdout.getvalue())
    second_output = json.loads(second_stdout.getvalue())
    first_call = create_payloads[0] if len(create_payloads) >= 1 else {}
    second_call = create_payloads[1] if len(create_payloads) >= 2 else {}
    first_evidence_dir_relative = Path(r"tmp\guangya-live-evidence")
    first_evidence_dir = ROOT / "tmp" / "guangya-live-evidence"
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
                "defaultsSourceApplied": first_output.get("defaultsSource") == "remediation:recommendedLiveUploadCommand",
                "defaultTargetResolved": first_output.get("targetProvider") == "guangya" and first_output.get("targetProfileId") == "gy-live-defaults-1",
                "defaultParentResolved": first_output.get("resolvedTargetParentId") == "folder-live-default" and first_call.get("parentId") == "folder-live-default",
                "defaultAutoTempAndEvidenceDirApplied": first_output.get("usedTempFile") is True
                and Path(str(first_output.get("evidenceDir") or "")) == first_evidence_dir_relative
                and first_bundle_ok,
                "defaultThresholdAndConflictApplied": first_call.get("conflictPolicy") == "auto_rename_new",
                "defaultAcknowledgeApplied": first_output.get("acknowledgedDownloadUpload") is True,
                "explicitOverrideStillWins": second_output.get("resolvedTargetParentId") == "manual-live-parent"
                and second_output.get("acknowledgedDownloadUpload") is False
                and ((second_output.get("summary") or {}).get("awaitingAcknowledgement")) is True,
                "sourceProviderFallsBackToGuangya": first_output.get("targetProvider") == "guangya",
                "missingProviderStillNeedsTargetProfile": missing_target_error == "target_profile_id_required",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
