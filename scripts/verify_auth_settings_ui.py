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
                "htmlHasAuthEvidenceSettingsPanel": "settingsAuthEvidenceTitle" in html and "settingsAuthEvidenceList" in html,
                "htmlHasAuthRemediationSettingsPanel": "settingsAuthRemediationTitle" in html and "settingsAuthRemediationList" in html,
                "jsHasAuthEvidenceState": "authEvidenceBundle: null" in app_js,
                "jsHasAuthRemediationState": "authRemediationBundle: null" in app_js,
                "jsHasAuthEvidenceLoader": 'async function loadAuthEvidenceBundleSummary()' in app_js and 'fetchJson("/api/auth/evidence_bundle")' in app_js,
                "jsHasAuthRemediationLoader": 'async function loadAuthRemediationBundleSummary()' in app_js and 'fetchJson("/api/auth/remediation_bundle")' in app_js,
                "jsHasAuthRemediationActions": 'function focusAuthRemediationProfile(profileId)' in app_js and 'async function openCaptureGuideForProvider(providerKey)' in app_js and 'focus: "Focus Existing Profile"' in app_js and 'capture: "Open Capture For Existing Profile"' in app_js and 'focusBtn.textContent = remediationLabels.focus;' in app_js and 'captureBtn.textContent = remediationLabels.capture;' in app_js,
                "jsRefreshProtectedDataLoadsAuthBundles": "loadAuthEvidenceBundleSummary()," in app_js and "loadAuthRemediationBundleSummary()," in app_js,
                "jsAuthEvidenceHasFirstGapActions": 'const firstAuthEvidenceGap = (state.authEvidenceBundle?.items || []).find((item) => {' in app_js
                and 'focusBtn.textContent = "Focus First Gap"' in app_js
                and 'refreshBtn.textContent = "Refresh First Gap"' in app_js
                and 'captureBtn.textContent = "Open Capture First Gap"' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(firstProfile.profileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(firstProfile.profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstProfile.providerKey || ""));' in app_js
                and "const missing = (firstProfile.missingFieldHints || []).join(\" | \");" in app_js
                and "const placeholderSecretHints = (firstProfile.placeholderSecretFieldHints || []).join(\" | \");" in app_js
                and "const liveRejectedStatuses = (firstProfile.liveRejectedStatuses || []).join(\"/\") || \"\";" in app_js
                and "const placeholderLiveRejectedProfiles = (firstProfile.placeholderLiveRejectedProfiles || []).join(\"/\") || \"\";" in app_js
                and "const liveRejectedSummaries = (firstProfile.liveRejectedSummaries || []).join(\" | \") || \"\";" in app_js
                and "missing=${missing}" in app_js
                and "placeholderSecretHints=${placeholderSecretHints}" in app_js
                and "liveRejectedStatuses=${liveRejectedStatuses}" in app_js
                and "placeholderLiveRejectedProfiles=${placeholderLiveRejectedProfiles}" in app_js
                and "liveRejectedSummaries=${liveRejectedSummaries}" in app_js,
                "jsRenderSettingsUsesAuthEvidence": "const authEvidenceSummary = state.authEvidenceBundle?.summary || {};" in app_js
                and "profileReadyProfiles=" in app_js
                and "writeReadyProfiles=" in app_js
                and "validationOkProfiles=" in app_js
                and "probeOkProfiles=" in app_js,
                "jsRenderSettingsUsesAuthRemediation": "const authRemediationSummary = state.authRemediationBundle?.summary || {};" in app_js
                and 'const firstAuthRemediationGap = (state.authRemediationBundle?.items || []).find((item) => item?.needsFix || item?.writeNeedsFix || item?.needsSecretRefresh) || null;' in app_js
                and 'focusBtn.textContent = "Focus First Fix"' in app_js
                and 'captureBtn.textContent = "Open Capture First Fix"' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(firstAuthRemediationGap.profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstAuthRemediationGap.providerKey || ""));' in app_js
                and "const firstLiveRejectedStatuses = (firstAuthRemediationGap.liveRejectedStatuses || []).join(\"/\") || \"\";" in app_js
                and "const firstPlaceholderLiveRejectedProfiles = (firstAuthRemediationGap.placeholderLiveRejectedProfiles || []).join(\"/\") || \"\";" in app_js
                and "const firstLiveRejectedSummaries = (firstAuthRemediationGap.liveRejectedSummaries || []).join(\" | \") || \"\";" in app_js
                and "readyProfiles=" in app_js
                and "needsFixProfiles=" in app_js
                and "writeNeedsFixProfiles=" in app_js
                and "needsSecretRefreshProfiles=" in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(item.profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js
                and "placeholderSecretHints=" in app_js
                and "liveRejectedStatuses=" in app_js
                and "placeholderLiveRejectedProfiles=" in app_js
                and "liveRejectedSummaries=" in app_js
                and "liveRejectedStatuses=${firstLiveRejectedStatuses}" in app_js
                and "placeholderLiveRejectedProfiles=${firstPlaceholderLiveRejectedProfiles}" in app_js
                and "liveRejectedSummaries=${firstLiveRejectedSummaries}" in app_js
                and "recreateProbe=" in app_js,
                "jsLogoutClearsAuthBundles": "state.authEvidenceBundle = null;" in app_js and "state.authRemediationBundle = null;" in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
