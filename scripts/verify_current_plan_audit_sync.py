from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.plan_audit import run_plan_audit
from cloudpan_sync.real_evidence_report import build_real_evidence_report


def _section(markdown: str, marker: str) -> str:
    start = markdown.find(marker)
    if start < 0:
        return ""
    next_start = markdown.find("\n### ", start + 1)
    if next_start < 0:
        return markdown[start:]
    return markdown[start:next_start]


def main() -> None:
    audit = run_plan_audit()
    summary = dict(audit.get("summary") or {})
    real_evidence = build_real_evidence_report()
    real_summary = dict(real_evidence.get("summary") or {})
    real_items = [dict(item or {}) for item in list(real_evidence.get("items") or [])]
    guangya_item = next((item for item in real_items if str(item.get("providerKey") or "") == "guangya"), {})
    guangya_runtime = dict(guangya_item.get("taskRuntimeEvidence") or {})
    guangya_runtime_profiles = [str(value or "") for value in list(guangya_runtime.get("profiles") or []) if str(value or "")]
    guangya_orphan_profiles = [str(value or "") for value in list(guangya_runtime.get("orphanProfiles") or []) if str(value or "")]
    markdown = (ROOT / "docs" / "04-PLAN_AUDIT_REPORT.md").read_text(encoding="utf-8")

    m4 = _section(markdown, "### M4 - 光鸭 Provider")
    m5 = _section(markdown, "### M5 - 首批常用网盘接入")
    preal = _section(markdown, "### P-REAL - 真实联调验证")

    print(
        json.dumps(
            {
                "summaryHasCurrentAuditCounts": (
                    f"`done={summary.get('done', 0)}`" in markdown
                    and f"`partial={summary.get('partial', 0)}`" in markdown
                    and f"`todo={summary.get('todo', 0)}`" in markdown
                    and f"`featureCompletionPercent={summary.get('featureCompletionPercent', 0)}`" in markdown
                    and f"`strictCompletionPercent={summary.get('strictCompletionPercent', 0)}`" in markdown
                    and f"`done={', '.join(summary.get('doneKeys', [])) or '(none)'}` `partial={', '.join(summary.get('partialKeys', [])) or '(none)'}` `todo={', '.join(summary.get('todoKeys', [])) or '(none)'}`" in markdown
                ),
                "summaryShowsExpectedAuditCounts": (
                    summary.get("done") == 5
                    and summary.get("partial") == 2
                    and summary.get("todo") == 1
                    and summary.get("featureCompletionPercent") == 85.7
                    and summary.get("strictCompletionPercent") == 75.0
                    and summary.get("doneKeys") == ["M1", "M2", "M3", "M6", "M7"]
                    and summary.get("partialKeys") == ["M4", "M5"]
                    and summary.get("todoKeys") == ["P-REAL"]
                ),
                "m4SectionStillPartial": (
                    "- 状态：`partial`" in m4
                    and "仍缺稳定的真实在线联调成功样本" in m4
                    and "runtime_orphan" in m4
                    and "gy-live-1" in m4
                    and "gy-live-defaults-1" in m4
                    and f"当前 Guangya 已有 `{len(guangya_runtime_profiles)}` 条 runtime success 记录" in m4
                ),
                "m5SectionStillPartial": (
                    "- 状态：`partial`" in m5
                    and "仍缺真实在线成功样本" in m5
                    and "runtime_orphan" in m5
                    and f"共有 `{real_summary.get('taskRuntimeOrphanProfileCount', 0)}` 条 `runtime_orphan` 成功样本" in m5
                    and "gy-live-2" in m5
                    and "gy-orphan-live-1" in m5
                ),
                "prealSectionStillTodo": (
                    "- 状态：`todo`" in preal
                    and f"仓库里有 `{real_summary.get('taskRuntimeSuccessCount', 0)}` 条 runtime success 样本" in preal
                    and f"当前 `guangya, uc, pikpak` 的 `{real_summary.get('taskRuntimeSuccessCount', 0)}` 条 runtime success 样本都属于 auth profile 已脱节的 `runtime_orphan` 记录" in preal
                    and f"其中 Guangya 还包含 `{', '.join(guangya_orphan_profiles)}` 共 `{len(guangya_orphan_profiles)}` 条 orphan success" in preal
                ),
                "markdownExplainsFeatureFormula": "featureCompletionPercent" in markdown and "M1-M7" in markdown,
                "markdownExplainsStrictFormula": "strictCompletionPercent" in markdown and "P-REAL" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
