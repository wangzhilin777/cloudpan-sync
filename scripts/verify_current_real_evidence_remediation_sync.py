from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.real_evidence_remediation import build_real_evidence_remediation_bundle


def _section(markdown: str, provider_key: str) -> str:
    marker = f"### {provider_key} - "
    start = markdown.find(marker)
    if start < 0:
        return ""
    next_start = markdown.find("\n### ", start + 1)
    if next_start < 0:
        return markdown[start:]
    return markdown[start:next_start]


def main() -> None:
    payload = build_real_evidence_remediation_bundle()
    summary = dict(payload.get("summary") or {})
    markdown = (ROOT / "docs" / "12-REAL_EVIDENCE_REMEDIATION_GUIDE.md").read_text(encoding="utf-8")

    cloud115 = _section(markdown, "115_open")
    guangya = _section(markdown, "guangya")
    quark = _section(markdown, "quark")
    cloud189 = _section(markdown, "189cloud")
    baidu = _section(markdown, "baidu_netdisk")
    xunlei = _section(markdown, "xunlei")
    pan123 = _section(markdown, "123_open")
    aliyun = _section(markdown, "aliyundrive_open")
    uc = _section(markdown, "uc")
    pikpak = _section(markdown, "pikpak")

    print(
        json.dumps(
            {
                "summaryHasCurrentRemediationCounts": (
                    f"- providersNeedingRuntimeSuccess: `{summary.get('providersNeedingRuntimeSuccess', 0)}`" in markdown
                    and f"- providersWithPostBootstrapRuntimeCommand: `{summary.get('providersWithPostBootstrapRuntimeCommand', 0)}`" in markdown
                    and f"- providersWithOverwriteVariantCommand: `{summary.get('providersWithOverwriteVariantCommand', 0)}`" in markdown
                    and f"- providersWithConflictPolicyNote: `{summary.get('providersWithConflictPolicyNote', 0)}`" in markdown
                    and f"- providersWithDeclaredConflictPolicies: `{summary.get('providersWithDeclaredConflictPolicies', 0)}`" in markdown
                    and f"- providersWithProviderManagedOverwrite: `{summary.get('providersWithProviderManagedOverwrite', 0)}`" in markdown
                    and f"- providersWithOverwriteDowngrade: `{summary.get('providersWithOverwriteDowngrade', 0)}`" in markdown
                    and f"- providersWithConflictUnsupported: `{summary.get('providersWithConflictUnsupported', 0)}`" in markdown
                    and f"- providersWithCreateCommand: `{summary.get('providersWithCreateCommand', 0)}`" in markdown
                    and f"- providersWithBootstrapCommand: `{summary.get('providersWithBootstrapCommand', 0)}`" in markdown
                    and f"- providersWithPostRefreshRuntimeCommand: `{summary.get('providersWithPostRefreshRuntimeCommand', 0)}`" in markdown
                    and f"- providersWithRecreateProbeCommand: `{summary.get('providersWithRecreateProbeCommand', 0)}`" in markdown
                    and f"- providersWithPrimaryCommand: `{summary.get('providersWithPrimaryCommand', 0)}`" in markdown
                    and f"- providersRuntimeOrphanOnly: `{summary.get('providersRuntimeOrphanOnly', 0)}`" in markdown
                    and f"- providerSummary: `noProfiles={', '.join(summary.get('providersWithNoProfilesList', [])) or '(none)'}` `needAuth={', '.join(summary.get('providersNeedingAuthEvidenceList', [])) or '(none)'}` `needRuntime={', '.join(summary.get('providersNeedingRuntimeSuccessList', [])) or '(none)'}` `recreateProbe={', '.join(summary.get('providersWithRecreateProbeCommandList', [])) or '(none)'}` `primaryCommand={', '.join(summary.get('providersWithPrimaryCommandList', [])) or '(none)'}` `overwriteVariant={', '.join(summary.get('providersWithOverwriteVariantCommandList', [])) or '(none)'}` `blockedOnly={', '.join(summary.get('providersBlockedOnlyList', [])) or '(none)'}` `candidateOnly={', '.join(summary.get('providersCandidateOnlyList', [])) or '(none)'}` `probeOnly={', '.join(summary.get('providersProbeOnlyList', [])) or '(none)'}` `runtimeOrphanOnly={', '.join(summary.get('providersRuntimeOrphanOnlyList', [])) or '(none)'}`" in markdown
                ),
                "summaryShowsExpectedRuntimeRemediationCounts": (
                    summary.get("providersNeedingRuntimeSuccess") == 7
                    and summary.get("providersWithPostBootstrapRuntimeCommand") == 6
                    and summary.get("providersWithPatchCommand") == 2
                    and summary.get("providersWithPatchProbeCommand") == 2
                    and summary.get("providersWithRecreateProbeCommand") == 4
                    and summary.get("providersWithOverwriteVariantCommand") == 6
                    and summary.get("providersWithConflictPolicyNote") == 6
                    and summary.get("providersWithDeclaredConflictPolicies") == 8
                    and summary.get("providersWithProviderManagedOverwrite") == 1
                    and summary.get("providersWithOverwriteDowngrade") == 7
                    and summary.get("providersWithConflictUnsupported") == 1
                    and summary.get("providersWithCreateCommand") == 8
                    and summary.get("providersWithBootstrapCommand") == 8
                    and summary.get("providersWithPostRefreshRuntimeCommand") == 0
                    and summary.get("providersWithPrimaryCommand") == 10
                    and summary.get("providersWithNoProfilesList") == ["115_open", "123_open", "189cloud", "baidu_netdisk", "pikpak", "quark", "uc", "xunlei"]
                    and summary.get("providersNeedingAuthEvidenceList") == ["115_open", "123_open", "189cloud", "aliyundrive_open", "baidu_netdisk", "guangya", "pikpak", "quark", "uc", "xunlei"]
                    and summary.get("providersNeedingRuntimeSuccessList") == ["115_open", "123_open", "189cloud", "aliyundrive_open", "baidu_netdisk", "quark", "xunlei"]
                    and summary.get("providersWithRecreateProbeCommandList") == ["aliyundrive_open", "guangya", "pikpak", "uc"]
                    and summary.get("providersWithPrimaryCommandList") == ["115_open", "123_open", "189cloud", "aliyundrive_open", "baidu_netdisk", "guangya", "pikpak", "quark", "uc", "xunlei"]
                    and summary.get("providersWithOverwriteVariantCommandList") == ["115_open", "123_open", "189cloud", "baidu_netdisk", "quark", "xunlei"]
                    and summary.get("providersBlockedOnlyList") == []
                    and summary.get("providersCandidateOnlyList") == []
                    and summary.get("providersProbeOnlyList") == []
                    and summary.get("providersRuntimeOrphanOnlyList") == ["guangya", "pikpak", "uc"]
                ),
                "cloud115SectionKeepsFastPostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in cloud115
                    and "create_fast_upload_candidate_task.py" in cloud115
                    and "--conflict-policy auto_rename_new" in cloud115
                    and "recommendedOverwriteVariantCommand" in cloud115
                    and "recommendedPrimaryCommand" in cloud115
                    and "label=post_bootstrap_runtime" in cloud115
                    and "--conflict-policy overwrite_existing" in cloud115
                    and "conflictPolicyNote:" in cloud115
                    and "overwrite_existing" in cloud115
                    and "probe_only_runtime_write_check" in cloud115
                    and "providerConflictNotes:" in cloud115
                    and "tmp\\115_open-post-bootstrap-runtime-evidence" in cloud115
                    and "先不要把首条样本建立在 overwrite_existing 上" in cloud115
                ),
                "quarkSectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in quark
                    and "create_live_upload_task.py" in quark
                    and "--conflict-policy auto_rename_new" in quark
                    and "recommendedOverwriteVariantCommand" in quark
                    and "recommendedPrimaryCommand" in quark
                    and "label=post_bootstrap_runtime" in quark
                    and "--conflict-policy overwrite_existing" in quark
                    and "conflictPolicyNote:" in quark
                    and "overwrite_existing" in quark
                    and "overwrite=downgrade_to_auto_rename" in quark
                    and "providerConflictNotes:" in quark
                    and "tmp\\quark-post-bootstrap-runtime-evidence" in quark
                    and "会诚实降级为自动改名" in quark
                ),
                "cloud189SectionKeepsFastPostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in cloud189
                    and "create_fast_upload_candidate_task.py" in cloud189
                    and "--conflict-policy auto_rename_new" in cloud189
                    and "recommendedOverwriteVariantCommand" in cloud189
                    and "recommendedPrimaryCommand" in cloud189
                    and "label=post_bootstrap_runtime" in cloud189
                    and "--conflict-policy overwrite_existing" in cloud189
                    and "conflictPolicyNote:" in cloud189
                    and "overwrite_existing" in cloud189
                    and "conflictSupport: `declared=(none)` `overwrite=unsupported` `auto_rename=unsupported`" in cloud189
                    and "providerConflictNotes:" in cloud189
                    and "tmp\\189cloud-post-bootstrap-runtime-evidence" in cloud189
                ),
                "baiduSectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in baidu
                    and "create_live_upload_task.py" in baidu
                    and "--conflict-policy auto_rename_new" in baidu
                    and "recommendedOverwriteVariantCommand" in baidu
                    and "recommendedPrimaryCommand" in baidu
                    and "label=post_bootstrap_runtime" in baidu
                    and "--conflict-policy overwrite_existing" in baidu
                    and "conflictPolicyNote:" in baidu
                    and "overwrite_existing" in baidu
                    and "conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported`" in baidu
                    and "providerConflictNotes:" in baidu
                    and "tmp\\baidu_netdisk-post-bootstrap-runtime-evidence" in baidu
                ),
                "xunleiSectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in xunlei
                    and "create_live_upload_task.py" in xunlei
                    and "--conflict-policy auto_rename_new" in xunlei
                    and "recommendedOverwriteVariantCommand" in xunlei
                    and "recommendedPrimaryCommand" in xunlei
                    and "label=post_bootstrap_runtime" in xunlei
                    and "--conflict-policy overwrite_existing" in xunlei
                    and "conflictPolicyNote:" in xunlei
                    and "overwrite_existing" in xunlei
                    and "conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported`" in xunlei
                    and "providerConflictNotes:" in xunlei
                    and "tmp\\xunlei-post-bootstrap-runtime-evidence" in xunlei
                ),
                "pan123SectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in pan123
                    and "create_live_upload_task.py" in pan123
                    and "--conflict-policy auto_rename_new" in pan123
                    and "recommendedOverwriteVariantCommand" in pan123
                    and "recommendedPrimaryCommand" in pan123
                    and "label=post_bootstrap_runtime" in pan123
                    and "--conflict-policy overwrite_existing" in pan123
                    and "conflictPolicyNote:" in pan123
                    and "overwrite_existing" in pan123
                    and "conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported`" in pan123
                    and "providerConflictNotes:" in pan123
                    and "tmp\\123_open-post-bootstrap-runtime-evidence" in pan123
                ),
                "aliyunSectionUsesRecreateProbePath": (
                    "recommendedRecreateProbeCommand" in aliyun
                    and "recommendedPrimaryCommand" in aliyun
                    and "label=recreate_probe" in aliyun
                    and "create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe" in aliyun
                    and "placeholderSecretFieldHints: `token`" in aliyun
                    and "tok-demo" not in aliyun
                    and "recommendedRefreshEvidenceCommand" not in aliyun
                    and "recommendedPostRefreshRuntimeCommand" not in aliyun
                    and "recommendedPostBootstrapRuntimeCommand" not in aliyun
                ),
                "guangyaSectionUsesRecreateProbePath": (
                    "runtimeOrphanProfiles: `gy-live-1, gy-live-2, gy-live-defaults-1, gy-orphan-live-1`" in guangya
                    and "recommendedRecreateProbeCommand" in guangya
                    and "recommendedRecreateProbeCommands: count=`4`" in guangya
                    and "recommendedPatchCommands: count=`2`" in guangya
                    and "recommendedPatchProbeCommands: count=`2`" in guangya
                    and "exactPatchHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-remediation-profile-id 0318479d-4669-415f-9083-7aecc102bf90`" in guangya
                    and "recommendedPrimaryCommand" in guangya
                    and "label=recreate_probe" in guangya
                    and "patch_auth_profile_extra.py --profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate" in guangya
                    and "patch_auth_profile_extra.py --profile-id 08684618-ea29-48a4-b603-2e40cdc37c3d --set parentId=YOUR_REAL_PARENT_ID --write --revalidate" in guangya
                    and "patch_and_probe_auth_profile.py --profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write" in guangya
                    and "patch_and_probe_auth_profile.py --profile-id 08684618-ea29-48a4-b603-2e40cdc37c3d --set parentId=YOUR_REAL_PARENT_ID --write" in guangya
                    and "create_auth_profile_stub.py --profile-id gy-live-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe" in guangya
                    and "create_auth_profile_stub.py --profile-id gy-live-2 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-2 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe" in guangya
                    and "create_auth_profile_stub.py --profile-id gy-live-defaults-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-defaults-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe" in guangya
                    and "create_auth_profile_stub.py --profile-id gy-orphan-live-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-orphan-live-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe" in guangya
                    and "exactRecreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-orphan-profile gy-orphan-live-1`" in guangya
                    and "placeholderSecretFieldHints: `token`" in guangya
                    and "recommendedPostRefreshRuntimeCommand" not in guangya
                ),
                "ucSectionUsesOrphanRecreateProbePath": (
                    "runtimeOrphanProfiles: `uc-live-1`" in uc
                    and "recommendedRecreateProbeCommand" in uc
                    and "recommendedPrimaryCommand" in uc
                    and "label=recreate_probe" in uc
                    and "create_auth_profile_stub.py --profile-id uc-live-1 --provider-key uc --auth-mode manual_cookie --display-name uc-restore-uc-live-1 --cookie YOUR_COOKIE --set pwdId=YOUR_SHARE_PWD_ID --probe" in uc
                    and "recommendedPostBootstrapRuntimeCommand" not in uc
                ),
                "pikpakSectionUsesOrphanRecreateProbePath": (
                    "runtimeOrphanProfiles: `pikpak-live-1`" in pikpak
                    and "recommendedRecreateProbeCommand" in pikpak
                    and "recommendedPrimaryCommand" in pikpak
                    and "label=recreate_probe" in pikpak
                    and "create_auth_profile_stub.py --profile-id pikpak-live-1 --provider-key pikpak --auth-mode manual_token --display-name pikpak-restore-pikpak-live-1 --token YOUR_TOKEN --set deviceId=YOUR_DEVICE_ID --probe" in pikpak
                    and "recommendedPostBootstrapRuntimeCommand" not in pikpak
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
