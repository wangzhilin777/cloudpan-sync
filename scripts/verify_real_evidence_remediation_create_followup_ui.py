from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    js_create_remediation_uses_summary_panel = 'setAuthValidationSummary(data, "Remediation Stub");' in app_js
    js_create_remediation_stores_latest_action = "state.lastRemediationAction = data;" in app_js
    js_create_remediation_only_auto_jumps_when_stub_created = 'if (data?.created === true && createdProfile) {' in app_js
    js_latest_remediation_action_stays_in_settings = (
        "latestRemediationAction=" in app_js
        and 'const latestIsExisting = lastRemediationAction.created === false && lastRemediationAction.status === "already_exists";' in app_js
        and 'focus: latestIsExisting ? "Focus Existing Profile" : "Focus Latest Created Stub"' in app_js
        and 'refresh: latestIsExisting ? "Refresh Existing Profile" : "Refresh Latest Created Stub"' in app_js
        and 'probe: latestIsExisting ? "Probe Existing Profile" : "Probe Latest Created Stub"' in app_js
        and 'capture: latestIsExisting ? "Open Capture For Existing Profile" : "Open Capture For Latest Created Stub"' in app_js
    )
    js_create_followup_uses_accurate_labels = (
        'focus: followupIsExisting ? "Focus Existing Profile" : "Focus Created Stub"' in app_js
        and 'refresh: followupIsExisting ? "Refresh Existing Profile" : "Refresh Created Stub"' in app_js
        and 'probe: followupIsExisting ? "Probe Existing Profile" : "Probe Created Stub"' in app_js
        and 'capture: followupIsExisting ? "Open Capture For Existing Profile" : "Open Capture For Created Stub"' in app_js
    )
    js_summary_followup_detects_bootstrap_chain = (
        "data?.recommendedBootstrapCommand" in app_js
        and "data?.recommendedPostBootstrapRuntimeCommand" in app_js
    )
    js_summary_followup_reuses_direct_actions = (
        "focusBtn.textContent = followupLabels.focus;" in app_js
        and "refreshBtn.textContent = followupLabels.refresh;" in app_js
        and "probeBtn.textContent = followupLabels.probe;" in app_js
        and "captureBtn.textContent = followupLabels.capture;" in app_js
    )
    real_evidence_remediation_create_followup_ui_flow_is_wired = (
        js_create_remediation_uses_summary_panel
        and js_create_remediation_stores_latest_action
        and js_create_remediation_only_auto_jumps_when_stub_created
        and js_latest_remediation_action_stays_in_settings
        and js_create_followup_uses_accurate_labels
        and js_summary_followup_detects_bootstrap_chain
        and js_summary_followup_reuses_direct_actions
    )
    print(
        json.dumps(
            {
                "jsCreateRemediationUsesSummaryPanel": js_create_remediation_uses_summary_panel,
                "jsCreateRemediationStoresLatestAction": js_create_remediation_stores_latest_action,
                "jsCreateRemediationOnlyAutoJumpsWhenStubCreated": js_create_remediation_only_auto_jumps_when_stub_created,
                "jsLatestRemediationActionStaysInSettings": js_latest_remediation_action_stays_in_settings,
                "jsCreateFollowupUsesAccurateLabels": js_create_followup_uses_accurate_labels,
                "jsSummaryFollowupDetectsBootstrapChain": js_summary_followup_detects_bootstrap_chain,
                "jsSummaryFollowupReusesDirectActions": js_summary_followup_reuses_direct_actions,
                "realEvidenceRemediationCreateFollowupUiFlowIsWired": real_evidence_remediation_create_followup_ui_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
