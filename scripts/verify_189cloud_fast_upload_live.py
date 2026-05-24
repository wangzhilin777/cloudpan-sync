from __future__ import annotations

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
    original_request_signed_xml = tianyi_fast_upload_live._request_signed_xml

    json_calls: list[dict[str, object]] = []
    xml_calls: list[dict[str, object]] = []

    file_path = ROOT / "tmp" / "verify-189cloud-fast-upload.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-189-fast-upload")

    def fake_load_profile(profile_id: str):
        if profile_id != "189-fast-1":
            return None, "", "", ""
        profile = type(
            "Profile",
            (),
            {
                "profileId": "189-fast-1",
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
        json_calls.append({"url": url, "form": dict(form), "sessionKey": session_key, "sessionSecret": session_secret})
        return 200, {
            "uploadFileId": 1001,
            "fileCommitUrl": "https://api.cloud.189.cn/commit-demo.action",
            "fileDataExists": 1,
        }

    def fake_request_signed_xml(url: str, *, form: dict[str, object], session_key: str, session_secret: str):
        xml_calls.append({"url": url, "form": dict(form), "sessionKey": session_key, "sessionSecret": session_secret})
        return 200, "<file><id>189-file-1</id><name>movie.mkv</name><size>31</size><md5>0123456789abcdef0123456789abcdef</md5><createDate>2026-05-25 12:00:00</createDate></file>"

    tianyi_fast_upload_live._load_profile_requirements = fake_load_profile
    tianyi_fast_upload_live._get_user_session = fake_get_user_session
    tianyi_fast_upload_live._request_signed_json = fake_request_signed_json
    tianyi_fast_upload_live._request_signed_xml = fake_request_signed_xml

    try:
        result = tianyi_fast_upload_live.upload_tianyi_fast_file(
            profile_id="189-fast-1",
            local_path=str(file_path),
            target_name="movie.mkv",
            parent_id="189-root",
        )
    finally:
        tianyi_fast_upload_live._load_profile_requirements = original_load_profile
        tianyi_fast_upload_live._get_user_session = original_get_session
        tianyi_fast_upload_live._request_signed_json = original_request_signed_json
        tianyi_fast_upload_live._request_signed_xml = original_request_signed_xml
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()

    payload = result.to_dict()
    commit_payload = ((payload.get("payload") or {}).get("commitResponse") or {})
    print(
        json.dumps(
            {
                "ok": payload.get("ok"),
                "mode": payload.get("mode"),
                "verifyOk": payload.get("verifyOk"),
                "verifyMode": payload.get("verifyMode"),
                "createCalled": len(json_calls) == 1,
                "commitCalled": len(xml_calls) == 1,
                "fileDataExists": ((payload.get("payload") or {}).get("fileDataExists")),
                "commitFileId": commit_payload.get("fileId"),
                "resolvedTargetName": ((payload.get("payload") or {}).get("resolvedTargetName")),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
