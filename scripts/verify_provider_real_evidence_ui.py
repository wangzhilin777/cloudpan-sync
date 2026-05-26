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
                "jsProviderPanelUsesRealEvidence": 'real_evidence auth=' in app_js and 'real_evidence_gaps=' in app_js and 'task_runtime=${Boolean(realEvidence.taskRuntimeEvidence?.ok)}(${realEvidence.taskRuntimeEvidence?.successCount || 0}/${realEvidence.taskRuntimeEvidence?.failedCount || 0}, candidate=${realEvidence.taskRuntimeEvidence?.candidateCount || 0}, probe=${realEvidence.taskRuntimeEvidence?.probeCount || 0}, blocked=${realEvidence.taskRuntimeEvidence?.blockedCount || 0}, conflict=${realEvidence.taskRuntimeEvidence?.conflictHandledCount || 0}, orphan=${realEvidence.taskRuntimeEvidence?.orphanProfileCount || 0})' in app_js,
                "jsProviderPanelHasRecoveryActions": 'function appendProviderRecoveryActions(actions, providerKey)' in app_js
                and 'function appendRuntimeOrphanRecreateButtons(actions, orphanItems, buttonPrefix = "Recreate Orphan Stub")' in app_js
                and 'const orphanItems = (remediationItem?.runtimeOrphanProfiles || []).map((runtimeOrphanProfileId) => ({' in app_js
                and 'const existingLabels = {' in app_js
                and 'focusBtn.textContent = existingLabels.focus;' in app_js
                and 'evidenceBtn.textContent = existingLabels.refresh;' in app_js
                and 'probeBtn.textContent = existingLabels.probe;' in app_js
                and 'captureBtn.textContent = matchedProfile ? "Open Capture For Existing Profile" : "Open Capture";' in app_js
                and 'createBtn.textContent = "Create Stub"' in app_js
                and 'recreateBtn.textContent =' in app_js
                and 'appendRuntimeOrphanRecreateButtons(actions, orphanItems, "Recreate Orphan Stub");' in app_js,
                "jsProviderPanelBindsRecoveryActions": 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(matchedProfile.profileId));' in app_js
                and 'evidenceBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(providerKey));' in app_js
                and 'createBtn.addEventListener("click", () => createRemediationProfile(providerKey));' in app_js
                and 'recreateBtn.addEventListener("click", () =>' in app_js
                and 'recreateRuntimeOrphanProfile(item.providerKey, currentOrphanProfileId)' in app_js
                and 'appendProviderRecoveryActions(actions, item.providerKey)' in app_js,
                "jsProviderPanelHasFirstGapActions": 'const firstProviderPanelGap =' in app_js
                and 'fully_verified=${Boolean(realEvidence?.fullyVerified)}' in app_js
                and 'runtime_orphan_profiles=${((realEvidence?.taskRuntimeEvidence || {}).orphanProfileCount || 0)}' in app_js
                and 'gaps=${(realEvidence?.gaps || []).join(" | ") || "(none)"}' in app_js
                and 'appendProviderRecoveryActions(actions, firstProviderPanelGap.providerKey)' in app_js,
                "jsProviderPanelSummaryHasOrphanRecovery": 'const firstProviderPanelOrphanItem = (state.runtimeOrphanRecovery?.items || [])[0] || null;' in app_js
                and 'runtime_orphan_recovery: providers=${state.statusMatrix.summary.taskRuntimeOrphanProviderCount || 0}, profiles=${state.statusMatrix.summary.taskRuntimeOrphanProfileCount || 0}, firstProvider=${firstProviderPanelOrphanItem?.providerKey || "(none)"}, firstProfile=${firstProviderPanelOrphanItem?.orphanProfileId || "(none)"}' in app_js
                and 'openOrphanBtn.textContent = "Open Runtime Orphan Recovery";' in app_js
                and 'appendRuntimeOrphanRecreateButtons(actions, state.runtimeOrphanRecovery?.items || [], "Recreate Orphan Stub");' in app_js,
                "jsProviderPanelShowsRuntimeTrack": 'task_runtime_track=${item.task_runtime_track || "runtime_planned"}, blocked=${item.task_runtime_blocked || 0}, conflictHandled=${item.task_runtime_conflict_handled || 0}' in app_js,
                "jsProviderPanelSummaryShowsConflictCounts": 'label: "autoRenameProbeOnly"' in app_js and 'label: "conflictUnsupported"' in app_js and 'label: "runtimeBlocked"' in app_js and 'label: "runtimeConflictHandled"' in app_js and 'label: "runtimeOrphan"' in app_js,
                "jsLoadRealEvidenceTriggersProviderRender": 'state.realEvidenceReport = data;' in app_js and 'renderProviderPanel();' in app_js,
                "jsLogoutClearsRealEvidenceReport": 'state.realEvidenceReport = null;' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
