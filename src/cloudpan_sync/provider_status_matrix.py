from __future__ import annotations

from datetime import datetime, timezone

from .auth_live_validate import list_live_validations
from .planner import _resolve_conflict_support
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
                "task_runtime_candidate": 0,
                "task_runtime_probe": 0,
                "task_runtime_blocked": 0,
                "task_runtime_conflict_handled": 0,
            },
        )
        bucket["task_runtime_samples"] += 1
        if bool(row.get("candidateOnly")):
            bucket["task_runtime_candidate"] += 1
        elif bool(row.get("probeOnly")):
            bucket["task_runtime_probe"] += 1
        elif bool(row.get("success")):
            bucket["task_runtime_success"] += 1
        else:
            bucket["task_runtime_failed"] += 1
        if str(row.get("executionMode") or "") == "blocked":
            bucket["task_runtime_blocked"] += 1
        if str(row.get("conflictAction") or ""):
            bucket["task_runtime_conflict_handled"] += 1
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
            "Current task runtime now drives Aliyun Drive Open real local-file upload for download_upload items with overwrite_existing / auto_rename_new conflict handling, plus a probe-only md5 fast-upload candidate check for fast_upload items.",
        )
    if provider_key == "123_open":
        return (
            "runtime_active",
            "Current task runtime now drives 123Pan Open real local-file upload for download_upload items with auto_rename_new and overwrite-to-auto-rename downgrade handling, plus a probe-only md5 fast-upload candidate check for fast_upload items.",
        )
    if provider_key == "115_open":
        return (
            "runtime_active",
            "Current task runtime now drives a 115 Open live create_dir write probe for download_upload items, and can also attempt 115 Open upload/init plus sign_check based rapid upload for fast_upload items when a usable local file plus sha1 is available; full binary upload fallback is still not wired yet.",
        )
    if provider_key == "xunlei":
        return (
            "runtime_active",
            "Current task runtime now drives a live Xunlei create_dir write probe for download_upload items, and can also attempt Xunlei rapid upload through the live /drive/v1/files create-by-hash call for fast_upload items when a usable local file plus gcid is available; full resumable binary upload fallback is still not wired yet.",
        )
    if provider_key == "pikpak":
        return (
            "runtime_active",
            "Current task runtime now drives a live PikPak create_dir write probe for download_upload items, and can also attempt PikPak rapid upload through the live /drive/v1/files create-by-hash call for fast_upload items when a usable local file plus gcid is available; full resumable binary upload fallback is still not wired yet.",
        )
    if provider_key == "baidu_netdisk":
        return (
            "runtime_active",
            "Current task runtime now drives Baidu Netdisk real local-file upload for download_upload items with auto_rename_new and overwrite-to-auto-rename downgrade handling, plus a probe-only md5 fast-upload candidate check for fast_upload items.",
        )
    if provider_key == "quark":
        return (
            "runtime_active",
            "Current task runtime now drives a live Quark create_dir write probe for download_upload items, and for fast_upload items it can first attempt upload/pre + update/hash rapid upload and then continue into upload/auth + multipart PUT + commit + upload/finish when hash miss occurs and a usable local file plus md5/sha1 context is available; the download_upload strategy still has not been upgraded into a direct local-file upload path.",
        )
    if provider_key == "uc":
        return (
            "runtime_active",
            "Current task runtime now drives a live UC Drive create_dir write probe for download_upload items, and for fast_upload items it can first attempt upload/pre + update/hash rapid upload and then continue into upload/auth + multipart PUT + commit + upload/finish when hash miss occurs and a usable local file plus md5/sha1 context is available; the download_upload strategy still has not been upgraded into a direct local-file upload path.",
        )
    if provider_key == "189cloud":
        return (
            "runtime_active",
            "Current task runtime can now attempt 189Cloud create_dir with account-level OAuth headers, and can also attempt 189Cloud rapid upload through createUploadFile plus fileCommitUrl when a usable local file plus md5 and account-level write auth are available; shareCode/accessCode-only profiles still remain read-only and full binary upload fallback is still not wired yet.",
        )
    return (
        "runtime_planned",
        "This provider has not reached task runtime write integration yet.",
    )


def _fast_check_ready(provider_key: str, profile: object, metadata_ready: bool) -> bool:
    if not metadata_ready:
        return False
    inputs = list(getattr(profile, "fastUploadInputs", []) or [])
    return bool(inputs)


def _conflict_support_snapshot(provider_key: str) -> dict[str, str]:
    overwrite_status, overwrite_note = _resolve_conflict_support(
        conflict_policy="overwrite_existing",
        provider_key=provider_key,
    )
    auto_rename_status, auto_rename_note = _resolve_conflict_support(
        conflict_policy="auto_rename_new",
        provider_key=provider_key,
    )
    return {
        "overwrite_support_status": overwrite_status,
        "overwrite_support_note": overwrite_note,
        "auto_rename_support_status": auto_rename_status,
        "auto_rename_support_note": auto_rename_note,
    }


def build_status_matrix() -> dict[str, object]:
    registry = {x.profile.providerKey: x.profile for x in build_provider_registry()}
    research = {str(x.get("providerKey") or ""): x for x in build_provider_research_index()}
    auth_ok = _latest_ok_by_provider()
    probe_rows = _latest_probe_by_provider()
    runtime_rows = _runtime_summary_by_provider()
    live_list_ready = {"guangya", "aliyundrive_open", "189cloud", "123_open", "115_open", "xunlei", "quark", "uc", "pikpak", "baidu_netdisk"}
    live_metadata_ready = {"guangya", "aliyundrive_open", "189cloud", "123_open", "115_open", "xunlei", "quark", "uc", "pikpak", "baidu_netdisk"}
    live_create_dir_ready = {"guangya", "aliyundrive_open", "189cloud", "123_open", "115_open", "xunlei", "pikpak", "baidu_netdisk", "quark", "uc"}

    items: list[dict[str, object]] = []
    for provider_key, profile in registry.items():
        row_research = research.get(provider_key, {})
        auth_ready = bool(auth_ok.get(provider_key, False))
        probe = dict(probe_rows.get(provider_key) or {})
        runtime = dict(runtime_rows.get(provider_key) or {})
        runtime_track, runtime_track_note = _runtime_track_for_provider(provider_key)
        conflict_support = _conflict_support_snapshot(provider_key)
        live_probe_ok = bool(probe.get("ok"))
        list_ready = provider_key in live_list_ready
        metadata_ready = provider_key in live_metadata_ready
        create_dir_ready = provider_key in live_create_dir_ready
        fast_check = _fast_check_ready(provider_key, profile, metadata_ready)
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
                "overwrite_support_status": conflict_support["overwrite_support_status"],
                "overwrite_support_note": conflict_support["overwrite_support_note"],
                "auto_rename_support_status": conflict_support["auto_rename_support_status"],
                "auto_rename_support_note": conflict_support["auto_rename_support_note"],
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
                "task_runtime_candidate": int(runtime.get("task_runtime_candidate", 0) or 0),
                "task_runtime_probe": int(runtime.get("task_runtime_probe", 0) or 0),
                "task_runtime_blocked": int(runtime.get("task_runtime_blocked", 0) or 0),
                "task_runtime_conflict_handled": int(runtime.get("task_runtime_conflict_handled", 0) or 0),
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
            "overwriteDowngradeCount": sum(
                1 for x in items if str(x["overwrite_support_status"]) == "downgrade_to_auto_rename"
            ),
            "overwriteSupportedCount": sum(
                1 for x in items if str(x["overwrite_support_status"]) == "supported"
            ),
            "autoRenameSupportedCount": sum(
                1 for x in items if str(x["auto_rename_support_status"]) == "supported"
            ),
            "autoRenameProbeOnlyCount": sum(
                1 for x in items if str(x["auto_rename_support_status"]) == "probe_only_runtime_write_check"
            ),
            "conflictUnsupportedProviderCount": sum(
                1
                for x in items
                if str(x["overwrite_support_status"]) == "unsupported"
                and str(x["auto_rename_support_status"]) == "unsupported"
            ),
            "taskRuntimeEvidenceProviderCount": sum(1 for x in items if int(x["task_runtime_success"]) > 0),
            "taskRuntimeFailedProviderCount": sum(1 for x in items if int(x["task_runtime_failed"]) > 0),
            "taskRuntimeCandidateEvidenceProviderCount": sum(1 for x in items if int(x["task_runtime_candidate"]) > 0),
            "taskRuntimeProbeEvidenceProviderCount": sum(1 for x in items if int(x["task_runtime_probe"]) > 0),
            "taskRuntimeSampleCount": sum(int(x["task_runtime_samples"]) for x in items),
            "taskRuntimeSuccessCount": sum(int(x["task_runtime_success"]) for x in items),
            "taskRuntimeFailedCount": sum(int(x["task_runtime_failed"]) for x in items),
            "taskRuntimeCandidateEvidenceCount": sum(int(x["task_runtime_candidate"]) for x in items),
            "taskRuntimeProbeEvidenceCount": sum(int(x["task_runtime_probe"]) for x in items),
            "taskRuntimeBlockedProviderCount": sum(1 for x in items if int(x["task_runtime_blocked"]) > 0),
            "taskRuntimeBlockedEvidenceCount": sum(int(x["task_runtime_blocked"]) for x in items),
            "taskRuntimeConflictHandledProviderCount": sum(
                1 for x in items if int(x["task_runtime_conflict_handled"]) > 0
            ),
            "taskRuntimeConflictHandledCount": sum(int(x["task_runtime_conflict_handled"]) for x in items),
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
        f"- Summary: providerCount={summary.get('providerCount', 0)}, authReadyCount={summary.get('authReadyCount', 0)}, createDirReadyCount={summary.get('createDirReadyCount', 0)}, fastCheckCount={summary.get('fastCheckCount', 0)}, liveProbeOkCount={summary.get('liveProbeOkCount', 0)}, conflictAwareProviderCount={summary.get('conflictAwareProviderCount', 0)}, overwriteReadyCount={summary.get('overwriteReadyCount', 0)}, autoRenameReadyCount={summary.get('autoRenameReadyCount', 0)}, overwriteDowngradeCount={summary.get('overwriteDowngradeCount', 0)}, overwriteSupportedCount={summary.get('overwriteSupportedCount', 0)}, autoRenameSupportedCount={summary.get('autoRenameSupportedCount', 0)}, autoRenameProbeOnlyCount={summary.get('autoRenameProbeOnlyCount', 0)}, conflictUnsupportedProviderCount={summary.get('conflictUnsupportedProviderCount', 0)}, taskRuntimeEvidenceProviderCount={summary.get('taskRuntimeEvidenceProviderCount', 0)}, taskRuntimeFailedProviderCount={summary.get('taskRuntimeFailedProviderCount', 0)}, taskRuntimeCandidateEvidenceProviderCount={summary.get('taskRuntimeCandidateEvidenceProviderCount', 0)}, taskRuntimeProbeEvidenceProviderCount={summary.get('taskRuntimeProbeEvidenceProviderCount', 0)}, taskRuntimeSampleCount={summary.get('taskRuntimeSampleCount', 0)}, taskRuntimeSuccessCount={summary.get('taskRuntimeSuccessCount', 0)}, taskRuntimeFailedCount={summary.get('taskRuntimeFailedCount', 0)}, taskRuntimeCandidateEvidenceCount={summary.get('taskRuntimeCandidateEvidenceCount', 0)}, taskRuntimeProbeEvidenceCount={summary.get('taskRuntimeProbeEvidenceCount', 0)}, taskRuntimeBlockedProviderCount={summary.get('taskRuntimeBlockedProviderCount', 0)}, taskRuntimeBlockedEvidenceCount={summary.get('taskRuntimeBlockedEvidenceCount', 0)}, taskRuntimeConflictHandledProviderCount={summary.get('taskRuntimeConflictHandledProviderCount', 0)}, taskRuntimeConflictHandledCount={summary.get('taskRuntimeConflictHandledCount', 0)}, taskRuntimeActiveCount={summary.get('taskRuntimeActiveCount', 0)}, taskRuntimeCandidateCount={summary.get('taskRuntimeCandidateCount', 0)}, taskRuntimeBlockedCount={summary.get('taskRuntimeBlockedCount', 0)}"
    )
    lines.append("")
    lines.append("| providerKey | supportStatus | auth_ready | list_ready | metadata_ready | create_dir_ready | fast_check | live_probe_ok | task_runtime_track | task_runtime_samples | task_runtime_success | task_runtime_failed | task_runtime_candidate | task_runtime_probe | task_runtime_blocked | task_runtime_conflict_handled | supports_overwrite | supports_auto_rename | overwrite_behavior | overwrite_support_status | auto_rename_support_status | conflict_policies | fallback_ready |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for row in payload.get("items", []):
        item = dict(row or {})
        lines.append(
            f"| {item.get('providerKey','')} | {item.get('supportStatus','')} | {item.get('auth_ready',False)} | {item.get('list_ready',False)} | {item.get('metadata_ready',False)} | {item.get('create_dir_ready',False)} | {item.get('fast_check',False)} | {item.get('live_probe_ok',False)} | {item.get('task_runtime_track','')} | {item.get('task_runtime_samples',0)} | {item.get('task_runtime_success',0)} | {item.get('task_runtime_failed',0)} | {item.get('task_runtime_candidate',0)} | {item.get('task_runtime_probe',0)} | {item.get('task_runtime_blocked',0)} | {item.get('task_runtime_conflict_handled',0)} | {item.get('supportsOverwrite',False)} | {item.get('supportsAutoRename',False)} | {item.get('overwriteBehavior','')} | {item.get('overwrite_support_status','')} | {item.get('auto_rename_support_status','')} | {', '.join(item.get('conflictPolicies', [])) or '(none)'} | {item.get('fallback_ready',False)} |"
        )
        if item.get("task_runtime_track_note"):
            lines.append(f"|  | runtime_note |  |  |  |  |  |  | {str(item.get('task_runtime_track_note') or '').replace('|', '/')} |  |  |  |  |  |  |  |  |  |  |  |")
        if item.get("overwrite_support_note"):
            lines.append(f"|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | {str(item.get('overwrite_support_note') or '').replace('|', '/')} |  |  |  |")
        if item.get("auto_rename_support_note"):
            lines.append(f"|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | {str(item.get('auto_rename_support_note') or '').replace('|', '/')} |  |  |")
        if item.get("conflictNotes"):
            lines.append(f"|  | note |  |  |  |  |  |  |  |  |  |  |  |  | {str(item.get('conflictNotes') or '').replace('|', '/')} |  |  |  |  |  |")
    lines.append("")
    return "\n".join(lines)
