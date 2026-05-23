from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_evidence import auth_evidence_bundle_to_markdown, refresh_auth_evidence_bundle
from cloudpan_sync.auth_profile_patch import configure_data_dir, patch_auth_profiles, select_auth_profiles
from cloudpan_sync.webapp import _auth_profile_view


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
        description="Patch selected auth profiles, refresh their evidence, and export an auth evidence bundle."
    )
    parser.add_argument("--profile-id", action="append", default=[], help="Exact profileId to update. Repeatable.")
    parser.add_argument("--provider-key", default="", help="Optional providerKey filter.")
    parser.add_argument("--display-name-contains", default="", help="Optional displayName contains filter.")
    parser.add_argument("--set", dest="sets", action="append", default=[], type=_parse_set_value, help="KEY=VALUE extra patch. Repeatable.")
    parser.add_argument("--page-size", type=int, default=100, help="Optional evidence refresh page size.")
    parser.add_argument("--dir-name", default="", help="Optional create_dir probe dir name.")
    parser.add_argument("--write", action="store_true", help="Persist profile patch and refreshed evidence to disk.")
    parser.add_argument("--data-dir", default="", help="Override .cloudpan_sync_data directory for local verification.")
    parser.add_argument("--bundle-output", default="", help="Optional markdown output path for the refreshed evidence bundle.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.profile_id and not args.provider_key and not args.display_name_contains:
        parser.error("Provide at least one selector: --profile-id, --provider-key, or --display-name-contains.")
    if not args.sets:
        parser.error("At least one --set KEY=VALUE is required.")
    if args.data_dir:
        configure_data_dir(args.data_dir)

    extra_updates = {key: value for key, value in args.sets}
    patch_result = patch_auth_profiles(
        extra_updates=extra_updates,
        profile_ids=args.profile_id,
        provider_key=args.provider_key,
        display_name_contains=args.display_name_contains,
        write=bool(args.write),
        revalidate=False,
    )
    selected_profiles = select_auth_profiles(
        profile_ids=args.profile_id,
        provider_key=args.provider_key,
        display_name_contains=args.display_name_contains,
    )
    bundle = refresh_auth_evidence_bundle(
        profiles=selected_profiles,
        profile_view_builder=_auth_profile_view,
        page_size=max(1, int(args.page_size or 100)),
        dir_name=str(args.dir_name or "").strip(),
        persist=bool(args.write),
    )

    bundle_output = ""
    if args.bundle_output:
        output_path = Path(args.bundle_output)
        output_path.write_text(auth_evidence_bundle_to_markdown(bundle), encoding="utf-8")
        bundle_output = str(output_path.resolve())

    print(
        json.dumps(
            {
                "patch": patch_result,
                "bundleSummary": bundle.get("summary", {}),
                "bundleOutput": bundle_output,
                "profileIds": [getattr(profile, "profileId", "") for profile in selected_profiles],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
