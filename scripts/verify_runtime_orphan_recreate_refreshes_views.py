from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    start = app_js.find('async function recreateRuntimeOrphanProfile(providerKey, orphanProfileId) {')
    end = app_js.find("\n}\n\nasync function loadLiveValidations()", start)
    segment = app_js[start:end] if start >= 0 and end > start else ""
    batch_start = app_js.find('async function batchRecreateRuntimeOrphanProfiles(providerKey = "", overwriteExisting = false) {')
    batch_end = app_js.find("\n}\n\nasync function loadLiveValidations()", batch_start)
    batch_segment = app_js[batch_start:batch_end] if batch_start >= 0 and batch_end > batch_start else ""
    js_has_recreate_runtime_orphan_function = start >= 0 and end > start
    js_recreate_refreshes_auth_panels = (
        "loadAuthProfiles()," in segment
        and "loadRuntimeOrphanRecoverySummary()," in segment
        and "loadAuthEvidenceBundleSummary()," in segment
        and "loadAuthRemediationSummary()," in segment
        and "loadLiveValidations()," in segment
    )
    js_recreate_refreshes_strict_evidence_views = (
        "loadRealEvidenceSummary()," in segment
        and "loadRealEvidenceRemediationSummary()," in segment
        and "loadTaskRuntimeEvidence()," in segment
        and "loadAuditSummary()," in segment
    )
    js_recreate_still_refreshes_status_matrix = "loadStatusMatrix()," in segment
    js_has_batch_recreate_runtime_orphan_function = batch_start >= 0 and batch_end > batch_start
    js_batch_recreate_refreshes_same_views = (
        "loadAuthProfiles()," in batch_segment
        and "loadRuntimeOrphanRecoverySummary()," in batch_segment
        and "loadAuthEvidenceBundleSummary()," in batch_segment
        and "loadAuthRemediationSummary()," in batch_segment
        and "loadLiveValidations()," in batch_segment
        and "loadRealEvidenceSummary()," in batch_segment
        and "loadRealEvidenceRemediationSummary()," in batch_segment
        and "loadTaskRuntimeEvidence()," in batch_segment
        and "loadStatusMatrix()," in batch_segment
        and "loadAuditSummary()," in batch_segment
    )
    runtime_orphan_recreate_refreshes_views_flow_is_wired = (
        js_has_recreate_runtime_orphan_function
        and js_recreate_refreshes_auth_panels
        and js_recreate_refreshes_strict_evidence_views
        and js_recreate_still_refreshes_status_matrix
        and js_has_batch_recreate_runtime_orphan_function
        and js_batch_recreate_refreshes_same_views
    )
    print(
        json.dumps(
            {
                "jsHasRecreateRuntimeOrphanFunction": js_has_recreate_runtime_orphan_function,
                "jsRecreateRefreshesAuthPanels": js_recreate_refreshes_auth_panels,
                "jsRecreateRefreshesStrictEvidenceViews": js_recreate_refreshes_strict_evidence_views,
                "jsRecreateStillRefreshesStatusMatrix": js_recreate_still_refreshes_status_matrix,
                "jsHasBatchRecreateRuntimeOrphanFunction": js_has_batch_recreate_runtime_orphan_function,
                "jsBatchRecreateRefreshesSameViews": js_batch_recreate_refreshes_same_views,
                "runtimeOrphanRecreateRefreshesViewsFlowIsWired": runtime_orphan_recreate_refreshes_views_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
