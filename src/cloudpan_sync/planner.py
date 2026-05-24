from __future__ import annotations

from .fingerprints import available_fast_inputs, build_fingerprint_set
from .models import PlanItem, PlanSummary, SourceEntry, TransferPlan
from .provider_registry import get_provider_profile


def _missing_fast_inputs(entry: SourceEntry, required: list[str]) -> list[str]:
    fingerprints = build_fingerprint_set(entry)
    available = set(available_fast_inputs(fingerprints, entry.path, entry.size))
    missing: list[str] = []
    for key in required:
        if key not in available:
            missing.append(key)
    return missing


def build_transfer_plan(
    source_provider: str,
    target_provider: str,
    entries: list[SourceEntry],
    threshold_mb: int,
    conflict_policy: str = "auto_rename_new",
    selected_roots: list[str] | None = None,
) -> TransferPlan:
    target_profile = get_provider_profile(target_provider)
    if target_profile is None:
        raise ValueError(f"Unknown target provider: {target_provider}")

    threshold_bytes = max(0, int(threshold_mb)) * 1024 * 1024
    items: list[PlanItem] = []
    counts: dict[str, int] = {}

    for entry in entries:
        fingerprints = build_fingerprint_set(entry)
        available_inputs = available_fast_inputs(fingerprints, entry.path, entry.size)
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

        conflict_support_status, conflict_note = _resolve_conflict_support(
            conflict_policy=str(conflict_policy or "auto_rename_new"),
            provider_key=target_profile.providerKey,
        )

        items.append(
            PlanItem(
                path=entry.path,
                size=entry.size,
                strategy=strategy,
                reason=reason,
                conflictPolicy=str(conflict_policy or "auto_rename_new"),
                conflictSupportStatus=conflict_support_status,
                conflictNote=conflict_note,
                normalizedFingerprints=fingerprints,
                availableFastInputs=available_inputs,
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
                "conflictPolicy": item.conflictPolicy,
                "conflictSupportStatus": item.conflictSupportStatus,
                "conflictNote": item.conflictNote,
                "missingFastInputs": item.missingFastInputs,
            }
        for item in items
        if item.strategy == "pending_manual"
    ]

    return TransferPlan(
        sourceProvider=source_provider,
        targetProvider=target_provider,
        thresholdMB=max(0, int(threshold_mb)),
        conflictPolicy=str(conflict_policy or "auto_rename_new"),
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
                        "conflictPolicy": item.conflictPolicy,
                        "conflictSupportStatus": item.conflictSupportStatus,
                        "conflictNote": item.conflictNote,
                    }
                    for item in scoped_sorted
                ],
            }
        )
    return groups


def _resolve_conflict_support(conflict_policy: str, provider_key: str) -> tuple[str, str]:
    profile = get_provider_profile(provider_key)
    if profile is None:
        return "unknown", "Target provider profile is missing, so conflict handling support could not be resolved."

    normalized_policy = str(conflict_policy or "auto_rename_new")
    if normalized_policy == "overwrite_existing":
        if profile.supportsOverwrite:
            return "supported", ""
        if profile.supportsAutoRename and profile.overwriteBehavior == "downgrade_to_auto_rename":
            return (
                "downgrade_to_auto_rename",
                "The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new.",
            )
        return (
            "unsupported",
            profile.conflictNotes
            or "The current target provider path does not guarantee overwrite_existing, and no safe downgrade is currently declared.",
        )

    if normalized_policy == "auto_rename_new":
        if profile.supportsAutoRename:
            return "supported", ""
        if provider_key == "aliyundrive_open":
            return (
                "probe_only_runtime_write_check",
                "Aliyun Drive Open task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet.",
            )
        return (
            "unsupported",
            profile.conflictNotes
            or "The current target provider path does not yet declare safe auto_rename_new handling.",
        )

    return "unknown", "Unknown conflict policy."
