from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_profile_remediation import auth_remediation_bundle_to_markdown, build_auth_remediation_bundle
from cloudpan_sync.auth_store import list_profiles
from cloudpan_sync import webapp
from cloudpan_sync.webapp import _auth_profile_view
from fastapi.testclient import TestClient


def _section(markdown: str, marker: str) -> str:
    start = markdown.find(marker)
    if start < 0:
        return ""
    next_start = markdown.find("\n### ", start + 1)
    if next_start < 0:
        return markdown[start:]
    return markdown[start:next_start]


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "gy-rem-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "smoke-guangya",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {},
                        "status": "invalid",
                        "lastError": "http_error:401",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                {
                    "profileId": "ali-rem-1",
                    "providerKey": "aliyundrive_open",
                    "authMode": "official_oauth",
                    "displayName": "aliyun-bootstrap",
                    "token": "tok-demo",
                    "cookie": "",
                    "extra": {"domainId": "domain-demo", "driveId": "drive-demo"},
                    "status": "invalid",
                    "lastError": "http_error:404",
                    "createdAt": "2026-05-23T00:00:00+00:00",
                    "updatedAt": "2026-05-23T00:00:00+00:00",
                },
                    {
                        "profileId": "189-rem-1",
                        "providerKey": "189cloud",
                        "authMode": "manual_cookie",
                        "displayName": "189-readonly-share",
                        "token": "",
                        "cookie": "",
                        "extra": {"shareCode": "share-demo"},
                        "status": "verified",
                        "lastError": "",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        configure_data_dir(data_dir)
        bundle = build_auth_remediation_bundle(profile_views=[_auth_profile_view(profile) for profile in list_profiles()])
        markdown = auth_remediation_bundle_to_markdown(bundle)
        summary = dict(bundle.get("summary") or {})
        smoke_guangya = _section(markdown, "### smoke-guangya [guangya]")
        aliyun_bootstrap = _section(markdown, "### aliyun-bootstrap [aliyundrive_open]")
        share_189 = _section(markdown, "### 189-readonly-share [189cloud]")

        original_password = webapp.ADMIN_PASSWORD
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            api_bundle = client.get("/api/auth/remediation_bundle").json()
            api_markdown = client.get("/api/auth/remediation_bundle_markdown").json()
        finally:
            webapp.ADMIN_PASSWORD = original_password

        print(
            json.dumps(
                {
                    "profileCount": summary.get("profileCount"),
                    "needsFixCount": summary.get("needsFixCount"),
                    "writeNeedsFixCount": summary.get("writeNeedsFixCount"),
                    "needsSecretRefreshCount": summary.get("needsSecretRefreshCount"),
                    "readyProfiles": summary.get("readyProfiles"),
                    "needsFixProfiles": summary.get("needsFixProfiles"),
                    "writeReadyProfiles": summary.get("writeReadyProfiles"),
                    "writeNeedsFixProfiles": summary.get("writeNeedsFixProfiles"),
                    "needsSecretRefreshProfiles": summary.get("needsSecretRefreshProfiles"),
                    "markdownHasSummary": (
                        "- profileCount: `3`" in markdown
                        and "- readyCount: `1`" in markdown
                        and "- needsFixCount: `2`" in markdown
                        and "- writeReadyCount: `2`" in markdown
                        and "- writeNeedsFixCount: `1`" in markdown
                        and "- needsSecretRefreshCount: `2`" in markdown
                        and "- profileSummary: `ready=189-readonly-share` `needsFix=aliyun-bootstrap, smoke-guangya` `writeReady=aliyun-bootstrap, smoke-guangya` `writeNeedsFix=189-readonly-share` `needsSecretRefresh=aliyun-bootstrap, smoke-guangya`" in markdown
                    ),
                    "markdownHasGuangyaRecreateProbeCommand": (
                        "- placeholderSecretFieldHints: `token`" in smoke_guangya
                        and "- liveRejected: profiles=`smoke-guangya` placeholderProfiles=`smoke-guangya` statuses=`401`" in smoke_guangya
                        and "- liveRejectedSummaries: `smoke-guangya:401`" in smoke_guangya
                        and "- recommendedPatchCommand:" not in smoke_guangya
                        and "create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name smoke-guangya --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe"
                        in smoke_guangya
                    ),
                    "markdownHasAliyunRecreateProbeCommand": (
                        "- placeholderSecretFieldHints: `token`" in aliyun_bootstrap
                        and "- liveRejected: profiles=`aliyun-bootstrap` placeholderProfiles=`aliyun-bootstrap` statuses=`404`" in aliyun_bootstrap
                        and "- liveRejectedSummaries: `aliyun-bootstrap:404`" in aliyun_bootstrap
                        and "- recommendedPatchCommand:" not in aliyun_bootstrap
                        and "create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe"
                        in aliyun_bootstrap
                    ),
                    "markdownHas189ReadonlyPatchCommand": (
                        "- writeBlockerNote:" in share_189
                        and "patch_189cloud_account_auth.py" in share_189
                    ),
                    "apiReadyCount": ((api_bundle.get("summary") or {}).get("readyCount")),
                    "apiWriteReadyCount": ((api_bundle.get("summary") or {}).get("writeReadyCount")),
                    "apiNeedsSecretRefreshCount": ((api_bundle.get("summary") or {}).get("needsSecretRefreshCount")),
                    "apiReadyProfiles": ((api_bundle.get("summary") or {}).get("readyProfiles")),
                    "apiNeedsFixProfiles": ((api_bundle.get("summary") or {}).get("needsFixProfiles")),
                    "apiWriteReadyProfiles": ((api_bundle.get("summary") or {}).get("writeReadyProfiles")),
                    "apiWriteNeedsFixProfiles": ((api_bundle.get("summary") or {}).get("writeNeedsFixProfiles")),
                    "apiNeedsSecretRefreshProfiles": ((api_bundle.get("summary") or {}).get("needsSecretRefreshProfiles")),
                    "apiSummaryMatchesSyntheticScenario": (
                        ((api_bundle.get("summary") or {}).get("profileCount")) == 3
                        and ((api_bundle.get("summary") or {}).get("readyCount")) == 1
                        and ((api_bundle.get("summary") or {}).get("needsFixCount")) == 2
                        and ((api_bundle.get("summary") or {}).get("writeReadyCount")) == 2
                        and ((api_bundle.get("summary") or {}).get("writeNeedsFixCount")) == 1
                        and ((api_bundle.get("summary") or {}).get("needsSecretRefreshCount")) == 2
                        and ((api_bundle.get("summary") or {}).get("readyProfiles")) == ["189-readonly-share"]
                        and ((api_bundle.get("summary") or {}).get("needsFixProfiles")) == ["aliyun-bootstrap", "smoke-guangya"]
                        and ((api_bundle.get("summary") or {}).get("writeReadyProfiles")) == ["aliyun-bootstrap", "smoke-guangya"]
                        and ((api_bundle.get("summary") or {}).get("writeNeedsFixProfiles")) == ["189-readonly-share"]
                        and ((api_bundle.get("summary") or {}).get("needsSecretRefreshProfiles")) == ["aliyun-bootstrap", "smoke-guangya"]
                    ),
                    "apiHasAliyunRecreateProbeCommand": bool(
                        next(
                            (
                                row
                                for row in (api_bundle.get("items") or [])
                                if str((row or {}).get("providerKey") or "") == "aliyundrive_open"
                                and bool((row or {}).get("needsSecretRefresh"))
                                and "token" in ",".join((row or {}).get("placeholderSecretFieldHints") or [])
                                and list((row or {}).get("liveRejectedStatuses") or []) == ["404"]
                                and list((row or {}).get("placeholderLiveRejectedProfiles") or []) == ["aliyun-bootstrap"]
                                and "create_auth_profile_stub.py" in str((row or {}).get("recommendedRecreateProbeCommand") or "")
                            ),
                            None,
                        )
                    ),
                    "apiMarkdownHasTitle": "# 授权补救指南 / Auth Remediation Guide" in str(api_markdown.get("markdown", "")),
                    "apiMarkdownHasRecreateProbeCommand": "recommendedRecreateProbeCommand" in str(api_markdown.get("markdown", ""))
                    and "placeholderSecretFieldHints: `token`" in str(api_markdown.get("markdown", ""))
                    and "liveRejected: profiles=`aliyun-bootstrap` placeholderProfiles=`aliyun-bootstrap` statuses=`404`" in str(api_markdown.get("markdown", ""))
                    and "profileSummary: `ready=189-readonly-share` `needsFix=aliyun-bootstrap, smoke-guangya` `writeReady=aliyun-bootstrap, smoke-guangya` `writeNeedsFix=189-readonly-share` `needsSecretRefresh=aliyun-bootstrap, smoke-guangya`" in str(api_markdown.get("markdown", "")),
                    "apiMarkdownHas189ReadonlyPatchCommand": "patch_189cloud_account_auth.py" in str(api_markdown.get("markdown", "")),
                    "authRemediationBundleFlowMatchesExpectedGuidance": (
                        summary.get("profileCount") == 3
                        and summary.get("needsFixCount") == 2
                        and summary.get("writeNeedsFixCount") == 1
                        and summary.get("needsSecretRefreshCount") == 2
                        and summary.get("readyProfiles") == ["189-readonly-share"]
                        and summary.get("needsFixProfiles") == ["aliyun-bootstrap", "smoke-guangya"]
                        and summary.get("writeReadyProfiles") == ["aliyun-bootstrap", "smoke-guangya"]
                        and summary.get("writeNeedsFixProfiles") == ["189-readonly-share"]
                        and summary.get("needsSecretRefreshProfiles") == ["aliyun-bootstrap", "smoke-guangya"]
                        and "- profileCount: `3`" in markdown
                        and "- needsFixCount: `2`" in markdown
                        and "- writeNeedsFixCount: `1`" in markdown
                        and "create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name smoke-guangya --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe" in smoke_guangya
                        and "create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe" in aliyun_bootstrap
                        and "patch_189cloud_account_auth.py" in share_189
                        and ((api_bundle.get("summary") or {}).get("profileCount")) == 3
                        and ((api_bundle.get("summary") or {}).get("readyCount")) == 1
                        and ((api_bundle.get("summary") or {}).get("needsFixCount")) == 2
                        and ((api_bundle.get("summary") or {}).get("writeReadyCount")) == 2
                        and ((api_bundle.get("summary") or {}).get("writeNeedsFixCount")) == 1
                        and ((api_bundle.get("summary") or {}).get("needsSecretRefreshCount")) == 2
                        and ((api_bundle.get("summary") or {}).get("readyProfiles")) == ["189-readonly-share"]
                        and ((api_bundle.get("summary") or {}).get("needsFixProfiles")) == ["aliyun-bootstrap", "smoke-guangya"]
                        and ((api_bundle.get("summary") or {}).get("writeReadyProfiles")) == ["aliyun-bootstrap", "smoke-guangya"]
                        and ((api_bundle.get("summary") or {}).get("writeNeedsFixProfiles")) == ["189-readonly-share"]
                        and ((api_bundle.get("summary") or {}).get("needsSecretRefreshProfiles")) == ["aliyun-bootstrap", "smoke-guangya"]
                        and "# 授权补救指南 / Auth Remediation Guide" in str(api_markdown.get("markdown", ""))
                        and "recommendedRecreateProbeCommand" in str(api_markdown.get("markdown", ""))
                        and "patch_189cloud_account_auth.py" in str(api_markdown.get("markdown", ""))
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
