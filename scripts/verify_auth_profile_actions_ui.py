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
                "jsAuthListShowsPatchHint": "patch_hint=" in app_js,
                "jsAuthListShowsWriteBlocker": "write_blocker=" in app_js,
                "jsAuthListHasCaptureHelpCondition": "const needsCaptureHelp = Boolean(" in app_js
                and "item.needsSecretRefresh" in app_js
                and "item.writeReady === false" in app_js
                and "item.missingFieldHints" in app_js,
                "jsAuthListHasOpenCaptureAction": 'captureBtn.textContent = "Open Capture"' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(item.providerKey));' in app_js,
                "jsAuthListKeepsEvidenceAction": 'evidenceBtn.textContent = "Refresh Evidence"' in app_js
                and 'evidenceBtn.addEventListener("click", () => showAuthEvidence(item));' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
