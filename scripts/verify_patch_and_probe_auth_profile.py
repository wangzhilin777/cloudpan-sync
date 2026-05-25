from __future__ import annotations

import json
import importlib.util
import io
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
from cloudpan_sync.provider_live_probe_store import list_provider_live_probes
from fastapi.encoders import jsonable_encoder

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
                        "profileId": "gy-patch-probe-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "gy-smoke",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {},
                        "status": "invalid",
                        "lastError": "missing_parent_id",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
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
        probe_calls: list[dict[str, object]] = []

        def fake_validate(profile: object) -> dict[str, object]:
            return {
                "ok": True,
                "profileId": getattr(profile, "profileId", ""),
                "providerKey": getattr(profile, "providerKey", ""),
                "providerDisplayName": getattr(profile, "displayName", ""),
                "mode": "live",
                "status": 200,
                "error": "",
                "summary": "validation ok",
                "checkedAt": "2026-05-23T00:00:00+00:00",
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
                "mode": "live",
                "summary": "probe ok",
                "checks": [
                    {"kind": "list", "ok": True, "status": 200, "error": "", "itemCount": 1, "note": "list ok"},
                    {"kind": "create_dir", "ok": True, "status": 200, "error": "", "createdDirId": "dir-created-1", "note": "create ok"},
                ],
                "parentId": parent_id,
                "fileId": file_id,
                "dirName": dir_name,
                "pageSize": page_size,
            }

        auth_live_validate.validate_profile_object = fake_validate
        provider_live_probe.run_provider_live_probe = fake_probe
        auth_profile_evidence.validate_profile_object = fake_validate
        auth_profile_evidence.run_provider_live_probe = fake_probe
        patch_and_probe_script.validate_profile_object = fake_validate
        patch_and_probe_script.run_provider_live_probe = fake_probe
        patch_and_probe_script.build_real_evidence_remediation_bundle = lambda: {
            "summary": {},
            "items": [
                {
                    "providerKey": "guangya",
                    "profileIds": ["gy-patch-probe-1"],
                    "nextStep": "基础证据补齐后继续补 runtime。",
                    "recommendedRefreshEvidenceCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id gy-patch-probe-1 --write",
                    "recommendedPostRefreshRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-patch-probe-1 --target-parent-id dir-100 --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\guangya-live-evidence",
                    "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider guangya --target-profile-id gy-patch-probe-1 --target-parent-id dir-100 --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\guangya-live-evidence",
                }
            ],
        }
        evidence_path = data_dir / "profile-evidence.md"
        try:
            first_stdout = io.StringIO()
            with redirect_stdout(first_stdout):
                patch_and_probe_script.main(
                    [
                        "--profile-id",
                        "gy-patch-probe-1",
                        "--set",
                        "parentId=dir-100",
                        "--set",
                        "fileId=file-9",
                        "--dir-name",
                        "verify-dir",
                        "--page-size",
                        "7",
                        "--write",
                        "--data-dir",
                        str(data_dir),
                        "--evidence-output",
                        str(evidence_path),
                    ]
                )
            first_payload = json.loads(first_stdout.getvalue())

            second_stdout = io.StringIO()
            with redirect_stdout(second_stdout):
                patch_and_probe_script.main(
                    [
                        "--profile-id",
                        "gy-patch-probe-1",
                        "--write",
                        "--data-dir",
                        str(data_dir),
                    ]
                )
            second_payload = json.loads(second_stdout.getvalue())

            missing_error = ""
            try:
                patch_and_probe_script.main(
                    [
                        "--profile-id",
                        "missing-profile",
                        "--data-dir",
                        str(data_dir),
                    ]
                )
            except SystemExit as exc:
                missing_error = str(exc)
        finally:
            auth_live_validate.validate_profile_object = original_validate
            provider_live_probe.run_provider_live_probe = original_probe
            auth_profile_evidence.validate_profile_object = original_evidence_validate
            auth_profile_evidence.run_provider_live_probe = original_evidence_probe
            patch_and_probe_script.validate_profile_object = original_validate
            patch_and_probe_script.run_provider_live_probe = original_probe
            patch_and_probe_script.build_real_evidence_remediation_bundle = original_remediation_builder

        profiles = json.loads((data_dir / "auth_profiles.json").read_text(encoding="utf-8"))
        validations = json.loads((data_dir / "auth_live_validations.json").read_text(encoding="utf-8"))
        probes = jsonable_encoder(list_provider_live_probes())
        profile = profiles[0]
        probe = probes[0]
        print(
            json.dumps(
                {
                    "profile": {
                        "parentId": profile["extra"].get("parentId", ""),
                        "fileId": profile["extra"].get("fileId", ""),
                        "status": profile["status"],
                    },
                    "validationCount": len(validations),
                    "latestValidationOk": validations[-1]["ok"],
                    "probeCount": len(probes),
                    "latestProbeSummary": probe.get("summary", ""),
                    "latestProbeChecks": [item.get("kind", "") for item in probe.get("checks", [])],
                    "probeCallHasDirNameAndPageSize": len(probe_calls) >= 1
                    and probe_calls[0].get("dirName") == "verify-dir"
                    and probe_calls[0].get("pageSize") == 7
                    and probe_calls[0].get("parentId") == "dir-100"
                    and probe_calls[0].get("fileId") == "file-9",
                    "firstJsonHasOutputAndWriteFlag": first_payload.get("written") is True
                    and first_payload.get("evidenceOutput") == str(evidence_path.resolve())
                    and dict(first_payload.get("validation") or {}).get("summary") == "validation ok"
                    and dict(first_payload.get("probe") or {}).get("summary") == "probe ok"
                    and dict(first_payload.get("remediation") or {}).get("recommendedPostRefreshRuntimeCommand", "").endswith("tmp\\guangya-live-evidence")
                    and dict(first_payload.get("remediation") or {}).get("recommendedOverwriteVariantCommand", "").endswith("tmp\\guangya-live-evidence"),
                    "secondJsonRefreshOnlyStillWrites": second_payload.get("written") is True
                    and dict(second_payload.get("extra") or {}).get("parentId") == "dir-100"
                    and dict(second_payload.get("remediation") or {}).get("nextStep") == "基础证据补齐后继续补 runtime。",
                    "refreshOnlyStillWorked": len(validations) >= 2 and len(probes) >= 1,
                    "evidenceFileExists": evidence_path.exists(),
                    "evidenceHasProfileId": "`gy-patch-probe-1`" in evidence_path.read_text(encoding="utf-8"),
                    "missingProfileRaises": missing_error == "profile_not_found: missing-profile",
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
