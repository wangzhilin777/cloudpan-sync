from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.export_local_live_adapter_verification import to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_local_live_adapter_verification.py"
SPEC = importlib.util.spec_from_file_location("export_local_live_adapter_verification", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "summary": {
            "providerCount": 2,
            "allOkProviders": ["guangya", "189cloud"],
            "md5ReadyProviders": ["guangya", "189cloud"],
            "gcidReadyProviders": ["guangya"],
            "probeCheckReadyProviders": ["guangya", "189cloud"],
            "matrixReadyProviders": ["guangya", "189cloud"],
            "accountCreateModeProviders": ["189cloud=live_account_auth"],
        },
        "guangya": {
            "list_ok": True,
            "metadata_ok": True,
            "create_ok": True,
            "metadata_md5": "0123456789abcdef0123456789abcdef",
            "metadata_gcid": "a" * 40,
        },
        "189cloud": {
            "list_ok": True,
            "metadata_ok": True,
            "create_ok": True,
            "create_mode": "live_account_auth",
            "create_file_id": "dir-189-1",
            "metadata_md5": "0123456789abcdef0123456789abcdef",
        },
        "probe_and_matrix": {
            "probeChecks": {
                "guangya": 3,
                "189cloud": 3,
            },
            "matrixRows": {
                "guangya": {
                    "list_ready": True,
                    "metadata_ready": True,
                    "create_dir_ready": True,
                    "live_probe_ok": True,
                },
                "189cloud": {
                    "list_ready": True,
                    "metadata_ready": True,
                    "create_dir_ready": True,
                    "live_probe_ok": True,
                },
            },
        },
    }

    original_root = export_script.ROOT
    original_builder = export_script.build_payload
    original_renderer = export_script.to_markdown

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.build_payload = lambda: synthetic_payload
        export_script.to_markdown = to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.build_payload = original_builder
            export_script.to_markdown = original_renderer

        output_path = tmp_root / "docs" / "07-LOCAL_LIVE_ADAPTER_VERIFICATION.md"
        markdown = output_path.read_text(encoding="utf-8")
    exported_file_exists = True
    exported_has_title = "# CloudPan Sync Local Live Adapter Verification" in markdown
    exported_has_provider_summary = "- providerSummary: `all_ok=guangya, 189cloud` `md5_ready=guangya, 189cloud` `gcid_ready=guangya` `probe_ready=guangya, 189cloud` `matrix_ready=guangya, 189cloud` `account_create_mode=189cloud=live_account_auth`" in markdown
    exported_has_guangya_section = "## guangya" in markdown and "- metadata_gcid: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`" in markdown
    exported_has_189_section = "## 189cloud" in markdown and "- create_mode: `live_account_auth`" in markdown and "- create_file_id: `dir-189-1`" in markdown
    exported_has_probe_checks = "- guangya: `3`" in markdown and "- 189cloud: `3`" in markdown
    exported_has_matrix_rows = "- guangya: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`" in markdown and "- 189cloud: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`" in markdown
    export_local_live_adapter_verification_flow_matches_expected_markdown = (
        exported_file_exists
        and exported_has_title
        and exported_has_provider_summary
        and exported_has_guangya_section
        and exported_has_189_section
        and exported_has_probe_checks
        and exported_has_matrix_rows
    )

    print(
        json.dumps(
            {
                "exportedFileExists": exported_file_exists,
                "exportedHasTitle": exported_has_title,
                "exportedHasProviderSummary": exported_has_provider_summary,
                "exportedHasGuangyaSection": exported_has_guangya_section,
                "exportedHas189Section": exported_has_189_section,
                "exportedHasProbeChecks": exported_has_probe_checks,
                "exportedHasMatrixRows": exported_has_matrix_rows,
                "exportLocalLiveAdapterVerificationFlowMatchesExpectedMarkdown": export_local_live_adapter_verification_flow_matches_expected_markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
