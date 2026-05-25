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


def _section(markdown: str, marker: str) -> str:
    start = markdown.find(marker)
    if start < 0:
        return ""
    next_start = markdown.find("\n### ", start + 1)
    if next_start < 0:
        return markdown[start:]
    return markdown[start:next_start]


def main() -> None:
    bundle = build_auth_remediation_bundle(profile_views=[_auth_profile_view(profile) for profile in list_profiles()])
    summary = dict(bundle.get("summary") or {})
    markdown = (ROOT / "docs" / "09-AUTH_REMEDIATION_GUIDE.md").read_text(encoding="utf-8")
    smoke_guangya = _section(markdown, "### smoke-guangya [guangya]")
    risk_smoke_guangya = _section(markdown, "### risk-smoke-guangya [guangya]")
    aliyun_bootstrap = _section(markdown, "### aliyun-bootstrap [aliyundrive_open]")

    print(
        json.dumps(
            {
                "summaryHasCurrentAuthRemediationCounts": (
                    f"- profileCount: `{summary.get('profileCount', 0)}`" in markdown
                    and f"- readyCount: `{summary.get('readyCount', 0)}`" in markdown
                    and f"- needsFixCount: `{summary.get('needsFixCount', 0)}`" in markdown
                    and f"- writeReadyCount: `{summary.get('writeReadyCount', 0)}`" in markdown
                    and f"- writeNeedsFixCount: `{summary.get('writeNeedsFixCount', 0)}`" in markdown
                    and f"- needsSecretRefreshCount: `{summary.get('needsSecretRefreshCount', 0)}`" in markdown
                    and f"- profileSummary: `ready={', '.join(summary.get('readyProfiles', [])) or '(none)'}` `needsFix={', '.join(summary.get('needsFixProfiles', [])) or '(none)'}` `writeReady={', '.join(summary.get('writeReadyProfiles', [])) or '(none)'}` `writeNeedsFix={', '.join(summary.get('writeNeedsFixProfiles', [])) or '(none)'}` `needsSecretRefresh={', '.join(summary.get('needsSecretRefreshProfiles', [])) or '(none)'}`" in markdown
                ),
                "summaryShowsExpectedAuthRemediationCounts": (
                    summary.get("profileCount") == 3
                    and summary.get("readyCount") == 0
                    and summary.get("needsFixCount") == 3
                    and summary.get("writeReadyCount") == 3
                    and summary.get("writeNeedsFixCount") == 0
                    and summary.get("needsSecretRefreshCount") == 3
                    and summary.get("readyProfiles") == []
                    and summary.get("needsFixProfiles") == ["aliyun-bootstrap", "risk-smoke-guangya", "smoke-guangya"]
                    and summary.get("writeReadyProfiles") == ["aliyun-bootstrap", "risk-smoke-guangya", "smoke-guangya"]
                    and summary.get("writeNeedsFixProfiles") == []
                    and summary.get("needsSecretRefreshProfiles") == ["aliyun-bootstrap", "risk-smoke-guangya", "smoke-guangya"]
                ),
                "hasSmokeGuangyaRecreateProbeCommand": (
                    "- placeholderSecretFieldHints: `token`" in smoke_guangya
                    and "extra.parentId (aliases: parent_id/parentFileId/dirId/pid)" in smoke_guangya
                    and "token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token" in smoke_guangya
                    and "- recommendedPatchCommand:" not in smoke_guangya
                    and "create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name smoke-guangya --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe" in smoke_guangya
                ),
                "hasRiskSmokeGuangyaRecreateProbeCommand": (
                    "- placeholderSecretFieldHints: `token`" in risk_smoke_guangya
                    and "- recommendedPatchCommand:" not in risk_smoke_guangya
                    and "create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name risk-smoke-guangya --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe" in risk_smoke_guangya
                ),
                "hasAliyunBootstrapRecreateProbeCommand": (
                    "- profileReady: `False`" in aliyun_bootstrap
                    and "- writeReady: `True`" in aliyun_bootstrap
                    and "- resolvedParentId: `root`" in aliyun_bootstrap
                    and "- placeholderSecretFieldHints: `token`" in aliyun_bootstrap
                    and "- recommendedPatchCommand:" not in aliyun_bootstrap
                    and "create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe" in aliyun_bootstrap
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
