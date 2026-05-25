from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.live_probe import probe_to_markdown, run_live_probe


def main() -> None:
    out = ROOT / "docs" / "05-PROVIDER_LIVE_PROBE_REPORT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(probe_to_markdown(run_live_probe()), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
