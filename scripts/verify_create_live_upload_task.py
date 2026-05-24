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
    original_fast_check = task_runtime.fetch_guangya_live_fast_check
    original_upload = task_runtime.upload_guangya_local_file

    task_json = ROOT / "tmp" / "verify-live-upload-task.json"
    task_markdown = ROOT / "tmp" / "verify-live-upload-task.md"
    auth_evidence = ROOT / "tmp" / "verify-live-auth-evidence.md"
    runtime_evidence = ROOT / "tmp" / "verify-live-runtime-evidence.md"
    real_evidence = ROOT / "tmp" / "verify-live-real-evidence.md"
    remediation = ROOT / "tmp" / "verify-live-remediation.md"
    for path in (task_json, task_markdown, auth_evidence, runtime_evidence, real_evidence, remediation):
        if path.exists():
            path.unlink()

    def fake_get_profile(profile_id: str) -> AuthProfile | None:
        if profile_id != "gy-live-1":
            return None
        return AuthProfile(
            profileId="gy-live-1",
            providerKey="guangya",
            authMode="manual_token",
            displayName="gy-live",
            token="demo-token",
            cookie="",
            extra={"parentId": "folder-live-1"},
            status="saved",
            lastError="",
            createdAt="2026-05-25T00:00:00+00:00",
            updatedAt="2026-05-25T00:00:00+00:00",
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
        return GuangyaUploadResult(
            ok=True,
            mode="binary_upload_multipart",
            usedProfile=True,
            profileId=profile_id,
            parentId=parent_id or "folder-live-1",
            status=200,
            error="",
            note="upload ok",
            riskHint="",
            payload={
                "resolvedTargetName": "cloudpan-sync-live-upload (1).bin",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "fileId": "file-live-1",
            },
            verifyOk=True,
            verifyMode="list_by_parent_name",
            verifyNote="verified by list",
            verifyPayload={"matchedItem": {"name": "cloudpan-sync-live-upload (1).bin"}},
        )

    live_upload_script.get_profile = fake_get_profile
    task_runtime.fetch_guangya_live_fast_check = fake_fast_check
    task_runtime.upload_guangya_local_file = fake_upload
    live_upload_script.task_runtime.fetch_guangya_live_fast_check = fake_fast_check
    live_upload_script.task_runtime.upload_guangya_local_file = fake_upload

    try:
        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            result = live_upload_script.main(
                [
                    "--target-profile-id",
                    "gy-live-1",
                    "--auto-temp-file",
                    "--conflict-policy",
                    "overwrite_existing",
                    "--task-json-output",
                    str(task_json),
                    "--markdown-output",
                    str(task_markdown),
                    "--auth-evidence-output",
                    str(auth_evidence),
                    "--runtime-evidence-output",
                    str(runtime_evidence),
                    "--real-evidence-output",
                    str(real_evidence),
                    "--remediation-output",
                    str(remediation),
                ]
            )
    finally:
        live_upload_script.get_profile = original_get_profile
        task_runtime.fetch_guangya_live_fast_check = original_fast_check
        task_runtime.upload_guangya_local_file = original_upload
        live_upload_script.task_runtime.fetch_guangya_live_fast_check = original_fast_check
        live_upload_script.task_runtime.upload_guangya_local_file = original_upload

    output = json.loads(stdout_buffer.getvalue())
    task_payload = json.loads(task_json.read_text(encoding="utf-8"))
    markdown = task_markdown.read_text(encoding="utf-8")
    auth_evidence_markdown = auth_evidence.read_text(encoding="utf-8")
    runtime_evidence_markdown = runtime_evidence.read_text(encoding="utf-8")
    real_evidence_markdown = real_evidence.read_text(encoding="utf-8")
    remediation_markdown = remediation.read_text(encoding="utf-8")

    for path in (task_json, task_markdown, auth_evidence, runtime_evidence, real_evidence, remediation):
        if path.exists():
            path.unlink()

    print(
        json.dumps(
            {
                "exitCode": result,
                "resolvedTargetParentId": output.get("resolvedTargetParentId") == "folder-live-1",
                "stateCompleted": output.get("state") == "completed",
                "hasRealTransferSuccess": ((output.get("summary") or {}).get("hasRealTransferSuccess")) is True,
                "completionKind": ((output.get("summary") or {}).get("completionKind")) == "real_transfer",
                "firstResultLive": ((((output.get("results") or [None])[0]) or {}).get("executionMode")) == "live",
                "firstResultVerifyOk": bool((((((output.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyOk"))),
                "jsonSavedState": task_payload.get("state") == "completed",
                "jsonSavedVerifyMode": (((((task_payload.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyMode")) == "list_by_parent_name",
                "markdownHasConflictAction": "conflictAction=`overwrite_downgraded_to_auto_rename`" in markdown,
                "markdownHasResolvedTargetName": "resolvedTargetName=`cloudpan-sync-live-upload (1).bin`" in markdown,
                "authEvidenceHasTitle": "# Auth Profile Evidence" in auth_evidence_markdown,
                "runtimeEvidenceHasTitle": "# CloudPan Sync 任务运行真实样本报告" in runtime_evidence_markdown,
                "realEvidenceHasTitle": "# CloudPan Sync 真实证据状态报告" in real_evidence_markdown,
                "remediationHasTitle": "# CloudPan Sync 真实联调补救指南" in remediation_markdown,
                "scriptHasMarkdownOutputArg": "--markdown-output" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasTaskJsonOutputArg": "--task-json-output" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasAuthEvidenceOutputArg": "--auth-evidence-output" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasRuntimeEvidenceOutputArg": "--runtime-evidence-output" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasRealEvidenceOutputArg": "--real-evidence-output" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasRemediationOutputArg": "--remediation-output" in SCRIPT_PATH.read_text(encoding="utf-8"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
