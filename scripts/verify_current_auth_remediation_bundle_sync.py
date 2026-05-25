from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_remediation import build_auth_remediation_bundle
from cloudpan_sync.auth_store import list_profiles
from cloudpan_sync.webapp import _auth_profile_view


def main() -> None:
    bundle = build_auth_remediation_bundle(profile_views=[_auth_profile_view(profile) for profile in list_profiles()])
    summary = dict(bundle.get("summary") or {})
    markdown = (ROOT / "docs" / "09-AUTH_REMEDIATION_GUIDE.md").read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "summaryHasCurrentAuthRemediationCounts": (
                    f"- profileCount: `{summary.get('profileCount', 0)}`" in markdown
                    and f"- readyCount: `{summary.get('readyCount', 0)}`" in markdown
                    and f"- needsFixCount: `{summary.get('needsFixCount', 0)}`" in markdown
                    and f"- writeReadyCount: `{summary.get('writeReadyCount', 0)}`" in markdown
                    and f"- writeNeedsFixCount: `{summary.get('writeNeedsFixCount', 0)}`" in markdown
                ),
                "summaryShowsExpectedAuthRemediationCounts": (
                    summary.get("profileCount") == 3
                    and summary.get("readyCount") == 0
                    and summary.get("needsFixCount") == 3
                    and summary.get("writeReadyCount") == 3
                    and summary.get("writeNeedsFixCount") == 0
                ),
                "hasSmokeGuangyaPatchCommand": (
                    "### smoke-guangya [guangya]" in markdown
                    and "extra.parentId (aliases: parent_id/parentFileId/dirId/pid)" in markdown
                    and "token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token" in markdown
                    and "--profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate" in markdown
                ),
                "hasRiskSmokeGuangyaPatchCommand": (
                    "### risk-smoke-guangya [guangya]" in markdown
                    and "--profile-id 08684618-ea29-48a4-b603-2e40cdc37c3d --set parentId=YOUR_REAL_PARENT_ID --write --revalidate" in markdown
                ),
                "hasAliyunBootstrapReadyProfile": (
                    "### aliyun-bootstrap [aliyundrive_open]" in markdown
                    and "- profileReady: `False`" in markdown
                    and "- writeReady: `True`" in markdown
                    and "- resolvedParentId: `root`" in markdown
                    and "--profile-id 22173a49-2206-4da8-8624-9bab7bbbe64b --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write --revalidate" in markdown
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
