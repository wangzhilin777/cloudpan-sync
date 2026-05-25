from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.verify_provider_live_adapters import verify_189cloud
from scripts.verify_provider_live_adapters import verify_115_open
from scripts.verify_provider_live_adapters import verify_123_open
from scripts.verify_provider_live_adapters import verify_aliyun_open
from scripts.verify_provider_live_adapters import verify_baidu
from scripts.verify_provider_live_adapters import verify_guangya
from scripts.verify_provider_live_adapters import verify_pikpak
from scripts.verify_provider_live_adapters import verify_probe_and_matrix
from scripts.verify_provider_live_adapters import verify_quark
from scripts.verify_provider_live_adapters import verify_uc
from scripts.verify_provider_live_adapters import verify_xunlei


PROVIDERS = (
    "guangya",
    "aliyundrive_open",
    "189cloud",
    "baidu_netdisk",
    "123_open",
    "115_open",
    "xunlei",
    "pikpak",
    "quark",
    "uc",
)


def build_local_live_adapter_verification() -> dict[str, object]:
    payload = {
        "guangya": verify_guangya(),
        "aliyundrive_open": verify_aliyun_open(),
        "189cloud": verify_189cloud(),
        "baidu_netdisk": verify_baidu(),
        "123_open": verify_123_open(),
        "115_open": verify_115_open(),
        "xunlei": verify_xunlei(),
        "pikpak": verify_pikpak(),
        "quark": verify_quark(),
        "uc": verify_uc(),
        "probe_and_matrix": verify_probe_and_matrix(),
    }
    probe_matrix = dict(payload.get("probe_and_matrix") or {})
    probe_checks = dict(probe_matrix.get("probeChecks") or {})
    matrix_rows = dict(probe_matrix.get("matrixRows") or {})
    payload["summary"] = {
        "providerCount": len(PROVIDERS),
        "allOkProviders": [provider for provider in PROVIDERS if all(bool((payload.get(provider) or {}).get(key)) for key in ("list_ok", "metadata_ok", "create_ok"))],
        "md5ReadyProviders": [provider for provider in PROVIDERS if str((payload.get(provider) or {}).get("metadata_md5") or "")],
        "gcidReadyProviders": [provider for provider in PROVIDERS if str((payload.get(provider) or {}).get("metadata_gcid") or "")],
        "probeCheckReadyProviders": [provider for provider in PROVIDERS if int(probe_checks.get(provider, 0) or 0) == 3],
        "matrixReadyProviders": [
            provider
            for provider in PROVIDERS
            if bool((matrix_rows.get(provider) or {}).get("list_ready"))
            and bool((matrix_rows.get(provider) or {}).get("metadata_ready"))
            and bool((matrix_rows.get(provider) or {}).get("create_dir_ready"))
            and bool((matrix_rows.get(provider) or {}).get("live_probe_ok"))
        ],
        "accountCreateModeProviders": [
            f"{provider}={str((payload.get(provider) or {}).get('create_mode') or '')}"
            for provider in PROVIDERS
            if str((payload.get(provider) or {}).get("create_mode") or "")
        ],
    }
    payload["items"] = [
        {
            "providerKey": provider,
            **dict(payload.get(provider) or {}),
            "probeChecksReady": int(probe_checks.get(provider, 0) or 0),
            "matrixRow": dict(matrix_rows.get(provider) or {}),
        }
        for provider in PROVIDERS
    ]
    return payload


def local_live_adapter_verification_to_markdown(payload: dict[str, object]) -> str:
    lines: list[str] = []
    summary = dict(payload.get("summary") or {})
    lines.append("# CloudPan Sync Local Live Adapter Verification")
    lines.append("")
    lines.append("> 本报告来自 `scripts/verify_provider_live_adapters.py` 的本地可控 stub 验证。")
    lines.append("> 它证明当前工作树里的适配器逻辑和聚合逻辑可跑通，但不等同于真实网盘在线成功。")
    lines.append("")
    lines.append(f"- providerCount: `{summary.get('providerCount', 0)}`")
    lines.append(
        f"- providerSummary: `all_ok={', '.join(summary.get('allOkProviders', [])) or '(none)'}` "
        f"`md5_ready={', '.join(summary.get('md5ReadyProviders', [])) or '(none)'}` "
        f"`gcid_ready={', '.join(summary.get('gcidReadyProviders', [])) or '(none)'}` "
        f"`probe_ready={', '.join(summary.get('probeCheckReadyProviders', [])) or '(none)'}` "
        f"`matrix_ready={', '.join(summary.get('matrixReadyProviders', [])) or '(none)'}` "
        f"`account_create_mode={', '.join(summary.get('accountCreateModeProviders', [])) or '(none)'}`"
    )
    lines.append("")

    for provider_key in PROVIDERS:
        row = dict(payload.get(provider_key) or {})
        lines.append(f"## {provider_key}")
        for key, value in row.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")

    probe_matrix = dict(payload.get("probe_and_matrix") or {})
    probe_checks = dict(probe_matrix.get("probeChecks") or {})
    matrix_rows = dict(probe_matrix.get("matrixRows") or {})

    lines.append("## Probe Checks")
    for provider_key, value in probe_checks.items():
        lines.append(f"- {provider_key}: `{value}`")
    lines.append("")

    lines.append("## Matrix Rows")
    for provider_key, row in matrix_rows.items():
        item = dict(row or {})
        lines.append(
            f"- {provider_key}: `list_ready={item.get('list_ready', False)}` `metadata_ready={item.get('metadata_ready', False)}` `create_dir_ready={item.get('create_dir_ready', False)}` `live_probe_ok={item.get('live_probe_ok', False)}`"
        )
    lines.append("")
    return "\n".join(lines).strip() + "\n"
