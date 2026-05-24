from __future__ import annotations

from hashlib import md5
from pathlib import Path
from datetime import datetime, timezone
from pathlib import PurePosixPath
import re
from uuid import uuid4

from .auth_store import get_profile
from .aliyun_open_live import fetch_aliyun_open_create_folder
from .aliyun_open_upload_live import upload_aliyun_open_local_file
from .baidu_netdisk_live import fetch_baidu_create_dir
from .baidu_netdisk_upload_live import upload_baidu_local_file
from .guangya_live import fetch_guangya_live_fast_check
from .guangya_upload_live import upload_guangya_local_file
from .models import SourceEntry, TaskCreateRequest
from .pan115_open_live import fetch_115_open_create_folder
from .pan123_open_live import fetch_123_open_create_folder
from .pan123_open_upload_live import upload_123_open_local_file
from .pikpak_fast_upload_live import upload_pikpak_fast_file
from .pikpak_live import fetch_pikpak_create_folder
from .planner import build_transfer_plan
from .quark_fast_upload_live import upload_quark_fast_file
from .quark_live import fetch_quark_create_folder
from .task_guard import evaluate_task_guard
from .task_runtime_evidence_store import save_task_runtime_evidence
from .tianyi_live import fetch_tianyi_create_folder
from .uc_fast_upload_live import upload_uc_fast_file
from .uc_live import fetch_uc_create_folder
from .xunlei_fast_upload_live import upload_xunlei_fast_file
from .xunlei_live import fetch_xunlei_create_folder


_TASKS: dict[str, dict[str, object]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _materialize_local_source_entry(raw: dict[str, object], default_path: str, default_size: int) -> SourceEntry | None:
    local_path = str(raw.get("localPath") or "").strip()
    if not local_path:
        return None
    file_path = Path(local_path)
    if not file_path.exists() or not file_path.is_file():
        return None

    size = int(raw.get("size", 0) or 0)
    actual_size = int(file_path.stat().st_size)
    if size <= 0:
        size = actual_size

    md5_value = str(raw.get("md5") or "").strip().lower()
    etag_value = str(raw.get("etag") or "").strip().lower()
    if not md5_value and not etag_value:
        hasher = md5()
        with file_path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                hasher.update(chunk)
        md5_value = hasher.hexdigest()

    return SourceEntry(
        path=str(raw.get("path") or default_path or ""),
        size=size,
        md5=md5_value,
        sha1=str(raw.get("sha1") or ""),
        sha256=str(raw.get("sha256") or ""),
        crc64=str(raw.get("crc64") or ""),
        gcid=str(raw.get("gcid") or ""),
        etag=etag_value,
        pickcode=str(raw.get("pickcode") or ""),
        blockListMd5=list(raw.get("blockListMd5") or []),
        raw=dict(raw.get("raw") or {}),
        localPath=local_path,
    )


def _probe_dir_name(task_id: str, path: str) -> str:
    stem = PurePosixPath(path or "/probe").stem or "probe"
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip("-._") or "probe"
    return f"cloudpan-sync-probe-{task_id[:8]}-{normalized[:40]}"


def _source_entry_for_item(
    source_entries_by_path: dict[str, dict[str, object]],
    item: dict[str, object],
) -> dict[str, object]:
    return dict(source_entries_by_path.get(str(item.get("path") or ""), {}) or {})


def _normalized_fingerprints_for_item(item: dict[str, object]) -> dict[str, object]:
    value = item.get("normalizedFingerprints")
    if hasattr(value, "model_dump"):
        return dict(value.model_dump() or {})
    return dict(value or {})


def _first_text(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _tianyi_account_auth_fields(profile_id: str) -> tuple[str, str, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return "", "", ""
    extra = getattr(profile, "extra", {}) or {}
    access_token = _first_text(
        getattr(profile, "token", ""),
        extra.get("authorization"),
        extra.get("Authorization"),
        extra.get("accessToken"),
        extra.get("access_token"),
    )
    signature = _first_text(extra.get("signature"), extra.get("Signature"))
    date_value = _first_text(extra.get("date"), extra.get("Date"))
    return access_token, signature, date_value


def list_tasks() -> list[dict[str, object]]:
    return sorted(_TASKS.values(), key=lambda x: str(x.get("createdAt", "")), reverse=True)


def get_task(task_id: str) -> dict[str, object] | None:
    return _TASKS.get(task_id)


def _task_requires_ack(guard: dict[str, object]) -> bool:
    required = dict(guard.get("requiresAcknowledgement") or {})
    acknowledged = dict(guard.get("acknowledged") or {})
    for key, required_value in required.items():
        if bool(required_value) and not bool(acknowledged.get(key)):
            return True
    return False


def _set_action_error(task: dict[str, object], action: str, reason: str) -> dict[str, object]:
    task["lastActionError"] = {
        "action": action,
        "reason": reason,
        "at": _now(),
    }
    task["updatedAt"] = task["lastActionError"]["at"]
    refresh_task_summary(task)
    return task


def _clear_action_error(task: dict[str, object]) -> None:
    task["lastActionError"] = {}


def _result_runtime_summary(results: list[dict[str, object]]) -> dict[str, int | str | bool]:
    counted = [
        dict(row or {})
        for row in results
        if str((row or {}).get("status") or "") in {"done", "failed"}
    ]
    probe_only = [
        row
        for row in counted
        if str(row.get("executionMode") or "") == "probe" and not bool(dict(row.get("liveAttempt") or {}).get("candidate"))
    ]
    candidate_only = [
        row
        for row in counted
        if bool(dict(row.get("liveAttempt") or {}).get("candidate"))
    ]
    live_success = [
        row
        for row in counted
        if str(row.get("executionMode") or "") == "live" and str(row.get("status") or "") == "done"
    ]
    live_failed = [
        row
        for row in counted
        if str(row.get("executionMode") or "") == "live" and str(row.get("status") or "") == "failed"
    ]
    completion_kind = ""
    if counted:
        if len(probe_only) == len(counted):
            completion_kind = "probe_only"
        elif len(candidate_only) == len(counted):
            completion_kind = "candidate_only"
        elif live_success:
            completion_kind = "real_transfer"
        elif live_failed:
            completion_kind = "live_failed"
        else:
            completion_kind = "mixed_non_live"
    return {
        "countedResultCount": len(counted),
        "probeOnlyCount": len(probe_only),
        "candidateOnlyCount": len(candidate_only),
        "liveSuccessCount": len(live_success),
        "liveFailedCount": len(live_failed),
        "completionKind": completion_kind,
        "hasRealTransferSuccess": bool(live_success),
    }


def allowed_task_actions(task: dict[str, object]) -> list[str]:
    state = str(task.get("state") or "")
    if state == "awaiting_ack":
        return ["acknowledge_risk", "retry"]
    if state == "blocked":
        return ["retry"]
    if state == "ready":
        return ["run", "pause", "retry"]
    if state == "running":
        return ["pause"]
    if state in {"paused", "risk_paused"}:
        return ["resume", "retry"]
    if state in {"completed", "completed_with_errors", "completed_probe_only", "completed_candidate_only"}:
        return ["retry"]
    return ["retry"]


def build_task_summary(task: dict[str, object]) -> dict[str, object]:
    guard = dict(task.get("guard") or {})
    blocking_reasons = list(guard.get("blockingReasons") or [])
    warning_reasons = list(guard.get("warningReasons") or [])
    requires_ack = dict(guard.get("requiresAcknowledgement") or {})
    acknowledged = dict(guard.get("acknowledged") or {})
    last_action_error = dict(task.get("lastActionError") or {})
    runtime_summary = _result_runtime_summary(list(task.get("results") or []))
    return {
        "state": str(task.get("state") or ""),
        "allowedActions": allowed_task_actions(task),
        "hardBlocked": bool(guard.get("hardBlocked")),
        "blockingCount": len(blocking_reasons),
        "warningCount": len(warning_reasons),
        "requiresAcknowledgement": requires_ack,
        "acknowledged": acknowledged,
        "awaitingAcknowledgement": _task_requires_ack(guard),
        "riskPaused": bool((task.get("risk") or {}).get("paused")),
        "riskReason": str((task.get("risk") or {}).get("reason") or ""),
        "hasLastActionError": bool(last_action_error.get("action") or last_action_error.get("reason")),
        "lastActionError": last_action_error,
        "countedResultCount": int(runtime_summary.get("countedResultCount", 0) or 0),
        "probeOnlyCount": int(runtime_summary.get("probeOnlyCount", 0) or 0),
        "candidateOnlyCount": int(runtime_summary.get("candidateOnlyCount", 0) or 0),
        "liveSuccessCount": int(runtime_summary.get("liveSuccessCount", 0) or 0),
        "liveFailedCount": int(runtime_summary.get("liveFailedCount", 0) or 0),
        "completionKind": str(runtime_summary.get("completionKind") or ""),
        "hasRealTransferSuccess": bool(runtime_summary.get("hasRealTransferSuccess")),
    }


def refresh_task_summary(task: dict[str, object]) -> dict[str, object]:
    task["summary"] = build_task_summary(task)
    return task


def _persist_task_runtime_evidence(task: dict[str, object], results: list[dict[str, object]]) -> None:
    provider_key = str(task.get("targetProvider") or "")
    profile_id = str(task.get("targetProfileId") or "")
    task_id = str(task.get("taskId") or "")
    updated_at = str(task.get("updatedAt") or _now())
    if not provider_key:
        return
    for row in results:
        result = dict(row or {})
        live_attempt = dict(result.get("liveAttempt") or {})
        mode = str(live_attempt.get("mode") or "")
        status = str(result.get("status") or "")
        if not mode:
            continue
        if mode in {"mock", "download_upload_mock"}:
            continue
        if status not in {"done", "failed"}:
            continue
        save_task_runtime_evidence(
            {
                "taskId": task_id,
                "providerKey": provider_key,
                "profileId": profile_id,
                "path": str(result.get("path") or ""),
                "mode": mode,
                "executionMode": str(result.get("executionMode") or ""),
                "candidateOnly": bool(live_attempt.get("candidate")),
                "probeOnly": str(result.get("executionMode") or "") == "probe",
                "success": status == "done",
                "status": status,
                "verifyOk": bool(live_attempt.get("verifyOk")),
                "verifyMode": str(live_attempt.get("verifyMode") or ""),
                "verifyNote": str(live_attempt.get("verifyNote") or ""),
                "conflictPolicy": str(result.get("conflictPolicy") or ""),
                "conflictAction": str(live_attempt.get("conflictAction") or ""),
                "resolvedTargetName": str(live_attempt.get("resolvedTargetName") or ""),
                "error": str(live_attempt.get("error") or ""),
                "riskHint": str(live_attempt.get("riskHint") or ""),
                "requiredAuth": list(live_attempt.get("requiredAuth") or []),
                "note": str(result.get("note") or ""),
                "savedAt": updated_at,
            }
        )


def build_task_list_view(task: dict[str, object]) -> dict[str, object]:
    summary = dict(task.get("summary") or build_task_summary(task))
    progress = dict(task.get("progress") or {})
    guard = dict(task.get("guard") or {})
    plan = dict(task.get("plan") or {})
    last_action_error = dict(task.get("lastActionError") or {})
    latest_results = list(task.get("results") or [])[:3]
    return {
        "taskId": str(task.get("taskId") or ""),
        "state": summary.get("state", ""),
        "sourceProvider": str(task.get("sourceProvider") or ""),
        "targetProvider": str(task.get("targetProvider") or ""),
        "targetProfileId": str(task.get("targetProfileId") or ""),
        "targetParentId": str(task.get("targetParentId") or ""),
        "conflictPolicy": str(task.get("conflictPolicy") or ""),
        "createdAt": str(task.get("createdAt") or ""),
        "updatedAt": str(task.get("updatedAt") or ""),
        "progress": progress,
        "summary": summary,
        "completionKind": str(summary.get("completionKind") or ""),
        "hasRealTransferSuccess": bool(summary.get("hasRealTransferSuccess")),
        "guard": guard,
        "lastActionError": last_action_error,
        "pendingItems": list(plan.get("pendingItems") or []),
        "latestResults": latest_results,
    }


def build_task_detail_view(task: dict[str, object]) -> dict[str, object]:
    summary = dict(task.get("summary") or build_task_summary(task))
    plan = dict(task.get("plan") or {})
    results = list(task.get("results") or [])
    return {
        "taskId": str(task.get("taskId") or ""),
        "state": str(summary.get("state") or task.get("state") or ""),
        "sourceProvider": str(task.get("sourceProvider") or ""),
        "targetProvider": str(task.get("targetProvider") or ""),
        "targetProfileId": str(task.get("targetProfileId") or ""),
        "targetParentId": str(task.get("targetParentId") or ""),
        "conflictPolicy": str(task.get("conflictPolicy") or ""),
        "createdAt": str(task.get("createdAt") or ""),
        "updatedAt": str(task.get("updatedAt") or ""),
        "progress": dict(task.get("progress") or {}),
        "summary": summary,
        "completionKind": str(summary.get("completionKind") or ""),
        "hasRealTransferSuccess": bool(summary.get("hasRealTransferSuccess")),
        "guard": dict(task.get("guard") or {}),
        "risk": dict(task.get("risk") or {}),
        "lastActionError": dict(task.get("lastActionError") or {}),
        "planSummary": dict(plan.get("summary") or {}),
        "executionGroups": list(plan.get("executionGroups") or []),
        "pendingItems": list(plan.get("pendingItems") or []),
        "results": results,
        "sourceEntries": list(task.get("sourceEntries") or []),
    }


def task_to_markdown(task: dict[str, object]) -> str:
    summary = dict(task.get("summary") or build_task_summary(task))
    progress = dict(task.get("progress") or {})
    guard = dict(task.get("guard") or {})
    plan = dict(task.get("plan") or {})
    pending_items = list(plan.get("pendingItems") or [])
    plan_items = list(plan.get("items") or [])
    results = list(task.get("results") or [])
    lines: list[str] = []
    lines.append("# CloudPan Sync 任务详情")
    lines.append("")
    lines.append(f"- taskId: `{task.get('taskId', '')}`")
    lines.append(f"- sourceProvider: `{task.get('sourceProvider', '')}`")
    lines.append(f"- targetProvider: `{task.get('targetProvider', '')}`")
    lines.append(f"- targetProfileId: `{task.get('targetProfileId', '') or '(none)'}`")
    lines.append(f"- targetParentId: `{task.get('targetParentId', '') or '(none)'}`")
    lines.append(f"- state: `{summary.get('state', '')}`")
    lines.append(f"- completionKind: `{summary.get('completionKind', '') or '(none)'}`")
    lines.append(f"- hasRealTransferSuccess: `{bool(summary.get('hasRealTransferSuccess'))}`")
    lines.append(f"- createdAt: `{task.get('createdAt', '')}`")
    lines.append(f"- updatedAt: `{task.get('updatedAt', '')}`")
    lines.append("")
    lines.append("## 同名文件冲突策略")
    lines.append("")
    lines.append(f"- selectedPolicy: `{task.get('conflictPolicy', '') or 'auto_rename_new'}`")
    lines.append(
        f"- summary: `liveSuccess={summary.get('liveSuccessCount', 0)}`"
        f" `liveFailed={summary.get('liveFailedCount', 0)}`"
        f" `probeOnly={summary.get('probeOnlyCount', 0)}`"
        f" `candidateOnly={summary.get('candidateOnlyCount', 0)}`"
    )
    if results:
        for index, row in enumerate(results, start=1):
            item = dict(row or {})
            live_attempt = dict(item.get("liveAttempt") or {})
            lines.append(
                f"- result[{index}]: path=`{item.get('path', '')}` status=`{item.get('status', '')}` executionMode=`{item.get('executionMode', '')}` "
                f"conflictPolicy=`{item.get('conflictPolicy', '') or task.get('conflictPolicy', '') or 'auto_rename_new'}` "
                f"conflictAction=`{live_attempt.get('conflictAction', '') or '(none)'}` "
                f"resolvedTargetName=`{live_attempt.get('resolvedTargetName', '') or '(none)'}`"
            )
    else:
        lines.append("- result: `(none)`")
    lines.append("")
    lines.append("## 计划摘要")
    lines.append("")
    lines.append(
        f"- progress: `total={progress.get('total', 0)}` `done={progress.get('done', 0)}` "
        f"`failed={progress.get('failed', 0)}` `pendingManual={progress.get('pendingManual', 0)}`"
    )
    plan_summary = dict(plan.get("summary") or {})
    strategy_counts = dict(plan_summary.get("strategyCounts") or {})
    lines.append(
        f"- planSummary: `total={plan_summary.get('total', 0)}` "
        f"`fast_upload={strategy_counts.get('fast_upload', 0)}` "
        f"`download_upload={strategy_counts.get('download_upload', 0)}` "
        f"`pending_manual={strategy_counts.get('pending_manual', 0)}`"
    )
    if pending_items:
        for index, item in enumerate(pending_items, start=1):
            row = dict(item or {})
            lines.append(
                f"- pending[{index}]: path=`{row.get('path', '')}` strategy=`{row.get('strategy', '')}` "
                f"conflictPolicy=`{row.get('conflictPolicy', '') or task.get('conflictPolicy', '') or 'auto_rename_new'}` "
                f"conflictSupportStatus=`{row.get('conflictSupportStatus', '') or '(none)'}` "
                f"conflictNote=`{row.get('conflictNote', '') or '(none)'}`"
            )
    else:
        lines.append("- pending: `(none)`")
    if plan_items:
        for index, item in enumerate(plan_items, start=1):
            row = dict(item or {})
            lines.append(
                f"- item[{index}]: path=`{row.get('path', '')}` strategy=`{row.get('strategy', '')}` "
                f"conflictPolicy=`{row.get('conflictPolicy', '') or task.get('conflictPolicy', '') or 'auto_rename_new'}` "
                f"conflictSupportStatus=`{row.get('conflictSupportStatus', '') or '(none)'}` "
                f"conflictNote=`{row.get('conflictNote', '') or '(none)'}`"
            )
    lines.append("")
    lines.append("## 风险与守卫")
    lines.append("")
    lines.append(
        f"- guard: `hardBlocked={bool(guard.get('hardBlocked'))}` "
        f"`awaitingAcknowledgement={bool(summary.get('awaitingAcknowledgement'))}` "
        f"`riskReason={summary.get('riskReason', '') or '(none)'}`"
    )
    blocking_reasons = list(guard.get("blockingReasons") or [])
    warning_reasons = list(guard.get("warningReasons") or [])
    lines.append(f"- blockingReasons: `{','.join(blocking_reasons) or '(none)'}`")
    lines.append(f"- warningReasons: `{','.join(warning_reasons) or '(none)'}`")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def create_task(payload: TaskCreateRequest) -> dict[str, object]:
    plan = build_transfer_plan(
        source_provider=payload.sourceProvider,
        target_provider=payload.targetProvider,
        entries=payload.entries,
        threshold_mb=payload.thresholdMB,
        conflict_policy=payload.conflictPolicy,
        selected_roots=payload.selectedRoots,
    ).model_dump()
    guard = evaluate_task_guard(payload, plan)
    task_id = str(uuid4())
    now = _now()
    risk_pause = bool(plan.get("summary", {}).get("strategyCounts", {}).get("pending_manual", 0) >= 3)
    ack_required = _task_requires_ack(guard)
    if bool(guard.get("hardBlocked")):
        state = "blocked"
    elif ack_required:
        state = "awaiting_ack"
    else:
        state = "risk_paused" if risk_pause else "ready"
    task = {
        "taskId": task_id,
        "state": state,
        "sourceProvider": payload.sourceProvider,
        "targetProvider": payload.targetProvider,
        "targetProfileId": payload.targetProfileId,
        "targetParentId": payload.targetParentId,
        "conflictPolicy": payload.conflictPolicy,
        "sourceEntries": [entry.model_dump() for entry in payload.entries],
        "createdAt": now,
        "updatedAt": now,
        "plan": plan,
        "guard": guard,
        "progress": {
            "total": int(plan.get("summary", {}).get("total", 0)),
            "done": 0,
            "failed": 0,
            "pendingManual": int(plan.get("summary", {}).get("strategyCounts", {}).get("pending_manual", 0)),
        },
        "results": [],
        "lastActionError": {},
        "risk": {
            "paused": risk_pause or bool(guard.get("hardBlocked")) or ack_required,
            "reason": (
                "guard_blocked"
                if bool(guard.get("hardBlocked"))
                else ("awaiting_acknowledgement" if ack_required else ("too_many_pending_manual_items" if risk_pause else ""))
            ),
        },
    }
    refresh_task_summary(task)
    _TASKS[task_id] = task
    return task


def run_task(task_id: str) -> dict[str, object]:
    task = _TASKS[task_id]
    if "run" not in allowed_task_actions(task):
        state = str(task.get("state") or "")
        reason = f"run_not_allowed_from_{state or 'unknown'}"
        if state == "awaiting_ack":
            reason = "run_not_allowed_until_acknowledge_risk"
        elif state == "blocked":
            reason = "run_not_allowed_while_guard_blocked"
        return _set_action_error(task, "run", reason)
    if str(task.get("state") or "") in {"completed", "completed_with_errors", "completed_probe_only", "completed_candidate_only"}:
        return task
    _clear_action_error(task)
    task["state"] = "running"
    items = task["plan"]["items"]
    done = 0
    failed = 0
    results: list[dict[str, object]] = []
    target_provider = str(task.get("targetProvider") or "")
    target_profile_id = str(task.get("targetProfileId") or "")
    target_parent_id = str(task.get("targetParentId") or "")
    conflict_policy = str(task.get("conflictPolicy") or "auto_rename_new")
    source_entries_by_path = {
        str(entry.get("path") or ""): dict(entry)
        for entry in task.get("sourceEntries", [])
        if isinstance(entry, dict)
    }
    guangya_fast_rows: dict[str, dict[str, object]] = {}
    guangya_fast_summary = {
        "note": "",
        "error": "",
        "riskHint": "",
    }

    if target_provider == "guangya" and target_profile_id:
        fast_entries: list[SourceEntry] = []
        for item in items:
            if item.get("strategy") != "fast_upload":
                continue
            source_entry = source_entries_by_path.get(str(item.get("path") or ""), {})
            fast_entries.append(
                SourceEntry(
                    path=str(item.get("path") or ""),
                    size=int(item.get("size", 0) or 0),
                    md5=str(source_entry.get("md5") or ""),
                    sha1=str(source_entry.get("sha1") or ""),
                    sha256=str(source_entry.get("sha256") or ""),
                    crc64=str(source_entry.get("crc64") or ""),
                    gcid=str(source_entry.get("gcid") or ""),
                    etag=str(source_entry.get("etag") or ""),
                    pickcode=str(source_entry.get("pickcode") or ""),
                    blockListMd5=list(source_entry.get("blockListMd5") or []),
                    raw=dict(source_entry.get("raw") or {}),
                )
            )
        if fast_entries:
            live_fast = fetch_guangya_live_fast_check(
                profile_id=target_profile_id,
                entries=fast_entries,
            )
            guangya_fast_summary = {
                "note": str(live_fast.note or ""),
                "error": str(live_fast.error or ""),
                "riskHint": str(live_fast.riskHint or ""),
            }
            for row in live_fast.items:
                path = str(row.get("path") or "")
                if path:
                    guangya_fast_rows[path] = row

    for item in items:
        strategy = item.get("strategy")
        path = str(item.get("path") or "")
        row_result = {
            "path": path,
            "strategy": strategy,
            "conflictPolicy": conflict_policy,
            "conflictSupportStatus": str(item.get("conflictSupportStatus") or "unknown"),
            "conflictNote": str(item.get("conflictNote") or ""),
            "executionMode": "",
            "status": "skipped",
            "note": "",
        }
        if strategy == "pending_manual":
            row_result["executionMode"] = "manual"
            row_result["status"] = "pending_manual"
            row_result["note"] = str(item.get("reason") or "")
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "guangya" and target_profile_id:
            row_result["executionMode"] = "live"
            live_row = guangya_fast_rows.get(path)
            if live_row and bool(live_row.get("canFastUpload")):
                done += 1
                row_result["status"] = "done"
                row_result["note"] = str(live_row.get("note") or "Guangya live fast-upload inventory hit succeeded.")
                row_result["liveAttempt"] = {
                    "mode": "guangya_live_fast_check",
                    "hashKind": live_row.get("hashKind", ""),
                    "canFastUpload": True,
                    "riskHint": "",
                }
            else:
                fallback_note = str((live_row or {}).get("note") or guangya_fast_summary.get("note") or "Guangya live fast-upload attempt did not hit provider inventory.")
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = fallback_note
                row_result["liveAttempt"] = {
                    "mode": "guangya_live_fast_check",
                    "hashKind": (live_row or {}).get("hashKind", ""),
                    "canFastUpload": bool((live_row or {}).get("canFastUpload")),
                    "error": (live_row or {}).get("error", "") or guangya_fast_summary.get("error", ""),
                    "riskHint": (live_row or {}).get("riskHint", "") or guangya_fast_summary.get("riskHint", ""),
                }
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "baidu_netdisk" and target_profile_id:
            source_entry = _source_entry_for_item(source_entries_by_path, item)
            normalized = _normalized_fingerprints_for_item(item)
            md5_value = _first_text(
                source_entry.get("md5"),
                normalized.get("md5"),
                source_entry.get("etag"),
                normalized.get("etag"),
            ).lower()
            row_result["executionMode"] = "probe"
            if md5_value:
                done += 1
                row_result["status"] = "done"
                row_result["note"] = (
                    "Baidu Netdisk fast-upload candidate confirmed from current md5/size fingerprints. "
                    "The current runtime only records candidate evidence and does not call a live rapid-upload API yet."
                )
                row_result["liveAttempt"] = {
                    "mode": "baidu_netdisk_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": True,
                    "requiredInputs": ["md5", "size"],
                    "hashValue": md5_value,
                    "riskHint": "",
                    "verifyOk": True,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "Current md5/size fingerprints satisfy Baidu Netdisk fast-upload precheck, but runtime remains probe-only.",
                    "verifyPayload": {
                        "md5": md5_value,
                        "size": int(item.get("size", 0) or 0),
                    },
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            else:
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = "Baidu Netdisk fast-upload candidate probe failed because md5 fingerprint is missing."
                row_result["liveAttempt"] = {
                    "mode": "baidu_netdisk_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": False,
                    "requiredInputs": ["md5", "size"],
                    "error": "missing_md5",
                    "riskHint": "Fast-upload candidate probe requires md5 fingerprint.",
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "pikpak" and target_profile_id:
            source_entry = _source_entry_for_item(source_entries_by_path, item)
            normalized = _normalized_fingerprints_for_item(item)
            gcid_value = _first_text(
                source_entry.get("gcid"),
                normalized.get("gcid"),
                source_entry.get("raw", {}).get("hash") if isinstance(source_entry.get("raw"), dict) else "",
                normalized.get("raw", {}).get("hash") if isinstance(normalized.get("raw"), dict) else "",
            ).lower()
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None and gcid_value:
                row_result["executionMode"] = "live"
                upload_result = upload_pikpak_fast_file(
                    profile_id=target_profile_id,
                    local_path=local_entry.localPath,
                    target_name=PurePosixPath(path or "/").name or Path(local_entry.localPath).name,
                    parent_id=target_parent_id or "",
                    expected_gcid=gcid_value or local_entry.gcid,
                )
                if upload_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = upload_result.note
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode,
                        "parentId": upload_result.parentId,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
                else:
                    failed += 1
                    row_result["status"] = "failed"
                    row_result["note"] = upload_result.note or "PikPak fast upload failed."
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode or "pikpak_fast_upload",
                        "parentId": upload_result.parentId or (target_parent_id or ""),
                        "error": upload_result.error,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
            elif gcid_value:
                row_result["executionMode"] = "probe"
                done += 1
                row_result["status"] = "done"
                row_result["note"] = (
                    "PikPak fast-upload candidate confirmed from current gcid/size fingerprints. "
                    "The current runtime only records candidate evidence because there is no usable local file for a live rapid-upload attempt."
                )
                row_result["liveAttempt"] = {
                    "mode": "pikpak_fast_upload_candidate",
                    "hashKind": "gcid",
                    "candidate": True,
                    "requiredInputs": ["gcid", "size"],
                    "hashValue": gcid_value,
                    "riskHint": "A live rapid-upload attempt still requires a usable local file with gcid context.",
                    "verifyOk": True,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "Current gcid/size fingerprints satisfy PikPak fast-upload precheck, but runtime remains probe-only without a local file.",
                    "verifyPayload": {
                        "gcid": gcid_value,
                        "size": int(item.get("size", 0) or 0),
                    },
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            else:
                row_result["executionMode"] = "probe"
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = "PikPak fast-upload candidate probe failed because gcid fingerprint is missing."
                row_result["liveAttempt"] = {
                    "mode": "pikpak_fast_upload_candidate",
                    "hashKind": "gcid",
                    "candidate": False,
                    "requiredInputs": ["gcid", "size"],
                    "error": "missing_gcid",
                    "riskHint": "Fast-upload candidate probe requires gcid fingerprint.",
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "quark" and target_profile_id:
            source_entry = _source_entry_for_item(source_entries_by_path, item)
            normalized = _normalized_fingerprints_for_item(item)
            md5_value = _first_text(
                source_entry.get("md5"),
                normalized.get("md5"),
                source_entry.get("etag"),
                normalized.get("etag"),
            ).lower()
            sha1_value = _first_text(
                source_entry.get("sha1"),
                normalized.get("sha1"),
            ).lower()
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None and md5_value:
                row_result["executionMode"] = "live"
                upload_result = upload_quark_fast_file(
                    profile_id=target_profile_id,
                    local_path=local_entry.localPath,
                    target_name=PurePosixPath(path or "/").name or Path(local_entry.localPath).name,
                    parent_id=target_parent_id or "0",
                    expected_md5=md5_value or local_entry.md5,
                    expected_sha1=sha1_value or local_entry.sha1,
                )
                if upload_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = upload_result.note
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode,
                        "parentId": upload_result.parentId,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
                else:
                    failed += 1
                    row_result["status"] = "failed"
                    row_result["note"] = upload_result.note or "Quark fast upload failed."
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode or "quark_fast_upload",
                        "parentId": upload_result.parentId or (target_parent_id or "0"),
                        "error": upload_result.error,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
            elif md5_value:
                row_result["executionMode"] = "probe"
                done += 1
                row_result["status"] = "done"
                row_result["note"] = (
                    "Quark fast-upload candidate confirmed from current md5/size fingerprints. "
                    "The current runtime only records candidate evidence because there is no usable local file for a live rapid-upload attempt."
                )
                row_result["liveAttempt"] = {
                    "mode": "quark_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": True,
                    "requiredInputs": ["md5", "size"],
                    "hashValue": md5_value,
                    "riskHint": "A live rapid-upload attempt still requires a usable local file with sha1/md5 context.",
                    "verifyOk": True,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "Current md5/size fingerprints satisfy Quark fast-upload precheck, but runtime remains probe-only without a local file.",
                    "verifyPayload": {
                        "md5": md5_value,
                        "size": int(item.get("size", 0) or 0),
                    },
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            else:
                row_result["executionMode"] = "probe"
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = "Quark fast-upload candidate probe failed because md5 fingerprint is missing."
                row_result["liveAttempt"] = {
                    "mode": "quark_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": False,
                    "requiredInputs": ["md5", "size"],
                    "error": "missing_md5",
                    "riskHint": "Fast-upload candidate probe requires md5 fingerprint.",
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "uc" and target_profile_id:
            source_entry = _source_entry_for_item(source_entries_by_path, item)
            normalized = _normalized_fingerprints_for_item(item)
            md5_value = _first_text(
                source_entry.get("md5"),
                normalized.get("md5"),
                source_entry.get("etag"),
                normalized.get("etag"),
            ).lower()
            sha1_value = _first_text(
                source_entry.get("sha1"),
                normalized.get("sha1"),
            ).lower()
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None and md5_value:
                row_result["executionMode"] = "live"
                upload_result = upload_uc_fast_file(
                    profile_id=target_profile_id,
                    local_path=local_entry.localPath,
                    target_name=PurePosixPath(path or "/").name or Path(local_entry.localPath).name,
                    parent_id=target_parent_id or "0",
                    expected_md5=md5_value or local_entry.md5,
                    expected_sha1=sha1_value or local_entry.sha1,
                )
                if upload_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = upload_result.note
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode,
                        "parentId": upload_result.parentId,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
                else:
                    failed += 1
                    row_result["status"] = "failed"
                    row_result["note"] = upload_result.note or "UC fast upload failed."
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode or "uc_fast_upload",
                        "parentId": upload_result.parentId or (target_parent_id or "0"),
                        "error": upload_result.error,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
            elif md5_value:
                row_result["executionMode"] = "probe"
                done += 1
                row_result["status"] = "done"
                row_result["note"] = (
                    "UC Drive fast-upload candidate confirmed from current md5/size fingerprints. "
                    "The current runtime only records candidate evidence because there is no usable local file for a live rapid-upload attempt."
                )
                row_result["liveAttempt"] = {
                    "mode": "uc_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": True,
                    "requiredInputs": ["md5", "size"],
                    "hashValue": md5_value,
                    "riskHint": "A live rapid-upload attempt still requires a usable local file with sha1/md5 context.",
                    "verifyOk": True,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "Current md5/size fingerprints satisfy UC Drive fast-upload precheck, but runtime remains probe-only without a local file.",
                    "verifyPayload": {
                        "md5": md5_value,
                        "size": int(item.get("size", 0) or 0),
                    },
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            else:
                row_result["executionMode"] = "probe"
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = "UC Drive fast-upload candidate probe failed because md5 fingerprint is missing."
                row_result["liveAttempt"] = {
                    "mode": "uc_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": False,
                    "requiredInputs": ["md5", "size"],
                    "error": "missing_md5",
                    "riskHint": "Fast-upload candidate probe requires md5 fingerprint.",
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "115_open" and target_profile_id:
            source_entry = _source_entry_for_item(source_entries_by_path, item)
            normalized = _normalized_fingerprints_for_item(item)
            sha1_value = _first_text(
                source_entry.get("sha1"),
                normalized.get("sha1"),
            ).lower()
            row_result["executionMode"] = "probe"
            if sha1_value:
                done += 1
                row_result["status"] = "done"
                row_result["note"] = (
                    "115 Open fast-upload candidate confirmed from current sha1/size fingerprints. "
                    "The current runtime only records candidate evidence and does not call a live rapid-upload API yet."
                )
                row_result["liveAttempt"] = {
                    "mode": "115_open_fast_upload_candidate",
                    "hashKind": "sha1",
                    "candidate": True,
                    "requiredInputs": ["sha1", "size"],
                    "hashValue": sha1_value,
                    "riskHint": "",
                    "verifyOk": True,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "Current sha1/size fingerprints satisfy 115 Open fast-upload precheck, but runtime remains probe-only.",
                    "verifyPayload": {
                        "sha1": sha1_value,
                        "size": int(item.get("size", 0) or 0),
                    },
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            else:
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = "115 Open fast-upload candidate probe failed because sha1 fingerprint is missing."
                row_result["liveAttempt"] = {
                    "mode": "115_open_fast_upload_candidate",
                    "hashKind": "sha1",
                    "candidate": False,
                    "requiredInputs": ["sha1", "size"],
                    "error": "missing_sha1",
                    "riskHint": "Fast-upload candidate probe requires sha1 fingerprint.",
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "xunlei" and target_profile_id:
            source_entry = _source_entry_for_item(source_entries_by_path, item)
            normalized = _normalized_fingerprints_for_item(item)
            gcid_value = _first_text(
                source_entry.get("gcid"),
                normalized.get("gcid"),
                source_entry.get("raw", {}).get("hash") if isinstance(source_entry.get("raw"), dict) else "",
                normalized.get("raw", {}).get("hash") if isinstance(normalized.get("raw"), dict) else "",
            ).lower()
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None and gcid_value:
                row_result["executionMode"] = "live"
                upload_result = upload_xunlei_fast_file(
                    profile_id=target_profile_id,
                    local_path=local_entry.localPath,
                    target_name=PurePosixPath(path or "/").name or Path(local_entry.localPath).name,
                    parent_id=target_parent_id or "",
                    expected_gcid=gcid_value or local_entry.gcid,
                )
                if upload_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = upload_result.note
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode,
                        "parentId": upload_result.parentId,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
                else:
                    failed += 1
                    row_result["status"] = "failed"
                    row_result["note"] = upload_result.note or "Xunlei fast upload failed."
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode or "xunlei_fast_upload",
                        "parentId": upload_result.parentId or (target_parent_id or ""),
                        "error": upload_result.error,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
            elif gcid_value:
                row_result["executionMode"] = "probe"
                done += 1
                row_result["status"] = "done"
                row_result["note"] = (
                    "Xunlei fast-upload candidate confirmed from current gcid/size fingerprints. "
                    "The current runtime only records candidate evidence because there is no usable local file for a live rapid-upload attempt."
                )
                row_result["liveAttempt"] = {
                    "mode": "xunlei_fast_upload_candidate",
                    "hashKind": "gcid",
                    "candidate": True,
                    "requiredInputs": ["gcid", "size"],
                    "hashValue": gcid_value,
                    "riskHint": "A live rapid-upload attempt still requires a usable local file with gcid context.",
                    "verifyOk": True,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "Current gcid/size fingerprints satisfy Xunlei fast-upload precheck, but runtime remains probe-only without a local file.",
                    "verifyPayload": {
                        "gcid": gcid_value,
                        "size": int(item.get("size", 0) or 0),
                    },
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            else:
                row_result["executionMode"] = "probe"
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = "Xunlei fast-upload candidate probe failed because gcid fingerprint is missing."
                row_result["liveAttempt"] = {
                    "mode": "xunlei_fast_upload_candidate",
                    "hashKind": "gcid",
                    "candidate": False,
                    "requiredInputs": ["gcid", "size"],
                    "error": "missing_gcid",
                    "riskHint": "Fast-upload candidate probe requires gcid fingerprint.",
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "aliyundrive_open" and target_profile_id:
            source_entry = _source_entry_for_item(source_entries_by_path, item)
            normalized = _normalized_fingerprints_for_item(item)
            md5_value = _first_text(
                source_entry.get("md5"),
                normalized.get("md5"),
                source_entry.get("etag"),
                normalized.get("etag"),
            ).lower()
            row_result["executionMode"] = "probe"
            if md5_value:
                done += 1
                row_result["status"] = "done"
                row_result["note"] = (
                    "Aliyun Drive Open fast-upload candidate confirmed from current md5/size fingerprints. "
                    "The current runtime only records candidate evidence and does not call a live rapid-upload API yet."
                )
                row_result["liveAttempt"] = {
                    "mode": "aliyundrive_open_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": True,
                    "requiredInputs": ["md5", "size"],
                    "hashValue": md5_value,
                    "riskHint": "",
                    "verifyOk": True,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "Current md5/size fingerprints satisfy Aliyun Drive Open fast-upload precheck, but runtime remains probe-only.",
                    "verifyPayload": {
                        "md5": md5_value,
                        "size": int(item.get("size", 0) or 0),
                    },
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            else:
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = "Aliyun Drive Open fast-upload candidate probe failed because md5 fingerprint is missing."
                row_result["liveAttempt"] = {
                    "mode": "aliyundrive_open_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": False,
                    "requiredInputs": ["md5", "size"],
                    "error": "missing_md5",
                    "riskHint": "Fast-upload candidate probe requires md5 fingerprint.",
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "123_open" and target_profile_id:
            source_entry = _source_entry_for_item(source_entries_by_path, item)
            normalized = _normalized_fingerprints_for_item(item)
            md5_value = _first_text(
                source_entry.get("md5"),
                normalized.get("md5"),
                source_entry.get("etag"),
                normalized.get("etag"),
            ).lower()
            row_result["executionMode"] = "probe"
            if md5_value:
                done += 1
                row_result["status"] = "done"
                row_result["note"] = (
                    "123Pan Open fast-upload candidate confirmed from current md5/size fingerprints. "
                    "The current runtime only records candidate evidence and does not call a live rapid-upload API yet."
                )
                row_result["liveAttempt"] = {
                    "mode": "123_open_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": True,
                    "requiredInputs": ["md5", "size"],
                    "hashValue": md5_value,
                    "riskHint": "",
                    "verifyOk": True,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "Current md5/size fingerprints satisfy 123Pan Open fast-upload precheck, but runtime remains probe-only.",
                    "verifyPayload": {
                        "md5": md5_value,
                        "size": int(item.get("size", 0) or 0),
                    },
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            else:
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = "123Pan Open fast-upload candidate probe failed because md5 fingerprint is missing."
                row_result["liveAttempt"] = {
                    "mode": "123_open_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": False,
                    "requiredInputs": ["md5", "size"],
                    "error": "missing_md5",
                    "riskHint": "Fast-upload candidate probe requires md5 fingerprint.",
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            results.append(row_result)
            continue

        if strategy == "fast_upload" and target_provider == "189cloud" and target_profile_id:
            source_entry = _source_entry_for_item(source_entries_by_path, item)
            normalized = _normalized_fingerprints_for_item(item)
            md5_value = _first_text(
                source_entry.get("md5"),
                normalized.get("md5"),
                source_entry.get("etag"),
                normalized.get("etag"),
            ).lower()
            access_token, signature, date_value = _tianyi_account_auth_fields(target_profile_id)
            row_result["executionMode"] = "probe"
            if md5_value and access_token and signature and date_value:
                done += 1
                row_result["status"] = "done"
                row_result["note"] = (
                    "189Cloud fast-upload candidate confirmed from current md5/size fingerprints and account-level write auth. "
                    "The current runtime only records candidate evidence and does not call a live rapid-upload API yet."
                )
                row_result["liveAttempt"] = {
                    "mode": "189cloud_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": True,
                    "requiredInputs": ["md5", "size"],
                    "requiredAuth": ["AccessToken", "Signature", "Date"],
                    "hashValue": md5_value,
                    "riskHint": "",
                    "verifyOk": True,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "Current md5/size fingerprints plus account-level write auth satisfy 189Cloud fast-upload precheck, but runtime remains probe-only.",
                    "verifyPayload": {
                        "md5": md5_value,
                        "size": int(item.get("size", 0) or 0),
                    },
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            else:
                failed += 1
                missing_parts: list[str] = []
                if not md5_value:
                    missing_parts.append("md5")
                if not access_token:
                    missing_parts.append("AccessToken")
                if not signature:
                    missing_parts.append("Signature")
                if not date_value:
                    missing_parts.append("Date")
                row_result["status"] = "failed"
                row_result["note"] = (
                    "189Cloud fast-upload candidate probe is not ready because required fingerprints or account-level write auth are missing."
                )
                row_result["liveAttempt"] = {
                    "mode": "189cloud_fast_upload_candidate",
                    "hashKind": "md5",
                    "candidate": False,
                    "requiredInputs": ["md5", "size"],
                    "requiredAuth": ["AccessToken", "Signature", "Date"],
                    "error": f"missing_{'_'.join(missing_parts).lower()}",
                    "riskHint": "189Cloud fast-upload candidate probe requires md5 plus account-level AccessToken/Signature/Date.",
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": PurePosixPath(path or "/").name or path,
                    "conflictAction": "",
                }
            results.append(row_result)
            continue

        if strategy == "download_upload" and target_provider == "guangya" and target_profile_id:
            row_result["executionMode"] = "live"
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                live_fallback = fetch_guangya_live_fast_check(
                    profile_id=target_profile_id,
                    entries=[local_entry],
                )
                fallback_summary = {
                    "note": str(live_fallback.note or ""),
                    "error": str(live_fallback.error or ""),
                    "riskHint": str(live_fallback.riskHint or ""),
                }
                live_row = next((row for row in live_fallback.items if str(row.get("path") or "") == path), {})
                if live_row and bool(live_row.get("canFastUpload")):
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = str(live_row.get("note") or "Guangya local-file fallback hit provider inventory.")
                    row_result["liveAttempt"] = {
                        "mode": "guangya_local_fallback_fast_check",
                        "hashKind": live_row.get("hashKind", ""),
                        "canFastUpload": True,
                        "localPath": local_entry.localPath,
                        "riskHint": "",
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = str(
                    (live_row or {}).get("note")
                    or fallback_summary.get("note")
                    or "Local file is present, but Guangya did not report an instant hit and binary upload is not implemented yet."
                )
                upload_result = upload_guangya_local_file(
                    profile_id=target_profile_id,
                    local_path=local_entry.localPath,
                    target_name=PurePosixPath(path or "/").name or Path(local_entry.localPath).name,
                    parent_id=target_parent_id,
                    expected_md5=local_entry.md5,
                    conflict_policy=conflict_policy,
                )
                if upload_result.ok:
                    done += 1
                    failed -= 1
                    row_result["status"] = "done"
                    row_result["note"] = upload_result.note
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode,
                        "parentId": upload_result.parentId,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "conflictPolicy": conflict_policy,
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
                    results.append(row_result)
                    continue
                row_result["liveAttempt"] = {
                    "mode": upload_result.mode or "guangya_local_fallback_fast_check",
                    "hashKind": (live_row or {}).get("hashKind", ""),
                    "canFastUpload": bool((live_row or {}).get("canFastUpload")),
                    "localPath": local_entry.localPath,
                    "error": upload_result.error or (live_row or {}).get("error", "") or fallback_summary.get("error", ""),
                    "riskHint": upload_result.riskHint or (live_row or {}).get("riskHint", "") or fallback_summary.get("riskHint", ""),
                    "parentId": upload_result.parentId,
                    "conflictPolicy": conflict_policy,
                    "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                    "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                }
                row_result["note"] = upload_result.note or row_result["note"]
                results.append(row_result)
                continue

        if strategy == "download_upload" and target_provider == "aliyundrive_open" and target_profile_id:
            row_result["executionMode"] = "live"
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                upload_result = upload_aliyun_open_local_file(
                    profile_id=target_profile_id,
                    local_path=local_entry.localPath,
                    target_name=PurePosixPath(path or "/").name or Path(local_entry.localPath).name,
                    parent_file_id=target_parent_id or "root",
                    expected_md5=local_entry.md5,
                    conflict_policy=conflict_policy,
                )
                if upload_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = upload_result.note
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode,
                        "parentId": upload_result.parentId,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "conflictPolicy": conflict_policy,
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = upload_result.note or "Aliyun Drive Open runtime upload failed."
                row_result["liveAttempt"] = {
                    "mode": upload_result.mode or "aliyundrive_open_upload",
                    "parentId": upload_result.parentId or (target_parent_id or "root"),
                    "error": upload_result.error,
                    "riskHint": upload_result.riskHint,
                    "payload": upload_result.payload or {},
                    "verifyOk": upload_result.verifyOk,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "conflictPolicy": conflict_policy,
                    "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                    "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                }
                results.append(row_result)
                continue

        if strategy == "download_upload" and target_provider == "123_open" and target_profile_id:
            row_result["executionMode"] = "live"
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                upload_result = upload_123_open_local_file(
                    profile_id=target_profile_id,
                    local_path=local_entry.localPath,
                    target_name=PurePosixPath(path or "/").name or Path(local_entry.localPath).name,
                    parent_file_id=target_parent_id or "0",
                    expected_md5=local_entry.md5 or local_entry.etag,
                    conflict_policy=conflict_policy,
                )
                if upload_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = upload_result.note
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode,
                        "parentId": upload_result.parentId,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "conflictPolicy": conflict_policy,
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = upload_result.note or "123Pan Open runtime upload failed."
                row_result["liveAttempt"] = {
                    "mode": upload_result.mode or "123_open_upload",
                    "parentId": upload_result.parentId or (target_parent_id or "0"),
                    "error": upload_result.error,
                    "riskHint": upload_result.riskHint,
                    "payload": upload_result.payload or {},
                    "verifyOk": upload_result.verifyOk,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "conflictPolicy": conflict_policy,
                    "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                    "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                }
                results.append(row_result)
                continue

        if strategy == "download_upload" and target_provider == "115_open" and target_profile_id:
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                probe_name = _probe_dir_name(str(task.get("taskId") or ""), path)
                probe_result = fetch_115_open_create_folder(
                    profile_id=target_profile_id,
                    parent_id=target_parent_id or "0",
                    dir_name=probe_name,
                )
                row_result["executionMode"] = "probe"
                if probe_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = (
                        "115 Open runtime write probe succeeded through live create_dir. "
                        "The current file transfer still completes with mock/download fallback flow."
                    )
                    row_result["liveAttempt"] = {
                        "mode": "115_open_create_dir_probe",
                        "parentId": target_parent_id or "0",
                        "riskHint": "",
                        "payload": probe_result.payload or {},
                        "verifyOk": True,
                        "verifyMode": "create_dir_response",
                        "verifyNote": probe_result.note,
                        "verifyPayload": probe_result.payload or {},
                        "resolvedTargetName": probe_name,
                        "conflictAction": "auto_rename_new",
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = probe_result.note or "115 Open runtime write probe failed."
                row_result["liveAttempt"] = {
                    "mode": "115_open_create_dir_probe",
                    "parentId": target_parent_id or "0",
                    "error": probe_result.error,
                    "riskHint": probe_result.note,
                    "payload": probe_result.payload or {},
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": probe_name,
                    "conflictAction": "",
                }
                results.append(row_result)
                continue

        if strategy == "download_upload" and target_provider == "xunlei" and target_profile_id:
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                probe_name = _probe_dir_name(str(task.get("taskId") or ""), path)
                probe_result = fetch_xunlei_create_folder(
                    profile_id=target_profile_id,
                    parent_id=target_parent_id,
                    dir_name=probe_name,
                )
                row_result["executionMode"] = "probe"
                if probe_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = (
                        "Xunlei runtime write probe succeeded through live create_dir. "
                        "The current file transfer still completes with mock/download fallback flow."
                    )
                    row_result["liveAttempt"] = {
                        "mode": "xunlei_create_dir_probe",
                        "parentId": target_parent_id,
                        "riskHint": "",
                        "payload": probe_result.payload or {},
                        "verifyOk": True,
                        "verifyMode": "create_dir_response",
                        "verifyNote": probe_result.note,
                        "verifyPayload": probe_result.payload or {},
                        "resolvedTargetName": probe_name,
                        "conflictAction": "auto_rename_new",
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = probe_result.note or "Xunlei runtime write probe failed."
                row_result["liveAttempt"] = {
                    "mode": "xunlei_create_dir_probe",
                    "parentId": target_parent_id,
                    "error": probe_result.error,
                    "riskHint": probe_result.note,
                    "payload": probe_result.payload or {},
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": probe_name,
                    "conflictAction": "",
                }
                results.append(row_result)
                continue

        if strategy == "download_upload" and target_provider == "pikpak" and target_profile_id:
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                probe_name = _probe_dir_name(str(task.get("taskId") or ""), path)
                probe_result = fetch_pikpak_create_folder(
                    profile_id=target_profile_id,
                    parent_id=target_parent_id,
                    dir_name=probe_name,
                )
                row_result["executionMode"] = "probe"
                if probe_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = (
                        "PikPak runtime write probe succeeded through live create_dir. "
                        "The current file transfer still completes with mock/download fallback flow."
                    )
                    row_result["liveAttempt"] = {
                        "mode": "pikpak_create_dir_probe",
                        "parentId": target_parent_id,
                        "riskHint": "",
                        "payload": probe_result.payload or {},
                        "verifyOk": True,
                        "verifyMode": "create_dir_response",
                        "verifyNote": probe_result.note,
                        "verifyPayload": probe_result.payload or {},
                        "resolvedTargetName": probe_name,
                        "conflictAction": "auto_rename_new",
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = probe_result.note or "PikPak runtime write probe failed."
                row_result["liveAttempt"] = {
                    "mode": "pikpak_create_dir_probe",
                    "parentId": target_parent_id,
                    "error": probe_result.error,
                    "riskHint": probe_result.note,
                    "payload": probe_result.payload or {},
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": probe_name,
                    "conflictAction": "",
                }
                results.append(row_result)
                continue

        if strategy == "download_upload" and target_provider == "baidu_netdisk" and target_profile_id:
            row_result["executionMode"] = "live"
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                upload_result = upload_baidu_local_file(
                    profile_id=target_profile_id,
                    local_path=local_entry.localPath,
                    target_name=PurePosixPath(path or "/").name or Path(local_entry.localPath).name,
                    parent_dir=target_parent_id or "/",
                    expected_md5=local_entry.md5 or local_entry.etag,
                    conflict_policy=conflict_policy,
                )
                if upload_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = upload_result.note
                    row_result["liveAttempt"] = {
                        "mode": upload_result.mode,
                        "parentId": upload_result.parentId,
                        "riskHint": upload_result.riskHint,
                        "payload": upload_result.payload or {},
                        "verifyOk": upload_result.verifyOk,
                        "verifyMode": upload_result.verifyMode,
                        "verifyNote": upload_result.verifyNote,
                        "verifyPayload": upload_result.verifyPayload or {},
                        "conflictPolicy": conflict_policy,
                        "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                        "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = upload_result.note or "Baidu Netdisk runtime upload failed."
                row_result["liveAttempt"] = {
                    "mode": upload_result.mode or "baidu_netdisk_upload",
                    "parentId": upload_result.parentId or (target_parent_id or "/"),
                    "error": upload_result.error,
                    "riskHint": upload_result.riskHint,
                    "payload": upload_result.payload or {},
                    "verifyOk": upload_result.verifyOk,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "conflictPolicy": conflict_policy,
                    "resolvedTargetName": (upload_result.payload or {}).get("resolvedTargetName", ""),
                    "conflictAction": (upload_result.payload or {}).get("conflictAction", ""),
                }
                results.append(row_result)
                continue

        if strategy == "download_upload" and target_provider == "189cloud" and target_profile_id:
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                probe_name = _probe_dir_name(str(task.get("taskId") or ""), path)
                probe_result = fetch_tianyi_create_folder(
                    profile_id=target_profile_id,
                    parent_id=target_parent_id,
                    dir_name=probe_name,
                )
                row_result["executionMode"] = "probe"
                if probe_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = (
                        "189Cloud runtime write probe succeeded through createFolder.action. "
                        "The current file transfer still completes with mock/download fallback flow."
                    )
                    row_result["liveAttempt"] = {
                        "mode": "189cloud_create_dir_probe",
                        "parentId": target_parent_id,
                        "riskHint": "",
                        "payload": probe_result.payload or {},
                        "requiredAuth": list((probe_result.payload or {}).get("requiredAuth") or []),
                        "verifyOk": True,
                        "verifyMode": "create_dir_response",
                        "verifyNote": probe_result.note,
                        "verifyPayload": probe_result.payload or {},
                        "resolvedTargetName": probe_name,
                        "conflictAction": "auto_rename_new",
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = probe_result.note or "189Cloud runtime write probe failed."
                row_result["liveAttempt"] = {
                    "mode": "189cloud_create_dir_probe",
                    "parentId": target_parent_id,
                    "error": probe_result.error,
                    "riskHint": probe_result.note,
                    "payload": probe_result.payload or {},
                    "requiredAuth": list((probe_result.payload or {}).get("requiredAuth") or []),
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": probe_name,
                    "conflictAction": "",
                }
                results.append(row_result)
                continue

        if strategy == "download_upload" and target_provider == "quark" and target_profile_id:
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                probe_name = _probe_dir_name(str(task.get("taskId") or ""), path)
                probe_result = fetch_quark_create_folder(
                    profile_id=target_profile_id,
                    parent_id=target_parent_id or "0",
                    dir_name=probe_name,
                )
                row_result["executionMode"] = "probe"
                if probe_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = (
                        "Quark runtime write probe succeeded through live create_dir. "
                        "The current file transfer still completes with mock/download fallback flow."
                    )
                    row_result["liveAttempt"] = {
                        "mode": "quark_create_dir_probe",
                        "parentId": target_parent_id or "0",
                        "riskHint": "",
                        "payload": probe_result.payload or {},
                        "verifyOk": True,
                        "verifyMode": "create_dir_response",
                        "verifyNote": probe_result.note,
                        "verifyPayload": probe_result.payload or {},
                        "resolvedTargetName": probe_name,
                        "conflictAction": "auto_rename_new",
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = probe_result.note or "Quark runtime write probe failed."
                row_result["liveAttempt"] = {
                    "mode": "quark_create_dir_probe",
                    "parentId": target_parent_id or "0",
                    "error": probe_result.error,
                    "riskHint": probe_result.note,
                    "payload": probe_result.payload or {},
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": probe_name,
                    "conflictAction": "",
                }
                results.append(row_result)
                continue

        if strategy == "download_upload" and target_provider == "uc" and target_profile_id:
            source_entry = source_entries_by_path.get(path, {})
            local_entry = _materialize_local_source_entry(source_entry, path, int(item.get("size", 0) or 0))
            if local_entry is not None:
                probe_name = _probe_dir_name(str(task.get("taskId") or ""), path)
                probe_result = fetch_uc_create_folder(
                    profile_id=target_profile_id,
                    parent_id=target_parent_id or "0",
                    dir_name=probe_name,
                )
                row_result["executionMode"] = "probe"
                if probe_result.ok:
                    done += 1
                    row_result["status"] = "done"
                    row_result["note"] = (
                        "UC Drive runtime write probe succeeded through live create_dir. "
                        "The current file transfer still completes with mock/download fallback flow."
                    )
                    row_result["liveAttempt"] = {
                        "mode": "uc_create_dir_probe",
                        "parentId": target_parent_id or "0",
                        "riskHint": "",
                        "payload": probe_result.payload or {},
                        "verifyOk": True,
                        "verifyMode": "create_dir_response",
                        "verifyNote": probe_result.note,
                        "verifyPayload": probe_result.payload or {},
                        "resolvedTargetName": probe_name,
                        "conflictAction": "auto_rename_new",
                    }
                    results.append(row_result)
                    continue
                failed += 1
                row_result["status"] = "failed"
                row_result["note"] = probe_result.note or "UC Drive runtime write probe failed."
                row_result["liveAttempt"] = {
                    "mode": "uc_create_dir_probe",
                    "parentId": target_parent_id or "0",
                    "error": probe_result.error,
                    "riskHint": probe_result.note,
                    "payload": probe_result.payload or {},
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "",
                    "verifyPayload": {},
                    "resolvedTargetName": probe_name,
                    "conflictAction": "",
                }
                results.append(row_result)
                continue

        if strategy == "download_upload" and int(item.get("size", 0)) > 512 * 1024 * 1024:
            row_result["executionMode"] = "blocked"
            failed += 1
            row_result["status"] = "failed"
            row_result["note"] = "Download-upload fallback is blocked for files larger than 512MB in the current runtime."
            row_result["liveAttempt"] = {
                "mode": "download_upload_blocked_by_size_limit",
                "riskHint": "download_upload_size_limit_exceeded",
                "verifyOk": False,
                "verifyMode": "",
                "verifyNote": "",
                "verifyPayload": {},
                "resolvedTargetName": str(item.get("targetName") or ""),
                "conflictAction": "",
                "error": "download_upload_blocked_by_size_limit",
                "requiredAuth": [],
                "payload": {
                    "size": int(item.get("size", 0) or 0),
                    "limitBytes": 512 * 1024 * 1024,
                    "strategy": strategy,
                },
            }
            results.append(row_result)
            continue
        row_result["executionMode"] = "mock"
        done += 1
        row_result["status"] = "done"
        row_result["note"] = "Task runtime completed the item with the current mock/download fallback flow."
        results.append(row_result)
    runtime_summary = _result_runtime_summary(results)
    task["progress"]["done"] = done
    task["progress"]["failed"] = failed
    task["progress"]["probeOnly"] = int(runtime_summary.get("probeOnlyCount", 0) or 0)
    task["progress"]["candidateOnly"] = int(runtime_summary.get("candidateOnlyCount", 0) or 0)
    task["progress"]["liveSuccess"] = int(runtime_summary.get("liveSuccessCount", 0) or 0)
    task["progress"]["liveFailed"] = int(runtime_summary.get("liveFailedCount", 0) or 0)
    task["results"] = results
    completion_kind = str(runtime_summary.get("completionKind") or "")
    has_real_transfer_success = bool(runtime_summary.get("hasRealTransferSuccess"))
    if failed > 0:
        task["state"] = "completed_with_errors"
    elif completion_kind == "candidate_only":
        task["state"] = "completed_candidate_only"
    elif completion_kind in {"probe_only", "mixed_non_live"} and not has_real_transfer_success:
        task["state"] = "completed_probe_only"
    else:
        task["state"] = "completed"
    task["updatedAt"] = _now()
    _persist_task_runtime_evidence(task, results)
    refresh_task_summary(task)
    return task


def pause_task(task_id: str) -> dict[str, object]:
    task = _TASKS[task_id]
    if "pause" not in allowed_task_actions(task):
        return _set_action_error(task, "pause", f"pause_not_allowed_from_{str(task.get('state') or 'unknown')}")
    _clear_action_error(task)
    task["state"] = "paused"
    task["updatedAt"] = _now()
    refresh_task_summary(task)
    return task


def resume_task(task_id: str) -> dict[str, object]:
    task = _TASKS[task_id]
    if "resume" not in allowed_task_actions(task):
        return _set_action_error(task, "resume", f"resume_not_allowed_from_{str(task.get('state') or 'unknown')}")
    _clear_action_error(task)
    task["state"] = "ready"
    task["risk"]["paused"] = False
    task["risk"]["reason"] = ""
    task["updatedAt"] = _now()
    refresh_task_summary(task)
    return task


def acknowledge_task_risk(task_id: str) -> dict[str, object]:
    task = _TASKS[task_id]
    if "acknowledge_risk" not in allowed_task_actions(task):
        return _set_action_error(task, "acknowledge_risk", f"acknowledge_risk_not_allowed_from_{str(task.get('state') or 'unknown')}")
    _clear_action_error(task)
    guard = dict(task.get("guard") or {})
    required = dict(guard.get("requiresAcknowledgement") or {})
    acknowledged = dict(guard.get("acknowledged") or {})
    for key, required_value in required.items():
        if bool(required_value):
            acknowledged[key] = True
    guard["acknowledged"] = acknowledged
    warning_reasons = list(guard.get("warningReasons") or [])
    guard["warningReasons"] = [item for item in warning_reasons if "requires explicit confirmation" not in str(item)]
    task["guard"] = guard

    pending_manual = int(((task.get("plan") or {}).get("summary") or {}).get("strategyCounts", {}).get("pending_manual", 0) or 0)
    risk_pause = pending_manual >= 3
    if bool(guard.get("hardBlocked")):
        task["state"] = "blocked"
        task["risk"]["paused"] = True
        task["risk"]["reason"] = "guard_blocked"
    else:
        task["state"] = "risk_paused" if risk_pause else "ready"
        task["risk"]["paused"] = risk_pause
        task["risk"]["reason"] = "too_many_pending_manual_items" if risk_pause else ""
    task["updatedAt"] = _now()
    refresh_task_summary(task)
    return task


def retry_task(task_id: str) -> dict[str, object]:
    task = _TASKS[task_id]
    if "retry" not in allowed_task_actions(task):
        return _set_action_error(task, "retry", f"retry_not_allowed_from_{str(task.get('state') or 'unknown')}")
    _clear_action_error(task)
    task["state"] = "ready"
    task["progress"]["done"] = 0
    task["progress"]["failed"] = 0
    task["updatedAt"] = _now()
    refresh_task_summary(task)
    return task
