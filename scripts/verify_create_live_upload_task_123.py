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
from cloudpan_sync.pan123_open_upload_live import Pan123OpenUploadResult

SCRIPT_PATH = ROOT / "scripts" / "create_live_upload_task.py"
SPEC = importlib.util.spec_from_file_location("create_live_upload_task", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
live_upload_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(live_upload_script)


def main() -> None:
    original_get_profile = live_upload_script.get_profile
    original_refresh_auth_evidence = live_upload_script.refresh_auth_profile_evidence
    original_upload = task_runtime.upload_123_open_local_file
    refresh_calls: list[dict[str, object]] = []

    evidence_dir = ROOT / "tmp" / "verify-123-live-evidence-bundle"
    if evidence_dir.exists():
        for child in evidence_dir.iterdir():
            if child.is_file():
                child.unlink()
        evidence_dir.rmdir()

    def fake_get_profile(profile_id: str) -> AuthProfile | None:
        if profile_id != "123-live-1":
            return None
        return AuthProfile(
            profileId="123-live-1",
            providerKey="123_open",
            authMode="manual_token",
            displayName="123-live",
            token="demo-token",
            cookie="",
            extra={"parentFileId": "0"},
            status="saved",
            lastError="",
            createdAt="2026-05-25T00:00:00+00:00",
            updatedAt="2026-05-25T00:00:00+00:00",
        )

    def fake_upload(
        profile_id: str,
        local_path: str,
        target_name: str,
        parent_file_id: str = "0",
        expected_md5: str = "",
        conflict_policy: str = "auto_rename_new",
    ) -> Pan123OpenUploadResult:
        return Pan123OpenUploadResult(
            ok=True,
            mode="binary_upload_single_part",
            usedProfile=True,
            profileId=profile_id,
            parentId=parent_file_id or "0",
            status=200,
            error="",
            note="123 upload ok",
            riskHint="",
            payload={
                "resolvedTargetName": "cloudpan-sync-live-upload (1).bin",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "fileId": "123-file-1",
            },
            verifyOk=True,
            verifyMode="metadata_by_file_id",
            verifyNote="verified by metadata",
            verifyPayload={"fileId": "123-file-1"},
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

    live_upload_script.get_profile = fake_get_profile
    live_upload_script.refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
    task_runtime.upload_123_open_local_file = fake_upload
    live_upload_script.task_runtime.upload_123_open_local_file = fake_upload

    try:
        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            result = live_upload_script.main(
                [
                    "--target-provider",
                    "123_open",
                    "--target-profile-id",
                    "123-live-1",
                    "--target-parent-id",
                    "0",
                    "--source-provider",
                    "quark",
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
        task_runtime.upload_123_open_local_file = original_upload
        live_upload_script.task_runtime.upload_123_open_local_file = original_upload

    output = json.loads(stdout_buffer.getvalue())
    task_json = evidence_dir / "task.json"
    task_markdown = evidence_dir / "task.md"
    runtime_evidence = evidence_dir / "runtime_evidence.md"
    task_payload = json.loads(task_json.read_text(encoding="utf-8"))
    markdown = task_markdown.read_text(encoding="utf-8")
    runtime_evidence_markdown = runtime_evidence.read_text(encoding="utf-8")

    for path in evidence_dir.iterdir():
        if path.is_file():
            path.unlink()
    evidence_dir.rmdir()

    print(
        json.dumps(
            {
                "exitCode": result,
                "stateCompleted": output.get("state") == "completed",
                "hasRealTransferSuccess": ((output.get("summary") or {}).get("hasRealTransferSuccess")) is True,
                "completionKind": ((output.get("summary") or {}).get("completionKind")) == "real_transfer",
                "firstResultLive": ((((output.get("results") or [None])[0]) or {}).get("executionMode")) == "live",
                "firstResultVerifyOk": bool((((((output.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyOk"))),
                "authEvidenceRefreshed": len(refresh_calls) == 1 and refresh_calls[0].get("profileId") == "123-live-1",
                "jsonSavedState": task_payload.get("state") == "completed",
                "jsonSavedVerifyMode": (((((task_payload.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyMode")) == "metadata_by_file_id",
                "markdownHasConflictAction": "conflictAction=`overwrite_downgraded_to_auto_rename`" in markdown,
                "markdownHasResolvedTargetName": "resolvedTargetName=`cloudpan-sync-live-upload (1).bin`" in markdown,
                "runtimeEvidenceHasTitle": "# CloudPan Sync 任务运行真实样本报告" in runtime_evidence_markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
