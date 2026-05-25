from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.export_local_live_adapter_verification import build_payload


PROVIDERS = (
    "guangya",
    "aliyundrive_open",
    "189cloud",
    "baidu_netdisk",
    "123_open",
    "115_open",
    "xunlei",
    "pikpak",
    "quark",
    "uc",
)


def main() -> None:
    payload = build_payload()
    markdown = (ROOT / "docs" / "07-LOCAL_LIVE_ADAPTER_VERIFICATION.md").read_text(encoding="utf-8")
    probe_matrix = dict(payload.get("probe_and_matrix") or {})
    probe_checks = dict(probe_matrix.get("probeChecks") or {})
    matrix_rows = dict(probe_matrix.get("matrixRows") or {})

    print(
        json.dumps(
            {
                "allProviderSectionsPresent": all(f"## {provider}" in markdown for provider in PROVIDERS),
                "allAdaptersReportListMetadataCreateOk": all(
                    bool((payload.get(provider) or {}).get("list_ok"))
                    and bool((payload.get(provider) or {}).get("metadata_ok"))
                    and bool((payload.get(provider) or {}).get("create_ok"))
                    for provider in PROVIDERS
                ),
                "markdownShowsAllAdaptersOk": all(
                    f"## {provider}" in markdown
                    and "- list_ok: `True`" in markdown.split(f"## {provider}", 1)[1].split("\n## ", 1)[0]
                    and "- metadata_ok: `True`" in markdown.split(f"## {provider}", 1)[1].split("\n## ", 1)[0]
                    and "- create_ok: `True`" in markdown.split(f"## {provider}", 1)[1].split("\n## ", 1)[0]
                    for provider in PROVIDERS
                ),
                "allProbeChecksAreThree": all(int(probe_checks.get(provider, 0) or 0) == 3 for provider in PROVIDERS),
                "markdownShowsProbeChecks": all(f"- {provider}: `3`" in markdown for provider in PROVIDERS),
                "allMatrixRowsLiveProbeOk": all(
                    bool((matrix_rows.get(provider) or {}).get("list_ready"))
                    and bool((matrix_rows.get(provider) or {}).get("metadata_ready"))
                    and bool((matrix_rows.get(provider) or {}).get("create_dir_ready"))
                    and bool((matrix_rows.get(provider) or {}).get("live_probe_ok"))
                    for provider in PROVIDERS
                ),
                "markdownShowsMatrixRowsLiveProbeOk": all(
                    f"- {provider}: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`"
                    in markdown
                    for provider in PROVIDERS
                ),
                "cloud189KeepsAccountCreateMode": "- create_mode: `live_account_auth`" in markdown
                and "- create_file_id: `dir-189-1`" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
