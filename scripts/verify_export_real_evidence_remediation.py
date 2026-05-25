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
            "providersWithRefreshEvidenceCommand": 0,
            "providersWithRuntimeProbeCommand": 0,
            "providersWithLiveUploadCommand": 4,
            "providersWithFastCandidateCommand": 1,
            "providersWithRuntimeSuccessCommand": 2,
            "providersWithPostBootstrapRuntimeCommand": 6,
            "providersWithCreateCommand": 0,
            "providersWithBootstrapCommand": 0,
            "providersBlockedOnly": 0,
            "providersCandidateOnly": 1,
            "providersProbeOnly": 0,
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
                "gaps": ["基础证据已齐，但尚未记录到真实 runtime 成功样本"],
                "recommendedLiveUploadCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需直接覆盖同名文件，可改成 overwrite_existing。",
                "nextStep": "当前基础证据已齐，可直接运行统一的 runtime success helper。",
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
                "gaps": ["已有 fast-upload candidate 样本，但尚未记录到真实 runtime 成功样本"],
                "recommendedFastCandidateCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-1 --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-fast-candidate-evidence",
                "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id 115-1 --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-fast-candidate-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需直接覆盖同名文件，可改成 overwrite_existing。",
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
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 189cloud --auth-mode manual_cookie --display-name 189cloud-manual_cookie --cookie YOUR_COOKIE --set shareCode=YOUR_VALUE --set accessCode=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 189cloud --auth-mode manual_cookie --display-name 189cloud-manual_cookie --cookie YOUR_COOKIE --set shareCode=YOUR_VALUE --set accessCode=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 189cloud --target-profile-id YOUR_PROFILE_ID --md5 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\189cloud-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需直接覆盖同名文件，可改成 overwrite_existing。",
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
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key quark --auth-mode manual_cookie --display-name quark-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key quark --auth-mode manual_cookie --display-name quark-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider quark --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\quark-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需直接覆盖同名文件，可改成 overwrite_existing。",
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
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key baidu_netdisk --auth-mode manual_cookie --display-name baidu_netdisk-manual_cookie --cookie YOUR_COOKIE --set fileId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key baidu_netdisk --auth-mode manual_cookie --display-name baidu_netdisk-manual_cookie --cookie YOUR_COOKIE --set fileId=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider baidu_netdisk --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\baidu_netdisk-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需直接覆盖同名文件，可改成 overwrite_existing。",
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
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key xunlei --auth-mode manual_token --display-name xunlei-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key xunlei --auth-mode manual_token --display-name xunlei-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider xunlei --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\xunlei-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需直接覆盖同名文件，可改成 overwrite_existing。",
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
                "gaps": ["缺少通过的 auth validation 证据"],
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 123_open --auth-mode manual_token --display-name 123_open-manual_token --token YOUR_TOKEN --set parentFileId=YOUR_VALUE",
                "recommendedBootstrapCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 123_open --auth-mode manual_token --display-name 123_open-manual_token --token YOUR_TOKEN --set parentFileId=YOUR_VALUE --probe",
                "recommendedPostBootstrapRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider 123_open --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\123_open-post-bootstrap-runtime-evidence",
                "conflictPolicyNote": "当前 helper 默认使用 --conflict-policy auto_rename_new；如需直接覆盖同名文件，可改成 overwrite_existing。",
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
                "exportedHasLiveRuntimeSuccessCommand": "recommendedRuntimeSuccessCommand" in markdown
                and r"tmp\guangya-live-evidence" in markdown,
                "exportedHasFastRuntimeSuccessCommand": "recommendedRuntimeSuccessCommand" in markdown
                and r"tmp\115_open-fast-candidate-evidence" in markdown,
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
                "exportedHasConflictPolicyNote": "conflictPolicyNote:" in markdown and "overwrite_existing" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
