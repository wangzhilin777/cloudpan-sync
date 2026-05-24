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
                "htmlHasTaskRuntimeEvidencePanel": 'settingsTaskRuntimeEvidenceTitle' in html and 'settingsTaskRuntimeEvidenceList' in html,
                "jsHasTaskRuntimeEvidenceState": 'taskRuntimeEvidence: []' in app_js and 'taskRuntimeEvidenceMeta: { historyCount: 0, summary: null }' in app_js,
                "jsHasTaskRuntimeEvidenceLoader": 'async function loadTaskRuntimeEvidence()' in app_js and 'fetchJson("/api/task_runtime_evidence")' in app_js,
                "jsRefreshProtectedDataLoadsTaskRuntimeEvidence": 'loadTaskRuntimeEvidence(),' in app_js,
                "jsRenderSettingsUsesTaskRuntimeEvidence": 'const runtimeEvidenceSummary = state.taskRuntimeEvidenceMeta?.summary || {};' in app_js and 'latestSamples=' in app_js and 'successProviders=' in app_js and 'failedProviders=' in app_js and 'blockedProviders=' in app_js and 'success=' in app_js and 'failed=' in app_js and 'blocked=' in app_js and 'conflictHandledProviders=' in app_js and 'conflictHandled=' in app_js and 'verifyOk=${Boolean(item.verifyOk)}' in app_js and 'success=${Boolean(item.success)}' in app_js and 'executionMode=${item.executionMode || \"\"}' in app_js and 'requiredAuth=${(item.requiredAuth || []).join(\"/\") || \"(none)\"}' in app_js and 'error=${item.error || \"(none)\"}' in app_js,
                "jsLogoutClearsTaskRuntimeEvidence": 'state.taskRuntimeEvidence = [];' in app_js and 'state.taskRuntimeEvidenceMeta = { historyCount: 0, summary: null };' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
