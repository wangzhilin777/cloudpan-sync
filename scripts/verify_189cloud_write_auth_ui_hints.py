from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_remediation import _patch_command_for_profile
from cloudpan_sync.webapp import _capture_field_hints


def main() -> None:
    index_html = (ROOT / "src" / "cloudpan_sync" / "web" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    patch_command = _patch_command_for_profile({"profileId": "189-demo", "providerKey": "189cloud"})
    capture_hints = _capture_field_hints("189cloud")

    print(
        json.dumps(
            {
                "htmlHas189WriteInputs": all(
                    token in index_html
                    for token in ("authExtraAccessToken", "authExtraSignature", "authExtraDate")
                ),
                "jsResets189WriteInputs": all(
                    token in app_js
                    for token in (
                        'document.getElementById("authExtraAccessToken").value = "";',
                        'document.getElementById("authExtraSignature").value = "";',
                        'document.getElementById("authExtraDate").value = "";',
                    )
                ),
                "jsFills189WriteInputs": all(
                    token in app_js
                    for token in (
                        'document.getElementById("authExtraAccessToken").value = profile.extra?.accessToken || profile.extra?.access_token || "";',
                        'document.getElementById("authExtraSignature").value = profile.extra?.signature || profile.extra?.Signature || "";',
                        'document.getElementById("authExtraDate").value = profile.extra?.date || profile.extra?.Date || "";',
                    )
                ),
                "jsCollects189WriteInputs": all(
                    token in app_js
                    for token in (
                        'const extraAccessToken = document.getElementById("authExtraAccessToken").value.trim();',
                        'const extraSignature = document.getElementById("authExtraSignature").value.trim();',
                        'const extraDate = document.getElementById("authExtraDate").value.trim();',
                        "extra.accessToken = extraAccessToken;",
                        "extra.signature = extraSignature;",
                        "extra.date = extraDate;",
                    )
                ),
                "jsPatchHintMentionsWriteAuth": "YOUR_ACCESS_TOKEN" in app_js and "YOUR_SIGNATURE" in app_js and "YOUR_GMT_DATE" in app_js,
                "captureHints": capture_hints,
                "captureHintsMentionWriteAuth": any("accessToken" in item or "token" in item for item in capture_hints)
                and any("signature" in item for item in capture_hints)
                and any("date" in item for item in capture_hints),
                "remediationCommand": patch_command,
                "remediationMentionsWriteAuth": all(
                    token in patch_command
                    for token in ("shareCode", "accessToken", "signature", "date")
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
