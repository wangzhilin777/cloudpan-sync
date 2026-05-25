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
                "jsHasRuntimeOrphanRecoveryState": "runtimeOrphanRecovery: null" in app_js and "lastRuntimeOrphanAction: null" in app_js,
                "jsHasRuntimeOrphanRecoveryLoader": 'async function loadRuntimeOrphanRecoverySummary()' in app_js and 'fetchJson("/api/runtime_orphan_recovery")' in app_js,
                "jsHasRuntimeOrphanRecoveryRecreateAction": 'async function recreateRuntimeOrphanProfile(providerKey, orphanProfileId)' in app_js and 'fetchJson("/api/runtime_orphan_recovery/recreate_profile"' in app_js and 'recreateBtn.textContent = "Recreate Stub"' in app_js,
                "jsHasRuntimeOrphanRecoveryCaptureAction": 'captureBtn.textContent = "Open Capture"' in app_js and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js,
                "jsHasRuntimeOrphanRecoveryFirstGapActions": 'const firstRuntimeOrphanGap = orphanRecoveryItems[0] || null;' in app_js
                and 'focus: hasExistingProfile ? "Focus Existing Orphan Profile" : "Focus First Match"' in app_js
                and 'refresh: hasExistingProfile ? "Refresh Existing Orphan Profile" : "Refresh First Match"' in app_js
                and 'probe: hasExistingProfile ? "Probe Existing Orphan Profile" : "Probe First Match"' in app_js
                and 'recreateBtn.textContent = "Recreate First Stub"' in app_js
                and 'capture: hasExistingProfile ? "Open Capture For Existing Orphan Profile" : "Open Capture First Gap"' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(existingProfileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(existingProfileId));' in app_js
                and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(existingProfileId));' in app_js
                and 'recreateBtn.addEventListener("click", () => recreateRuntimeOrphanProfile(firstRuntimeOrphanGap.providerKey, firstRuntimeOrphanGap.orphanProfileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstRuntimeOrphanGap.providerKey || ""));' in app_js,
                "jsRefreshProtectedDataLoadsRuntimeOrphanRecovery": "loadRuntimeOrphanRecoverySummary()," in app_js,
                "jsLogoutClearsRuntimeOrphanRecovery": "state.runtimeOrphanRecovery = null;" in app_js and "state.lastRuntimeOrphanAction = null;" in app_js,
                "jsSettingsRenderUsesRuntimeOrphanRecovery": "const orphanRecoverySummary = state.runtimeOrphanRecovery?.summary || {};" in app_js and "latestRuntimeOrphanAction=" in app_js and "orphanProfilesList=" in app_js and "recreate=" in app_js and "refresh=" in app_js and "runtimeProbe=" in app_js and "runtimeSuccess=" in app_js and "overwriteVariant=" in app_js and 'recreateBtn.addEventListener("click", () => recreateRuntimeOrphanProfile(item.providerKey, item.orphanProfileId));' in app_js and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
