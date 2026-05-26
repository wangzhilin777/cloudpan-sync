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


def _snippet_labels(payload: dict[str, object]) -> list[str]:
    return [str(item.get("label") or "") for item in (payload.get("browserConsoleSnippets") or []) if isinstance(item, dict)]


def main() -> None:
    app = webapp.create_app()
    client = TestClient(app)
    client.post("/api/login", json={"password": webapp.ADMIN_PASSWORD})

    quark = client.post("/api/auth/capture/start", json={"providerKey": "quark"}).json()
    guangya = client.post("/api/auth/capture/start", json={"providerKey": "guangya"}).json()
    aliyun = client.post("/api/auth/capture/start", json={"providerKey": "aliyundrive_open"}).json()

    print(
        json.dumps(
            {
                "quarkHasStructuredGuide": (
                    quark.get("status") == "capture_pending"
                    and quark.get("providerKey") == "quark"
                    and bool(quark.get("loginUrlHint"))
                    and quark.get("preferredCaptureMode") == "manual_cookie"
                    and "manual_cookie" in (quark.get("recommendedAuthModes") or [])
                    and isinstance(quark.get("requiredFieldHints"), list)
                    and isinstance(quark.get("manualSteps"), list)
                    and isinstance(quark.get("pasteTargets"), list)
                    and isinstance(quark.get("browserConsoleSnippets"), list)
                    and isinstance(quark.get("networkCaptureTips"), list)
                ),
                "quarkIncludesCookieAndShareHints": (
                    any("authCookie" in str(item) for item in (quark.get("pasteTargets") or []))
                    and any("authExtraPwdId" in str(item) for item in (quark.get("pasteTargets") or []))
                    and "Copy Cookie" in _snippet_labels(quark)
                    and "Copy Share Hints" in _snippet_labels(quark)
                ),
                "guangyaUsesTokenCaptureMode": (
                    guangya.get("preferredCaptureMode") == "manual_token"
                    and any("authToken" in str(item) for item in (guangya.get("pasteTargets") or []))
                    and any("authExtraParentId" in str(item) for item in (guangya.get("pasteTargets") or []))
                    and "Dump Storage" in _snippet_labels(guangya)
                ),
                "aliyunMentionsOpenSpecificFields": (
                    aliyun.get("preferredCaptureMode") == "official_oauth"
                    and any("authExtraDomainId" in str(item) for item in (aliyun.get("pasteTargets") or []))
                    and any("authExtraDriveId" in str(item) for item in (aliyun.get("pasteTargets") or []))
                    and any("domainId/driveId" in str(item) for item in (aliyun.get("manualSteps") or []))
                ),
                "authCaptureGuideFlowMatchesExpectedProviders": (
                    quark.get("status") == "capture_pending"
                    and quark.get("providerKey") == "quark"
                    and bool(quark.get("loginUrlHint"))
                    and quark.get("preferredCaptureMode") == "manual_cookie"
                    and "manual_cookie" in (quark.get("recommendedAuthModes") or [])
                    and any("authCookie" in str(item) for item in (quark.get("pasteTargets") or []))
                    and any("authExtraPwdId" in str(item) for item in (quark.get("pasteTargets") or []))
                    and "Copy Cookie" in _snippet_labels(quark)
                    and "Copy Share Hints" in _snippet_labels(quark)
                    and guangya.get("status") == "capture_pending"
                    and guangya.get("providerKey") == "guangya"
                    and guangya.get("preferredCaptureMode") == "manual_token"
                    and any("authToken" in str(item) for item in (guangya.get("pasteTargets") or []))
                    and any("authExtraParentId" in str(item) for item in (guangya.get("pasteTargets") or []))
                    and "Dump Storage" in _snippet_labels(guangya)
                    and aliyun.get("status") == "capture_pending"
                    and aliyun.get("providerKey") == "aliyundrive_open"
                    and aliyun.get("preferredCaptureMode") == "official_oauth"
                    and any("authExtraDomainId" in str(item) for item in (aliyun.get("pasteTargets") or []))
                    and any("authExtraDriveId" in str(item) for item in (aliyun.get("pasteTargets") or []))
                    and any("domainId/driveId" in str(item) for item in (aliyun.get("manualSteps") or []))
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
