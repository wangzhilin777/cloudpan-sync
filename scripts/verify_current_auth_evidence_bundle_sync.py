from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_evidence import build_auth_evidence_bundle
from cloudpan_sync.auth_store import list_profiles
from cloudpan_sync.webapp import _auth_profile_view


def main() -> None:
    bundle = build_auth_evidence_bundle(profiles=list_profiles(), profile_view_builder=_auth_profile_view)
    summary = dict(bundle.get("summary") or {})
    markdown = (ROOT / "docs" / "08-AUTH_EVIDENCE_BUNDLE.md").read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "summaryHasCurrentAuthEvidenceCounts": (
                    f"- profileCount: `{summary.get('profileCount', 0)}`" in markdown
                    and f"- profileReadyCount: `{summary.get('profileReadyCount', 0)}`" in markdown
                    and f"- writeReadyCount: `{summary.get('writeReadyCount', 0)}`" in markdown
                    and f"- validationOkCount: `{summary.get('validationOkCount', 0)}`" in markdown
                    and f"- probeOkCount: `{summary.get('probeOkCount', 0)}`" in markdown
                ),
                "summaryShowsExpectedAuthEvidenceCounts": (
                    summary.get("profileCount") == 3
                    and summary.get("profileReadyCount") == 0
                    and summary.get("writeReadyCount") == 3
                    and summary.get("validationOkCount") == 0
                    and summary.get("probeOkCount") == 0
                ),
                "hasSmokeGuangyaProfile": (
                    "### smoke-guangya [guangya]" in markdown
                    and "- profileReady: `False`" in markdown
                    and "- writeReady: `True`" in markdown
                    and "extra.parentId (aliases: parent_id/parentFileId/dirId/pid)" in markdown
                    and "token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token" in markdown
                    and "- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`" in markdown
                ),
                "hasRiskSmokeGuangyaProfile": (
                    "### risk-smoke-guangya [guangya]" in markdown
                    and markdown.count("- latestValidation: `Guangya live list requires parentId in request or auth profile extra.parentId.`") >= 2
                    and markdown.count("- latestProbe: `Guangya live list requires parentId in request or auth profile extra.parentId.`") >= 2
                ),
                "hasAliyunBootstrapProfile": (
                    "### aliyun-bootstrap [aliyundrive_open]" in markdown
                    and "- profileReady: `False`" in markdown
                    and "- writeReady: `True`" in markdown
                    and "- resolvedParentId: `root`" in markdown
                    and "token looks like placeholder data; replace tok-demo with a real Aliyun OAuth token" in markdown
                    and "extra.domainId still uses placeholder data; replace domain-demo with a real domainId" in markdown
                    and "extra.driveId still uses placeholder data; replace drive-demo with a real driveId" in markdown
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
