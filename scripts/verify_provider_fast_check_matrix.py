from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import provider_status_matrix


def _find_row(items: list[dict[str, object]], provider_key: str) -> dict[str, object]:
    for item in items:
        if str(item.get("providerKey") or "") == provider_key:
            return item
    raise RuntimeError(f"provider not found: {provider_key}")


def main() -> None:
    payload = provider_status_matrix.build_status_matrix()
    items = list(payload.get("items") or [])
    keys = [
        "guangya",
        "aliyundrive_open",
        "115_open",
        "189cloud",
        "baidu_netdisk",
        "quark",
        "uc",
        "xunlei",
        "pikpak",
        "123_open",
    ]
    rows = {key: _find_row(items, key) for key in keys}
    providers = {
        key: {
            "fast_check": rows[key].get("fast_check"),
            "metadata_ready": rows[key].get("metadata_ready"),
        }
        for key in keys
    }
    provider_fast_check_matrix_matches_expected_providers = (
        ((payload.get("summary") or {}).get("fastCheckCount")) == 10
        and all(bool((providers.get(key) or {}).get("fast_check")) for key in keys)
        and all(bool((providers.get(key) or {}).get("metadata_ready")) for key in keys)
    )
    print(
        json.dumps(
            {
                "fastCheckCount": ((payload.get("summary") or {}).get("fastCheckCount")),
                "providers": providers,
                "providerFastCheckMatrixMatchesExpectedProviders": provider_fast_check_matrix_matches_expected_providers,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
