from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_evidence import auth_profile_evidence_to_markdown, refresh_auth_profile_evidence
from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_live_validate import run_profile_live_validation
from cloudpan_sync.auth_store import save_profile
from cloudpan_sync.models import AuthProfileInput
from cloudpan_sync.real_evidence_remediation import build_real_evidence_remediation_bundle
from cloudpan_sync.webapp import _auth_profile_evidence


def _parse_extra(values: list[str]) -> dict[str, str]:
    extra: dict[str, str] = {}
    for value in values:
        text = str(value or "").strip()
        if not text or "=" not in text:
            continue
        key, raw = text.split("=", 1)
        key = key.strip()
        raw = raw.strip()
        if key and raw:
            extra[key] = raw
    return extra


def _remediation_followup(profile_id: str) -> dict[str, object]:
    payload = build_real_evidence_remediation_bundle()
    for item in payload.get("items", []):
        row = dict(item or {})
        profile_ids = [str(value or "") for value in (row.get("profileIds") or [])]
        if profile_id not in profile_ids:
            continue
        return {
            "nextStep": str(row.get("nextStep") or ""),
            "recommendedRefreshEvidenceCommand": str(row.get("recommendedRefreshEvidenceCommand") or ""),
            "recommendedPostRefreshRuntimeCommand": str(row.get("recommendedPostRefreshRuntimeCommand") or ""),
            "recommendedRuntimeSuccessCommand": str(row.get("recommendedRuntimeSuccessCommand") or ""),
            "recommendedOverwriteVariantCommand": str(row.get("recommendedOverwriteVariantCommand") or ""),
        }
    return {}


def main() -> None:
    custom_data_dir = str(os.environ.get("CLOUDPAN_SYNC_DATA_DIR") or "").strip()
    if custom_data_dir:
        configure_data_dir(custom_data_dir)
    parser = argparse.ArgumentParser(description="Create a local auth profile stub for CloudPan Sync.")
    parser.add_argument("--provider-key", required=True, help="Provider key, such as guangya or aliyundrive_open.")
    parser.add_argument("--auth-mode", required=True, help="Auth mode, such as manual_token or manual_cookie.")
    parser.add_argument("--display-name", default="", help="Display name. Defaults to providerKey-authMode.")
    parser.add_argument("--token", default="", help="Optional token value.")
    parser.add_argument("--cookie", default="", help="Optional cookie value.")
    parser.add_argument("--set", dest="extra", action="append", default=[], help="Extra field in key=value form.")
    parser.add_argument("--validate", action="store_true", help="Run provider-aware live validation after saving.")
    parser.add_argument("--probe", action="store_true", help="Run validation + live probe evidence refresh after saving.")
    parser.add_argument("--page-size", type=int, default=100, help="Optional live probe page size.")
    parser.add_argument("--dir-name", default="", help="Optional create_dir probe name.")
    parser.add_argument("--evidence-output", default="", help="Optional markdown evidence output file path.")
    args = parser.parse_args()

    payload = AuthProfileInput(
        providerKey=str(args.provider_key).strip(),
        authMode=str(args.auth_mode).strip(),
        displayName=str(args.display_name).strip() or f"{str(args.provider_key).strip()}-{str(args.auth_mode).strip()}",
        token=str(args.token or "").strip(),
        cookie=str(args.cookie or "").strip(),
        extra=_parse_extra(list(args.extra or [])),
    )
    profile = save_profile(payload)
    result: dict[str, object] = {
        "profileId": profile.profileId,
        "providerKey": profile.providerKey,
        "authMode": profile.authMode,
        "displayName": profile.displayName,
        "extra": dict(profile.extra or {}),
        "written": True,
    }
    if args.probe:
        evidence = refresh_auth_profile_evidence(
            profile=profile,
            page_size=max(1, int(args.page_size or 100)),
            dir_name=str(args.dir_name or "").strip(),
            persist=True,
            profile_view_builder=_auth_profile_evidence.__globals__["_auth_profile_view"],
        )
        result["evidence"] = evidence
        if args.evidence_output:
            output_path = Path(args.evidence_output)
            output_path.write_text(auth_profile_evidence_to_markdown(evidence), encoding="utf-8")
            result["evidenceOutput"] = str(output_path.resolve())
    elif args.validate:
        result["validation"] = run_profile_live_validation(profile.profileId)
    result["remediation"] = _remediation_followup(profile.profileId)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
