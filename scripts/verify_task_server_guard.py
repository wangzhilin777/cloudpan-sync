from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import task_guard, task_runtime
from cloudpan_sync.models import AuthProfile, TaskCreateRequest, SourceEntry


def main() -> None:
    original_get_profile = task_guard.get_profile
    original_tasks = dict(task_runtime._TASKS)
    task_runtime._TASKS.clear()

    try:
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

        soft_guard = task_runtime.create_task(
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
        soft_guard_snapshot = copy.deepcopy(soft_guard)
        acknowledged_soft_guard = task_runtime.acknowledge_task_risk(str(soft_guard.get("taskId") or ""))
    finally:
        task_guard.get_profile = original_get_profile
        task_runtime._TASKS.clear()
        task_runtime._TASKS.update(original_tasks)

    blocked_task = {
        "state": blocked.get("state"),
        "riskReason": (blocked.get("risk") or {}).get("reason"),
        "hardBlocked": (blocked.get("guard") or {}).get("hardBlocked"),
        "blockingReasons": (blocked.get("guard") or {}).get("blockingReasons"),
        "targetProfileWriteReady": (((blocked.get("guard") or {}).get("targetProfile") or {}).get("writeReady")),
    }
    soft_guard_task = {
        "state": soft_guard_snapshot.get("state"),
        "riskReason": (soft_guard_snapshot.get("risk") or {}).get("reason"),
        "hardBlocked": (soft_guard_snapshot.get("guard") or {}).get("hardBlocked"),
        "requiresAcknowledgement": (soft_guard_snapshot.get("guard") or {}).get("requiresAcknowledgement"),
        "acknowledged": (soft_guard_snapshot.get("guard") or {}).get("acknowledged"),
        "warningReasons": (soft_guard_snapshot.get("guard") or {}).get("warningReasons"),
    }
    acknowledged_soft_guard_task = {
        "state": acknowledged_soft_guard.get("state"),
        "riskReason": (acknowledged_soft_guard.get("risk") or {}).get("reason"),
        "acknowledged": (acknowledged_soft_guard.get("guard") or {}).get("acknowledged"),
        "warningReasons": (acknowledged_soft_guard.get("guard") or {}).get("warningReasons"),
    }

    print(
        json.dumps(
            {
                "blockedTask": blocked_task,
                "softGuardTask": soft_guard_task,
                "acknowledgedSoftGuardTask": acknowledged_soft_guard_task,
                "serverGuardFlowMatchesExpectedStates": (
                    blocked_task["state"] == "blocked"
                    and blocked_task["riskReason"] == "guard_blocked"
                    and blocked_task["hardBlocked"] is True
                    and blocked_task["targetProfileWriteReady"] is False
                    and any("shareCode/accessCode-only" in str(item) for item in (blocked_task["blockingReasons"] or []))
                    and soft_guard_task["state"] == "awaiting_ack"
                    and soft_guard_task["riskReason"] == "awaiting_acknowledgement"
                    and soft_guard_task["hardBlocked"] is False
                    and ((soft_guard_task["requiresAcknowledgement"] or {}).get("downloadUpload")) is True
                    and ((soft_guard_task["acknowledged"] or {}).get("downloadUpload")) is False
                    and any("explicit confirmation" in str(item) for item in (soft_guard_task["warningReasons"] or []))
                    and acknowledged_soft_guard_task["state"] == "ready"
                    and acknowledged_soft_guard_task["riskReason"] == ""
                    and ((acknowledged_soft_guard_task["acknowledged"] or {}).get("downloadUpload")) is True
                    and not (acknowledged_soft_guard_task["warningReasons"] or [])
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
