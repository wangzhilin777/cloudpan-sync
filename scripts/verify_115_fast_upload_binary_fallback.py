from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import pan115_fast_upload_live


def main() -> None:
    original_load_profile = pan115_fast_upload_live._load_profile_requirements
    original_post_form = pan115_fast_upload_live._post_form
    original_request_upload_token = pan115_fast_upload_live._request_upload_token
    original_upload_binary = pan115_fast_upload_live._upload_binary_to_115_oss
    original_verify_uploaded_file = pan115_fast_upload_live._verify_uploaded_file

    request_calls: list[dict[str, object]] = []
    token_calls: list[dict[str, object]] = []
    upload_calls: list[dict[str, object]] = []

    file_path = ROOT / "tmp" / "verify-115-fast-upload-fallback.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-115-fast-upload-fallback")

    def fake_load_profile(profile_id: str):
        if profile_id != "115-fast-2":
            return None, "", ""
        profile = type(
            "Profile",
            (),
            {
                "profileId": "115-fast-2",
                "providerKey": "115_open",
                "extra": {},
            },
        )()
        return profile, "demo-access-token", "UID=demo;"

    def fake_post_form(url: str, form: dict[str, object], access_token: str, cookie: str):
        request_calls.append({"url": url, "form": dict(form)})
        if len(request_calls) == 1:
            return 200, {
                "state": True,
                "data": {
                    "status": 7,
                    "sign_key": "range-check",
                    "sign_check": "0-5",
                    "bucket": "115-bucket-demo",
                    "object": "folder/movie.mkv",
                    "callback": {
                        "callback": "callback-body-demo",
                        "callback_var": '{"x:sha1":"demo"}',
                    },
                },
            }
        return 200, {
            "state": True,
            "data": {
                "status": 1,
                "bucket": "115-bucket-demo",
                "object": "folder/movie.mkv",
                "callback": {
                    "callback": "callback-body-demo",
                    "callback_var": '{"x:sha1":"demo"}',
                },
            },
        }

    def fake_request_upload_token(access_token: str, cookie: str):
        token_calls.append({"accessToken": access_token, "cookie": cookie})
        return 200, {
            "state": True,
            "data": {
                "endpoint": "oss-cn-hangzhou.aliyuncs.com",
                "access_key_id": "ak-demo",
                "access_key_secret": "sk-demo",
                "security_token": "sts-demo",
            },
        }

    def fake_upload_binary(file_path_arg: Path, session: dict[str, object]):
        upload_calls.append(
            {
                "path": str(file_path_arg),
                "session": dict(session),
                "size": file_path_arg.stat().st_size,
            }
        )
        return "", "", {"uploadKind": "single_part", "bucket": session.get("bucket"), "object": session.get("object"), "status": 200}

    def fake_verify_uploaded_file(*, profile_id: str, parent_id: str, target_name: str, file_id: str, expected_sha1: str):
        return True, "list_by_parent_name", "verified by 115 list", {"targetName": target_name, "sha1": expected_sha1}

    pan115_fast_upload_live._load_profile_requirements = fake_load_profile
    pan115_fast_upload_live._post_form = fake_post_form
    pan115_fast_upload_live._request_upload_token = fake_request_upload_token
    pan115_fast_upload_live._upload_binary_to_115_oss = fake_upload_binary
    pan115_fast_upload_live._verify_uploaded_file = fake_verify_uploaded_file

    try:
        result = pan115_fast_upload_live.upload_115_open_fast_file(
            profile_id="115-fast-2",
            local_path=str(file_path),
            target_name="movie.mkv",
            parent_id="115-root",
        )
    finally:
        pan115_fast_upload_live._load_profile_requirements = original_load_profile
        pan115_fast_upload_live._post_form = original_post_form
        pan115_fast_upload_live._request_upload_token = original_request_upload_token
        pan115_fast_upload_live._upload_binary_to_115_oss = original_upload_binary
        pan115_fast_upload_live._verify_uploaded_file = original_verify_uploaded_file
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()

    payload = result.to_dict()
    binary_payload = ((payload.get("payload") or {}).get("binaryUpload") or {})
    upload_session = ((payload.get("payload") or {}).get("uploadSession") or {})
    print(
        json.dumps(
            {
                "ok": payload.get("ok"),
                "mode": payload.get("mode"),
                "verifyOk": payload.get("verifyOk"),
                "verifyMode": payload.get("verifyMode"),
                "requestCount": len(request_calls),
                "tokenRequested": len(token_calls) == 1,
                "binaryUploadCalled": len(upload_calls) == 1,
                "uploadKind": binary_payload.get("uploadKind"),
                "bucket": upload_session.get("bucket"),
                "object": upload_session.get("object"),
                "endpoint": upload_session.get("endpoint"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
