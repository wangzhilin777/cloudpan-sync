from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import webapp


def main() -> None:
    app = webapp.create_app()
    client = TestClient(app)
    index_html = client.get("/").text
    app_js = client.get("/assets/app.js").text

    result = {
        "htmlHasThresholdInput": 'id="taskThresholdMB"' in index_html,
        "htmlHasConflictPolicySelector": 'id="taskConflictPolicy"' in index_html,
        "htmlHasConflictPolicyAutoRenameOption": '<option value="auto_rename_new">auto_rename_new</option>' in index_html,
        "htmlHasConflictPolicyOverwriteOption": '<option value="overwrite_existing">overwrite_existing</option>' in index_html,
        "htmlHasPreviewButton": 'id="taskPreviewBtn"' in index_html,
        "htmlHasPreviewPanel": 'id="taskPlanPreviewPanel"' in index_html,
        "htmlHasPreviewActions": 'id="taskPlanPreviewActions"' in index_html,
        "htmlHasPreviewSummary": 'id="taskPlanPreviewSummary"' in index_html,
        "htmlHasPreviewRisk": 'id="taskPlanPreviewRisk"' in index_html,
        "htmlHasCreateGuard": 'id="taskCreateGuard"' in index_html,
        "htmlHasPreviewAck": 'id="taskPlanPreviewAck"' in index_html and 'id="taskPlanPreviewAckWrap"' in index_html,
        "jsHasPreviewFunction": "async function previewTaskPlan()" in app_js,
        "jsHasPreviewRenderer": "function renderTaskPlanPreview()" in app_js,
        "jsHasFetchPlanHelper": "async function fetchTaskPlanPreview()" in app_js,
        "jsHasAckReset": "function resetTaskPlanAck()" in app_js,
        "jsHasPreviewRecoveryActions": 'const actionsWrap = document.getElementById("taskPlanPreviewActions");' in app_js
        and 'focusBtn.textContent = "Focus Profile"' in app_js
        and 'refreshBtn.textContent = "Refresh Evidence"' in app_js
        and 'probeBtn.textContent = "Run Live Probe"' in app_js
        and 'captureBtn.textContent = "Open Capture"' in app_js
        and 'createBtn.textContent = "Create Stub"' in app_js
        and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(targetProfile.profileId));' in app_js
        and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(targetProfile.profileId));' in app_js
        and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(targetProfile.profileId));' in app_js
        and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(targetProviderKey));' in app_js
        and 'createBtn.addEventListener("click", () => createRemediationProfile(targetProviderKey));' in app_js,
        "jsReadsThresholdAndConflictPolicyFromForm": 'const thresholdRaw = document.getElementById("taskThresholdMB").value.trim();' in app_js
        and 'const conflictPolicy = document.getElementById("taskConflictPolicy").value;' in app_js,
        "jsSendsThresholdAndConflictPolicyInPreview": 'thresholdMB: Number(thresholdRaw || 0) || 0,' in app_js
        and "conflictPolicy," in app_js,
        "jsPreviewMetaShowsThresholdAndConflictPolicy": 'thresholdMB=${plan.thresholdMB || 0}, conflictPolicy=${plan.conflictPolicy || "auto_rename_new"}' in app_js,
        "jsCreateRequestPreservesThresholdAndConflictPolicy": "thresholdMB: body.thresholdMB," in app_js
        and "conflictPolicy: body.conflictPolicy," in app_js,
        "jsHasTaskActionStateHelper": "function taskActionsForState(task)" in app_js,
        "jsHasTaskStatusPillHelpers": "function appendTaskStatusPill(container, label, className = \"\")" in app_js and "function appendTaskGuardPill(container, label, className = \"\")" in app_js,
        "jsPrefersTaskSummary": "task.summary || {}" in app_js and "summary.state || task.state" in app_js and "summary.lastActionError || task.lastActionError" in app_js,
        "jsBindsPreviewButton": 'document.getElementById("taskPreviewBtn").addEventListener("click", previewTaskPlan);' in app_js,
        "jsBindsTargetProviderChange": 'document.getElementById("taskTargetProvider").addEventListener("change", onTaskTargetProviderChange);' in app_js,
        "jsFiltersProfilesByTargetProvider": 'profile.providerKey === targetProvider' in app_js,
        "jsHasRiskLines": 'pending_manual=' in app_js and 'download_upload=' in app_js and 'conflict unsupported:' in app_js,
        "jsHasTargetProfileReadiness": 'targetProfile not ready:' in app_js and 'targetProfile not write-ready:' in app_js and 'profileReady=' in app_js and 'writeReady=' in app_js,
        "jsBlocksCreateOnWriteReady": 'Task creation blocked: target profile' in app_js and 'targetProfile.writeReady === false' in app_js,
        "jsBlocksCreateOnConflictUnsupported": 'Task creation blocked:' in app_js and 'item.conflictSupportStatus === "unsupported"' in app_js,
        "jsRequiresAckForSoftRisk": 'Task creation requires confirmation:' in app_js and 'taskPlanPreviewAck' in app_js and 'counts.pending_manual' in app_js and 'counts.download_upload' in app_js,
        "jsUsesSummaryAllowedActions": "task?.summary?.allowedActions" in app_js and 'return ["retry"]' in app_js,
        "jsHasAcknowledgeRiskAction": 'task?.summary?.allowedActions' in app_js,
        "jsHasGuardPillSummary": 'guard=hard_blocked' in app_js and 'warnings=' in app_js and 'downloadUpload:' in app_js,
        "jsHasLastActionErrorDisplay": 'lastActionError=' in app_js and 'task-action-error' in app_js and 'lastActionError.reason' in app_js,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
