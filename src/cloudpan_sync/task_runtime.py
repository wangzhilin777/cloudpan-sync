from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .models import TaskCreateRequest
from .planner import build_transfer_plan


_TASKS: dict[str, dict[str, object]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def list_tasks() -> list[dict[str, object]]:
    return sorted(_TASKS.values(), key=lambda x: str(x.get("createdAt", "")), reverse=True)


def get_task(task_id: str) -> dict[str, object] | None:
    return _TASKS.get(task_id)


def create_task(payload: TaskCreateRequest) -> dict[str, object]:
    plan = build_transfer_plan(
        source_provider=payload.sourceProvider,
        target_provider=payload.targetProvider,
        entries=payload.entries,
        threshold_mb=payload.thresholdMB,
        selected_roots=payload.selectedRoots,
    ).model_dump()
    task_id = str(uuid4())
    now = _now()
    risk_pause = bool(plan.get("summary", {}).get("strategyCounts", {}).get("pending_manual", 0) >= 3)
    state = "risk_paused" if risk_pause else "ready"
    task = {
        "taskId": task_id,
        "state": state,
        "sourceProvider": payload.sourceProvider,
        "targetProvider": payload.targetProvider,
        "createdAt": now,
        "updatedAt": now,
        "plan": plan,
        "progress": {
            "total": int(plan.get("summary", {}).get("total", 0)),
            "done": 0,
            "failed": 0,
            "pendingManual": int(plan.get("summary", {}).get("strategyCounts", {}).get("pending_manual", 0)),
        },
        "risk": {
            "paused": risk_pause,
            "reason": "too_many_pending_manual_items" if risk_pause else "",
        },
    }
    _TASKS[task_id] = task
    return task


def run_task(task_id: str) -> dict[str, object]:
    task = _TASKS[task_id]
    if task["state"] in {"paused", "risk_paused"}:
        return task
    if task["state"] == "completed":
        return task
    task["state"] = "running"
    items = task["plan"]["items"]
    done = 0
    failed = 0
    for item in items:
        strategy = item.get("strategy")
        if strategy == "pending_manual":
            continue
        if strategy == "download_upload" and int(item.get("size", 0)) > 512 * 1024 * 1024:
            failed += 1
            continue
        done += 1
    task["progress"]["done"] = done
    task["progress"]["failed"] = failed
    task["state"] = "completed" if failed == 0 else "completed_with_errors"
    task["updatedAt"] = _now()
    return task


def pause_task(task_id: str) -> dict[str, object]:
    task = _TASKS[task_id]
    if task["state"] in {"running", "ready", "completed_with_errors"}:
        task["state"] = "paused"
        task["updatedAt"] = _now()
    return task


def resume_task(task_id: str) -> dict[str, object]:
    task = _TASKS[task_id]
    if task["state"] in {"paused", "risk_paused", "completed_with_errors"}:
        task["state"] = "ready"
        task["risk"]["paused"] = False
        task["risk"]["reason"] = ""
        task["updatedAt"] = _now()
    return task


def retry_task(task_id: str) -> dict[str, object]:
    task = _TASKS[task_id]
    task["state"] = "ready"
    task["progress"]["done"] = 0
    task["progress"]["failed"] = 0
    task["updatedAt"] = _now()
    return task
