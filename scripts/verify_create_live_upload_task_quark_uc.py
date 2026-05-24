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
from cloudpan_sync.models import AuthProfile
from cloudpan_sync.quark_fast_upload_live import QuarkFastUploadResult
from cloudpan_sync.uc_fast_upload_live import UcFastUploadResult

SCRIPT_PATH = ROOT / "scripts" / "create_live_upload_task.py"
SPEC = importlib.util.spec_from_file_location("create_live_upload_task", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
live_upload_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(live_upload_script)


def _cleanup_dir(path: Path) -> None:
    if not path.exists():
        return
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
    path.rmdir()


def _run_case(
    *,
    provider_key: str,
    profile_id: str,
) -> dict[str, object]:
    original_get_profile = live_upload_script.get_profile
    original_refresh_auth_evidence = live_upload_script.refresh_auth_profile_evidence
    original_quark_upload = task_runtime.upload_quark_fast_file
    original_uc_upload = task_runtime.upload_uc_fast_file
    refresh_calls: list[dict[str, object]] = []

    evidence_dir = ROOT / "tmp" / f"verify-{provider_key}-live-evidence-bundle"
    _cleanup_dir(evidence_dir)

    def fake_get_profile(current_profile_id: str) -> AuthProfile | None:
        if current_profile_id != profile_id:
            return None
        return AuthProfile(
            profileId=profile_id,
            providerKey=provider_key,
            authMode="manual_cookie",
            displayName=f"{provider_key}-live",
            token="",
            cookie="sid=demo",
            extra={"parentId": "0", "pwdId": "share-demo"},
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

    def fake_quark_upload(
        *,
        profile_id: str,
        local_path: str,
        target_name: str,
        parent_id: str = "0",
        expected_md5: str = "",
        expected_sha1: str = "",
        conflict_policy: str = "auto_rename_new",
    ) -> QuarkFastUploadResult:
        return QuarkFastUploadResult(
            ok=True,
            mode="binary_upload_after_hash_miss",
            usedProfile=True,
            profileId=profile_id,
            parentId=parent_id or "0",
            status=200,
            error="",
            note="quark upload ok",
            payload={
                "resolvedTargetName": "cloudpan-sync-live-upload (1).bin",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "fileId": "quark-file-1",
            },
            verifyOk=True,
            verifyMode="finish_response",
            verifyNote="verified",
            verifyPayload={"fileId": "quark-file-1"},
        )

    def fake_uc_upload(
        *,
        profile_id: str,
        local_path: str,
        target_name: str,
        parent_id: str = "0",
        expected_md5: str = "",
        expected_sha1: str = "",
        conflict_policy: str = "auto_rename_new",
    ) -> UcFastUploadResult:
        return UcFastUploadResult(
            ok=True,
            mode="binary_upload_after_hash_miss",
            usedProfile=True,
            profileId=profile_id,
            parentId=parent_id or "0",
            status=200,
            error="",
            note="uc upload ok",
            payload={
                "resolvedTargetName": "cloudpan-sync-live-upload (1).bin",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "fileId": "uc-file-1",
            },
            verifyOk=True,
            verifyMode="finish_response",
            verifyNote="verified",
            verifyPayload={"fileId": "uc-file-1"},
        )

    live_upload_script.get_profile = fake_get_profile
    live_upload_script.refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
    task_runtime.upload_quark_fast_file = fake_quark_upload
    task_runtime.upload_uc_fast_file = fake_uc_upload
    live_upload_script.task_runtime.upload_quark_fast_file = fake_quark_upload
    live_upload_script.task_runtime.upload_uc_fast_file = fake_uc_upload

    try:
        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            result = live_upload_script.main(
                [
                    "--target-provider",
                    provider_key,
                    "--target-profile-id",
                    profile_id,
                    "--target-parent-id",
                    "0",
                    "--source-provider",
                    "baidu_netdisk",
                    "--auto-temp-file",
                    "--conflict-policy",
                    "overwrite_existing",
                    "--evidence-dir",
                    str(evidence_dir),
                ]
            )
    finally:
        live_upload_script.get_profile = original_get_profile
        live_upload_script.refresh_auth_profile_evidence = original_refresh_auth_evidence
        task_runtime.upload_quark_fast_file = original_quark_upload
        task_runtime.upload_uc_fast_file = original_uc_upload
        live_upload_script.task_runtime.upload_quark_fast_file = original_quark_upload
        live_upload_script.task_runtime.upload_uc_fast_file = original_uc_upload

    output = json.loads(stdout_buffer.getvalue())
    task_payload = json.loads((evidence_dir / "task.json").read_text(encoding="utf-8"))
    markdown = (evidence_dir / "task.md").read_text(encoding="utf-8")
    auth_evidence_markdown = (evidence_dir / "auth_evidence.md").read_text(encoding="utf-8")
    runtime_evidence_markdown = (evidence_dir / "runtime_evidence.md").read_text(encoding="utf-8")
    real_evidence_markdown = (evidence_dir / "real_evidence.md").read_text(encoding="utf-8")
    remediation_markdown = (evidence_dir / "remediation.md").read_text(encoding="utf-8")
    bundle_uses_fixed_filenames = all(
        (evidence_dir / name).exists()
        for name in (
            "task.json",
            "task.md",
            "auth_evidence.md",
            "runtime_evidence.md",
            "real_evidence.md",
            "remediation.md",
        )
    )
    _cleanup_dir(evidence_dir)

    return {
        "exitCode": result,
        "stateCompleted": output.get("state") == "completed",
        "hasRealTransferSuccess": ((output.get("summary") or {}).get("hasRealTransferSuccess")) is True,
        "completionKind": ((output.get("summary") or {}).get("completionKind")) == "real_transfer",
        "firstResultLive": ((((output.get("results") or [None])[0]) or {}).get("executionMode")) == "live",
        "firstResultVerifyOk": bool((((((output.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyOk"))),
        "authEvidenceRefreshed": len(refresh_calls) == 1 and refresh_calls[0].get("profileId") == profile_id,
        "jsonSavedState": task_payload.get("state") == "completed",
        "jsonSavedVerifyMode": (((((task_payload.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyMode")) == "finish_response",
        "markdownHasConflictAction": "conflictAction=`overwrite_downgraded_to_auto_rename`" in markdown,
        "markdownHasResolvedTargetName": "resolvedTargetName=`cloudpan-sync-live-upload (1).bin`" in markdown,
        "authEvidenceHasTitle": "# Auth Profile Evidence" in auth_evidence_markdown,
        "runtimeEvidenceHasTitle": "# CloudPan Sync 任务运行真实样本报告" in runtime_evidence_markdown,
        "realEvidenceHasTitle": "# CloudPan Sync 真实证据状态报告" in real_evidence_markdown,
        "remediationHasTitle": "# CloudPan Sync 真实联调补救指南" in remediation_markdown,
        "bundleUsesFixedFilenames": bundle_uses_fixed_filenames,
    }


def main() -> None:
    print(
        json.dumps(
            {
                "quark": _run_case(provider_key="quark", profile_id="quark-live-1"),
                "uc": _run_case(provider_key="uc", profile_id="uc-live-1"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
