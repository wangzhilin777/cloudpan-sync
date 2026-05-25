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

    anonymous_session = client.get("/api/session").json()
    anonymous_audit = client.get("/api/plan/audit")
    anonymous_capture = client.post("/api/auth/capture/start", json={"providerKey": "quark"})
    anonymous_capture_parse = client.post("/api/auth/capture/parse", json={"providerKey": "quark", "rawText": "cookie: sid=1"})

    login_result = client.post("/api/login", json={"password": webapp.ADMIN_PASSWORD})
    logged_in_session = client.get("/api/session").json()
    capture_result = client.post("/api/auth/capture/start", json={"providerKey": "quark"})
    capture_parse_result = client.post(
        "/api/auth/capture/parse",
        json={"providerKey": "quark", "rawText": "cookie: sid=abc123; kps=xyz789\nhttps://pan.quark.cn/s/demo?pwdId=pwd-1"},
    )
    logout_result = client.post("/api/logout")
    logged_out_session = client.get("/api/session").json()

    capture_payload = capture_result.json() if capture_result.status_code == 200 else {}
    capture_parse_payload = capture_parse_result.json() if capture_parse_result.status_code == 200 else {}

    print(
        json.dumps(
            {
                "htmlHasLoginPanel": 'id="loginPanel"' in index_html and 'id="loginBtn"' in index_html and 'id="logoutBtn"' in index_html,
                "htmlHasTabsContainer": 'id="tabs"' in index_html,
                "htmlHasWizardPanel": 'id="wizardSteps"' in index_html and 'id="wizardSecondaryNav"' in index_html and 'id="wizardSummaryBody"' in index_html,
                "htmlHasAuthModal": (
                    'id="authModal"' in index_html
                    and 'id="authOpenModalBtn"' in index_html
                    and 'id="authStartCaptureBtn"' in index_html
                    and 'id="authOpenLoginUrlBtn"' in index_html
                    and 'id="authCaptureRawInput"' in index_html
                    and 'id="authParseCaptureBtn"' in index_html
                    and 'id="authApplyCaptureBtn"' in index_html
                ),
                "htmlHasAdvancedDetails": '<details class="advanced-block">' in index_html,
                "anonymousSessionLoggedOut": anonymous_session.get("loggedIn") is False,
                "anonymousAuditBlocked": anonymous_audit.status_code == 401 and "please_login_first" in anonymous_audit.text,
                "anonymousCaptureBlocked": anonymous_capture.status_code == 401 and "please_login_first" in anonymous_capture.text,
                "anonymousCaptureParseBlocked": anonymous_capture_parse.status_code == 401 and "please_login_first" in anonymous_capture_parse.text,
                "loginSetsSession": login_result.status_code == 200 and logged_in_session.get("loggedIn") is True,
                "captureGuideWorksAfterLogin": (
                    capture_result.status_code == 200
                    and capture_payload.get("status") == "capture_pending"
                    and capture_payload.get("providerKey") == "quark"
                    and bool(capture_payload.get("loginUrlHint"))
                    and isinstance(capture_payload.get("requiredFieldHints"), list)
                    and isinstance(capture_payload.get("manualSteps"), list)
                    and isinstance(capture_payload.get("pasteTargets"), list)
                    and isinstance(capture_payload.get("browserConsoleSnippets"), list)
                    and isinstance(capture_payload.get("networkCaptureTips"), list)
                ),
                "captureParseWorksAfterLogin": (
                    capture_parse_result.status_code == 200
                    and capture_parse_payload.get("status") == "capture_parsed"
                    and capture_parse_payload.get("suggestedProfile", {}).get("authMode") == "manual_cookie"
                    and capture_parse_payload.get("suggestedProfile", {}).get("extra", {}).get("pwdId") == "pwd-1"
                ),
                "logoutClearsSession": logout_result.status_code == 200 and logged_out_session.get("loggedIn") is False,
                "jsDeclaresTabKeys": "const tabKeys = [" in app_js and '"nav.new_task"' in app_js and '"nav.settings"' in app_js,
                "jsRendersTabsFromKeys": 'const tabs = document.getElementById("tabs");' in app_js and "for (const key of tabKeys)" in app_js and "node.textContent = t(key);" in app_js,
                "jsTogglesLoginAndAppPanels": "loginPanel.hidden = state.loggedIn;" in app_js and "appPanel.hidden = !state.loggedIn;" in app_js and "logoutBtn.hidden = !state.loggedIn;" in app_js,
                "jsHasWizardRenderers": "const wizardSteps = [" in app_js and "function renderWizardSteps()" in app_js and "stepNode.textContent = `${index + 1}. ${t(step.title)}`;" in app_js and "summaryBody.textContent = t(wizardSteps[state.activeWizardStep].description);" in app_js,
                "jsHasAuthModalOpenAndCapture": 'document.getElementById("authOpenModalBtn").addEventListener("click", openAuthModal);' in app_js and "function openAuthModal()" in app_js and "modal.showModal();" in app_js and 'document.getElementById("authStartCaptureBtn").addEventListener("click", startCaptureGuide);' in app_js and 'document.getElementById("authOpenLoginUrlBtn").addEventListener("click", openCaptureLoginPage);' in app_js and 'document.getElementById("authParseCaptureBtn").addEventListener("click", parseCapturedAuthText);' in app_js and 'document.getElementById("authApplyCaptureBtn").addEventListener("click", applyParsedCaptureSuggestion);' in app_js and 'fetchJson("/api/auth/capture/start"' in app_js and 'fetchJson("/api/auth/capture/parse"' in app_js and "window.open(loginUrl, \"_blank\", \"noopener\")" in app_js,
                "jsRendersStructuredCaptureGuide": "browserConsoleSnippets" in app_js and "manualSteps" in app_js and "pasteTargets=" in app_js and "networkCaptureTips" in app_js and "recommendedAuthModes" in app_js and "preferredCaptureMode" in app_js and "appliedFields=" in app_js and "stillMissing=" in app_js and "placeholderHints=" in app_js and "applySuggestedProfileToAuthForm" in app_js,
                "jsBootstrapsLoginAndLogout": 'document.getElementById("loginBtn").addEventListener("click", onLogin);' in app_js and 'document.getElementById("logoutBtn").addEventListener("click", onLogout);' in app_js and "await refreshSession();" in app_js and "await refreshProtectedData();" in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
