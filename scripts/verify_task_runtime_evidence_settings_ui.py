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
                "jsHasTaskRuntimeEvidenceActions": 'const findRuntimeEvidenceProfile = (item) =>' in app_js
                and 'const runtimeOrphanRows = (state.taskRuntimeEvidence || []).filter((item) => {' in app_js
                and 'runtimeOrphanProviders=${runtimeOrphanProviders.length || 0}' in app_js
                and 'runtimeOrphanProfiles=${runtimeOrphanProfiles.length || 0}' in app_js
                and 'runtimeOrphanProviderList=${runtimeOrphanProviders.join("/") || "(none)"}' in app_js
                and 'runtimeOrphanProfileList=${runtimeOrphanProfiles.join("/") || "(none)"}' in app_js
                and 'const existingLabels = {' in app_js
                and 'const orphanRuntimeProfileId = !matchedProfile ? String(item.profileId || "").trim() : "";' in app_js
                and 'focusBtn.textContent = existingLabels.focus;' in app_js
                and 'refreshBtn.textContent = existingLabels.refresh;' in app_js
                and 'probeBtn.textContent = existingLabels.probe;' in app_js
                and 'captureBtn.textContent = matchedProfile ? "Open Capture For Existing Profile" : "Open Capture";' in app_js
                and 'recreateBtn.textContent = "Recreate Orphan Stub"' in app_js
                and 'profileId=${item.profileId || "(none)"}' in app_js
                and 'orphanProfileId=${orphanRuntimeProfileId || "(none)"}' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(matchedProfile.profileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey || matchedProfile?.providerKey || ""));' in app_js
                and 'recreateBtn.addEventListener("click", () => recreateRuntimeOrphanProfile(item.providerKey || "", orphanRuntimeProfileId));' in app_js,
                "jsHasTaskRuntimeFirstGapActions": 'const firstRuntimeEvidenceGap =' in app_js
                and 'const firstRuntimeOrphanProfileId = !hasExistingProfile ? String(firstRuntimeEvidenceGap.profileId || "").trim() : "";' in app_js
                and 'const firstRuntimeLabels = {' in app_js
                and 'focusBtn.textContent = firstRuntimeLabels.focus;' in app_js
                and 'refreshBtn.textContent = firstRuntimeLabels.refresh;' in app_js
                and 'probeBtn.textContent = firstRuntimeLabels.probe;' in app_js
                and 'captureBtn.textContent = firstRuntimeLabels.capture;' in app_js
                and 'createBtn.textContent = "Create Stub First Runtime"' in app_js
                and 'recreateBtn.textContent = "Recreate Orphan Stub First Runtime"' in app_js
                and 'profileId=${firstRuntimeEvidenceGap.profileId || "(none)"}' in app_js
                and 'orphanProfileId=${firstRuntimeOrphanProfileId || "(none)"}' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(matchedProfile.profileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                and 'probeBtn.addEventListener("click", () => probeRealEvidenceRemediationProfile(matchedProfile.profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstRuntimeEvidenceGap.providerKey || matchedProfile?.providerKey || ""));' in app_js
                and 'createBtn.addEventListener("click", () => createRemediationProfile(firstRuntimeEvidenceGap.providerKey || ""));' in app_js
                and 'recreateBtn.addEventListener("click", () => recreateRuntimeOrphanProfile(firstRuntimeEvidenceGap.providerKey || "", firstRuntimeOrphanProfileId));' in app_js,
                "jsHasTaskRuntimeSummaryOrphanRecovery": 'const firstRuntimeOrphanItem = runtimeOrphanRows[0] || null;' in app_js
                and 'runtime_orphan_recovery: providers=${runtimeOrphanProviders.length || 0}, profiles=${runtimeOrphanProfiles.length || 0}, firstProvider=${firstRuntimeOrphanItem?.providerKey || "(none)"}, firstProfile=${firstRuntimeOrphanItem?.profileId || "(none)"}' in app_js
                and 'openOrphanBtn.textContent = "Open Runtime Orphan Recovery";' in app_js
                and 'appendRuntimeOrphanRecreateButtons(actions, runtimeOrphanRows, "Recreate Runtime Orphan Stub");' in app_js,
                "jsRenderSettingsUsesTaskRuntimeEvidence": 'const runtimeEvidenceSummary = state.taskRuntimeEvidenceMeta?.summary || {};' in app_js and 'latestSamples=' in app_js and 'successProviders=' in app_js and 'failedProviders=' in app_js and 'candidateProviders=' in app_js and 'probeProviders=' in app_js and 'blockedProviders=' in app_js and 'success=' in app_js and 'failed=' in app_js and 'candidate=' in app_js and 'probe=' in app_js and 'blocked=' in app_js and 'conflictHandledProviders=' in app_js and 'conflictHandled=' in app_js and 'runtimeOrphanProviders=' in app_js and 'runtimeOrphanProfiles=' in app_js and 'runtimeOrphanProviderList=' in app_js and 'runtimeOrphanProfileList=' in app_js and 'successProfiles=' in app_js and 'failedProfiles=' in app_js and 'candidateProfiles=' in app_js and 'probeProfiles=' in app_js and 'blockedProfiles=' in app_js and 'conflictHandledProfiles=' in app_js and 'path=${item.path || \"(unknown)\"}' in app_js and 'profileId=${item.profileId || \"(none)\"}' in app_js and 'orphanProfileId=${orphanRuntimeProfileId || \"(none)\"}' in app_js and 'verifyOk=${Boolean(item.verifyOk)}' in app_js and 'verifyMode=${item.verifyMode || \"(none)\"}' in app_js and 'success=${Boolean(item.success)}' in app_js and 'candidateOnly=${Boolean(item.candidateOnly)}' in app_js and 'probeOnly=${Boolean(item.probeOnly)}' in app_js and 'executionMode=${item.executionMode || \"\"}' in app_js and 'resolvedTargetName=${item.resolvedTargetName || \"(none)\"}' in app_js and 'riskHint=${item.riskHint || \"(none)\"}' in app_js and 'requiredAuth=${(item.requiredAuth || []).join(\"/\") || \"(none)\"}' in app_js and 'error=${item.error || \"(none)\"}' in app_js,
                "jsLogoutClearsTaskRuntimeEvidence": 'state.taskRuntimeEvidence = [];' in app_js and 'state.taskRuntimeEvidenceMeta = { historyCount: 0, summary: null };' in app_js,
                "settingsTaskRuntimeEvidenceFlowIsWired": (
                    'settingsTaskRuntimeEvidenceTitle' in html
                    and 'settingsTaskRuntimeEvidenceList' in html
                    and 'taskRuntimeEvidence: []' in app_js
                    and 'taskRuntimeEvidenceMeta: { historyCount: 0, summary: null }' in app_js
                    and 'async function loadTaskRuntimeEvidence()' in app_js
                    and 'fetchJson("/api/task_runtime_evidence")' in app_js
                    and 'loadTaskRuntimeEvidence(),' in app_js
                    and 'const runtimeEvidenceSummary = state.taskRuntimeEvidenceMeta?.summary || {};' in app_js
                    and 'runtime_orphan_recovery: providers=${runtimeOrphanProviders.length || 0}, profiles=${runtimeOrphanProfiles.length || 0}, firstProvider=${firstRuntimeOrphanItem?.providerKey || "(none)"}, firstProfile=${firstRuntimeOrphanItem?.profileId || "(none)"}' in app_js
                    and 'appendRuntimeOrphanRecreateButtons(actions, runtimeOrphanRows, "Recreate Runtime Orphan Stub");' in app_js
                    and 'state.taskRuntimeEvidence = [];' in app_js
                    and 'state.taskRuntimeEvidenceMeta = { historyCount: 0, summary: null };' in app_js
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
