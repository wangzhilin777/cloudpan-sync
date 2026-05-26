from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.task_runtime_evidence_store import build_task_runtime_evidence_payload


def main() -> None:
    payload = build_task_runtime_evidence_payload()
    summary = dict(payload.get("summary") or {})
    markdown = (ROOT / "docs" / "11-TASK_RUNTIME_EVIDENCE.md").read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "summaryHasCurrentRuntimeCounts": (
                    f"`sampleCount={summary.get('sampleCount', 0)}`" in markdown
                    and f"`providerCount={summary.get('providerCount', 0)}`" in markdown
                    and f"`profileCount={summary.get('profileCount', 0)}`" in markdown
                    and f"`successProviderCount={summary.get('successProviderCount', 0)}`" in markdown
                    and f"`successCount={summary.get('successCount', 0)}`" in markdown
                    and f"`verifyOkCount={summary.get('verifyOkCount', 0)}`" in markdown
                    and f"`conflictHandledCount={summary.get('conflictHandledCount', 0)}`" in markdown
                    and f"`runtimeOrphanProviderCount={summary.get('runtimeOrphanProviderCount', 0)}`" in markdown
                    and f"`runtimeOrphanProfileCount={summary.get('runtimeOrphanProfileCount', 0)}`" in markdown
                ),
                "summaryShowsExpectedRuntimeCounts": (
                    summary.get("sampleCount") == 4
                    and summary.get("providerCount") == 3
                    and summary.get("profileCount") == 4
                    and summary.get("successProviderCount") == 3
                    and summary.get("successCount") == 4
                    and summary.get("failedCount") == 0
                    and summary.get("verifyOkCount") == 4
                    and summary.get("conflictHandledCount") == 4
                    and summary.get("runtimeOrphanProviderCount") == 3
                    and summary.get("runtimeOrphanProfileCount") == 4
                ),
                "profileSummaryShowsCurrentProfiles": (
                    "profileSummary:" in markdown
                    and f"`success={', '.join(summary.get('successProfiles', []) or []) or '(none)'}`" in markdown
                    and f"`failed={', '.join(summary.get('failedProfiles', []) or []) or '(none)'}`" in markdown
                    and f"`candidate={', '.join(summary.get('candidateProfiles', []) or []) or '(none)'}`" in markdown
                    and f"`probe={', '.join(summary.get('probeProfiles', []) or []) or '(none)'}`" in markdown
                    and f"`blocked={', '.join(summary.get('blockedProfiles', []) or []) or '(none)'}`" in markdown
                    and f"`conflictHandled={', '.join(summary.get('conflictHandledProfiles', []) or []) or '(none)'}`" in markdown
                    and f"`runtimeOrphan={', '.join(summary.get('runtimeOrphanProfiles', []) or []) or '(none)'}`" in markdown
                ),
                "hasPikpakSuccessRow": (
                    "- pikpak profile=pikpak-live-1" in markdown
                    and "mode=binary_upload_after_hash_miss" in markdown
                    and "verifyMode=metadata_by_file_id" in markdown
                    and "orphanProfileId=pikpak-live-1" in markdown
                ),
                "hasUcSuccessRow": (
                    "- uc profile=uc-live-1" in markdown
                    and "verifyMode=finish_response" in markdown
                    and "orphanProfileId=uc-live-1" in markdown
                ),
                "hasGuangyaSuccessRow": (
                    "- guangya profile=gy-live-1" in markdown
                    and "mode=binary_upload_multipart" in markdown
                    and "verifyMode=list_by_parent_name" in markdown
                    and "orphanProfileId=gy-live-1" in markdown
                ),
                "hasGuangyaDefaultsSuccessRow": (
                    "- guangya profile=gy-live-defaults-1" in markdown
                    and "conflictAction=auto_rename_new" in markdown
                    and "orphanProfileId=gy-live-defaults-1" in markdown
                ),
                "allRowsKeepConflictDowngrade": markdown.count("conflictAction=overwrite_downgraded_to_auto_rename") == 3,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
