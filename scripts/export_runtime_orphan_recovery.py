from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.runtime_orphan_recovery import build_runtime_orphan_recovery, runtime_orphan_recovery_to_markdown


def main() -> None:
    payload = build_runtime_orphan_recovery()
    output_path = ROOT / "docs" / "13-RUNTIME_ORPHAN_RECOVERY.md"
    output_path.write_text(runtime_orphan_recovery_to_markdown(payload), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
