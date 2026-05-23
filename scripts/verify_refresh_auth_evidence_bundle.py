from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import webapp
from cloudpan_sync.auth_profile_patch import configure_data_dir
from fastapi.testclient import TestClient


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "gy-refresh-bundle-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "gy-refresh-ok",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {"parentId": "dir-100", "fileId": "file-9"},
                        "status": "saved",
                        "lastError": "",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                    {
                        "profileId": "gy-refresh-bundle-2",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "gy-refresh-missing",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {},
                        "status": "saved",
                        "lastError": "",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        configure_data_dir(data_dir)

        original_refresh_bundle = webapp.refresh_auth_evidence_bundle
        original_password = webapp.ADMIN_PASSWORD

        def fake_refresh_auth_evidence_bundle(*, profiles: list[object], profile_view_builder, page_size: int = 100, dir_name: str = "", persist: bool = True):
            items = []
            for profile in profiles:
                view = profile_view_builder(profile)
                is_ready = bool(view.get("resolvedParentId"))
                items.append(
                    {
                        "profile": view,
                        "latestValidation": {"ok": is_ready, "summary": "validation ok" if is_ready else "validation missing"},
                        "latestProbe": {"ok": is_ready, "summary": "probe ok" if is_ready else "probe missing"},
                        "summary": {
                            "profileReady": bool(view.get("profileReady")),
                            "validationOk": is_ready,
                            "probeOk": is_ready,
                            "resolvedParentId": str(view.get("resolvedParentId") or ""),
                            "resolvedFileId": str(view.get("resolvedFileId") or ""),
                        },
                    }
                )
            return {
                "summary": {
                    "profileCount": len(items),
                    "profileReadyCount": sum(1 for item in items if bool((item.get("summary") or {}).get("profileReady"))),
                    "validationOkCount": sum(1 for item in items if bool((item.get("summary") or {}).get("validationOk"))),
                    "probeOkCount": sum(1 for item in items if bool((item.get("summary") or {}).get("probeOk"))),
                },
                "items": items,
            }

        webapp.refresh_auth_evidence_bundle = fake_refresh_auth_evidence_bundle
        webapp.ADMIN_PASSWORD = "admin123"
        try:
            app = webapp.create_app()
            client = TestClient(app)
            client.post("/api/login", json={"password": "admin123"})
            payload = client.post("/api/auth/refresh_evidence_bundle", json={"pageSize": 33, "dirName": "verify-dir"}).json()
        finally:
            webapp.refresh_auth_evidence_bundle = original_refresh_bundle
            webapp.ADMIN_PASSWORD = original_password

        print(
            json.dumps(
                {
                    "profileCount": ((payload.get("bundle") or {}).get("summary") or {}).get("profileCount"),
                    "validationOkCount": ((payload.get("bundle") or {}).get("summary") or {}).get("validationOkCount"),
                    "probeOkCount": ((payload.get("bundle") or {}).get("summary") or {}).get("probeOkCount"),
                    "markdownHasTitle": "# Auth Evidence Bundle" in str(payload.get("markdown", "")),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
