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
                "htmlHasProviderStatusPanel": 'settingsProviderStatusTitle' in html and 'settingsProviderStatusList' in html,
                "jsLoadStatusMatrixRefreshesSettings": 'renderProviderPanel();' in app_js and 'renderSettingsPanel();' in app_js,
                "jsRenderSettingsUsesProviderStatusSummary": 'const providerStatusSummary = state.statusMatrix?.summary || {};' in app_js and 'runtimeBlockedProviders=' in app_js and 'runtimeBlocked=' in app_js and 'runtimeConflictHandled=' in app_js and 'runtimeActive=' in app_js and 'runtimeCandidate=' in app_js and 'runtimeTrackBlocked=' in app_js,
                "jsSetsProviderStatusTitle": 'document.getElementById("settingsProviderStatusTitle").textContent = "Provider Status Matrix";' in app_js,
                "jsLogoutClearsStatusMatrix": 'state.statusMatrix = null;' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
