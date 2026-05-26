from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.live_probe import run_live_probe


def main() -> None:
    payload = run_live_probe()
    summary = dict(payload.get("summary") or {})
    markdown = (ROOT / "docs" / "05-PROVIDER_LIVE_PROBE_REPORT.md").read_text(encoding="utf-8")
    current_live_probe_report_sync_matches_runtime_summary = (
        f"providerCount={summary.get('providerCount', 0)}" in markdown
        and f"totalChecks={summary.get('totalChecks', 0)}" in markdown
        and f"okChecks={summary.get('okChecks', 0)}" in markdown
        and f"failedChecks={summary.get('failedChecks', 0)}" in markdown
        and f"profileProbeProviderCount={summary.get('profileProbeProviderCount', 0)}" in markdown
        and f"profileProbeOkCount={summary.get('profileProbeOkCount', 0)}" in markdown
        and f"profileProbeFailedCount={summary.get('profileProbeFailedCount', 0)}" in markdown
        and f"- profileProbeProfiles: `ok={', '.join(summary.get('profileProbeOkProfiles', [])) or '(none)'}` `failed={', '.join(summary.get('profileProbeFailedProfiles', [])) or '(none)'}`" in markdown
        and f"- profileProbeProviderSummary: `ok_providers={', '.join(summary.get('profileProbeOkProviders', [])) or '(none)'}` `failed_providers={', '.join(summary.get('profileProbeFailedProviders', [])) or '(none)'}` `failed_modes={', '.join(summary.get('profileProbeFailedModes', [])) or '(none)'}`" in markdown
        and summary.get("profileProbeOkProfiles") == []
        and len(summary.get("profileProbeFailedProfiles") or []) == 4
        and "## guangya - Guangya" in markdown
        and "profile_probe: ok=False mode=live_error checks=1" in markdown
        and "## aliyundrive_open - Aliyun Drive Open" in markdown
        and "profile_probe: ok=False mode=live_error checks=1" in markdown
        and "## pikpak - PikPak" in markdown
        and "profile_probe: ok=False mode=live_error checks=1" in markdown
        and "## uc - UC Drive" in markdown
        and "profile_probe: ok=False mode=live_error checks=1" in markdown
    )

    print(
        json.dumps(
            {
                "summaryHasCurrentProbeCounts": (
                    f"providerCount={summary.get('providerCount', 0)}" in markdown
                    and f"totalChecks={summary.get('totalChecks', 0)}" in markdown
                    and f"okChecks={summary.get('okChecks', 0)}" in markdown
                    and f"failedChecks={summary.get('failedChecks', 0)}" in markdown
                    and f"profileProbeProviderCount={summary.get('profileProbeProviderCount', 0)}" in markdown
                    and f"profileProbeOkCount={summary.get('profileProbeOkCount', 0)}" in markdown
                    and f"profileProbeFailedCount={summary.get('profileProbeFailedCount', 0)}" in markdown
                    and f"- profileProbeProfiles: `ok={', '.join(summary.get('profileProbeOkProfiles', [])) or '(none)'}` `failed={', '.join(summary.get('profileProbeFailedProfiles', [])) or '(none)'}`" in markdown
                    and f"- profileProbeProviderSummary: `ok_providers={', '.join(summary.get('profileProbeOkProviders', [])) or '(none)'}` `failed_providers={', '.join(summary.get('profileProbeFailedProviders', [])) or '(none)'}` `failed_modes={', '.join(summary.get('profileProbeFailedModes', [])) or '(none)'}`" in markdown
                ),
                "summaryShowsExpectedCurrentProbeProfiles": (
                    summary.get("profileProbeOkProfiles") == []
                    and len(summary.get("profileProbeFailedProfiles") or []) == 4
                ),
                "guangyaSectionKeepsCurrentProfileProbe": (
                    "## guangya - Guangya" in markdown
                    and "profile_probe: ok=False mode=live_error checks=1" in markdown
                ),
                "aliyunSectionKeepsCurrentProfileProbe": (
                    "## aliyundrive_open - Aliyun Drive Open" in markdown
                    and "profile_probe: ok=False mode=live_error checks=1" in markdown
                ),
                "currentLiveProbeReportSyncMatchesRuntimeSummary": current_live_probe_report_sync_matches_runtime_summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
