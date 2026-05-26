from __future__ import annotations

import importlib.util
import json
import os
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_store import get_profile, save_profile
from cloudpan_sync.models import AuthProfileInput

SCRIPT_PATH = ROOT / "scripts" / "recreate_runtime_orphan_stubs.py"
SPEC = importlib.util.spec_from_file_location("recreate_runtime_orphan_stubs", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
recreate_runtime_orphan_stubs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recreate_runtime_orphan_stubs)


def _run(args: list[str]) -> dict[str, object]:
    original_argv = sys.argv[:]
    try:
        sys.argv = [str(SCRIPT_PATH), *args]
        stdout_buffer = StringIO()
        with redirect_stdout(stdout_buffer):
            recreate_runtime_orphan_stubs.main()
        return json.loads(stdout_buffer.getvalue())
    finally:
        sys.argv = original_argv


def main() -> None:
    original_env = os.environ.get("CLOUDPAN_SYNC_DATA_DIR")
    original_builder = recreate_runtime_orphan_stubs.build_runtime_orphan_recovery

    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir) / ".cloudpan_sync_data"
        os.environ["CLOUDPAN_SYNC_DATA_DIR"] = str(data_dir)
        configure_data_dir(data_dir)

        save_profile(
            AuthProfileInput(
                providerKey="guangya",
                authMode="manual_token",
                displayName="already-saved-guangya",
                token="tok-existing",
                cookie="",
                extra={"parentId": "existing-parent"},
            ),
            profile_id_override="gy-live-1",
        )

        synthetic_payload = {
            "summary": {
                "providerCount": 2,
                "orphanProfileCount": 3,
            },
            "items": [
                {
                    "providerKey": "guangya",
                    "orphanProfileId": "gy-live-1",
                    "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-live-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-1 --token YOUR_TOKEN --set parentId=YOUR_PARENT_ID --probe",
                    "recommendedPrimaryCommandLabel": "Refresh Existing Orphan Profile",
                    "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-live-1 --write",
                    "recommendedRefreshEvidenceCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-live-1 --write",
                    "recommendedRuntimeProbeCommand": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --target-provider guangya --target-profile-id gy-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-runtime-orphan-probe-evidence",
                    "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-runtime-orphan-success-evidence",
                    "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\guangya-runtime-orphan-success-evidence",
                    "exactCreateHelper": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-runtime-orphan-profile gy-live-1",
                    "exactRefreshEvidenceHelper": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --from-runtime-orphan-profile gy-live-1",
                    "exactRuntimeProbeHelper": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --from-runtime-orphan-profile gy-live-1",
                    "exactRuntimeSuccessHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-runtime-orphan-profile gy-live-1",
                    "exactOverwriteVariantHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-runtime-orphan-profile gy-live-1",
                },
                {
                    "providerKey": "pikpak",
                    "orphanProfileId": "pikpak-live-1",
                    "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id pikpak-live-1 --provider-key pikpak --auth-mode manual_token --display-name pikpak-restore-pikpak-live-1 --token YOUR_TOKEN --set deviceId=YOUR_DEVICE_ID --probe",
                    "recommendedPrimaryCommandLabel": "Recreate Orphan Stub",
                    "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id pikpak-live-1 --provider-key pikpak --auth-mode manual_token --display-name pikpak-restore-pikpak-live-1 --token YOUR_TOKEN --set deviceId=YOUR_DEVICE_ID --probe",
                    "recommendedRefreshEvidenceCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id pikpak-live-1 --write",
                    "recommendedRuntimeProbeCommand": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --target-provider pikpak --target-profile-id pikpak-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\pikpak-runtime-orphan-probe-evidence",
                    "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider pikpak --target-profile-id pikpak-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\pikpak-runtime-orphan-success-evidence",
                    "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider pikpak --target-profile-id pikpak-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\pikpak-runtime-orphan-success-evidence",
                    "exactCreateHelper": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-runtime-orphan-profile pikpak-live-1",
                    "exactRefreshEvidenceHelper": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --from-runtime-orphan-profile pikpak-live-1",
                    "exactRuntimeProbeHelper": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --from-runtime-orphan-profile pikpak-live-1",
                    "exactRuntimeSuccessHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-runtime-orphan-profile pikpak-live-1",
                    "exactOverwriteVariantHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-runtime-orphan-profile pikpak-live-1",
                },
                {
                    "providerKey": "uc",
                    "orphanProfileId": "uc-live-1",
                    "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id uc-live-1 --provider-key uc --auth-mode manual_cookie --display-name uc-restore-uc-live-1 --cookie YOUR_COOKIE --set pwdId=YOUR_PWD_ID --probe",
                    "recommendedPrimaryCommandLabel": "Recreate Orphan Stub",
                    "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id uc-live-1 --provider-key uc --auth-mode manual_cookie --display-name uc-restore-uc-live-1 --cookie YOUR_COOKIE --set pwdId=YOUR_PWD_ID --probe",
                    "recommendedRefreshEvidenceCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id uc-live-1 --write",
                    "recommendedRuntimeProbeCommand": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --target-provider uc --target-profile-id uc-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\uc-runtime-orphan-probe-evidence",
                    "recommendedRuntimeSuccessCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider uc --target-profile-id uc-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\uc-runtime-orphan-success-evidence",
                    "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider uc --target-profile-id uc-live-1 --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\uc-runtime-orphan-success-evidence",
                    "exactCreateHelper": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-runtime-orphan-profile uc-live-1",
                    "exactRefreshEvidenceHelper": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --from-runtime-orphan-profile uc-live-1",
                    "exactRuntimeProbeHelper": r".\.venv\Scripts\python.exe scripts\create_runtime_probe_task.py --from-runtime-orphan-profile uc-live-1",
                    "exactRuntimeSuccessHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-runtime-orphan-profile uc-live-1",
                    "exactOverwriteVariantHelper": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --from-runtime-orphan-profile uc-live-1",
                },
            ],
        }

        recreate_runtime_orphan_stubs.build_runtime_orphan_recovery = lambda: synthetic_payload

        try:
            dry_run = _run([])
            provider_filtered = _run(["--provider-key", "pikpak"])
            write_run = _run(["--write"])
            gy_profile_after_write = get_profile("gy-live-1")
            overwrite_run = _run(["--write", "--orphan-profile-id", "gy-live-1", "--overwrite-existing"])
            gy_profile_after_overwrite = get_profile("gy-live-1")
        finally:
            recreate_runtime_orphan_stubs.build_runtime_orphan_recovery = original_builder
            if original_env is None:
                os.environ.pop("CLOUDPAN_SYNC_DATA_DIR", None)
            else:
                os.environ["CLOUDPAN_SYNC_DATA_DIR"] = original_env

        pikpak_profile = get_profile("pikpak-live-1")
        uc_profile = get_profile("uc-live-1")

        print(
            json.dumps(
                {
                    "dryRunSelectedAll": dry_run.get("selectedCount") == 3,
                    "dryRunSkipsExisting": dry_run.get("skippedExistingCount") == 1
                    and any(
                        item.get("orphanProfileId") == "gy-live-1" and item.get("action") == "skip_existing"
                        for item in (dry_run.get("items") or [])
                    ),
                    "dryRunShowsWouldWrite": sorted(
                        item.get("orphanProfileId")
                        for item in (dry_run.get("items") or [])
                        if item.get("action") == "would_write"
                    )
                    == ["pikpak-live-1", "uc-live-1"],
                    "providerFilterWorks": provider_filtered.get("selectedCount") == 1
                    and provider_filtered.get("filters") == {"providerKeys": ["pikpak"], "orphanProfileIds": []}
                    and ((provider_filtered.get("items") or [])[0].get("orphanProfileId") == "pikpak-live-1"),
                    "writeCreatesMissingProfiles": write_run.get("writtenCount") == 2
                    and pikpak_profile is not None
                    and pikpak_profile.providerKey == "pikpak"
                    and pikpak_profile.extra.get("deviceId") == "YOUR_DEVICE_ID"
                    and uc_profile is not None
                    and uc_profile.providerKey == "uc"
                    and uc_profile.cookie == "YOUR_COOKIE"
                    and uc_profile.extra.get("pwdId") == "YOUR_PWD_ID",
                    "writeKeepsExistingSkippedByDefault": gy_profile_after_write is not None
                    and gy_profile_after_write.displayName == "already-saved-guangya"
                    and write_run.get("skippedExistingCount") == 1,
                    "overwriteExistingRewritesProfile": overwrite_run.get("writtenCount") == 1
                    and gy_profile_after_overwrite is not None
                    and gy_profile_after_overwrite.displayName == "guangya-restore-gy-live-1"
                    and gy_profile_after_overwrite.extra.get("parentId") == "YOUR_PARENT_ID",
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
