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
    html_has_provider_research_panel = "providerResearchList" in html and "providersResearchTitle" in html
    js_render_provider_uses_research = (
        'for (const item of state.providerResearch) {' in app_js
        and 'real_evidence_gaps=' in app_js
        and 'live_probe=${probe.mode}, ok=${probe.ok}, checks=${(probe.checks || []).length}' in app_js
    )
    js_provider_research_has_first_gap_actions = (
        'const firstProviderResearchGap =' in app_js
        and 'status=${firstProviderResearchGap.status || "unknown"}' in app_js
        and 'fully_verified=${Boolean(realEvidence?.fullyVerified)}' in app_js
        and 'runtime_orphan_profiles=${((realEvidence?.taskRuntimeEvidence || {}).orphanProfileCount || 0)}' in app_js
        and 'appendProviderRecoveryActions(actions, firstProviderResearchGap.providerKey)' in app_js
    )
    js_provider_research_has_summary_orphan_recovery = (
        'const firstProviderResearchOrphanItem = (state.runtimeOrphanRecovery?.items || [])[0] || null;' in app_js
        and 'runtime_orphan_recovery: providers=${state.realEvidenceSummary?.taskRuntimeOrphanProviderCount || 0}, profiles=${state.realEvidenceSummary?.taskRuntimeOrphanProfileCount || 0}, firstProvider=${firstProviderResearchOrphanItem?.providerKey || "(none)"}, firstProfile=${firstProviderResearchOrphanItem?.orphanProfileId || "(none)"}' in app_js
        and 'openOrphanBtn.textContent = "Open Runtime Orphan Recovery";' in app_js
        and 'appendRuntimeOrphanRecreateButtons(actions, state.runtimeOrphanRecovery?.items || [], "Recreate Orphan Stub");' in app_js
    )
    provider_research_ui_flow_is_wired = (
        html_has_provider_research_panel
        and js_render_provider_uses_research
        and js_provider_research_has_first_gap_actions
        and js_provider_research_has_summary_orphan_recovery
    )
    print(
        json.dumps(
            {
                "htmlHasProviderResearchPanel": html_has_provider_research_panel,
                "jsRenderProviderUsesResearch": js_render_provider_uses_research,
                "jsProviderResearchHasFirstGapActions": js_provider_research_has_first_gap_actions,
                "jsProviderResearchHasSummaryOrphanRecovery": js_provider_research_has_summary_orphan_recovery,
                "providerResearchUiFlowIsWired": provider_research_ui_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
