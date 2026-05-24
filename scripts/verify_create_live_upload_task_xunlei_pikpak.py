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
from cloudpan_sync.xunlei_fast_upload_live import XunleiFastUploadResult
from cloudpan_sync.pikpak_fast_upload_live import PikPakFastUploadResult

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
    upload_mode: str,
    verify_mode: str,
) -> dict[str, object]:
    original_get_profile = live_upload_script.get_profile
    original_refresh_auth_evidence = live_upload_script.refresh_auth_profile_evidence
    original_xunlei_upload = task_runtime.upload_xunlei_fast_file
    original_pikpak_upload = task_runtime.upload_pikpak_fast_file
    refresh_calls: list[dict[str, object]] = []

    evidence_dir = ROOT / "tmp" / f"verify-{provider_key}-live-evidence-bundle"
    _cleanup_dir(evidence_dir)

    def fake_get_profile(current_profile_id: str) -> AuthProfile | None:
        if current_profile_id != profile_id:
            return None
        return AuthProfile(
            profileId=profile_id,
            providerKey=provider_key,
            authMode="manual_token",
            displayName=f"{provider_key}-live",
            token="demo-token",
            cookie="",
            extra={"parentId": "target-root"},
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

    def fake_xunlei_upload(
        *,
        profile_id: str,
        local_path: str,
        target_name: str,
        parent_id: str = "",
        expected_gcid: str = "",
        conflict_policy: str = "auto_rename_new",
    ) -> XunleiFastUploadResult:
        return XunleiFastUploadResult(
            ok=True,
            mode=upload_mode,
            usedProfile=True,
            profileId=profile_id,
            parentId=parent_id or "target-root",
            status=200,
            error="",
            note="xunlei upload ok",
            payload={
                "resolvedTargetName": "cloudpan-sync-live-upload (1).bin",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "fileId": "xunlei-file-1",
            },
            verifyOk=True,
            verifyMode=verify_mode,
            verifyNote="verified",
            verifyPayload={"fileId": "xunlei-file-1"},
        )

    def fake_pikpak_upload(
        *,
        profile_id: str,
        local_path: str,
        target_name: str,
        parent_id: str = "",
        expected_gcid: str = "",
        conflict_policy: str = "auto_rename_new",
    ) -> PikPakFastUploadResult:
        return PikPakFastUploadResult(
            ok=True,
            mode=upload_mode,
            usedProfile=True,
            profileId=profile_id,
            parentId=parent_id or "target-root",
            status=200,
            error="",
            note="pikpak upload ok",
            payload={
                "resolvedTargetName": "cloudpan-sync-live-upload (1).bin",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "fileId": "pikpak-file-1",
            },
            verifyOk=True,
            verifyMode=verify_mode,
            verifyNote="verified",
            verifyPayload={"fileId": "pikpak-file-1"},
        )

    live_upload_script.get_profile = fake_get_profile
    live_upload_script.refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
    task_runtime.upload_xunlei_fast_file = fake_xunlei_upload
    task_runtime.upload_pikpak_fast_file = fake_pikpak_upload
    live_upload_script.task_runtime.upload_xunlei_fast_file = fake_xunlei_upload
    live_upload_script.task_runtime.upload_pikpak_fast_file = fake_pikpak_upload

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
                    "target-root",
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
        task_runtime.upload_xunlei_fast_file = original_xunlei_upload
        task_runtime.upload_pikpak_fast_file = original_pikpak_upload
        live_upload_script.task_runtime.upload_xunlei_fast_file = original_xunlei_upload
        live_upload_script.task_runtime.upload_pikpak_fast_file = original_pikpak_upload

    output = json.loads(stdout_buffer.getvalue())
    task_payload = json.loads((evidence_dir / "task.json").read_text(encoding="utf-8"))
    markdown = (evidence_dir / "task.md").read_text(encoding="utf-8")
    runtime_evidence_markdown = (evidence_dir / "runtime_evidence.md").read_text(encoding="utf-8")
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
        "jsonSavedVerifyMode": (((((task_payload.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyMode")) == verify_mode,
        "markdownHasConflictAction": "conflictAction=`overwrite_downgraded_to_auto_rename`" in markdown,
        "markdownHasResolvedTargetName": "resolvedTargetName=`cloudpan-sync-live-upload (1).bin`" in markdown,
        "runtimeEvidenceHasTitle": "# CloudPan Sync 任务运行真实样本报告" in runtime_evidence_markdown,
    }


def main() -> None:
    print(
        json.dumps(
            {
                "xunlei": _run_case(
                    provider_key="xunlei",
                    profile_id="xunlei-live-1",
                    upload_mode="binary_upload_after_hash_miss",
                    verify_mode="metadata_by_file_id",
                ),
                "pikpak": _run_case(
                    provider_key="pikpak",
                    profile_id="pikpak-live-1",
                    upload_mode="binary_upload_after_hash_miss",
                    verify_mode="metadata_by_file_id",
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
