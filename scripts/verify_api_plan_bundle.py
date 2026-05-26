from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import task_runtime, webapp
from cloudpan_sync.models import AuthProfile


@contextmanager
def patched_attr(target: object, name: str, value: object):
    original = getattr(target, name)
    setattr(target, name, value)
    try:
        yield
    finally:
        setattr(target, name, original)


def main() -> None:
    original_tasks = dict(task_runtime._TASKS)
    task_runtime._TASKS.clear()

    profiles: dict[str, AuthProfile] = {}
    saved_snapshots: list[dict[str, object]] = []
    create_validation_calls: list[str] = []
    live_validation_calls: list[str] = []

    def fake_get_profile(profile_id: str):
        return profiles.get(profile_id)

    def fake_list_profiles():
        return list(profiles.values())

    def fake_update_profile(profile: AuthProfile):
        profiles[profile.profileId] = profile
        saved_snapshots.append(
            {
                "profileId": profile.profileId,
                "status": profile.status,
                "createValidationCallsBeforeSave": len(create_validation_calls),
                "liveValidationCallsBeforeSave": len(live_validation_calls),
            }
        )

    def fake_validate_profile_object(profile: AuthProfile):
        create_validation_calls.append(profile.profileId)
        return {
            "ok": True,
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "providerDisplayName": profile.displayName,
            "mode": "live",
            "status": 200,
            "error": "",
            "summary": "create validation ok",
            "checkedAt": "2026-05-26T00:00:00+00:00",
            "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}],
            "parentId": profile.extra.get("parentId", ""),
            "fileId": profile.extra.get("fileId", ""),
            "riskHint": "",
            "requiredFieldHints": [],
        }

    def fake_run_profile_live_validation(profile_id: str):
        live_validation_calls.append(profile_id)
        profile = profiles.get(profile_id)
        return {
            "ok": True,
            "profileId": profile_id,
            "providerKey": getattr(profile, "providerKey", ""),
            "providerDisplayName": getattr(profile, "displayName", ""),
            "mode": "live",
            "status": 200,
            "error": "",
            "summary": "live validate ok",
            "checkedAt": "2026-05-26T00:05:00+00:00",
            "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}],
            "parentId": (getattr(profile, "extra", {}) or {}).get("parentId", ""),
            "fileId": (getattr(profile, "extra", {}) or {}).get("fileId", ""),
            "riskHint": "",
            "requiredFieldHints": [],
        }

    def fake_auth_profile_view(profile: AuthProfile):
        extra = dict(profile.extra or {})
        return {
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "authMode": profile.authMode,
            "displayName": profile.displayName,
            "token": "tok-***" if profile.token else "",
            "cookie": "cookie-***" if profile.cookie else "",
            "extra": extra,
            "status": profile.status,
            "lastError": profile.lastError,
            "resolvedParentId": extra.get("parentId", ""),
            "resolvedFileId": extra.get("fileId", ""),
            "missingFieldHints": [],
            "writeMissingFieldHints": [],
            "profileReady": True,
            "writeReady": True,
        }

    with patched_attr(webapp, "ADMIN_PASSWORD", "admin123"):
        with patched_attr(webapp, "get_profile", fake_get_profile):
            with patched_attr(webapp, "list_profiles", fake_list_profiles):
                with patched_attr(webapp, "update_profile", fake_update_profile):
                    with patched_attr(webapp, "validate_profile_object", fake_validate_profile_object):
                        with patched_attr(webapp, "run_profile_live_validation", fake_run_profile_live_validation):
                            with patched_attr(webapp, "append_live_validation", lambda row: row):
                                with patched_attr(webapp, "_auth_profile_view", fake_auth_profile_view):
                                    app = webapp.create_app()
                                    client = TestClient(app)

                                    registry_payload = client.get("/api/providers").json()
                                    anonymous_session = client.get("/api/session").json()
                                    anonymous_profiles = client.get("/api/auth/profiles")
                                    anonymous_tasks = client.get("/api/tasks")
                                    anonymous_plan = client.post(
                                        "/api/plan/mock",
                                        json={
                                            "sourceProvider": "quark",
                                            "targetProvider": "guangya",
                                            "thresholdMB": 200,
                                            "conflictPolicy": "overwrite_existing",
                                            "selectedRoots": ["/demo.bin"],
                                            "entries": [{"path": "/demo.bin", "size": 4, "md5": ""}],
                                        },
                                    )

                                    bad_login = client.post("/api/login", json={"password": "wrong"})
                                    login_result = client.post("/api/login", json={"password": "admin123"})
                                    logged_in_session = client.get("/api/session").json()

                                    created_profile = client.post(
                                        "/api/auth/profiles",
                                        json={
                                            "providerKey": "guangya",
                                            "authMode": "manual_token",
                                            "displayName": "gy-api",
                                            "token": "tok-real",
                                            "cookie": "",
                                            "extra": {"parentId": "dir-100"},
                                        },
                                    ).json()
                                    created_profile_id = str((created_profile.get("item") or {}).get("profileId") or "")
                                    listed_profiles = client.get("/api/auth/profiles").json()
                                    validated_profile = client.post(f"/api/auth/profiles/{created_profile_id}/validate").json()

                                    plan_payload = {
                                        "sourceProvider": "quark",
                                        "targetProvider": "guangya",
                                        "thresholdMB": 200,
                                        "conflictPolicy": "overwrite_existing",
                                        "selectedRoots": ["/demo.bin"],
                                        "entries": [{"path": "/demo.bin", "size": 4, "md5": ""}],
                                    }
                                    mock_plan = client.post("/api/plan/mock", json=plan_payload).json()
                                    created_task = client.post("/api/tasks", json=plan_payload).json()
                                    task_id = str((created_task.get("item") or {}).get("taskId") or "")
                                    task_list = client.get("/api/tasks").json()
                                    fetched_task = client.get(f"/api/tasks/{task_id}").json()

                                    logout_result = client.post("/api/logout")
                                    logged_out_session = client.get("/api/session").json()

    task_runtime._TASKS.clear()
    task_runtime._TASKS.update(original_tasks)

    registry_items = list(registry_payload.get("items") or [])
    registry_by_key = {str(item.get("providerKey") or ""): dict(item) for item in registry_items}
    created_item = dict(created_profile.get("item") or {})
    validated_item = dict(validated_profile.get("item") or {})
    created_task_item = dict(created_task.get("item") or {})
    created_task_list = dict(created_task.get("listView") or {})
    fetched_task_detail = dict(fetched_task.get("detailView") or {})
    first_saved = saved_snapshots[0] if saved_snapshots else {}
    last_saved = saved_snapshots[-1] if saved_snapshots else {}
    listed_profile_items = list(listed_profiles.get("items") or [])
    listed_task_items = list(task_list.get("items") or [])
    listed_task_rows = list(task_list.get("listItems") or [])
    mock_plan_items = list(mock_plan.get("items") or [])
    created_plan_items = list((created_task_item.get("plan") or {}).get("items") or [])

    print(
        json.dumps(
            {
                "providerRegistryHasCoreProviders": (
                    "guangya" in registry_by_key
                    and "aliyundrive_open" in registry_by_key
                    and "quark" in registry_by_key
                ),
                "providerRegistryCarriesConflictPolicies": (
                    registry_by_key.get("guangya", {}).get("conflictPolicies") == ["overwrite_existing", "auto_rename_new"]
                    and registry_by_key.get("guangya", {}).get("supportsAutoRename") is True
                    and registry_by_key.get("guangya", {}).get("overwriteBehavior") == "downgrade_to_auto_rename"
                    and registry_by_key.get("aliyundrive_open", {}).get("supportsOverwrite") is True
                ),
                "anonymousSessionLoggedOut": anonymous_session.get("loggedIn") is False,
                "anonymousProfilesBlocked": anonymous_profiles.status_code == 401 and "please_login_first" in anonymous_profiles.text,
                "anonymousTasksBlocked": anonymous_tasks.status_code == 401 and "please_login_first" in anonymous_tasks.text,
                "anonymousPlanBlocked": anonymous_plan.status_code == 401 and "please_login_first" in anonymous_plan.text,
                "badPasswordRejected": bad_login.status_code == 401 and "invalid_password" in bad_login.text,
                "loginSetsSession": login_result.status_code == 200 and logged_in_session.get("loggedIn") is True,
                "authSaveRunsValidationBeforePersist": (
                    bool(created_profile_id)
                    and created_item.get("status") == "verified"
                    and created_profile.get("validation", {}).get("ok") is True
                    and first_saved.get("createValidationCallsBeforeSave") == 1
                ),
                "authProfilesListReturnsSavedProfile": (
                    len(listed_profile_items) == 1
                    and listed_profile_items[0].get("profileId") == created_profile_id
                    and listed_profile_items[0].get("resolvedParentId") == "dir-100"
                ),
                "authValidateUpdatesProfile": (
                    validated_profile.get("validation", {}).get("ok") is True
                    and validated_item.get("status") == "verified"
                    and last_saved.get("liveValidationCallsBeforeSave") == 1
                ),
                "mockPlanCarriesThresholdAndConflictPolicy": (
                    mock_plan.get("thresholdMB") == 200
                    and mock_plan.get("conflictPolicy") == "overwrite_existing"
                    and len(mock_plan_items) == 1
                    and mock_plan_items[0].get("strategy") == "download_upload"
                    and mock_plan_items[0].get("conflictPolicy") == "overwrite_existing"
                    and mock_plan_items[0].get("conflictSupportStatus") == "downgrade_to_auto_rename"
                ),
                "taskCreatePersistsPlanAndConflictPolicy": (
                    bool(task_id)
                    and created_task_item.get("state") == "awaiting_ack"
                    and created_task_item.get("conflictPolicy") == "overwrite_existing"
                    and (created_task_item.get("plan") or {}).get("conflictPolicy") == "overwrite_existing"
                    and len(created_plan_items) == 1
                    and created_plan_items[0].get("conflictPolicy") == "overwrite_existing"
                    and created_task_list.get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and created_task_list.get("firstConflictSupportStatus") == "downgrade_to_auto_rename"
                    and created_task_list.get("firstConflictNote") == "The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new."
                    and created_task_list.get("summary", {}).get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and created_task_list.get("summary", {}).get("firstConflictSupportStatus") == "downgrade_to_auto_rename"
                    and created_task_list.get("summary", {}).get("firstConflictNote") == "The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new."
                    and created_task.get("detailView", {}).get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and created_task.get("detailView", {}).get("firstConflictSupportStatus") == "downgrade_to_auto_rename"
                    and created_task.get("detailView", {}).get("firstConflictNote") == "The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new."
                    and len(created_task.get("detailView", {}).get("planItems") or []) == 1
                    and ((created_task.get("detailView", {}).get("planItems") or [{}])[0]).get("conflictSupportStatus") == "downgrade_to_auto_rename"
                    and created_task.get("detailView", {}).get("summary", {}).get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and created_task.get("detailView", {}).get("summary", {}).get("firstConflictSupportStatus") == "downgrade_to_auto_rename"
                    and created_task.get("detailView", {}).get("summary", {}).get("firstConflictNote") == "The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new."
                ),
                "taskListReturnsQueueState": (
                    len(listed_task_items) == 1
                    and len(listed_task_rows) == 1
                    and listed_task_rows[0].get("taskId") == task_id
                    and listed_task_rows[0].get("state") == "awaiting_ack"
                    and listed_task_rows[0].get("conflictPolicy") == "overwrite_existing"
                    and listed_task_rows[0].get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and listed_task_rows[0].get("firstConflictSupportStatus") == "downgrade_to_auto_rename"
                    and listed_task_rows[0].get("firstConflictNote") == "The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new."
                    and listed_task_rows[0].get("summary", {}).get("awaitingAcknowledgement") is True
                    and listed_task_rows[0].get("summary", {}).get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and listed_task_rows[0].get("summary", {}).get("firstConflictSupportStatus") == "downgrade_to_auto_rename"
                    and listed_task_rows[0].get("summary", {}).get("firstConflictNote") == "The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new."
                ),
                "taskDetailReturnsConflictPolicyAndPendingItems": (
                    fetched_task_detail.get("taskId") == task_id
                    and fetched_task_detail.get("state") == "awaiting_ack"
                    and fetched_task_detail.get("conflictPolicy") == "overwrite_existing"
                    and fetched_task_detail.get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and fetched_task_detail.get("firstConflictSupportStatus") == "downgrade_to_auto_rename"
                    and fetched_task_detail.get("firstConflictNote") == "The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new."
                    and len(fetched_task_detail.get("planItems") or []) == 1
                    and ((fetched_task_detail.get("planItems") or [{}])[0]).get("conflictSupportStatus") == "downgrade_to_auto_rename"
                    and len(fetched_task_detail.get("pendingItems") or []) == 0
                    and fetched_task_detail.get("summary", {}).get("awaitingAcknowledgement") is True
                    and fetched_task_detail.get("summary", {}).get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and fetched_task_detail.get("summary", {}).get("firstConflictSupportStatus") == "downgrade_to_auto_rename"
                    and fetched_task_detail.get("summary", {}).get("firstConflictNote") == "The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new."
                ),
                "logoutClearsSession": logout_result.status_code == 200 and logged_out_session.get("loggedIn") is False,
                "apiPlanBundleFlowMatchesExpectedLifecycle": (
                    "guangya" in registry_by_key
                    and registry_by_key.get("guangya", {}).get("conflictPolicies") == ["overwrite_existing", "auto_rename_new"]
                    and anonymous_session.get("loggedIn") is False
                    and anonymous_profiles.status_code == 401
                    and anonymous_tasks.status_code == 401
                    and anonymous_plan.status_code == 401
                    and bad_login.status_code == 401
                    and login_result.status_code == 200
                    and logged_in_session.get("loggedIn") is True
                    and bool(created_profile_id)
                    and created_item.get("status") == "verified"
                    and created_profile.get("validation", {}).get("ok") is True
                    and len(listed_profile_items) == 1
                    and validated_profile.get("validation", {}).get("ok") is True
                    and mock_plan.get("conflictPolicy") == "overwrite_existing"
                    and len(mock_plan_items) == 1
                    and mock_plan_items[0].get("conflictSupportStatus") == "downgrade_to_auto_rename"
                    and bool(task_id)
                    and created_task_item.get("state") == "awaiting_ack"
                    and created_task_item.get("conflictPolicy") == "overwrite_existing"
                    and created_task_list.get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and len(listed_task_rows) == 1
                    and listed_task_rows[0].get("state") == "awaiting_ack"
                    and listed_task_rows[0].get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and fetched_task_detail.get("state") == "awaiting_ack"
                    and fetched_task_detail.get("conflictPolicy") == "overwrite_existing"
                    and fetched_task_detail.get("conflictSupportSummaryStatuses") == ["downgrade_to_auto_rename"]
                    and logout_result.status_code == 200
                    and logged_out_session.get("loggedIn") is False
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
