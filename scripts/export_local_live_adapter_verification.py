from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.local_live_adapter_verification import build_local_live_adapter_verification
from cloudpan_sync.local_live_adapter_verification import local_live_adapter_verification_to_markdown


def build_payload() -> dict[str, object]:
    return build_local_live_adapter_verification()


def to_markdown(payload: dict[str, object]) -> str:
    return local_live_adapter_verification_to_markdown(payload)


def main() -> None:
    out = ROOT / "docs" / "07-LOCAL_LIVE_ADAPTER_VERIFICATION.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(build_payload()), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
