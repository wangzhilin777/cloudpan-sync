from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_live_validate import latest_live_validations, list_live_validations, live_validation_summary


def _count(text: str, needle: str) -> int:
    return text.count(needle)


def main() -> None:
    rows = list_live_validations()
    latest_rows = latest_live_validations()
    summary = live_validation_summary()
    markdown = (ROOT / "docs" / "03-AUTH_LIVE_VALIDATION_REPORT.md").read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "summaryHasCurrentValidationCounts": (
                    f"- totalRecords: `{len(rows)}`" in markdown
                    and f"- latestProfileCount: `{summary.get('profileCount', 0)}`" in markdown
                    and f"- latestOkCount: `{summary.get('okCount', 0)}`" in markdown
                    and f"- latestFailedCount: `{summary.get('failedCount', 0)}`" in markdown
                    and f"- latestProviders: `{', '.join(summary.get('providerKeys', [])) or '(none)'}`" in markdown
                ),
                "summaryShowsExpectedValidationCounts": (
                    len(rows) == 4
                    and summary.get("profileCount") == 2
                    and summary.get("okCount") == 0
                    and summary.get("failedCount") == 2
                    and summary.get("providerKeys") == ["guangya"]
                ),
                "latestSectionKeepsTwoGuangyaRows": (
                    _count(markdown, "### guangya -") >= 4
                    and _count(markdown, "- mode: `profile_incomplete`") >= 4
                    and _count(markdown, "- error: `missing_parent_id`") >= 4
                ),
                "latestRowsMatchLatestValidationCount": _count(markdown.split("## Recent History")[0], "### guangya -") == len(latest_rows),
                "recentHistoryKeepsCheckCountRows": _count(markdown, "- checkCount: `1`") == len(rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
