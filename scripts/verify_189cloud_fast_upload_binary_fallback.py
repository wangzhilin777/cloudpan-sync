from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import tianyi_fast_upload_live


def main() -> None:
    original_load_profile = tianyi_fast_upload_live._load_profile_requirements
    original_get_session = tianyi_fast_upload_live._get_user_session
    original_request_signed_json = tianyi_fast_upload_live._request_signed_json
    original_request_signed_json_get = tianyi_fast_upload_live._request_signed_json_get
    original_request_signed_xml = tianyi_fast_upload_live._request_signed_xml
    original_binary_upload = tianyi_fast_upload_live._upload_binary_to_file_upload_url

    json_calls: list[dict[str, object]] = []
    get_calls: list[dict[str, object]] = []
    xml_calls: list[dict[str, object]] = []
    put_calls: list[dict[str, object]] = []

    file_path = ROOT / "tmp" / "verify-189cloud-fast-upload-fallback.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-189-fast-upload-fallback")
    file_md5 = hashlib.md5(file_path.read_bytes()).hexdigest()

    def fake_load_profile(profile_id: str):
        if profile_id != "189-fast-2":
            return None, "", "", ""
        profile = type(
            "Profile",
            (),
            {
                "profileId": "189-fast-2",
                "providerKey": "189cloud",
                "extra": {},
            },
        )()
        return profile, "demo-access-token", "sig-demo", "Sat, 24 May 2026 00:00:00 GMT"

    def fake_get_user_session(access_token: str):
        return 200, {
            "sessionKey": "session-key-demo",
            "sessionSecret": "0123456789abcdef0123456789abcdef",
        }

    def fake_request_signed_json(url: str, *, form: dict[str, object], session_key: str, session_secret: str):
        json_calls.append({"url": url, "form": dict(form)})
        return 200, {
            "uploadFileId": 1002,
            "fileUploadUrl": "https://upload.cloud.189.cn/upload-demo",
            "fileCommitUrl": "https://api.cloud.189.cn/commit-demo.action",
            "fileDataExists": 0,
        }

    def fake_request_signed_json_get(url: str, *, query: dict[str, str], session_key: str, session_secret: str):
        get_calls.append({"url": url, "query": dict(query)})
        return 200, {
            "uploadFileId": 1002,
            "fileUploadUrl": "https://upload.cloud.189.cn/upload-demo",
            "fileCommitUrl": "https://api.cloud.189.cn/commit-demo.action",
            "fileDataExists": 0,
            "dataSize": 0,
            "size": file_path.stat().st_size,
        }

    def fake_request_signed_xml(url: str, *, form: dict[str, object], session_key: str, session_secret: str):
        xml_calls.append({"url": url, "form": dict(form)})
        return 200, (
            "<file><id>189-file-fallback-1</id><name>movie.mkv</name><size>"
            f"{file_path.stat().st_size}</size><md5>{file_md5}</md5>"
            "<createDate>2026-05-25 12:00:00</createDate></file>"
        )

    def fake_binary_upload(upload_path: Path, file_upload_url: str, upload_file_id: int):
        put_calls.append(
            {
                "path": str(upload_path),
                "fileUploadUrl": file_upload_url,
                "uploadFileId": upload_file_id,
                "size": upload_path.stat().st_size,
            }
        )
        return 200, {"status": 200}

    tianyi_fast_upload_live._load_profile_requirements = fake_load_profile
    tianyi_fast_upload_live._get_user_session = fake_get_user_session
    tianyi_fast_upload_live._request_signed_json = fake_request_signed_json
    tianyi_fast_upload_live._request_signed_json_get = fake_request_signed_json_get
    tianyi_fast_upload_live._request_signed_xml = fake_request_signed_xml
    tianyi_fast_upload_live._upload_binary_to_file_upload_url = fake_binary_upload

    try:
        result = tianyi_fast_upload_live.upload_tianyi_fast_file(
            profile_id="189-fast-2",
            local_path=str(file_path),
            target_name="movie.mkv",
            parent_id="189-root",
        )
    finally:
        tianyi_fast_upload_live._load_profile_requirements = original_load_profile
        tianyi_fast_upload_live._get_user_session = original_get_session
        tianyi_fast_upload_live._request_signed_json = original_request_signed_json
        tianyi_fast_upload_live._request_signed_json_get = original_request_signed_json_get
        tianyi_fast_upload_live._request_signed_xml = original_request_signed_xml
        tianyi_fast_upload_live._upload_binary_to_file_upload_url = original_binary_upload
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()

    payload = result.to_dict()
    verify_payload = payload.get("verifyPayload") or {}
    print(
        json.dumps(
            {
                "ok": payload.get("ok"),
                "mode": payload.get("mode"),
                "verifyOk": payload.get("verifyOk"),
                "verifyMode": payload.get("verifyMode"),
                "createCalled": len(json_calls) == 1,
                "putCalled": len(put_calls) == 1,
                "statusCalled": len(get_calls) == 1,
                "commitCalled": len(xml_calls) == 1,
                "statusUploadedBytes": ((verify_payload.get("statusView") or {}).get("uploadedBytes")),
                "commitFileId": verify_payload.get("fileId"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
