from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_live_validate import latest_live_validations, list_live_validations, live_validation_summary


def main() -> None:
    out = ROOT / "docs" / "03-AUTH_LIVE_VALIDATION_REPORT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = list_live_validations()
    latest_rows = latest_live_validations()
    summary = live_validation_summary()
    lines: list[str] = []
    lines.append("# CloudPan Sync Auth Live Validation Report")
    lines.append("")
    lines.append(f"- totalRecords: `{len(rows)}`")
    lines.append(f"- latestProfileCount: `{summary.get('profileCount', 0)}`")
    lines.append(f"- latestOkCount: `{summary.get('okCount', 0)}`")
    lines.append(f"- latestFailedCount: `{summary.get('failedCount', 0)}`")
    lines.append(f"- latestProviders: `{', '.join(summary.get('providerKeys', [])) or '(none)'}`")
    lines.append("")
    lines.append("## Latest By Profile")
    lines.append("")
    for row in latest_rows:
        lines.append(f"### {row.get('providerKey', '')} - {row.get('providerDisplayName', '')}")
        lines.append(f"- checkedAt: `{row.get('checkedAt', '')}`")
        lines.append(f"- ok: `{row.get('ok', False)}` status: `{row.get('status', 0)}`")
        if row.get("mode"):
            lines.append(f"- mode: `{row.get('mode', '')}`")
        if row.get("summary"):
            lines.append(f"- summary: `{row.get('summary', '')}`")
        lines.append(f"- error: `{row.get('error', '')}`")
        lines.append("")

    lines.append("## Recent History")
    lines.append("")
    for row in rows[-100:]:
        lines.append(f"### {row.get('providerKey', '')} - {row.get('providerDisplayName', '')}")
        lines.append(f"- checkedAt: `{row.get('checkedAt', '')}`")
        lines.append(f"- ok: `{row.get('ok', False)}` status: `{row.get('status', 0)}`")
        if row.get("mode"):
            lines.append(f"- mode: `{row.get('mode', '')}`")
        if row.get("parentId") or row.get("fileId"):
            lines.append(f"- probeArgs: `parentId={row.get('parentId', '')}` `fileId={row.get('fileId', '')}`")
        if row.get("summary"):
            lines.append(f"- summary: `{row.get('summary', '')}`")
        if row.get("endpointUrl"):
            lines.append(f"- endpoint: `{row.get('endpointUrl', '')}`")
        if row.get("finalUrl"):
            lines.append(f"- finalUrl: `{row.get('finalUrl', '')}`")
        lines.append(f"- error: `{row.get('error', '')}`")
        checks = row.get("checks") or []
        if isinstance(checks, list) and checks:
            lines.append(f"- checkCount: `{len(checks)}`")
        lines.append("")
    out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
