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
    selected_roots: list[str] | None = None,
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

    execution_groups = _build_execution_groups(items, selected_roots or [])
    pending_items = [
        {
            "path": item.path,
            "size": item.size,
            "reason": item.reason,
            "missingFastInputs": item.missingFastInputs,
        }
        for item in items
        if item.strategy == "pending_manual"
    ]

    return TransferPlan(
        sourceProvider=source_provider,
        targetProvider=target_provider,
        thresholdMB=max(0, int(threshold_mb)),
        items=items,
        summary=PlanSummary(total=len(items), strategyCounts=counts),
        executionGroups=execution_groups,
        pendingItems=pending_items,
    )


def _normalize_path(path: str) -> str:
    value = (path or "/").replace("\\", "/").strip()
    value = "/" + value.strip("/")
    return "/" if value == "" else value


def _path_depth(path: str) -> int:
    normalized = _normalize_path(path)
    if normalized == "/":
        return 0
    return len([seg for seg in normalized.split("/") if seg])


def _build_execution_groups(items: list[PlanItem], selected_roots: list[str]) -> list[dict[str, object]]:
    if not items:
        return []
    roots = [_normalize_path(root) for root in selected_roots if str(root or "").strip()]
    if not roots:
        # fallback: infer roots from first segment, preserve appearance order
        seen: set[str] = set()
        for item in items:
            normalized = _normalize_path(item.path)
            parts = [seg for seg in normalized.split("/") if seg]
            root = f"/{parts[0]}" if parts else "/"
            if root not in seen:
                roots.append(root)
                seen.add(root)

    groups: list[dict[str, object]] = []
    for root in roots:
        scoped = [item for item in items if _normalize_path(item.path).startswith(root.rstrip("/") + "/") or _normalize_path(item.path) == root]
        if not scoped:
            continue
        scoped_sorted = sorted(scoped, key=lambda x: (-_path_depth(x.path), _normalize_path(x.path)))
        groups.append(
            {
                "root": root,
                "order": "deepest_first",
                "items": [
                    {
                        "path": item.path,
                        "size": item.size,
                        "strategy": item.strategy,
                    }
                    for item in scoped_sorted
                ],
            }
        )
    return groups
