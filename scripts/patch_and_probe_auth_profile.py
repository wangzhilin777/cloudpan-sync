from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_evidence import auth_profile_evidence_to_markdown, refresh_auth_profile_evidence
from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_store import get_profile, update_profile
from cloudpan_sync.real_evidence_remediation import build_real_evidence_remediation_bundle
from cloudpan_sync.webapp import _auth_profile_evidence


def _parse_set_value(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("Expected KEY=VALUE")
    key, value = raw.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        raise argparse.ArgumentTypeError("KEY cannot be empty")
    if not value:
        raise argparse.ArgumentTypeError("VALUE cannot be empty")
    return key, value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Patch one saved auth profile, or just refresh its evidence, then run provider-aware validation and live probe."
    )
    parser.add_argument("--profile-id", required=True, help="Exact profileId to update.")
    parser.add_argument("--set", dest="sets", action="append", default=[], type=_parse_set_value, help="KEY=VALUE extra patch. Repeatable.")
    parser.add_argument("--dir-name", default="", help="Optional create_dir probe name.")
    parser.add_argument("--page-size", type=int, default=100, help="Optional live probe page size.")
    parser.add_argument("--write", action="store_true", help="Persist the extra patch before validate/probe.")
    parser.add_argument("--data-dir", default="", help="Override .cloudpan_sync_data directory for local verification.")
    parser.add_argument("--evidence-output", default="", help="Optional markdown evidence output file path.")
    return parser


def _merge_extra(existing: dict[str, str], updates: dict[str, str]) -> dict[str, str]:
    merged = dict(existing or {})
    for key, value in updates.items():
        text = str(value or "").strip()
        if text:
            merged[key] = text
    return merged


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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.data_dir:
        configure_data_dir(args.data_dir)
    profile = get_profile(args.profile_id)
    if profile is None:
        raise SystemExit(f"profile_not_found: {args.profile_id}")

    updates = {key: value for key, value in args.sets}
    profile.extra = _merge_extra(profile.extra or {}, updates)
    if args.write:
        update_profile(profile)
    evidence = refresh_auth_profile_evidence(
        profile=profile,
        page_size=max(1, int(args.page_size or 100)),
        dir_name=str(args.dir_name or profile.extra.get("dirName") or "").strip(),
        persist=bool(args.write),
        profile_view_builder=_auth_profile_evidence.__globals__["_auth_profile_view"],
    )
    validation = evidence.get("latestValidation") or {}
    probe = evidence.get("latestProbe") or {}

    evidence_output = ""
    if args.evidence_output:
        output_path = Path(args.evidence_output)
        output_path.write_text(auth_profile_evidence_to_markdown(evidence), encoding="utf-8")
        evidence_output = str(output_path.resolve())

    print(
        json.dumps(
            {
                "profileId": profile.profileId,
                "providerKey": profile.providerKey,
                "written": bool(args.write),
                "extra": profile.extra,
                "validation": validation,
                "probe": probe,
                "evidenceOutput": evidence_output,
                "remediation": _remediation_followup(profile.profileId),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
