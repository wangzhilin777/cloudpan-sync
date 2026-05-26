from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import runtime_orphan_recovery, webapp
from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_store import get_profile, save_profile
from cloudpan_sync.models import AuthProfileInput


def main() -> None:
    original_runtime = runtime_orphan_recovery.latest_task_runtime_evidence
    original_profiles = runtime_orphan_recovery.list_profiles
    with tempfile.TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir) / ".cloudpan_sync_data"
        configure_data_dir(data_dir)
        save_profile(
            AuthProfileInput(
                providerKey="guangya",
                authMode="manual_token",
                displayName="existing-guangya",
                token="tok-existing",
                cookie="",
                extra={"parentId": "existing-parent"},
            ),
            profile_id_override="gy-batch-1",
        )
        runtime_orphan_recovery.latest_task_runtime_evidence = lambda: [
            {
                "providerKey": "guangya",
                "profileId": "gy-batch-1",
                "path": "/demo-a.bin",
                "mode": "binary_upload_multipart",
                "verifyMode": "metadata_by_parent_name",
                "conflictPolicy": "auto_rename_new",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "savedAt": "2026-05-26T00:00:00+00:00",
                "success": True,
            },
            {
                "providerKey": "pikpak",
                "profileId": "pikpak-batch-1",
                "path": "/demo-b.bin",
                "mode": "binary_upload_after_hash_miss",
                "verifyMode": "metadata_by_file_id",
                "conflictPolicy": "overwrite_existing",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "savedAt": "2026-05-26T00:01:00+00:00",
                "success": True,
            },
        ]
        runtime_orphan_recovery.list_profiles = original_profiles
        try:
            app = webapp.create_app()
            with TestClient(app) as client:
                anonymous = client.post("/api/runtime_orphan_recovery/recreate_profiles", json={})
                client.post("/api/login", json={"password": webapp.ADMIN_PASSWORD})
                batch_missing = client.post(
                    "/api/runtime_orphan_recovery/recreate_profiles",
                    json={"providerKey": "", "overwriteExisting": False, "orphanProfileIds": []},
                )
                batch_missing_payload = batch_missing.json() if batch_missing.status_code == 200 else {}
                guangya_after_missing = get_profile("gy-batch-1")
                pikpak_after_missing = get_profile("pikpak-batch-1")
                batch_overwrite = client.post(
                    "/api/runtime_orphan_recovery/recreate_profiles",
                    json={"providerKey": "guangya", "overwriteExisting": True, "orphanProfileIds": []},
                )
                batch_overwrite_payload = batch_overwrite.json() if batch_overwrite.status_code == 200 else {}
                guangya_after_overwrite = get_profile("gy-batch-1")

            print(
                json.dumps(
                    {
                        "anonymousBlocked": anonymous.status_code == 401 and "please_login_first" in anonymous.text,
                        "batchMissingSkipsExistingAndCreatesMissing": (
                            batch_missing.status_code == 200
                            and batch_missing_payload.get("status") == "batch_completed"
                            and batch_missing_payload.get("selectedCount") == 1
                            and batch_missing_payload.get("createdCount") == 1
                            and batch_missing_payload.get("alreadyExistsCount") == 0
                            and batch_missing_payload.get("overwrittenCount") == 0
                            and "recreate_runtime_orphan_stubs.py --write" in str(batch_missing_payload.get("recommendedBatchWriteMissingCommand") or "")
                            and any(item.get("status") == "stub_created" for item in (batch_missing_payload.get("items") or []))
                            and guangya_after_missing is not None
                            and guangya_after_missing.displayName == "existing-guangya"
                            and pikpak_after_missing is not None
                            and pikpak_after_missing.providerKey == "pikpak"
                        ),
                        "batchOverwriteRewritesExisting": (
                            batch_overwrite.status_code == 200
                            and batch_overwrite_payload.get("selectedCount") == 1
                            and batch_overwrite_payload.get("createdCount") == 0
                            and batch_overwrite_payload.get("overwrittenCount") == 1
                            and batch_overwrite_payload.get("alreadyExistsCount") == 0
                            and batch_overwrite_payload.get("providerKey") == "guangya"
                            and "recreate_runtime_orphan_stubs.py --write --overwrite-existing --provider-key guangya" in str(batch_overwrite_payload.get("recommendedBatchOverwriteExistingCommand") or "")
                            and guangya_after_overwrite is not None
                            and guangya_after_overwrite.displayName == "guangya-restore-gy-batch-1"
                            and (guangya_after_overwrite.extra or {}).get("parentId") == "YOUR_REAL_PARENT_ID"
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        finally:
            runtime_orphan_recovery.latest_task_runtime_evidence = original_runtime
            runtime_orphan_recovery.list_profiles = original_profiles


if __name__ == "__main__":
    main()
