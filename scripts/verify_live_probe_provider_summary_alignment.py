from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import live_probe


def main() -> None:
    original_research = live_probe.build_provider_research_index
    original_latest = live_probe.latest_provider_live_probes
    original_probe_url = live_probe._probe_url

    try:
        live_probe.build_provider_research_index = lambda: [
            {"providerKey": "guangya", "displayName": "Guangya", "webLoginUrl": "https://guangya.example"},
            {"providerKey": "pikpak", "displayName": "PikPak", "officialDocsUrl": "https://pikpak.example"},
        ]
        live_probe.latest_provider_live_probes = lambda: [
            {
                "providerKey": "guangya",
                "profileId": "gy-1",
                "ok": False,
                "mode": "profile_incomplete",
                "summary": "missing parentId",
                "checks": [{"kind": "list", "ok": False}],
            },
            {
                "providerKey": "guangya",
                "profileId": "gy-2",
                "ok": False,
                "mode": "live_error",
                "summary": "live rejected",
                "checks": [{"kind": "list", "ok": False}, {"kind": "metadata", "ok": False}],
            },
        ]
        live_probe._probe_url = lambda kind, url, timeout_sec=8: live_probe.ProbeResult(
            kind=kind,
            url=url,
            ok=True,
            status=200,
            finalUrl=url,
            error="",
        )

        payload = live_probe.run_live_probe()
        markdown = live_probe.probe_to_markdown(payload)
        summary = dict(payload.get("summary") or {})
        guangya = next((item for item in payload.get("items", []) if item.get("providerKey") == "guangya"), {})

        print(
            json.dumps(
                {
                    "profileProbeProviderCountIsProviderScoped": summary.get("profileProbeProviderCount") == 1,
                    "profileProbeFailedCountIsProviderScoped": summary.get("profileProbeFailedCount") == 1,
                    "profileProbeProfileSummaryIsProviderScoped": summary.get("profileProbeOkProfiles") == []
                    and summary.get("profileProbeFailedProfiles") == ["gy-2"]
                    and summary.get("profileProbeOkProviders") == []
                    and summary.get("profileProbeFailedProviders") == ["guangya"]
                    and summary.get("profileProbeFailedModes") == ["live_error"],
                    "guangyaUsesLatestProfileProbe": (
                        ((guangya.get("profileProbe") or {}).get("mode")) == "live_error"
                        and ((guangya.get("profileProbe") or {}).get("profileId")) == "gy-2"
                        and ((guangya.get("profileProbe") or {}).get("checkCount")) == 2
                    ),
                    "markdownSummaryMatchesProviderScopedCounts": (
                        "profileProbeProviderCount=1" in markdown
                        and "profileProbeFailedCount=1" in markdown
                        and "- profileProbeProfiles: `ok=(none)` `failed=gy-2`" in markdown
                        and "- profileProbeProviderSummary: `ok_providers=(none)` `failed_providers=guangya` `failed_modes=live_error`" in markdown
                    ),
                    "markdownHasSingleGuangyaProfileProbeRow": markdown.count("profile_probe:") == 1
                    and "mode=live_error checks=2 summary=live rejected" in markdown,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        live_probe.build_provider_research_index = original_research
        live_probe.latest_provider_live_probes = original_latest
        live_probe._probe_url = original_probe_url


if __name__ == "__main__":
    main()
