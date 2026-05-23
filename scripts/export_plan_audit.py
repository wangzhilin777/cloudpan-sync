from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.plan_audit import run_plan_audit, to_markdown


def main() -> None:
    out = ROOT / "docs" / "04-PLAN_AUDIT_REPORT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(run_plan_audit()), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
