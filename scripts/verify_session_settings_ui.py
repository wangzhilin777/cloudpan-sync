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
    html_has_session_panel = "settingsSessionTitle" in html and "settingsSessionList" in html
    js_render_settings_uses_session_summary = (
        'const sessionRows = [' in app_js
        and 'summary.auth_profiles' in app_js
        and 'summary.tasks' in app_js
    )
    js_session_has_first_gap_actions = (
        'const firstSessionGap = !state.loggedIn' in app_js
        and 'session_gap=missing_auth_profiles' in app_js
        and 'session_gap=missing_tasks' in app_js
        and 'openAuthBtn.textContent = "Open Auth Profiles"' in app_js
        and 'openNewTaskBtn.textContent = "Open New Task"' in app_js
        and 'openQueueBtn.textContent = "Open Queue"' in app_js
        and 'state.activeTab = "nav.auth";' in app_js
        and 'state.activeTab = "nav.new_task";' in app_js
        and 'state.activeTab = "nav.queue";' in app_js
    )
    session_settings_ui_flow_is_wired = (
        html_has_session_panel
        and js_render_settings_uses_session_summary
        and js_session_has_first_gap_actions
    )
    print(
        json.dumps(
            {
                "htmlHasSessionPanel": html_has_session_panel,
                "jsRenderSettingsUsesSessionSummary": js_render_settings_uses_session_summary,
                "jsSessionHasFirstGapActions": js_session_has_first_gap_actions,
                "sessionSettingsUiFlowIsWired": session_settings_ui_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
