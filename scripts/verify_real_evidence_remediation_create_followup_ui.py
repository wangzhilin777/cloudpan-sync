from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    print(
        json.dumps(
            {
                "jsCreateRemediationUsesSummaryPanel": 'setAuthValidationSummary(data, "Remediation Stub");' in app_js,
                "jsCreateRemediationStoresLatestAction": "state.lastRemediationAction = data;" in app_js,
                "jsCreateRemediationOnlyAutoJumpsWhenStubCreated": 'if (data?.created === true && createdProfile) {' in app_js,
                "jsLatestRemediationActionStaysInSettings": "latestRemediationAction=" in app_js
                and "const latestIsExisting = lastRemediationAction.created === false && lastRemediationAction.status === \"already_exists\";" in app_js
                and 'focus: latestIsExisting ? "Focus Existing Profile" : "Focus Latest Created Stub"' in app_js
                and 'refresh: latestIsExisting ? "Refresh Existing Profile" : "Refresh Latest Created Stub"' in app_js
                and 'probe: latestIsExisting ? "Probe Existing Profile" : "Probe Latest Created Stub"' in app_js
                and 'capture: latestIsExisting ? "Open Capture For Existing Profile" : "Open Capture For Latest Created Stub"' in app_js,
                "jsCreateFollowupUsesAccurateLabels": 'focus: followupIsExisting ? "Focus Existing Profile" : "Focus Created Stub"' in app_js
                and 'refresh: followupIsExisting ? "Refresh Existing Profile" : "Refresh Created Stub"' in app_js
                and 'probe: followupIsExisting ? "Probe Existing Profile" : "Probe Created Stub"' in app_js
                and 'capture: followupIsExisting ? "Open Capture For Existing Profile" : "Open Capture For Created Stub"' in app_js,
                "jsSummaryFollowupDetectsBootstrapChain": "data?.recommendedBootstrapCommand" in app_js
                and "data?.recommendedPostBootstrapRuntimeCommand" in app_js,
                "jsSummaryFollowupReusesDirectActions": "focusBtn.textContent = followupLabels.focus;" in app_js
                and "refreshBtn.textContent = followupLabels.refresh;" in app_js
                and "probeBtn.textContent = followupLabels.probe;" in app_js
                and "captureBtn.textContent = followupLabels.capture;" in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
