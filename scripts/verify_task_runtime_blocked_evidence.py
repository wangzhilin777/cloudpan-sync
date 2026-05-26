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
    first_result = (((run_payload.get("item") or {}).get("results") or [None])[0])
    first_live_attempt = dict(((first_result or {}).get("liveAttempt") or {}))
    print(
        json.dumps(
            {
                "blockedRuntimeEvidencePersisted": (
                    (run_payload.get("item") or {}).get("state") == "completed_with_errors"
                    and str((first_result or {}).get("executionMode") or "") == "blocked"
                    and str((first_result or {}).get("status") or "") == "failed"
                    and first_live_attempt.get("mode") == "download_upload_blocked_by_size_limit"
                    and first_live_attempt.get("riskHint") == "download_upload_size_limit_exceeded"
                    and first_live_attempt.get("error") == "download_upload_blocked_by_size_limit"
                    and int((first_live_attempt.get("payload") or {}).get("limitBytes") or 0) == 536870912
                    and len(latest) == 1
                    and row.get("mode") == "download_upload_blocked_by_size_limit"
                    and row.get("executionMode") == "blocked"
                    and row.get("status") == "failed"
                    and row.get("riskHint") == "download_upload_size_limit_exceeded"
                    and row.get("error") == "download_upload_blocked_by_size_limit"
                    and summary.get("blockedProviderCount") == 1
                    and summary.get("blockedCount") == 1
                    and summary.get("failedProviderCount") == 1
                    and summary.get("failedCount") == 1
                ),
                "taskState": (run_payload.get("item") or {}).get("state"),
                "firstResult": first_result,
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
