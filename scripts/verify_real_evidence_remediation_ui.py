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
                "htmlHasRemediationPanel": "settingsRealEvidenceRemediationTitle" in html and "settingsRealEvidenceRemediationList" in html,
                "jsHasRemediationState": "realEvidenceRemediation: null" in app_js,
                "jsHasRemediationLoader": 'async function loadRealEvidenceRemediationSummary()' in app_js and 'fetchJson("/api/real_evidence_remediation_bundle")' in app_js,
                "jsRefreshProtectedDataLoadsRemediation": "loadRealEvidenceRemediationSummary()," in app_js,
                "jsLogoutClearsRemediation": "state.realEvidenceRemediation = null;" in app_js,
                "jsSettingsRenderUsesRemediation": "settingsRealEvidenceRemediationList" in app_js and "providersWithNoProfiles" in app_js and "providersNeedingRuntimeSuccess" in app_js and "recommendedAuthModes" in app_js and "webLoginUrl" in app_js and "requiredFieldHints" in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
