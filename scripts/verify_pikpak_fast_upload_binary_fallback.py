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
    original_upload_resumable = pikpak_fast_upload_live._upload_resumable_binary

    request_calls: list[tuple[str, dict[str, object]]] = []
    upload_calls: list[dict[str, object]] = []

    file_path = ROOT / "tmp" / "verify-pikpak-fast-upload-fallback.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-pikpak-fast-upload-fallback")

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
            "upload_type": "UPLOAD_TYPE_RESUMABLE",
            "file": {"id": "pk-file-2", "name": "demo.bin", "hash": body.get("hash", "")},
            "resumable": {
                "provider": "S3",
                "params": {
                    "access_key_id": "ak",
                    "access_key_secret": "sk",
                    "security_token": "token",
                    "bucket": "bucket-pk",
                    "endpoint": "bucket-pk.example.invalid",
                    "key": "folder/demo.bin",
                },
            },
        }

    def fake_upload_resumable(file_path_arg: Path, resumable: dict[str, object]):
        upload_calls.append(
            {
                "fileName": file_path_arg.name,
                "provider": ((resumable.get("provider") or "") if isinstance(resumable, dict) else ""),
                "bucket": (((resumable.get("params") or {}).get("bucket")) if isinstance(resumable, dict) else ""),
            }
        )
        return "", "", {"bucket": "bucket-pk", "key": "folder/demo.bin", "provider": "S3"}

    def fake_verify_uploaded_file(*, profile_id: str, parent_id: str, target_name: str, file_id: str, expected_gcid: str):
        return True, "metadata_by_file_id", "verified by pikpak metadata", {"fileId": file_id, "gcid": expected_gcid}

    pikpak_fast_upload_live._load_profile_requirements = fake_load_profile
    pikpak_fast_upload_live._post_json = fake_post_json
    pikpak_fast_upload_live._verify_uploaded_file = fake_verify_uploaded_file
    pikpak_fast_upload_live._upload_resumable_binary = fake_upload_resumable

    try:
        result = pikpak_fast_upload_live.upload_pikpak_fast_file(
            profile_id="pikpak-fast-1",
            local_path=str(file_path),
            target_name="demo.bin",
            parent_id="root-pikpak",
        )
    finally:
        pikpak_fast_upload_live._load_profile_requirements = original_load_profile
        pikpak_fast_upload_live._post_json = original_post_json
        pikpak_fast_upload_live._verify_uploaded_file = original_verify_uploaded_file
        pikpak_fast_upload_live._upload_resumable_binary = original_upload_resumable
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
                "createCalled": bool(request_calls),
                "resumableUploadCalled": bool(upload_calls),
                "usedBinaryFallback": bool((payload.get("verifyPayload") or {}).get("usedBinaryFallback")),
                "uploadBucket": ((payload.get("payload") or {}).get("resumableUpload") or {}).get("bucket"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
