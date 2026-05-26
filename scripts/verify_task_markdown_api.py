from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import task_runtime, webapp


def main() -> None:
    original_password = webapp.ADMIN_PASSWORD
    original_tasks = dict(task_runtime._TASKS)
    task_runtime._TASKS.clear()

    try:
        webapp.ADMIN_PASSWORD = "admin123"
        app = webapp.create_app()
        client = TestClient(app)
        login = client.post("/api/login", json={"password": "admin123"})
        assert login.status_code == 200, login.text

        create_resp = client.post(
            "/api/tasks",
            json={
                "sourceProvider": "quark",
                "targetProvider": "guangya",
                "targetProfileId": "",
                "targetParentId": "",
                "thresholdMB": 200,
                "conflictPolicy": "overwrite_existing",
                "acknowledgePendingManual": True,
                "acknowledgeDownloadUpload": True,
                "selectedRoots": ["/demo.bin"],
                "entries": [{"path": "/demo.bin", "size": 4, "md5": ""}],
            },
        )
        assert create_resp.status_code == 200, create_resp.text
        created = create_resp.json()
        task_id = str(((created.get("item") or {}).get("taskId")) or "")
        assert task_id, created

        task = task_runtime.get_task(task_id)
        assert task is not None, task_id
        first_item = dict(((task.get("plan") or {}).get("items") or [{}])[0] or {})
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

        markdown_resp = client.get(f"/api/tasks/{task_id}/markdown")
        assert markdown_resp.status_code == 200, markdown_resp.text
        markdown = str((markdown_resp.json() or {}).get("markdown") or "")

        print(
            json.dumps(
                {
                    "hasTitle": "# CloudPan Sync 任务详情" in markdown,
                    "hasConflictSection": "## 同名文件冲突策略" in markdown,
                    "hasSelectedPolicy": "selectedPolicy: `overwrite_existing`" in markdown,
                    "hasSupportSummary": f"supportSummary: `statuses={first_item.get('conflictSupportStatus', '') or '(none)'}`" in markdown,
                    "hasFirstPlannedConflict": (
                        f"firstPlannedConflict: path=`{first_item.get('path', '') or '(none)'}`" in markdown
                        and f"strategy=`{first_item.get('strategy', '') or '(none)'}`" in markdown
                        and f"conflictSupportStatus=`{first_item.get('conflictSupportStatus', '') or '(none)'}`" in markdown
                        and f"conflictNote=`{first_item.get('conflictNote', '') or '(none)'}`" in markdown
                    ),
                    "hasResultConflictPolicy": "conflictPolicy=`overwrite_existing`" in markdown,
                    "hasRuntimeConflictAction": "conflictAction=`overwrite_downgraded_to_auto_rename`" in markdown,
                    "hasResolvedTargetName": "resolvedTargetName=`demo (1).bin`" in markdown,
                    "hasPendingConflictStatus": "conflictSupportStatus=" in markdown,
                    "hasGuardSummary": "## 风险与守卫" in markdown and "riskReason=" in markdown,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        webapp.ADMIN_PASSWORD = original_password
        task_runtime._TASKS.clear()
        task_runtime._TASKS.update(original_tasks)


if __name__ == "__main__":
    main()
