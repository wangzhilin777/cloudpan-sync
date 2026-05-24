from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import quark_fast_upload_live


class _FakeHeaders:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = dict(values)

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._values.get(key, default)


class _FakeResponse:
    def __init__(self, status: int, headers: dict[str, str] | None = None, body: bytes = b"") -> None:
        self.status = status
        self.headers = _FakeHeaders(headers or {})
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def main() -> None:
    original_get_profile = quark_fast_upload_live.get_profile
    original_request_json = quark_fast_upload_live._request_json
    original_urlopen = quark_fast_upload_live.urlopen

    request_calls: list[tuple[str, str, dict[str, object]]] = []
    oss_calls: list[tuple[str, str]] = []

    file_path = ROOT / "tmp" / "verify-quark-fast-upload-fallback.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"cloudpan-sync-quark-fast-upload-fallback")

    def fake_get_profile(profile_id: str):
        if profile_id != "quark-fast-1":
            return None
        return type(
            "Profile",
            (),
            {
                "profileId": "quark-fast-1",
                "providerKey": "quark",
                "cookie": "sid=demo",
                "extra": {},
            },
        )()

    def fake_request_json(url: str, method: str, headers: dict[str, str], body: dict[str, object] | None = None):
        payload = dict(body or {})
        request_calls.append((method, url, payload))
        if "/file/upload/pre?" in url:
            return 200, {
                "code": 0,
                "data": {
                    "task_id": "task-qf-2",
                    "obj_key": "folder/demo.bin",
                    "fid": "fid-qf-2",
                    "bucket": "bucket-qf",
                    "upload_url": "https://oss-cn-test.aliyuncs.com",
                    "upload_id": "upload-qf-1",
                    "part_size": 8,
                    "auth_info": {"token": "demo-auth"},
                    "callback": {"callbackUrl": "https://callback.invalid"},
                },
            }
        if "/file/update/hash?" in url:
            return 200, {"code": 0, "data": {"finish": False, "fid": "fid-qf-2"}}
        if "/file/upload/auth?" in url:
            return 200, {"code": 0, "data": {"auth_key": "OSS demo auth"}}
        if "/file/upload/finish?" in url:
            return 200, {"code": 0, "data": {"fid": "fid-qf-2", "file_name": "demo.bin"}}
        raise AssertionError(f"unexpected_request: {url}")

    def fake_urlopen(request, timeout: int = 0):
        url = request.full_url
        method = request.get_method()
        oss_calls.append((method, url))
        if method == "PUT":
            return _FakeResponse(200, {"Etag": '"etag-part-1"'})
        if method == "POST":
            return _FakeResponse(200, {}, b"<CompleteMultipartUploadResult />")
        raise AssertionError(f"unexpected_oss_call: {method} {url}")

    quark_fast_upload_live.get_profile = fake_get_profile
    quark_fast_upload_live._request_json = fake_request_json
    quark_fast_upload_live.urlopen = fake_urlopen

    try:
        result = quark_fast_upload_live.upload_quark_fast_file(
            profile_id="quark-fast-1",
            local_path=str(file_path),
            target_name="demo.bin",
            parent_id="0",
        )
    finally:
        quark_fast_upload_live.get_profile = original_get_profile
        quark_fast_upload_live._request_json = original_request_json
        quark_fast_upload_live.urlopen = original_urlopen
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()

    payload = result.to_dict()
    live_payload = dict(payload.get("payload") or {})
    fallback_payload = dict(live_payload.get("uploadFallback") or {})
    print(
        json.dumps(
            {
                "ok": payload.get("ok"),
                "mode": payload.get("mode"),
                "verifyOk": payload.get("verifyOk"),
                "verifyMode": payload.get("verifyMode"),
                "usedBinaryFallback": bool((payload.get("verifyPayload") or {}).get("usedBinaryFallback")),
                "uploadAuthCalls": sum(1 for _, url, _ in request_calls if "/file/upload/auth?" in url),
                "finishCalled": any("/file/upload/finish?" in url for _, url, _ in request_calls),
                "ossPutCalled": any(method == "PUT" for method, _ in oss_calls),
                "ossPostCalled": any(method == "POST" for method, _ in oss_calls),
                "partCount": fallback_payload.get("partCount"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
