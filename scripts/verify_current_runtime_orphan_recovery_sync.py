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
    guangya_live_2 = _section(markdown, "## guangya - Guangya - gy-live-2")
    guangya_defaults = _section(markdown, "## guangya - Guangya - gy-live-defaults-1")
    guangya_orphan_live = _section(markdown, "## guangya - Guangya - gy-orphan-live-1")
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
                    and summary.get("orphanProfileCount") == 6
                    and summary.get("runtimeSampleCount") == 6
                    and summary.get("providersWithSavedProfiles") == 1
                    and summary.get("providersWithoutSavedProfiles") == 2
                    and summary.get("orphanProviders") == ["guangya", "pikpak", "uc"]
                    and summary.get("orphanProfiles") == ["gy-live-1", "gy-live-2", "gy-live-defaults-1", "gy-orphan-live-1", "pikpak-live-1", "uc-live-1"]
                ),
                "guangyaSectionHasRecoveryCommand": "--profile-id gy-live-1" in guangya and "existingProviderProfiles: count=`2`" in guangya,
                "guangyaSectionHasPrimaryCommand": "recommendedPrimaryCommand:" in guangya and "label=Refresh Existing Orphan Profile" in guangya,
                "guangyaSectionHasExactRuntimeHelpers": "exactRefreshEvidenceHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-runtime-orphan-profile gy-live-1`" in guangya
                and "exactRuntimeProbeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py --from-runtime-orphan-profile gy-live-1`" in guangya
                and "exactRuntimeSuccessHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile gy-live-1`" in guangya
                and "exactOverwriteVariantHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile gy-live-1`" in guangya,
                "guangyaLive2SectionHasRecoveryCommand": "--profile-id gy-live-2" in guangya_live_2 and "existingProviderProfiles: count=`2`" in guangya_live_2,
                "guangyaLive2SectionHasPrimaryCommand": "recommendedPrimaryCommand:" in guangya_live_2 and "label=Refresh Existing Orphan Profile" in guangya_live_2,
                "guangyaLive2SectionHasExactRuntimeHelpers": "exactRefreshEvidenceHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-runtime-orphan-profile gy-live-2`" in guangya_live_2
                and "exactRuntimeProbeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py --from-runtime-orphan-profile gy-live-2`" in guangya_live_2
                and "exactRuntimeSuccessHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile gy-live-2`" in guangya_live_2
                and "exactOverwriteVariantHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile gy-live-2`" in guangya_live_2,
                "guangyaDefaultsSectionHasRecoveryCommand": "--profile-id gy-live-defaults-1" in guangya_defaults and "existingProviderProfiles: count=`2`" in guangya_defaults,
                "guangyaDefaultsSectionHasPrimaryCommand": "recommendedPrimaryCommand:" in guangya_defaults and "label=Refresh Existing Orphan Profile" in guangya_defaults,
                "guangyaDefaultsSectionHasExactRuntimeHelpers": "exactRefreshEvidenceHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-runtime-orphan-profile gy-live-defaults-1`" in guangya_defaults
                and "exactRuntimeProbeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py --from-runtime-orphan-profile gy-live-defaults-1`" in guangya_defaults
                and "exactRuntimeSuccessHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile gy-live-defaults-1`" in guangya_defaults
                and "exactOverwriteVariantHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile gy-live-defaults-1`" in guangya_defaults,
                "guangyaOrphanLiveSectionHasRecoveryCommand": "--profile-id gy-orphan-live-1" in guangya_orphan_live and "existingProviderProfiles: count=`2`" in guangya_orphan_live,
                "guangyaOrphanLiveSectionHasPrimaryCommand": "recommendedPrimaryCommand:" in guangya_orphan_live and "label=Refresh Existing Orphan Profile" in guangya_orphan_live,
                "guangyaOrphanLiveSectionHasExactRuntimeHelpers": "exactRefreshEvidenceHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-runtime-orphan-profile gy-orphan-live-1`" in guangya_orphan_live
                and "exactRuntimeProbeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py --from-runtime-orphan-profile gy-orphan-live-1`" in guangya_orphan_live
                and "exactRuntimeSuccessHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile gy-orphan-live-1`" in guangya_orphan_live
                and "exactOverwriteVariantHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile gy-orphan-live-1`" in guangya_orphan_live,
                "pikpakSectionHasRecoveryCommand": "--profile-id pikpak-live-1" in pikpak and "preferred=`manual_token`" in pikpak,
                "pikpakSectionHasPrimaryCommand": "recommendedPrimaryCommand:" in pikpak and "label=Recreate Orphan Stub" in pikpak,
                "pikpakSectionHasExactRuntimeHelpers": "exactRefreshEvidenceHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-runtime-orphan-profile pikpak-live-1`" in pikpak
                and "exactRuntimeProbeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py --from-runtime-orphan-profile pikpak-live-1`" in pikpak
                and "exactRuntimeSuccessHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile pikpak-live-1`" in pikpak
                and "exactOverwriteVariantHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile pikpak-live-1`" in pikpak,
                "ucSectionHasRecoveryCommand": "--profile-id uc-live-1" in uc and "preferred=`manual_cookie`" in uc,
                "ucSectionHasPrimaryCommand": "recommendedPrimaryCommand:" in uc and "label=Recreate Orphan Stub" in uc,
                "ucSectionHasExactRuntimeHelpers": "exactRefreshEvidenceHelper: `.\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-runtime-orphan-profile uc-live-1`" in uc
                and "exactRuntimeProbeHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py --from-runtime-orphan-profile uc-live-1`" in uc
                and "exactRuntimeSuccessHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile uc-live-1`" in uc
                and "exactOverwriteVariantHelper: `.\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile uc-live-1`" in uc,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
