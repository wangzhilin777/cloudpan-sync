from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> None:
    index_html = (SRC / "cloudpan_sync" / "web" / "index.html").read_text(encoding="utf-8")
    app_js = (SRC / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
    app_css = (SRC / "cloudpan_sync" / "web" / "assets" / "app.css").read_text(encoding="utf-8")
    i18n_text = (SRC / "cloudpan_sync" / "i18n.py").read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "htmlHasPendingFoldDetails": (
                    'id="pendingDetails"' in index_html
                    and 'class="pending-fold"' in index_html
                    and 'id="pendingSummary"' in index_html
                    and 'id="pendingFoldHint"' in index_html
                    and 'id="pendingSummaryMeta"' in index_html
                    and 'class="pending-fold-body"' in index_html
                ),
                "jsBindsPendingFoldTexts": (
                    'document.getElementById("pendingTitle").textContent = t("panel.pending.title");' in app_js
                    and 'document.getElementById("pendingFoldHint").textContent = t("panel.pending.fold_hint");' in app_js
                    and 'document.getElementById("pendingSubtitle").textContent = t("panel.pending.subtitle");' in app_js
                ),
                "jsUpdatesPendingFoldSummaryMeta": (
                    'const summaryMeta = document.getElementById("pendingSummaryMeta");' in app_js
                    and 'summaryMeta.textContent = `tasks=${state.tasks.length}, pending=${rows.length}`;' in app_js
                    and 'const details = document.getElementById("pendingDetails");' in app_js
                    and "details.open = rows.length > 0;" in app_js
                ),
                "cssStylesPendingFold": (
                    ".pending-fold {" in app_css
                    and ".pending-fold-summary {" in app_css
                    and '.pending-fold-summary::after {' in app_css
                    and 'content: "展开";' in app_css
                    and '.pending-fold[open] > .pending-fold-summary::after {' in app_css
                    and 'content: "收起";' in app_css
                    and ".pending-fold-body {" in app_css
                ),
                "i18nHasPendingFoldHint": (
                    '"panel.pending.fold_hint": "可折叠查看人工确认条目"' in i18n_text
                    and '"panel.pending.fold_hint": "Collapsible manual review items"' in i18n_text
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
