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
                "htmlHasLocalAdapterVerificationPanel": "settingsLocalAdapterVerificationTitle" in html and "settingsLocalAdapterVerificationList" in html,
                "jsHasLocalAdapterVerificationState": "localLiveAdapterVerification: null" in app_js,
                "jsHasLocalAdapterVerificationLoader": 'async function loadLocalLiveAdapterVerificationSummary()' in app_js and 'fetchJson("/api/local_live_adapter_verification")' in app_js,
                "jsRefreshProtectedDataLoadsLocalAdapterVerification": "loadLocalLiveAdapterVerificationSummary()," in app_js,
                "jsHasLocalAdapterFirstGapActions": 'const firstLocalAdapterGap =' in app_js
                and 'focusBtn.textContent = "Focus First Gap"' in app_js
                and 'refreshBtn.textContent = "Refresh First Gap"' in app_js
                and 'probeBtn.textContent = "Run First Probe"' in app_js
                and 'captureBtn.textContent = "Open Capture First Gap"' in app_js
                and 'createBtn.textContent = "Create Stub First Gap"' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(matchedProfile.profileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstLocalAdapterGap.providerKey || ""));' in app_js
                and 'createBtn.addEventListener("click", () => createRemediationProfile(firstLocalAdapterGap.providerKey || ""));' in app_js,
                "jsRenderSettingsUsesLocalAdapterVerification": "const localAdapterSummary = state.localLiveAdapterVerification?.summary || {};" in app_js
                and "allOkProviders=" in app_js
                and "md5ReadyProviders=" in app_js
                and "gcidReadyProviders=" in app_js
                and "probeReadyProviders=" in app_js
                and "matrixReadyProviders=" in app_js
                and "accountCreateModeProviders=" in app_js
                and "probeChecks=${item.probeChecksReady || 0}" in app_js
                and "createMode=${item.create_mode || \"(none)\"}" in app_js
                and "matrix=list:${Boolean(matrixRow.list_ready)}" in app_js,
                "jsLogoutClearsLocalAdapterVerification": "state.localLiveAdapterVerification = null;" in app_js,
                "localLiveAdapterVerificationSettingsUiFlowIsWired": (
                    "settingsLocalAdapterVerificationTitle" in html
                    and "settingsLocalAdapterVerificationList" in html
                    and "localLiveAdapterVerification: null" in app_js
                    and 'async function loadLocalLiveAdapterVerificationSummary()' in app_js
                    and 'fetchJson("/api/local_live_adapter_verification")' in app_js
                    and "loadLocalLiveAdapterVerificationSummary()," in app_js
                    and 'const firstLocalAdapterGap =' in app_js
                    and 'focusBtn.textContent = "Focus First Gap"' in app_js
                    and 'refreshBtn.textContent = "Refresh First Gap"' in app_js
                    and 'probeBtn.textContent = "Run First Probe"' in app_js
                    and 'captureBtn.textContent = "Open Capture First Gap"' in app_js
                    and 'createBtn.textContent = "Create Stub First Gap"' in app_js
                    and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(matchedProfile.profileId));' in app_js
                    and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                    and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                    and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstLocalAdapterGap.providerKey || ""));' in app_js
                    and 'createBtn.addEventListener("click", () => createRemediationProfile(firstLocalAdapterGap.providerKey || ""));' in app_js
                    and "const localAdapterSummary = state.localLiveAdapterVerification?.summary || {};" in app_js
                    and "allOkProviders=" in app_js
                    and "md5ReadyProviders=" in app_js
                    and "gcidReadyProviders=" in app_js
                    and "probeReadyProviders=" in app_js
                    and "matrixReadyProviders=" in app_js
                    and "accountCreateModeProviders=" in app_js
                    and "probeChecks=${item.probeChecksReady || 0}" in app_js
                    and "createMode=${item.create_mode || \"(none)\"}" in app_js
                    and "matrix=list:${Boolean(matrixRow.list_ready)}" in app_js
                    and "state.localLiveAdapterVerification = null;" in app_js
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
