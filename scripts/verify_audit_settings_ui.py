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
                "htmlHasAuditPanel": 'settingsAuditTitle' in html and 'settingsAuditList' in html,
                "jsHasAuditSummaryState": 'auditSummary: null' in app_js and 'auditItems: []' in app_js,
                "jsHasAuditLoader": 'async function loadAuditSummary()' in app_js and 'fetchJson("/api/plan/audit")' in app_js,
                "jsRefreshProtectedDataLoadsAudit": 'loadAuditSummary(),' in app_js,
                "jsAuditHasFirstGapActions": 'state.auditItems = data.items || [];' in app_js
                and 'const firstAuditGap = auditItems.find((item) => item.status !== "done") || null;' in app_js
                and 'openSettingsBtn.textContent = "Open First Gap Settings"' in app_js
                and 'openProvidersBtn.textContent = "Open Provider Matrix"' in app_js
                and 'openAuthBtn.textContent = "Open Auth Profiles"' in app_js
                and 'state.activeTab = "nav.settings";' in app_js
                and 'state.activeTab = "nav.providers";' in app_js
                and 'state.activeTab = "nav.auth";' in app_js,
                "jsRenderSettingsUsesAuditSummary": 'const audit = state.auditSummary || {};' in app_js and 'done=' in app_js and 'partial=' in app_js and 'todo=' in app_js and 'featureCompletionPercent=' in app_js and 'strictCompletionPercent=' in app_js and 'providerCount=' in app_js and 'researchCount=' in app_js and 'gaps=${firstAuditGap.gaps || "(none)"}' in app_js,
                "jsLogoutClearsAuditSummary": 'state.auditSummary = null;' in app_js and 'state.auditItems = [];' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
