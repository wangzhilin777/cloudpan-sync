from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
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


def build_payload() -> dict[str, object]:
    return {
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


def to_markdown(payload: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("# CloudPan Sync Local Live Adapter Verification")
    lines.append("")
    lines.append("> 本报告来自 `scripts/verify_provider_live_adapters.py` 的本地可控 stub 验证。")
    lines.append("> 它证明当前工作树里的适配器逻辑和聚合逻辑可跑通，但不等同于真实网盘在线成功。")
    lines.append("")

    for provider_key in ("guangya", "aliyundrive_open", "189cloud", "baidu_netdisk", "123_open", "115_open", "xunlei", "pikpak", "quark", "uc"):
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


def main() -> None:
    out = ROOT / "docs" / "07-LOCAL_LIVE_ADAPTER_VERIFICATION.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    out.write_text(to_markdown(payload), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
