from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.provider_status_matrix import build_status_matrix, matrix_to_markdown


def main() -> None:
    out = ROOT / "docs" / "06-PROVIDER_STATUS_MATRIX.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(matrix_to_markdown(build_status_matrix()), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
