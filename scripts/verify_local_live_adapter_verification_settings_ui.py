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
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
