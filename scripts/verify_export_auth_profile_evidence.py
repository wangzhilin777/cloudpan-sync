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

    print(
        json.dumps(
            {
                "mainReturnedZero": exit_code == 0,
                "configuredDataDir": configured_dirs == [str(data_dir)],
                "exportedHasTitle": "# Auth Profile Evidence" in markdown,
                "exportedHasProfileSummary": "- profileId: `189-share`" in markdown
                and "- providerKey: `189cloud`" in markdown
                and "- displayName: `189 Share Profile`" in markdown
                and "- resolvedParentId: `share-parent`" in markdown,
                "exportedHasReadonlyDetails": "- missingFieldHints: `accessToken`" in markdown
                and "- writeMissingFieldHints: `signature, date`" in markdown
                and "- writeBlockerNote: 当前 189Cloud share 档案仍为只读。" in markdown,
                "exportedHasValidationAndProbe": "## Latest Validation" in markdown
                and "- error: `share_auth_readonly`" in markdown
                and "## Latest Probe" in markdown
                and "  - `create_dir` ok=False status=403 error=share_auth_readonly note=share profile readonly" in markdown,
                "missingProfileRaises": not_found_error == "profile_not_found: missing-profile",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
