from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> None:
    app_js = (SRC / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    print(
        json.dumps(
            {
                "jsRenderTaskListHasLatestResultRows": "function renderTaskList()" in app_js and ".slice(0, 3)" in app_js,
                "jsRenderTaskListPrefersLatestResults": "const resultRows = task.latestResults || task.results || [];" in app_js,
                "jsRenderTaskListShowsTargetProfileSummary": "const targetProfileText = targetProfile.displayName || task.targetProfileId || \"(none)\";" in app_js and 'const profileReadyText = Object.prototype.hasOwnProperty.call(targetProfile, "profileReady")' in app_js and 'const writeReadyText = Object.prototype.hasOwnProperty.call(targetProfile, "writeReady")' in app_js and 'targetProfile=${targetProfileText}, targetProfileId=${task.targetProfileId || "(none)"}, targetParentId=${task.targetParentId || "(none)"}, conflictPolicy=${task.conflictPolicy || "auto_rename_new"}, profileReady=${profileReadyText}, writeReady=${writeReadyText}' in app_js,
                "jsRenderTaskListShowsProbeAndCompletionSummary": 'appendTaskStatusPill(meta, `probe=${summary.probeOnlyCount || task.progress.probeOnly || 0}`);' in app_js and 'appendTaskStatusPill(meta, `candidate=${summary.candidateOnlyCount || task.progress.candidateOnly || 0}`);' in app_js and 'appendTaskStatusPill(meta, `completion=${summary.completionKind}`);' in app_js,
                "jsRenderTaskListShowsRiskReason": "summary.riskReason" in app_js and 'appendTaskGuardPill(guardRow, `risk=${summary.riskReason}`, "warning");' in app_js,
                "jsRenderTaskListShowsAwaitingAcknowledgement": "summary.awaitingAcknowledgement" in app_js and 'appendTaskGuardPill(guardRow, "awaitingAcknowledgement=true", "ack");' in app_js,
                "jsRenderTaskListShowsRiskPaused": "summary.riskPaused" in app_js and 'appendTaskGuardPill(guardRow, "riskPaused=true", "warning");' in app_js,
                "jsRenderTaskListShowsTargetProfileReadiness": 'const targetProfile = guard.targetProfile || {};' in app_js and 'appendTaskGuardPill(guardRow, "targetProfileReady=false", "warning");' in app_js and 'appendTaskGuardPill(guardRow, "targetWriteReady=false", "blocking");' in app_js,
                "jsRenderTaskListShowsTargetProfileMissingHints": 'targetProfileMissing=${(targetProfile.missingFieldHints || []).join(" | ") || "(none)"}' in app_js and 'targetWriteMissing=${(targetProfile.writeMissingFieldHints || []).join(" | ") || "(none)"}' in app_js and 'writeBlocker=${targetProfile.writeBlockerNote}' in app_js,
                "jsRenderTaskListShowsRiskHint": 'row.liveAttempt?.riskHint ? ` - ${row.liveAttempt.riskHint}` : ""' in app_js,
                "jsRenderTaskListShowsVerifyMode": 'row.liveAttempt?.verifyMode' in app_js and 'verify=${row.liveAttempt.verifyOk ? "ok" : "pending"}:${row.liveAttempt.verifyMode}' in app_js,
                "jsRenderTaskListShowsVerifyNote": 'row.liveAttempt?.verifyNote' in app_js and 'verifyNote=${row.liveAttempt.verifyNote}' in app_js,
                "jsRenderTaskListShowsConflictAction": 'row.liveAttempt?.conflictAction' in app_js and 'conflict=${row.liveAttempt.conflictAction}:${row.liveAttempt.resolvedTargetName || "(same)"}' in app_js,
                "jsRenderTaskListShowsRequiredAuth": 'row.liveAttempt?.requiredAuth?.length' in app_js and 'requiredAuth=${row.liveAttempt.requiredAuth.join("/")}' in app_js,
                "jsRenderTaskListShowsError": 'row.liveAttempt?.error' in app_js and 'error=${row.liveAttempt.error}' in app_js,
                "jsRenderTaskListShowsRowNote": 'row.note' in app_js and 'note=${row.note}' in app_js,
                "jsLoadTasksUsesListItems": 'state.tasks = data.listItems || data.items || [];' in app_js,
                "jsRenderPendingListCarriesTaskSummary": 'const taskSummary = task?.summary || {};' in app_js and 'taskState: taskSummary.state || task.state || ""' in app_js and 'taskRiskReason: taskSummary.riskReason || ""' in app_js,
                "jsRenderPendingListCarriesConflictPolicy": 'conflictPolicy: item.conflictPolicy || "auto_rename_new"' in app_js,
                "jsRenderPendingListCarriesConflictFields": 'conflictSupportStatus: item.conflictSupportStatus || ""' in app_js and 'conflictNote: item.conflictNote || ""' in app_js,
                "jsRenderPendingListShowsTaskSummary": 'state=${row.taskState || "(unknown)"}' in app_js and 'risk=${row.taskRiskReason || "(none)"}' in app_js,
                "jsRenderPendingListShowsConflictPolicy": 'conflictPolicy=${row.conflictPolicy || "auto_rename_new"}' in app_js,
                "jsRenderPendingListShowsConflictFields": 'const conflictSupportText = row.conflictSupportStatus ? `, conflictSupport=${row.conflictSupportStatus}` : "";' in app_js and 'const conflictNoteText = row.conflictNote ? `, conflictNote=${row.conflictNote}` : "";' in app_js,
                "jsRenderPendingListCarriesAvailableFastInputs": 'availableFastInputs: item.availableFastInputs || []' in app_js,
                "jsRenderPendingListShowsAvailableFastInputs": 'available=${row.availableFastInputs.join(",") || "(none)"}' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
