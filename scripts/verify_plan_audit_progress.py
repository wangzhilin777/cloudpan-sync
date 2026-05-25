from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.plan_audit import run_plan_audit, to_markdown


def main() -> None:
    audit = run_plan_audit()
    summary = dict(audit.get("summary") or {})
    markdown = to_markdown(audit)
    feature_percent = summary.get("featureCompletionPercent")
    strict_percent = summary.get("strictCompletionPercent")
    print(
        json.dumps(
            {
                "featureMilestoneCount": summary.get("featureMilestoneCount"),
                "strictMilestoneCount": summary.get("strictMilestoneCount"),
                "featureCompletionPercent": feature_percent,
                "strictCompletionPercent": strict_percent,
                "featureFormulaExpected": feature_percent == 85.7,
                "strictFormulaExpected": strict_percent == 75.0,
                "markdownHasFeaturePercent": "featureCompletionPercent=85.7" in markdown,
                "markdownHasStrictPercent": "strictCompletionPercent=75.0" in markdown,
                "markdownHasMilestoneSummary": "milestoneSummary: `done=M1, M2, M3, M6, M7` `partial=M4, M5` `todo=P-REAL`" in markdown,
                "markdownExplainsFeatureFormula": "featureCompletionPercent" in markdown and "M1-M7" in markdown,
                "markdownExplainsStrictFormula": "strictCompletionPercent" in markdown and "P-REAL" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
