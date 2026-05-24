from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import uc_fast_upload_live


def main() -> None:
    original_get_profile = uc_fast_upload_live.get_profile
    original_request_json = uc_fast_upload_live._request_json

    request_calls: list[tuple[str, str, dict[str, object]]] = []

    file_path = ROOT / "tmp" / "verify-uc-fast-upload.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-uc-fast-upload")

    def fake_get_profile(profile_id: str):
        if profile_id != "uc-fast-1":
            return None
        return type(
            "Profile",
            (),
            {
                "profileId": "uc-fast-1",
                "providerKey": "uc",
                "cookie": "sid=demo",
                "extra": {},
            },
        )()

    def fake_request_json(url: str, method: str, headers: dict[str, str], body: dict[str, object] | None = None):
        request_calls.append((method, url, dict(body or {})))
        if "/file/upload/pre?" in url:
            return 200, {"code": 0, "data": {"task_id": "task-uf-1", "obj_key": "obj-uf-1", "fid": "fid-uf-1"}}
        if "/file/update/hash?" in url:
            return 200, {"code": 0, "data": {"finish": True, "fid": "fid-uf-1"}}
        if "/file/upload/finish?" in url:
            return 200, {"code": 0, "data": {"fid": "fid-uf-1", "file_name": "movie.mkv"}}
        raise AssertionError(f"unexpected_request: {url}")

    uc_fast_upload_live.get_profile = fake_get_profile
    uc_fast_upload_live._request_json = fake_request_json

    try:
        result = uc_fast_upload_live.upload_uc_fast_file(
            profile_id="uc-fast-1",
            local_path=str(file_path),
            target_name="movie.mkv",
            parent_id="0",
        )
    finally:
        uc_fast_upload_live.get_profile = original_get_profile
        uc_fast_upload_live._request_json = original_request_json
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()

    payload = result.to_dict()
    print(
        json.dumps(
            {
                "ok": payload.get("ok"),
                "mode": payload.get("mode"),
                "verifyOk": payload.get("verifyOk"),
                "verifyMode": payload.get("verifyMode"),
                "resolvedTargetName": ((payload.get("payload") or {}).get("resolvedTargetName")),
                "preCalled": any("/file/upload/pre?" in url for _, url, _ in request_calls),
                "hashCalled": any("/file/update/hash?" in url for _, url, _ in request_calls),
                "finishCalled": any("/file/upload/finish?" in url for _, url, _ in request_calls),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
