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
                "jsRefreshProtectedDataLoadsAuthBundles": "loadAuthEvidenceBundleSummary()," in app_js and "loadAuthRemediationBundleSummary()," in app_js,
                "jsRenderSettingsUsesAuthEvidence": "const authEvidenceSummary = state.authEvidenceBundle?.summary || {};" in app_js
                and "profileReadyProfiles=" in app_js
                and "writeReadyProfiles=" in app_js
                and "validationOkProfiles=" in app_js
                and "probeOkProfiles=" in app_js,
                "jsRenderSettingsUsesAuthRemediation": "const authRemediationSummary = state.authRemediationBundle?.summary || {};" in app_js
                and "readyProfiles=" in app_js
                and "needsFixProfiles=" in app_js
                and "writeNeedsFixProfiles=" in app_js
                and "needsSecretRefreshProfiles=" in app_js,
                "jsLogoutClearsAuthBundles": "state.authEvidenceBundle = null;" in app_js and "state.authRemediationBundle = null;" in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
