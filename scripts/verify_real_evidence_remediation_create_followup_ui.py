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
                and 'focusBtn.textContent = "Focus Latest Stub"' in app_js
                and 'refreshBtn.textContent = "Refresh Latest Stub"' in app_js
                and 'probeBtn.textContent = "Probe Latest Stub"' in app_js
                and 'captureBtn.textContent = "Open Capture For Latest Stub"' in app_js,
                "jsSummaryFollowupDetectsBootstrapChain": "data?.recommendedBootstrapCommand" in app_js
                and "data?.recommendedPostBootstrapRuntimeCommand" in app_js,
                "jsSummaryFollowupReusesDirectActions": 'focusBtn.textContent = "Focus Recreated Stub"' in app_js
                and 'refreshBtn.textContent = "Refresh Recreated Stub"' in app_js
                and 'probeBtn.textContent = "Probe Recreated Stub"' in app_js
                and 'captureBtn.textContent = "Open Capture For Recreated Stub"' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
