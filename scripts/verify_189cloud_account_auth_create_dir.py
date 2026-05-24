from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import tianyi_live


class patched_attr:
    def __init__(self, obj: object, name: str, value: object):
        self.obj = obj
        self.name = name
        self.value = value
        self.original = getattr(obj, name)

    def __enter__(self):
        setattr(self.obj, self.name, self.value)
        return self

    def __exit__(self, exc_type, exc, tb):
        setattr(self.obj, self.name, self.original)
        return False


def main() -> None:
    captured: dict[str, object] = {}
    profile = SimpleNamespace(
        profileId="189-write-test",
        token="access-token-demo",
        extra={
            "signature": "sig-demo",
            "date": "Sat, 24 May 2026 00:00:00 GMT",
            "fileId": "root-file",
        },
    )

    def fake_request_json(url: str, method: str = "GET", headers: dict[str, str] | None = None, body: str = ""):
        captured["url"] = url
        captured["method"] = method
        captured["headers"] = dict(headers or {})
        captured["body"] = body
        return 200, {"res_code": 0, "id": "189-dir-1", "name": "demo-dir"}

    with patched_attr(tianyi_live, "get_profile", lambda profile_id: profile):
        with patched_attr(tianyi_live, "_request_json", fake_request_json):
            result = tianyi_live.fetch_tianyi_create_folder("189-write-test", parent_id="root-file", dir_name="demo-dir")

    print(
        json.dumps(
            {
                "ok": result.ok,
                "mode": result.mode,
                "fileId": ((result.payload or {}).get("item") or {}).get("fileId", ""),
                "request": {
                    "url": captured.get("url"),
                    "method": captured.get("method"),
                    "hasAccessToken": bool((captured.get("headers") or {}).get("AccessToken")),
                    "hasAccesstoken": bool((captured.get("headers") or {}).get("Accesstoken")),
                    "hasSignature": bool((captured.get("headers") or {}).get("Signature")),
                    "hasDate": bool((captured.get("headers") or {}).get("Date")),
                    "body": captured.get("body"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
