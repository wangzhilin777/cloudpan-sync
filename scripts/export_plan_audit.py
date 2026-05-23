from __future__ import annotations

from pathlib import Path

from cloudpan_sync.plan_audit import run_plan_audit, to_markdown


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "docs" / "PLAN_AUDIT_REPORT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(run_plan_audit()), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
