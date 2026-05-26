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
                "conflictPolicy": "auto_rename_new",
                "acknowledgePendingManual": True,
                "acknowledgeDownloadUpload": True,
                "selectedRoots": ["/demo.bin"],
                "entries": [{"path": "/demo.bin", "size": 4, "md5": ""}],
            },
        )
        assert create_resp.status_code == 200, create_resp.text
        created = create_resp.json()
        created_item = dict(created.get("item") or {})
        created_list = dict(created.get("listView") or {})
        created_detail = dict(created.get("detailView") or {})
        task_id = str(created_item.get("taskId") or "")
        assert task_id, created

        pending_resp = client.post(
            "/api/tasks",
            json={
                "sourceProvider": "quark",
                "targetProvider": "guangya",
                "targetProfileId": "",
                "targetParentId": "",
                "thresholdMB": 0,
                "conflictPolicy": "auto_rename_new",
                "acknowledgePendingManual": True,
                "acknowledgeDownloadUpload": False,
                "selectedRoots": ["/pending.bin"],
                "entries": [{"path": "/pending.bin", "size": 4, "md5": ""}],
            },
        )
        assert pending_resp.status_code == 200, pending_resp.text
        pending_created = pending_resp.json()
        pending_list_view = dict(pending_created.get("listView") or {})

        list_resp = client.get("/api/tasks")
        assert list_resp.status_code == 200, list_resp.text
        listed = list_resp.json()
        list_items = list(listed.get("listItems") or [])
        assert list_items, listed
        first_list = dict(list_items[0] or {})
        pending_list_item = next(
            (
                dict(item or {})
                for item in list_items
                if str((item or {}).get("taskId") or "") == str(pending_list_view.get("taskId") or "")
            ),
            {},
        )

        get_resp = client.get(f"/api/tasks/{task_id}")
        assert get_resp.status_code == 200, get_resp.text
        fetched = get_resp.json()
        fetched_list = dict(fetched.get("listView") or {})
        fetched_detail = dict(fetched.get("detailView") or {})

        action_resp = client.post(f"/api/tasks/{task_id}/action", json={"action": "run"})
        assert action_resp.status_code == 200, action_resp.text
        action = action_resp.json()
        action_list = dict(action.get("listView") or {})
        action_detail = dict(action.get("detailView") or {})
        first_action_result = dict((action_detail.get("results") or [None])[0] or {})

        expected_conflict_statuses = ["supported"]
        expected_conflict_status = "supported"
        expected_conflict_note = ""

        print(
            json.dumps(
                {
                    "createTaskHasViews": bool(created_list and created_detail),
                    "createTaskViewsCarryConflictSummary": (
                        created_list.get("taskId") == task_id
                        and created_list.get("state") == "ready"
                        and isinstance(created_list.get("progress"), dict)
                        and isinstance(created_list.get("summary"), dict)
                        and isinstance(created_list.get("guard"), dict)
                        and created_list.get("conflictSupportSummaryStatuses") == expected_conflict_statuses
                        and created_list.get("firstConflictSupportStatus") == expected_conflict_status
                        and created_list.get("firstConflictNote") == expected_conflict_note
                        and created_detail.get("taskId") == task_id
                        and created_detail.get("state") == "ready"
                        and created_detail.get("state") == ((created_detail.get("summary") or {}).get("state"))
                        and created_detail.get("conflictSupportSummaryStatuses") == expected_conflict_statuses
                        and created_detail.get("firstConflictSupportStatus") == expected_conflict_status
                        and created_detail.get("firstConflictNote") == expected_conflict_note
                        and isinstance(created_detail.get("planSummary"), dict)
                        and len(created_detail.get("planItems") or []) == 1
                        and len(created_detail.get("executionGroups") or []) == 1
                        and len(created_detail.get("sourceEntries") or []) == 1
                    ),
                    "pendingTaskListViewCarriesPendingItems": (
                        pending_list_view.get("state") == "ready"
                        and len(pending_list_view.get("pendingItems") or []) == 1
                        and isinstance((((pending_list_view.get("pendingItems") or [None])[0]) or {}).get("availableFastInputs"), list)
                    ),
                    "listEndpointCarriesConflictSummary": (
                        len(listed.get("items") or []) == 2
                        and len(list_items) == 2
                        and isinstance(first_list.get("summary"), dict)
                        and isinstance(first_list.get("progress"), dict)
                        and first_list.get("conflictSupportSummaryStatuses") == expected_conflict_statuses
                        and first_list.get("firstConflictSupportStatus") == expected_conflict_status
                        and first_list.get("firstConflictNote") == expected_conflict_note
                        and isinstance(first_list.get("pendingItems"), list)
                        and isinstance(first_list.get("latestResults"), list)
                        and isinstance(pending_list_item.get("pendingItems"), list)
                        and isinstance(((((pending_list_item.get("pendingItems") or [None])[0]) or {}).get("availableFastInputs")), list)
                    ),
                    "getEndpointCarriesConflictSummary": (
                        bool(fetched_list)
                        and bool(fetched_detail)
                        and fetched_list.get("conflictSupportSummaryStatuses") == expected_conflict_statuses
                        and fetched_list.get("firstConflictSupportStatus") == expected_conflict_status
                        and fetched_list.get("firstConflictNote") == expected_conflict_note
                        and fetched_detail.get("conflictSupportSummaryStatuses") == expected_conflict_statuses
                        and fetched_detail.get("firstConflictSupportStatus") == expected_conflict_status
                        and fetched_detail.get("firstConflictNote") == expected_conflict_note
                        and isinstance(fetched_detail.get("planItems"), list)
                        and isinstance(fetched_detail.get("state"), str)
                        and "completionKind" in fetched_detail
                        and isinstance(fetched_detail.get("results"), list)
                        and isinstance(fetched_detail.get("sourceEntries"), list)
                    ),
                    "actionEndpointCarriesConflictSummary": (
                        action.get("action") == "run"
                        and action.get("actionApplied") is True
                        and action.get("allowedActions") == ["retry"]
                        and bool(action_list)
                        and bool(action_detail)
                        and action_list.get("conflictSupportSummaryStatuses") == expected_conflict_statuses
                        and action_list.get("firstConflictSupportStatus") == expected_conflict_status
                        and action_list.get("firstConflictNote") == expected_conflict_note
                        and action_detail.get("conflictSupportSummaryStatuses") == expected_conflict_statuses
                        and action_detail.get("firstConflictSupportStatus") == expected_conflict_status
                        and action_detail.get("firstConflictNote") == expected_conflict_note
                        and isinstance(action_detail.get("planItems"), list)
                        and isinstance(action_detail.get("state"), str)
                        and "completionKind" in action_detail
                        and action_detail.get("state") == ((action_detail.get("summary") or {}).get("state"))
                        and len(action_detail.get("results") or []) == 1
                        and first_action_result.get("executionMode") == "mock"
                    ),
                    "createListView": {
                        "taskId": created_list.get("taskId"),
                        "state": created_list.get("state"),
                        "completionKind": created_list.get("completionKind"),
                        "hasRealTransferSuccess": created_list.get("hasRealTransferSuccess"),
                        "hasProgress": isinstance(created_list.get("progress"), dict),
                        "hasSummary": isinstance(created_list.get("summary"), dict),
                        "hasGuard": isinstance(created_list.get("guard"), dict),
                        "conflictSupportSummaryStatuses": created_list.get("conflictSupportSummaryStatuses"),
                        "firstConflictSupportStatus": created_list.get("firstConflictSupportStatus"),
                        "firstConflictNote": created_list.get("firstConflictNote"),
                        "pendingItemsCount": len(created_list.get("pendingItems") or []),
                        "latestResultsCount": len(created_list.get("latestResults") or []),
                    },
                    "pendingCreateListView": {
                        "taskId": pending_list_view.get("taskId"),
                        "state": pending_list_view.get("state"),
                        "pendingItemsCount": len(pending_list_view.get("pendingItems") or []),
                        "firstPendingItemHasAvailableFastInputs": isinstance((((pending_list_view.get("pendingItems") or [None])[0]) or {}).get("availableFastInputs"), list),
                    },
                    "createDetailView": {
                        "taskId": created_detail.get("taskId"),
                        "topLevelState": created_detail.get("state"),
                        "completionKind": created_detail.get("completionKind"),
                        "hasRealTransferSuccess": created_detail.get("hasRealTransferSuccess"),
                        "summaryState": ((created_detail.get("summary") or {}).get("state")),
                        "stateMatchesSummary": created_detail.get("state") == ((created_detail.get("summary") or {}).get("state")),
                        "conflictSupportSummaryStatuses": created_detail.get("conflictSupportSummaryStatuses"),
                        "firstConflictSupportStatus": created_detail.get("firstConflictSupportStatus"),
                        "firstConflictNote": created_detail.get("firstConflictNote"),
                        "hasPlanSummary": isinstance(created_detail.get("planSummary"), dict),
                        "planItemsCount": len(created_detail.get("planItems") or []),
                        "executionGroupsCount": len(created_detail.get("executionGroups") or []),
                        "pendingItemsCount": len(created_detail.get("pendingItems") or []),
                        "resultsCount": len(created_detail.get("results") or []),
                        "sourceEntriesCount": len(created_detail.get("sourceEntries") or []),
                    },
                    "listEndpoint": {
                        "itemsCount": len(listed.get("items") or []),
                        "listItemsCount": len(list_items),
                        "firstTaskId": first_list.get("taskId"),
                        "firstHasSummary": isinstance(first_list.get("summary"), dict),
                        "firstHasProgress": isinstance(first_list.get("progress"), dict),
                        "firstConflictSupportSummaryStatuses": first_list.get("conflictSupportSummaryStatuses"),
                        "firstConflictSupportStatus": first_list.get("firstConflictSupportStatus"),
                        "firstConflictNote": first_list.get("firstConflictNote"),
                        "firstHasPendingItems": isinstance(first_list.get("pendingItems"), list),
                        "firstHasLatestResults": isinstance(first_list.get("latestResults"), list),
                        "pendingTaskHasPendingItems": isinstance(pending_list_item.get("pendingItems"), list),
                        "pendingTaskFirstPendingItemHasAvailableFastInputs": isinstance(((((pending_list_item.get("pendingItems") or [None])[0]) or {}).get("availableFastInputs")), list),
                    },
                    "getEndpoint": {
                        "hasListView": bool(fetched_list),
                        "hasDetailView": bool(fetched_detail),
                        "listConflictSupportSummaryStatuses": fetched_list.get("conflictSupportSummaryStatuses"),
                        "listFirstConflictSupportStatus": fetched_list.get("firstConflictSupportStatus"),
                        "listFirstConflictNote": fetched_list.get("firstConflictNote"),
                        "detailConflictSupportSummaryStatuses": fetched_detail.get("conflictSupportSummaryStatuses"),
                        "detailFirstConflictSupportStatus": fetched_detail.get("firstConflictSupportStatus"),
                        "detailFirstConflictNote": fetched_detail.get("firstConflictNote"),
                        "detailHasPlanItems": isinstance(fetched_detail.get("planItems"), list),
                        "detailHasState": isinstance(fetched_detail.get("state"), str),
                        "detailHasCompletionKind": "completionKind" in fetched_detail,
                        "detailHasResults": isinstance(fetched_detail.get("results"), list),
                        "detailHasSourceEntries": isinstance(fetched_detail.get("sourceEntries"), list),
                    },
                    "actionEndpoint": {
                        "action": action.get("action"),
                        "actionApplied": action.get("actionApplied"),
                        "allowedActions": action.get("allowedActions"),
                        "hasListView": bool(action_list),
                        "hasDetailView": bool(action_detail),
                        "listConflictSupportSummaryStatuses": action_list.get("conflictSupportSummaryStatuses"),
                        "listFirstConflictSupportStatus": action_list.get("firstConflictSupportStatus"),
                        "listFirstConflictNote": action_list.get("firstConflictNote"),
                        "detailConflictSupportSummaryStatuses": action_detail.get("conflictSupportSummaryStatuses"),
                        "detailFirstConflictSupportStatus": action_detail.get("firstConflictSupportStatus"),
                        "detailFirstConflictNote": action_detail.get("firstConflictNote"),
                        "detailHasPlanItems": isinstance(action_detail.get("planItems"), list),
                        "detailHasState": isinstance(action_detail.get("state"), str),
                        "detailHasCompletionKind": "completionKind" in action_detail,
                        "detailState": ((action_detail.get("summary") or {}).get("state")),
                        "detailTopLevelState": action_detail.get("state"),
                        "detailStateMatchesSummary": action_detail.get("state") == ((action_detail.get("summary") or {}).get("state")),
                        "detailResultsCount": len(action_detail.get("results") or []),
                        "firstExecutionMode": first_action_result.get("executionMode"),
                    },
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
