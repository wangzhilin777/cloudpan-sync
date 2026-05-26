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


def _first(items: list[dict[str, object]]) -> dict[str, object]:
    if not items:
        raise RuntimeError("no items returned")
    return dict(items[0] or {})


def main() -> None:
    original_password = webapp.ADMIN_PASSWORD
    webapp.ADMIN_PASSWORD = "admin123"
    try:
        app = webapp.create_app()
        client = TestClient(app)
        client.post("/api/login", json={"password": "admin123"})

        guangya_plan = client.post(
            "/api/plan/mock",
            json={
                "sourceProvider": "quark",
                "targetProvider": "guangya",
                "thresholdMB": 200,
                "conflictPolicy": "overwrite_existing",
                "selectedRoots": ["/demo.bin"],
                "entries": [{"path": "/demo.bin", "size": 4, "md5": "a", "localPath": ""}],
            },
        ).json()

        tianyi_plan = client.post(
            "/api/plan/mock",
            json={
                "sourceProvider": "quark",
                "targetProvider": "189cloud",
                "thresholdMB": 200,
                "conflictPolicy": "auto_rename_new",
                "selectedRoots": ["/demo.bin"],
                "entries": [{"path": "/demo.bin", "size": 4, "md5": "a", "localPath": ""}],
            },
        ).json()
    finally:
        webapp.ADMIN_PASSWORD = original_password

    guangya_row = _first(guangya_plan.get("items") or [])
    tianyi_row = _first(tianyi_plan.get("items") or [])
    plan_conflict_support_flow_matches_expected_providers = (
        guangya_plan.get("conflictPolicy") == "overwrite_existing"
        and guangya_row.get("conflictSupportStatus") == "downgrade_to_auto_rename"
        and "downgrade to auto_rename_new" in str(guangya_row.get("conflictNote") or "")
        and tianyi_plan.get("conflictPolicy") == "auto_rename_new"
        and tianyi_row.get("conflictSupportStatus") == "unsupported"
        and "shareCode/accessCode-only" in str(tianyi_row.get("conflictNote") or "")
    )
    print(
        json.dumps(
            {
                "guangya": {
                    "conflictPolicy": guangya_plan.get("conflictPolicy"),
                    "itemConflictSupportStatus": guangya_row.get("conflictSupportStatus"),
                    "itemConflictNote": guangya_row.get("conflictNote"),
                },
                "tianyi189cloud": {
                    "conflictPolicy": tianyi_plan.get("conflictPolicy"),
                    "itemConflictSupportStatus": tianyi_row.get("conflictSupportStatus"),
                    "itemConflictNote": tianyi_row.get("conflictNote"),
                },
                "planConflictSupportFlowMatchesExpectedProviders": plan_conflict_support_flow_matches_expected_providers,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
