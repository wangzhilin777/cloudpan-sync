from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    start = app_js.find('async function createRemediationProfile(providerKey) {')
    end = app_js.find("\n}\n\nasync function refreshRealEvidenceRemediationProfile", start)
    segment = app_js[start:end] if start >= 0 and end > start else ""
    js_has_create_remediation_function = start >= 0 and end > start
    js_create_refreshes_auth_panels = (
        "loadAuthProfiles()," in segment
        and "loadRealEvidenceRemediationSummary()," in segment
        and "loadAuthEvidenceBundleSummary()," in segment
        and "loadAuthRemediationSummary()," in segment
        and "loadLiveValidations()," in segment
    )
    js_create_refreshes_strict_evidence_views = (
        "loadRealEvidenceSummary()," in segment
        and "loadTaskRuntimeEvidence()," in segment
        and "loadAuditSummary()," in segment
    )
    js_create_still_refreshes_status_matrix = "loadStatusMatrix()," in segment
    real_evidence_remediation_create_refreshes_views_flow_is_wired = (
        js_has_create_remediation_function
        and js_create_refreshes_auth_panels
        and js_create_refreshes_strict_evidence_views
        and js_create_still_refreshes_status_matrix
    )
    print(
        json.dumps(
            {
                "jsHasCreateRemediationFunction": js_has_create_remediation_function,
                "jsCreateRefreshesAuthPanels": js_create_refreshes_auth_panels,
                "jsCreateRefreshesStrictEvidenceViews": js_create_refreshes_strict_evidence_views,
                "jsCreateStillRefreshesStatusMatrix": js_create_still_refreshes_status_matrix,
                "realEvidenceRemediationCreateRefreshesViewsFlowIsWired": real_evidence_remediation_create_refreshes_views_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
