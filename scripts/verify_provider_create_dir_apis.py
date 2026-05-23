from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import webapp
from fastapi.testclient import TestClient


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
    original_password = webapp.ADMIN_PASSWORD
    webapp.ADMIN_PASSWORD = "admin123"
    try:
        app = webapp.create_app()
        client = TestClient(app)
        client.post("/api/login", json={"password": "admin123"})

        with patched_attr(
            webapp,
            "fetch_quark_create_folder",
            lambda profile_id, parent_id="0", dir_name="": SimpleNamespace(
                ok=True,
                profileId=profile_id,
                status=200,
                note="quark mkdir ok",
                payload={"parentId": parent_id, "item": {"fileId": "quark-dir-1", "name": dir_name}},
                error="",
            ),
        ):
            quark = client.post(
                "/api/providers/quark/create_dir",
                json={"profileId": "quark-profile", "parentId": "0", "dirName": "demo-dir"},
            ).json()

        with patched_attr(
            webapp,
            "fetch_uc_create_folder",
            lambda profile_id, parent_id="0", dir_name="": SimpleNamespace(
                ok=True,
                profileId=profile_id,
                status=200,
                note="uc mkdir ok",
                payload={"parentId": parent_id, "item": {"fileId": "uc-dir-1", "name": dir_name}},
                error="",
            ),
        ):
            uc = client.post(
                "/api/providers/uc/create_dir",
                json={"profileId": "uc-profile", "parentId": "0", "dirName": "demo-dir"},
            ).json()
    finally:
        webapp.ADMIN_PASSWORD = original_password

    print(
        json.dumps(
            {
                "quark": {
                    "mode": quark.get("mode"),
                    "fileId": ((quark.get("item") or {}).get("fileId")),
                    "parentId": quark.get("parentId"),
                },
                "uc": {
                    "mode": uc.get("mode"),
                    "fileId": ((uc.get("item") or {}).get("fileId")),
                    "parentId": uc.get("parentId"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
