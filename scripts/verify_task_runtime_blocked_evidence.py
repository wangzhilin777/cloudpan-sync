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

from cloudpan_sync import task_runtime, task_runtime_evidence_store, webapp


def main() -> None:
    original_tasks = dict(task_runtime._TASKS)
    original_password = webapp.ADMIN_PASSWORD
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE

    task_runtime._TASKS.clear()

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = tmp_path / "task_runtime_evidence.json"
        webapp.ADMIN_PASSWORD = "admin123"

        try:
            app = webapp.create_app()
            client = TestClient(app)
            login = client.post("/api/login", json={"password": "admin123"})
            assert login.status_code == 200, login.text

            created = client.post(
                "/api/tasks",
                json={
                    "sourceProvider": "quark",
                    "targetProvider": "quark",
                    "targetParentId": "0",
                    "thresholdMB": 1024,
                    "conflictPolicy": "auto_rename_new",
                    "acknowledgeDownloadUpload": True,
                    "selectedRoots": ["/large.iso"],
                    "entries": [
                        {
                            "path": "/large.iso",
                            "size": 600 * 1024 * 1024,
                            "md5": "",
                        }
                    ],
                },
            ).json()
            task_id = str((created.get("item") or {}).get("taskId") or "")
            run_payload = client.post(f"/api/tasks/{task_id}/action", json={"action": "run"}).json()

            latest = task_runtime_evidence_store.latest_task_runtime_evidence()
            summary = task_runtime_evidence_store.task_runtime_evidence_summary()
        finally:
            task_runtime._TASKS.clear()
            task_runtime._TASKS.update(original_tasks)
            webapp.ADMIN_PASSWORD = original_password
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file

    row = latest[0] if latest else {}
    print(
        json.dumps(
            {
                "taskState": (run_payload.get("item") or {}).get("state"),
                "firstResult": (((run_payload.get("item") or {}).get("results") or [None])[0]),
                "runtimeEvidenceCount": len(latest),
                "firstRuntimeRow": row,
                "summary": summary,
                "blockedModePersisted": row.get("mode"),
                "executionModePersisted": row.get("executionMode"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
