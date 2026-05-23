from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_live_validate import list_live_validations


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "docs" / "AUTH_LIVE_VALIDATION_REPORT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = list_live_validations()
    lines: list[str] = []
    lines.append("# CloudPan Sync Auth Live Validation Report")
    lines.append("")
    lines.append(f"- totalRecords: `{len(rows)}`")
    lines.append("")
    for row in rows[-100:]:
        lines.append(f"## {row.get('providerKey', '')} - {row.get('providerDisplayName', '')}")
        lines.append(f"- checkedAt: `{row.get('checkedAt', '')}`")
        lines.append(f"- ok: `{row.get('ok', False)}` status: `{row.get('status', 0)}`")
        lines.append(f"- endpoint: `{row.get('endpointUrl', '')}`")
        lines.append(f"- finalUrl: `{row.get('finalUrl', '')}`")
        lines.append(f"- error: `{row.get('error', '')}`")
        lines.append("")
    out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
