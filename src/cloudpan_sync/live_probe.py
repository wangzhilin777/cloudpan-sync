from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .provider_live_probe_store import latest_provider_live_probes
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
    saved_profile_probes = {str(row.get("providerKey") or ""): dict(row) for row in latest_provider_live_probes()}
    ok_checks = 0
    total_checks = 0
    adapter_probe_ok = 0
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
        saved_probe = saved_profile_probes.get(provider_key, {})
        saved_probe_ok = bool(saved_probe.get("ok"))
        if saved_probe_ok:
            adapter_probe_ok += 1
        rows.append(
            {
                "providerKey": provider_key,
                "displayName": display_name,
                "checks": [c.to_dict() for c in checks],
                "profileProbe": {
                    "ok": saved_probe_ok,
                    "mode": str(saved_probe.get("mode") or ""),
                    "summary": str(saved_probe.get("summary") or ""),
                    "checkCount": len(saved_probe.get("checks") or []) if isinstance(saved_probe.get("checks"), list) else 0,
                },
            }
        )
    provider_profile_probe_count = sum(
        1 for row in rows if int((((row.get("profileProbe") or {}).get("checkCount", 0)) or 0)) > 0
    )
    provider_profile_probe_ok_count = sum(
        1
        for row in rows
        if int((((row.get("profileProbe") or {}).get("checkCount", 0)) or 0)) > 0
        and bool(((row.get("profileProbe") or {}).get("ok")))
    )
    provider_profile_probe_failed_count = max(0, provider_profile_probe_count - provider_profile_probe_ok_count)

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "providerCount": len(research),
            "totalChecks": total_checks,
            "okChecks": ok_checks,
            "failedChecks": max(0, total_checks - ok_checks),
            "profileProbeProviderCount": provider_profile_probe_count,
            "profileProbeOkCount": provider_profile_probe_ok_count,
            "profileProbeFailedCount": provider_profile_probe_failed_count,
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
        f"- Summary: providerCount={summary.get('providerCount', 0)}, totalChecks={summary.get('totalChecks', 0)}, okChecks={summary.get('okChecks', 0)}, failedChecks={summary.get('failedChecks', 0)}, profileProbeProviderCount={summary.get('profileProbeProviderCount', 0)}, profileProbeOkCount={summary.get('profileProbeOkCount', 0)}, profileProbeFailedCount={summary.get('profileProbeFailedCount', 0)}"
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
        profile_probe = dict(row.get("profileProbe") or {})
        if int(profile_probe.get("checkCount", 0) or 0) > 0:
            lines.append(
                f"- profile_probe: ok={profile_probe.get('ok', False)} mode={profile_probe.get('mode', '')} checks={profile_probe.get('checkCount', 0)} summary={profile_probe.get('summary', '')}"
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"
