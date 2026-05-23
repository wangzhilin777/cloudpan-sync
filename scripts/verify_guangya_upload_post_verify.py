from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import guangya_upload_live
from cloudpan_sync.models import AuthProfile


class _FakeResponse:
    status_code = 400
    text = "fallback to multipart"


class _FakeHTTPStatusError(Exception):
    def __init__(self, response: object):
        self.response = response


class _DirectUploadClient:
    def __init__(self, *args, **kwargs):
        pass

    def file_upload(self, local_path: str, name: str, parent_id: str):
        return {"data": {"fileId": "f-direct-1", "name": name, "parentId": parent_id}}

    def close(self):
        return None


class _MultipartUploadClient:
    def __init__(self, *args, **kwargs):
        self._upload_info_calls = 0

    def file_upload(self, local_path: str, name: str, parent_id: str):
        raise _FakeHTTPStatusError(_FakeResponse())

    def upload_token(self, name: str, size: int, parent_id: str):
        return {"data": {"taskId": "task-1", "uploadUrl": "https://example.invalid/upload"}}

    def check_can_flash_upload(self, task_id: str, file_path: Path):
        return {"data": {"canFlashUpload": False}}

    def cdn_upload(self, file_path: Path, token_data: dict[str, object], content_type: str = ""):
        return None

    def upload_info(self, task_id: str):
        self._upload_info_calls += 1
        if self._upload_info_calls == 1:
            return {"msg": "文件上传中"}
        return {"msg": "完成", "data": {"taskId": task_id}}

    def close(self):
        return None


def main() -> None:
    original_client = guangya_upload_live.GuangyaClient
    original_http_error = guangya_upload_live.HTTPStatusError
    original_get_profile = guangya_upload_live.get_profile
    original_metadata = guangya_upload_live.fetch_guangya_live_metadata
    original_list = guangya_upload_live.fetch_guangya_live_list
    original_sleep = guangya_upload_live.sleep

    profile = AuthProfile(
        profileId="gy-upload-1",
        providerKey="guangya",
        authMode="manual_token",
        displayName="gy-upload",
        token="Bearer tok-direct",
        cookie="",
        extra={"parentId": "dir-100"},
        status="verified",
        lastError="",
        createdAt="2026-05-23T00:00:00+00:00",
        updatedAt="2026-05-23T00:00:00+00:00",
    )

    def fake_get_profile(profile_id: str):
        return profile if profile_id == profile.profileId else None

    def fake_metadata(profile_id: str, file_id: str):
        if file_id == "f-direct-1":
            return type(
                "MetadataResult",
                (),
                {
                    "ok": True,
                    "items": [{"fileId": file_id, "name": "demo.bin", "md5": "d41d8cd98f00b204e9800998ecf8427e"}],
                    "status": 200,
                    "error": "",
                    "riskHint": "",
                },
            )()
        return type(
            "MetadataResult",
            (),
            {
                "ok": False,
                "items": [],
                "status": 404,
                "error": "missing_file_id",
                "riskHint": "metadata missing",
            },
        )()

    def fake_list(profile_id: str, parent_id: str = "", page_size: int = 100):
        return type(
            "ListResult",
            (),
            {
                "ok": True,
                "items": [{"fileId": "f-list-1", "name": "demo.bin", "parentId": parent_id, "size": 4}],
                "status": 200,
                "error": "",
                "riskHint": "",
            },
        )()

    with TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "demo.bin"
        file_path.write_bytes(b"demo")

        guangya_upload_live.HTTPStatusError = _FakeHTTPStatusError
        guangya_upload_live.get_profile = fake_get_profile
        guangya_upload_live.fetch_guangya_live_metadata = fake_metadata
        guangya_upload_live.fetch_guangya_live_list = fake_list
        guangya_upload_live.sleep = lambda seconds: None

        try:
            guangya_upload_live.GuangyaClient = _DirectUploadClient
            direct = guangya_upload_live.upload_guangya_local_file(
                profile_id=profile.profileId,
                local_path=str(file_path),
                target_name="demo.bin",
                parent_id="dir-100",
                conflict_policy="auto_rename_new",
            ).to_dict()

            guangya_upload_live.GuangyaClient = _MultipartUploadClient
            multipart = guangya_upload_live.upload_guangya_local_file(
                profile_id=profile.profileId,
                local_path=str(file_path),
                target_name="demo.bin",
                parent_id="dir-100",
                conflict_policy="overwrite_existing",
            ).to_dict()
        finally:
            guangya_upload_live.GuangyaClient = original_client
            guangya_upload_live.HTTPStatusError = original_http_error
            guangya_upload_live.get_profile = original_get_profile
            guangya_upload_live.fetch_guangya_live_metadata = original_metadata
            guangya_upload_live.fetch_guangya_live_list = original_list
            guangya_upload_live.sleep = original_sleep

    print(
        json.dumps(
            {
                "direct": {
                    "ok": direct.get("ok"),
                    "mode": direct.get("mode"),
                    "verifyOk": direct.get("verifyOk"),
                    "verifyMode": direct.get("verifyMode"),
                    "verifyNote": direct.get("verifyNote"),
                    "conflictAction": ((direct.get("payload") or {}).get("conflictAction")),
                    "resolvedTargetName": ((direct.get("payload") or {}).get("resolvedTargetName")),
                },
                "multipart": {
                    "ok": multipart.get("ok"),
                    "mode": multipart.get("mode"),
                    "verifyOk": multipart.get("verifyOk"),
                    "verifyMode": multipart.get("verifyMode"),
                    "verifyNote": multipart.get("verifyNote"),
                    "conflictAction": ((multipart.get("payload") or {}).get("conflictAction")),
                    "resolvedTargetName": ((multipart.get("payload") or {}).get("resolvedTargetName")),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
