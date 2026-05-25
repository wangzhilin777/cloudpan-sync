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
