from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import auth_live_validate, provider_live_probe
from cloudpan_sync import auth_profile_evidence
from cloudpan_sync.auth_profile_patch import configure_data_dir

PATCH_AND_PROBE_PATH = ROOT / "scripts" / "patch_and_probe_auth_profile.py"
SPEC = importlib.util.spec_from_file_location("patch_and_probe_auth_profile", PATCH_AND_PROBE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {PATCH_AND_PROBE_PATH}")
patch_and_probe_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patch_and_probe_script)


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "gy-patch-defaults",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "gy-defaults",
                        "token": "tok_defaults",
                        "cookie": "",
                        "extra": {},
                        "status": "unknown",
                        "lastError": "",
                        "createdAt": "2026-05-26T00:00:00+00:00",
                        "updatedAt": "2026-05-26T00:00:00+00:00",
                    },
                    {
                        "profileId": "gy-patch-defaults-2",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "gy-defaults-2",
                        "token": "tok_defaults_2",
                        "cookie": "",
                        "extra": {},
                        "status": "unknown",
                        "lastError": "",
                        "createdAt": "2026-05-26T00:00:00+00:00",
                        "updatedAt": "2026-05-26T00:00:00+00:00",
                    }
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        configure_data_dir(data_dir)

        original_validate = auth_live_validate.validate_profile_object
        original_probe = provider_live_probe.run_provider_live_probe
        original_evidence_validate = auth_profile_evidence.validate_profile_object
        original_evidence_probe = auth_profile_evidence.run_provider_live_probe
        original_remediation_builder = patch_and_probe_script.build_real_evidence_remediation_bundle
        original_runtime_orphan_builder = patch_and_probe_script.build_runtime_orphan_recovery
        probe_calls: list[dict[str, object]] = []

        def fake_validate(profile: object) -> dict[str, object]:
            return {
                "ok": True,
                "profileId": getattr(profile, "profileId", ""),
                "providerKey": getattr(profile, "providerKey", ""),
                "summary": "validation ok",
                "checkedAt": "2026-05-26T00:00:00+00:00",
                "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}],
                "parentId": str((getattr(profile, "extra", {}) or {}).get("parentId") or ""),
                "fileId": str((getattr(profile, "extra", {}) or {}).get("fileId") or ""),
                "riskHint": "",
                "requiredFieldHints": [],
            }

        def fake_probe(profile_id: str, parent_id: str = "", file_id: str = "", page_size: int = 100, dir_name: str = "") -> dict[str, object]:
            probe_calls.append(
                {
                    "profileId": profile_id,
                    "parentId": parent_id,
                    "fileId": file_id,
                    "pageSize": page_size,
                    "dirName": dir_name,
                }
            )
            return {
                "ok": True,
                "profileId": profile_id,
                "providerKey": "guangya",
                "summary": "probe ok",
                "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "itemCount": 1, "note": "list ok"}],
                "parentId": parent_id,
                "fileId": file_id,
                "dirName": dir_name,
                "pageSize": page_size,
            }

        auth_live_validate.validate_profile_object = fake_validate
        provider_live_probe.run_provider_live_probe = fake_probe
        auth_profile_evidence.validate_profile_object = fake_validate
        auth_profile_evidence.run_provider_live_probe = fake_probe
        patch_and_probe_script.build_real_evidence_remediation_bundle = lambda: {
            "summary": {},
            "items": [
                {
                    "providerKey": "guangya",
                    "profileIds": ["gy-patch-defaults", "gy-patch-defaults-2"],
                    "recommendedPatchProbeCommands": [
                        r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-patch-defaults --set parentId=YOUR_REAL_PARENT_ID --set fileId=YOUR_FILE_ID --write",
                        r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-patch-defaults-2 --set parentId=YOUR_REAL_PARENT_ID --set fileId=YOUR_FILE_ID_2 --write",
                    ],
                    "recommendedPatchProbeCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-patch-defaults --set parentId=YOUR_REAL_PARENT_ID --set fileId=YOUR_FILE_ID --write",
                },
                {
                    "providerKey": "aliyundrive_open",
                    "profileIds": ["ali-patch-defaults"],
                    "recommendedPatchCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id ali-patch-defaults --set domainId=YOUR_DOMAIN_ID --write",
                },
            ],
        }
        patch_and_probe_script.build_runtime_orphan_recovery = lambda: {
            "summary": {},
            "items": [
                {
                    "providerKey": "guangya",
                    "orphanProfileId": "gy-patch-defaults-2",
                    "recommendedRefreshEvidenceCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-patch-defaults-2 --set parentId=YOUR_ORPHAN_PARENT_ID --set fileId=YOUR_ORPHAN_FILE_ID --write",
                }
            ],
        }
        try:
            defaults_stdout = io.StringIO()
            with redirect_stdout(defaults_stdout):
                patch_and_probe_script.main(
                    [
                        "--from-remediation-provider",
                        "guangya",
                        "--set",
                        "parentId=dir-explicit",
                        "--dir-name",
                        "verify-defaults-dir",
                        "--page-size",
                        "9",
                        "--data-dir",
                        str(data_dir),
                    ]
                )
            defaults_payload = json.loads(defaults_stdout.getvalue())

            exact_defaults_stdout = io.StringIO()
            with redirect_stdout(exact_defaults_stdout):
                patch_and_probe_script.main(
                    [
                        "--from-remediation-profile-id",
                        "gy-patch-defaults-2",
                        "--set",
                        "parentId=dir-exact",
                        "--dir-name",
                        "verify-exact-dir",
                        "--page-size",
                        "7",
                        "--data-dir",
                        str(data_dir),
                    ]
                )
            exact_defaults_payload = json.loads(exact_defaults_stdout.getvalue())

            orphan_defaults_stdout = io.StringIO()
            with redirect_stdout(orphan_defaults_stdout):
                patch_and_probe_script.main(
                    [
                        "--from-runtime-orphan-profile",
                        "gy-patch-defaults-2",
                        "--set",
                        "parentId=dir-orphan-exact",
                        "--dir-name",
                        "verify-orphan-dir",
                        "--page-size",
                        "5",
                        "--data-dir",
                        str(data_dir),
                    ]
                )
            orphan_defaults_payload = json.loads(orphan_defaults_stdout.getvalue())

            missing_profile_id_error = ""
            try:
                patch_and_probe_script.main(["--from-remediation-provider", "missing-provider", "--data-dir", str(data_dir)])
            except SystemExit as exc:
                missing_profile_id_error = str(exc)
            missing_exact_profile_id_error = ""
            try:
                patch_and_probe_script.main(["--from-remediation-profile-id", "missing-profile", "--data-dir", str(data_dir)])
            except SystemExit as exc:
                missing_exact_profile_id_error = str(exc)
            missing_orphan_profile_id_error = ""
            try:
                patch_and_probe_script.main(["--from-runtime-orphan-profile", "missing-orphan-profile", "--data-dir", str(data_dir)])
            except SystemExit as exc:
                missing_orphan_profile_id_error = str(exc)
        finally:
            auth_live_validate.validate_profile_object = original_validate
            provider_live_probe.run_provider_live_probe = original_probe
            auth_profile_evidence.validate_profile_object = original_evidence_validate
            auth_profile_evidence.run_provider_live_probe = original_evidence_probe
            patch_and_probe_script.build_real_evidence_remediation_bundle = original_remediation_builder
            patch_and_probe_script.build_runtime_orphan_recovery = original_runtime_orphan_builder

        profiles = json.loads((data_dir / "auth_profiles.json").read_text(encoding="utf-8"))
        profile = next(item for item in profiles if item.get("profileId") == "gy-patch-defaults")
        exact_profile = next(item for item in profiles if item.get("profileId") == "gy-patch-defaults-2")
        print(
            json.dumps(
                {
                    "defaultsSourceApplied": defaults_payload.get("defaultsSource") == "remediation:recommendedPatchProbeCommand",
                    "defaultProfileResolved": defaults_payload.get("profileId") == "gy-patch-defaults",
                    "writeInherited": defaults_payload.get("written") is True and profile.get("updatedAt", "") != "2026-05-26T00:00:00+00:00",
                    "defaultAndExplicitSetsMerged": dict(defaults_payload.get("extra") or {}).get("fileId") == "YOUR_FILE_ID"
                    and dict(defaults_payload.get("extra") or {}).get("parentId") == "dir-explicit",
                    "probeUsedMergedValues": len(probe_calls) >= 1
                    and probe_calls[0].get("profileId") == "gy-patch-defaults"
                    and probe_calls[0].get("parentId") == "dir-explicit"
                    and probe_calls[0].get("fileId") == "YOUR_FILE_ID"
                    and probe_calls[0].get("dirName") == "verify-defaults-dir"
                    and probe_calls[0].get("pageSize") == 9,
                    "profilePersistedMergedValues": dict(profile.get("extra") or {}).get("fileId") == "YOUR_FILE_ID"
                    and dict(profile.get("extra") or {}).get("parentId") == "dir-explicit",
                    "exactDefaultsSourceApplied": exact_defaults_payload.get("defaultsSource") == "remediation:recommendedPatchProbeCommands",
                    "exactDefaultProfileResolved": exact_defaults_payload.get("profileId") == "gy-patch-defaults-2",
                    "exactWriteInherited": exact_defaults_payload.get("written") is True and exact_profile.get("updatedAt", "") != "2026-05-26T00:00:00+00:00",
                    "exactDefaultAndExplicitSetsMerged": dict(exact_defaults_payload.get("extra") or {}).get("fileId") == "YOUR_FILE_ID_2"
                    and dict(exact_defaults_payload.get("extra") or {}).get("parentId") == "dir-exact",
                    "exactProbeUsedMergedValues": len(probe_calls) >= 2
                    and probe_calls[1].get("profileId") == "gy-patch-defaults-2"
                    and probe_calls[1].get("parentId") == "dir-exact"
                    and probe_calls[1].get("fileId") == "YOUR_FILE_ID_2"
                    and probe_calls[1].get("dirName") == "verify-exact-dir"
                    and probe_calls[1].get("pageSize") == 7,
                    "exactProfilePersistedMergedValues": exact_defaults_payload.get("written") is True
                    and dict(exact_defaults_payload.get("extra") or {}).get("fileId") == "YOUR_FILE_ID_2"
                    and dict(exact_defaults_payload.get("extra") or {}).get("parentId") == "dir-exact",
                    "orphanDefaultsSourceApplied": orphan_defaults_payload.get("defaultsSource") == "runtime_orphan:recommendedRefreshEvidenceCommand",
                    "orphanDefaultProfileResolved": orphan_defaults_payload.get("profileId") == "gy-patch-defaults-2",
                    "orphanDefaultAndExplicitSetsMerged": dict(orphan_defaults_payload.get("extra") or {}).get("fileId") == "YOUR_ORPHAN_FILE_ID"
                    and dict(orphan_defaults_payload.get("extra") or {}).get("parentId") == "dir-orphan-exact",
                    "orphanProbeUsedMergedValues": len(probe_calls) == 3
                    and probe_calls[2].get("profileId") == "gy-patch-defaults-2"
                    and probe_calls[2].get("parentId") == "dir-orphan-exact"
                    and probe_calls[2].get("fileId") == "YOUR_ORPHAN_FILE_ID"
                    and probe_calls[2].get("dirName") == "verify-orphan-dir"
                    and probe_calls[2].get("pageSize") == 5,
                    "missingProviderStillNeedsProfileId": missing_profile_id_error == "profile_id_required",
                    "missingExactProfileStillNeedsProfileId": missing_exact_profile_id_error == "profile_id_required",
                    "missingOrphanProfileStillNeedsProfileId": missing_orphan_profile_id_error == "profile_id_required",
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
