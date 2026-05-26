from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.runtime_orphan_recovery import build_runtime_orphan_recovery


def _section(markdown: str, marker: str) -> str:
    start = markdown.find(marker)
    if start < 0:
        return ""
    next_start = markdown.find("\n## ", start + 1)
    if next_start < 0:
        return markdown[start:]
    return markdown[start:next_start]


def main() -> None:
    payload = build_runtime_orphan_recovery()
    summary = dict(payload.get("summary") or {})
    markdown = (ROOT / "docs" / "13-RUNTIME_ORPHAN_RECOVERY.md").read_text(encoding="utf-8")
    guangya = _section(markdown, "## guangya - ")
    guangya_defaults = _section(markdown, "## guangya - Guangya - gy-live-defaults-1")
    pikpak = _section(markdown, "## pikpak - ")
    uc = _section(markdown, "## uc - ")

    print(
        json.dumps(
            {
                "summaryHasCurrentCounts": (
                    f"`providerCount={summary.get('providerCount', 0)}`" in markdown
                    and f"`orphanProfileCount={summary.get('orphanProfileCount', 0)}`" in markdown
                    and f"`runtimeSampleCount={summary.get('runtimeSampleCount', 0)}`" in markdown
                    and f"`providersWithSavedProfiles={summary.get('providersWithSavedProfiles', 0)}`" in markdown
                    and f"`providersWithoutSavedProfiles={summary.get('providersWithoutSavedProfiles', 0)}`" in markdown
                ),
                "summaryShowsExpectedCurrentValues": (
                    summary.get("providerCount") == 3
                    and summary.get("orphanProfileCount") == 4
                    and summary.get("runtimeSampleCount") == 4
                    and summary.get("providersWithSavedProfiles") == 1
                    and summary.get("providersWithoutSavedProfiles") == 2
                    and summary.get("orphanProviders") == ["guangya", "pikpak", "uc"]
                    and summary.get("orphanProfiles") == ["gy-live-1", "gy-live-defaults-1", "pikpak-live-1", "uc-live-1"]
                ),
                "guangyaSectionHasRecoveryCommand": "--profile-id gy-live-1" in guangya and "existingProviderProfiles: count=`2`" in guangya,
                "guangyaSectionHasPrimaryCommand": "recommendedPrimaryCommand:" in guangya and "label=Refresh Existing Orphan Profile" in guangya,
                "guangyaDefaultsSectionHasRecoveryCommand": "--profile-id gy-live-defaults-1" in guangya_defaults and "existingProviderProfiles: count=`2`" in guangya_defaults,
                "guangyaDefaultsSectionHasPrimaryCommand": "recommendedPrimaryCommand:" in guangya_defaults and "label=Refresh Existing Orphan Profile" in guangya_defaults,
                "pikpakSectionHasRecoveryCommand": "--profile-id pikpak-live-1" in pikpak and "preferred=`manual_token`" in pikpak,
                "pikpakSectionHasPrimaryCommand": "recommendedPrimaryCommand:" in pikpak and "label=Recreate Orphan Stub" in pikpak,
                "ucSectionHasRecoveryCommand": "--profile-id uc-live-1" in uc and "preferred=`manual_cookie`" in uc,
                "ucSectionHasPrimaryCommand": "recommendedPrimaryCommand:" in uc and "label=Recreate Orphan Stub" in uc,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
