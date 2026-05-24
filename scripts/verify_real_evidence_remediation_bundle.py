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
from cloudpan_sync.real_evidence_remediation import (
    _create_command_for_provider,
    build_real_evidence_remediation_bundle,
    real_evidence_remediation_to_markdown,
)
from cloudpan_sync.provider_auth_hints import capture_field_hints, provider_auth_modes
from cloudpan_sync import webapp
from fastapi.testclient import TestClient


def main() -> None:
    synthetic_report = {
        "items": [
            {
                "providerKey": "guangya",
                "displayName": "Guangya",
                "authEvidence": {"ok": True},
                "listEvidence": {"ok": True},
                "metadataEvidence": {"ok": True},
                "createDirEvidence": {"ok": True},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["基础证据已齐，但尚未记录到真实 runtime 成功样本"],
            },
            {
                "providerKey": "189cloud",
                "displayName": "Tianyi 189Cloud",
                "authEvidence": {"ok": False},
                "listEvidence": {"ok": False},
                "metadataEvidence": {"ok": False},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["缺少通过的 auth validation 证据"],
            },
            {
                "providerKey": "quark",
                "displayName": "Quark",
                "authEvidence": {"ok": False},
                "listEvidence": {"ok": False},
                "metadataEvidence": {"ok": False},
                "createDirEvidence": {"ok": False},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0},
                "gaps": ["缺少通过的 auth validation 证据"],
            },
            {
                "providerKey": "115_open",
                "displayName": "115 Open",
                "authEvidence": {"ok": True},
                "listEvidence": {"ok": True},
                "metadataEvidence": {"ok": True},
                "createDirEvidence": {"ok": True},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0, "candidateCount": 1},
                "gaps": ["已有 fast-upload candidate 样本，但尚未记录到真实 runtime 成功样本"],
            },
            {
                "providerKey": "123_open",
                "displayName": "123Pan Open",
                "authEvidence": {"ok": True},
                "listEvidence": {"ok": True},
                "metadataEvidence": {"ok": True},
                "createDirEvidence": {"ok": True},
                "taskRuntimeEvidence": {"ok": False, "blockedCount": 0, "probeCount": 1},
                "gaps": ["已有 probe-only 样本，但尚未记录到真实传输成功样本"],
            },
        ]
    }
    synthetic_profiles = [
            {
                "profileId": "gy-rem-1",
                "providerKey": "guangya",
                "displayName": "smoke-guangya",
                "profileReady": True,
                "writeReady": True,
                "resolvedParentId": "gy-parent-1",
            },
        {
            "profileId": "115-rem-1",
            "providerKey": "115_open",
            "displayName": "115-ready",
            "profileReady": True,
            "writeReady": True,
            "resolvedParentId": "115-root-1",
        },
        {
            "profileId": "123-rem-1",
            "providerKey": "123_open",
            "displayName": "123-ready",
            "profileReady": True,
            "writeReady": True,
            "resolvedParentId": "0",
        },
        {
            "profileId": "189-rem-1",
            "providerKey": "189cloud",
            "displayName": "share-189",
            "profileReady": True,
            "writeReady": False,
        },
        {
            "profileId": "quark-rem-1",
            "providerKey": "quark",
            "displayName": "quark-manual",
            "profileReady": False,
            "writeReady": True,
        },
    ]
    bundle = build_real_evidence_remediation_bundle(report=synthetic_report, profile_views=synthetic_profiles)
    markdown = real_evidence_remediation_to_markdown(bundle)
    quark_create = _create_command_for_provider(
        provider_key="quark",
        auth_modes=provider_auth_modes("quark"),
        field_hints=capture_field_hints("quark"),
    )
    pan115_create = _create_command_for_provider(
        provider_key="115_open",
        auth_modes=provider_auth_modes("115_open"),
        field_hints=capture_field_hints("115_open"),
    )
    baidu_create = _create_command_for_provider(
        provider_key="baidu_netdisk",
        auth_modes=provider_auth_modes("baidu_netdisk"),
        field_hints=capture_field_hints("baidu_netdisk"),
    )
    xunlei_create = _create_command_for_provider(
        provider_key="xunlei",
        auth_modes=provider_auth_modes("xunlei"),
        field_hints=capture_field_hints("xunlei"),
    )
    pikpak_create = _create_command_for_provider(
        provider_key="pikpak",
        auth_modes=provider_auth_modes("pikpak"),
        field_hints=capture_field_hints("pikpak"),
    )

    with TemporaryDirectory() as tmp_dir:
        configure_data_dir(Path(tmp_dir))
        original_password = webapp.ADMIN_PASSWORD
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            api_bundle = client.get("/api/real_evidence_remediation_bundle").json()
            api_markdown = client.get("/api/real_evidence_remediation_markdown").json()
        finally:
            webapp.ADMIN_PASSWORD = original_password

    print(
        json.dumps(
            {
                "providerCount": ((bundle.get("summary") or {}).get("providerCount")),
                "providersWithCreateCommand": ((bundle.get("summary") or {}).get("providersWithCreateCommand")),
                "providersWithBootstrapCommand": ((bundle.get("summary") or {}).get("providersWithBootstrapCommand")),
                "providersWithPatchCommand": ((bundle.get("summary") or {}).get("providersWithPatchCommand")),
                "providersWithPatchProbeCommand": ((bundle.get("summary") or {}).get("providersWithPatchProbeCommand")),
                "providersWithRefreshEvidenceCommand": ((bundle.get("summary") or {}).get("providersWithRefreshEvidenceCommand")),
                "providersWithRuntimeProbeCommand": ((bundle.get("summary") or {}).get("providersWithRuntimeProbeCommand")),
                "providersWithLiveUploadCommand": ((bundle.get("summary") or {}).get("providersWithLiveUploadCommand")),
                "providersWithFastCandidateCommand": ((bundle.get("summary") or {}).get("providersWithFastCandidateCommand")),
                "providersBlockedOnly": ((bundle.get("summary") or {}).get("providersBlockedOnly")),
                "providersCandidateOnly": ((bundle.get("summary") or {}).get("providersCandidateOnly")),
                "providersProbeOnly": ((bundle.get("summary") or {}).get("providersProbeOnly")),
                "markdownHasCreateCommand": "create_auth_profile_stub.py" in markdown,
                "markdownHasBootstrapCommand": "recommendedBootstrapCommand" in markdown and "--probe" in markdown,
                "guangyaHasPatchCommand": "patch_auth_profile_extra.py" in markdown,
                "guangyaHasPatchProbeCommand": "patch_and_probe_auth_profile.py" in markdown,
                "markdownHasRefreshEvidenceCommand": "recommendedRefreshEvidenceCommand" in markdown and "--profile-id" in markdown,
                "markdownHasRuntimeProbeCommand": "recommendedRuntimeProbeCommand" in markdown and "create_runtime_probe_task.py" in markdown,
                "runtimeProbeCommandCarriesResolvedParent": "--target-parent-id 115-root-1" in markdown and "--evidence-dir tmp\\115_open-runtime-probe-evidence" in markdown,
                "markdownHasLiveUploadCommand": "recommendedLiveUploadCommand" in markdown and "create_live_upload_task.py" in markdown,
                "liveUploadCommandCarriesResolvedParent": "--target-parent-id gy-parent-1" in markdown and "--evidence-dir tmp\\guangya-live-evidence" in markdown,
                "markdownHasFastCandidateCommand": "recommendedFastCandidateCommand" in markdown and "create_fast_upload_candidate_task.py" in markdown,
                "fastCandidateCommandCarriesResolvedParent": "--target-parent-id 115-root-1" in markdown and "--evidence-dir tmp\\115_open-fast-candidate-evidence" in markdown,
                "markdownHasCandidateOnlyFlag": "runtimeCandidateOnly=True" in markdown,
                "markdownHasProbeOnlyFlag": "runtimeProbeOnly=True" in markdown,
                "probeOnlyKeepsRuntimeCommand": "123_open" in markdown and "create_runtime_probe_task.py" in markdown,
                "quarkPrefersManualCookie": "--provider-key quark --auth-mode manual_cookie" in quark_create and "--cookie YOUR_COOKIE" in quark_create,
                "quarkSkipsCookieHeaderExtra": "--set cookie_header=YOUR_VALUE" not in quark_create,
                "115PrefersManualCookie": "--provider-key 115_open --auth-mode manual_cookie" in pan115_create and "--cookie YOUR_COOKIE" in pan115_create,
                "baiduManualCookieSkipsAuthorizationExtra": "--provider-key baidu_netdisk --auth-mode manual_cookie" in baidu_create and "--set authorization=YOUR_VALUE" not in baidu_create,
                "xunleiPrefersManualToken": "--provider-key xunlei --auth-mode manual_token" in xunlei_create and "--token YOUR_TOKEN" in xunlei_create and "--set deviceId=YOUR_VALUE" in xunlei_create,
                "pikpakPrefersManualToken": "--provider-key pikpak --auth-mode manual_token" in pikpak_create and "--token YOUR_TOKEN" in pikpak_create and "--set authorization=YOUR_VALUE" not in pikpak_create,
                "cloud189HasHelper": "patch_189cloud_account_auth.py" in markdown,
                "markdownHasAuthModes": "recommendedAuthModes" in markdown,
                "markdownHasLoginUrl": "webLoginUrl" in markdown,
                "markdownHasFieldHints": "requiredFieldHints" in markdown,
                "markdownHasNextStep": "nextStep:" in markdown,
                "apiHasSummary": bool((api_bundle.get("summary") or {}).get("providerCount", 0) >= 0),
                "apiMarkdownHasTitle": "# CloudPan Sync 真实联调补救指南" in str(api_markdown.get("markdown", "")),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
