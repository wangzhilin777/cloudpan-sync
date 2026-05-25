from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> None:
    html = (ROOT / "src" / "cloudpan_sync" / "web" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    print(
        json.dumps(
            {
                "htmlHasRemediationPanel": "settingsRealEvidenceRemediationTitle" in html and "settingsRealEvidenceRemediationList" in html,
                "jsHasRemediationState": "realEvidenceRemediation: null" in app_js,
                "jsHasRemediationLoader": 'async function loadRealEvidenceRemediationSummary()' in app_js and 'fetchJson("/api/real_evidence_remediation_bundle")' in app_js,
                "jsHasRemediationCreateAction": 'async function createRemediationProfile(providerKey)' in app_js and 'fetchJson("/api/real_evidence_remediation/create_profile"' in app_js and 'createBtn.textContent = "Create Stub"' in app_js,
                "jsHasRemediationProfileActions": 'async function refreshRealEvidenceRemediationProfile(profileId)' in app_js and 'async function probeRealEvidenceRemediationProfile(profileId)' in app_js and 'focusBtn.textContent = "Focus Profile"' in app_js and 'refreshBtn.textContent = "Refresh Evidence"' in app_js and 'probeBtn.textContent = "Run Live Probe"' in app_js and 'captureBtn.textContent = "Open Capture"' in app_js,
                "jsRefreshProtectedDataLoadsRemediation": "loadRealEvidenceRemediationSummary()," in app_js,
                "jsLogoutClearsRemediation": "state.realEvidenceRemediation = null;" in app_js and "state.lastRemediationAction = null;" in app_js,
                "jsRemediationSummaryShowsLiveUploadCount": "liveUploadCommands=${remediationSummary.providersWithLiveUploadCommand || 0}" in app_js,
                "jsRemediationSummaryShowsFastCandidateCount": "fastCandidateCommands=${remediationSummary.providersWithFastCandidateCommand || 0}" in app_js,
                "jsRemediationSummaryShowsRuntimeSuccessCount": "runtimeSuccessCommands=${remediationSummary.providersWithRuntimeSuccessCommand || 0}" in app_js,
                "jsRemediationSummaryShowsPostBootstrapCount": "postBootstrapRuntimeCommands=${remediationSummary.providersWithPostBootstrapRuntimeCommand || 0}" in app_js,
                "jsRemediationSummaryShowsPrimaryCommandCount": "primaryCommands=${remediationSummary.providersWithPrimaryCommand || 0}" in app_js,
                "jsRemediationSummaryShowsRecreateProbeCount": "recreateProbeCommands=${remediationSummary.providersWithRecreateProbeCommand || 0}" in app_js,
                "jsRemediationSummaryShowsOverwriteVariantCount": "overwriteVariantCommands=${remediationSummary.providersWithOverwriteVariantCommand || 0}" in app_js,
                "jsRemediationSummaryShowsConflictPolicyNoteCount": "conflictPolicyNotes=${remediationSummary.providersWithConflictPolicyNote || 0}" in app_js,
                "jsRemediationSummaryShowsPostRefreshRuntimeCount": "postRefreshRuntimeCommands=${remediationSummary.providersWithPostRefreshRuntimeCommand || 0}" in app_js,
                "jsRemediationSummaryShowsDirectOverwriteCount": "directOverwrite=${remediationSummary.providersWithProviderManagedOverwrite || 0}" in app_js,
                "jsRemediationSummaryShowsOverwriteDowngradeCount": "overwriteDowngrade=${remediationSummary.providersWithOverwriteDowngrade || 0}" in app_js,
                "jsRemediationSummaryShowsConflictUnsupportedCount": "conflictUnsupported=${remediationSummary.providersWithConflictUnsupported || 0}" in app_js,
                "jsRemediationRowsShowLiveUploadCommand": "liveUpload=${item.recommendedLiveUploadCommand}" in app_js,
                "jsRemediationRowsShowFastCandidateCommand": "fastCandidate=${item.recommendedFastCandidateCommand}" in app_js,
                "jsRemediationRowsShowRuntimeSuccessCommand": "runtimeSuccess=${item.recommendedRuntimeSuccessCommand}" in app_js,
                "jsRemediationRowsShowPostRefreshRuntimeCommand": "postRefreshRuntime=${item.recommendedPostRefreshRuntimeCommand}" in app_js,
                "jsRemediationRowsShowPostBootstrapCommand": "postBootstrapRuntime=${item.recommendedPostBootstrapRuntimeCommand}" in app_js,
                "jsRemediationRowsShowPrimaryCommand": "primary=${item.recommendedPrimaryCommand}" in app_js and "primaryLabel=${item.recommendedPrimaryCommandLabel}" in app_js,
                "jsRemediationRowsShowRecreateProbeCommand": "recreateProbe=${item.recommendedRecreateProbeCommand}" in app_js,
                "jsRemediationRowsShowSecretRefreshState": "needsSecretRefresh=${Boolean(item.needsSecretRefresh)}" in app_js and "placeholderSecretHints=${placeholderSecretHints}" in app_js,
                "jsRemediationRowsPreserveRuntimeCommandText": "runtimeSuccess=${item.recommendedRuntimeSuccessCommand}" in app_js
                and "postRefreshRuntime=${item.recommendedPostRefreshRuntimeCommand}" in app_js
                and "postBootstrapRuntime=${item.recommendedPostBootstrapRuntimeCommand}" in app_js,
                "jsRemediationRowsShowOverwriteVariant": "overwriteVariant=${item.recommendedOverwriteVariantCommand}" in app_js,
                "jsRemediationRowsShowConflictPolicyNote": "conflictPolicyNote=${item.conflictPolicyNote}" in app_js,
                "jsRemediationRowsShowConflictSupportStatus": "overwriteSupport=${item.overwriteSupportStatus || \"unknown\"}" in app_js and "autoRenameSupport=${item.autoRenameSupportStatus || \"unknown\"}" in app_js and "overwriteBehavior=${item.overwriteBehavior || \"unknown\"}" in app_js and "conflictDeclared=${(item.declaredConflictPolicies || []).join(\"/\") || \"(none)\"}" in app_js,
                "jsRemediationRowsShowProviderConflictNotes": "providerConflictNotes=${item.providerConflictNotes}" in app_js,
                "jsRemediationRowsBindCreateStub": 'createBtn.addEventListener("click", () => createRemediationProfile(item.providerKey));' in app_js,
                "jsRemediationRowsBindProfileActions": 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(profileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(profileId));' in app_js
                and 'if (liveProbeProviderSet.has(item.providerKey)) {' in app_js
                and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js
                and 'const profileId = (item.profileIds || [])[0] || "";' in app_js,
                "jsSettingsRenderUsesRemediation": "settingsRealEvidenceRemediationList" in app_js and "providersWithNoProfiles" in app_js and "providersNeedingRuntimeSuccess" in app_js and "recommendedAuthModes" in app_js and "webLoginUrl" in app_js and "requiredFieldHints" in app_js and "recommendedCreateCommand" in app_js and "providersWithCreateCommand" in app_js and "recommendedBootstrapCommand" in app_js and "providersWithBootstrapCommand" in app_js and "recommendedPatchProbeCommand" in app_js and "providersWithPatchProbeCommand" in app_js and "recommendedRecreateProbeCommand" in app_js and "providersWithRecreateProbeCommand" in app_js and "recommendedRefreshEvidenceCommand" in app_js and "providersWithRefreshEvidenceCommand" in app_js and "recommendedPostRefreshRuntimeCommand" in app_js and "providersWithPostRefreshRuntimeCommand" in app_js and "recommendedRuntimeProbeCommand" in app_js and "providersWithRuntimeProbeCommand" in app_js and "recommendedLiveUploadCommand" in app_js and "providersWithLiveUploadCommand" in app_js and "recommendedFastCandidateCommand" in app_js and "providersWithFastCandidateCommand" in app_js and "recommendedRuntimeSuccessCommand" in app_js and "providersWithRuntimeSuccessCommand" in app_js and "recommendedPostBootstrapRuntimeCommand" in app_js and "providersWithPostBootstrapRuntimeCommand" in app_js and "recommendedPrimaryCommand" in app_js and "recommendedPrimaryCommandLabel" in app_js and "providersWithPrimaryCommand" in app_js and "recommendedOverwriteVariantCommand" in app_js and "conflictPolicyNote" in app_js and "providersWithProviderManagedOverwrite" in app_js and "providersWithOverwriteDowngrade" in app_js and "providersWithConflictUnsupported" in app_js and "declaredConflictPolicies" in app_js and "overwriteSupportStatus" in app_js and "autoRenameSupportStatus" in app_js and "providerConflictNotes" in app_js and "providersCandidateOnly" in app_js and "providersProbeOnly" in app_js and "providersRuntimeOrphanOnly" in app_js and "needsSecretRefresh" in app_js and "placeholderSecretFieldHints" in app_js and "runtimeOrphanProfiles" in app_js and "candidateOnly=${Boolean(item.runtimeCandidateOnly)}" in app_js and "probeOnly=${Boolean(item.runtimeProbeOnly)}" in app_js and "runtimeOrphanOnly=${Boolean(item.runtimeOrphanOnly)}" in app_js and "primary=${item.recommendedPrimaryCommand}" in app_js and "primaryLabel=${item.recommendedPrimaryCommandLabel}" in app_js and "recreateProbe=${item.recommendedRecreateProbeCommand}" in app_js and "postRefreshRuntime=${item.recommendedPostRefreshRuntimeCommand}" in app_js and "runtimeSuccess=${item.recommendedRuntimeSuccessCommand}" in app_js and "postBootstrapRuntime=${item.recommendedPostBootstrapRuntimeCommand}" in app_js and "overwriteVariant=${item.recommendedOverwriteVariantCommand}" in app_js and "conflictPolicyNote=${item.conflictPolicyNote}" in app_js and "noProfilesProviders=" in app_js and "needAuthProviders=" in app_js and "needRuntimeProviders=" in app_js and "recreateProbeProviders=" in app_js and "primaryCommandProviders=" in app_js and "overwriteVariantProviders=" in app_js and "blockedOnlyProviders=" in app_js and "candidateOnlyProviders=" in app_js and "probeOnlyProviders=" in app_js and "runtimeOrphanOnlyProviders=" in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
