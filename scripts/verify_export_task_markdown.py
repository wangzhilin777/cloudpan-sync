from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import task_runtime
from cloudpan_sync.models import SourceEntry, TaskCreateRequest


def main() -> None:
    original_tasks = dict(task_runtime._TASKS)
    task_runtime._TASKS.clear()

    output = ROOT / "tmp" / "verify-task-markdown.md"
    snapshot = ROOT / "tmp" / "verify-task-markdown.json"
    if output.exists():
        output.unlink()
    if snapshot.exists():
        snapshot.unlink()

    try:
        task = task_runtime.create_task(
            TaskCreateRequest(
                sourceProvider="quark",
                targetProvider="guangya",
                targetProfileId="",
                targetParentId="",
                thresholdMB=200,
                conflictPolicy="overwrite_existing",
                selectedRoots=["/demo.bin"],
                entries=[SourceEntry(path="/demo.bin", size=4, md5="abc")],
            )
        )
        task["results"] = [
            {
                "path": "/demo.bin",
                "status": "done",
                "executionMode": "live",
                "conflictPolicy": "overwrite_existing",
                "liveAttempt": {
                    "mode": "download_upload",
                    "conflictAction": "overwrite_downgraded_to_auto_rename",
                    "resolvedTargetName": "demo (1).bin",
                    "verifyOk": True,
                    "verifyMode": "list_by_parent_name",
                    "verifyNote": "verified by list",
                },
            }
        ]
        task_runtime.refresh_task_summary(task)
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(json.dumps({"item": task}, ensure_ascii=False, indent=2), encoding="utf-8")

        result = subprocess.run(
            [
                str(ROOT / ".venv" / "Scripts" / "python.exe"),
                str(ROOT / "scripts" / "export_task_markdown.py"),
                "--task-json",
                str(snapshot),
                "--output",
                str(output),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        markdown = output.read_text(encoding="utf-8")
        print(
            json.dumps(
                {
                    "stdoutHasOutputPath": str(output) in result.stdout,
                    "fileExists": output.exists(),
                    "markdownHasTitle": "# CloudPan Sync 任务详情" in markdown,
                    "markdownHasSelectedPolicy": "selectedPolicy: `overwrite_existing`" in markdown,
                    "markdownHasConflictAction": "conflictAction=`overwrite_downgraded_to_auto_rename`" in markdown,
                    "markdownHasResolvedTargetName": "resolvedTargetName=`demo (1).bin`" in markdown,
                    "markdownHasPlanConflictSupport": "conflictSupportStatus=`downgrade_to_auto_rename`" in markdown,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        if output.exists():
            output.unlink()
        if snapshot.exists():
            snapshot.unlink()
        task_runtime._TASKS.clear()
        task_runtime._TASKS.update(original_tasks)


if __name__ == "__main__":
    main()
