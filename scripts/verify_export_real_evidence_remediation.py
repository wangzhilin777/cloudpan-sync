from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.real_evidence_remediation import real_evidence_remediation_to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_real_evidence_remediation.py"
SPEC = importlib.util.spec_from_file_location("export_real_evidence_remediation", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
            "summary": {
                "providerCount": 6,
                "providersWithNoProfiles": 0,
                "providersNeedingAuthEvidence": 0,
                "providersNeedingListEvidence": 0,
            "providersNeedingMetadataEvidence": 0,
            "providersNeedingCreateDirEvidence": 0,
            "providersNeedingRuntimeSuccess": 6,
            "providersWithPatchCommand": 0,
            "providersWithPatchProbeCommand": 0,
            "providersWithRecreateProbeCommand": 1,
            "providersWithRefreshEvidenceCommand": 0,
            "providersWithPostRefreshRuntimeCommand": 1,
            "providersWithRuntimeProbeCommand": 0,
            "providersWithLiveUploadCommand": 4,
                "providersWithFastCandidateCommand": 1,
                "providersWithRuntimeSuccessCommand": 2,
                "providersWithPostBootstrapRuntimeCommand": 6,
                "providersWithPrimaryCommand": 6,
                "providersWithOverwriteVariantCommand": 6,
                "providersWithConflictPolicyNote": 6,
                "providersWithDeclaredConflictPolicies": 5,
                "providersWithProviderManagedOverwrite": 0,
                "providersWithOverwriteDowngrade": 5,
                "providersWithConflictUnsupported": 2,
            "providersWithCreateCommand": 0,
            "providersWithBootstrapCommand": 0,
            "providersBlockedOnly": 0,
            "providersCandidateOnly": 1,
            "providersProbeOnly": 0,
            "providersWithNoProfilesList": [],
            "providersNeedingAuthEvidenceList": [],
            "providersNeedingRuntimeSuccessList": ["115_open", "123_open", "189cloud", "baidu_netdisk", "guangya", "quark"],
            "providersWithRecreateProbeCommandList": ["guangya"],
            "providersWithPrimaryCommandList": ["115_open", "123_open", "189cloud", "baidu_netdisk", "guangya", "quark"],
            "providersWithOverwriteVariantCommandList": ["115_open", "123_open", "189cloud", "baidu_netdisk", "guangya", "quark"],
            "providersBlockedOnlyList": [],
            "providersCandidateOnlyList": ["115_open"],
            "providersProbeOnlyList": [],
        },
        "items": [
            {
                "providerKey": "guangya",
                "displayName": "Guangya",
                "profileCount": 1,
                "authReadyProfiles": 1,
                "writeReadyProfiles": 1,
                "recommendedAuthModes": ["manual_token"],
                "webLoginUrl": "https://guangyapan.com/",
                "requiredFieldHints": ["token or extra.authorization"],
                "needsAuthEvidence": False,
                "needsListEvidence": False,
                "needsMetadataEvidence": False,
                "needsCreateDirEvidence": False,
                "needsRuntimeSuccess": True,
                "runtimeBlockedOnly": False,
                "runtimeCandidateOnly": False,
                "runtimeProbeOnly": False,
                "runtimeOrphanProfiles": ["gy-orphan-1", "gy-orphan-2"],
                "needsSecretRefresh": True,
                "placeholderSecretFieldHints": ["token"],
                "declaredConflictPolicies": ["overwrite_existing", "auto_rename_new"],
                "supportsOverwrite": False,
                "supportsAutoRename": True,
                "overwriteBehavior": "downgrade_to_auto_rename",
                "overwriteSupportStatus": "downgrade_to_auto_rename",
                "autoRenameSupportStatus": "supported",
                "providerConflictNotes": "当前 Guangya fallback 上传链路已接受 overwrite_existing / auto_rename_new，但 overwrite_existing 仍会诚实降级为 auto_rename_new。",
                "gaps": ["基础证据已齐，但尚未记录到真实 runtime 成功样本"],
                "recommendedPatchCommands": [
                    r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id gy-1 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate",
                    r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id gy-2 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate",
                ],
                "recommendedPatchProbeCommands": [
                    r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-1 --set parentId=YOUR_REAL_PARENT_ID --write",
                    r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-2 --set parentId=YOUR_REAL_PARENT_ID --write",
                ],
                "recommendedPatchCommand": r".\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id gy-1 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate",
                "recommendedPatchProbeCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-1 --set parentId=YOUR_REAL_PARENT_ID --write",
                "recommendedRecreateProbeCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name Guangya --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe",
                "recommendedRecreateProbeCommands": [
                    r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-orphan-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-orphan-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe",
                    r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-orphan-2 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-orphan-2 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe",
                ],
                "recommendedLiveUploadCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence",
                "recommendedPostRefreshRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence",
                "recommendedPrimaryCommandLabel": "recreate_probe",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name Guangya --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-1 --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\guangya-live-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。",
                "nextStep": "当前档案仍含占位 token/cookie 等 secret 字段；先用真实凭证重建或编辑档案，再重跑 validation / live probe。",
            },
            {
                "providerKey": "115_open",
                "displayName": "115 Open",
                "profileCount": 1,
                "authReadyProfiles": 1,
                "writeReadyProfiles": 1,
                "recommendedAuthModes": ["manual_cookie"],
                "requiredFieldHints": ["cookie or extra.cookie_header"],
                "needsAuthEvidence": False,
                "needsListEvidence": False,
                "needsMetadataEvidence": False,
                "needsCreateDirEvidence": False,
                "needsRuntimeSuccess": True,
                "runtimeBlockedOnly": False,
                "runtimeCandidateOnly": True,
                "runtimeProbeOnly": False,
                "declaredConflictPolicies": [],
                "supportsOverwrite": False,
                "supportsAutoRename": False,
                "overwriteBehavior": "not_implemented",
                "overwriteSupportStatus": "unsupported",
                "autoRenameSupportStatus": "unsupported",
                "providerConflictNotes": "当前 115 Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。",
                "gaps": ["已有 fast-upload candidate 样本，但尚未记录到真实 runtime 成功样本"],
                "recommendedFastCandidateCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-1 --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-fast-candidate-evidence",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-1 --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-fast-candidate-evidence",
                "recommendedPrimaryCommandLabel": "runtime_success",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-1 --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-fast-candidate-evidence",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-1 --sha1 auto --auto-temp-file --conflict-policy overwrite_existing --evidence-dir tmp\115_open-fast-candidate-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。",
                "nextStep": "当前基础证据已齐，可直接运行统一的 runtime success helper。",
            },
            {
                "providerKey": "189cloud",
                "displayName": "Tianyi 189Cloud",
                "profileCount": 0,
                "authReadyProfiles": 0,
                "writeReadyProfiles": 0,
                "recommendedAuthModes": ["manual_cookie"],
                "requiredFieldHints": ["extra.shareCode", "extra.accessCode"],
                "needsAuthEvidence": True,
                "needsListEvidence": True,
                "needsMetadataEvidence": True,
                "needsCreateDirEvidence": True,
                "needsRuntimeSuccess": True,
                "runtimeBlockedOnly": False,
                "runtimeCandidateOnly": False,
                "runtimeProbeOnly": False,
                "declaredConflictPolicies": [],
                "supportsOverwrite": False,
                "supportsAutoRename": False,
                "overwriteBehavior": "readonly_auth_blocked",
                "overwriteSupportStatus": "unsupported",
                "autoRenameSupportStatus": "unsupported",
                "providerConflictNotes": "当前 189Cloud 已接入账号级 create_dir 写目录尝试，但 shareCode/accessCode-only 档案仍然只读，真实文件上传与同名冲突处理仍未声明为已支持。",
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 189cloud --auth-mode manual_cookie --display-name 189cloud-manual_cookie --cookie YOUR_COOKIE --set shareCode=YOUR_VALUE --set accessCode=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 189cloud --auth-mode manual_cookie --display-name 189cloud-manual_cookie --cookie YOUR_COOKIE --set shareCode=YOUR_VALUE --set accessCode=YOUR_VALUE --probe",
                "recommendedPrimaryCommandLabel": "bootstrap",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 189cloud --auth-mode manual_cookie --display-name 189cloud-manual_cookie --cookie YOUR_COOKIE --set shareCode=YOUR_VALUE --set accessCode=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 189cloud --target-profile-id YOUR_PROFILE_ID --md5 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\189cloud-post-bootstrap-runtime-evidence",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 189cloud --target-profile-id YOUR_PROFILE_ID --md5 auto --auto-temp-file --conflict-policy overwrite_existing --evidence-dir tmp\189cloud-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。",
                "nextStep": "先创建 `189cloud` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。",
            },
            {
                "providerKey": "quark",
                "displayName": "Quark",
                "profileCount": 0,
                "authReadyProfiles": 0,
                "writeReadyProfiles": 0,
                "recommendedAuthModes": ["manual_cookie"],
                "requiredFieldHints": ["extra.pwdId"],
                "needsAuthEvidence": True,
                "needsListEvidence": True,
                "needsMetadataEvidence": True,
                "needsCreateDirEvidence": True,
                "needsRuntimeSuccess": True,
                "runtimeBlockedOnly": False,
                "runtimeCandidateOnly": False,
                "runtimeProbeOnly": False,
                "declaredConflictPolicies": ["overwrite_existing", "auto_rename_new"],
                "supportsOverwrite": False,
                "supportsAutoRename": True,
                "overwriteBehavior": "downgrade_to_auto_rename",
                "overwriteSupportStatus": "downgrade_to_auto_rename",
                "autoRenameSupportStatus": "supported",
                "providerConflictNotes": "当前 Quark 已接入任务运行阶段真实本地文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。",
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key quark --auth-mode manual_cookie --display-name quark-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key quark --auth-mode manual_cookie --display-name quark-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE --probe",
                "recommendedPrimaryCommandLabel": "bootstrap",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key quark --auth-mode manual_cookie --display-name quark-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider quark --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\quark-post-bootstrap-runtime-evidence",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider quark --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\quark-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。",
                "nextStep": "先创建 `quark` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。",
            },
            {
                "providerKey": "baidu_netdisk",
                "displayName": "Baidu Netdisk",
                "profileCount": 0,
                "authReadyProfiles": 0,
                "writeReadyProfiles": 0,
                "recommendedAuthModes": ["manual_cookie"],
                "requiredFieldHints": ["extra.fileId"],
                "needsAuthEvidence": True,
                "needsListEvidence": True,
                "needsMetadataEvidence": True,
                "needsCreateDirEvidence": True,
                "needsRuntimeSuccess": True,
                "runtimeBlockedOnly": False,
                "runtimeCandidateOnly": False,
                "runtimeProbeOnly": False,
                "declaredConflictPolicies": ["overwrite_existing", "auto_rename_new"],
                "supportsOverwrite": False,
                "supportsAutoRename": True,
                "overwriteBehavior": "downgrade_to_auto_rename",
                "overwriteSupportStatus": "downgrade_to_auto_rename",
                "autoRenameSupportStatus": "supported",
                "providerConflictNotes": "当前 Baidu Netdisk 已接入任务运行阶段真实小文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。",
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key baidu_netdisk --auth-mode manual_cookie --display-name baidu_netdisk-manual_cookie --cookie YOUR_COOKIE --set fileId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key baidu_netdisk --auth-mode manual_cookie --display-name baidu_netdisk-manual_cookie --cookie YOUR_COOKIE --set fileId=YOUR_VALUE --probe",
                "recommendedPrimaryCommandLabel": "bootstrap",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key baidu_netdisk --auth-mode manual_cookie --display-name baidu_netdisk-manual_cookie --cookie YOUR_COOKIE --set fileId=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider baidu_netdisk --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\baidu_netdisk-post-bootstrap-runtime-evidence",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider baidu_netdisk --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\baidu_netdisk-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。",
                "nextStep": "先创建 `baidu_netdisk` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。",
            },
            {
                "providerKey": "xunlei",
                "displayName": "Xunlei Drive",
                "profileCount": 0,
                "authReadyProfiles": 0,
                "writeReadyProfiles": 0,
                "recommendedAuthModes": ["manual_token"],
                "requiredFieldHints": ["extra.deviceId"],
                "needsAuthEvidence": True,
                "needsListEvidence": True,
                "needsMetadataEvidence": True,
                "needsCreateDirEvidence": True,
                "needsRuntimeSuccess": True,
                "runtimeBlockedOnly": False,
                "runtimeCandidateOnly": False,
                "runtimeProbeOnly": False,
                "declaredConflictPolicies": ["overwrite_existing", "auto_rename_new"],
                "supportsOverwrite": False,
                "supportsAutoRename": True,
                "overwriteBehavior": "downgrade_to_auto_rename",
                "overwriteSupportStatus": "downgrade_to_auto_rename",
                "autoRenameSupportStatus": "supported",
                "providerConflictNotes": "当前 Xunlei 已接入任务运行阶段真实本地文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。",
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key xunlei --auth-mode manual_token --display-name xunlei-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key xunlei --auth-mode manual_token --display-name xunlei-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE --probe",
                "recommendedPrimaryCommandLabel": "bootstrap",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key xunlei --auth-mode manual_token --display-name xunlei-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider xunlei --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\xunlei-post-bootstrap-runtime-evidence",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider xunlei --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\xunlei-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。",
                "nextStep": "先创建 `xunlei` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。",
            },
            {
                "providerKey": "123_open",
                "displayName": "123Pan Open",
                "profileCount": 0,
                "authReadyProfiles": 0,
                "writeReadyProfiles": 0,
                "recommendedAuthModes": ["manual_token"],
                "requiredFieldHints": ["extra.parentFileId"],
                "needsAuthEvidence": True,
                "needsListEvidence": True,
                "needsMetadataEvidence": True,
                "needsCreateDirEvidence": True,
                "needsRuntimeSuccess": True,
                "runtimeBlockedOnly": False,
                "runtimeCandidateOnly": False,
                "runtimeProbeOnly": False,
                "declaredConflictPolicies": ["overwrite_existing", "auto_rename_new"],
                "supportsOverwrite": False,
                "supportsAutoRename": True,
                "overwriteBehavior": "downgrade_to_auto_rename",
                "overwriteSupportStatus": "downgrade_to_auto_rename",
                "autoRenameSupportStatus": "supported",
                "providerConflictNotes": "当前 123Pan Open 已接入任务运行阶段真实小文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。",
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 123_open --auth-mode manual_token --display-name 123_open-manual_token --token YOUR_TOKEN --set parentFileId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 123_open --auth-mode manual_token --display-name 123_open-manual_token --token YOUR_TOKEN --set parentFileId=YOUR_VALUE --probe",
                "recommendedPrimaryCommandLabel": "bootstrap",
                "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 123_open --auth-mode manual_token --display-name 123_open-manual_token --token YOUR_TOKEN --set parentFileId=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider 123_open --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\123_open-post-bootstrap-runtime-evidence",
                "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider 123_open --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\123_open-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。",
                "nextStep": "先创建 `123_open` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。",
            },
        ],
    }

    original_root = export_script.ROOT
    original_builder = export_script.build_real_evidence_remediation_bundle
    original_renderer = export_script.real_evidence_remediation_to_markdown

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.build_real_evidence_remediation_bundle = lambda: synthetic_payload
        export_script.real_evidence_remediation_to_markdown = real_evidence_remediation_to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.build_real_evidence_remediation_bundle = original_builder
            export_script.real_evidence_remediation_to_markdown = original_renderer

        output_path = tmp_root / "docs" / "12-REAL_EVIDENCE_REMEDIATION_GUIDE.md"
        markdown = output_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "exportedFileExists": True,
                "exportedHasTitle": "# CloudPan Sync 真实联调补救指南" in markdown,
                "exportedHasLiveUploadSummary": "providersWithLiveUploadCommand: `4`" in markdown,
                "exportedHasFastCandidateSummary": "providersWithFastCandidateCommand: `1`" in markdown,
                "exportedHasRuntimeSuccessSummary": "providersWithRuntimeSuccessCommand: `2`" in markdown,
                "exportedHasPostBootstrapRuntimeSummary": "providersWithPostBootstrapRuntimeCommand: `6`" in markdown,
                "exportedHasPrimaryCommandSummary": "providersWithPrimaryCommand: `6`" in markdown,
                "exportedHasRecreateProbeSummary": "providersWithRecreateProbeCommand: `1`" in markdown,
                "exportedHasOverwriteVariantSummary": "providersWithOverwriteVariantCommand: `6`" in markdown,
                "exportedHasConflictPolicyNoteSummary": "providersWithConflictPolicyNote: `6`" in markdown,
                "exportedHasPostRefreshRuntimeSummary": "providersWithPostRefreshRuntimeCommand: `1`" in markdown,
                "exportedHasDeclaredConflictPolicySummary": "providersWithDeclaredConflictPolicies: `5`" in markdown,
                "exportedHasOverwriteDowngradeSummary": "providersWithOverwriteDowngrade: `5`" in markdown,
                "exportedHasConflictUnsupportedSummary": "providersWithConflictUnsupported: `2`" in markdown,
                "exportedHasProviderSummary": "- providerSummary: `noProfiles=(none)` `needAuth=(none)` `needRuntime=115_open, 123_open, 189cloud, baidu_netdisk, guangya, quark` `recreateProbe=guangya` `primaryCommand=115_open, 123_open, 189cloud, baidu_netdisk, guangya, quark` `overwriteVariant=115_open, 123_open, 189cloud, baidu_netdisk, guangya, quark` `blockedOnly=(none)` `candidateOnly=115_open` `probeOnly=(none)`" in markdown,
                "exportedHasLiveRuntimeSuccessCommand": "recommendedRuntimeSuccessCommand" in markdown
                and r"tmp\guangya-live-evidence" in markdown,
                "exportedHasFastRuntimeSuccessCommand": "recommendedRuntimeSuccessCommand" in markdown
                and r"tmp\115_open-fast-candidate-evidence" in markdown,
                "exportedHasPostRefreshRuntimeCommand": "recommendedPostRefreshRuntimeCommand" in markdown
                and r"tmp\guangya-live-evidence" in markdown,
                "exportedHasPrimaryCommand": "recommendedPrimaryCommand" in markdown
                and "label=recreate_probe" in markdown
                and "label=bootstrap" in markdown,
                "exportedHasMultiPatchCommandList": "recommendedPatchCommands: count=`2`" in markdown
                and "--profile-id gy-1 " in markdown
                and "--profile-id gy-2 " in markdown,
                "exportedHasMultiPatchProbeCommandList": "recommendedPatchProbeCommands: count=`2`" in markdown
                and "--profile-id gy-1 " in markdown
                and "--profile-id gy-2 " in markdown,
                "exportedHasRecreateProbeCommand": "recommendedRecreateProbeCommand" in markdown
                and "placeholderSecretFieldHints: `token`" in markdown
                and "create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token" in markdown,
                "exportedHasExactRecreateHelper": "exactRecreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-orphan-profile" in markdown,
                "exportedHasPostBootstrapRuntimeCommand": "recommendedPostBootstrapRuntimeCommand" in markdown
                and r"tmp\189cloud-post-bootstrap-runtime-evidence" in markdown,
                "exportedHasLivePostBootstrapHelpers": r"tmp\quark-post-bootstrap-runtime-evidence" in markdown
                and r"tmp\baidu_netdisk-post-bootstrap-runtime-evidence" in markdown
                and r"tmp\xunlei-post-bootstrap-runtime-evidence" in markdown
                and r"tmp\123_open-post-bootstrap-runtime-evidence" in markdown,
                "exportedPostBootstrapNextStepMentionsRuntimeFollowup": "post-bootstrap runtime helper" in markdown
                and "runtime success" in markdown,
                "exportedHasCandidateOnlyFlag": "runtimeCandidateOnly=True" in markdown,
                "exportedShowsConflictPolicyChoice": "--conflict-policy auto_rename_new" in markdown,
                "exportedHasOverwriteVariantCommand": "recommendedOverwriteVariantCommand" in markdown and "--conflict-policy overwrite_existing" in markdown,
                "exportedHasConflictPolicyNote": "conflictPolicyNote:" in markdown and "overwrite_existing" in markdown,
                "exportedHasConflictSupportRows": "conflictSupport:" in markdown and "providerConflictNotes:" in markdown and "overwrite=downgrade_to_auto_rename" in markdown and "overwrite=unsupported" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
