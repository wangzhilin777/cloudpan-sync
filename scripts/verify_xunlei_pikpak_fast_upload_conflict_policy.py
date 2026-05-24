from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import pikpak_fast_upload_live, xunlei_fast_upload_live


def _run_pikpak_case() -> dict[str, object]:
    original_load_profile = pikpak_fast_upload_live._load_profile_requirements
    original_post_json = pikpak_fast_upload_live._post_json
    original_verify_uploaded_file = pikpak_fast_upload_live._verify_uploaded_file
    original_upload_resumable = pikpak_fast_upload_live._upload_resumable_binary
    original_fetch_list = pikpak_fast_upload_live.fetch_pikpak_live_list

    file_path = ROOT / "tmp" / "verify-pikpak-conflict.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"pikpak-conflict")

    request_calls: list[dict[str, object]] = []

    def fake_load_profile(profile_id: str):
        profile = type("Profile", (), {"profileId": profile_id, "providerKey": "pikpak", "extra": {}})()
        return profile, {"authorization": "Bearer demo", "x-device-id": "device-1"}

    def fake_fetch_list(profile_id: str, parent_id: str = "", limit: int = 100, page_token: str = ""):
        return type(
            "ListResult",
            (),
            {
                "ok": True,
                "payload": {"items": [{"name": "demo.bin"}]},
                "status": 200,
                "error": "",
            },
        )()

    def fake_post_json(path: str, body: dict[str, object], auth_headers: dict[str, str]):
        request_calls.append(dict(body))
        return 200, {
            "upload_type": "UPLOAD_TYPE_RESUMABLE",
            "file": {"id": "pk-file-1", "name": body.get("name")},
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
        return "", "", {"bucket": "bucket-pk", "key": "folder/demo.bin", "provider": "S3"}

    def fake_verify_uploaded_file(*, profile_id: str, parent_id: str, target_name: str, file_id: str, expected_gcid: str):
        return True, "metadata_by_file_id", "verified", {"fileId": file_id}

    pikpak_fast_upload_live._load_profile_requirements = fake_load_profile
    pikpak_fast_upload_live.fetch_pikpak_live_list = fake_fetch_list
    pikpak_fast_upload_live._post_json = fake_post_json
    pikpak_fast_upload_live._verify_uploaded_file = fake_verify_uploaded_file
    pikpak_fast_upload_live._upload_resumable_binary = fake_upload_resumable
    try:
        result = pikpak_fast_upload_live.upload_pikpak_fast_file(
            profile_id="pikpak-profile-1",
            local_path=str(file_path),
            target_name="demo.bin",
            parent_id="root-pikpak",
            conflict_policy="overwrite_existing",
        )
        payload = result.to_dict()
        return {
            "ok": payload.get("ok"),
            "mode": payload.get("mode"),
            "requestedName": (request_calls[0] if request_calls else {}).get("name"),
            "resolvedTargetName": ((payload.get("payload") or {}).get("resolvedTargetName")),
            "conflictAction": ((payload.get("payload") or {}).get("conflictAction")),
            "noteHasDowngrade": "downgraded" in str(payload.get("note") or ""),
        }
    finally:
        pikpak_fast_upload_live._load_profile_requirements = original_load_profile
        pikpak_fast_upload_live.fetch_pikpak_live_list = original_fetch_list
        pikpak_fast_upload_live._post_json = original_post_json
        pikpak_fast_upload_live._verify_uploaded_file = original_verify_uploaded_file
        pikpak_fast_upload_live._upload_resumable_binary = original_upload_resumable
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()


def _run_xunlei_case() -> dict[str, object]:
    original_load_profile = xunlei_fast_upload_live._load_profile_requirements
    original_request_json = xunlei_fast_upload_live._request_json
    original_verify_uploaded_file = xunlei_fast_upload_live._verify_uploaded_file
    original_upload_resumable = xunlei_fast_upload_live._upload_resumable_binary
    original_fetch_list = xunlei_fast_upload_live.fetch_xunlei_live_list

    file_path = ROOT / "tmp" / "verify-xunlei-conflict.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"xunlei-conflict")

    request_calls: list[dict[str, object]] = []

    def fake_load_profile(profile_id: str):
        profile = type("Profile", (), {"profileId": profile_id, "providerKey": "xunlei", "extra": {}})()
        return profile, {"authorization": "Bearer demo", "x-device-id": "device-1", "x-client-id": "client-1"}

    def fake_fetch_list(profile_id: str, parent_id: str = "", limit: int = 100, page_token: str = ""):
        return type(
            "ListResult",
            (),
            {
                "ok": True,
                "payload": {"items": [{"name": "demo.bin"}]},
                "status": 200,
                "error": "",
            },
        )()

    def fake_request_json(url: str, body: dict[str, object], auth_headers: dict[str, str]):
        request_calls.append(dict(body))
        return 200, {
            "upload_type": "UPLOAD_TYPE_RESUMABLE",
            "file": {"id": "xl-file-1", "name": body.get("name")},
            "resumable": {
                "provider": "S3",
                "params": {
                    "access_key_id": "ak",
                    "access_key_secret": "sk",
                    "security_token": "token",
                    "bucket": "bucket-xl",
                    "endpoint": "bucket-xl.example.invalid",
                    "key": "folder/demo.bin",
                },
            },
        }

    def fake_upload_resumable(file_path_arg: Path, resumable: dict[str, object]):
        return "", "", {"bucket": "bucket-xl", "key": "folder/demo.bin", "provider": "S3"}

    def fake_verify_uploaded_file(*, profile_id: str, parent_id: str, target_name: str, file_id: str, expected_gcid: str):
        return True, "metadata_by_file_id", "verified", {"fileId": file_id}

    xunlei_fast_upload_live._load_profile_requirements = fake_load_profile
    xunlei_fast_upload_live.fetch_xunlei_live_list = fake_fetch_list
    xunlei_fast_upload_live._request_json = fake_request_json
    xunlei_fast_upload_live._verify_uploaded_file = fake_verify_uploaded_file
    xunlei_fast_upload_live._upload_resumable_binary = fake_upload_resumable
    try:
        result = xunlei_fast_upload_live.upload_xunlei_fast_file(
            profile_id="xunlei-profile-1",
            local_path=str(file_path),
            target_name="demo.bin",
            parent_id="root-xunlei",
            conflict_policy="overwrite_existing",
        )
        payload = result.to_dict()
        return {
            "ok": payload.get("ok"),
            "mode": payload.get("mode"),
            "requestedName": (request_calls[0] if request_calls else {}).get("name"),
            "resolvedTargetName": ((payload.get("payload") or {}).get("resolvedTargetName")),
            "conflictAction": ((payload.get("payload") or {}).get("conflictAction")),
            "noteHasDowngrade": "downgraded" in str(payload.get("note") or ""),
        }
    finally:
        xunlei_fast_upload_live._load_profile_requirements = original_load_profile
        xunlei_fast_upload_live.fetch_xunlei_live_list = original_fetch_list
        xunlei_fast_upload_live._request_json = original_request_json
        xunlei_fast_upload_live._verify_uploaded_file = original_verify_uploaded_file
        xunlei_fast_upload_live._upload_resumable_binary = original_upload_resumable
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()


def main() -> None:
    print(
        json.dumps(
            {
                "pikpak": _run_pikpak_case(),
                "xunlei": _run_xunlei_case(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
