from __future__ import annotations

import json
from datetime import datetime, timezone

from .auth_store import DATA_DIR


RUNTIME_EVIDENCE_FILE = DATA_DIR / "task_runtime_evidence.json"


def _read_rows() -> list[dict[str, object]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RUNTIME_EVIDENCE_FILE.exists():
        return []
    text = RUNTIME_EVIDENCE_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        rows = json.loads(text)
    except json.JSONDecodeError:
        return []
    return rows if isinstance(rows, list) else []


def _write_rows(rows: list[dict[str, object]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_EVIDENCE_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def list_task_runtime_evidence() -> list[dict[str, object]]:
    return _read_rows()


def latest_task_runtime_evidence() -> list[dict[str, object]]:
    latest_by_key: dict[str, dict[str, object]] = {}
    for row in _read_rows():
        provider_key = str(row.get("providerKey") or "")
        profile_id = str(row.get("profileId") or "")
        path = str(row.get("path") or "")
        mode = str(row.get("mode") or "")
        if not provider_key or not path:
            continue
        latest_by_key[f"{provider_key}::{profile_id}::{path}::{mode}"] = row
    return list(latest_by_key.values())


def task_runtime_evidence_summary() -> dict[str, object]:
    latest = latest_task_runtime_evidence()
    return {
        "sampleCount": len(latest),
        "providerCount": len({str(row.get("providerKey") or "") for row in latest if str(row.get("providerKey") or "")}),
        "profileCount": len({str(row.get("profileId") or "") for row in latest if str(row.get("profileId") or "")}),
        "successCount": sum(1 for row in latest if bool(row.get("success"))),
        "failedCount": sum(1 for row in latest if not bool(row.get("success"))),
        "verifyOkCount": sum(1 for row in latest if bool(row.get("verifyOk"))),
        "conflictHandledCount": sum(1 for row in latest if str(row.get("conflictAction") or "")),
        "providers": sorted({str(row.get("providerKey") or "") for row in latest if str(row.get("providerKey") or "")}),
    }


def build_task_runtime_evidence_payload() -> dict[str, object]:
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "items": list_task_runtime_evidence(),
        "latestItems": latest_task_runtime_evidence(),
        "summary": task_runtime_evidence_summary(),
    }


def task_runtime_evidence_to_markdown(payload: dict[str, object]) -> str:
    summary = dict(payload.get("summary") or {})
    lines: list[str] = []
    lines.append("# CloudPan Sync 任务运行真实样本报告")
    lines.append("")
    lines.append(f"- 生成时间：`{payload.get('generatedAt', '')}`")
    lines.append(
        "- 汇总："
        f" `sampleCount={summary.get('sampleCount', 0)}`"
        f" `providerCount={summary.get('providerCount', 0)}`"
        f" `profileCount={summary.get('profileCount', 0)}`"
        f" `successCount={summary.get('successCount', 0)}`"
        f" `failedCount={summary.get('failedCount', 0)}`"
        f" `verifyOkCount={summary.get('verifyOkCount', 0)}`"
        f" `conflictHandledCount={summary.get('conflictHandledCount', 0)}`"
    )
    lines.append("")
    for row in payload.get("latestItems", []):
        item = dict(row or {})
        lines.append(
            f"- {item.get('providerKey', '')} profile={item.get('profileId', '')} path={item.get('path', '')} "
            f"mode={item.get('mode', '')} success={item.get('success', False)} verifyOk={item.get('verifyOk', False)} "
            f"verifyMode={item.get('verifyMode', '')} conflictAction={item.get('conflictAction', '')} "
            f"resolvedTargetName={item.get('resolvedTargetName', '')} requiredAuth={','.join(item.get('requiredAuth', []) or [])} error={item.get('error', '')}"
        )
    if not payload.get("latestItems"):
        lines.append("- none")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def save_task_runtime_evidence(row: dict[str, object]) -> dict[str, object]:
    rows = _read_rows()
    identity = (
        str(row.get("taskId") or ""),
        str(row.get("providerKey") or ""),
        str(row.get("profileId") or ""),
        str(row.get("path") or ""),
        str(row.get("mode") or ""),
    )
    replaced = False
    for index, existing in enumerate(rows):
        existing_identity = (
            str(existing.get("taskId") or ""),
            str(existing.get("providerKey") or ""),
            str(existing.get("profileId") or ""),
            str(existing.get("path") or ""),
            str(existing.get("mode") or ""),
        )
        if existing_identity == identity:
            rows[index] = row
            replaced = True
            break
    if not replaced:
        rows.append(row)
    _write_rows(rows)
    return row


def delete_task_runtime_evidence(profile_id: str) -> None:
    rows = _read_rows()
    kept = [row for row in rows if str(row.get("profileId") or "") != str(profile_id or "")]
    _write_rows(kept)
