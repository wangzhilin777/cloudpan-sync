from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import task_runtime_evidence_store, webapp


def main() -> None:
    original_password = webapp.ADMIN_PASSWORD
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE
    try:
        with TemporaryDirectory() as tmp_dir:
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = Path(tmp_dir) / "task_runtime_evidence.json"
            task_runtime_evidence_store.save_task_runtime_evidence(
                {
                    "taskId": "task-1",
                    "providerKey": "guangya",
                    "profileId": "gy-1",
                    "path": "/demo.bin",
                    "mode": "binary_upload_multipart",
                    "success": True,
                    "verifyOk": True,
                    "verifyMode": "list_by_parent_name",
                    "verifyNote": "verified by list",
                    "conflictPolicy": "overwrite_existing",
                    "conflictAction": "overwrite_downgraded_to_auto_rename",
                    "resolvedTargetName": "demo (1).bin",
                    "savedAt": "2026-05-24T00:00:00+00:00",
                }
            )
            payload = task_runtime_evidence_store.build_task_runtime_evidence_payload()
            markdown = task_runtime_evidence_store.task_runtime_evidence_to_markdown(payload)

            webapp.ADMIN_PASSWORD = "admin123"
            app = webapp.create_app()
            client = TestClient(app)
            login = client.post("/api/login", json={"password": "admin123"})
            assert login.status_code == 200, login.text
            api_payload = client.get("/api/task_runtime_evidence").json()
            api_markdown = client.get("/api/task_runtime_evidence_markdown").json()

            print(
                json.dumps(
                    {
                        "summary": payload.get("summary"),
                        "firstLatestItem": ((payload.get("latestItems") or [None])[0]),
                        "markdownHasTitle": "# CloudPan Sync 任务运行真实样本报告" in markdown,
                        "apiSummary": api_payload.get("summary"),
                        "apiMarkdownHasTitle": "# CloudPan Sync 任务运行真实样本报告" in str(api_markdown.get("markdown") or ""),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
    finally:
        webapp.ADMIN_PASSWORD = original_password
        task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file


if __name__ == "__main__":
    main()
