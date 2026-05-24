from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import aliyun_open_upload_live
from cloudpan_sync.models import AuthProfile


def main() -> None:
    original_get_profile = aliyun_open_upload_live.get_profile
    original_post_json = aliyun_open_upload_live._post_json
    original_put_file = aliyun_open_upload_live._put_file
    original_metadata = aliyun_open_upload_live.fetch_aliyun_open_live_metadata
    original_list = aliyun_open_upload_live.fetch_aliyun_open_live_list

    profile = AuthProfile(
        profileId="ali-upload-1",
        providerKey="aliyundrive_open",
        authMode="official_oauth",
        displayName="aliyun-upload",
        token="Bearer ali-token",
        cookie="",
        extra={"domainId": "demo-domain", "driveId": "drive-1"},
        status="verified",
        lastError="",
        createdAt="2026-05-25T00:00:00+00:00",
        updatedAt="2026-05-25T00:00:00+00:00",
    )

    def fake_get_profile(profile_id: str):
        return profile if profile_id == profile.profileId else None

    def fake_metadata(profile_id: str, file_id: str):
        return type(
            "MetadataResult",
            (),
            {
                "ok": True,
                "status": 200,
                "error": "",
                "payload": {
                    "entry": {
                        "path": "demo.bin",
                        "size": 4,
                        "md5": "fe01ce2a7fbac8fafaed7c982a04e229",
                        "raw": {"fileId": file_id},
                    }
                },
            },
        )()

    def fake_list(profile_id: str, parent_file_id: str = "root", limit: int = 100):
        return type(
            "ListResult",
            (),
            {
                "ok": True,
                "status": 200,
                "error": "",
                "payload": {
                    "items": [
                        {"fileId": "ali-file-1", "name": "demo.bin", "parentId": parent_file_id, "size": 4}
                    ]
                },
            },
        )()

    post_calls: list[tuple[str, dict[str, object]]] = []
    put_calls: list[str] = []

    def fake_post_json(url: str, body: dict[str, object], auth: str):
        post_calls.append((url, dict(body)))
        if url.endswith("/v2/file/create"):
            return (
                201,
                {
                    "file_id": "ali-file-1",
                    "upload_id": "ali-upload-id-1",
                    "name": "demo (1).bin",
                    "part_info_list": [{"part_number": 1, "upload_url": "https://upload.example.invalid/part1"}],
                },
            )
        if url.endswith("/v2/file/complete"):
            return (
                200,
                {
                    "file_id": "ali-file-1",
                    "name": "demo (1).bin",
                },
            )
        raise RuntimeError(f"unexpected_url:{url}")

    def fake_put_file(upload_url: str, file_path: Path) -> int:
        put_calls.append(f"{upload_url}|{file_path.name}|{file_path.stat().st_size}")
        return 200

    aliyun_open_upload_live.get_profile = fake_get_profile
    aliyun_open_upload_live._post_json = fake_post_json
    aliyun_open_upload_live._put_file = fake_put_file
    aliyun_open_upload_live.fetch_aliyun_open_live_metadata = fake_metadata
    aliyun_open_upload_live.fetch_aliyun_open_live_list = fake_list

    try:
        with TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "demo.bin"
            file_path.write_bytes(b"demo")
            result = aliyun_open_upload_live.upload_aliyun_open_local_file(
                profile_id=profile.profileId,
                local_path=str(file_path),
                target_name="demo.bin",
                parent_file_id="root",
                expected_md5="fe01ce2a7fbac8fafaed7c982a04e229",
                conflict_policy="auto_rename_new",
            ).to_dict()
    finally:
        aliyun_open_upload_live.get_profile = original_get_profile
        aliyun_open_upload_live._post_json = original_post_json
        aliyun_open_upload_live._put_file = original_put_file
        aliyun_open_upload_live.fetch_aliyun_open_live_metadata = original_metadata
        aliyun_open_upload_live.fetch_aliyun_open_live_list = original_list

    print(
        json.dumps(
            {
                "ok": result.get("ok"),
                "mode": result.get("mode"),
                "verifyOk": result.get("verifyOk"),
                "verifyMode": result.get("verifyMode"),
                "resolvedTargetName": ((result.get("payload") or {}).get("resolvedTargetName")),
                "conflictAction": ((result.get("payload") or {}).get("conflictAction")),
                "createUsedAutoRename": any(
                    str(body.get("check_name_mode") or "") == "auto_rename"
                    for _, body in post_calls
                    if _.endswith("/v2/file/create")
                ),
                "completeCalled": any(url.endswith("/v2/file/complete") for url, _ in post_calls),
                "putCalled": len(put_calls) == 1 and "demo.bin|4" in put_calls[0],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
