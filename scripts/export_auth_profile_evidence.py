from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_profile_evidence import auth_profile_evidence_to_markdown
from cloudpan_sync.auth_store import get_profile
from cloudpan_sync.webapp import _auth_profile_evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export a single auth profile evidence snapshot as Markdown.")
    parser.add_argument("--profile-id", required=True, help="Exact profileId to export.")
    parser.add_argument("--data-dir", default="", help="Override .cloudpan_sync_data directory.")
    parser.add_argument("--output", default="", help="Optional output markdown file path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.data_dir:
        configure_data_dir(args.data_dir)
    profile = get_profile(args.profile_id)
    if profile is None:
        raise SystemExit(f"profile_not_found: {args.profile_id}")
    markdown = auth_profile_evidence_to_markdown(_auth_profile_evidence(profile))
    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
        print(Path(args.output).resolve())
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
