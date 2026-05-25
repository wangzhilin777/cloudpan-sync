from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.plan_audit import to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_plan_audit.py"
SPEC = importlib.util.spec_from_file_location("export_plan_audit", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "generatedAt": "2026-05-25T00:00:00+00:00",
        "summary": {
            "done": 5,
            "partial": 2,
            "todo": 1,
            "providerCount": 10,
            "researchCount": 10,
            "featureMilestoneCount": 7,
            "strictMilestoneCount": 8,
            "featureCompletionPercent": 85.7,
            "strictCompletionPercent": 75.0,
        },
        "items": [
            {
                "key": "M5",
                "title": "首批常用网盘接入",
                "status": "partial",
                "evidence": "首批 provider 已补齐到 10 个。",
                "gaps": "真实秒传 API 成功样本仍缺。",
            },
            {
                "key": "P-REAL",
                "title": "真实联调验证",
                "status": "todo",
                "evidence": "已具备本地 mock 验证链路与真实证据状态报告。",
                "gaps": "尚未提供首批 provider 的真实联调成功证据。",
            },
        ],
    }

    original_root = export_script.ROOT
    original_runner = export_script.run_plan_audit
    original_renderer = export_script.to_markdown

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.run_plan_audit = lambda: synthetic_payload
        export_script.to_markdown = to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.run_plan_audit = original_runner
            export_script.to_markdown = original_renderer

        output_path = tmp_root / "docs" / "04-PLAN_AUDIT_REPORT.md"
        markdown = output_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "exportedFileExists": True,
                "exportedHasTitle": "# CloudPan Sync 计划完成度审计报告" in markdown,
                "exportedHasSummary": "done=5" in markdown and "partial=2" in markdown and "todo=1" in markdown,
                "exportedHasProgressPercents": "featureCompletionPercent=85.7" in markdown and "strictCompletionPercent=75.0" in markdown,
                "exportedHasFormulaNotes": "M1-M7" in markdown and "P-REAL" in markdown,
                "exportedHasProviderCoverage": "providerCount=10" in markdown and "researchCount=10" in markdown,
                "exportedHasM5Row": "### M5 - 首批常用网盘接入" in markdown and "状态：`partial`" in markdown,
                "exportedHasPRealRow": "### P-REAL - 真实联调验证" in markdown and "状态：`todo`" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
