from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_evidence import auth_evidence_bundle_to_markdown, build_auth_evidence_bundle
from cloudpan_sync.auth_store import list_profiles
from cloudpan_sync.webapp import _auth_profile_view


def main() -> None:
    out = ROOT / "docs" / "08-AUTH_EVIDENCE_BUNDLE.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    bundle = build_auth_evidence_bundle(profiles=list_profiles(), profile_view_builder=_auth_profile_view)
    out.write_text(auth_evidence_bundle_to_markdown(bundle), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
