from __future__ import annotations

from datetime import datetime, timezone

from .auth_live_validate import list_live_validations
from .provider_live_probe_store import list_provider_live_probes
from .provider_registry import build_provider_registry
from .provider_research import build_provider_research_index
from .task_runtime_evidence_store import latest_task_runtime_evidence


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


def _runtime_summary_by_provider() -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for row in latest_task_runtime_evidence():
        key = str(row.get("providerKey") or "")
        if not key:
            continue
        bucket = result.setdefault(
            key,
            {
                "task_runtime_samples": 0,
                "task_runtime_success": 0,
                "task_runtime_failed": 0,
            },
        )
        bucket["task_runtime_samples"] += 1
        if bool(row.get("success")):
            bucket["task_runtime_success"] += 1
        else:
            bucket["task_runtime_failed"] += 1
    return result


def _runtime_track_for_provider(provider_key: str) -> tuple[str, str]:
    if provider_key == "guangya":
        return (
            "runtime_active",
            "Current task runtime already drives Guangya live fast-check and fallback upload attempts.",
        )
    if provider_key == "aliyundrive_open":
        return (
            "runtime_active",
            "Current task runtime now drives an Aliyun Drive Open live create_dir write probe before mock/download fallback completion.",
        )
    if provider_key == "123_open":
        return (
            "runtime_active",
            "Current task runtime now drives a 123Pan Open live create_dir write probe before mock/download fallback completion.",
        )
    if provider_key == "115_open":
        return (
            "runtime_active",
            "Current task runtime now drives a 115 Open live create_dir write probe before mock/download fallback completion.",
        )
    if provider_key == "xunlei":
        return (
            "runtime_active",
            "Current task runtime now drives a live Xunlei create_dir write probe before mock/download fallback completion.",
        )
    if provider_key == "pikpak":
        return (
            "runtime_active",
            "Current task runtime now drives a live PikPak create_dir write probe before mock/download fallback completion.",
        )
    if provider_key == "baidu_netdisk":
        return (
            "runtime_active",
            "Current task runtime now drives a live Baidu Netdisk create_dir write probe before mock/download fallback completion.",
        )
    if provider_key == "quark":
        return (
            "runtime_active",
            "Current task runtime now drives a live Quark create_dir write probe before mock/download fallback completion.",
        )
    if provider_key == "189cloud":
        return (
            "runtime_blocked",
            "Current 189Cloud path is still shareCode/accessCode read-only, so task runtime write attempts cannot start yet.",
        )
    if provider_key in {
        "uc",
    }:
        return (
            "runtime_candidate",
            "Live list/metadata/create_dir capability is already wired, but task runtime write/upload flow is not connected yet.",
        )
    return (
        "runtime_planned",
        "This provider has not reached task runtime write integration yet.",
    )


def build_status_matrix() -> dict[str, object]:
    registry = {x.profile.providerKey: x.profile for x in build_provider_registry()}
    research = {str(x.get("providerKey") or ""): x for x in build_provider_research_index()}
    auth_ok = _latest_ok_by_provider()
    probe_rows = _latest_probe_by_provider()
    runtime_rows = _runtime_summary_by_provider()
    live_list_ready = {"guangya", "aliyundrive_open", "189cloud", "123_open", "115_open", "xunlei", "quark", "uc", "pikpak", "baidu_netdisk"}
    live_metadata_ready = {"guangya", "aliyundrive_open", "189cloud", "123_open", "115_open", "xunlei", "quark", "uc", "pikpak", "baidu_netdisk"}
    live_create_dir_ready = {"guangya", "aliyundrive_open", "123_open", "115_open", "xunlei", "pikpak", "baidu_netdisk", "quark", "uc"}

    items: list[dict[str, object]] = []
    for provider_key, profile in registry.items():
        row_research = research.get(provider_key, {})
        auth_ready = bool(auth_ok.get(provider_key, False))
        probe = dict(probe_rows.get(provider_key) or {})
        runtime = dict(runtime_rows.get(provider_key) or {})
        runtime_track, runtime_track_note = _runtime_track_for_provider(provider_key)
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
                "task_runtime_track": runtime_track,
                "task_runtime_track_note": runtime_track_note,
                "task_runtime_samples": int(runtime.get("task_runtime_samples", 0) or 0),
                "task_runtime_success": int(runtime.get("task_runtime_success", 0) or 0),
                "task_runtime_failed": int(runtime.get("task_runtime_failed", 0) or 0),
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
            "taskRuntimeEvidenceProviderCount": sum(1 for x in items if int(x["task_runtime_success"]) > 0),
            "taskRuntimeFailedProviderCount": sum(1 for x in items if int(x["task_runtime_failed"]) > 0),
            "taskRuntimeSampleCount": sum(int(x["task_runtime_samples"]) for x in items),
            "taskRuntimeSuccessCount": sum(int(x["task_runtime_success"]) for x in items),
            "taskRuntimeFailedCount": sum(int(x["task_runtime_failed"]) for x in items),
            "taskRuntimeActiveCount": sum(1 for x in items if str(x["task_runtime_track"]) == "runtime_active"),
            "taskRuntimeCandidateCount": sum(1 for x in items if str(x["task_runtime_track"]) == "runtime_candidate"),
            "taskRuntimeBlockedCount": sum(1 for x in items if str(x["task_runtime_track"]) == "runtime_blocked"),
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
        f"- Summary: providerCount={summary.get('providerCount', 0)}, authReadyCount={summary.get('authReadyCount', 0)}, createDirReadyCount={summary.get('createDirReadyCount', 0)}, fastCheckCount={summary.get('fastCheckCount', 0)}, liveProbeOkCount={summary.get('liveProbeOkCount', 0)}, conflictAwareProviderCount={summary.get('conflictAwareProviderCount', 0)}, overwriteReadyCount={summary.get('overwriteReadyCount', 0)}, autoRenameReadyCount={summary.get('autoRenameReadyCount', 0)}, taskRuntimeEvidenceProviderCount={summary.get('taskRuntimeEvidenceProviderCount', 0)}, taskRuntimeFailedProviderCount={summary.get('taskRuntimeFailedProviderCount', 0)}, taskRuntimeSampleCount={summary.get('taskRuntimeSampleCount', 0)}, taskRuntimeSuccessCount={summary.get('taskRuntimeSuccessCount', 0)}, taskRuntimeFailedCount={summary.get('taskRuntimeFailedCount', 0)}, taskRuntimeActiveCount={summary.get('taskRuntimeActiveCount', 0)}, taskRuntimeCandidateCount={summary.get('taskRuntimeCandidateCount', 0)}, taskRuntimeBlockedCount={summary.get('taskRuntimeBlockedCount', 0)}"
    )
    lines.append("")
    lines.append("| providerKey | supportStatus | auth_ready | list_ready | metadata_ready | create_dir_ready | fast_check | live_probe_ok | task_runtime_track | task_runtime_samples | task_runtime_success | task_runtime_failed | supports_overwrite | supports_auto_rename | overwrite_behavior | conflict_policies | fallback_ready |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for row in payload.get("items", []):
        item = dict(row or {})
        lines.append(
            f"| {item.get('providerKey','')} | {item.get('supportStatus','')} | {item.get('auth_ready',False)} | {item.get('list_ready',False)} | {item.get('metadata_ready',False)} | {item.get('create_dir_ready',False)} | {item.get('fast_check',False)} | {item.get('live_probe_ok',False)} | {item.get('task_runtime_track','')} | {item.get('task_runtime_samples',0)} | {item.get('task_runtime_success',0)} | {item.get('task_runtime_failed',0)} | {item.get('supportsOverwrite',False)} | {item.get('supportsAutoRename',False)} | {item.get('overwriteBehavior','')} | {', '.join(item.get('conflictPolicies', [])) or '(none)'} | {item.get('fallback_ready',False)} |"
        )
        if item.get("task_runtime_track_note"):
            lines.append(f"|  | runtime_note |  |  |  |  |  |  | {str(item.get('task_runtime_track_note') or '').replace('|', '/')} |  |  |  |  |  |  |  |  |")
        if item.get("conflictNotes"):
            lines.append(f"|  | note |  |  |  |  |  |  |  |  |  |  |  |  | {str(item.get('conflictNotes') or '').replace('|', '/')} |  |  |")
    lines.append("")
    return "\n".join(lines)
