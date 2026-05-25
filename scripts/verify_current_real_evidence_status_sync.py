from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.real_evidence_report import build_real_evidence_report


def _section(markdown: str, provider_key: str) -> str:
    marker = f"## {provider_key} - "
    start = markdown.find(marker)
    if start < 0:
        return ""
    next_start = markdown.find("\n## ", start + 1)
    if next_start < 0:
        return markdown[start:]
    return markdown[start:next_start]


def main() -> None:
    payload = build_real_evidence_report()
    summary = dict(payload.get("summary") or {})
    markdown = (ROOT / "docs" / "10-REAL_EVIDENCE_STATUS.md").read_text(encoding="utf-8")

    guangya = _section(markdown, "guangya")
    uc = _section(markdown, "uc")
    pikpak = _section(markdown, "pikpak")
    aliyun = _section(markdown, "aliyundrive_open")
    quark = _section(markdown, "quark")
    baidu = _section(markdown, "baidu_netdisk")
    pan123 = _section(markdown, "123_open")

    print(
        json.dumps(
            {
                "summaryHasCurrentRuntimeCounts": (
                    f"`task_runtime={summary.get('taskRuntimeEvidenceProviderCount', 0)}`" in markdown
                    and f"`runtime_samples={summary.get('taskRuntimeSampleCount', 0)}`" in markdown
                    and f"`runtime_success={summary.get('taskRuntimeSuccessCount', 0)}`" in markdown
                    and f"`runtime_conflict_handled={summary.get('taskRuntimeConflictHandledCount', 0)}`" in markdown
                ),
                "summaryShowsThreeRuntimeSuccessProviders": (
                    summary.get("taskRuntimeEvidenceProviderCount") == 3
                    and summary.get("taskRuntimeSampleCount") == 3
                    and summary.get("taskRuntimeSuccessCount") == 3
                ),
                "guangyaSectionShowsRuntimeSuccess": "samples=1 success=1 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=1" in guangya,
                "ucSectionShowsRuntimeSuccess": "samples=1 success=1 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=1" in uc,
                "pikpakSectionShowsRuntimeSuccess": "samples=1 success=1 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=1" in pikpak,
                "aliyunSectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in aliyun,
                "quarkSectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in quark,
                "baiduSectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in baidu,
                "pan123SectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in pan123,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
