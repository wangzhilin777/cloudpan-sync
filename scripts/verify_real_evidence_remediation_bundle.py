from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.real_evidence_remediation import (
    _create_command_for_provider,
    _post_bootstrap_runtime_command_for_provider,
    build_real_evidence_remediation_bundle,
    real_evidence_remediation_to_markdown,
)
from cloudpan_sync.provider_auth_hints import capture_field_hints, provider_auth_modes
from cloudpan_sync import webapp
from fastapi.testclient import TestClient


def main() -> None:
    synthetic_report = {
        "items": [
            {
                "providerKey": "guangya",
                "displayName": "Guangya",
                "authEvidence": {"ok": True},
                "listEvidence": {"ok": True},
                "metadataEvidence": {"ok": True},
                "createDirEvidence": {"ok": True},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0, "orphanProfileCount": 1, "orphanProfiles": ["gy-orphan"]},
                "gaps": ["基础证据已齐，但尚未记录到真实 runtime 成功样本", "已有 runtime 样本，但对应 auth profile 未保存在当前仓库"],
            },
            {
                "providerKey": "189cloud",
                "displayName": "Tianyi 189Cloud",
                "authEvidence": {"ok": False},
                "listEvidence": {"ok": False},
                "metadataEvidence": {"ok": False},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["缺少通过的 auth validation 证据"],
            },
            {
                "providerKey": "baidu_netdisk",
                "displayName": "Baidu Netdisk",
                "authEvidence": {"ok": False},
                "listEvidence": {"ok": False},
                "metadataEvidence": {"ok": False},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["缺少通过的 auth validation 证据"],
            },
            {
                "providerKey": "quark",
                "displayName": "Quark",
                "authEvidence": {"ok": False},
                "listEvidence": {"ok": False},
                "metadataEvidence": {"ok": False},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["缺少通过的 auth validation 证据"],
            },
            {
                "providerKey": "xunlei",
                "displayName": "Xunlei Drive",
                "authEvidence": {"ok": False},
                "listEvidence": {"ok": False},
                "metadataEvidence": {"ok": False},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["缺少通过的 auth validation 证据"],
            },
            {
                "providerKey": "115_open",
                "displayName": "115 Open",
                "authEvidence": {"ok": True},
                "listEvidence": {"ok": True},
                "metadataEvidence": {"ok": True},
                "createDirEvidence": {"ok": True},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0, "candidateCount": 1},
                "gaps": ["已有 fast-upload candidate 样本，但尚未记录到真实 runtime 成功样本"],
            },
            {
                "providerKey": "aliyundrive_open",
                "displayName": "Aliyun Drive Open",
                "authEvidence": {"ok": True},
                "listEvidence": {"ok": True},
                "metadataEvidence": {"ok": True},
                "createDirEvidence": {"ok": True},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0, "probeCount": 1},
                "gaps": ["已有 probe-only 样本，但尚未记录到真实传输成功样本"],
            },
            {
                "providerKey": "123_open",
                "displayName": "123Pan Open",
                "authEvidence": {"ok": False},
                "listEvidence": {"ok": False},
                "metadataEvidence": {"ok": False},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["缺少通过的 auth validation 证据"],
            },
            {
                "providerKey": "pikpak",
                "displayName": "PikPak",
                "authEvidence": {"ok": True},
                "listEvidence": {"ok": True},
                "metadataEvidence": {"ok": True},
                "createDirEvidence": {"ok": True},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["基础证据已齐，但尚未记录到真实 runtime 成功样本"],
            },
            {
                "providerKey": "uc",
                "displayName": "UC Drive",
                "authEvidence": {"ok": True},
                "listEvidence": {"ok": True},
                "metadataEvidence": {"ok": True},
                "createDirEvidence": {"ok": True},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0, "orphanProfileCount": 1, "orphanProfiles": ["uc-orphan"]},
                "gaps": ["已有 runtime 样本，但对应 auth profile 未保存在当前仓库"],
            },
        ]
    }
    synthetic_profiles = [
            {
                "profileId": "gy-rem-1",
                "providerKey": "guangya",
                "displayName": "smoke-guangya",
                "profileReady": False,
                "writeReady": True,
                "resolvedParentId": "gy-parent-1",
                "needsSecretRefresh": True,
                "placeholderSecretFieldHints": ["token"],
            },
        {
            "profileId": "115-rem-1",
            "providerKey": "115_open",
            "displayName": "115-ready",
            "profileReady": True,
            "writeReady": True,
            "resolvedParentId": "115-root-1",
        },
        {
            "profileId": "ali-rem-1",
            "providerKey": "aliyundrive_open",
            "displayName": "aliyun-ready",
            "profileReady": False,
            "writeReady": True,
            "resolvedParentId": "aliyun-root-0",
            "needsSecretRefresh": True,
            "placeholderSecretFieldHints": ["token"],
        },
        {
            "profileId": "pp-rem-1",
            "providerKey": "pikpak",
            "displayName": "pikpak-ready",
            "profileReady": True,
            "writeReady": True,
        },
    ]
    bundle = build_real_evidence_remediation_bundle(report=synthetic_report, profile_views=synthetic_profiles)
    markdown = real_evidence_remediation_to_markdown(bundle)
    quark_create = _create_command_for_provider(
        provider_key="quark",
        auth_modes=provider_auth_modes("quark"),
        field_hints=capture_field_hints("quark"),
    )
    pan115_create = _create_command_for_provider(
        provider_key="115_open",
        auth_modes=provider_auth_modes("115_open"),
        field_hints=capture_field_hints("115_open"),
    )
    baidu_create = _create_command_for_provider(
        provider_key="baidu_netdisk",
        auth_modes=provider_auth_modes("baidu_netdisk"),
        field_hints=capture_field_hints("baidu_netdisk"),
    )
    xunlei_create = _create_command_for_provider(
        provider_key="xunlei",
        auth_modes=provider_auth_modes("xunlei"),
        field_hints=capture_field_hints("xunlei"),
    )
    pikpak_create = _create_command_for_provider(
        provider_key="pikpak",
        auth_modes=provider_auth_modes("pikpak"),
        field_hints=capture_field_hints("pikpak"),
    )

    with TemporaryDirectory() as tmp_dir:
        configure_data_dir(Path(tmp_dir))
        original_password = webapp.ADMIN_PASSWORD
        original_webapp_builder = webapp.build_real_evidence_remediation_bundle
        original_webapp_renderer = webapp.real_evidence_remediation_to_markdown
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            webapp.build_real_evidence_remediation_bundle = lambda: bundle
            webapp.real_evidence_remediation_to_markdown = real_evidence_remediation_to_markdown
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            api_bundle = client.get("/api/real_evidence_remediation_bundle").json()
            api_markdown = client.get("/api/real_evidence_remediation_markdown").json()
        finally:
            webapp.ADMIN_PASSWORD = original_password
            webapp.build_real_evidence_remediation_bundle = original_webapp_builder
            webapp.real_evidence_remediation_to_markdown = original_webapp_renderer

    print(
        json.dumps(
            {
                "providerCount": ((bundle.get("summary") or {}).get("providerCount")),
                "providersWithCreateCommand": ((bundle.get("summary") or {}).get("providersWithCreateCommand")),
                "providersWithBootstrapCommand": ((bundle.get("summary") or {}).get("providersWithBootstrapCommand")),
                "providersWithPatchCommand": ((bundle.get("summary") or {}).get("providersWithPatchCommand")),
                "providersWithPatchProbeCommand": ((bundle.get("summary") or {}).get("providersWithPatchProbeCommand")),
                "providersWithRecreateProbeCommand": ((bundle.get("summary") or {}).get("providersWithRecreateProbeCommand")),
                "providersWithRefreshEvidenceCommand": ((bundle.get("summary") or {}).get("providersWithRefreshEvidenceCommand")),
                "providersWithPostRefreshRuntimeCommand": ((bundle.get("summary") or {}).get("providersWithPostRefreshRuntimeCommand")),
                "providersWithRuntimeProbeCommand": ((bundle.get("summary") or {}).get("providersWithRuntimeProbeCommand")),
                "providersWithLiveUploadCommand": ((bundle.get("summary") or {}).get("providersWithLiveUploadCommand")),
                "providersWithFastCandidateCommand": ((bundle.get("summary") or {}).get("providersWithFastCandidateCommand")),
                "providersWithRuntimeSuccessCommand": ((bundle.get("summary") or {}).get("providersWithRuntimeSuccessCommand")),
                "providersWithPostBootstrapRuntimeCommand": ((bundle.get("summary") or {}).get("providersWithPostBootstrapRuntimeCommand")),
                "providersWithPrimaryCommand": ((bundle.get("summary") or {}).get("providersWithPrimaryCommand")),
                "providersWithOverwriteVariantCommand": ((bundle.get("summary") or {}).get("providersWithOverwriteVariantCommand")),
                "providersWithConflictPolicyNote": ((bundle.get("summary") or {}).get("providersWithConflictPolicyNote")),
                "providersWithDeclaredConflictPolicies": ((bundle.get("summary") or {}).get("providersWithDeclaredConflictPolicies")),
                "providersWithProviderManagedOverwrite": ((bundle.get("summary") or {}).get("providersWithProviderManagedOverwrite")),
                "providersWithOverwriteDowngrade": ((bundle.get("summary") or {}).get("providersWithOverwriteDowngrade")),
                "providersWithConflictUnsupported": ((bundle.get("summary") or {}).get("providersWithConflictUnsupported")),
                "summaryHasExpectedLiveUploadCount": ((bundle.get("summary") or {}).get("providersWithLiveUploadCommand")) == 1,
                "summaryHasExpectedFastCandidateCount": ((bundle.get("summary") or {}).get("providersWithFastCandidateCommand")) == 2,
                "summaryHasExpectedRuntimeSuccessCount": ((bundle.get("summary") or {}).get("providersWithRuntimeSuccessCommand")) == 2,
                "summaryHasExpectedPostBootstrapCount": ((bundle.get("summary") or {}).get("providersWithPostBootstrapRuntimeCommand")) == 6,
                "summaryHasExpectedPrimaryCommandCount": ((bundle.get("summary") or {}).get("providersWithPrimaryCommand")) == 10,
                "summaryHasExpectedRecreateProbeCount": ((bundle.get("summary") or {}).get("providersWithRecreateProbeCommand")) == 3,
                "summaryHasExpectedOverwriteVariantCount": ((bundle.get("summary") or {}).get("providersWithOverwriteVariantCommand")) == 10,
                "summaryHasExpectedConflictPolicyNoteCount": ((bundle.get("summary") or {}).get("providersWithConflictPolicyNote")) == 10,
                "summaryHasExpectedPostRefreshRuntimeCount": ((bundle.get("summary") or {}).get("providersWithPostRefreshRuntimeCommand")) == 0,
                "summaryHasExpectedDeclaredConflictPoliciesCount": ((bundle.get("summary") or {}).get("providersWithDeclaredConflictPolicies")) == 8,
                "summaryHasExpectedDirectOverwriteCount": ((bundle.get("summary") or {}).get("providersWithProviderManagedOverwrite")) == 1,
                "summaryHasExpectedOverwriteDowngradeCount": ((bundle.get("summary") or {}).get("providersWithOverwriteDowngrade")) == 7,
                "summaryHasExpectedConflictUnsupportedCount": ((bundle.get("summary") or {}).get("providersWithConflictUnsupported")) == 1,
                "providersBlockedOnly": ((bundle.get("summary") or {}).get("providersBlockedOnly")),
                "providersCandidateOnly": ((bundle.get("summary") or {}).get("providersCandidateOnly")),
                "providersProbeOnly": ((bundle.get("summary") or {}).get("providersProbeOnly")),
                "providersWithNoProfilesList": ((bundle.get("summary") or {}).get("providersWithNoProfilesList")),
                "providersNeedingAuthEvidenceList": ((bundle.get("summary") or {}).get("providersNeedingAuthEvidenceList")),
                "providersNeedingRuntimeSuccessList": ((bundle.get("summary") or {}).get("providersNeedingRuntimeSuccessList")),
                "providersWithRecreateProbeCommandList": ((bundle.get("summary") or {}).get("providersWithRecreateProbeCommandList")),
                "providersWithPrimaryCommandList": ((bundle.get("summary") or {}).get("providersWithPrimaryCommandList")),
                "providersWithOverwriteVariantCommandList": ((bundle.get("summary") or {}).get("providersWithOverwriteVariantCommandList")),
                "providersBlockedOnlyList": ((bundle.get("summary") or {}).get("providersBlockedOnlyList")),
                "providersCandidateOnlyList": ((bundle.get("summary") or {}).get("providersCandidateOnlyList")),
                "providersProbeOnlyList": ((bundle.get("summary") or {}).get("providersProbeOnlyList")),
                "providersRuntimeOrphanOnlyList": ((bundle.get("summary") or {}).get("providersRuntimeOrphanOnlyList")),
                "markdownHasProviderSummary": "- providerSummary: `noProfiles=123_open, 189cloud, baidu_netdisk, quark, uc, xunlei` `needAuth=123_open, 189cloud, baidu_netdisk, quark, xunlei` `needRuntime=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, guangya, pikpak, quark, uc, xunlei` `recreateProbe=aliyundrive_open, guangya, uc` `primaryCommand=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, guangya, pikpak, quark, uc, xunlei` `overwriteVariant=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, guangya, pikpak, quark, uc, xunlei` `blockedOnly=(none)` `candidateOnly=115_open` `probeOnly=aliyundrive_open` `runtimeOrphanOnly=guangya, uc`" in markdown,
                "markdownHasCreateCommand": "create_auth_profile_stub.py" in markdown,
                "markdownHasBootstrapCommand": "recommendedBootstrapCommand" in markdown and "--probe" in markdown,
                "guangyaHasPatchCommand": "patch_auth_profile_extra.py" in markdown,
                "guangyaHasPatchProbeCommand": "patch_and_probe_auth_profile.py" in markdown,
                "markdownHasRefreshEvidenceCommand": "recommendedRefreshEvidenceCommand" not in markdown,
                "markdownHasPostRefreshRuntimeCommand": "recommendedPostRefreshRuntimeCommand" not in markdown,
                "markdownHasRuntimeProbeCommand": "recommendedRuntimeProbeCommand" in markdown and "create_runtime_probe_task.py" in markdown,
                "runtimeProbeCommandCarriesResolvedParent": "--target-parent-id 115-root-1" in markdown and "--evidence-dir tmp\\115_open-runtime-probe-evidence" in markdown,
                "runtimeProbeCommandShowsConflictChoice": "--target-provider 115_open" in markdown and "--conflict-policy auto_rename_new" in markdown,
                "markdownHasLiveUploadCommand": "recommendedLiveUploadCommand" in markdown and "create_live_upload_task.py" in markdown,
                "liveUploadCommandCarriesResolvedParent": "--target-provider pikpak" in markdown and "--evidence-dir tmp\\pikpak-live-evidence" in markdown,
                "liveUploadCommandShowsConflictChoice": "tmp\\pikpak-live-evidence" in markdown and "--conflict-policy auto_rename_new" in markdown,
                "markdownHasFastCandidateCommand": "recommendedFastCandidateCommand" in markdown and "create_fast_upload_candidate_task.py" in markdown,
                "fastCandidateCommandCarriesResolvedParent": "--target-parent-id 115-root-1" in markdown and "--evidence-dir tmp\\115_open-fast-candidate-evidence" in markdown,
                "fastCandidateCommandShowsConflictChoice": "tmp\\115_open-fast-candidate-evidence" in markdown and "--conflict-policy auto_rename_new" in markdown,
                "markdownHasRuntimeSuccessCommand": "recommendedRuntimeSuccessCommand" in markdown,
                "markdownHasPostBootstrapRuntimeCommand": "recommendedPostBootstrapRuntimeCommand" in markdown and "tmp\\189cloud-post-bootstrap-runtime-evidence" in markdown,
                "markdownHasPrimaryCommand": "recommendedPrimaryCommand" in markdown and "label=recreate_probe" in markdown and "label=post_bootstrap_runtime" in markdown,
                "markdownHasRecreateProbeCommand": "recommendedRecreateProbeCommand" in markdown and "placeholderSecretFieldHints: `token`" in markdown,
                "markdownHasExpandedPostBootstrapHelpers": "tmp\\quark-post-bootstrap-runtime-evidence" in markdown and "tmp\\xunlei-post-bootstrap-runtime-evidence" in markdown and "tmp\\123_open-post-bootstrap-runtime-evidence" in markdown and "tmp\\uc-post-bootstrap-runtime-evidence" in markdown,
                "postBootstrapCommandShowsConflictChoice": "tmp\\189cloud-post-bootstrap-runtime-evidence" in markdown and "--conflict-policy auto_rename_new" in markdown,
                "markdownHasOverwriteVariantCommand": "recommendedOverwriteVariantCommand" in markdown and "--conflict-policy overwrite_existing" in markdown,
                "markdownHasConflictPolicyNote": "conflictPolicyNote:" in markdown and "overwrite_existing" in markdown,
                "markdownHasConflictSupportSummary": "providersWithProviderManagedOverwrite" in markdown and "providersWithOverwriteDowngrade" in markdown and "providersWithConflictUnsupported" in markdown,
                "markdownHasConflictSupportRows": "conflictSupport:" in markdown and "providerConflictNotes:" in markdown,
                "postBootstrapNextStepMentionsRuntimeFollowup": "189cloud" in markdown and "post-bootstrap runtime helper" in markdown and "runtime success" in markdown,
                "runtimeSuccessFallsBackToFastHelper": "115_open" in markdown and "tmp\\115_open-fast-candidate-evidence" in markdown,
                "runtimeSuccessUsesLiveHelperWhenAvailable": "pikpak" in markdown and "tmp\\pikpak-live-evidence" in markdown,
                "markdownHasCandidateOnlyFlag": "runtimeCandidateOnly=True" in markdown,
                "markdownHasProbeOnlyFlag": "runtimeProbeOnly=True" in markdown,
                "probeOnlyKeepsRuntimeCommand": "123_open" in markdown and "create_runtime_probe_task.py" in markdown,
                "quarkPrefersManualCookie": "--provider-key quark --auth-mode manual_cookie" in quark_create and "--cookie YOUR_COOKIE" in quark_create,
                "quarkSkipsCookieHeaderExtra": "--set cookie_header=YOUR_VALUE" not in quark_create,
                "115PrefersManualCookie": "--provider-key 115_open --auth-mode manual_cookie" in pan115_create and "--cookie YOUR_COOKIE" in pan115_create,
                "quarkPostBootstrapUsesLiveHelper": "create_live_upload_task.py" in _post_bootstrap_runtime_command_for_provider("quark")
                and "tmp\\quark-post-bootstrap-runtime-evidence" in _post_bootstrap_runtime_command_for_provider("quark"),
                "xunleiPostBootstrapUsesLiveHelper": "create_live_upload_task.py" in _post_bootstrap_runtime_command_for_provider("xunlei")
                and "--threshold-mb 1" in _post_bootstrap_runtime_command_for_provider("xunlei"),
                "cloud115PostBootstrapKeepsFastHelper": "create_fast_upload_candidate_task.py" in _post_bootstrap_runtime_command_for_provider("115_open")
                and "--sha1 auto" in _post_bootstrap_runtime_command_for_provider("115_open"),
                "baiduManualCookieSkipsAuthorizationExtra": "--provider-key baidu_netdisk --auth-mode manual_cookie" in baidu_create and "--set authorization=YOUR_VALUE" not in baidu_create,
                "xunleiPrefersManualToken": "--provider-key xunlei --auth-mode manual_token" in xunlei_create and "--token YOUR_TOKEN" in xunlei_create and "--set deviceId=YOUR_VALUE" in xunlei_create,
                "pikpakPrefersManualToken": "--provider-key pikpak --auth-mode manual_token" in pikpak_create and "--token YOUR_TOKEN" in pikpak_create and "--set authorization=YOUR_VALUE" not in pikpak_create,
                "cloud189HasHelper": "patch_189cloud_account_auth.py" in markdown,
                "markdownHasAuthModes": "recommendedAuthModes" in markdown,
                "markdownHasLoginUrl": "webLoginUrl" in markdown,
                "markdownHasFieldHints": "requiredFieldHints" in markdown,
                "markdownHasNextStep": "nextStep:" in markdown,
                "apiHasSummary": bool((api_bundle.get("summary") or {}).get("providerCount", 0) >= 0),
                "apiHasRuntimeSuccessSummary": ((api_bundle.get("summary") or {}).get("providersWithRuntimeSuccessCommand")) == ((bundle.get("summary") or {}).get("providersWithRuntimeSuccessCommand")),
                "apiHasPostBootstrapRuntimeSummary": ((api_bundle.get("summary") or {}).get("providersWithPostBootstrapRuntimeCommand")) == ((bundle.get("summary") or {}).get("providersWithPostBootstrapRuntimeCommand")) == 6,
                "apiHasExpectedLiveUploadSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithLiveUploadCommand")) == ((bundle.get("summary") or {}).get("providersWithLiveUploadCommand")) == 1,
                "apiHasExpectedFastCandidateSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithFastCandidateCommand")) == ((bundle.get("summary") or {}).get("providersWithFastCandidateCommand")) == 2,
                "apiHasExpectedRuntimeSuccessSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithRuntimeSuccessCommand")) == ((bundle.get("summary") or {}).get("providersWithRuntimeSuccessCommand")) == 2,
                "apiHasExpectedPrimaryCommandSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithPrimaryCommand")) == ((bundle.get("summary") or {}).get("providersWithPrimaryCommand")) == 10,
                "apiHasExpectedRecreateProbeSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithRecreateProbeCommand")) == ((bundle.get("summary") or {}).get("providersWithRecreateProbeCommand")) == 3,
                "apiHasExpectedOverwriteVariantSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithOverwriteVariantCommand")) == ((bundle.get("summary") or {}).get("providersWithOverwriteVariantCommand")) == 10,
                "apiHasExpectedConflictPolicyNoteSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithConflictPolicyNote")) == ((bundle.get("summary") or {}).get("providersWithConflictPolicyNote")) == 10,
                "apiHasExpectedPostRefreshRuntimeSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithPostRefreshRuntimeCommand")) == ((bundle.get("summary") or {}).get("providersWithPostRefreshRuntimeCommand")) == 0,
                "apiHasExpectedDeclaredConflictPoliciesSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithDeclaredConflictPolicies")) == ((bundle.get("summary") or {}).get("providersWithDeclaredConflictPolicies")) == 8,
                "apiHasExpectedDirectOverwriteSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithProviderManagedOverwrite")) == ((bundle.get("summary") or {}).get("providersWithProviderManagedOverwrite")) == 1,
                "apiHasExpectedOverwriteDowngradeSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithOverwriteDowngrade")) == ((bundle.get("summary") or {}).get("providersWithOverwriteDowngrade")) == 7,
                "apiHasExpectedConflictUnsupportedSummaryCount": ((api_bundle.get("summary") or {}).get("providersWithConflictUnsupported")) == ((bundle.get("summary") or {}).get("providersWithConflictUnsupported")) == 1,
                "apiHasExpectedProviderSummaryLists": ((api_bundle.get("summary") or {}).get("providersWithNoProfilesList")) == ["123_open", "189cloud", "baidu_netdisk", "quark", "uc", "xunlei"]
                and ((api_bundle.get("summary") or {}).get("providersNeedingAuthEvidenceList")) == ["123_open", "189cloud", "baidu_netdisk", "quark", "xunlei"]
                and ((api_bundle.get("summary") or {}).get("providersNeedingRuntimeSuccessList")) == ["115_open", "123_open", "189cloud", "aliyundrive_open", "baidu_netdisk", "guangya", "pikpak", "quark", "uc", "xunlei"]
                and ((api_bundle.get("summary") or {}).get("providersWithRecreateProbeCommandList")) == ["aliyundrive_open", "guangya", "uc"]
                and ((api_bundle.get("summary") or {}).get("providersWithPrimaryCommandList")) == ["115_open", "123_open", "189cloud", "aliyundrive_open", "baidu_netdisk", "guangya", "pikpak", "quark", "uc", "xunlei"]
                and ((api_bundle.get("summary") or {}).get("providersWithOverwriteVariantCommandList")) == ["115_open", "123_open", "189cloud", "aliyundrive_open", "baidu_netdisk", "guangya", "pikpak", "quark", "uc", "xunlei"]
                and ((api_bundle.get("summary") or {}).get("providersBlockedOnlyList")) == []
                and ((api_bundle.get("summary") or {}).get("providersCandidateOnlyList")) == ["115_open"]
                and ((api_bundle.get("summary") or {}).get("providersProbeOnlyList")) == ["aliyundrive_open"]
                and ((api_bundle.get("summary") or {}).get("providersRuntimeOrphanOnlyList")) == ["guangya", "uc"],
                "apiHasOverwriteVariantCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "115_open"
                            and "--conflict-policy overwrite_existing" in str((row or {}).get("recommendedOverwriteVariantCommand") or "")
                        ),
                        None,
                    )
                ),
                "apiHasConflictPolicyNote": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "guangya"
                            and "overwrite_existing" in str((row or {}).get("conflictPolicyNote") or "")
                        ),
                        None,
                    )
                ),
                "apiHasAliyunDirectOverwriteStatus": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "aliyundrive_open"
                            and str((row or {}).get("overwriteSupportStatus") or "") == "supported"
                            and "overwrite_existing" in ",".join((row or {}).get("declaredConflictPolicies") or [])
                        ),
                        None,
                    )
                ),
                "apiHas115ConflictProbeOnlyStatus": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "115_open"
                            and str((row or {}).get("overwriteSupportStatus") or "") == "unsupported"
                            and str((row or {}).get("autoRenameSupportStatus") or "") == "probe_only_runtime_write_check"
                        ),
                        None,
                    )
                ),
                "apiHasGuangyaRuntimeSuccessCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "pikpak"
                            and "create_live_upload_task.py" in str((row or {}).get("recommendedRuntimeSuccessCommand") or "")
                            and "--conflict-policy auto_rename_new" in str((row or {}).get("recommendedRuntimeSuccessCommand") or "")
                        ),
                        None,
                    )
                ),
                "apiHasGuangyaPrimaryCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "guangya"
                            and str((row or {}).get("recommendedPrimaryCommandLabel") or "") == "recreate_probe"
                            and "create_auth_profile_stub.py" in str((row or {}).get("recommendedPrimaryCommand") or "")
                            and bool((row or {}).get("needsSecretRefresh"))
                            and "token" in ",".join((row or {}).get("placeholderSecretFieldHints") or [])
                        ),
                        None,
                    )
                ),
                "apiHasAliyunRecreateProbeCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "aliyundrive_open"
                            and str((row or {}).get("recommendedPrimaryCommandLabel") or "") == "recreate_probe"
                            and "create_auth_profile_stub.py" in str((row or {}).get("recommendedRecreateProbeCommand") or "")
                            and bool((row or {}).get("needsSecretRefresh"))
                            and "token" in ",".join((row or {}).get("placeholderSecretFieldHints") or [])
                        ),
                        None,
                    )
                ),
                "apiHasGuangyaOrphanRecreateProbeCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "guangya"
                            and str((row or {}).get("recommendedPrimaryCommandLabel") or "") == "recreate_probe"
                            and "--profile-id gy-orphan" in str((row or {}).get("recommendedRecreateProbeCommand") or "")
                            and "guangya-restore-gy-orphan" in str((row or {}).get("recommendedPrimaryCommand") or "")
                        ),
                        None,
                    )
                ),
                "apiHasUcOrphanRecreateProbeCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "uc"
                            and str((row or {}).get("recommendedPrimaryCommandLabel") or "") == "recreate_probe"
                            and "--profile-id uc-orphan" in str((row or {}).get("recommendedRecreateProbeCommand") or "")
                            and "uc-restore-uc-orphan" in str((row or {}).get("recommendedPrimaryCommand") or "")
                            and "runtimeOrphanOnly" in str(api_markdown.get("markdown", ""))
                        ),
                        None,
                    )
                ),
                "apiHas189PrimaryBootstrapCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "189cloud"
                            and str((row or {}).get("recommendedPrimaryCommandLabel") or "") == "post_bootstrap_runtime"
                            and "create_fast_upload_candidate_task.py" in str((row or {}).get("recommendedPrimaryCommand") or "")
                        ),
                        None,
                    )
                ),
                "apiHas115RuntimeSuccessCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "115_open"
                            and "create_fast_upload_candidate_task.py" in str((row or {}).get("recommendedRuntimeSuccessCommand") or "")
                            and "--conflict-policy auto_rename_new" in str((row or {}).get("recommendedRuntimeSuccessCommand") or "")
                        ),
                        None,
                    )
                ),
                "apiHas189PostBootstrapRuntimeCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "189cloud"
                            and "create_fast_upload_candidate_task.py" in str((row or {}).get("recommendedPostBootstrapRuntimeCommand") or "")
                            and "--conflict-policy auto_rename_new" in str((row or {}).get("recommendedPostBootstrapRuntimeCommand") or "")
                            and "post-bootstrap runtime helper" in str((row or {}).get("nextStep") or "")
                        ),
                        None,
                    )
                ),
                "apiHasQuarkPostBootstrapRuntimeCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "quark"
                            and "create_live_upload_task.py" in str((row or {}).get("recommendedPostBootstrapRuntimeCommand") or "")
                            and "--conflict-policy auto_rename_new" in str((row or {}).get("recommendedPostBootstrapRuntimeCommand") or "")
                        ),
                        None,
                    )
                ),
                "apiHasBaiduPostBootstrapRuntimeCommand": bool(
                    next(
                        (
                            row
                            for row in (api_bundle.get("items") or [])
                            if str((row or {}).get("providerKey") or "") == "baidu_netdisk"
                            and "create_live_upload_task.py" in str((row or {}).get("recommendedPostBootstrapRuntimeCommand") or "")
                            and "--conflict-policy auto_rename_new" in str((row or {}).get("recommendedPostBootstrapRuntimeCommand") or "")
                        ),
                        None,
                    )
                ),
                "apiMarkdownHasTitle": "# CloudPan Sync 真实联调补救指南" in str(api_markdown.get("markdown", "")),
                "apiMarkdownHasRuntimeSuccessCommand": "recommendedRuntimeSuccessCommand" in str(api_markdown.get("markdown", "")),
                "apiMarkdownHasPostBootstrapRuntimeCommand": "recommendedPostBootstrapRuntimeCommand" in str(api_markdown.get("markdown", "")),
                "apiMarkdownHasPrimaryCommand": "recommendedPrimaryCommand" in str(api_markdown.get("markdown", "")) and "label=recreate_probe" in str(api_markdown.get("markdown", "")) and "label=post_bootstrap_runtime" in str(api_markdown.get("markdown", "")),
                "apiMarkdownHasRecreateProbeCommand": "recommendedRecreateProbeCommand" in str(api_markdown.get("markdown", "")) and "placeholderSecretFieldHints: `token`" in str(api_markdown.get("markdown", "")),
                "apiMarkdownHasOverwriteVariantCommand": "recommendedOverwriteVariantCommand" in str(api_markdown.get("markdown", "")) and "--conflict-policy overwrite_existing" in str(api_markdown.get("markdown", "")),
                "apiMarkdownHasConflictPolicyNote": "conflictPolicyNote:" in str(api_markdown.get("markdown", "")) and "overwrite_existing" in str(api_markdown.get("markdown", "")),
                "apiMarkdownHasConflictSupportRows": "conflictSupport:" in str(api_markdown.get("markdown", "")) and "providerConflictNotes:" in str(api_markdown.get("markdown", "")),
                "apiMarkdownHasProviderSummary": "providerSummary: `noProfiles=123_open, 189cloud, baidu_netdisk, quark, uc, xunlei` `needAuth=123_open, 189cloud, baidu_netdisk, quark, xunlei` `needRuntime=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, guangya, pikpak, quark, uc, xunlei` `recreateProbe=aliyundrive_open, guangya, uc` `primaryCommand=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, guangya, pikpak, quark, uc, xunlei` `overwriteVariant=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, guangya, pikpak, quark, uc, xunlei` `blockedOnly=(none)` `candidateOnly=115_open` `probeOnly=aliyundrive_open` `runtimeOrphanOnly=guangya, uc`" in str(api_markdown.get("markdown", "")),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
