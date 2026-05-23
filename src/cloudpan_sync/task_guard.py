from __future__ import annotations

from .auth_profile_view import auth_profile_view
from .auth_store import get_profile
from .models import TaskCreateRequest


def evaluate_task_guard(payload: TaskCreateRequest, plan: dict[str, object]) -> dict[str, object]:
    target_profile_view: dict[str, object] | None = None
    blocking_reasons: list[str] = []
    warning_reasons: list[str] = []
    requires_ack = {
        "pendingManual": False,
        "downloadUpload": False,
    }
    acknowledged = {
        "pendingManual": bool(payload.acknowledgePendingManual),
        "downloadUpload": bool(payload.acknowledgeDownloadUpload),
    }

    if payload.targetProfileId:
        profile = get_profile(payload.targetProfileId)
        if profile is not None:
            target_profile_view = auth_profile_view(profile)
            if target_profile_view.get("profileReady") is False:
                warning_reasons.append(
                    f"targetProfile not ready: {(target_profile_view.get('missingFieldHints') or [])}"
                )
            if target_profile_view.get("writeReady") is False:
                blocking_reasons.append(
                    "targetProfile not write-ready: "
                    + " | ".join((target_profile_view.get("writeMissingFieldHints") or []) or ["(unknown)"])
                )
        else:
            warning_reasons.append(f"targetProfile missing: {payload.targetProfileId}")

    strategy_counts = dict((plan.get("summary") or {}).get("strategyCounts") or {})
    if int(strategy_counts.get("pending_manual", 0) or 0) > 0:
        requires_ack["pendingManual"] = True
        if not acknowledged["pendingManual"]:
            warning_reasons.append("pending_manual requires explicit confirmation")
    if int(strategy_counts.get("download_upload", 0) or 0) > 0:
        requires_ack["downloadUpload"] = True
        if not acknowledged["downloadUpload"]:
            warning_reasons.append("download_upload requires explicit confirmation")

    items = list(plan.get("items") or [])
    unsupported = next((item for item in items if str((item or {}).get("conflictSupportStatus") or "") == "unsupported"), None)
    if unsupported is not None:
        blocking_reasons.append(
            f"conflict unsupported: {str(unsupported.get('path') or '')} | {str(unsupported.get('conflictNote') or '')}"
        )

    return {
        "hardBlocked": bool(blocking_reasons),
        "blockingReasons": blocking_reasons,
        "warningReasons": warning_reasons,
        "requiresAcknowledgement": requires_ack,
        "acknowledged": acknowledged,
        "targetProfile": target_profile_view,
    }
