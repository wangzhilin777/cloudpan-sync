from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> None:
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    print(
        json.dumps(
            {
                "jsHasRealEvidenceReportState": 'realEvidenceReport: null' in app_js,
                "jsHasRealEvidenceByProviderHelper": 'function realEvidenceByProvider(providerKey)' in app_js,
                "jsProviderPanelUsesRealEvidence": 'real_evidence auth=' in app_js and 'real_evidence_gaps=' in app_js and 'task_runtime=${Boolean(realEvidence.taskRuntimeEvidence?.ok)}(${realEvidence.taskRuntimeEvidence?.successCount || 0}/${realEvidence.taskRuntimeEvidence?.failedCount || 0})' in app_js,
                "jsProviderPanelShowsRuntimeTrack": 'task_runtime_track=${item.task_runtime_track || "runtime_planned"}, conflictHandled=${item.task_runtime_conflict_handled || 0}' in app_js,
                "jsProviderPanelSummaryShowsConflictCounts": 'label: "autoRenameProbeOnly"' in app_js and 'label: "conflictUnsupported"' in app_js and 'label: "runtimeConflictHandled"' in app_js,
                "jsLoadRealEvidenceTriggersProviderRender": 'state.realEvidenceReport = data;' in app_js and 'renderProviderPanel();' in app_js,
                "jsLogoutClearsRealEvidenceReport": 'state.realEvidenceReport = null;' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
