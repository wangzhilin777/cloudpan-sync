from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.models import SourceEntry
from cloudpan_sync.planner import build_transfer_plan
from cloudpan_sync.provider_registry import get_provider_profile


def main() -> None:
    provider = get_provider_profile("115_open")

    fast_entry = SourceEntry(path="/1/11/111/movie-fast.bin", size=4, sha1="sha1-fast")
    fallback_entry = SourceEntry(path="/1/11/112/movie-fallback.bin", size=2 * 1024 * 1024, md5="md5-only")
    pending_entry = SourceEntry(path="/1/11/archive-large.bin", size=9 * 1024 * 1024, md5="md5-only")
    second_root_entry = SourceEntry(path="/2/21/211/movie-second.bin", size=4, md5="md5-second")

    plan = build_transfer_plan(
        source_provider="quark",
        target_provider="115_open",
        entries=[fast_entry, fallback_entry, pending_entry, second_root_entry],
        threshold_mb=3,
        conflict_policy="auto_rename_new",
        selected_roots=["/1", "/2"],
    ).model_dump()

    items = {str(item.get("path") or ""): dict(item) for item in plan.get("items") or []}
    summary = dict(plan.get("summary") or {})
    strategy_counts = dict(summary.get("strategyCounts") or {})
    execution_groups = list(plan.get("executionGroups") or [])
    pending_items = list(plan.get("pendingItems") or [])

    first_group = execution_groups[0] if execution_groups else {}
    second_group = execution_groups[1] if len(execution_groups) > 1 else {}
    first_group_paths = [str(item.get("path") or "") for item in first_group.get("items") or []]
    second_group_paths = [str(item.get("path") or "") for item in second_group.get("items") or []]

    print(
        json.dumps(
            {
                "providerCapabilityFor115Open": (
                    provider is not None
                    and provider.providerKey == "115_open"
                    and provider.fastUploadInputs == ["sha1", "size"]
                    and provider.authModes == ["official_oauth", "manual_cookie"]
                ),
                "fastUploadStrategyUsesProviderInputs": (
                    items["/1/11/111/movie-fast.bin"].get("strategy") == "fast_upload"
                    and items["/1/11/111/movie-fast.bin"].get("missingFastInputs") == []
                    and "sha1" in list(items["/1/11/111/movie-fast.bin"].get("availableFastInputs") or [])
                ),
                "fallbackThresholdCreatesDownloadUpload": (
                    items["/1/11/112/movie-fallback.bin"].get("strategy") == "download_upload"
                    and "sha1" in list(items["/1/11/112/movie-fallback.bin"].get("missingFastInputs") or [])
                    and "size" in list(items["/1/11/112/movie-fallback.bin"].get("availableFastInputs") or [])
                ),
                "oversizeFallsBackToPendingManual": (
                    items["/1/11/archive-large.bin"].get("strategy") == "pending_manual"
                    and len(pending_items) == 1
                    and pending_items[0].get("path") == "/1/11/archive-large.bin"
                    and pending_items[0].get("conflictPolicy") == "auto_rename_new"
                ),
                "summaryCountsCoverThreeStrategyBranches": (
                    summary.get("total") == 4
                    and strategy_counts.get("fast_upload") == 1
                    and strategy_counts.get("download_upload") == 2
                    and strategy_counts.get("pending_manual") == 1
                ),
                "executionGroupsKeepSelectedRootOrder": (
                    len(execution_groups) == 2
                    and first_group.get("root") == "/1"
                    and second_group.get("root") == "/2"
                    and first_group.get("order") == "deepest_first"
                    and second_group.get("order") == "deepest_first"
                ),
                "executionGroupsUseDeepestFirstInsideRoot": (
                    first_group_paths == [
                        "/1/11/111/movie-fast.bin",
                        "/1/11/112/movie-fallback.bin",
                        "/1/11/archive-large.bin",
                    ]
                    and second_group_paths == ["/2/21/211/movie-second.bin"]
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
