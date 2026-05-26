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
    html_has_real_evidence_panel = 'settingsRealEvidenceTitle' in html and 'settingsRealEvidenceList' in html
    js_has_real_evidence_state = 'realEvidenceSummary: null' in app_js
    js_has_real_evidence_loader = 'async function loadRealEvidenceSummary()' in app_js and 'fetchJson("/api/real_evidence")' in app_js
    js_refresh_protected_data_loads_real_evidence = 'loadRealEvidenceSummary(),' in app_js
    js_has_real_evidence_first_gap_actions = 'const firstRealEvidenceGap = (state.realEvidenceRemediation?.items || []).find((item) => item?.nextStep) || null;' in app_js \
        and 'const firstGapOrphanProfileId = (firstRealEvidenceGap.runtimeOrphanProfiles || [])[0] || "";' in app_js \
        and 'const firstGapOrphanItems = (firstRealEvidenceGap.runtimeOrphanProfiles || []).map((runtimeOrphanProfileId) => ({' in app_js \
        and 'focus: firstGapHasProfile ? "Focus Existing Profile" : "Focus First Gap"' in app_js \
        and 'refresh: firstGapHasProfile ? "Refresh Existing Profile" : "Refresh First Gap"' in app_js \
        and 'probe: firstGapHasProfile ? "Probe Existing Profile" : "Run First Probe"' in app_js \
        and 'capture: firstGapHasProfile ? "Open Capture For Existing Profile" : "Open Capture First Gap"' in app_js \
        and 'createBtn.textContent = "Create Stub First Gap"' in app_js \
        and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(profileId));' in app_js \
        and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(profileId));' in app_js \
        and 'if (liveProbeProviderSet.has(firstRealEvidenceGap.providerKey)) {' in app_js \
        and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(profileId));' in app_js \
        and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstRealEvidenceGap.providerKey || ""));' in app_js \
        and 'createBtn.addEventListener("click", () => createRemediationProfile(firstRealEvidenceGap.providerKey || ""));' in app_js \
        and 'appendRuntimeOrphanRecreateButtons(actions, firstGapOrphanItems, "Recreate Orphan Stub First Gap");' in app_js
    js_render_settings_uses_real_evidence = 'const realEvidence = state.realEvidenceSummary || {};' in app_js \
        and 'latestValidationProfiles=' in app_js \
        and 'latestProbeProfiles=' in app_js \
        and 'task_runtime=' in app_js \
        and 'task_runtime_failed=' in app_js \
        and 'task_runtime_candidate=' in app_js \
        and 'task_runtime_probe=' in app_js \
        and 'runtime_samples=' in app_js \
        and 'runtime_success=' in app_js \
        and 'runtime_failed=' in app_js \
        and 'runtime_candidate=' in app_js \
        and 'runtime_probe=' in app_js \
        and 'runtime_blocked_providers=' in app_js \
        and 'runtime_blocked=' in app_js \
        and 'runtime_conflict_handled=' in app_js \
        and 'runtime_orphan_providers=' in app_js \
        and 'runtime_orphan_profiles=' in app_js \
        and 'fully_verified=' in app_js \
        and 'authProviders=' in app_js \
        and 'listProviders=' in app_js \
        and 'metadataProviders=' in app_js \
        and 'createDirProviders=' in app_js \
        and 'fullyVerifiedProviders=' in app_js \
        and 'runtimeSuccessProviders=' in app_js \
        and 'runtimeFailedProvidersList=' in app_js \
        and 'runtimeCandidateProvidersList=' in app_js \
        and 'runtimeProbeProvidersList=' in app_js \
        and 'runtimeBlockedProvidersList=' in app_js \
        and 'runtimeOrphanProvidersList=' in app_js \
        and 'runtimeOrphanProfilesList=' in app_js \
        and 'const firstRealEvidenceOrphanItem = (state.runtimeOrphanRecovery?.items || [])[0] || null;' in app_js \
        and 'runtime_orphan_recovery: providers=${realEvidence.taskRuntimeOrphanProviderCount || 0}' in app_js \
        and 'openOrphanBtn.textContent = "Open Runtime Orphan Recovery";' in app_js \
        and 'appendRuntimeOrphanRecreateButtons(actions, state.runtimeOrphanRecovery?.items || [], "Recreate Orphan Stub");' in app_js
    js_logout_clears_real_evidence = 'state.realEvidenceSummary = null;' in app_js
    real_evidence_settings_ui_flow_is_wired = (
        html_has_real_evidence_panel
        and js_has_real_evidence_state
        and js_has_real_evidence_loader
        and js_refresh_protected_data_loads_real_evidence
        and js_has_real_evidence_first_gap_actions
        and js_render_settings_uses_real_evidence
        and js_logout_clears_real_evidence
    )
    print(
        json.dumps(
            {
                "htmlHasRealEvidencePanel": html_has_real_evidence_panel,
                "jsHasRealEvidenceState": js_has_real_evidence_state,
                "jsHasRealEvidenceLoader": js_has_real_evidence_loader,
                "jsRefreshProtectedDataLoadsRealEvidence": js_refresh_protected_data_loads_real_evidence,
                "jsHasRealEvidenceFirstGapActions": js_has_real_evidence_first_gap_actions,
                "jsRenderSettingsUsesRealEvidence": js_render_settings_uses_real_evidence,
                "jsLogoutClearsRealEvidence": js_logout_clears_real_evidence,
                "realEvidenceSettingsUiFlowIsWired": real_evidence_settings_ui_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
