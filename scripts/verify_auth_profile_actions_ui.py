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
    js_auth_list_shows_patch_hint = "patch_hint=" in app_js
    js_auth_list_shows_write_blocker = "write_blocker=" in app_js
    js_auth_list_has_capture_help_condition = (
        "const needsCaptureHelp = Boolean(" in app_js
        and "item.needsSecretRefresh" in app_js
        and "item.writeReady === false" in app_js
        and "item.missingFieldHints" in app_js
    )
    js_auth_list_has_open_capture_action = (
        'capture: "Open Capture For Existing Profile"' in app_js
        and 'captureBtn.textContent = authListLabels.capture;' in app_js
        and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js
    )
    js_auth_list_keeps_evidence_action = (
        'refresh: "Refresh Existing Profile"' in app_js
        and 'evidenceBtn.textContent = authListLabels.refresh;' in app_js
        and 'evidenceBtn.addEventListener("click", () => showAuthEvidence(item));' in app_js
    )
    js_auth_list_has_existing_profile_probe_action = (
        'probe: "Probe Existing Profile"' in app_js
        and 'probeBtn.textContent = authListLabels.probe;' in app_js
        and 'probeBtn.addEventListener("click", () => probeProviderLive(item));' in app_js
    )
    auth_profile_actions_ui_flow_is_wired = (
        js_auth_list_shows_patch_hint
        and js_auth_list_shows_write_blocker
        and js_auth_list_has_capture_help_condition
        and js_auth_list_has_open_capture_action
        and js_auth_list_keeps_evidence_action
        and js_auth_list_has_existing_profile_probe_action
    )
    print(
        json.dumps(
            {
                "jsAuthListShowsPatchHint": js_auth_list_shows_patch_hint,
                "jsAuthListShowsWriteBlocker": js_auth_list_shows_write_blocker,
                "jsAuthListHasCaptureHelpCondition": js_auth_list_has_capture_help_condition,
                "jsAuthListHasOpenCaptureAction": js_auth_list_has_open_capture_action,
                "jsAuthListKeepsEvidenceAction": js_auth_list_keeps_evidence_action,
                "jsAuthListHasExistingProfileProbeAction": js_auth_list_has_existing_profile_probe_action,
                "authProfileActionsUiFlowIsWired": auth_profile_actions_ui_flow_is_wired,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
