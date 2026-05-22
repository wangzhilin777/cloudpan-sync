from __future__ import annotations

from .models import PlanItem, PlanSummary, SourceEntry, TransferPlan
from .provider_registry import get_provider_profile


def _missing_fast_inputs(entry: SourceEntry, required: list[str]) -> list[str]:
    missing: list[str] = []
    for key in required:
        if key == "size":
            if int(entry.size) <= 0:
                missing.append(key)
        elif key == "name":
            if not entry.path.strip():
                missing.append(key)
        else:
            if not getattr(entry, key, ""):
                missing.append(key)
    return missing


def build_transfer_plan(
    source_provider: str,
    target_provider: str,
    entries: list[SourceEntry],
    threshold_mb: int,
) -> TransferPlan:
    target_profile = get_provider_profile(target_provider)
    if target_profile is None:
        raise ValueError(f"Unknown target provider: {target_provider}")

    threshold_bytes = max(0, int(threshold_mb)) * 1024 * 1024
    items: list[PlanItem] = []
    counts: dict[str, int] = {}

    for entry in entries:
        missing = _missing_fast_inputs(entry, target_profile.fastUploadInputs)
        if not missing:
            strategy = "fast_upload"
            reason = "All required fast-upload inputs are available."
        elif threshold_bytes > 0 and entry.size <= threshold_bytes:
            strategy = "download_upload"
            reason = "Fast-upload inputs are missing, but size is within fallback threshold."
        else:
            strategy = "pending_manual"
            reason = "Fast-upload inputs are missing and fallback needs manual confirmation."

        items.append(
            PlanItem(
                path=entry.path,
                size=entry.size,
                strategy=strategy,
                reason=reason,
                missingFastInputs=missing,
            )
        )
        counts[strategy] = counts.get(strategy, 0) + 1

    return TransferPlan(
        sourceProvider=source_provider,
        targetProvider=target_provider,
        thresholdMB=max(0, int(threshold_mb)),
        items=items,
        summary=PlanSummary(total=len(items), strategyCounts=counts),
    )
