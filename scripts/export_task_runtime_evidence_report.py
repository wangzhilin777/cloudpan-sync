from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.task_runtime_evidence_store import build_task_runtime_evidence_payload, task_runtime_evidence_to_markdown


def main() -> None:
    out = ROOT / "docs" / "11-TASK_RUNTIME_EVIDENCE.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(task_runtime_evidence_to_markdown(build_task_runtime_evidence_payload()), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
