from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    start = app_js.find('async function recreateRuntimeOrphanProfile(providerKey, orphanProfileId) {')
    end = app_js.find("\n}\n\nasync function loadLiveValidations()", start)
    segment = app_js[start:end] if start >= 0 and end > start else ""
    print(
        json.dumps(
            {
                "jsHasRecreateRuntimeOrphanFunction": start >= 0 and end > start,
                "jsRecreateRefreshesAuthPanels": "loadAuthProfiles()," in segment
                and "loadRuntimeOrphanRecoverySummary()," in segment
                and "loadAuthEvidenceBundleSummary()," in segment
                and "loadAuthRemediationSummary()," in segment
                and "loadLiveValidations()," in segment,
                "jsRecreateRefreshesStrictEvidenceViews": "loadRealEvidenceSummary()," in segment
                and "loadRealEvidenceRemediationSummary()," in segment
                and "loadTaskRuntimeEvidence()," in segment
                and "loadAuditSummary()," in segment,
                "jsRecreateStillRefreshesStatusMatrix": "loadStatusMatrix()," in segment,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
