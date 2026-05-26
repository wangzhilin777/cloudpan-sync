from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import task_guard, task_runtime, webapp
from cloudpan_sync.models import AuthProfile, TaskCreateRequest, SourceEntry


def main() -> None:
    original_get_profile = task_guard.get_profile
    original_password = webapp.ADMIN_PASSWORD
    original_tasks = dict(task_runtime._TASKS)
    task_runtime._TASKS.clear()

    try:
        webapp.ADMIN_PASSWORD = "admin123"
        share_only_profile = AuthProfile(
            profileId="profile-189-readonly",
            providerKey="189cloud",
            authMode="manual_cookie",
            displayName="readonly-189",
            token="",
            cookie="",
            extra={"shareCode": "share-1"},
            status="saved",
            lastError="",
            createdAt="2026-05-23T00:00:00+00:00",
            updatedAt="2026-05-23T00:00:00+00:00",
        )

        def fake_get_profile(profile_id: str):
            if profile_id == "profile-189-readonly":
                return share_only_profile
            return None

        task_guard.get_profile = fake_get_profile

        blocked = task_runtime.create_task(
            TaskCreateRequest(
                sourceProvider="quark",
                targetProvider="189cloud",
                targetProfileId="profile-189-readonly",
                thresholdMB=200,
                conflictPolicy="auto_rename_new",
                selectedRoots=["/demo.bin"],
                entries=[SourceEntry(path="/demo.bin", size=4, md5="abc")],
            )
        )
        blocked_after_resume = task_runtime.resume_task(str(blocked.get("taskId") or ""))

        awaiting_ack = task_runtime.create_task(
            TaskCreateRequest(
                sourceProvider="quark",
                targetProvider="guangya",
                targetProfileId="",
                thresholdMB=200,
                conflictPolicy="auto_rename_new",
                selectedRoots=["/demo.bin"],
                entries=[SourceEntry(path="/demo.bin", size=4, md5="")],
            )
        )
        awaiting_ack_snapshot = copy.deepcopy(awaiting_ack)
        awaiting_ack_after_run = task_runtime.run_task(str(awaiting_ack.get("taskId") or ""))
        awaiting_ack_after_run_snapshot = copy.deepcopy(awaiting_ack_after_run)

        app = webapp.create_app()
        client = TestClient(app)
        client.post("/api/login", json={"password": "admin123"})
        action_resp = client.post(
            f"/api/tasks/{awaiting_ack_snapshot.get('taskId')}/action",
            json={"action": "run"},
        ).json()
        awaiting_ack_after_ack = task_runtime.acknowledge_task_risk(str(awaiting_ack.get("taskId") or ""))
    finally:
        task_guard.get_profile = original_get_profile
        webapp.ADMIN_PASSWORD = original_password
        task_runtime._TASKS.clear()
        task_runtime._TASKS.update(original_tasks)

    print(
        json.dumps(
            {
                "blockedResumeGuarded": (
                    blocked_after_resume.get("state") == "blocked"
                    and task_runtime.allowed_task_actions(blocked_after_resume) == ["retry"]
                    and dict(blocked_after_resume.get("lastActionError") or {}).get("action") == "resume"
                    and dict(blocked_after_resume.get("lastActionError") or {}).get("reason") == "resume_not_allowed_from_blocked"
                ),
                "awaitingAckRunGuarded": (
                    awaiting_ack_snapshot.get("state") == "awaiting_ack"
                    and task_runtime.allowed_task_actions(awaiting_ack_snapshot) == ["acknowledge_risk", "retry"]
                    and awaiting_ack_after_run_snapshot.get("state") == "awaiting_ack"
                    and dict(awaiting_ack_after_run_snapshot.get("lastActionError") or {}).get("action") == "run"
                    and dict(awaiting_ack_after_run_snapshot.get("lastActionError") or {}).get("reason") == "run_not_allowed_until_acknowledge_risk"
                ),
                "acknowledgeRiskRestoresRunnableState": (
                    awaiting_ack_after_ack.get("state") == "ready"
                    and task_runtime.allowed_task_actions(awaiting_ack_after_ack) == ["run", "pause", "retry"]
                    and dict(awaiting_ack_after_ack.get("lastActionError") or {}) == {}
                ),
                "httpActionGuardMatchesRuntime": (
                    action_resp.get("action") == "run"
                    and action_resp.get("actionApplied") is False
                    and dict(action_resp.get("actionError") or {}).get("action") == "run"
                    and dict(action_resp.get("actionError") or {}).get("reason") == "run_not_allowed_until_acknowledge_risk"
                    and action_resp.get("allowedActions") == ["acknowledge_risk", "retry"]
                ),
                "taskActionGuardFlowMatchesExpectedTransitions": (
                    blocked_after_resume.get("state") == "blocked"
                    and task_runtime.allowed_task_actions(blocked_after_resume) == ["retry"]
                    and dict(blocked_after_resume.get("lastActionError") or {}).get("action") == "resume"
                    and dict(blocked_after_resume.get("lastActionError") or {}).get("reason") == "resume_not_allowed_from_blocked"
                    and awaiting_ack_snapshot.get("state") == "awaiting_ack"
                    and task_runtime.allowed_task_actions(awaiting_ack_snapshot) == ["acknowledge_risk", "retry"]
                    and awaiting_ack_after_run_snapshot.get("state") == "awaiting_ack"
                    and dict(awaiting_ack_after_run_snapshot.get("lastActionError") or {}).get("action") == "run"
                    and dict(awaiting_ack_after_run_snapshot.get("lastActionError") or {}).get("reason") == "run_not_allowed_until_acknowledge_risk"
                    and action_resp.get("action") == "run"
                    and action_resp.get("actionApplied") is False
                    and dict(action_resp.get("actionError") or {}).get("reason") == "run_not_allowed_until_acknowledge_risk"
                    and action_resp.get("allowedActions") == ["acknowledge_risk", "retry"]
                    and awaiting_ack_after_ack.get("state") == "ready"
                    and task_runtime.allowed_task_actions(awaiting_ack_after_ack) == ["run", "pause", "retry"]
                    and dict(awaiting_ack_after_ack.get("lastActionError") or {}) == {}
                ),
                "blockedResume": {
                    "state": blocked_after_resume.get("state"),
                    "allowedActions": task_runtime.allowed_task_actions(blocked_after_resume),
                    "lastActionError": blocked_after_resume.get("lastActionError"),
                },
                "awaitingAckBefore": {
                    "state": awaiting_ack_snapshot.get("state"),
                    "allowedActions": task_runtime.allowed_task_actions(awaiting_ack_snapshot),
                },
                "awaitingAckRun": {
                    "state": awaiting_ack_after_run_snapshot.get("state"),
                    "lastActionError": awaiting_ack_after_run_snapshot.get("lastActionError"),
                },
                "awaitingAckAfterAcknowledge": {
                    "state": awaiting_ack_after_ack.get("state"),
                    "allowedActions": task_runtime.allowed_task_actions(awaiting_ack_after_ack),
                    "lastActionError": awaiting_ack_after_ack.get("lastActionError"),
                },
                "httpActionResponse": {
                    "action": action_resp.get("action"),
                    "actionApplied": action_resp.get("actionApplied"),
                    "actionError": action_resp.get("actionError"),
                    "allowedActions": action_resp.get("allowedActions"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
