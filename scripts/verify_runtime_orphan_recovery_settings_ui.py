from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    html = (ROOT / "src" / "cloudpan_sync" / "web" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    html_has_runtime_orphan_recovery_panel = "settingsRuntimeOrphanRecoveryList" in html and "Runtime Orphan Recovery" in html
    js_has_runtime_orphan_recovery_state = (
        "runtimeOrphanRecovery: null" in app_js
        and "lastRuntimeOrphanAction: null" in app_js
        and "lastRuntimeOrphanBatchAction: null" in app_js
    )
    js_has_runtime_orphan_recovery_loader = (
        'async function loadRuntimeOrphanRecoverySummary()' in app_js
        and 'fetchJson("/api/runtime_orphan_recovery")' in app_js
    )
    js_has_runtime_orphan_recovery_recreate_action = (
        'async function recreateRuntimeOrphanProfile(providerKey, orphanProfileId)' in app_js
        and 'fetchJson("/api/runtime_orphan_recovery/recreate_profile"' in app_js
        and 'recreateBtn.textContent = "Recreate Orphan Stub"' in app_js
    )
    js_has_runtime_orphan_recovery_batch_action = (
        'async function batchRecreateRuntimeOrphanProfiles(providerKey = "", overwriteExisting = false)' in app_js
        and 'fetchJson("/api/runtime_orphan_recovery/recreate_profiles"' in app_js
        and 'batchBtn.textContent = "Batch Recreate Missing Orphan Stubs"' in app_js
        and 'overwriteBtn.textContent = "Batch Overwrite Existing Orphan Stubs"' in app_js
    )
    js_has_runtime_orphan_recovery_capture_action = (
        'captureBtn.textContent = existingProfileId ? orphanRowLabels.capture : "Open Capture";' in app_js
        and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js
    )
    js_has_runtime_orphan_recovery_existing_profile_row_actions = (
        'const existingProfileId = (item.existingProviderProfileIds || [])[0] || "";' in app_js
        and 'focus: "Focus Existing Orphan Profile"' in app_js
        and 'refresh: "Refresh Existing Orphan Profile"' in app_js
        and 'probe: "Probe Existing Orphan Profile"' in app_js
        and 'capture: "Open Capture For Existing Orphan Profile"' in app_js
        and 'focusBtn.textContent = orphanRowLabels.focus;' in app_js
        and 'refreshBtn.textContent = orphanRowLabels.refresh;' in app_js
        and 'if (liveProbeProviderSet.has(item.providerKey)) {' in app_js
        and 'probeBtn.textContent = orphanRowLabels.probe;' in app_js
        and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(existingProfileId));' in app_js
        and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(existingProfileId));' in app_js
        and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(existingProfileId));' in app_js
        and 'captureBtn.textContent = existingProfileId ? orphanRowLabels.capture : "Open Capture";' in app_js
    )
    js_has_runtime_orphan_recovery_first_gap_actions = (
        'const firstRuntimeOrphanGap = orphanRecoveryItems[0] || null;' in app_js
        and 'focus: hasExistingProfile ? "Focus Existing Orphan Profile" : "Focus First Match"' in app_js
        and 'refresh: hasExistingProfile ? "Refresh Existing Orphan Profile" : "Refresh First Match"' in app_js
        and 'probe: hasExistingProfile ? "Probe Existing Orphan Profile" : "Probe First Match"' in app_js
        and 'recreateBtn.textContent = "Recreate Orphan Stub First Gap"' in app_js
        and 'capture: hasExistingProfile ? "Open Capture For Existing Orphan Profile" : "Open Capture First Gap"' in app_js
        and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(existingProfileId));' in app_js
        and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(existingProfileId));' in app_js
        and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(existingProfileId));' in app_js
        and 'recreateBtn.addEventListener("click", () => recreateRuntimeOrphanProfile(firstRuntimeOrphanGap.providerKey, firstRuntimeOrphanGap.orphanProfileId));' in app_js
        and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstRuntimeOrphanGap.providerKey || ""));' in app_js
    )
    js_refresh_protected_data_loads_runtime_orphan_recovery = "loadRuntimeOrphanRecoverySummary()," in app_js
    js_logout_clears_runtime_orphan_recovery = (
        "state.runtimeOrphanRecovery = null;" in app_js
        and "state.lastRuntimeOrphanAction = null;" in app_js
        and "state.lastRuntimeOrphanBatchAction = null;" in app_js
    )
    js_settings_render_uses_runtime_orphan_recovery = (
        "const orphanRecoverySummary = state.runtimeOrphanRecovery?.summary || {};" in app_js
        and "latestRuntimeOrphanAction=" in app_js
        and "latestRuntimeOrphanBatchAction=" in app_js
        and "runtime_orphan_batch_actions:" in app_js
        and "orphanProfilesList=" in app_js
        and "batchDryRun=" in app_js
        and "batchWriteMissing=" in app_js
        and "batchOverwriteExisting=" in app_js
        and "primary=" in app_js
        and "primaryLabel=" in app_js
        and "recreate=" in app_js
        and "exactRecreate=" in app_js
        and "refresh=" in app_js
        and "exactRefresh=" in app_js
        and "runtimeProbe=" in app_js
        and "exactRuntimeProbe=" in app_js
        and "runtimeSuccess=" in app_js
        and "exactRuntimeSuccess=" in app_js
        and "overwriteVariant=" in app_js
        and "exactOverwriteVariant=" in app_js
        and 'batchBtn.addEventListener("click", () => batchRecreateRuntimeOrphanProfiles("", false));' in app_js
        and 'overwriteBtn.addEventListener("click", () => batchRecreateRuntimeOrphanProfiles("", true));' in app_js
        and 'recreateBtn.addEventListener("click", () => recreateRuntimeOrphanProfile(item.providerKey, item.orphanProfileId));' in app_js
        and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js
    )
    runtime_orphan_recovery_settings_ui_flow_is_wired = (
        html_has_runtime_orphan_recovery_panel
        and js_has_runtime_orphan_recovery_state
        and js_has_runtime_orphan_recovery_loader
        and js_has_runtime_orphan_recovery_recreate_action
        and js_has_runtime_orphan_recovery_batch_action
        and js_has_runtime_orphan_recovery_capture_action
        and js_has_runtime_orphan_recovery_existing_profile_row_actions
        and js_has_runtime_orphan_recovery_first_gap_actions
        and js_refresh_protected_data_loads_runtime_orphan_recovery
        and js_logout_clears_runtime_orphan_recovery
        and js_settings_render_uses_runtime_orphan_recovery
    )
    print(
        json.dumps(
            {
                "htmlHasRuntimeOrphanRecoveryPanel": html_has_runtime_orphan_recovery_panel,
                "jsHasRuntimeOrphanRecoveryState": js_has_runtime_orphan_recovery_state,
                "jsHasRuntimeOrphanRecoveryLoader": js_has_runtime_orphan_recovery_loader,
                "jsHasRuntimeOrphanRecoveryRecreateAction": js_has_runtime_orphan_recovery_recreate_action,
                "jsHasRuntimeOrphanRecoveryBatchAction": js_has_runtime_orphan_recovery_batch_action,
                "jsHasRuntimeOrphanRecoveryCaptureAction": js_has_runtime_orphan_recovery_capture_action,
                "jsHasRuntimeOrphanRecoveryExistingProfileRowActions": js_has_runtime_orphan_recovery_existing_profile_row_actions,
                "jsHasRuntimeOrphanRecoveryFirstGapActions": js_has_runtime_orphan_recovery_first_gap_actions,
                "jsRefreshProtectedDataLoadsRuntimeOrphanRecovery": js_refresh_protected_data_loads_runtime_orphan_recovery,
                "jsLogoutClearsRuntimeOrphanRecovery": js_logout_clears_runtime_orphan_recovery,
                "jsSettingsRenderUsesRuntimeOrphanRecovery": js_settings_render_uses_runtime_orphan_recovery,
                "runtimeOrphanRecoverySettingsUiFlowIsWired": runtime_orphan_recovery_settings_ui_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
