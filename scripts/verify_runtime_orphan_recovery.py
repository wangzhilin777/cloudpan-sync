from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import runtime_orphan_recovery, webapp
from cloudpan_sync.models import AuthProfile


def main() -> None:
    original_runtime = runtime_orphan_recovery.latest_task_runtime_evidence
    original_profiles = runtime_orphan_recovery.list_profiles
    try:
        runtime_orphan_recovery.latest_task_runtime_evidence = lambda: [
            {
                "providerKey": "guangya",
                "profileId": "gy-orphan",
                "path": "/a.bin",
                "mode": "binary_upload_multipart",
                "executionMode": "live",
                "success": True,
                "candidateOnly": False,
                "probeOnly": False,
                "verifyMode": "list_by_parent_name",
                "conflictPolicy": "overwrite_existing",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "savedAt": "2026-05-25T00:00:00+00:00",
            },
            {
                "providerKey": "uc",
                "profileId": "uc-orphan",
                "path": "/b.bin",
                "mode": "binary_upload_after_hash_miss",
                "executionMode": "live",
                "success": True,
                "candidateOnly": False,
                "probeOnly": False,
                "verifyMode": "finish_response",
                "conflictPolicy": "overwrite_existing",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "savedAt": "2026-05-25T00:01:00+00:00",
            },
        ]
        runtime_orphan_recovery.list_profiles = lambda: [
            AuthProfile(
                profileId="saved-guangya-1",
                providerKey="guangya",
                authMode="manual_token",
                displayName="saved-guangya",
                token="tok",
                cookie="",
                extra={},
                status="saved",
                lastError="",
                createdAt="2026-05-25T00:00:00+00:00",
                updatedAt="2026-05-25T00:00:00+00:00",
            )
        ]

        payload = runtime_orphan_recovery.build_runtime_orphan_recovery()
        markdown = runtime_orphan_recovery.runtime_orphan_recovery_to_markdown(payload)

        app = webapp.create_app()
        client = TestClient(app)
        client.cookies.set("cloudpan_sync_session", webapp.build_session_token("admin"))
        api_payload = client.get("/api/runtime_orphan_recovery").json()
        api_markdown = client.get("/api/runtime_orphan_recovery_markdown").json()

        print(
            json.dumps(
                {
                    "summaryHasExpectedCounts": (
                        (payload.get("summary") or {}).get("providerCount") == 2
                        and (payload.get("summary") or {}).get("orphanProfileCount") == 2
                        and (payload.get("summary") or {}).get("runtimeSampleCount") == 2
                        and (payload.get("summary") or {}).get("providersWithSavedProfiles") == 1
                        and (payload.get("summary") or {}).get("providersWithoutSavedProfiles") == 1
                    ),
                    "summaryHasExpectedLists": (
                        (payload.get("summary") or {}).get("orphanProviders") == ["guangya", "uc"]
                        and (payload.get("summary") or {}).get("orphanProfiles") == ["gy-orphan", "uc-orphan"]
                        and (payload.get("summary") or {}).get("providersWithSavedProfilesList") == ["guangya"]
                        and (payload.get("summary") or {}).get("providersWithoutSavedProfilesList") == ["uc"]
                    ),
                    "guangyaItemHasProfileIdCommand": any(
                        row.get("providerKey") == "guangya"
                        and "--profile-id gy-orphan" in str(row.get("recommendedCreateCommand") or "")
                        and "--provider-key guangya" in str(row.get("recommendedCreateCommand") or "")
                        for row in (payload.get("items") or [])
                    ),
                    "ucItemHasCookieRecoveryCommand": any(
                        row.get("providerKey") == "uc"
                        and "--profile-id uc-orphan" in str(row.get("recommendedCreateCommand") or "")
                        and "--cookie YOUR_COOKIE" in str(row.get("recommendedCreateCommand") or "")
                        for row in (payload.get("items") or [])
                    ),
                    "itemsHaveFollowupCommands": any(
                        row.get("providerKey") == "guangya"
                        and str(row.get("recommendedPrimaryCommandLabel") or "") == "Refresh Existing Orphan Profile"
                        and "patch_and_probe_auth_profile.py --profile-id gy-orphan --write" in str(row.get("recommendedPrimaryCommand") or "")
                        and "patch_and_probe_auth_profile.py --profile-id gy-orphan --write" in str(row.get("recommendedRefreshEvidenceCommand") or "")
                        and "create_runtime_probe_task.py --target-provider guangya --target-profile-id gy-orphan" in str(row.get("recommendedRuntimeProbeCommand") or "")
                        and "create_live_upload_task.py --target-provider guangya --target-profile-id gy-orphan" in str(row.get("recommendedRuntimeSuccessCommand") or "")
                        and "--conflict-policy overwrite_existing" in str(row.get("recommendedOverwriteVariantCommand") or "")
                        for row in (payload.get("items") or [])
                    ),
                    "markdownHasTitle": "# CloudPan Sync Runtime Orphan Recovery Guide" in markdown,
                    "markdownHasSummary": "orphanProfileCount=2" in markdown and "providersWithSavedProfiles=1" in markdown,
                    "markdownHasOrphanSummary": "orphanSummary:" in markdown and "profiles=gy-orphan, uc-orphan" in markdown,
                    "markdownHasCreateCommands": "--profile-id gy-orphan" in markdown and "--profile-id uc-orphan" in markdown,
                    "markdownHasFollowupCommands": "recommendedPrimaryCommand" in markdown and "recommendedRefreshEvidenceCommand" in markdown and "exactRefreshEvidenceHelper" in markdown and "recommendedRuntimeProbeCommand" in markdown and "recommendedRuntimeSuccessCommand" in markdown and "recommendedOverwriteVariantCommand" in markdown,
                    "apiHasSummary": (api_payload.get("summary") or {}).get("orphanProfiles") == ["gy-orphan", "uc-orphan"],
                    "apiMarkdownHasGuide": "--profile-id gy-orphan" in str(api_markdown.get("markdown") or "") and "exactRefreshEvidenceHelper" in str(api_markdown.get("markdown") or "") and "recommendedRuntimeSuccessCommand" in str(api_markdown.get("markdown") or ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        runtime_orphan_recovery.latest_task_runtime_evidence = original_runtime
        runtime_orphan_recovery.list_profiles = original_profiles


if __name__ == "__main__":
    main()
