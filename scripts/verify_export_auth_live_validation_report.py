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

SCRIPT_PATH = ROOT / "scripts" / "export_auth_live_validation_report.py"
SPEC = importlib.util.spec_from_file_location("export_auth_live_validation_report", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    all_rows = [
        {
            "providerKey": "guangya",
            "providerDisplayName": "Guangya",
            "checkedAt": "2026-05-25T01:00:00+00:00",
            "ok": True,
            "status": 200,
            "mode": "cookie_refresh",
            "summary": "cookie refresh succeeded",
            "error": "",
            "endpointUrl": "https://api.guangya.example/list",
            "finalUrl": "https://api.guangya.example/list",
            "checks": [{"kind": "list"}],
        },
        {
            "providerKey": "189cloud",
            "providerDisplayName": "Tianyi 189Cloud",
            "checkedAt": "2026-05-25T02:00:00+00:00",
            "ok": False,
            "status": 403,
            "mode": "share_probe",
            "summary": "share profile readonly",
            "error": "share_auth_readonly",
            "parentId": "share-parent",
            "fileId": "share-file",
            "endpointUrl": "https://open.189.example/share",
            "finalUrl": "https://open.189.example/share",
            "checks": [{"kind": "create_dir"}, {"kind": "list"}],
        },
    ]
    latest_rows = [all_rows[0], all_rows[1]]
    summary = {
        "profileCount": 2,
        "okCount": 1,
        "failedCount": 1,
        "okProfiles": ["Guangya"],
        "failedProfiles": ["Tianyi 189Cloud"],
        "providerKeys": ["guangya", "189cloud"],
    }

    original_root = export_script.ROOT
    original_list = export_script.list_live_validations
    original_latest = export_script.latest_live_validations
    original_summary = export_script.live_validation_summary

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.list_live_validations = lambda: all_rows
        export_script.latest_live_validations = lambda: latest_rows
        export_script.live_validation_summary = lambda: summary
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.list_live_validations = original_list
            export_script.latest_live_validations = original_latest
            export_script.live_validation_summary = original_summary

        output_path = tmp_root / "docs" / "03-AUTH_LIVE_VALIDATION_REPORT.md"
        markdown = output_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "exportedFileExists": True,
                "exportedHasTitle": "# CloudPan Sync Auth Live Validation Report" in markdown,
                "exportedHasSummary": "- totalRecords: `2`" in markdown
                and "- latestProfileCount: `2`" in markdown
                and "- latestOkCount: `1`" in markdown
                and "- latestFailedCount: `1`" in markdown
                and "- latestProviders: `guangya, 189cloud`" in markdown
                and "- latestProfiles: `ok=Guangya` `failed=Tianyi 189Cloud`" in markdown,
                "exportedHasLatestRows": "## Latest By Profile" in markdown
                and "### guangya - Guangya" in markdown
                and "- mode: `cookie_refresh`" in markdown
                and "- summary: `cookie refresh succeeded`" in markdown
                and "### 189cloud - Tianyi 189Cloud" in markdown
                and "- error: `share_auth_readonly`" in markdown,
                "exportedHasRecentHistoryRows": "## Recent History" in markdown
                and "- probeArgs: `parentId=share-parent` `fileId=share-file`" in markdown
                and "- endpoint: `https://open.189.example/share`" in markdown
                and "- finalUrl: `https://open.189.example/share`" in markdown
                and "- checkCount: `2`" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
