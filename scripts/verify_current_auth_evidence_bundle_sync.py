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
    guangya_restore_live = "### guangya-restore-gy-live-1 [guangya]" in markdown
    pikpak_restore_live = "### pikpak-restore-pikpak-live-1 [pikpak]" in markdown
    uc_restore_live = "### uc-restore-uc-live-1 [uc]" in markdown

    print(
        json.dumps(
            {
                "summaryHasCurrentAuthEvidenceCounts": (
                    f"- profileCount: `{summary.get('profileCount', 0)}`" in markdown
                    and f"- profileReadyCount: `{summary.get('profileReadyCount', 0)}`" in markdown
                    and f"- writeReadyCount: `{summary.get('writeReadyCount', 0)}`" in markdown
                    and f"- validationOkCount: `{summary.get('validationOkCount', 0)}`" in markdown
                    and f"- probeOkCount: `{summary.get('probeOkCount', 0)}`" in markdown
                        and f"- profileSummary: `profileReady={', '.join(summary.get('profileReadyProfiles', [])) or '(none)'}` `writeReady={', '.join(summary.get('writeReadyProfiles', [])) or '(none)'}` `validationOk={', '.join(summary.get('validationOkProfiles', [])) or '(none)'}` `probeOk={', '.join(summary.get('probeOkProfiles', [])) or '(none)'}`" in markdown
                ),
                "summaryShowsExpectedAuthEvidenceCounts": (
                    summary.get("profileCount") == 9
                    and summary.get("profileReadyCount") == 0
                    and summary.get("writeReadyCount") == 9
                    and summary.get("validationOkCount") == 0
                    and summary.get("probeOkCount") == 0
                    and summary.get("profileReadyProfiles") == []
                    and summary.get("writeReadyProfiles")
                    == [
                        "aliyun-bootstrap",
                        "guangya-restore-gy-live-1",
                        "guangya-restore-gy-live-2",
                        "guangya-restore-gy-live-defaults-1",
                        "guangya-restore-gy-orphan-live-1",
                        "pikpak-restore-pikpak-live-1",
                        "risk-smoke-guangya",
                        "smoke-guangya",
                        "uc-restore-uc-live-1",
                    ]
                    and summary.get("validationOkProfiles") == []
                    and summary.get("probeOkProfiles") == []
                ),
                "hasSmokeGuangyaProfile": (
                    "### smoke-guangya [guangya]" in markdown
                    and "- profileReady: `False`" in markdown
                    and "- writeReady: `True`" in markdown
                    and "extra.parentId (aliases: parent_id/parentFileId/dirId/pid)" in markdown
                    and "token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token" in markdown
                    and "- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`" in markdown
                    and "- placeholderSecretFieldHints: `token`" in markdown
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
                    and "- placeholderSecretFieldHints: `token`" in markdown
                    and "- liveRejected: profiles=`aliyun-bootstrap` placeholderProfiles=`aliyun-bootstrap` statuses=`404`" in markdown
                    and "- liveRejectedSummaries: `aliyun-bootstrap:404`" in markdown
                ),
                "hasGuangyaRestoreLiveRejectedProfile": (
                    guangya_restore_live
                    and "- liveRejected: profiles=`guangya-restore-gy-live-1` placeholderProfiles=`guangya-restore-gy-live-1` statuses=`401`" in markdown
                    and "- liveRejectedSummaries: `guangya-restore-gy-live-1:401`" in markdown
                ),
                "hasPikpakRestoreLiveRejectedProfile": (
                    pikpak_restore_live
                    and "- liveRejected: profiles=`pikpak-restore-pikpak-live-1` placeholderProfiles=`pikpak-restore-pikpak-live-1` statuses=`401`" in markdown
                    and "- liveRejectedSummaries: `pikpak-restore-pikpak-live-1:401`" in markdown
                ),
                "hasUcRestoreLiveRejectedProfile": (
                    uc_restore_live
                    and "- liveRejected: profiles=`uc-restore-uc-live-1` placeholderProfiles=`uc-restore-uc-live-1` statuses=`404`" in markdown
                    and "- liveRejectedSummaries: `uc-restore-uc-live-1:404`" in markdown
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
