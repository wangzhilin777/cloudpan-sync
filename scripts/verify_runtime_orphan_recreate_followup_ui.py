from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    print(
        json.dumps(
            {
                "jsHasOrphanFollowupDetection": "const hasOrphanFollowup = Boolean(" in app_js
                and "data?.recommendedBootstrapCommand" in app_js
                and "data?.recommendedRefreshEvidenceCommand" in app_js
                and "data?.exactRefreshEvidenceHelper" in app_js
                and "data?.recommendedRuntimeProbeCommand" in app_js
                and "data?.exactRuntimeProbeHelper" in app_js
                and "data?.recommendedRuntimeSuccessCommand" in app_js
                and "data?.exactRuntimeSuccessHelper" in app_js
                and "data?.recommendedPostBootstrapRuntimeCommand" in app_js
                and "data?.recommendedOverwriteVariantCommand" in app_js
                and "data?.exactOverwriteVariantHelper" in app_js,
                "jsStoresLatestOrphanAction": "state.lastRuntimeOrphanAction = data;" in app_js,
                "jsOnlyAutoJumpsWhenOrphanStubCreated": 'if (data?.created === true && recreated) {' in app_js,
                "jsOrphanFollowupUsesAccurateLabels": 'focus: followupIsExisting ? "Focus Existing Orphan Profile" : "Focus Recreated Stub"' in app_js
                and 'refresh: followupIsExisting ? "Refresh Existing Orphan Profile" : "Refresh Recreated Stub"' in app_js
                and 'probe: followupIsExisting ? "Probe Existing Orphan Profile" : "Probe Recreated Stub"' in app_js
                and 'capture: followupIsExisting ? "Open Capture For Existing Orphan Profile" : "Open Capture For Recreated Stub"' in app_js,
                "jsHasOrphanFollowupActions": 'focusBtn.textContent = followupLabels.focus;' in app_js
                and 'refreshBtn.textContent = followupLabels.refresh;' in app_js
                and 'probeBtn.textContent = followupLabels.probe;' in app_js
                and 'captureBtn.textContent = followupLabels.capture;' in app_js,
                "jsLatestOrphanActionStaysInSettings": "latestRuntimeOrphanAction=" in app_js
                and "const latestIsExisting = lastRuntimeOrphanAction.created === false && lastRuntimeOrphanAction.status === \"already_exists\";" in app_js
                and 'focus: latestIsExisting ? "Focus Existing Orphan Profile" : "Focus Latest Recreated Stub"' in app_js
                and 'refresh: latestIsExisting ? "Refresh Existing Orphan Profile" : "Refresh Latest Recreated Stub"' in app_js
                and 'probe: latestIsExisting ? "Probe Existing Orphan Profile" : "Probe Latest Recreated Stub"' in app_js
                and 'capture: latestIsExisting ? "Open Capture For Existing Orphan Profile" : "Open Capture For Latest Recreated Stub"' in app_js,
                "jsHasOrphanFollowupBindings": 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(followupProfileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(followupProfileId));' in app_js
                and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(followupProfileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(followupProviderKey));' in app_js,
                "jsLatestOrphanActionShowsExactHelpers": "exactRefresh=" in app_js
                and "exactRuntimeProbe=" in app_js
                and "exactRuntimeSuccess=" in app_js
                and "exactOverwriteVariant=" in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
