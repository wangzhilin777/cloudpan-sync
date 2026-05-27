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
            "fetch_tianyi_create_folder",
            lambda profile_id, parent_id="", dir_name="": SimpleNamespace(
                ok=False,
                mode="unsupported_readonly_share_auth",
                profileId=profile_id,
                status=0,
                note="189Cloud create folder is not available on the current shareCode/accessCode read-only probe path; official createFolder.action requires account-level OAuth headers.",
                payload={"requiredAuth": ["AccessToken", "Signature", "Date"]},
                error="share_auth_readonly",
            ),
        ):
            readonly_result = client.post(
                "/api/providers/189cloud/create_dir",
                json={"profileId": "189-profile", "parentId": "root-file", "dirName": "demo-dir"},
            ).json()

        with patched_attr(
            webapp,
            "fetch_tianyi_create_folder",
            lambda profile_id, parent_id="", dir_name="": SimpleNamespace(
                ok=True,
                mode="live_account_auth",
                profileId=profile_id,
                status=200,
                note="189Cloud live create folder succeeded with account-level OAuth headers.",
                payload={"parentId": parent_id, "item": {"fileId": "189-dir-1", "name": dir_name}},
                error="",
            ),
        ):
            account_result = client.post(
                "/api/providers/189cloud/create_dir",
                json={"profileId": "189-write-profile", "parentId": "root-file", "dirName": "demo-dir"},
            ).json()
    finally:
        webapp.ADMIN_PASSWORD = original_password

    print(
        json.dumps(
            {
                "readonly": {
                    "mode": readonly_result.get("mode"),
                    "fallbackReason": readonly_result.get("fallbackReason"),
                    "requiredAuth": readonly_result.get("requiredAuth"),
                },
                "readonlyCreateDirFallbackMatchesExpectedAuthHints": readonly_result.get("mode")
                == "unsupported_readonly_share_auth"
                and readonly_result.get("fallbackReason") == "share_auth_readonly"
                and readonly_result.get("requiredAuth") == ["AccessToken", "Signature", "Date"],
                "accountAuth": {
                    "mode": account_result.get("mode"),
                    "fileId": ((account_result.get("item") or {}).get("fileId")),
                    "parentId": account_result.get("parentId"),
                },
                "accountCreateDirReturnsLiveFolderResult": account_result.get("mode") == "live"
                and ((account_result.get("item") or {}).get("fileId")) == "189-dir-1"
                and account_result.get("parentId") == "root-file",
                "tianyiCreateDirApiFlowMatchesExpectedModes": (
                    readonly_result.get("mode") == "unsupported_readonly_share_auth"
                    and readonly_result.get("fallbackReason") == "share_auth_readonly"
                    and readonly_result.get("requiredAuth") == ["AccessToken", "Signature", "Date"]
                    and account_result.get("mode") == "live"
                    and ((account_result.get("item") or {}).get("fileId")) == "189-dir-1"
                    and account_result.get("parentId") == "root-file"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
