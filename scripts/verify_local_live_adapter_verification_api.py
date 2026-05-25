from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import local_live_adapter_verification, webapp


def main() -> None:
    original_password = webapp.ADMIN_PASSWORD
    originals = {
        "verify_guangya": local_live_adapter_verification.verify_guangya,
        "verify_aliyun_open": local_live_adapter_verification.verify_aliyun_open,
        "verify_189cloud": local_live_adapter_verification.verify_189cloud,
        "verify_baidu": local_live_adapter_verification.verify_baidu,
        "verify_123_open": local_live_adapter_verification.verify_123_open,
        "verify_115_open": local_live_adapter_verification.verify_115_open,
        "verify_xunlei": local_live_adapter_verification.verify_xunlei,
        "verify_pikpak": local_live_adapter_verification.verify_pikpak,
        "verify_quark": local_live_adapter_verification.verify_quark,
        "verify_uc": local_live_adapter_verification.verify_uc,
        "verify_probe_and_matrix": local_live_adapter_verification.verify_probe_and_matrix,
    }
    try:
        webapp.ADMIN_PASSWORD = "admin123"
        local_live_adapter_verification.verify_guangya = lambda: {
            "list_ok": True,
            "metadata_ok": True,
            "create_ok": True,
            "metadata_md5": "0123456789abcdef0123456789abcdef",
            "metadata_gcid": "a" * 40,
        }
        local_live_adapter_verification.verify_aliyun_open = lambda: {
            "list_ok": True,
            "metadata_ok": True,
            "create_ok": True,
            "metadata_md5": "fedcba9876543210fedcba9876543210",
        }
        local_live_adapter_verification.verify_189cloud = lambda: {
            "list_ok": True,
            "metadata_ok": True,
            "create_ok": True,
            "create_mode": "live_account_auth",
            "create_file_id": "dir-189-1",
            "metadata_md5": "11111111111111111111111111111111",
        }
        local_live_adapter_verification.verify_baidu = lambda: {"list_ok": True, "metadata_ok": True, "create_ok": True}
        local_live_adapter_verification.verify_123_open = lambda: {"list_ok": True, "metadata_ok": True, "create_ok": True}
        local_live_adapter_verification.verify_115_open = lambda: {"list_ok": True, "metadata_ok": True, "create_ok": True}
        local_live_adapter_verification.verify_xunlei = lambda: {"list_ok": True, "metadata_ok": True, "create_ok": True}
        local_live_adapter_verification.verify_pikpak = lambda: {"list_ok": True, "metadata_ok": True, "create_ok": True}
        local_live_adapter_verification.verify_quark = lambda: {"list_ok": True, "metadata_ok": True, "create_ok": True}
        local_live_adapter_verification.verify_uc = lambda: {"list_ok": True, "metadata_ok": True, "create_ok": True}
        local_live_adapter_verification.verify_probe_and_matrix = lambda: {
            "probeChecks": {provider: 3 for provider in local_live_adapter_verification.PROVIDERS},
            "matrixRows": {
                provider: {
                    "list_ready": True,
                    "metadata_ready": True,
                    "create_dir_ready": True,
                    "live_probe_ok": True,
                }
                for provider in local_live_adapter_verification.PROVIDERS
            },
        }

        payload = local_live_adapter_verification.build_local_live_adapter_verification()
        markdown = local_live_adapter_verification.local_live_adapter_verification_to_markdown(payload)

        app = webapp.create_app()
        client = TestClient(app)
        login = client.post("/api/login", json={"password": "admin123"})
        assert login.status_code == 200, login.text
        api_payload = client.get("/api/local_live_adapter_verification").json()
        api_markdown = client.get("/api/local_live_adapter_verification_markdown").json()

        print(
            json.dumps(
                {
                    "summaryProviderCount": (payload.get("summary") or {}).get("providerCount"),
                    "payloadHasItems": len(payload.get("items") or []) == 10,
                    "payloadHasCreateModeSummary": "189cloud=live_account_auth" in ((payload.get("summary") or {}).get("accountCreateModeProviders") or []),
                    "markdownHasTitle": "# CloudPan Sync Local Live Adapter Verification" in markdown,
                    "markdownHasProviderSummary": "providerSummary: `all_ok=guangya, aliyundrive_open, 189cloud, baidu_netdisk, 123_open, 115_open, xunlei, pikpak, quark, uc`" in markdown,
                    "markdownHas189CreateMode": "- create_mode: `live_account_auth`" in markdown and "- create_file_id: `dir-189-1`" in markdown,
                    "apiSummaryProviderCount": (api_payload.get("summary") or {}).get("providerCount"),
                    "apiHasItems": len(api_payload.get("items") or []) == 10,
                    "apiMarkdownHasTitle": "# CloudPan Sync Local Live Adapter Verification" in str(api_markdown.get("markdown") or ""),
                    "apiMarkdownHasMatrixRow": "- guangya: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`" in str(api_markdown.get("markdown") or ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        webapp.ADMIN_PASSWORD = original_password
        for name, value in originals.items():
            setattr(local_live_adapter_verification, name, value)


if __name__ == "__main__":
    main()
