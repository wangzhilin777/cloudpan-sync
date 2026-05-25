from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    html = (ROOT / "src" / "cloudpan_sync" / "web" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    print(
        json.dumps(
            {
                "htmlHasRuntimeOrphanRecoveryPanel": "settingsRuntimeOrphanRecoveryList" in html and "Runtime Orphan Recovery" in html,
                "jsHasRuntimeOrphanRecoveryState": "runtimeOrphanRecovery: null" in app_js,
                "jsHasRuntimeOrphanRecoveryLoader": 'async function loadRuntimeOrphanRecoverySummary()' in app_js and 'fetchJson("/api/runtime_orphan_recovery")' in app_js,
                "jsRefreshProtectedDataLoadsRuntimeOrphanRecovery": "loadRuntimeOrphanRecoverySummary()," in app_js,
                "jsLogoutClearsRuntimeOrphanRecovery": "state.runtimeOrphanRecovery = null;" in app_js,
                "jsSettingsRenderUsesRuntimeOrphanRecovery": "const orphanRecoverySummary = state.runtimeOrphanRecovery?.summary || {};" in app_js and "orphanProfilesList=" in app_js and "recreate=" in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
