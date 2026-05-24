from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import pikpak_fast_upload_live


def main() -> None:
    original_load_profile = pikpak_fast_upload_live._load_profile_requirements
    original_post_json = pikpak_fast_upload_live._post_json
    original_verify_uploaded_file = pikpak_fast_upload_live._verify_uploaded_file

    request_calls: list[tuple[str, dict[str, object]]] = []

    file_path = ROOT / "tmp" / "verify-pikpak-fast-upload.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-pikpak-fast-upload")

    def fake_load_profile(profile_id: str):
        if profile_id != "pikpak-fast-1":
            return None, {}
        profile = type(
            "Profile",
            (),
            {
                "profileId": "pikpak-fast-1",
                "providerKey": "pikpak",
                "extra": {},
            },
        )()
        return profile, {"authorization": "Bearer demo", "x-device-id": "device-1"}

    def fake_post_json(path: str, body: dict[str, object], auth_headers: dict[str, str]):
        request_calls.append((path, dict(body)))
        return 200, {
            "upload_type": "UPLOAD_TYPE_UNKNOWN",
            "file": {"id": "pk-file-1", "name": "movie.mkv", "hash": body.get("hash", "")},
        }

    def fake_verify_uploaded_file(*, profile_id: str, parent_id: str, target_name: str, file_id: str, expected_gcid: str):
        return True, "metadata_by_file_id", "verified by pikpak metadata", {"fileId": file_id, "gcid": expected_gcid}

    pikpak_fast_upload_live._load_profile_requirements = fake_load_profile
    pikpak_fast_upload_live._post_json = fake_post_json
    pikpak_fast_upload_live._verify_uploaded_file = fake_verify_uploaded_file

    try:
        result = pikpak_fast_upload_live.upload_pikpak_fast_file(
            profile_id="pikpak-fast-1",
            local_path=str(file_path),
            target_name="movie.mkv",
            parent_id="root-pikpak",
        )
    finally:
        pikpak_fast_upload_live._load_profile_requirements = original_load_profile
        pikpak_fast_upload_live._post_json = original_post_json
        pikpak_fast_upload_live._verify_uploaded_file = original_verify_uploaded_file
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
