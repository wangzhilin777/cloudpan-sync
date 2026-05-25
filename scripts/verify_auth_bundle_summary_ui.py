from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_evidence import refresh_auth_evidence_bundle


class _FakeProfile:
    def __init__(self, profile_id: str) -> None:
        self.profileId = profile_id


def main() -> None:
    app_js = (ROOT / "src" / "cloudpan_sync" / "web" / "assets" / "app.js").read_text(encoding="utf-8")

    original_refresh = sys.modules["cloudpan_sync.auth_profile_evidence"].refresh_auth_profile_evidence

    fake_items = [
        {
            "profile": {"profileId": "gy-1", "displayName": "Guangya Primary"},
            "summary": {"profileReady": True, "writeReady": True, "validationOk": True, "probeOk": False},
        },
        {
            "profile": {"profileId": "ali-1", "displayName": "Aliyun Open"},
            "summary": {"profileReady": False, "writeReady": True, "validationOk": False, "probeOk": False},
        },
    ]

    def fake_refresh_auth_profile_evidence(*, profile, page_size=100, dir_name="", persist=True, profile_view_builder=None):
        for item in fake_items:
            if (item.get("profile") or {}).get("profileId") == getattr(profile, "profileId", ""):
                return item
        raise AssertionError("unexpected profile")

    sys.modules["cloudpan_sync.auth_profile_evidence"].refresh_auth_profile_evidence = fake_refresh_auth_profile_evidence
    try:
        bundle = refresh_auth_evidence_bundle(
            profiles=[_FakeProfile("gy-1"), _FakeProfile("ali-1")],
            profile_view_builder=lambda profile: {"profileId": getattr(profile, "profileId", "")},
            persist=False,
        )
    finally:
        sys.modules["cloudpan_sync.auth_profile_evidence"].refresh_auth_profile_evidence = original_refresh

    summary = dict(bundle.get("summary") or {})
    print(
        json.dumps(
            {
                "refreshBundleKeepsProfileSummaryLists": summary.get("profileReadyProfiles") == ["Guangya Primary"]
                and summary.get("writeReadyProfiles") == ["Aliyun Open", "Guangya Primary"]
                and summary.get("validationOkProfiles") == ["Guangya Primary"]
                and summary.get("probeOkProfiles") == [],
                "jsAuthEvidenceBundleShowsProfileSummary": "profileReadyProfiles=" in app_js
                and "writeReadyProfiles=" in app_js
                and "validationOkProfiles=" in app_js
                and "probeOkProfiles=" in app_js,
                "jsAuthEvidenceBundleHasFirstGapActions": 'focusBtn.textContent = "Focus First Gap"' in app_js
                and 'refreshBtn.textContent = "Refresh First Gap"' in app_js
                and 'captureBtn.textContent = "Open Capture First Gap"' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(firstProfile.profileId));' in app_js
                and 'refreshBtn.addEventListener("click", () => refreshRealEvidenceRemediationProfile(firstProfile.profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstProfile.providerKey || ""));' in app_js,
                "jsAuthRemediationShowsProfileSummary": "readyProfiles=" in app_js
                and "needsFixProfiles=" in app_js
                and "writeReadyProfiles=" in app_js
                and "writeNeedsFixProfiles=" in app_js
                and "needsSecretRefreshProfiles=" in app_js,
                "jsAuthRemediationHasFirstFixActions": 'focusBtn.textContent = "Focus First Fix"' in app_js
                and 'captureBtn.textContent = "Open Capture First Fix"' in app_js
                and 'focusBtn.addEventListener("click", () => focusAuthRemediationProfile(firstNeedsFix.profileId));' in app_js
                and 'captureBtn.addEventListener("click", () => openCaptureGuideForProvider(firstNeedsFix.providerKey || ""));' in app_js,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
