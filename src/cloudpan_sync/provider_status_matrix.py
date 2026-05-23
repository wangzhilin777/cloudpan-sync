from __future__ import annotations

from datetime import datetime, timezone

from .auth_live_validate import list_live_validations
from .provider_registry import build_provider_registry
from .provider_research import build_provider_research_index


def _latest_ok_by_provider() -> dict[str, bool]:
    result: dict[str, bool] = {}
    for row in list_live_validations():
        key = str(row.get("providerKey") or "")
        if not key:
            continue
        ok = bool(row.get("ok"))
        result[key] = result.get(key, False) or ok
    return result


def build_status_matrix() -> dict[str, object]:
    registry = {x.profile.providerKey: x.profile for x in build_provider_registry()}
    research = {str(x.get("providerKey") or ""): x for x in build_provider_research_index()}
    auth_ok = _latest_ok_by_provider()

    items: list[dict[str, object]] = []
    for provider_key, profile in registry.items():
        row_research = research.get(provider_key, {})
        auth_ready = bool(auth_ok.get(provider_key, False))
        # current code path keeps list/metadata as mock-ready for all registry providers
        list_ready = True
        metadata_ready = True
        fast_check = provider_key in {"guangya", "xunlei", "pikpak", "aliyundrive_open", "115_open"}
        fallback_ready = True
        support_status = "auth_ready" if auth_ready else "planned"
        if auth_ready and list_ready and metadata_ready:
            support_status = "metadata_ready"
        if auth_ready and list_ready and metadata_ready and fast_check:
            support_status = "fast_check"

        items.append(
            {
                "providerKey": provider_key,
                "displayName": profile.displayName,
                "authModes": profile.authModes,
                "registryStatus": profile.status,
                "researchStatus": row_research.get("status", ""),
                "auth_ready": auth_ready,
                "list_ready": list_ready,
                "metadata_ready": metadata_ready,
                "fast_check": fast_check,
                "fallback_ready": fallback_ready,
                "supportStatus": support_status,
            }
        )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "providerCount": len(items),
            "authReadyCount": sum(1 for x in items if x["auth_ready"]),
            "fastCheckCount": sum(1 for x in items if x["fast_check"]),
        },
        "items": sorted(items, key=lambda x: str(x.get("providerKey") or "")),
    }


def matrix_to_markdown(payload: dict[str, object]) -> str:
    summary = dict(payload.get("summary") or {})
    lines: list[str] = []
    lines.append("# CloudPan Sync Provider Status Matrix")
    lines.append("")
    lines.append(f"- GeneratedAt: `{payload.get('generatedAt', '')}`")
    lines.append(
        f"- Summary: providerCount={summary.get('providerCount', 0)}, authReadyCount={summary.get('authReadyCount', 0)}, fastCheckCount={summary.get('fastCheckCount', 0)}"
    )
    lines.append("")
    lines.append("| providerKey | supportStatus | auth_ready | list_ready | metadata_ready | fast_check | fallback_ready |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in payload.get("items", []):
        item = dict(row or {})
        lines.append(
            f"| {item.get('providerKey','')} | {item.get('supportStatus','')} | {item.get('auth_ready',False)} | {item.get('list_ready',False)} | {item.get('metadata_ready',False)} | {item.get('fast_check',False)} | {item.get('fallback_ready',False)} |"
        )
    lines.append("")
    return "\n".join(lines)
