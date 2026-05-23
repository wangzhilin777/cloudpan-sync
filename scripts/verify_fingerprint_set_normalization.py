from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import webapp


def main() -> None:
    original_password = webapp.ADMIN_PASSWORD
    webapp.ADMIN_PASSWORD = "admin123"
    try:
        app = webapp.create_app()
        client = TestClient(app)
        client.post("/api/login", json={"password": "admin123"})
        payload = {
            "sourceProvider": "quark",
            "targetProvider": "115_open",
            "thresholdMB": 200,
            "conflictPolicy": "auto_rename_new",
            "selectedRoots": ["/demo.bin"],
            "entries": [
                {
                    "path": "/demo.bin",
                    "size": 4,
                    "sha1": " AA-BB-CC ",
                    "raw": {
                        "md5": " \"ABCDEF0123456789ABCDEF0123456789\" ",
                        "etag": " \"ET-Tag-1\" ",
                        "pickCode": " pc-1 ",
                        "block_list_md5": " 0011 , 2233 ; 0011 ",
                    },
                }
            ],
        }
        plan = client.post("/api/plan/mock", json=payload).json()
    finally:
        webapp.ADMIN_PASSWORD = original_password

    row = ((plan.get("items") or [{}])[0])
    fingerprints = row.get("normalizedFingerprints") or {}
    print(
        json.dumps(
            {
                "strategy": row.get("strategy"),
                "availableFastInputs": row.get("availableFastInputs"),
                "missingFastInputs": row.get("missingFastInputs"),
                "normalizedFingerprints": {
                    "md5": fingerprints.get("md5"),
                    "sha1": fingerprints.get("sha1"),
                    "etag": fingerprints.get("etag"),
                    "pickcode": fingerprints.get("pickcode"),
                    "blockListMd5": fingerprints.get("blockListMd5"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
