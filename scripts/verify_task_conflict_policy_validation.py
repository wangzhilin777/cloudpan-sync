from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import webapp


def main() -> None:
    original_password = webapp.ADMIN_PASSWORD
    webapp.ADMIN_PASSWORD = "admin123"
    try:
        app = webapp.create_app()
        client = TestClient(app)
        client.post("/api/login", json={"password": "admin123"})

        bad_plan = client.post(
            "/api/plan/mock",
            json={
                "sourceProvider": "quark",
                "targetProvider": "guangya",
                "thresholdMB": 200,
                "conflictPolicy": "invalid_policy",
                "selectedRoots": ["/demo.bin"],
                "entries": [{"path": "/demo.bin", "size": 4, "md5": ""}],
            },
        )

        bad_task = client.post(
            "/api/tasks",
            json={
                "sourceProvider": "quark",
                "targetProvider": "guangya",
                "targetProfileId": "gy-1",
                "targetParentId": "dir-100",
                "thresholdMB": 200,
                "conflictPolicy": "invalid_policy",
                "selectedRoots": ["/demo.bin"],
                "entries": [{"path": "/demo.bin", "size": 4, "md5": ""}],
            },
        )
    finally:
        webapp.ADMIN_PASSWORD = original_password

    bad_plan_status = bad_plan.status_code
    bad_plan_has_conflict_policy = "conflictPolicy" in bad_plan.text
    bad_task_status = bad_task.status_code
    bad_task_has_conflict_policy = "conflictPolicy" in bad_task.text

    print(
        json.dumps(
            {
                "badPlanStatus": bad_plan_status,
                "badPlanDetailHasConflictPolicy": bad_plan_has_conflict_policy,
                "badTaskStatus": bad_task_status,
                "badTaskDetailHasConflictPolicy": bad_task_has_conflict_policy,
                "invalidConflictPolicyRejectedEverywhere": (
                    bad_plan_status == 422
                    and bad_plan_has_conflict_policy is True
                    and bad_task_status == 422
                    and bad_task_has_conflict_policy is True
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
