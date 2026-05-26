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
    html_has_provider_status_panel = 'settingsProviderStatusTitle' in html and 'settingsProviderStatusList' in html
    js_load_status_matrix_refreshes_settings = 'renderProviderPanel();' in app_js and 'renderSettingsPanel();' in app_js
    js_provider_status_has_first_gap_actions = 'const firstProviderStatusGap =' in app_js \
        and 'const firstProviderStatusOrphanItem = (state.runtimeOrphanRecovery?.items || [])[0] || null;' in app_js \
        and 'runtime_orphan_recovery: providers=${providerStatusSummary.taskRuntimeOrphanProviderCount || 0}' in app_js \
        and 'openOrphanBtn.textContent = "Open Runtime Orphan Recovery";' in app_js \
        and 'appendRuntimeOrphanRecreateButtons(actions, state.runtimeOrphanRecovery?.items || [], "Recreate Orphan Stub");' in app_js \
        and 'const firstProviderStatusRealEvidence = realEvidenceByProvider(firstProviderStatusGap.providerKey);' in app_js \
        and 'appendProviderRecoveryActions(actions, firstProviderStatusGap.providerKey);' in app_js \
        and 'runtime_track=${firstProviderStatusGap.task_runtime_track || "runtime_planned"}' in app_js \
        and 'blocked=${firstProviderStatusGap.task_runtime_blocked || 0}' in app_js \
        and 'runtime_orphan_profiles=${((firstProviderStatusRealEvidence?.taskRuntimeEvidence || {}).orphanProfileCount || 0)}' in app_js
    js_render_settings_uses_provider_status_summary = 'const providerStatusSummary = state.statusMatrix?.summary || {};' in app_js \
        and 'liveProbeOk=' in app_js \
        and 'conflictAware=' in app_js \
        and 'overwriteReady=' in app_js \
        and 'autoRenameReady=' in app_js \
        and 'overwriteDowngrade=' in app_js \
        and 'overwriteSupported=' in app_js \
        and 'autoRenameSupported=' in app_js \
        and 'autoRenameProbeOnly=' in app_js \
        and 'conflictUnsupported=' in app_js \
        and 'runtimeEvidenceProviders=' in app_js \
        and 'runtimeFailedProviders=' in app_js \
        and 'runtimeCandidateProviders=' in app_js \
        and 'taskRuntimeCandidateEvidenceProviderCount' in app_js \
        and 'runtimeProbeProviders=' in app_js \
        and 'taskRuntimeProbeEvidenceProviderCount' in app_js \
        and 'runtimeSuccess=' in app_js \
        and 'runtimeFailed=' in app_js \
        and 'runtimeCandidate=' in app_js \
        and 'taskRuntimeCandidateEvidenceCount' in app_js \
        and 'runtimeProbe=' in app_js \
        and 'taskRuntimeProbeEvidenceCount' in app_js \
        and 'runtimeBlockedProviders=' in app_js \
        and 'runtimeBlocked=' in app_js \
        and 'runtimeConflictHandledProviders=' in app_js \
        and 'runtimeConflictHandled=' in app_js \
        and 'runtimeOrphanProviders=' in app_js \
        and 'taskRuntimeOrphanProviderCount' in app_js \
        and 'runtimeOrphanProfiles=' in app_js \
        and 'taskRuntimeOrphanProfileCount' in app_js \
        and 'runtimeActive=' in app_js \
        and 'runtimeCandidate=' in app_js \
        and 'runtimeTrackBlocked=' in app_js \
        and 'authReadyProviders=' in app_js \
        and 'createDirProviders=' in app_js \
        and 'fastCheckProviders=' in app_js \
        and 'liveProbeOkProviders=' in app_js \
        and 'overwriteDowngradeProviders=' in app_js \
        and 'overwriteSupportedProviders=' in app_js \
        and 'autoRenameSupportedProviders=' in app_js \
        and 'autoRenameProbeOnlyProviders=' in app_js \
        and 'conflictUnsupportedProviders=' in app_js \
        and 'runtimeSuccessProviders=' in app_js \
        and 'runtimeFailedProvidersList=' in app_js \
        and 'runtimeCandidateProvidersList=' in app_js \
        and 'runtimeProbeProvidersList=' in app_js \
        and 'runtimeBlockedProvidersList=' in app_js \
        and 'runtimeConflictHandledProvidersList=' in app_js \
        and 'runtimeOrphanProvidersList=' in app_js \
        and 'runtimeOrphanProfilesList=' in app_js
    js_sets_provider_status_title = 'document.getElementById("settingsProviderStatusTitle").textContent = "Provider Status Matrix";' in app_js
    js_logout_clears_status_matrix = 'state.statusMatrix = null;' in app_js
    provider_status_settings_ui_flow_is_wired = (
        html_has_provider_status_panel
        and js_load_status_matrix_refreshes_settings
        and js_provider_status_has_first_gap_actions
        and js_render_settings_uses_provider_status_summary
        and js_sets_provider_status_title
        and js_logout_clears_status_matrix
    )
    print(
        json.dumps(
            {
                "htmlHasProviderStatusPanel": html_has_provider_status_panel,
                "jsLoadStatusMatrixRefreshesSettings": js_load_status_matrix_refreshes_settings,
                "jsProviderStatusHasFirstGapActions": js_provider_status_has_first_gap_actions,
                "jsRenderSettingsUsesProviderStatusSummary": js_render_settings_uses_provider_status_summary,
                "jsSetsProviderStatusTitle": js_sets_provider_status_title,
                "jsLogoutClearsStatusMatrix": js_logout_clears_status_matrix,
                "providerStatusSettingsUiFlowIsWired": provider_status_settings_ui_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
