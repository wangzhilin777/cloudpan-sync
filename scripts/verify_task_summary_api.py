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
        acknowledged = task_runtime.acknowledge_task_risk(str(awaiting_ack.get("taskId") or ""))
    finally:
        task_guard.get_profile = original_get_profile
        task_runtime._TASKS.clear()
        task_runtime._TASKS.update(original_tasks)

    blocked_summary = dict(blocked.get("summary") or {})
    awaiting_ack_summary = dict(awaiting_ack_snapshot.get("summary") or {})
    acknowledged_summary = dict(acknowledged.get("summary") or {})

    print(
        json.dumps(
            {
                "blockedSummaryHasConflictFields": (
                    blocked_summary.get("state") == "blocked"
                    and blocked_summary.get("hardBlocked") is True
                    and blocked_summary.get("conflictSupportSummaryStatuses") == ["unsupported"]
                    and blocked_summary.get("firstConflictSupportStatus") == "unsupported"
                    and blocked_summary.get("firstConflictNote") == "当前 189Cloud 已接入账号级 create_dir 写目录尝试，但 shareCode/accessCode-only 档案仍然只读，真实文件上传与同名冲突处理仍未声明为已支持。"
                ),
                "awaitingAckSummaryHasConflictFields": (
                    awaiting_ack_summary.get("state") == "awaiting_ack"
                    and awaiting_ack_summary.get("awaitingAcknowledgement") is True
                    and awaiting_ack_summary.get("conflictSupportSummaryStatuses") == ["supported"]
                    and awaiting_ack_summary.get("firstConflictSupportStatus") == "supported"
                    and awaiting_ack_summary.get("firstConflictNote") == ""
                ),
                "acknowledgedSummaryHasConflictFields": (
                    acknowledged_summary.get("state") == "ready"
                    and acknowledged_summary.get("awaitingAcknowledgement") is False
                    and acknowledged_summary.get("riskPaused") is False
                    and acknowledged_summary.get("conflictSupportSummaryStatuses") == ["supported"]
                    and acknowledged_summary.get("firstConflictSupportStatus") == "supported"
                    and acknowledged_summary.get("firstConflictNote") == ""
                ),
                "summaryConflictFieldsFlowMatchesStates": (
                    blocked_summary.get("state") == "blocked"
                    and blocked_summary.get("riskReason") == "guard_blocked"
                    and blocked_summary.get("hardBlocked") is True
                    and blocked_summary.get("conflictSupportSummaryStatuses") == ["unsupported"]
                    and blocked_summary.get("firstConflictSupportStatus") == "unsupported"
                    and awaiting_ack_summary.get("state") == "awaiting_ack"
                    and awaiting_ack_summary.get("riskReason") == "awaiting_acknowledgement"
                    and awaiting_ack_summary.get("awaitingAcknowledgement") is True
                    and awaiting_ack_summary.get("conflictSupportSummaryStatuses") == ["supported"]
                    and awaiting_ack_summary.get("firstConflictSupportStatus") == "supported"
                    and acknowledged_summary.get("state") == "ready"
                    and acknowledged_summary.get("riskReason") == ""
                    and acknowledged_summary.get("awaitingAcknowledgement") is False
                    and acknowledged_summary.get("riskPaused") is False
                    and acknowledged_summary.get("conflictSupportSummaryStatuses") == ["supported"]
                    and acknowledged_summary.get("firstConflictSupportStatus") == "supported"
                ),
                "blockedSummary": blocked_summary,
                "awaitingAckSummary": awaiting_ack_summary,
                "acknowledgedSummary": acknowledged_summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
