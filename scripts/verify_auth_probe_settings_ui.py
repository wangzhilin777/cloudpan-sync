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
                "htmlHasValidationAndProbePanels": "settingsValidationList" in html and "settingsProviderProbeList" in html,
                "jsValidationSummaryShowsProfiles": 'const validationSummary = state.liveValidationMeta?.summary || {};' in app_js
                and 'okProfiles=' in app_js
                and 'failedProfiles=' in app_js
                and 'okProviders=' in app_js
                and 'failedProviders=' in app_js
                and 'failedModes=' in app_js,
                "jsProbeSummaryShowsProfiles": 'const probeSummary = state.providerLiveProbeMeta?.summary || {};' in app_js
                and 'okProfiles=' in app_js
                and 'failedProfiles=' in app_js
                and 'providers=' in app_js,
                "jsRefreshProtectedDataLoadsBoth": 'async function refreshProtectedData()' in app_js and 'state.liveValidationMeta = {' in app_js and 'state.providerLiveProbeMeta = {' in app_js,
                "jsLogoutClearsBoth": 'state.liveValidationMeta = { historyCount: 0, summary: null };' in app_js and 'state.providerLiveProbeMeta = { historyCount: 0, summary: null };' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
