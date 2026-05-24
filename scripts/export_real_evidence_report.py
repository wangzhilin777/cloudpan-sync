from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.real_evidence_report import build_real_evidence_report, real_evidence_to_markdown


def main() -> None:
    out = ROOT / "docs" / "10-REAL_EVIDENCE_STATUS.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(real_evidence_to_markdown(build_real_evidence_report()), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
