from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "export_local_live_adapter_verification.py"
SPEC = importlib.util.spec_from_file_location("export_local_live_adapter_verification", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "guangya": {
            "list_ok": True,
            "metadata_ok": True,
            "create_ok": True,
            "metadata_md5": "0123456789abcdef0123456789abcdef",
        },
        "aliyundrive_open": {
            "list_ok": True,
            "metadata_ok": True,
            "create_ok": True,
            "drive_id": "drive-demo",
        },
        "189cloud": {
            "list_ok": True,
            "metadata_ok": False,
            "create_ok": False,
            "error": "share_auth_readonly",
        },
        "baidu_netdisk": {"list_ok": True, "metadata_ok": True, "create_ok": True, "metadata_md5": "md5-demo"},
        "123_open": {"list_ok": True, "metadata_ok": True, "create_ok": True, "file_id": "123-file"},
        "115_open": {"list_ok": True, "metadata_ok": True, "create_ok": True, "metadata_sha1": "a" * 40},
        "xunlei": {"list_ok": True, "metadata_ok": True, "create_ok": True, "metadata_gcid": "b" * 40},
        "pikpak": {"list_ok": True, "metadata_ok": True, "create_ok": True, "metadata_gcid": "c" * 40},
        "quark": {"list_ok": True, "metadata_ok": True, "create_ok": True, "metadata_md5": "quark-md5"},
        "uc": {"list_ok": True, "metadata_ok": True, "create_ok": True, "metadata_md5": "uc-md5"},
        "probe_and_matrix": {
            "probeChecks": {
                "guangya": 3,
                "aliyundrive_open": 3,
                "189cloud": 2,
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
                    "metadata_ready": False,
                    "create_dir_ready": False,
                    "live_probe_ok": False,
                },
            },
        },
    }

    original_root = export_script.ROOT
    original_build_payload = export_script.build_payload

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.build_payload = lambda: synthetic_payload
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.build_payload = original_build_payload

        output_path = tmp_root / "docs" / "07-LOCAL_LIVE_ADAPTER_VERIFICATION.md"
        markdown = output_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "exportedFileExists": True,
                "exportedHasTitleAndNotes": "# CloudPan Sync Local Live Adapter Verification" in markdown
                and "> 本报告来自 `scripts/verify_provider_live_adapters.py` 的本地可控 stub 验证。" in markdown
                and "> 它证明当前工作树里的适配器逻辑和聚合逻辑可跑通，但不等同于真实网盘在线成功。" in markdown,
                "exportedHasProviderSections": "## guangya" in markdown
                and "- list_ok: `True`" in markdown
                and "- metadata_md5: `0123456789abcdef0123456789abcdef`" in markdown
                and "## 189cloud" in markdown
                and "- metadata_ok: `False`" in markdown
                and "- error: `share_auth_readonly`" in markdown,
                "exportedHasProbeChecks": "## Probe Checks" in markdown
                and "- guangya: `3`" in markdown
                and "- aliyundrive_open: `3`" in markdown
                and "- 189cloud: `2`" in markdown,
                "exportedHasMatrixRows": "## Matrix Rows" in markdown
                and "- guangya: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`" in markdown
                and "- 189cloud: `list_ready=True` `metadata_ready=False` `create_dir_ready=False` `live_probe_ok=False`" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
