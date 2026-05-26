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
    original_runtime_orphan_builder = live_upload_script.build_runtime_orphan_recovery
    original_fast_check = task_runtime.fetch_guangya_live_fast_check
    original_upload = task_runtime.upload_guangya_local_file
    refresh_calls: list[dict[str, object]] = []

    task_json = ROOT / "tmp" / "verify-live-upload-task.json"
    task_markdown = ROOT / "tmp" / "verify-live-upload-task.md"
    auth_evidence = ROOT / "tmp" / "verify-live-auth-evidence.md"
    runtime_evidence = ROOT / "tmp" / "verify-live-runtime-evidence.md"
    real_evidence = ROOT / "tmp" / "verify-live-real-evidence.md"
    remediation = ROOT / "tmp" / "verify-live-remediation.md"
    evidence_dir = ROOT / "tmp" / "verify-live-evidence-bundle"
    for path in (task_json, task_markdown, auth_evidence, runtime_evidence, real_evidence, remediation):
        if path.exists():
            path.unlink()
    if evidence_dir.exists():
        for child in evidence_dir.iterdir():
            if child.is_file():
                child.unlink()
        evidence_dir.rmdir()

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

    def fake_refresh_auth_profile_evidence(
        *,
        profile: object,
        page_size: int = 100,
        dir_name: str = "",
        persist: bool = True,
        profile_view_builder=None,
    ) -> dict[str, object]:
        refresh_calls.append(
            {
                "profileId": getattr(profile, "profileId", ""),
                "pageSize": page_size,
                "dirName": dir_name,
                "persist": persist,
            }
        )
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
                "profileIds": ["gy-live-1", "gy-live-2"],
                "recommendedAuthModes": ["web_login_capture", "manual_token"],
                "requiredFieldHints": ["token or extra.authorization", "extra.parentId"],
                "webLoginUrl": "https://guangyapan.com/",
                "officialDocsUrl": "",
                "nextStep": "当前档案仍含占位 token/cookie 等 secret 字段；先用真实凭证重建或编辑档案，再重跑 validation / live probe。",
                "needsSecretRefresh": True,
                "placeholderSecretFieldHints": ["token"],
                "recommendedPrimaryCommandLabel": "recreate_probe",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name gy-live --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe",
                "recommendedRecreateProbeCommands": [
                    r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-orphan-live-1 --provider-key guangya --auth-mode manual_token --display-name gy-live --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe",
                    r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-orphan-live-2 --provider-key guangya --auth-mode manual_token --display-name gy-live-2 --token YOUR_TOKEN_2 --set parentId=YOUR_REAL_PARENT_ID_2 --probe",
                ],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name guangya-manual_token --token YOUR_TOKEN --set parentId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name guangya-manual_token --token YOUR_TOKEN --set parentId=YOUR_VALUE --probe",
                "recommendedPatchCommand": r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id gy-live-1 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate",
                "recommendedPatchProbeCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-live-1 --set parentId=YOUR_REAL_PARENT_ID --write",
                "recommendedPatchCommands": [
                    r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id gy-live-1 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate",
                    r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id gy-live-2 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate",
                ],
                "recommendedPatchProbeCommands": [
                    r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-live-1 --set parentId=YOUR_REAL_PARENT_ID --write",
                    r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-live-2 --set parentId=YOUR_REAL_PARENT_ID --write",
                ],
                "recommendedRecreateProbeCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name gy-live --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe",
                "exactPatchHelper": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --from-remediation-profile-id gy-live-1",
                "exactCreateHelper": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-remediation-provider guangya",
                "exactRecreateHelper": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-remediation-orphan-profile gy-orphan-live-1",
                "recommendedLiveUploadCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-live-1 --target-parent-id folder-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-live-2 --target-parent-id folder-live-2 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence-2",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-live-1 --target-parent-id folder-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\guangya-live-evidence",
                "exactRuntimeSuccessHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-remediation-profile-id gy-live-2",
                "exactOverwriteVariantHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-remediation-profile-id gy-live-1",
                "conflictPolicyNote": "支持 direct_select；若同路径同名已存在，可选 overwrite_existing 或 auto_rename_new。",
                "providerConflictNotes": "光鸭 live upload 默认优先 auto_rename_new，overwrite_existing 可能退化为自动改名。",
            }
        ],
    }
    live_upload_script.build_runtime_orphan_recovery = lambda: {
        "summary": {},
        "items": [
            {
                "providerKey": "guangya",
                "orphanProfileId": "gy-orphan-live-1",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-orphan-live-1 --target-parent-id orphan-live-parent --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-runtime-orphan-success-evidence",
            }
        ],
    }
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
                    "--evidence-dir",
                    str(evidence_dir),
                ]
            )

        second_stdout = io.StringIO()
        with contextlib.redirect_stdout(second_stdout):
            second_result = live_upload_script.main(
                [
                    "--target-profile-id",
                    "gy-live-1",
                    "--target-parent-id",
                    "manual-live-parent",
                    "--auto-temp-file",
                    "--no-acknowledge-download-upload",
                    "--no-refresh-auth-evidence",
                    "--task-json-output",
                    str(ROOT / "tmp" / "verify-live-task.json"),
                    "--auth-evidence-output",
                    str(ROOT / "tmp" / "verify-live-auth-only.md"),
                ]
            )

        exact_stdout = io.StringIO()
        with contextlib.redirect_stdout(exact_stdout):
            exact_result = live_upload_script.main(
                [
                    "--from-remediation-profile-id",
                    "gy-live-2",
                    "--auto-temp-file",
                ]
            )

        orphan_exact_stdout = io.StringIO()
        with contextlib.redirect_stdout(orphan_exact_stdout):
            orphan_exact_result = live_upload_script.main(
                [
                    "--from-runtime-orphan-profile",
                    "gy-orphan-live-1",
                    "--auto-temp-file",
                ]
            )
    finally:
        live_upload_script.get_profile = original_get_profile
        live_upload_script.refresh_auth_profile_evidence = original_refresh_auth_evidence
        live_upload_script.build_real_evidence_remediation_bundle = original_remediation_builder
        live_upload_script.build_runtime_orphan_recovery = original_runtime_orphan_builder
        task_runtime.fetch_guangya_live_fast_check = original_fast_check
        task_runtime.upload_guangya_local_file = original_upload
        live_upload_script.task_runtime.fetch_guangya_live_fast_check = original_fast_check
        live_upload_script.task_runtime.upload_guangya_local_file = original_upload

    output = json.loads(stdout_buffer.getvalue())
    second_output = json.loads(second_stdout.getvalue())
    exact_output = json.loads(exact_stdout.getvalue())
    orphan_exact_output = json.loads(orphan_exact_stdout.getvalue())
    task_json = evidence_dir / "task.json"
    task_markdown = evidence_dir / "task.md"
    auth_evidence = evidence_dir / "auth_evidence.md"
    runtime_evidence = evidence_dir / "runtime_evidence.md"
    real_evidence = evidence_dir / "real_evidence.md"
    remediation = evidence_dir / "remediation.md"
    task_payload = json.loads(task_json.read_text(encoding="utf-8"))
    markdown = task_markdown.read_text(encoding="utf-8")
    auth_evidence_markdown = auth_evidence.read_text(encoding="utf-8")
    runtime_evidence_markdown = runtime_evidence.read_text(encoding="utf-8")
    real_evidence_markdown = real_evidence.read_text(encoding="utf-8")
    remediation_markdown = remediation.read_text(encoding="utf-8")

    for path in (task_json, task_markdown, auth_evidence, runtime_evidence, real_evidence, remediation):
        if path.exists():
            path.unlink()
    if evidence_dir.exists():
        evidence_dir.rmdir()
    second_task_json = ROOT / "tmp" / "verify-live-task.json"
    second_auth_evidence = ROOT / "tmp" / "verify-live-auth-only.md"
    second_outputs_ok = second_task_json.exists() and second_auth_evidence.exists()
    if second_task_json.exists():
        second_task_json.unlink()
    if second_auth_evidence.exists():
        second_auth_evidence.unlink()

    print(
        json.dumps(
            {
                "exitCode": result,
                "secondExitCode": second_result,
                "exactExitCode": exact_result,
                "orphanExactExitCode": orphan_exact_result,
                "resolvedTargetParentId": output.get("resolvedTargetParentId") == "folder-live-1",
                "evidenceDirOutput": output.get("evidenceDir") == str(evidence_dir),
                "stateCompleted": output.get("state") == "completed",
                "hasRealTransferSuccess": ((output.get("summary") or {}).get("hasRealTransferSuccess")) is True,
                "completionKind": ((output.get("summary") or {}).get("completionKind")) == "real_transfer",
                "firstResultLive": ((((output.get("results") or [None])[0]) or {}).get("executionMode")) == "live",
                "firstResultVerifyOk": bool((((((output.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyOk"))),
                "authEvidenceRefreshed": len(refresh_calls) == 1 and refresh_calls[0].get("profileId") == "gy-live-1" and refresh_calls[0].get("persist") is True,
                "remediationPrimaryCommandIncluded": dict(output.get("remediationFollowup") or {}).get("recommendedPrimaryCommandLabel") == "recreate_probe"
                and "create_auth_profile_stub.py" in dict(output.get("remediationFollowup") or {}).get("recommendedPrimaryCommand", ""),
                "remediationAuthContextIncluded": dict(output.get("remediationFollowup") or {}).get("recommendedAuthModes") == ["web_login_capture", "manual_token"]
                and dict(output.get("remediationFollowup") or {}).get("requiredFieldHints") == ["token or extra.authorization", "extra.parentId"]
                and dict(output.get("remediationFollowup") or {}).get("webLoginUrl") == "https://guangyapan.com/"
                and dict(output.get("remediationFollowup") or {}).get("officialDocsUrl") == "",
                "remediationSecretRefreshIncluded": dict(output.get("remediationFollowup") or {}).get("needsSecretRefresh") is True
                and dict(output.get("remediationFollowup") or {}).get("placeholderSecretFieldHints") == ["token"]
                and "create_auth_profile_stub.py" in dict(output.get("remediationFollowup") or {}).get("recommendedRecreateProbeCommand", "")
                and len(dict(output.get("remediationFollowup") or {}).get("recommendedRecreateProbeCommands", [])) == 2
                and any("--profile-id gy-orphan-live-2" in value for value in dict(output.get("remediationFollowup") or {}).get("recommendedRecreateProbeCommands", []))
                and "--provider-key guangya" in dict(output.get("remediationFollowup") or {}).get("recommendedCreateCommand", "")
                and "--probe" in dict(output.get("remediationFollowup") or {}).get("recommendedBootstrapCommand", "")
                and "create_auth_profile_stub.py --from-remediation-provider guangya" in dict(output.get("remediationFollowup") or {}).get("exactCreateHelper", "")
                and "create_auth_profile_stub.py --from-remediation-orphan-profile gy-orphan-live-1" in dict(output.get("remediationFollowup") or {}).get("exactRecreateHelper", ""),
                "remediationPatchIncluded": "patch_auth_profile_extra.py --profile-id gy-live-1" in dict(output.get("remediationFollowup") or {}).get("recommendedPatchCommand", "")
                and "patch_and_probe_auth_profile.py --profile-id gy-live-1" in dict(output.get("remediationFollowup") or {}).get("recommendedPatchProbeCommand", "")
                and len(dict(output.get("remediationFollowup") or {}).get("recommendedPatchCommands", [])) == 2
                and any("--profile-id gy-live-2" in value for value in dict(output.get("remediationFollowup") or {}).get("recommendedPatchCommands", []))
                and len(dict(output.get("remediationFollowup") or {}).get("recommendedPatchProbeCommands", [])) == 2
                and any("--profile-id gy-live-2" in value for value in dict(output.get("remediationFollowup") or {}).get("recommendedPatchProbeCommands", []))
                and "patch_and_probe_auth_profile.py --from-remediation-profile-id gy-live-1" in dict(output.get("remediationFollowup") or {}).get("exactPatchHelper", ""),
                "remediationFollowupIncluded": dict(output.get("remediationFollowup") or {}).get("recommendedRuntimeSuccessCommand", "").endswith("tmp\\guangya-live-evidence-2")
                and "create_live_upload_task.py --from-remediation-profile-id gy-live-2" in dict(output.get("remediationFollowup") or {}).get("exactRuntimeSuccessHelper", "")
                and dict(output.get("remediationFollowup") or {}).get("recommendedOverwriteVariantCommand", "").endswith("tmp\\guangya-live-evidence")
                and "create_live_upload_task.py --from-remediation-profile-id gy-live-1" in dict(output.get("remediationFollowup") or {}).get("exactOverwriteVariantHelper", "")
                and "direct_select" in dict(output.get("remediationFollowup") or {}).get("conflictPolicyNote", "")
                and "auto_rename_new" in dict(output.get("remediationFollowup") or {}).get("providerConflictNotes", ""),
                "explicitTargetParentWins": second_output.get("resolvedTargetParentId") == "manual-live-parent",
                "noRefreshSkipsAuthRefresh": len(refresh_calls) == 1 and second_output.get("refreshedAuthEvidence") is False,
                "explicitOutputsCreated": second_outputs_ok
                and second_output.get("taskJsonOutput") == str(second_task_json)
                and second_output.get("authEvidenceOutput") == str(second_auth_evidence),
                "exactProfileDefaultsApplied": exact_output.get("defaultsSource") == "remediation:recommendedRuntimeSuccessCommand"
                and exact_output.get("targetProfileId") == "gy-live-2"
                and exact_output.get("resolvedTargetParentId") == "folder-live-2",
                "runtimeOrphanDefaultsApplied": orphan_exact_output.get("defaultsSource") == "runtime_orphan:recommendedRuntimeSuccessCommand"
                and orphan_exact_output.get("targetProfileId") == "gy-orphan-live-1"
                and orphan_exact_output.get("resolvedTargetParentId") == "orphan-live-parent",
                "noAcknowledgeFlagHonored": second_output.get("acknowledgedDownloadUpload") is False,
                "jsonSavedState": task_payload.get("state") == "completed",
                "jsonSavedVerifyMode": (((((task_payload.get("results") or [None])[0]) or {}).get("liveAttempt") or {}).get("verifyMode")) == "list_by_parent_name",
                "markdownHasConflictAction": "conflictAction=`overwrite_downgraded_to_auto_rename`" in markdown,
                "markdownHasResolvedTargetName": "resolvedTargetName=`cloudpan-sync-live-upload (1).bin`" in markdown,
                "authEvidenceHasTitle": "# Auth Profile Evidence" in auth_evidence_markdown,
                "runtimeEvidenceHasTitle": "# CloudPan Sync 任务运行真实样本报告" in runtime_evidence_markdown,
                "realEvidenceHasTitle": "# CloudPan Sync 真实证据状态报告" in real_evidence_markdown,
                "remediationHasTitle": "# CloudPan Sync 真实联调补救指南" in remediation_markdown,
                "bundleUsesFixedFilenames": all(
                    path.name in {"task.json", "task.md", "auth_evidence.md", "runtime_evidence.md", "real_evidence.md", "remediation.md"}
                    for path in (task_json, task_markdown, auth_evidence, runtime_evidence, real_evidence, remediation)
                ),
                "scriptHasEvidenceDirArg": "--evidence-dir" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasExactProfileArg": "--from-remediation-profile-id" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasRuntimeOrphanArg": "--from-runtime-orphan-profile" in SCRIPT_PATH.read_text(encoding="utf-8"),
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
