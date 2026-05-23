from __future__ import annotations

from datetime import datetime, timezone

from .auth_live_validate import list_live_validations
from .provider_live_probe_store import list_provider_live_probes
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


def _latest_probe_by_provider() -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for row in list_provider_live_probes():
        key = str(row.get("providerKey") or "")
        if not key:
            continue
        result[key] = row
    return result


def build_status_matrix() -> dict[str, object]:
    registry = {x.profile.providerKey: x.profile for x in build_provider_registry()}
    research = {str(x.get("providerKey") or ""): x for x in build_provider_research_index()}
    auth_ok = _latest_ok_by_provider()
    probe_rows = _latest_probe_by_provider()
    live_list_ready = {"guangya", "aliyundrive_open", "189cloud", "123_open", "115_open", "xunlei", "quark", "uc", "pikpak", "baidu_netdisk"}
    live_metadata_ready = {"guangya", "aliyundrive_open", "189cloud", "123_open", "115_open", "xunlei", "quark", "uc", "pikpak", "baidu_netdisk"}
    live_create_dir_ready = {"guangya", "aliyundrive_open", "123_open", "115_open", "xunlei", "pikpak", "baidu_netdisk", "quark", "uc"}

    items: list[dict[str, object]] = []
    for provider_key, profile in registry.items():
        row_research = research.get(provider_key, {})
        auth_ready = bool(auth_ok.get(provider_key, False))
        probe = dict(probe_rows.get(provider_key) or {})
        live_probe_ok = bool(probe.get("ok"))
        list_ready = provider_key in live_list_ready
        metadata_ready = provider_key in live_metadata_ready
        create_dir_ready = provider_key in live_create_dir_ready
        fast_check = provider_key in {"guangya", "xunlei", "pikpak", "aliyundrive_open", "115_open"}
        fallback_ready = True
        support_status = "auth_ready" if auth_ready else "planned"
        if list_ready:
            support_status = "list_ready" if not auth_ready else "list_ready"
        if auth_ready and list_ready and metadata_ready:
            support_status = "metadata_ready"
        if auth_ready and list_ready and metadata_ready and fast_check:
            support_status = "fast_check"
        if live_probe_ok and metadata_ready:
            support_status = "metadata_ready"

        items.append(
            {
                "providerKey": provider_key,
                "displayName": profile.displayName,
                "authModes": profile.authModes,
                "conflictPolicies": profile.conflictPolicies,
                "supportsOverwrite": profile.supportsOverwrite,
                "supportsAutoRename": profile.supportsAutoRename,
                "overwriteBehavior": profile.overwriteBehavior,
                "conflictNotes": profile.conflictNotes,
                "registryStatus": profile.status,
                "researchStatus": row_research.get("status", ""),
                "auth_ready": auth_ready,
                "list_ready": list_ready,
                "metadata_ready": metadata_ready,
                "create_dir_ready": create_dir_ready,
                "fast_check": fast_check,
                "fallback_ready": fallback_ready,
                "live_probe_ok": live_probe_ok,
                "lastProbeMode": str(probe.get("mode") or ""),
                "supportStatus": support_status,
            }
        )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "providerCount": len(items),
            "authReadyCount": sum(1 for x in items if x["auth_ready"]),
            "createDirReadyCount": sum(1 for x in items if x["create_dir_ready"]),
            "fastCheckCount": sum(1 for x in items if x["fast_check"]),
            "liveProbeOkCount": sum(1 for x in items if x["live_probe_ok"]),
            "conflictAwareProviderCount": sum(1 for x in items if x["conflictPolicies"]),
            "overwriteReadyCount": sum(1 for x in items if x["supportsOverwrite"]),
            "autoRenameReadyCount": sum(1 for x in items if x["supportsAutoRename"]),
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
        f"- Summary: providerCount={summary.get('providerCount', 0)}, authReadyCount={summary.get('authReadyCount', 0)}, createDirReadyCount={summary.get('createDirReadyCount', 0)}, fastCheckCount={summary.get('fastCheckCount', 0)}, liveProbeOkCount={summary.get('liveProbeOkCount', 0)}, conflictAwareProviderCount={summary.get('conflictAwareProviderCount', 0)}, overwriteReadyCount={summary.get('overwriteReadyCount', 0)}, autoRenameReadyCount={summary.get('autoRenameReadyCount', 0)}"
    )
    lines.append("")
    lines.append("| providerKey | supportStatus | auth_ready | list_ready | metadata_ready | create_dir_ready | fast_check | live_probe_ok | supports_overwrite | supports_auto_rename | overwrite_behavior | conflict_policies | fallback_ready |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for row in payload.get("items", []):
        item = dict(row or {})
        lines.append(
            f"| {item.get('providerKey','')} | {item.get('supportStatus','')} | {item.get('auth_ready',False)} | {item.get('list_ready',False)} | {item.get('metadata_ready',False)} | {item.get('create_dir_ready',False)} | {item.get('fast_check',False)} | {item.get('live_probe_ok',False)} | {item.get('supportsOverwrite',False)} | {item.get('supportsAutoRename',False)} | {item.get('overwriteBehavior','')} | {', '.join(item.get('conflictPolicies', [])) or '(none)'} | {item.get('fallback_ready',False)} |"
        )
        if item.get("conflictNotes"):
            lines.append(f"|  | note |  |  |  |  |  |  |  |  |  | {str(item.get('conflictNotes') or '').replace('|', '/')} |  |")
    lines.append("")
    return "\n".join(lines)
