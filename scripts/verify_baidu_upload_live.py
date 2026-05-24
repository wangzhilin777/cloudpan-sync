from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import baidu_netdisk_upload_live
from cloudpan_sync.models import AuthProfile


def main() -> None:
    original_load_profile = baidu_netdisk_upload_live._load_profile_requirements
    original_post_form = baidu_netdisk_upload_live._post_form
    original_tmpfile = baidu_netdisk_upload_live._post_multipart_tmpfile
    original_metadata = baidu_netdisk_upload_live.fetch_baidu_live_metadata
    original_list = baidu_netdisk_upload_live.fetch_baidu_live_list

    profile = AuthProfile(
        profileId="bd-upload-1",
        providerKey="baidu_netdisk",
        authMode="manual_token",
        displayName="bd-upload",
        token="bd-token",
        cookie="",
        extra={"dir": "/"},
        status="verified",
        lastError="",
        createdAt="2026-05-25T00:00:00+00:00",
        updatedAt="2026-05-25T00:00:00+00:00",
    )

    def fake_load_profile(profile_id: str):
        if profile_id != profile.profileId:
            return None, "", ""
        return profile, "bd-token", ""

    def fake_metadata(profile_id: str, file_id: str = "", path: str = ""):
        return type(
            "MetadataResult",
            (),
            {
                "ok": True,
                "status": 200,
                "error": "",
                "payload": {
                    "entry": {
                        "path": "/demo (1).bin",
                        "size": 4,
                        "md5": "fe01ce2a7fbac8fafaed7c982a04e229",
                        "raw": {"fs_id": file_id},
                    }
                },
            },
        )()

    def fake_list(profile_id: str, dir_path: str = "/", limit: int = 100):
        return type(
            "ListResult",
            (),
            {
                "ok": True,
                "status": 200,
                "error": "",
                "payload": {
                    "items": [
                        {"fileId": "bd-file-1", "name": "demo.bin", "path": "/demo.bin", "parentId": dir_path}
                    ]
                },
            },
        )()

    form_calls: list[tuple[str, dict[str, object]]] = []
    tmpfile_calls: list[str] = []

    def fake_post_form(method_name: str, body: dict[str, object], access_token: str, cookie: str):
        form_calls.append((method_name, dict(body)))
        if method_name == "precreate":
            return (
                200,
                {
                    "uploadid": "bd-upload-id-1",
                },
            )
        if method_name == "create":
            return (
                200,
                {
                    "fs_id": "bd-file-1",
                    "path": "/demo (1).bin",
                },
            )
        raise RuntimeError(f"unexpected_method:{method_name}")

    def fake_post_tmpfile(*, access_token: str, cookie: str, remote_path: str, upload_id: str, file_path: Path):
        tmpfile_calls.append(f"{remote_path}|{upload_id}|{file_path.name}|{file_path.stat().st_size}")
        return (
            200,
            {
                "md5": "fe01ce2a7fbac8fafaed7c982a04e229",
            },
        )

    baidu_netdisk_upload_live._load_profile_requirements = fake_load_profile
    baidu_netdisk_upload_live._post_form = fake_post_form
    baidu_netdisk_upload_live._post_multipart_tmpfile = fake_post_tmpfile
    baidu_netdisk_upload_live.fetch_baidu_live_metadata = fake_metadata
    baidu_netdisk_upload_live.fetch_baidu_live_list = fake_list

    try:
        with TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "demo.bin"
            file_path.write_bytes(b"demo")
            result = baidu_netdisk_upload_live.upload_baidu_local_file(
                profile_id=profile.profileId,
                local_path=str(file_path),
                target_name="demo.bin",
                parent_dir="/",
                expected_md5="fe01ce2a7fbac8fafaed7c982a04e229",
                conflict_policy="overwrite_existing",
            ).to_dict()
    finally:
        baidu_netdisk_upload_live._load_profile_requirements = original_load_profile
        baidu_netdisk_upload_live._post_form = original_post_form
        baidu_netdisk_upload_live._post_multipart_tmpfile = original_tmpfile
        baidu_netdisk_upload_live.fetch_baidu_live_metadata = original_metadata
        baidu_netdisk_upload_live.fetch_baidu_live_list = original_list

    print(
        json.dumps(
            {
                "ok": result.get("ok"),
                "mode": result.get("mode"),
                "verifyOk": result.get("verifyOk"),
                "verifyMode": result.get("verifyMode"),
                "resolvedTargetName": ((result.get("payload") or {}).get("resolvedTargetName")),
                "conflictAction": ((result.get("payload") or {}).get("conflictAction")),
                "precreateCalled": any(method == "precreate" for method, _ in form_calls),
                "createCalled": any(method == "create" for method, _ in form_calls),
                "tmpfileCalled": len(tmpfile_calls) == 1 and "|bd-upload-id-1|demo.bin|4" in tmpfile_calls[0],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
