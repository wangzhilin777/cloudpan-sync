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
    html_has_auth_evidence_settings_panel = "settingsAuthEvidenceTitle" in html and "settingsAuthEvidenceList" in html
    html_has_auth_remediation_settings_panel = "settingsAuthRemediationTitle" in html and "settingsAuthRemediationList" in html
    js_has_auth_evidence_state = "authEvidenceBundle: null" in app_js
    js_has_auth_remediation_state = "authRemediationBundle: null" in app_js
    js_has_auth_evidence_loader = 'async function loadAuthEvidenceBundleSummary()' in app_js and 'fetchJson("/api/auth/evidence_bundle")' in app_js
    js_has_auth_remediation_loader = 'async function loadAuthRemediationBundleSummary()' in app_js and 'fetchJson("/api/auth/remediation_bundle")' in app_js
    js_has_auth_remediation_actions = 'function focusAuthRemediationProfile(profileId)' in app_js \
        and 'async function openCaptureGuideForProvider(providerKey)' in app_js \
        and 'focus: "Focus Existing Profile"' in app_js \
        and 'capture: "Open Capture For Existing Profile"' in app_js \
        and 'focusBtn.textContent = remediationLabels.focus;' in app_js \
        and 'captureBtn.textContent = remediationLabels.capture;' in app_js
    js_refresh_protected_data_loads_auth_bundles = "loadAuthEvidenceBundleSummary()," in app_js and "loadAuthRemediationBundleSummary()," in app_js
    js_auth_evidence_has_first_gap_actions = 'const firstAuthEvidenceGap = (state.authEvidenceBundle?.items || []).find((item) => {' in app_js \
        and 'focusBtn.textContent = "Focus First Gap"' in app_js \
        and 'refreshBtn.textContent = "Refresh First Gap"' in app_js \
        and 'captureBtn.textContent = "Open Capture First Gap"' in app_js \
        and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(firstProfile.profileId));' in app_js \
        and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(firstProfile.profileId));' in app_js \
        and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstProfile.providerKey || ""));' in app_js \
        and "const missing = (firstProfile.missingFieldHints || []).join(\" | \");" in app_js \
        and "const placeholderSecretHints = (firstProfile.placeholderSecretFieldHints || []).join(\" | \");" in app_js \
        and "const liveRejectedStatuses = (firstProfile.liveRejectedStatuses || []).join(\"/\") || \"\";" in app_js \
        and "const placeholderLiveRejectedProfiles = (firstProfile.placeholderLiveRejectedProfiles || []).join(\"/\") || \"\";" in app_js \
        and "const liveRejectedSummaries = (firstProfile.liveRejectedSummaries || []).join(\" | \") || \"\";" in app_js \
        and "missing=${missing}" in app_js \
        and "placeholderSecretHints=${placeholderSecretHints}" in app_js \
        and "liveRejectedStatuses=${liveRejectedStatuses}" in app_js \
        and "placeholderLiveRejectedProfiles=${placeholderLiveRejectedProfiles}" in app_js \
        and "liveRejectedSummaries=${liveRejectedSummaries}" in app_js
    js_render_settings_uses_auth_evidence = "const authEvidenceSummary = state.authEvidenceBundle?.summary || {};" in app_js \
        and "profileReadyProfiles=" in app_js \
        and "writeReadyProfiles=" in app_js \
        and "validationOkProfiles=" in app_js \
        and "probeOkProfiles=" in app_js \
        and "const firstSummary = firstNeedsWork.summary || {};" in app_js \
        and "const firstMissing = (firstProfile.missingFieldHints || []).join(\" | \");" in app_js \
        and "const firstPlaceholderSecretHints = (firstProfile.placeholderSecretFieldHints || []).join(\" | \");" in app_js \
        and "const firstLiveRejectedStatuses = (firstProfile.liveRejectedStatuses || []).join(\"/\") || \"\";" in app_js \
        and "const firstPlaceholderLiveRejectedProfiles = (firstProfile.placeholderLiveRejectedProfiles || []).join(\"/\") || \"\";" in app_js \
        and "const firstLiveRejectedSummaries = (firstProfile.liveRejectedSummaries || []).join(\" | \") || \"\";" in app_js \
        and 'firstGapMeta.textContent = `${firstProfile.displayName || firstProfile.profileId || "(unknown)"} [${firstProfile.providerKey || "(unknown)"}]: profileReady=${Boolean(firstSummary.profileReady)}, writeReady=${Boolean(firstSummary.writeReady)}, validationOk=${Boolean(firstSummary.validationOk)}, probeOk=${Boolean(firstSummary.probeOk)}${firstMissing ? `, missing=${firstMissing}` : ""}${firstPlaceholderSecretHints ? `, placeholderSecretHints=${firstPlaceholderSecretHints}` : ""}${firstLiveRejectedStatuses ? `, liveRejectedStatuses=${firstLiveRejectedStatuses}` : ""}${firstPlaceholderLiveRejectedProfiles ? `, placeholderLiveRejectedProfiles=${firstPlaceholderLiveRejectedProfiles}` : ""}${firstLiveRejectedSummaries ? `, liveRejectedSummaries=${firstLiveRejectedSummaries}` : ""}`;' in app_js \
        and 'heading.textContent = `Auth Evidence: ${profile.displayName || profile.profileId || "(unknown)"}`;' in app_js \
        and 'rejectedMeta.textContent = `liveRejectedStatuses=${liveRejectedStatuses || "(none)"}, placeholderLiveRejectedProfiles=${placeholderLiveRejectedProfiles || "(none)"}, liveRejectedSummaries=${liveRejectedSummaries || "(none)"}`;' in app_js
    js_render_settings_uses_auth_remediation = "const authRemediationSummary = state.authRemediationBundle?.summary || {};" in app_js \
        and 'const firstAuthRemediationGap = (state.authRemediationBundle?.items || []).find((item) => item?.needsFix || item?.writeNeedsFix || item?.needsSecretRefresh) || null;' in app_js \
        and 'focusBtn.textContent = "Focus First Fix"' in app_js \
        and 'captureBtn.textContent = "Open Capture First Fix"' in app_js \
        and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(firstAuthRemediationGap.profileId));' in app_js \
        and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstAuthRemediationGap.providerKey || ""));' in app_js \
        and 'heading.textContent = "Auth Remediation Guide";' in app_js \
        and "const firstLiveRejectedStatuses = (firstAuthRemediationGap.liveRejectedStatuses || []).join(\"/\") || \"\";" in app_js \
        and "const firstPlaceholderLiveRejectedProfiles = (firstAuthRemediationGap.placeholderLiveRejectedProfiles || []).join(\"/\") || \"\";" in app_js \
        and "const firstLiveRejectedSummaries = (firstAuthRemediationGap.liveRejectedSummaries || []).join(\" | \") || \"\";" in app_js \
        and "const firstMissing = (firstNeedsFix.missingFieldHints || []).join(\" | \");" in app_js \
        and "const firstWriteMissing = (firstNeedsFix.writeMissingFieldHints || []).join(\" | \");" in app_js \
        and "const firstPlaceholderSecretHints = (firstNeedsFix.placeholderSecretFieldHints || []).join(\" | \");" in app_js \
        and "readyProfiles=" in app_js \
        and "needsFixProfiles=" in app_js \
        and "writeNeedsFixProfiles=" in app_js \
        and "needsSecretRefreshProfiles=" in app_js \
        and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(item.profileId));' in app_js \
        and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js \
        and "placeholderSecretHints=" in app_js \
        and "liveRejectedStatuses=" in app_js \
        and "placeholderLiveRejectedProfiles=" in app_js \
        and "liveRejectedSummaries=" in app_js \
        and 'firstFixMeta.textContent = `${firstNeedsFix.displayName || firstNeedsFix.profileId || "(unknown)"} [${firstNeedsFix.providerKey || "(unknown)"}]: profileReady=${Boolean(firstNeedsFix.profileReady)}, writeReady=${Boolean(firstNeedsFix.writeReady)}${firstMissing ? `, missing=${firstMissing}` : ""}${firstWriteMissing ? `, writeMissing=${firstWriteMissing}` : ""}${firstPlaceholderSecretHints ? `, placeholderSecretHints=${firstPlaceholderSecretHints}` : ""}${Boolean(firstNeedsFix.needsSecretRefresh) ? ", needsSecretRefresh=true" : ""}`;' in app_js \
        and "liveRejectedStatuses=${firstLiveRejectedStatuses}" in app_js \
        and "placeholderLiveRejectedProfiles=${firstPlaceholderLiveRejectedProfiles}" in app_js \
        and "liveRejectedSummaries=${firstLiveRejectedSummaries}" in app_js \
        and 'rejectedMeta.textContent = `liveRejectedStatuses=${(firstNeedsFix.liveRejectedStatuses || []).join("/") || "(none)"}, placeholderLiveRejectedProfiles=${(firstNeedsFix.placeholderLiveRejectedProfiles || []).join("/") || "(none)"}, liveRejectedSummaries=${(firstNeedsFix.liveRejectedSummaries || []).join(" | ") || "(none)"}`;' in app_js \
        and "recreateProbe=" in app_js
    js_logout_clears_auth_bundles = "state.authEvidenceBundle = null;" in app_js and "state.authRemediationBundle = null;" in app_js
    auth_settings_ui_flow_is_wired = (
        html_has_auth_evidence_settings_panel
        and html_has_auth_remediation_settings_panel
        and js_has_auth_evidence_state
        and js_has_auth_remediation_state
        and js_has_auth_evidence_loader
        and js_has_auth_remediation_loader
        and js_has_auth_remediation_actions
        and js_refresh_protected_data_loads_auth_bundles
        and js_auth_evidence_has_first_gap_actions
        and js_render_settings_uses_auth_evidence
        and js_render_settings_uses_auth_remediation
        and js_logout_clears_auth_bundles
    )
    print(
        json.dumps(
            {
                "htmlHasAuthEvidenceSettingsPanel": html_has_auth_evidence_settings_panel,
                "htmlHasAuthRemediationSettingsPanel": html_has_auth_remediation_settings_panel,
                "jsHasAuthEvidenceState": js_has_auth_evidence_state,
                "jsHasAuthRemediationState": js_has_auth_remediation_state,
                "jsHasAuthEvidenceLoader": js_has_auth_evidence_loader,
                "jsHasAuthRemediationLoader": js_has_auth_remediation_loader,
                "jsHasAuthRemediationActions": js_has_auth_remediation_actions,
                "jsRefreshProtectedDataLoadsAuthBundles": js_refresh_protected_data_loads_auth_bundles,
                "jsAuthEvidenceHasFirstGapActions": js_auth_evidence_has_first_gap_actions,
                "jsRenderSettingsUsesAuthEvidence": js_render_settings_uses_auth_evidence,
                "jsRenderSettingsUsesAuthRemediation": js_render_settings_uses_auth_remediation,
                "jsLogoutClearsAuthBundles": js_logout_clears_auth_bundles,
                "authSettingsUiFlowIsWired": auth_settings_ui_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
