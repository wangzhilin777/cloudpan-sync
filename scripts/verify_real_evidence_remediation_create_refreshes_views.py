from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    start = app_js.find('async function createRemediationProfile(providerKey) {')
    end = app_js.find("\n}\n\nasync function refreshRealEvidenceRemediationProfile", start)
    segment = app_js[start:end] if start >= 0 and end > start else ""
    print(
        json.dumps(
            {
                "jsHasCreateRemediationFunction": start >= 0 and end > start,
                "jsCreateRefreshesAuthPanels": "loadAuthProfiles()," in segment
                and "loadRealEvidenceRemediationSummary()," in segment
                and "loadAuthEvidenceBundleSummary()," in segment
                and "loadAuthRemediationSummary()," in segment
                and "loadLiveValidations()," in segment,
                "jsCreateRefreshesStrictEvidenceViews": "loadRealEvidenceSummary()," in segment
                and "loadTaskRuntimeEvidence()," in segment
                and "loadAuditSummary()," in segment,
                "jsCreateStillRefreshesStatusMatrix": "loadStatusMatrix()," in segment,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
