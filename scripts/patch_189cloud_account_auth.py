from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir, patch_auth_profiles
from cloudpan_sync.tianyi_auth_capture import extract_189cloud_account_auth


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Patch 189Cloud account-level write auth from captured headers or curl text.")
    parser.add_argument("--profile-id", action="append", default=[], help="Exact profileId to update. Repeatable.")
    parser.add_argument("--display-name-contains", default="", help="Optional displayName contains filter.")
    parser.add_argument("--raw-file", default="", help="File containing captured headers, curl text, or JSON.")
    parser.add_argument("--raw-text", default="", help="Inline captured headers, curl text, or JSON.")
    parser.add_argument("--write", action="store_true", help="Persist the patched profiles to disk.")
    parser.add_argument("--revalidate", action="store_true", help="Run provider-aware auth revalidation after patch.")
    parser.add_argument("--data-dir", default="", help="Override .cloudpan_sync_data directory for local verification.")
    return parser


def _load_raw_text(args: argparse.Namespace) -> str:
    if args.raw_text:
        return str(args.raw_text)
    if args.raw_file:
        return Path(args.raw_file).read_text(encoding="utf-8")
    raise ValueError("Either --raw-text or --raw-file is required.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.profile_id and not args.display_name_contains:
        parser.error("Provide at least one selector: --profile-id or --display-name-contains.")
    if args.data_dir:
        configure_data_dir(args.data_dir)

    raw_text = _load_raw_text(args)
    extracted = extract_189cloud_account_auth(raw_text)
    missing = [key for key in ("accessToken", "signature", "date") if not extracted.get(key)]
    if missing:
        parser.error(f"Could not extract required 189Cloud account auth fields: {', '.join(missing)}")

    result = patch_auth_profiles(
        extra_updates=extracted,
        profile_ids=args.profile_id,
        provider_key="189cloud",
        display_name_contains=args.display_name_contains,
        write=args.write,
        revalidate=args.revalidate,
    )
    print(
        json.dumps(
            {
                "extracted": extracted,
                "result": result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

