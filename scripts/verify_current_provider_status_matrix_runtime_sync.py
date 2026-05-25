from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.provider_status_matrix import build_status_matrix


def _find_row(markdown: str, provider_key: str) -> str:
    prefix = f"| {provider_key} |"
    for line in markdown.splitlines():
        if line.startswith(prefix):
            return line
    return ""


def main() -> None:
    payload = build_status_matrix()
    summary = dict(payload.get("summary") or {})
    markdown = (ROOT / "docs" / "06-PROVIDER_STATUS_MATRIX.md").read_text(encoding="utf-8")

    guangya_row = _find_row(markdown, "guangya")
    uc_row = _find_row(markdown, "uc")
    pikpak_row = _find_row(markdown, "pikpak")
    aliyun_row = _find_row(markdown, "aliyundrive_open")
    quark_row = _find_row(markdown, "quark")
    baidu_row = _find_row(markdown, "baidu_netdisk")
    pan123_row = _find_row(markdown, "123_open")

    print(
        json.dumps(
            {
                "summaryHasCurrentRuntimeCounts": (
                    f"taskRuntimeEvidenceProviderCount={summary.get('taskRuntimeEvidenceProviderCount', 0)}" in markdown
                    and f"taskRuntimeSampleCount={summary.get('taskRuntimeSampleCount', 0)}" in markdown
                    and f"taskRuntimeSuccessCount={summary.get('taskRuntimeSuccessCount', 0)}" in markdown
                    and f"taskRuntimeConflictHandledProviderCount={summary.get('taskRuntimeConflictHandledProviderCount', 0)}" in markdown
                    and f"taskRuntimeConflictHandledCount={summary.get('taskRuntimeConflictHandledCount', 0)}" in markdown
                ),
                "summaryShowsThreeRuntimeSuccessProviders": (
                    summary.get("taskRuntimeEvidenceProviderCount") == 3
                    and summary.get("taskRuntimeSuccessCount") == 3
                    and summary.get("taskRuntimeSampleCount") == 3
                ),
                "guangyaRowShowsRuntimeSuccess": "| guangya |" in guangya_row and "| 1 | 1 | 0 | 0 | 0 | 0 | 1 |" in guangya_row,
                "ucRowShowsRuntimeSuccess": "| uc |" in uc_row and "| 1 | 1 | 0 | 0 | 0 | 0 | 1 |" in uc_row,
                "pikpakRowShowsRuntimeSuccess": "| pikpak |" in pikpak_row and "| 1 | 1 | 0 | 0 | 0 | 0 | 1 |" in pikpak_row,
                "aliyunRowShowsNoRuntimeSuccess": "| aliyundrive_open |" in aliyun_row and "| 0 | 0 | 0 | 0 | 0 | 0 |" in aliyun_row,
                "quarkRowShowsNoRuntimeSuccess": "| quark |" in quark_row and "| 0 | 0 | 0 | 0 | 0 | 0 |" in quark_row,
                "baiduRowShowsNoRuntimeSuccess": "| baidu_netdisk |" in baidu_row and "| 0 | 0 | 0 | 0 | 0 | 0 |" in baidu_row,
                "pan123RowShowsNoRuntimeSuccess": "| 123_open |" in pan123_row and "| 0 | 0 | 0 | 0 | 0 | 0 |" in pan123_row,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
