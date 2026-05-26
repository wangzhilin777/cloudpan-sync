from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    html = (ROOT / "src" / "cloudpan_sync" / "web" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    print(
        json.dumps(
            {
                "htmlHasRuntimeOrphanRecoveryPanel": "settingsRuntimeOrphanRecoveryList" in html and "Runtime Orphan Recovery" in html,
                "jsHasRuntimeOrphanRecoveryState": "runtimeOrphanRecovery: null" in app_js and "lastRuntimeOrphanAction: null" in app_js and "lastRuntimeOrphanBatchAction: null" in app_js,
                "jsHasRuntimeOrphanRecoveryLoader": 'async function loadRuntimeOrphanRecoverySummary()' in app_js and 'fetchJson("/api/runtime_orphan_recovery")' in app_js,
                "jsHasRuntimeOrphanRecoveryRecreateAction": 'async function recreateRuntimeOrphanProfile(providerKey, orphanProfileId)' in app_js and 'fetchJson("/api/runtime_orphan_recovery/recreate_profile"' in app_js and 'recreateBtn.textContent = "Recreate Orphan Stub"' in app_js,
                "jsHasRuntimeOrphanRecoveryBatchAction": 'async function batchRecreateRuntimeOrphanProfiles(providerKey = "", overwriteExisting = false)' in app_js and 'fetchJson("/api/runtime_orphan_recovery/recreate_profiles"' in app_js and 'batchBtn.textContent = "Batch Recreate Missing Orphan Stubs"' in app_js and 'overwriteBtn.textContent = "Batch Overwrite Existing Orphan Stubs"' in app_js,
                "jsHasRuntimeOrphanRecoveryCaptureAction": 'captureBtn.textContent = existingProfileId ? orphanRowLabels.capture : "Open Capture";' in app_js and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js,
                "jsHasRuntimeOrphanRecoveryExistingProfileRowActions": 'const existingProfileId = (item.existingProviderProfileIds || [])[0] || "";' in app_js
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
                and 'captureBtn.textContent = existingProfileId ? orphanRowLabels.capture : "Open Capture";' in app_js,
                "jsHasRuntimeOrphanRecoveryFirstGapActions": 'const firstRuntimeOrphanGap = orphanRecoveryItems[0] || null;' in app_js
                and 'focus: hasExistingProfile ? "Focus Existing Orphan Profile" : "Focus First Match"' in app_js
                and 'refresh: hasExistingProfile ? "Refresh Existing Orphan Profile" : "Refresh First Match"' in app_js
                and 'probe: hasExistingProfile ? "Probe Existing Orphan Profile" : "Probe First Match"' in app_js
                and 'recreateBtn.textContent = "Recreate Orphan Stub First Gap"' in app_js
                and 'capture: hasExistingProfile ? "Open Capture For Existing Orphan Profile" : "Open Capture First Gap"' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(existingProfileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(existingProfileId));' in app_js
                and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(existingProfileId));' in app_js
                and 'recreateBtn.addEventListener("click", () => recreateRuntimeOrphanProfile(firstRuntimeOrphanGap.providerKey, firstRuntimeOrphanGap.orphanProfileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstRuntimeOrphanGap.providerKey || ""));' in app_js,
                "jsRefreshProtectedDataLoadsRuntimeOrphanRecovery": "loadRuntimeOrphanRecoverySummary()," in app_js,
                "jsLogoutClearsRuntimeOrphanRecovery": "state.runtimeOrphanRecovery = null;" in app_js and "state.lastRuntimeOrphanAction = null;" in app_js and "state.lastRuntimeOrphanBatchAction = null;" in app_js,
                "jsSettingsRenderUsesRuntimeOrphanRecovery": "const orphanRecoverySummary = state.runtimeOrphanRecovery?.summary || {};" in app_js and "latestRuntimeOrphanAction=" in app_js and "latestRuntimeOrphanBatchAction=" in app_js and "runtime_orphan_batch_actions:" in app_js and "orphanProfilesList=" in app_js and "batchDryRun=" in app_js and "batchWriteMissing=" in app_js and "batchOverwriteExisting=" in app_js and "primary=" in app_js and "primaryLabel=" in app_js and "recreate=" in app_js and "exactRecreate=" in app_js and "refresh=" in app_js and "exactRefresh=" in app_js and "runtimeProbe=" in app_js and "exactRuntimeProbe=" in app_js and "runtimeSuccess=" in app_js and "exactRuntimeSuccess=" in app_js and "overwriteVariant=" in app_js and "exactOverwriteVariant=" in app_js and 'batchBtn.addEventListener("click", () => batchRecreateRuntimeOrphanProfiles("", false));' in app_js and 'overwriteBtn.addEventListener("click", () => batchRecreateRuntimeOrphanProfiles("", true));' in app_js and 'recreateBtn.addEventListener("click", () => recreateRuntimeOrphanProfile(item.providerKey, item.orphanProfileId));' in app_js and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
