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
                    and f"- providersWithPatchCommand: `{summary.get('providersWithPatchCommand', 0)}`" in markdown
                    and f"- providersWithPatchProbeCommand: `{summary.get('providersWithPatchProbeCommand', 0)}`" in markdown
                    and f"- providersWithRecreateProbeCommand: `{summary.get('providersWithRecreateProbeCommand', 0)}`" in markdown
                    and f"- providersWithPrimaryCommand: `{summary.get('providersWithPrimaryCommand', 0)}`" in markdown
                    and f"- providersNeedingSecretRefresh: `{summary.get('providersNeedingSecretRefresh', 0)}`" in markdown
                    and f"- providersPlaceholderLiveRejected: `{summary.get('providersPlaceholderLiveRejected', 0)}`" in markdown
                    and f"- providerSummary: `noProfiles={', '.join(summary.get('providersWithNoProfilesList', [])) or '(none)'}` `needAuth={', '.join(summary.get('providersNeedingAuthEvidenceList', [])) or '(none)'}` `needRuntime={', '.join(summary.get('providersNeedingRuntimeSuccessList', [])) or '(none)'}` `needSecretRefresh={', '.join(summary.get('providersNeedingSecretRefreshList', [])) or '(none)'}` `placeholderLiveRejected={', '.join(summary.get('providersPlaceholderLiveRejectedList', [])) or '(none)'}` `recreateProbe={', '.join(summary.get('providersWithRecreateProbeCommandList', [])) or '(none)'}` `primaryCommand={', '.join(summary.get('providersWithPrimaryCommandList', [])) or '(none)'}` `overwriteVariant={', '.join(summary.get('providersWithOverwriteVariantCommandList', [])) or '(none)'}` `blockedOnly={', '.join(summary.get('providersBlockedOnlyList', [])) or '(none)'}` `candidateOnly={', '.join(summary.get('providersCandidateOnlyList', [])) or '(none)'}` `probeOnly={', '.join(summary.get('providersProbeOnlyList', [])) or '(none)'}` `runtimeOrphanOnly={', '.join(summary.get('providersRuntimeOrphanOnlyList', [])) or '(none)'}`" in markdown
                ),
                "summaryShowsExpectedRuntimeRemediationCounts": (
                    summary.get("providersNeedingRuntimeSuccess") == 7
                    and summary.get("providersWithPostBootstrapRuntimeCommand") == 6
                    and summary.get("providersWithPatchCommand") == 4
                    and summary.get("providersWithPatchProbeCommand") == 4
                    and summary.get("providersWithRecreateProbeCommand") == 4
                    and summary.get("providersWithOverwriteVariantCommand") == 6
                    and summary.get("providersWithConflictPolicyNote") == 6
                    and summary.get("providersWithDeclaredConflictPolicies") == 8
                    and summary.get("providersWithProviderManagedOverwrite") == 1
                    and summary.get("providersWithOverwriteDowngrade") == 7
                    and summary.get("providersWithConflictUnsupported") == 1
                    and summary.get("providersWithCreateCommand") == 6
                    and summary.get("providersWithBootstrapCommand") == 6
                    and summary.get("providersWithPostRefreshRuntimeCommand") == 0
                    and summary.get("providersWithPrimaryCommand") == 10
                    and summary.get("providersWithNoProfilesList") == ["115_open", "123_open", "189cloud", "baidu_netdisk", "quark", "xunlei"]
                    and summary.get("providersNeedingAuthEvidenceList") == ["115_open", "123_open", "189cloud", "aliyundrive_open", "baidu_netdisk", "guangya", "pikpak", "quark", "uc", "xunlei"]
                    and summary.get("providersNeedingRuntimeSuccessList") == ["115_open", "123_open", "189cloud", "aliyundrive_open", "baidu_netdisk", "quark", "xunlei"]
                    and summary.get("providersWithRecreateProbeCommandList") == ["aliyundrive_open", "guangya", "pikpak", "uc"]
                    and summary.get("providersWithPrimaryCommandList") == ["115_open", "123_open", "189cloud", "aliyundrive_open", "baidu_netdisk", "guangya", "pikpak", "quark", "uc", "xunlei"]
                    and summary.get("providersWithOverwriteVariantCommandList") == ["115_open", "123_open", "189cloud", "baidu_netdisk", "quark", "xunlei"]
                    and summary.get("providersBlockedOnlyList") == []
                    and summary.get("providersCandidateOnlyList") == []
                    and summary.get("providersProbeOnlyList") == []
                    and summary.get("providersRuntimeOrphanOnlyList") == []
                    and summary.get("providersNeedingSecretRefreshList") == ["aliyundrive_open", "guangya", "pikpak", "uc"]
                    and summary.get("providersPlaceholderLiveRejectedList") == ["aliyundrive_open", "guangya", "pikpak", "uc"]
                ),
                "cloud115SectionKeepsFastPostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in cloud115
                    and "create_fast_upload_candidate_task.py" in cloud115
                    and "exactCreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-provider 115_open`" in cloud115
                    and "exactPostBootstrapRuntimeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_fast_upload_candidate_task.py --from-remediation-provider 115_open`" in cloud115
                    and "--conflict-policy auto_rename_new" in cloud115
                    and "recommendedOverwriteVariantCommand" in cloud115
                    and "recommendedPrimaryCommand" in cloud115
                    and "label=post_bootstrap_runtime" in cloud115
                    and "--conflict-policy overwrite_existing" in cloud115
                    and "probe_only_runtime_write_check" in cloud115
                    and "tmp\\115_open-post-bootstrap-runtime-evidence" in cloud115
                    and "先不要把首条样本建立在 overwrite_existing 上" in cloud115
                ),
                "quarkSectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in quark
                    and "create_live_upload_task.py" in quark
                    and "exactCreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-provider quark`" in quark
                    and "exactPostBootstrapRuntimeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-remediation-provider quark`" in quark
                    and "--conflict-policy auto_rename_new" in quark
                    and "recommendedOverwriteVariantCommand" in quark
                    and "label=post_bootstrap_runtime" in quark
                    and "overwrite=downgrade_to_auto_rename" in quark
                    and "tmp\\quark-post-bootstrap-runtime-evidence" in quark
                    and "会诚实降级为自动改名" in quark
                ),
                "cloud189SectionKeepsFastPostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in cloud189
                    and "create_fast_upload_candidate_task.py" in cloud189
                    and "exactCreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-provider 189cloud`" in cloud189
                    and "exactPostBootstrapRuntimeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_fast_upload_candidate_task.py --from-remediation-provider 189cloud`" in cloud189
                    and "conflictSupport: `declared=(none)` `overwrite=unsupported` `auto_rename=unsupported`" in cloud189
                    and "tmp\\189cloud-post-bootstrap-runtime-evidence" in cloud189
                ),
                "baiduSectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in baidu
                    and "create_live_upload_task.py" in baidu
                    and "exactCreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-provider baidu_netdisk`" in baidu
                    and "exactPostBootstrapRuntimeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-remediation-provider baidu_netdisk`" in baidu
                    and "tmp\\baidu_netdisk-post-bootstrap-runtime-evidence" in baidu
                ),
                "xunleiSectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in xunlei
                    and "create_live_upload_task.py" in xunlei
                    and "exactCreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-provider xunlei`" in xunlei
                    and "exactPostBootstrapRuntimeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-remediation-provider xunlei`" in xunlei
                    and "tmp\\xunlei-post-bootstrap-runtime-evidence" in xunlei
                ),
                "pan123SectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in pan123
                    and "create_live_upload_task.py" in pan123
                    and "exactCreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-provider 123_open`" in pan123
                    and "exactPostBootstrapRuntimeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-remediation-provider 123_open`" in pan123
                    and "tmp\\123_open-post-bootstrap-runtime-evidence" in pan123
                ),
                "aliyunSectionUsesRecreateProbePath": (
                    "recommendedRecreateProbeCommand" in aliyun
                    and "label=recreate_probe" in aliyun
                    and "create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe" in aliyun
                    and "exactPatchHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-remediation-profile-id 22173a49-2206-4da8-8624-9bab7bbbe64b`" in aliyun
                    and "exactRecreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-profile-id 22173a49-2206-4da8-8624-9bab7bbbe64b`" in aliyun
                    and "placeholderSecretFieldHints: `token`" in aliyun
                    and "liveRejected: profiles=`aliyun-bootstrap` placeholderProfiles=`aliyun-bootstrap` statuses=`404`" in aliyun
                    and "当前档案仍含占位 token/cookie 等 secret 字段" in aliyun
                    and "recommendedPostBootstrapRuntimeCommand" not in aliyun
                ),
                "guangyaSectionUsesRecreateProbePath": (
                    "recommendedRecreateProbeCommand" in guangya
                    and "recommendedPatchCommands: count=`6`" in guangya
                    and "recommendedPatchProbeCommands: count=`6`" in guangya
                    and "exactPatchHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-remediation-profile-id 0318479d-4669-415f-9083-7aecc102bf90`" in guangya
                    and "exactRecreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-profile-id 0318479d-4669-415f-9083-7aecc102bf90`" in guangya
                    and "patch_auth_profile_extra.py --profile-id gy-live-1 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate" in guangya
                    and "patch_and_probe_auth_profile.py --profile-id gy-live-1 --set parentId=YOUR_REAL_PARENT_ID --write" in guangya
                    and "placeholderSecretFieldHints: `token`" in guangya
                    and "liveRejected: profiles=`guangya-restore-gy-live-1, gy-patch-probe-1` placeholderProfiles=`guangya-restore-gy-live-1` statuses=`401`" in guangya
                    and "recommendedPostBootstrapRuntimeCommand" not in guangya
                ),
                "ucSectionUsesOrphanRecreateProbePath": (
                    "recommendedRecreateProbeCommand" in uc
                    and "label=recreate_probe" in uc
                    and "create_auth_profile_stub.py --provider-key uc --auth-mode manual_cookie --display-name uc-restore-uc-live-1 --cookie YOUR_COOKIE --set pwdId=YOUR_SHARE_PWD_ID --probe" in uc
                    and "exactPatchHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-remediation-profile-id uc-live-1`" in uc
                    and "exactRecreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-profile-id uc-live-1`" in uc
                    and "liveRejected: profiles=`uc-restore-uc-live-1` placeholderProfiles=`uc-restore-uc-live-1` statuses=`404`" in uc
                    and "recommendedPostBootstrapRuntimeCommand" not in uc
                ),
                "pikpakSectionUsesOrphanRecreateProbePath": (
                    "recommendedRecreateProbeCommand" in pikpak
                    and "label=recreate_probe" in pikpak
                    and "create_auth_profile_stub.py --provider-key pikpak --auth-mode manual_token --display-name pikpak-restore-pikpak-live-1 --token YOUR_TOKEN --set deviceId=YOUR_DEVICE_ID --probe" in pikpak
                    and "exactPatchHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-remediation-profile-id pikpak-live-1`" in pikpak
                    and "exactRecreateHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-profile-id pikpak-live-1`" in pikpak
                    and "liveRejected: profiles=`pikpak-restore-pikpak-live-1` placeholderProfiles=`pikpak-restore-pikpak-live-1` statuses=`401`" in pikpak
                    and "recommendedPostBootstrapRuntimeCommand" not in pikpak
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
