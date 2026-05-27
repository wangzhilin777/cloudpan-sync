from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import pan123_open_upload_live
from cloudpan_sync.models import AuthProfile


def main() -> None:
    original_get_profile = pan123_open_upload_live.get_profile
    original_post_json = pan123_open_upload_live._post_json
    original_put_file = pan123_open_upload_live._put_file
    original_metadata = pan123_open_upload_live.fetch_123_open_live_metadata
    original_list = pan123_open_upload_live.fetch_123_open_live_list
    original_sleep = pan123_open_upload_live.sleep

    profile = AuthProfile(
        profileId="pan123-upload-1",
        providerKey="123_open",
        authMode="manual_token",
        displayName="123-upload",
        token="Bearer pan123-token",
        cookie="",
        extra={"parentFileId": "0"},
        status="verified",
        lastError="",
        createdAt="2026-05-25T00:00:00+00:00",
        updatedAt="2026-05-25T00:00:00+00:00",
    )

    def fake_get_profile(profile_id: str):
        return profile if profile_id == profile.profileId else None

    def fake_metadata(profile_id: str, file_id: str, parent_file_id: str = "0"):
        return type(
            "MetadataResult",
            (),
            {
                "ok": True,
                "status": 200,
                "error": "",
                "payload": {
                    "entry": {
                        "path": "demo (1).bin",
                        "size": 4,
                        "md5": "fe01ce2a7fbac8fafaed7c982a04e229",
                        "raw": {"fileId": file_id},
                    }
                },
            },
        )()

    def fake_list(profile_id: str, parent_file_id: str = "0", limit: int = 100, last_file_id: int = 0):
        return type(
            "ListResult",
            (),
            {
                "ok": True,
                "status": 200,
                "error": "",
                "payload": {
                    "items": [
                        {"fileId": "123-file-1", "name": "demo.bin", "parentId": parent_file_id, "size": 4}
                    ]
                },
            },
        )()

    post_calls: list[tuple[str, dict[str, object]]] = []
    put_calls: list[str] = []

    def fake_post_json(path: str, body: dict[str, object], auth: str):
        post_calls.append((path, dict(body)))
        if path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_CREATE_PATH:
            return (
                200,
                {
                    "data": {
                        "preuploadID": "pre-1",
                        "fileID": "123-file-1",
                    }
                },
            )
        if path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_URL_PATH:
            return (
                200,
                {
                    "data": {
                        "presignedURL": "https://upload.example.invalid/123/part1",
                    }
                },
            )
        if path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_COMPLETE_PATH:
            return (
                200,
                {
                    "data": {
                        "async": True,
                        "completed": False,
                    }
                },
            )
        if path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_ASYNC_RESULT_PATH:
            return (
                200,
                {
                    "data": {
                        "completed": True,
                        "fileID": "123-file-1",
                    }
                },
            )
        raise RuntimeError(f"unexpected_path:{path}")

    def fake_put_file(upload_url: str, file_path: Path) -> int:
        put_calls.append(f"{upload_url}|{file_path.name}|{file_path.stat().st_size}")
        return 200

    pan123_open_upload_live.get_profile = fake_get_profile
    pan123_open_upload_live._post_json = fake_post_json
    pan123_open_upload_live._put_file = fake_put_file
    pan123_open_upload_live.fetch_123_open_live_metadata = fake_metadata
    pan123_open_upload_live.fetch_123_open_live_list = fake_list
    pan123_open_upload_live.sleep = lambda seconds: None

    try:
        with TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "demo.bin"
            file_path.write_bytes(b"demo")
            result = pan123_open_upload_live.upload_123_open_local_file(
                profile_id=profile.profileId,
                local_path=str(file_path),
                target_name="demo.bin",
                parent_file_id="0",
                expected_md5="fe01ce2a7fbac8fafaed7c982a04e229",
                conflict_policy="overwrite_existing",
            ).to_dict()
    finally:
        pan123_open_upload_live.get_profile = original_get_profile
        pan123_open_upload_live._post_json = original_post_json
        pan123_open_upload_live._put_file = original_put_file
        pan123_open_upload_live.fetch_123_open_live_metadata = original_metadata
        pan123_open_upload_live.fetch_123_open_live_list = original_list
        pan123_open_upload_live.sleep = original_sleep

    print(
        json.dumps(
            {
                "ok": result.get("ok"),
                "mode": result.get("mode"),
                "verifyOk": result.get("verifyOk"),
                "verifyMode": result.get("verifyMode"),
                "resolvedTargetName": ((result.get("payload") or {}).get("resolvedTargetName")),
                "conflictAction": ((result.get("payload") or {}).get("conflictAction")),
                "createCalled": any(path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_CREATE_PATH for path, _ in post_calls),
                "getUploadUrlCalled": any(path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_URL_PATH for path, _ in post_calls),
                "completeCalled": any(path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_COMPLETE_PATH for path, _ in post_calls),
                "asyncResultCalled": any(path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_ASYNC_RESULT_PATH for path, _ in post_calls),
                "putCalled": len(put_calls) == 1 and "demo.bin|4" in put_calls[0],
                "pan123UploadLiveFlowMatchesExpectedOfficialChain": (
                    result.get("ok") is True
                    and result.get("mode") == "binary_upload_single_part"
                    and result.get("verifyOk") is True
                    and result.get("verifyMode") == "metadata_by_file_id"
                    and ((result.get("payload") or {}).get("resolvedTargetName")) == "demo (1).bin"
                    and ((result.get("payload") or {}).get("conflictAction")) == "overwrite_downgraded_to_auto_rename"
                    and any(path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_CREATE_PATH for path, _ in post_calls)
                    and any(path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_URL_PATH for path, _ in post_calls)
                    and any(path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_COMPLETE_PATH for path, _ in post_calls)
                    and any(path == pan123_open_upload_live.PAN123_OPEN_UPLOAD_ASYNC_RESULT_PATH for path, _ in post_calls)
                    and len(put_calls) == 1
                    and "demo.bin|4" in put_calls[0]
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
