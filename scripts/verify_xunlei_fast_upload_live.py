from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import xunlei_fast_upload_live


def main() -> None:
    original_load_profile = xunlei_fast_upload_live._load_profile_requirements
    original_request_json = xunlei_fast_upload_live._request_json
    original_verify_uploaded_file = xunlei_fast_upload_live._verify_uploaded_file

    request_calls: list[tuple[str, dict[str, object]]] = []

    file_path = ROOT / "tmp" / "verify-xunlei-fast-upload.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-xunlei-fast-upload")

    def fake_load_profile(profile_id: str):
        if profile_id != "xunlei-fast-1":
            return None, {}
        profile = type(
            "Profile",
            (),
            {
                "profileId": "xunlei-fast-1",
                "providerKey": "xunlei",
                "extra": {},
            },
        )()
        return profile, {"authorization": "Bearer demo", "x-device-id": "device-1", "x-client-id": "client-1"}

    def fake_request_json(url: str, body: dict[str, object], auth_headers: dict[str, str]):
        request_calls.append((url, dict(body)))
        return 200, {
            "upload_type": "UPLOAD_TYPE_UNKNOWN",
            "file": {"id": "xl-file-1", "name": "movie.mkv", "hash": body.get("hash", "")},
        }

    def fake_verify_uploaded_file(*, profile_id: str, parent_id: str, target_name: str, file_id: str, expected_gcid: str):
        return True, "metadata_by_file_id", "verified by xunlei metadata", {"fileId": file_id, "gcid": expected_gcid}

    xunlei_fast_upload_live._load_profile_requirements = fake_load_profile
    xunlei_fast_upload_live._request_json = fake_request_json
    xunlei_fast_upload_live._verify_uploaded_file = fake_verify_uploaded_file

    try:
        result = xunlei_fast_upload_live.upload_xunlei_fast_file(
            profile_id="xunlei-fast-1",
            local_path=str(file_path),
            target_name="movie.mkv",
            parent_id="root-xunlei",
        )
    finally:
        xunlei_fast_upload_live._load_profile_requirements = original_load_profile
        xunlei_fast_upload_live._request_json = original_request_json
        xunlei_fast_upload_live._verify_uploaded_file = original_verify_uploaded_file
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
                "createCalled": bool(request_calls),
                "uploadType": ((payload.get("payload") or {}).get("uploadType")),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
