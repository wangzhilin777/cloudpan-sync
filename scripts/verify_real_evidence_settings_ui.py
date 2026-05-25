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
                "htmlHasRealEvidencePanel": 'settingsRealEvidenceTitle' in html and 'settingsRealEvidenceList' in html,
                "jsHasRealEvidenceState": 'realEvidenceSummary: null' in app_js,
                "jsHasRealEvidenceLoader": 'async function loadRealEvidenceSummary()' in app_js and 'fetchJson("/api/real_evidence")' in app_js,
                "jsRefreshProtectedDataLoadsRealEvidence": 'loadRealEvidenceSummary(),' in app_js,
                "jsHasRealEvidenceFirstGapActions": 'const firstRealEvidenceGap = (state.realEvidenceRemediation?.items || []).find((item) => item?.nextStep) || null;' in app_js
                and 'focus: firstGapHasProfile ? "Focus Existing Profile" : "Focus First Gap"' in app_js
                and 'refresh: firstGapHasProfile ? "Refresh Existing Profile" : "Refresh First Gap"' in app_js
                and 'probe: firstGapHasProfile ? "Probe Existing Profile" : "Run First Probe"' in app_js
                and 'capture: firstGapHasProfile ? "Open Capture For Existing Profile" : "Open Capture First Gap"' in app_js
                and 'createBtn.textContent = "Create Stub First Gap"' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(profileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(profileId));' in app_js
                and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstRealEvidenceGap.providerKey || ""));' in app_js
                and 'createBtn.addEventListener("click", () => createRemediationProfile(firstRealEvidenceGap.providerKey || ""));' in app_js,
                "jsRenderSettingsUsesRealEvidence": 'const realEvidence = state.realEvidenceSummary || {};' in app_js and 'latestValidationProfiles=' in app_js and 'latestProbeProfiles=' in app_js and 'task_runtime=' in app_js and 'task_runtime_failed=' in app_js and 'task_runtime_candidate=' in app_js and 'task_runtime_probe=' in app_js and 'runtime_samples=' in app_js and 'runtime_success=' in app_js and 'runtime_failed=' in app_js and 'runtime_candidate=' in app_js and 'runtime_probe=' in app_js and 'runtime_blocked_providers=' in app_js and 'runtime_blocked=' in app_js and 'runtime_conflict_handled=' in app_js and 'runtime_orphan_providers=' in app_js and 'runtime_orphan_profiles=' in app_js and 'fully_verified=' in app_js and 'authProviders=' in app_js and 'listProviders=' in app_js and 'metadataProviders=' in app_js and 'createDirProviders=' in app_js and 'fullyVerifiedProviders=' in app_js and 'runtimeSuccessProviders=' in app_js and 'runtimeFailedProvidersList=' in app_js and 'runtimeCandidateProvidersList=' in app_js and 'runtimeProbeProvidersList=' in app_js and 'runtimeBlockedProvidersList=' in app_js and 'runtimeOrphanProvidersList=' in app_js and 'runtimeOrphanProfilesList=' in app_js,
                "jsLogoutClearsRealEvidence": 'state.realEvidenceSummary = null;' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
