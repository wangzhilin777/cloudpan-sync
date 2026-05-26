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
    original_runtime_orphan_builder = runtime_probe_script.build_runtime_orphan_recovery
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
    runtime_probe_script.build_real_evidence_remediation_bundle = lambda: {
        "summary": {},
        "items": [
            {
                "providerKey": "aliyundrive_open",
                "profileIds": ["ali-runtime-1", "ali-runtime-2"],
                "recommendedAuthModes": ["official_oauth"],
                "requiredFieldHints": ["token or extra.authorization", "extra.domainId", "extra.driveId"],
                "webLoginUrl": "https://www.alipan.com/",
                "officialDocsUrl": "https://www.alipan.com/",
                "nextStep": "当前档案仍含占位 token/cookie 等 secret 字段；先用真实凭证重建或编辑档案，再重跑 validation / live probe。",
                "needsSecretRefresh": True,
                "placeholderSecretFieldHints": ["token"],
                "recommendedPrimaryCommandLabel": "recreate_probe",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name ali-runtime --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe",
                "recommendedRecreateProbeCommands": [
                    r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id ali-orphan-runtime-1 --provider-key aliyundrive_open --auth-mode official_oauth --display-name ali-runtime --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe",
                    r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id ali-orphan-runtime-2 --provider-key aliyundrive_open --auth-mode official_oauth --display-name ali-runtime-2 --token YOUR_TOKEN_2 --set domainId=YOUR_DOMAIN_ID_2 --set driveId=YOUR_DRIVE_ID_2 --probe",
                ],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyundrive_open-official_oauth --token YOUR_TOKEN --set domainId=YOUR_VALUE --set driveId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyundrive_open-official_oauth --token YOUR_TOKEN --set domainId=YOUR_VALUE --set driveId=YOUR_VALUE --probe",
                "recommendedPatchCommand": r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id ali-runtime-1 --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write --revalidate",
                "recommendedPatchProbeCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id ali-runtime-1 --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write",
                "recommendedPatchCommands": [
                    r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id ali-runtime-1 --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write --revalidate",
                    r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id ali-runtime-2 --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write --revalidate",
                ],
                "recommendedPatchProbeCommands": [
                    r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id ali-runtime-1 --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write",
                    r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id ali-runtime-2 --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write",
                ],
                "recommendedRecreateProbeCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name ali-runtime --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe",
                "exactPatchHelper": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --from-remediation-profile-id ali-runtime-1",
                "exactCreateHelper": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-remediation-provider aliyundrive_open",
                "exactRecreateHelper": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-remediation-orphan-profile ali-orphan-runtime-1",
                "recommendedRuntimeProbeCommand": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --target-provider aliyundrive_open --target-profile-id ali-runtime-1 --target-parent-id folder-demo --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\aliyundrive_open-runtime-probe-evidence",
                "exactRuntimeProbeHelper": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --from-remediation-profile-id ali-runtime-1",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider aliyundrive_open --target-profile-id ali-runtime-2 --target-parent-id folder-demo-2 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\aliyundrive_open-live-evidence-2",
                "recommendedPostRefreshRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider aliyundrive_open --target-profile-id ali-runtime-1 --target-parent-id folder-demo --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\aliyundrive_open-live-evidence",
                "exactPostRefreshRuntimeHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-remediation-profile-id ali-runtime-1",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider aliyundrive_open --target-profile-id ali-runtime-1 --target-parent-id folder-demo --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\aliyundrive_open-live-evidence",
                "exactRefreshEvidenceHelper": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --from-remediation-profile-id ali-runtime-1",
                "exactRuntimeSuccessHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-remediation-profile-id ali-runtime-2",
                "exactOverwriteVariantHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-remediation-profile-id ali-runtime-1",
                "conflictPolicyNote": "支持 direct_select；若同路径同名已存在，可选 overwrite_existing 或 auto_rename_new。",
                "providerConflictNotes": "阿里云盘开放版当前推荐 auto_rename_new 作为默认兜底，必要时再切 overwrite_existing。",
            }
        ],
    }
    runtime_probe_script.build_runtime_orphan_recovery = lambda: {
        "summary": {},
        "items": [
            {
                "providerKey": "aliyundrive_open",
                "orphanProfileId": "ali-orphan-runtime-1",
                "recommendedRuntimeProbeCommand": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --target-provider aliyundrive_open --target-profile-id ali-orphan-runtime-1 --target-parent-id orphan-folder-demo --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\aliyundrive_open-runtime-orphan-probe-evidence",
            }
        ],
    }
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

        second_stdout = io.StringIO()
        with contextlib.redirect_stdout(second_stdout):
            second_result = runtime_probe_script.main(
                [
                    "--target-provider",
                    "aliyundrive_open",
                    "--target-profile-id",
                    "ali-runtime-1",
                    "--target-parent-id",
                    "manual-parent",
                    "--auto-temp-file",
                    "--task-json-output",
                    str(ROOT / "tmp" / "verify-runtime-probe-task.json"),
                    "--no-refresh-auth-evidence",
                    "--auth-evidence-output",
                    str(ROOT / "tmp" / "verify-runtime-auth-evidence.md"),
                ]
            )

        exact_stdout = io.StringIO()
        with contextlib.redirect_stdout(exact_stdout):
            exact_result = runtime_probe_script.main(
                [
                    "--from-remediation-profile-id",
                    "ali-runtime-1",
                    "--auto-temp-file",
                ]
            )

        orphan_exact_stdout = io.StringIO()
        with contextlib.redirect_stdout(orphan_exact_stdout):
            orphan_exact_result = runtime_probe_script.main(
                [
                    "--from-runtime-orphan-profile",
                    "ali-orphan-runtime-1",
                    "--auto-temp-file",
                ]
            )
    finally:
        task_runtime.create_task = original_create_task
        task_runtime.run_task = original_run_task
        runtime_probe_script.task_runtime.create_task = original_create_task
        runtime_probe_script.task_runtime.run_task = original_run_task
        runtime_probe_script.get_profile = original_get_profile
        runtime_probe_script.refresh_auth_profile_evidence = original_refresh_auth_evidence
        runtime_probe_script.build_real_evidence_remediation_bundle = original_remediation_builder
        runtime_probe_script.build_runtime_orphan_recovery = original_runtime_orphan_builder

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
    second_task_json = ROOT / "tmp" / "verify-runtime-probe-task.json"
    second_auth_evidence = ROOT / "tmp" / "verify-runtime-auth-evidence.md"
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
                "scriptEmittedTaskJson": output.get("taskId") == "task-runtime-1",
                "scriptResolvedTargetParentId": output.get("resolvedTargetParentId") == "folder-demo",
                "scriptEvidenceDirOutput": output.get("evidenceDir") == str(evidence_dir),
                "scriptAuthEvidenceRefreshed": output.get("refreshedAuthEvidence") is True
                and len(refresh_calls) >= 1
                and refresh_calls[0].get("profileId") == "ali-runtime-1",
                "scriptEvidenceBundleCreated": evidence_titles_ok,
                "scriptRemediationPrimaryCommandIncluded": dict(output.get("remediationFollowup") or {}).get("recommendedPrimaryCommandLabel") == "recreate_probe"
                and "create_auth_profile_stub.py" in dict(output.get("remediationFollowup") or {}).get("recommendedPrimaryCommand", ""),
                "scriptRemediationAuthContextIncluded": dict(output.get("remediationFollowup") or {}).get("recommendedAuthModes") == ["official_oauth"]
                and dict(output.get("remediationFollowup") or {}).get("requiredFieldHints") == ["token or extra.authorization", "extra.domainId", "extra.driveId"]
                and dict(output.get("remediationFollowup") or {}).get("webLoginUrl") == "https://www.alipan.com/"
                and dict(output.get("remediationFollowup") or {}).get("officialDocsUrl") == "https://www.alipan.com/",
                "scriptRemediationSecretRefreshIncluded": dict(output.get("remediationFollowup") or {}).get("needsSecretRefresh") is True
                and dict(output.get("remediationFollowup") or {}).get("placeholderSecretFieldHints") == ["token"]
                and "create_auth_profile_stub.py" in dict(output.get("remediationFollowup") or {}).get("recommendedRecreateProbeCommand", "")
                and len(dict(output.get("remediationFollowup") or {}).get("recommendedRecreateProbeCommands", [])) == 2
                and any("--profile-id ali-orphan-runtime-2" in value for value in dict(output.get("remediationFollowup") or {}).get("recommendedRecreateProbeCommands", []))
                and "--provider-key aliyundrive_open" in dict(output.get("remediationFollowup") or {}).get("recommendedCreateCommand", "")
                and "--probe" in dict(output.get("remediationFollowup") or {}).get("recommendedBootstrapCommand", "")
                and "create_auth_profile_stub.py --from-remediation-provider aliyundrive_open" in dict(output.get("remediationFollowup") or {}).get("exactCreateHelper", "")
                and "create_auth_profile_stub.py --from-remediation-orphan-profile ali-orphan-runtime-1" in dict(output.get("remediationFollowup") or {}).get("exactRecreateHelper", ""),
                "scriptRemediationPatchIncluded": "patch_auth_profile_extra.py --profile-id ali-runtime-1" in dict(output.get("remediationFollowup") or {}).get("recommendedPatchCommand", "")
                and "patch_and_probe_auth_profile.py --profile-id ali-runtime-1" in dict(output.get("remediationFollowup") or {}).get("recommendedPatchProbeCommand", "")
                and len(dict(output.get("remediationFollowup") or {}).get("recommendedPatchCommands", [])) == 2
                and any("--profile-id ali-runtime-2" in value for value in dict(output.get("remediationFollowup") or {}).get("recommendedPatchCommands", []))
                and len(dict(output.get("remediationFollowup") or {}).get("recommendedPatchProbeCommands", [])) == 2
                and any("--profile-id ali-runtime-2" in value for value in dict(output.get("remediationFollowup") or {}).get("recommendedPatchProbeCommands", []))
                and "patch_and_probe_auth_profile.py --from-remediation-profile-id ali-runtime-1" in dict(output.get("remediationFollowup") or {}).get("exactPatchHelper", ""),
                "scriptRemediationFollowupIncluded": dict(output.get("remediationFollowup") or {}).get("recommendedPostRefreshRuntimeCommand", "").endswith("tmp\\aliyundrive_open-live-evidence")
                and "patch_and_probe_auth_profile.py --from-remediation-profile-id ali-runtime-1" in dict(output.get("remediationFollowup") or {}).get("exactRefreshEvidenceHelper", "")
                and "create_live_upload_task.py --from-remediation-profile-id ali-runtime-1" in dict(output.get("remediationFollowup") or {}).get("exactPostRefreshRuntimeHelper", "")
                and "create_runtime_probe_task.py --from-remediation-profile-id ali-runtime-1" in dict(output.get("remediationFollowup") or {}).get("exactRuntimeProbeHelper", "")
                and "create_live_upload_task.py --from-remediation-profile-id ali-runtime-2" in dict(output.get("remediationFollowup") or {}).get("exactRuntimeSuccessHelper", "")
                and dict(output.get("remediationFollowup") or {}).get("recommendedOverwriteVariantCommand", "").endswith("tmp\\aliyundrive_open-live-evidence")
                and "create_live_upload_task.py --from-remediation-profile-id ali-runtime-1" in dict(output.get("remediationFollowup") or {}).get("exactOverwriteVariantHelper", "")
                and "direct_select" in dict(output.get("remediationFollowup") or {}).get("conflictPolicyNote", "")
                and "auto_rename_new" in dict(output.get("remediationFollowup") or {}).get("providerConflictNotes", ""),
                "scriptExplicitTargetParentWins": second_output.get("resolvedTargetParentId") == "manual-parent",
                "scriptNoRefreshSkipsAuthRefresh": second_output.get("refreshedAuthEvidence") is False,
                "scriptExplicitOutputsCreated": second_outputs_ok
                and second_output.get("taskJsonOutput") == str(second_task_json)
                and second_output.get("authEvidenceOutput") == str(second_auth_evidence),
                "scriptExactProfileDefaultsApplied": exact_output.get("defaultsSource") == "remediation:recommendedRuntimeProbeCommand"
                and exact_output.get("targetProfileId") == "ali-runtime-1"
                and exact_output.get("resolvedTargetParentId") == "folder-demo",
                "scriptRuntimeOrphanDefaultsApplied": orphan_exact_output.get("defaultsSource") == "runtime_orphan:recommendedRuntimeProbeCommand"
                and orphan_exact_output.get("resolvedTargetParentId") == "orphan-folder-demo",
                "scriptHasAutoTempFile": "--auto-temp-file" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasExactProfileArg": "--from-remediation-profile-id" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasRuntimeOrphanArg": "--from-runtime-orphan-profile" in SCRIPT_PATH.read_text(encoding="utf-8"),
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
