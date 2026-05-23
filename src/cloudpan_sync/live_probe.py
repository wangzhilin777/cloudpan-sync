from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .provider_research import build_provider_research_index


@dataclass
class ProbeResult:
    kind: str
    url: str
    ok: bool
    status: int
    finalUrl: str
    error: str

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "url": self.url,
            "ok": self.ok,
            "status": self.status,
            "finalUrl": self.finalUrl,
            "error": self.error,
        }


def _probe_url(kind: str, url: str, timeout_sec: int = 8) -> ProbeResult:
    if not url:
        return ProbeResult(kind=kind, url="", ok=False, status=0, finalUrl="", error="empty_url")
    req = Request(
        url=url,
        headers={
            "User-Agent": "CloudPanSyncProbe/1.0",
            "Accept": "text/html,application/json,*/*",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=timeout_sec) as resp:
            status = int(getattr(resp, "status", 0) or 0)
            final_url = str(getattr(resp, "url", "") or "")
            return ProbeResult(
                kind=kind,
                url=url,
                ok=200 <= status < 400,
                status=status,
                finalUrl=final_url,
                error="",
            )
    except HTTPError as exc:
        return ProbeResult(
            kind=kind,
            url=url,
            ok=False,
            status=int(exc.code or 0),
            finalUrl=url,
            error=f"http_error:{exc.code}",
        )
    except URLError as exc:
        return ProbeResult(
            kind=kind,
            url=url,
            ok=False,
            status=0,
            finalUrl=url,
            error=f"url_error:{exc.reason}",
        )
    except Exception as exc:  # pragma: no cover
        return ProbeResult(
            kind=kind,
            url=url,
            ok=False,
            status=0,
            finalUrl=url,
            error=f"unexpected:{exc}",
        )


def run_live_probe() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    research = build_provider_research_index()
    ok_checks = 0
    total_checks = 0
    for provider in research:
        provider_key = str(provider.get("providerKey") or "")
        display_name = str(provider.get("displayName") or provider_key)
        docs_url = str(provider.get("officialDocsUrl") or "")
        login_url = str(provider.get("webLoginUrl") or "")
        checks: list[ProbeResult] = []
        if docs_url:
            checks.append(_probe_url("official_docs", docs_url))
        if login_url:
            checks.append(_probe_url("web_login", login_url))
        total_checks += len(checks)
        ok_checks += sum(1 for c in checks if c.ok)
        rows.append(
            {
                "providerKey": provider_key,
                "displayName": display_name,
                "checks": [c.to_dict() for c in checks],
            }
        )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "providerCount": len(research),
            "totalChecks": total_checks,
            "okChecks": ok_checks,
            "failedChecks": max(0, total_checks - ok_checks),
        },
        "items": rows,
    }


def probe_to_markdown(payload: dict[str, object]) -> str:
    summary = dict(payload.get("summary") or {})
    lines: list[str] = []
    lines.append("# CloudPan Sync Provider Live Probe Report")
    lines.append("")
    lines.append(f"- GeneratedAt: `{payload.get('generatedAt', '')}`")
    lines.append(
        f"- Summary: providerCount={summary.get('providerCount', 0)}, totalChecks={summary.get('totalChecks', 0)}, okChecks={summary.get('okChecks', 0)}, failedChecks={summary.get('failedChecks', 0)}"
    )
    lines.append("")
    for item in payload.get("items", []):
        row = dict(item or {})
        lines.append(f"## {row.get('providerKey', '')} - {row.get('displayName', '')}")
        checks = list(row.get("checks") or [])
        if not checks:
            lines.append("- no-check: officialDocsUrl/webLoginUrl missing")
        for c in checks:
            ck = dict(c or {})
            lines.append(
                f"- {ck.get('kind', '')}: ok={ck.get('ok', False)} status={ck.get('status', 0)} url={ck.get('url', '')} final={ck.get('finalUrl', '')} error={ck.get('error', '')}"
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"
