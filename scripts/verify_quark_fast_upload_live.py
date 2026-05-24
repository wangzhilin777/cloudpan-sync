from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import quark_fast_upload_live


def main() -> None:
    original_get_profile = quark_fast_upload_live.get_profile
    original_request_json = quark_fast_upload_live._request_json

    request_calls: list[tuple[str, str, dict[str, object]]] = []

    file_path = ROOT / "tmp" / "verify-quark-fast-upload.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-quark-fast-upload")

    def fake_get_profile(profile_id: str):
        if profile_id != "quark-fast-1":
            return None
        return type(
            "Profile",
            (),
            {
                "profileId": "quark-fast-1",
                "providerKey": "quark",
                "cookie": "sid=demo",
                "extra": {},
            },
        )()

    def fake_request_json(url: str, method: str, headers: dict[str, str], body: dict[str, object] | None = None):
        request_calls.append((method, url, dict(body or {})))
        if "/file/upload/pre?" in url:
            return 200, {"code": 0, "data": {"task_id": "task-qf-1", "obj_key": "obj-qf-1", "fid": "fid-qf-1"}}
        if "/file/update/hash?" in url:
            return 200, {"code": 0, "data": {"finish": True, "fid": "fid-qf-1"}}
        if "/file/upload/finish?" in url:
            return 200, {"code": 0, "data": {"fid": "fid-qf-1", "file_name": "movie.mkv"}}
        raise AssertionError(f"unexpected_request: {url}")

    quark_fast_upload_live.get_profile = fake_get_profile
    quark_fast_upload_live._request_json = fake_request_json

    try:
        result = quark_fast_upload_live.upload_quark_fast_file(
            profile_id="quark-fast-1",
            local_path=str(file_path),
            target_name="movie.mkv",
            parent_id="0",
        )
    finally:
        quark_fast_upload_live.get_profile = original_get_profile
        quark_fast_upload_live._request_json = original_request_json
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
