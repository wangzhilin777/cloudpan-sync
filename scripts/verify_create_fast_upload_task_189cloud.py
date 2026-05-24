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
from cloudpan_sync.tianyi_fast_upload_live import TianyiFastUploadResult

SCRIPT_PATH = ROOT / "scripts" / "create_fast_upload_candidate_task.py"
SPEC = importlib.util.spec_from_file_location("create_fast_upload_candidate_task", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
fast_upload_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fast_upload_script)


def main() -> None:
    original_get_profile = fast_upload_script.get_profile
    original_refresh_auth_evidence = fast_upload_script.refresh_auth_profile_evidence
    original_upload = task_runtime.upload_tianyi_fast_file
    original_task_runtime_get_profile = task_runtime.get_profile
    original_evaluate_task_guard = task_runtime.evaluate_task_guard
    refresh_calls: list[dict[str, object]] = []

    evidence_dir = ROOT / "tmp" / "verify-189cloud-fast-task-evidence-bundle"
    if evidence_dir.exists():
        for child in evidence_dir.iterdir():
            if child.is_file():
                child.unlink()
        evidence_dir.rmdir()

    def fake_get_profile(profile_id: str) -> AuthProfile | None:
        if profile_id != "189cloud-fast-1":
            return None
        return AuthProfile(
            profileId="189cloud-fast-1",
            providerKey="189cloud",
            authMode="manual_cookie",
            displayName="189cloud-fast",
            token="demo-access-token",
            cookie="SESSION=demo",
            extra={
                "parentId": "-11",
                "shareCode": "demo-share-code",
                "signature": "demo-signature",
                "date": "Mon, 25 May 2026 00:00:00 GMT",
            },
            status="saved",
            lastError="",
            createdAt="2026-05-25T00:00:00+00:00",
            updatedAt="2026-05-25T00:00:00+00:00",
        )

    def fake_upload(
        *,
        profile_id: str,
        local_path: str,
        target_name: str,
        parent_id: str = "",
        expected_md5: str = "",
    ) -> TianyiFastUploadResult:
        return TianyiFastUploadResult(
            ok=True,
            mode="rapid_upload_by_hash",
            usedProfile=True,
            profileId=profile_id,
            parentId=parent_id or "-11",
            status=200,
            error="",
            note="189cloud rapid upload ok",
            payload={
                "resolvedTargetName": "cloudpan-sync-fast-candidate.bin",
                "uploadFileId": 189001,
                "fileCommitUrl": "https://api.cloud.189.cn/fileCommitUrl.demo",
                "conflictAction": "",
                "providedWriteHeaders": True,
            },
            verifyOk=True,
            verifyMode="commit_response_xml",
            verifyNote="verified by commit response",
            verifyPayload={"fileId": "189-file-1", "md5": "dummy"},
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

    def fake_evaluate_task_guard(payload: object, plan: dict[str, object]) -> dict[str, object]:
        profile = fake_get_profile("189cloud-fast-1")
        profile_view = {
            "profileId": "189cloud-fast-1",
            "providerKey": "189cloud",
            "profileReady": True,
            "writeReady": True,
            "resolvedParentId": "-11",
            "resolvedFileId": "",
            "missingFieldHints": [],
            "writeMissingFieldHints": [],
            "writeBlockerNote": "",
        }
        if profile is None:
            profile_view = {}
        return {
            "hardBlocked": False,
            "blockingReasons": [],
            "warningReasons": [],
            "requiresAcknowledgement": {
                "pendingManual": False,
                "downloadUpload": False,
            },
            "acknowledged": {
                "pendingManual": False,
                "downloadUpload": False,
            },
            "targetProfile": profile_view,
        }

    fast_upload_script.get_profile = fake_get_profile
    fast_upload_script.refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
    task_runtime.upload_tianyi_fast_file = fake_upload
    task_runtime.get_profile = fake_get_profile
    task_runtime.evaluate_task_guard = fake_evaluate_task_guard
    fast_upload_script.task_runtime.upload_tianyi_fast_file = fake_upload
    fast_upload_script.task_runtime.get_profile = fake_get_profile
    fast_upload_script.task_runtime.evaluate_task_guard = fake_evaluate_task_guard

    try:
        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            result = fast_upload_script.main(
                [
                    "--target-provider",
                    "189cloud",
                    "--target-profile-id",
                    "189cloud-fast-1",
                    "--target-parent-id",
                    "-11",
                    "--source-provider",
                    "baidu_netdisk",
                    "--auto-temp-file",
                    "--evidence-dir",
                    str(evidence_dir),
                ]
            )
    finally:
        fast_upload_script.get_profile = original_get_profile
        fast_upload_script.refresh_auth_profile_evidence = original_refresh_auth_evidence
        task_runtime.upload_tianyi_fast_file = original_upload
        task_runtime.get_profile = original_task_runtime_get_profile
        task_runtime.evaluate_task_guard = original_evaluate_task_guard
        fast_upload_script.task_runtime.upload_tianyi_fast_file = original_upload
        fast_upload_script.task_runtime.get_profile = original_task_runtime_get_profile
        fast_upload_script.task_runtime.evaluate_task_guard = original_evaluate_task_guard

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
                "authEvidenceRefreshed": len(refresh_calls) == 1 and refresh_calls[0].get("profileId") == "189cloud-fast-1",
                "jsonSavedState": task_payload.get("state") == "completed",
                "jsonSavedVerifyMode": (((((task_payload.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyMode")) == "commit_response_xml",
                "markdownHasCompletionKind": "completionKind: `real_transfer`" in markdown,
                "runtimeEvidenceHasTitle": "# CloudPan Sync 任务运行真实样本报告" in runtime_evidence_markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
