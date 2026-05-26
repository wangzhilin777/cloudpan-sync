from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.task_runtime import get_task, task_to_markdown


def _normalize_detail_snapshot(detail: dict[str, object]) -> dict[str, object]:
    normalized = dict(detail or {})
    if "plan" not in normalized:
        normalized["plan"] = {
            "summary": dict(normalized.get("planSummary") or {}),
            "items": list(normalized.get("planItems") or []),
            "pendingItems": list(normalized.get("pendingItems") or []),
            "executionGroups": list(normalized.get("executionGroups") or []),
        }
    return normalized


def _load_task_snapshot(path_text: str) -> dict[str, object]:
    payload = json.loads(Path(path_text).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        if isinstance(payload.get("item"), dict):
            return dict(payload.get("item") or {})
        if isinstance(payload.get("detailView"), dict):
            return _normalize_detail_snapshot(dict(payload.get("detailView") or {}))
        if "plan" not in payload and any(key in payload for key in ("planSummary", "planItems", "pendingItems", "executionGroups")):
            return _normalize_detail_snapshot(payload)
        return payload
    raise SystemExit(f"invalid_task_json: {path_text}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a saved task detail snapshot as Markdown.")
    parser.add_argument("--task-id", default="", help="Task id to export from the current in-process task store.")
    parser.add_argument("--task-json", default="", help="Path to a saved task snapshot JSON file.")
    parser.add_argument("--output", default="", help="Optional output markdown file path. Prints to stdout when omitted.")
    args = parser.parse_args()

    task_json = str(args.task_json or "").strip()
    task_id = str(args.task_id or "").strip()
    if task_json:
        task = _load_task_snapshot(task_json)
    elif task_id:
        task = get_task(task_id)
        if task is None:
            raise SystemExit(f"task_not_found: {task_id}")
    else:
        raise SystemExit("either --task-id or --task-json is required")

    markdown = task_to_markdown(task)
    output = str(args.output or "").strip()
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(output_path)
        return
    print(markdown, end="")


if __name__ == "__main__":
    main()
