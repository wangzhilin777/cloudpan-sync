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
    original_verify_uploaded_file = pan115_fast_upload_live._verify_uploaded_file

    request_calls: list[dict[str, object]] = []

    file_path = ROOT / "tmp" / "verify-115-fast-upload.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-115-fast-upload")

    def fake_load_profile(profile_id: str):
        if profile_id != "115-fast-1":
            return None, "", ""
        profile = type(
            "Profile",
            (),
            {
                "profileId": "115-fast-1",
                "providerKey": "115_open",
                "extra": {},
            },
        )()
        return profile, "demo-access-token", "UID=demo;"

    def fake_post_form(url: str, form: dict[str, object], access_token: str, cookie: str):
        request_calls.append(
            {
                "url": url,
                "form": dict(form),
                "hasAccessToken": bool(access_token),
                "hasCookie": bool(cookie),
            }
        )
        if len(request_calls) == 1:
            return 200, {
                "state": True,
                "data": {
                    "status": 7,
                    "sign_key": "range-check",
                    "sign_check": "0-5",
                    "file_id": "",
                    "pick_code": "",
                },
            }
        return 200, {
            "state": True,
            "data": {
                "status": 2,
                "file_id": "115-file-1",
                "pick_code": "pc115",
            },
        }

    def fake_verify_uploaded_file(*, profile_id: str, parent_id: str, target_name: str, file_id: str, expected_sha1: str):
        return True, "metadata_by_file_id", "verified by 115 metadata", {"fileId": file_id, "sha1": expected_sha1}

    pan115_fast_upload_live._load_profile_requirements = fake_load_profile
    pan115_fast_upload_live._post_form = fake_post_form
    pan115_fast_upload_live._verify_uploaded_file = fake_verify_uploaded_file

    try:
        result = pan115_fast_upload_live.upload_115_open_fast_file(
            profile_id="115-fast-1",
            local_path=str(file_path),
            target_name="movie.mkv",
            parent_id="115-root",
        )
    finally:
        pan115_fast_upload_live._load_profile_requirements = original_load_profile
        pan115_fast_upload_live._post_form = original_post_form
        pan115_fast_upload_live._verify_uploaded_file = original_verify_uploaded_file
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()

    payload = result.to_dict()
    second_attempt = ((payload.get("payload") or {}).get("secondAttempt") or {})
    print(
        json.dumps(
            {
                "ok": payload.get("ok"),
                "mode": payload.get("mode"),
                "verifyOk": payload.get("verifyOk"),
                "verifyMode": payload.get("verifyMode"),
                "requestCount": len(request_calls),
                "firstStatus": (((payload.get("payload") or {}).get("initResponse") or {}).get("data") or {}).get("status"),
                "secondStatus": (((payload.get("payload") or {}).get("followupResponse") or {}).get("data") or {}).get("status"),
                "signCheckUsed": second_attempt.get("signCheck"),
                "resolvedTargetName": ((payload.get("payload") or {}).get("resolvedTargetName")),
                "target": ((payload.get("payload") or {}).get("target")),
                "pan115FastUploadLiveFlowMatchesExpectedRapidUpload": (
                    payload.get("ok") is True
                    and payload.get("mode") == "rapid_upload_by_hash"
                    and payload.get("verifyOk") is True
                    and payload.get("verifyMode") == "metadata_by_file_id"
                    and len(request_calls) == 2
                    and (((payload.get("payload") or {}).get("initResponse") or {}).get("data") or {}).get("status") == 7
                    and (((payload.get("payload") or {}).get("followupResponse") or {}).get("data") or {}).get("status") == 2
                    and second_attempt.get("signCheck") == "0-5"
                    and ((payload.get("payload") or {}).get("resolvedTargetName")) == "movie.mkv"
                    and ((payload.get("payload") or {}).get("target")) == "U_1_115-root"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
