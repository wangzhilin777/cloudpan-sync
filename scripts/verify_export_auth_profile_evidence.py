from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SCRIPT_PATH = ROOT / "scripts" / "export_auth_profile_evidence.py"
SPEC = importlib.util.spec_from_file_location("export_auth_profile_evidence", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


class FakeProfile:
    def __init__(self, profile_id: str, provider_key: str) -> None:
        self.profileId = profile_id
        self.providerKey = provider_key


def main() -> None:
    configured_dirs: list[str] = []
    fake_profile = FakeProfile("189-share", "189cloud")

    original_configure = export_script.configure_data_dir
    original_get_profile = export_script.get_profile
    original_build_payload = export_script._auth_profile_evidence
    original_renderer = export_script.auth_profile_evidence_to_markdown

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        output_path = tmp_root / "auth-profile-evidence.md"
        data_dir = tmp_root / ".cloudpan_sync_data"

        export_script.configure_data_dir = lambda path: configured_dirs.append(str(path))
        export_script.get_profile = lambda profile_id: fake_profile if profile_id == "189-share" else None
        export_script._auth_profile_evidence = lambda profile: {
            "profile": {
                "profileId": profile.profileId,
                "providerKey": profile.providerKey,
                "displayName": "189 Share Profile",
                "missingFieldHints": ["accessToken"],
                "placeholderSecretFieldHints": ["token"],
                "liveRejectedProfiles": ["189 Share Profile"],
                "placeholderLiveRejectedProfiles": ["189 Share Profile"],
                "liveRejectedStatuses": ["403"],
                "liveRejectedSummaries": ["189 Share Profile:403"],
                "writeMissingFieldHints": ["signature", "date"],
                "writeBlockerNote": "当前 189Cloud share 档案仍为只读。",
            },
            "summary": {
                "profileReady": False,
                "writeReady": False,
                "validationOk": False,
                "probeOk": False,
                "resolvedParentId": "share-parent",
                "resolvedFileId": "",
            },
            "latestValidation": {
                "ok": False,
                "mode": "share_probe",
                "status": 403,
                "error": "share_auth_readonly",
                "summary": "share auth readonly",
                "checkedAt": "2026-05-25T03:00:00+00:00",
            },
            "latestProbe": {
                "ok": False,
                "mode": "create_dir_probe",
                "summary": "create_dir probe blocked by readonly auth",
                "checks": [
                    {
                        "kind": "create_dir",
                        "ok": False,
                        "status": 403,
                        "error": "share_auth_readonly",
                        "note": "share profile readonly",
                    }
                ],
            },
        }

        try:
            exit_code = export_script.main(
                [
                    "--profile-id",
                    "189-share",
                    "--data-dir",
                    str(data_dir),
                    "--output",
                    str(output_path),
                ]
            )
            markdown = output_path.read_text(encoding="utf-8")

            not_found_error = ""
            try:
                export_script.main(["--profile-id", "missing-profile"])
            except SystemExit as exc:
                not_found_error = str(exc)
        finally:
            export_script.configure_data_dir = original_configure
            export_script.get_profile = original_get_profile
            export_script._auth_profile_evidence = original_build_payload
            export_script.auth_profile_evidence_to_markdown = original_renderer
    main_returned_zero = exit_code == 0
    configured_data_dir = configured_dirs == [str(data_dir)]
    exported_has_title = "# Auth Profile Evidence" in markdown
    exported_has_profile_summary = (
        "- profileId: `189-share`" in markdown
        and "- providerKey: `189cloud`" in markdown
        and "- displayName: `189 Share Profile`" in markdown
        and "- resolvedParentId: `share-parent`" in markdown
    )
    exported_has_readonly_details = (
        "- missingFieldHints: `accessToken`" in markdown
        and "- placeholderSecretFieldHints: `token`" in markdown
        and "- liveRejected: profiles=`189 Share Profile` placeholderProfiles=`189 Share Profile` statuses=`403`" in markdown
        and "- liveRejectedSummaries: `189 Share Profile:403`" in markdown
        and "- writeMissingFieldHints: `signature, date`" in markdown
        and "- writeBlockerNote: 当前 189Cloud share 档案仍为只读。" in markdown
    )
    exported_has_validation_and_probe = (
        "## Latest Validation" in markdown
        and "- error: `share_auth_readonly`" in markdown
        and "## Latest Probe" in markdown
        and "  - `create_dir` ok=False status=403 error=share_auth_readonly note=share profile readonly" in markdown
    )
    missing_profile_raises = not_found_error == "profile_not_found: missing-profile"
    export_auth_profile_evidence_flow_matches_expected_markdown = (
        main_returned_zero
        and configured_data_dir
        and exported_has_title
        and exported_has_profile_summary
        and exported_has_readonly_details
        and exported_has_validation_and_probe
        and missing_profile_raises
    )

    print(
        json.dumps(
            {
                "mainReturnedZero": main_returned_zero,
                "configuredDataDir": configured_data_dir,
                "exportedHasTitle": exported_has_title,
                "exportedHasProfileSummary": exported_has_profile_summary,
                "exportedHasReadonlyDetails": exported_has_readonly_details,
                "exportedHasValidationAndProbe": exported_has_validation_and_probe,
                "missingProfileRaises": missing_profile_raises,
                "exportAuthProfileEvidenceFlowMatchesExpectedMarkdown": export_auth_profile_evidence_flow_matches_expected_markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
