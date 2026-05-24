from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.real_evidence_remediation import (
    build_real_evidence_remediation_bundle,
    real_evidence_remediation_to_markdown,
)


def main() -> None:
    out = ROOT / "docs" / "12-REAL_EVIDENCE_REMEDIATION_GUIDE.md"
    out.write_text(real_evidence_remediation_to_markdown(build_real_evidence_remediation_bundle()), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
