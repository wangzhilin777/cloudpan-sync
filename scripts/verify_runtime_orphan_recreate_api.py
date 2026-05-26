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
from cloudpan_sync.auth_store import get_profile, list_profiles


def main() -> None:
    original_runtime = runtime_orphan_recovery.latest_task_runtime_evidence
    original_profiles = runtime_orphan_recovery.list_profiles
    with tempfile.TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir) / ".cloudpan_sync_data"
        configure_data_dir(data_dir)
        runtime_orphan_recovery.latest_task_runtime_evidence = lambda: [
            {
                "providerKey": "guangya",
                "profileId": "gy-orphan-api",
                "path": "/demo.bin",
                "mode": "binary_upload_multipart",
                "verifyMode": "metadata_by_parent_name",
                "conflictPolicy": "auto_rename_new",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "savedAt": "2026-05-26T00:00:00+00:00",
                "success": True,
            }
        ]
        runtime_orphan_recovery.list_profiles = original_profiles
        try:
            app = webapp.create_app()
            with TestClient(app) as client:
                anonymous = client.post(
                    "/api/runtime_orphan_recovery/recreate_profile",
                    json={"providerKey": "guangya", "orphanProfileId": "gy-orphan-api"},
                )
                client.post("/api/login", json={"password": webapp.ADMIN_PASSWORD})
                created = client.post(
                    "/api/runtime_orphan_recovery/recreate_profile",
                    json={"providerKey": "guangya", "orphanProfileId": "gy-orphan-api"},
                )
                created_payload = created.json() if created.status_code == 200 else {}
                created_profile = get_profile("gy-orphan-api")
                orphan_after = client.get("/api/runtime_orphan_recovery").json()
                auth_profiles = client.get("/api/auth/profiles").json()
                recreated_again = client.post(
                    "/api/runtime_orphan_recovery/recreate_profile",
                    json={"providerKey": "guangya", "orphanProfileId": "gy-orphan-api"},
                )
                recreated_again_payload = recreated_again.json() if recreated_again.status_code == 200 else {}
                expected_refresh = ".\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --profile-id gy-orphan-api --write"
                expected_runtime_probe = (
                    ".\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py "
                    "--target-provider guangya --target-profile-id gy-orphan-api"
                )
                expected_runtime_success = (
                    ".\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py "
                    "--target-provider guangya --target-profile-id gy-orphan-api"
                )

            print(
                json.dumps(
                    {
                        "anonymousBlocked": anonymous.status_code == 401 and "please_login_first" in anonymous.text,
                        "createdStubProfile": (
                            created.status_code == 200
                            and created_payload.get("status") == "stub_created"
                            and created_payload.get("created") is True
                            and (created_payload.get("item") or {}).get("profileId") == "gy-orphan-api"
                            and (created_payload.get("item") or {}).get("providerKey") == "guangya"
                            and "parentId" in ((created_payload.get("item") or {}).get("extra") or {})
                            and "token" in ((created_payload.get("item") or {}).get("placeholderSecretFieldHints") or [])
                            and "patch_and_probe_auth_profile.py --profile-id gy-orphan-api --write" in str(created_payload.get("recommendedRefreshEvidenceCommand") or "")
                            and "patch_and_probe_auth_profile.py --from-runtime-orphan-profile gy-orphan-api" in str(created_payload.get("exactRefreshEvidenceHelper") or "")
                            and "create_runtime_probe_task.py --target-provider guangya --target-profile-id gy-orphan-api" in str(created_payload.get("recommendedRuntimeProbeCommand") or "")
                            and "create_runtime_probe_task.py --from-runtime-orphan-profile gy-orphan-api" in str(created_payload.get("exactRuntimeProbeHelper") or "")
                            and "create_live_upload_task.py --target-provider guangya --target-profile-id gy-orphan-api" in str(created_payload.get("recommendedRuntimeSuccessCommand") or "")
                            and "create_live_upload_task.py --from-runtime-orphan-profile gy-orphan-api" in str(created_payload.get("exactRuntimeSuccessHelper") or "")
                        ),
                        "storedProfileUsesRequestedId": (
                            created_profile is not None
                            and created_profile.profileId == "gy-orphan-api"
                            and created_profile.providerKey == "guangya"
                            and created_profile.authMode == "manual_token"
                            and (created_profile.extra or {}).get("parentId") == "YOUR_REAL_PARENT_ID"
                        ),
                        "orphanRemovedAfterRecreate": (
                            (orphan_after.get("summary") or {}).get("orphanProfileCount") == 0
                            and (orphan_after.get("items") or []) == []
                        ),
                        "authProfilesContainsRecreatedStub": any(
                            item.get("profileId") == "gy-orphan-api" and item.get("providerKey") == "guangya"
                            for item in (auth_profiles.get("items") or [])
                        ),
                        "secondCallReturnsAlreadyExists": (
                            recreated_again.status_code == 200
                            and recreated_again_payload.get("status") == "already_exists"
                            and recreated_again_payload.get("created") is False
                            and str(recreated_again_payload.get("recommendedBootstrapCommand") or "") == ""
                            and str(recreated_again_payload.get("recommendedRefreshEvidenceCommand") or "") == expected_refresh
                            and "patch_and_probe_auth_profile.py --from-runtime-orphan-profile gy-orphan-api" in str(recreated_again_payload.get("exactRefreshEvidenceHelper") or "")
                            and expected_runtime_probe in str(recreated_again_payload.get("recommendedRuntimeProbeCommand") or "")
                            and "create_runtime_probe_task.py --from-runtime-orphan-profile gy-orphan-api" in str(recreated_again_payload.get("exactRuntimeProbeHelper") or "")
                            and expected_runtime_success in str(recreated_again_payload.get("recommendedRuntimeSuccessCommand") or "")
                            and "create_live_upload_task.py --from-runtime-orphan-profile gy-orphan-api" in str(recreated_again_payload.get("exactRuntimeSuccessHelper") or "")
                            and "--conflict-policy overwrite_existing"
                            in str(recreated_again_payload.get("recommendedOverwriteVariantCommand") or "")
                        ),
                        "dataDirContainsSingleProfile": len(list_profiles()) == 1,
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
