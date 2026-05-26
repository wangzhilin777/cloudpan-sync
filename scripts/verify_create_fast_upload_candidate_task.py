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
    original_runtime_orphan_builder = fast_candidate_script.build_runtime_orphan_recovery
    refresh_calls: list[dict[str, object]] = []

    def fake_create_task(payload: object) -> dict[str, object]:
        return {
            "taskId": "task-fast-candidate-1",
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
            "targetProfileId": "115-fast-1",
            "sourceEntries": [
                {
                    "path": "/cloudpan-sync-fast-candidate.bin",
                    "size": 28,
                    "sha1": "96b06f478886641050f54f5504c05dbf1e0f0711",
                    "localPath": "temp.bin",
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
        if profile_id != "115-fast-1":
            return None
        return AuthProfile(
            profileId="115-fast-1",
            providerKey="115_open",
            authMode="manual_cookie",
            displayName="115-fast",
            token="",
            cookie="UID=1; CID=2",
            extra={"cid": "115-root"},
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
    fast_candidate_script.task_runtime.create_task = fake_create_task
    fast_candidate_script.task_runtime.run_task = fake_run_task
    fast_candidate_script.get_profile = fake_get_profile
    fast_candidate_script.refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
    fast_candidate_script.build_real_evidence_remediation_bundle = lambda: {
        "summary": {},
        "items": [
            {
                "providerKey": "115_open",
                "profileIds": ["115-fast-1", "115-fast-2"],
                "recommendedAuthModes": ["manual_cookie", "official_oauth"],
                "requiredFieldHints": ["cookie or extra.cookie_header", "optional extra.parentId or extra.cid"],
                "webLoginUrl": "",
                "officialDocsUrl": "",
                "declaredConflictPolicies": [],
                "supportsOverwrite": False,
                "supportsAutoRename": False,
                "overwriteBehavior": "not_implemented",
                "overwriteSupportStatus": "unsupported",
                "autoRenameSupportStatus": "probe_only_runtime_write_check",
                "profileCount": 2,
                "authReadyProfiles": 0,
                "writeReadyProfiles": 2,
                "needsAuthEvidence": True,
                "needsListEvidence": True,
                "needsMetadataEvidence": True,
                "needsCreateDirEvidence": True,
                "needsRuntimeSuccess": True,
                "runtimeBlockedOnly": False,
                "runtimeCandidateOnly": False,
                "runtimeProbeOnly": True,
                "runtimeOrphanOnly": False,
                "runtimeOrphanProfiles": [],
                "gaps": ["缺少通过的 auth validation 证据", "已有 probe-only 样本，但尚未记录到真实传输成功样本"],
                "nextStep": "当前档案仍含占位 token/cookie 等 secret 字段；先用真实凭证重建或编辑档案，再重跑 validation / live probe。",
                "needsSecretRefresh": True,
                "placeholderSecretFieldHints": ["cookie"],
                "recommendedPrimaryCommandLabel": "recreate_probe",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 115_open --auth-mode manual_cookie --display-name 115-fast --cookie YOUR_COOKIE --set parentId=YOUR_PARENT_ID --probe",
                "recommendedRecreateProbeCommands": [
                    r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id 115-orphan-fast-1 --provider-key 115_open --auth-mode manual_cookie --display-name 115-fast --cookie YOUR_COOKIE --set parentId=YOUR_PARENT_ID --probe",
                    r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id 115-orphan-fast-2 --provider-key 115_open --auth-mode manual_cookie --display-name 115-fast-2 --cookie YOUR_COOKIE_2 --set parentId=YOUR_PARENT_ID_2 --probe",
                ],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 115_open --auth-mode manual_cookie --display-name 115_open-manual_cookie --cookie YOUR_COOKIE --set parentId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 115_open --auth-mode manual_cookie --display-name 115_open-manual_cookie --cookie YOUR_COOKIE --set parentId=YOUR_VALUE --probe",
                "recommendedPatchCommand": r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 115-fast-1 --set cid=115-root --write --revalidate",
                "recommendedPatchProbeCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id 115-fast-1 --set cid=115-root --write",
                "recommendedPatchCommands": [
                    r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 115-fast-1 --set cid=115-root --write --revalidate",
                    r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 115-fast-2 --set cid=115-root-2 --write --revalidate",
                ],
                "recommendedPatchProbeCommands": [
                    r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id 115-fast-1 --set cid=115-root --write",
                    r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id 115-fast-2 --set cid=115-root-2 --write",
                ],
                "recommendedRecreateProbeCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 115_open --auth-mode manual_cookie --display-name 115-fast --cookie YOUR_COOKIE --set parentId=YOUR_PARENT_ID --probe",
                "exactPatchHelper": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --from-remediation-profile-id 115-fast-1",
                "exactCreateHelper": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-remediation-provider 115_open",
                "exactRecreateHelper": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-remediation-orphan-profile 115-orphan-fast-1",
                "recommendedFastCandidateCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-fast-1 --target-parent-id 115-root --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-fast-candidate-evidence",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-fast-2 --target-parent-id 115-root-2 --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-fast-candidate-evidence-2",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-fast-1 --target-parent-id 115-root --sha1 auto --auto-temp-file --conflict-policy overwrite_existing --evidence-dir tmp\115_open-fast-candidate-evidence",
                "exactRuntimeSuccessHelper": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --from-remediation-profile-id 115-fast-2",
                "exactOverwriteVariantHelper": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --from-remediation-profile-id 115-fast-1",
                "conflictPolicyNote": "支持 direct_select；若同路径同名已存在，可选 overwrite_existing 或 auto_rename_new。",
                "providerConflictNotes": "115 秒传候选默认建议 auto_rename_new，避免误覆盖现有同名文件。",
            }
        ],
    }
    fast_candidate_script.build_runtime_orphan_recovery = lambda: {
        "summary": {},
        "items": [
            {
                "providerKey": "115_open",
                "orphanProfileId": "115-orphan-fast-1",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-orphan-fast-1 --target-parent-id orphan-fast-root --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-runtime-orphan-success-evidence",
            }
        ],
    }
    try:
        evidence_dir = ROOT / "tmp" / "verify-fast-candidate-evidence"
        if evidence_dir.exists():
            for child in evidence_dir.iterdir():
                if child.is_file():
                    child.unlink()
            evidence_dir.rmdir()
        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            result = fast_candidate_script.main(
                [
                    "--target-provider",
                    "115_open",
                    "--target-profile-id",
                    "115-fast-1",
                    "--auto-temp-file",
                    "--sha1",
                    "auto",
                    "--evidence-dir",
                    str(evidence_dir),
                ]
            )

        second_stdout = io.StringIO()
        with contextlib.redirect_stdout(second_stdout):
            second_result = fast_candidate_script.main(
                [
                    "--target-provider",
                    "115_open",
                    "--target-profile-id",
                    "115-fast-1",
                    "--target-parent-id",
                    "manual-fast-parent",
                    "--auto-temp-file",
                    "--sha1",
                    "auto",
                    "--task-json-output",
                    str(ROOT / "tmp" / "verify-fast-candidate-task.json"),
                    "--no-refresh-auth-evidence",
                    "--auth-evidence-output",
                    str(ROOT / "tmp" / "verify-fast-candidate-auth-evidence.md"),
                ]
            )

        exact_stdout = io.StringIO()
        with contextlib.redirect_stdout(exact_stdout):
            exact_result = fast_candidate_script.main(
                [
                    "--from-remediation-profile-id",
                    "115-fast-2",
                    "--auto-temp-file",
                    "--sha1",
                    "auto",
                ]
            )

        orphan_exact_stdout = io.StringIO()
        with contextlib.redirect_stdout(orphan_exact_stdout):
            orphan_exact_result = fast_candidate_script.main(
                [
                    "--from-runtime-orphan-profile",
                    "115-orphan-fast-1",
                    "--auto-temp-file",
                    "--sha1",
                    "auto",
                ]
            )
    finally:
        task_runtime.create_task = original_create_task
        task_runtime.run_task = original_run_task
        fast_candidate_script.task_runtime.create_task = original_create_task
        fast_candidate_script.task_runtime.run_task = original_run_task
        fast_candidate_script.get_profile = original_get_profile
        fast_candidate_script.refresh_auth_profile_evidence = original_refresh_auth_evidence
        fast_candidate_script.build_real_evidence_remediation_bundle = original_remediation_builder
        fast_candidate_script.build_runtime_orphan_recovery = original_runtime_orphan_builder

    output = json.loads(stdout_buffer.getvalue())
    second_output = json.loads(second_stdout.getvalue())
    exact_output = json.loads(exact_stdout.getvalue())
    orphan_exact_output = json.loads(orphan_exact_stdout.getvalue())
    source_entry = ((output.get("sourceEntries") or [{}])[0]) if output.get("sourceEntries") else {}
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
    second_task_json = ROOT / "tmp" / "verify-fast-candidate-task.json"
    second_auth_evidence = ROOT / "tmp" / "verify-fast-candidate-auth-evidence.md"
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
                "scriptEmittedTaskJson": output.get("taskId") == "task-fast-candidate-1",
                "scriptResolvedTargetParentId": output.get("resolvedTargetParentId") == "115-root",
                "scriptEvidenceDirOutput": output.get("evidenceDir") == str(evidence_dir),
                "scriptAuthEvidenceRefreshed": len(refresh_calls) == 1 and refresh_calls[0].get("profileId") == "115-fast-1",
                "scriptEvidenceBundleCreated": evidence_titles_ok,
                "scriptRemediationPrimaryCommandIncluded": dict(output.get("remediationFollowup") or {}).get("recommendedPrimaryCommandLabel") == "recreate_probe"
                and "create_auth_profile_stub.py" in dict(output.get("remediationFollowup") or {}).get("recommendedPrimaryCommand", ""),
                "scriptRemediationAuthContextIncluded": dict(output.get("remediationFollowup") or {}).get("recommendedAuthModes") == ["manual_cookie", "official_oauth"]
                and dict(output.get("remediationFollowup") or {}).get("requiredFieldHints") == ["cookie or extra.cookie_header", "optional extra.parentId or extra.cid"]
                and dict(output.get("remediationFollowup") or {}).get("webLoginUrl") == ""
                and dict(output.get("remediationFollowup") or {}).get("officialDocsUrl") == "",
                "scriptRemediationConflictSupportIncluded": dict(output.get("remediationFollowup") or {}).get("declaredConflictPolicies") == []
                and dict(output.get("remediationFollowup") or {}).get("supportsOverwrite") is False
                and dict(output.get("remediationFollowup") or {}).get("supportsAutoRename") is False
                and dict(output.get("remediationFollowup") or {}).get("overwriteBehavior") == "not_implemented"
                and dict(output.get("remediationFollowup") or {}).get("overwriteSupportStatus") == "unsupported"
                and dict(output.get("remediationFollowup") or {}).get("autoRenameSupportStatus") == "probe_only_runtime_write_check",
                "scriptRemediationStatusContextIncluded": dict(output.get("remediationFollowup") or {}).get("profileCount") == 2
                and dict(output.get("remediationFollowup") or {}).get("authReadyProfiles") == 0
                and dict(output.get("remediationFollowup") or {}).get("writeReadyProfiles") == 2
                and dict(output.get("remediationFollowup") or {}).get("needsAuthEvidence") is True
                and dict(output.get("remediationFollowup") or {}).get("needsListEvidence") is True
                and dict(output.get("remediationFollowup") or {}).get("needsMetadataEvidence") is True
                and dict(output.get("remediationFollowup") or {}).get("needsCreateDirEvidence") is True
                and dict(output.get("remediationFollowup") or {}).get("needsRuntimeSuccess") is True
                and dict(output.get("remediationFollowup") or {}).get("runtimeBlockedOnly") is False
                and dict(output.get("remediationFollowup") or {}).get("runtimeCandidateOnly") is False
                and dict(output.get("remediationFollowup") or {}).get("runtimeProbeOnly") is True
                and dict(output.get("remediationFollowup") or {}).get("runtimeOrphanOnly") is False
                and dict(output.get("remediationFollowup") or {}).get("runtimeOrphanProfiles") == []
                and dict(output.get("remediationFollowup") or {}).get("gaps") == ["缺少通过的 auth validation 证据", "已有 probe-only 样本，但尚未记录到真实传输成功样本"],
                "scriptRemediationSecretRefreshIncluded": dict(output.get("remediationFollowup") or {}).get("needsSecretRefresh") is True
                and dict(output.get("remediationFollowup") or {}).get("placeholderSecretFieldHints") == ["cookie"]
                and "create_auth_profile_stub.py" in dict(output.get("remediationFollowup") or {}).get("recommendedRecreateProbeCommand", "")
                and len(dict(output.get("remediationFollowup") or {}).get("recommendedRecreateProbeCommands", [])) == 2
                and any("--profile-id 115-orphan-fast-2" in value for value in dict(output.get("remediationFollowup") or {}).get("recommendedRecreateProbeCommands", []))
                and "--provider-key 115_open" in dict(output.get("remediationFollowup") or {}).get("recommendedCreateCommand", "")
                and "--probe" in dict(output.get("remediationFollowup") or {}).get("recommendedBootstrapCommand", "")
                and "create_auth_profile_stub.py --from-remediation-provider 115_open" in dict(output.get("remediationFollowup") or {}).get("exactCreateHelper", "")
                and "create_auth_profile_stub.py --from-remediation-orphan-profile 115-orphan-fast-1" in dict(output.get("remediationFollowup") or {}).get("exactRecreateHelper", ""),
                "scriptRemediationPatchIncluded": "patch_auth_profile_extra.py --profile-id 115-fast-1" in dict(output.get("remediationFollowup") or {}).get("recommendedPatchCommand", "")
                and "patch_and_probe_auth_profile.py --profile-id 115-fast-1" in dict(output.get("remediationFollowup") or {}).get("recommendedPatchProbeCommand", "")
                and len(dict(output.get("remediationFollowup") or {}).get("recommendedPatchCommands", [])) == 2
                and any("--profile-id 115-fast-2" in value for value in dict(output.get("remediationFollowup") or {}).get("recommendedPatchCommands", []))
                and len(dict(output.get("remediationFollowup") or {}).get("recommendedPatchProbeCommands", [])) == 2
                and any("--profile-id 115-fast-2" in value for value in dict(output.get("remediationFollowup") or {}).get("recommendedPatchProbeCommands", []))
                and "patch_and_probe_auth_profile.py --from-remediation-profile-id 115-fast-1" in dict(output.get("remediationFollowup") or {}).get("exactPatchHelper", ""),
                "scriptRemediationFollowupIncluded": dict(output.get("remediationFollowup") or {}).get("recommendedRuntimeSuccessCommand", "").endswith("tmp\\115_open-fast-candidate-evidence-2")
                and "create_fast_upload_candidate_task.py --from-remediation-profile-id 115-fast-2" in dict(output.get("remediationFollowup") or {}).get("exactRuntimeSuccessHelper", "")
                and dict(output.get("remediationFollowup") or {}).get("recommendedOverwriteVariantCommand", "").endswith("tmp\\115_open-fast-candidate-evidence")
                and "create_fast_upload_candidate_task.py --from-remediation-profile-id 115-fast-1" in dict(output.get("remediationFollowup") or {}).get("exactOverwriteVariantHelper", "")
                and "direct_select" in dict(output.get("remediationFollowup") or {}).get("conflictPolicyNote", "")
                and "auto_rename_new" in dict(output.get("remediationFollowup") or {}).get("providerConflictNotes", ""),
                "scriptExplicitTargetParentWins": second_output.get("resolvedTargetParentId") == "manual-fast-parent",
                "scriptNoRefreshSkipsAuthRefresh": len(refresh_calls) == 1 and second_output.get("refreshedAuthEvidence") is False,
                "scriptExplicitOutputsCreated": second_outputs_ok
                and second_output.get("taskJsonOutput") == str(second_task_json)
                and second_output.get("authEvidenceOutput") == str(second_auth_evidence),
                "scriptExactProfileDefaultsApplied": exact_output.get("defaultsSource") == "remediation:recommendedRuntimeSuccessCommand"
                and exact_output.get("resolvedTargetParentId") == "115-root-2",
                "scriptRuntimeOrphanDefaultsApplied": orphan_exact_output.get("defaultsSource") == "runtime_orphan:recommendedRuntimeSuccessCommand"
                and orphan_exact_output.get("resolvedTargetParentId") == "orphan-fast-root",
                "scriptRequiredFastInputs": output.get("requiredFastInputs") == ["sha1", "size"],
                "scriptAutoComputedSha1": bool(source_entry.get("sha1")),
                "scriptHasAutoTempFile": "--auto-temp-file" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasExactProfileArg": "--from-remediation-profile-id" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasRuntimeOrphanArg": "--from-runtime-orphan-profile" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasSha1Arg": "--sha1" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasGcidArg": "--gcid" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptHasEvidenceDirArg": "--evidence-dir" in SCRIPT_PATH.read_text(encoding="utf-8"),
                "scriptCandidateOnlyState": output.get("state") == "completed_candidate_only" and ((output.get("summary") or {}).get("completionKind") == "candidate_only"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
