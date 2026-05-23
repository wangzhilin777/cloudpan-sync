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


def _find_row(items: list[dict[str, object]], provider_key: str) -> dict[str, object]:
    for item in items:
        if str(item.get("providerKey") or "") == provider_key:
            return item
    raise RuntimeError(f"provider not found: {provider_key}")


def main() -> None:
    original_password = webapp.ADMIN_PASSWORD
    webapp.ADMIN_PASSWORD = "admin123"
    try:
        app = webapp.create_app()
        client = TestClient(app)
        client.post("/api/login", json={"password": "admin123"})

        providers = client.get("/api/providers").json()
        matrix = client.get("/api/providers/status_matrix").json()
    finally:
        webapp.ADMIN_PASSWORD = original_password

    provider_items = providers.get("items") or []
    matrix_items = matrix.get("items") or []
    guangya_provider = _find_row(provider_items, "guangya")
    guangya_matrix = _find_row(matrix_items, "guangya")
    tianyi_matrix = _find_row(matrix_items, "189cloud")

    print(
        json.dumps(
            {
                "summary": matrix.get("summary") or {},
                "guangyaProvider": {
                    "conflictPolicies": guangya_provider.get("conflictPolicies"),
                    "supportsOverwrite": guangya_provider.get("supportsOverwrite"),
                    "supportsAutoRename": guangya_provider.get("supportsAutoRename"),
                    "overwriteBehavior": guangya_provider.get("overwriteBehavior"),
                },
                "guangyaMatrix": {
                    "conflictPolicies": guangya_matrix.get("conflictPolicies"),
                    "supportsOverwrite": guangya_matrix.get("supportsOverwrite"),
                    "supportsAutoRename": guangya_matrix.get("supportsAutoRename"),
                    "overwriteBehavior": guangya_matrix.get("overwriteBehavior"),
                },
                "tianyiMatrix": {
                    "create_dir_ready": tianyi_matrix.get("create_dir_ready"),
                    "conflictPolicies": tianyi_matrix.get("conflictPolicies"),
                    "supportsOverwrite": tianyi_matrix.get("supportsOverwrite"),
                    "supportsAutoRename": tianyi_matrix.get("supportsAutoRename"),
                    "overwriteBehavior": tianyi_matrix.get("overwriteBehavior"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
