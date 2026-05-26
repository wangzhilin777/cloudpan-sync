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

from cloudpan_sync.live_probe import probe_to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_live_probe_report.py"
SPEC = importlib.util.spec_from_file_location("export_live_probe_report", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "generatedAt": "2026-05-25T00:00:00+00:00",
        "summary": {
            "providerCount": 3,
            "totalChecks": 4,
            "okChecks": 2,
            "failedChecks": 2,
            "profileProbeProviderCount": 2,
            "profileProbeOkCount": 1,
            "profileProbeFailedCount": 1,
            "profileProbeOkProfiles": ["gy-1"],
            "profileProbeFailedProfiles": ["189-1"],
            "profileProbeOkProviders": ["guangya"],
            "profileProbeFailedProviders": ["189cloud"],
            "profileProbeFailedModes": ["share_probe"],
        },
        "items": [
            {
                "providerKey": "guangya",
                "displayName": "Guangya",
                "checks": [
                    {
                        "kind": "official_docs",
                        "ok": True,
                        "status": 200,
                        "url": "https://docs.guangya.example",
                        "finalUrl": "https://docs.guangya.example",
                        "error": "",
                    },
                    {
                        "kind": "web_login",
                        "ok": False,
                        "status": 403,
                        "url": "https://login.guangya.example",
                        "finalUrl": "https://login.guangya.example/blocked",
                        "error": "http_error:403",
                    },
                ],
                "profileProbe": {
                    "ok": True,
                    "mode": "cookie_refresh",
                    "summary": "2 checks passed",
                    "checkCount": 2,
                },
            },
            {
                "providerKey": "189cloud",
                "displayName": "Tianyi 189Cloud",
                "checks": [
                    {
                        "kind": "official_docs",
                        "ok": False,
                        "status": 0,
                        "url": "https://open.189.cn",
                        "finalUrl": "https://open.189.cn",
                        "error": "url_error:timed out",
                    }
                ],
                "profileProbe": {
                    "ok": False,
                    "mode": "share_probe",
                    "summary": "share profile is readonly",
                    "checkCount": 1,
                },
            },
            {
                "providerKey": "115_open",
                "displayName": "115 Open",
                "checks": [
                    {
                        "kind": "web_login",
                        "ok": True,
                        "status": 302,
                        "url": "https://115.example/login",
                        "finalUrl": "https://115.example/home",
                        "error": "",
                    }
                ],
                "profileProbe": {
                    "ok": False,
                    "mode": "",
                    "summary": "",
                    "checkCount": 0,
                },
            },
        ],
    }

    original_root = export_script.ROOT
    original_runner = export_script.run_live_probe
    original_renderer = export_script.probe_to_markdown

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.run_live_probe = lambda: synthetic_payload
        export_script.probe_to_markdown = probe_to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.run_live_probe = original_runner
            export_script.probe_to_markdown = original_renderer

        output_path = tmp_root / "docs" / "05-PROVIDER_LIVE_PROBE_REPORT.md"
        markdown = output_path.read_text(encoding="utf-8")
    exported_file_exists = True
    exported_has_title = "# CloudPan Sync Provider Live Probe Report" in markdown
    exported_has_summary_counts = (
        "providerCount=3" in markdown
        and "totalChecks=4" in markdown
        and "okChecks=2" in markdown
        and "failedChecks=2" in markdown
        and "profileProbeProviderCount=2" in markdown
        and "profileProbeOkCount=1" in markdown
        and "profileProbeFailedCount=1" in markdown
        and "- profileProbeProfiles: `ok=gy-1` `failed=189-1`" in markdown
        and "- profileProbeProviderSummary: `ok_providers=guangya` `failed_providers=189cloud` `failed_modes=share_probe`" in markdown
    )
    exported_has_guangya_rows = (
        "## guangya - Guangya" in markdown
        and "- official_docs: ok=True status=200 url=https://docs.guangya.example final=https://docs.guangya.example error=" in markdown
        and "- web_login: ok=False status=403 url=https://login.guangya.example final=https://login.guangya.example/blocked error=http_error:403" in markdown
    )
    exported_has_profile_probe_rows = (
        "- profile_probe: ok=True mode=cookie_refresh checks=2 summary=2 checks passed" in markdown
        and "- profile_probe: ok=False mode=share_probe checks=1 summary=share profile is readonly" in markdown
    )
    exported_has_no_empty_profile_probe_row = (
        "## 115_open - 115 Open" in markdown
        and "- web_login: ok=True status=302 url=https://115.example/login final=https://115.example/home error=" in markdown
        and "checks=0 summary=" not in markdown
    )
    export_live_probe_report_flow_matches_expected_markdown = (
        exported_file_exists
        and exported_has_title
        and exported_has_summary_counts
        and exported_has_guangya_rows
        and exported_has_profile_probe_rows
        and exported_has_no_empty_profile_probe_row
    )

    print(
        json.dumps(
            {
                "exportedFileExists": exported_file_exists,
                "exportedHasTitle": exported_has_title,
                "exportedHasSummaryCounts": exported_has_summary_counts,
                "exportedHasGuangyaRows": exported_has_guangya_rows,
                "exportedHasProfileProbeRows": exported_has_profile_probe_rows,
                "exportedHasNoEmptyProfileProbeRow": exported_has_no_empty_profile_probe_row,
                "exportLiveProbeReportFlowMatchesExpectedMarkdown": export_live_probe_report_flow_matches_expected_markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
