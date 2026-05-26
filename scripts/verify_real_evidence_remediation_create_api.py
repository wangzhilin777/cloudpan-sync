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

from cloudpan_sync import webapp
from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_store import get_profile, list_profiles


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir) / ".cloudpan_sync_data"
        configure_data_dir(data_dir)
        app = webapp.create_app()
        with TestClient(app) as client:
            anonymous = client.post(
                "/api/real_evidence_remediation/create_profile",
                json={"providerKey": "aliyundrive_open"},
            )
            client.post("/api/login", json={"password": webapp.ADMIN_PASSWORD})
            created = client.post(
                "/api/real_evidence_remediation/create_profile",
                json={"providerKey": "aliyundrive_open"},
            )
            created_payload = created.json() if created.status_code == 200 else {}
            created_item = created_payload.get("item") or {}
            profile_id = str(created_item.get("profileId") or "")
            stored = get_profile(profile_id) if profile_id else None
            auth_profiles = client.get("/api/auth/profiles").json()
            created_again = client.post(
                "/api/real_evidence_remediation/create_profile",
                json={"providerKey": "aliyundrive_open"},
            )
            created_again_payload = created_again.json() if created_again.status_code == 200 else {}
            created_again_item = created_again_payload.get("item") or {}
            expected_refresh = f".\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --profile-id {profile_id} --write"
            expected_runtime_probe = (
                ".\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py "
                f"--target-provider aliyundrive_open --target-profile-id {profile_id}"
            )
            expected_runtime = (
                ".\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py "
                f"--target-provider aliyundrive_open --target-profile-id {profile_id}"
            )

        print(
            json.dumps(
                {
                    "anonymousBlocked": anonymous.status_code == 401 and "please_login_first" in anonymous.text,
                    "createdAliyunStub": (
                        created.status_code == 200
                        and created_payload.get("status") == "stub_created"
                        and created_payload.get("created") is True
                        and created_item.get("providerKey") == "aliyundrive_open"
                        and created_item.get("authMode") == "official_oauth"
                        and ((created_item.get("extra") or {}).get("domainId") == "YOUR_DOMAIN_ID")
                        and ((created_item.get("extra") or {}).get("driveId") == "YOUR_DRIVE_ID")
                        and "token" in (created_item.get("placeholderSecretFieldHints") or [])
                        and "create_auth_profile_stub.py --from-remediation-provider aliyundrive_open" in str(created_payload.get("exactCreateHelper") or "")
                        and "create_auth_profile_stub.py --provider-key aliyundrive_open" in str(created_payload.get("recommendedBootstrapCommand") or "")
                        and "create_live_upload_task.py --target-provider aliyundrive_open --target-profile-id YOUR_PROFILE_ID" in str(created_payload.get("recommendedPostBootstrapRuntimeCommand") or "")
                        and "create_live_upload_task.py --from-remediation-profile-id" in str(created_payload.get("exactPostBootstrapRuntimeHelper") or "")
                        and str(created_payload.get("exactRecreateHelper") or "") == ""
                        and "--conflict-policy overwrite_existing" in str(created_payload.get("recommendedOverwriteVariantCommand") or "")
                        and "patch_and_probe_auth_profile.py --from-remediation-profile-id" in str(created_payload.get("exactRefreshEvidenceHelper") or "")
                        and str(created_payload.get("exactPostRefreshRuntimeHelper") or "") == ""
                        and "create_runtime_probe_task.py --from-remediation-profile-id" in str(created_payload.get("exactRuntimeProbeHelper") or "")
                        and "create_live_upload_task.py --from-remediation-profile-id" in str(created_payload.get("exactRuntimeSuccessHelper") or "")
                        and "create_live_upload_task.py --from-remediation-profile-id" in str(created_payload.get("exactOverwriteVariantHelper") or "")
                    ),
                    "storedProfileHasPlaceholders": (
                        stored is not None
                        and stored.providerKey == "aliyundrive_open"
                        and stored.authMode == "official_oauth"
                        and (stored.extra or {}).get("domainId") == "YOUR_DOMAIN_ID"
                        and (stored.extra or {}).get("driveId") == "YOUR_DRIVE_ID"
                    ),
                    "authProfilesContainsCreatedStub": any(
                        item.get("profileId") == profile_id and item.get("providerKey") == "aliyundrive_open"
                        for item in (auth_profiles.get("items") or [])
                    ),
                    "secondCallReturnsAlreadyExists": (
                        created_again.status_code == 200
                        and created_again_payload.get("status") == "already_exists"
                        and created_again_payload.get("created") is False
                        and (created_again_item.get("profileId") == profile_id)
                        and str(created_again_payload.get("nextStep") or "").strip() != ""
                        and str(created_again_payload.get("exactCreateHelper") or "") == ""
                        and str(created_again_payload.get("recommendedBootstrapCommand") or "") == ""
                        and str(created_again_payload.get("exactRecreateHelper") or "") == ""
                        and str(created_again_payload.get("recommendedRefreshEvidenceCommand") or "") == expected_refresh
                        and "patch_and_probe_auth_profile.py --from-remediation-profile-id" in str(created_again_payload.get("exactRefreshEvidenceHelper") or "")
                        and str(created_again_payload.get("exactPostRefreshRuntimeHelper") or "") == ""
                        and str(created_again_payload.get("exactPostBootstrapRuntimeHelper") or "") == ""
                        and expected_runtime_probe in str(created_again_payload.get("recommendedRuntimeProbeCommand") or "")
                        and "create_runtime_probe_task.py --from-remediation-profile-id" in str(created_again_payload.get("exactRuntimeProbeHelper") or "")
                        and expected_runtime in str(created_again_payload.get("recommendedRuntimeSuccessCommand") or "")
                        and "create_live_upload_task.py --from-remediation-profile-id" in str(created_again_payload.get("exactRuntimeSuccessHelper") or "")
                        and "--conflict-policy overwrite_existing"
                        in str(created_again_payload.get("recommendedOverwriteVariantCommand") or "")
                        and "create_live_upload_task.py --from-remediation-profile-id" in str(created_again_payload.get("exactOverwriteVariantHelper") or "")
                    ),
                    "singleProfileWritten": len(list_profiles()) == 1,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
