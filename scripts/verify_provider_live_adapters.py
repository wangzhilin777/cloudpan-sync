from __future__ import annotations

import json
import sys
from contextlib import ExitStack, contextmanager
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import baidu_netdisk_live
from cloudpan_sync import guangya_live
from cloudpan_sync import aliyun_open_live
from cloudpan_sync import pan115_open_live
from cloudpan_sync import pan123_open_live
from cloudpan_sync import pikpak_live
from cloudpan_sync import provider_live_probe
from cloudpan_sync import provider_status_matrix
from cloudpan_sync import quark_live
from cloudpan_sync import tianyi_live
from cloudpan_sync import uc_live
from cloudpan_sync import xunlei_live


@contextmanager
def patched_attr(target: object, name: str, value: object):
    original = getattr(target, name)
    setattr(target, name, value)
    try:
        yield
    finally:
        setattr(target, name, original)


def verify_baidu() -> dict[str, object]:
    profile = SimpleNamespace(profileId="bd-test", token="bd-token", cookie="", extra={})

    def fake_get(method_name: str, params: dict[str, object], access_token: str, cookie: str):
        if method_name == "list":
            return 200, {
                "list": [
                    {"fs_id": 11, "path": "/share", "server_filename": "share", "isdir": 1, "size": 0},
                    {
                        "fs_id": 22,
                        "path": "/movie.mkv",
                        "server_filename": "movie.mkv",
                        "isdir": 0,
                        "size": 1503238553,
                        "md5": "0123456789abcdef0123456789abcdef",
                    },
                ]
            }
        if method_name == "filemetas":
            return 200, {
                "info": [
                    {
                        "fs_id": 22,
                        "path": "/movie.mkv",
                        "server_filename": "movie.mkv",
                        "isdir": 0,
                        "size": 1503238553,
                        "md5": "0123456789abcdef0123456789abcdef",
                    }
                ]
            }
        raise AssertionError(method_name)

    def fake_post(method_name: str, body: dict[str, object], access_token: str, cookie: str):
        return 200, {"fs_id": 33, "path": "/demo-dir", "server_filename": "demo-dir", "isdir": 1}

    with patched_attr(baidu_netdisk_live, "get_profile", lambda profile_id: profile):
        with patched_attr(baidu_netdisk_live, "_request_json", fake_get):
            with patched_attr(baidu_netdisk_live, "_post_form", fake_post):
                list_result = baidu_netdisk_live.fetch_baidu_live_list("bd-test", dir_path="/", limit=50)
                meta_result = baidu_netdisk_live.fetch_baidu_live_metadata("bd-test", file_id="22")
                create_result = baidu_netdisk_live.fetch_baidu_create_dir("bd-test", parent_dir="/", dir_name="demo-dir")
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "metadata_md5": meta_result.payload.get("entry", {}).get("md5", ""),
    }


def verify_guangya() -> dict[str, object]:
    profile = SimpleNamespace(profileId="gy-test", token="gy-token", extra={"authorization": "gy-token", "parentId": "dir-root"})

    class FakeResponse:
        def __init__(self, payload: dict[str, object], status: int = 200):
            self.payload = payload
            self.status = status

        def read(self) -> bytes:
            return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(request, timeout: int = 15):
        url = request.full_url
        if "get_file_list" in url:
            return FakeResponse(
                {
                    "data": {
                        "records": [
                            {"fileId": "dir-1", "fileName": "media", "isDir": 1, "parentId": "dir-root", "fileSize": 0},
                            {"fileId": "file-1", "fileName": "movie.mkv", "isDir": 0, "parentId": "dir-root", "fileSize": 1503238553, "md5": "0123456789abcdef0123456789abcdef"},
                        ]
                    }
                }
            )
        if "get_res_download_url" in url:
            return FakeResponse(
                {
                    "data": {
                        "fileId": "file-1",
                        "fileName": "movie.mkv",
                        "fileSize": 1503238553,
                        "md5": "0123456789abcdef0123456789abcdef",
                        "gcid": "a" * 40,
                    }
                }
            )
        if "create_dir" in url:
            return FakeResponse({"data": {"fileId": "new-dir-1", "fileName": "demo-dir", "isDir": 1, "parentId": "dir-root", "fileSize": 0}})
        raise AssertionError(url)

    with patched_attr(guangya_live, "get_profile", lambda profile_id: profile):
        with patched_attr(guangya_live, "urlopen", fake_urlopen):
            list_result = guangya_live.fetch_guangya_live_list("gy-test", parent_id="dir-root", page_size=50)
            meta_result = guangya_live.fetch_guangya_live_metadata("gy-test", file_id="file-1")
            create_result = guangya_live.fetch_guangya_create_dir("gy-test", parent_id="dir-root", dir_name="demo-dir")
    meta_item = meta_result.items[0] if meta_result.items else {}
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "metadata_md5": meta_item.get("md5", ""),
        "metadata_gcid": meta_item.get("gcid", ""),
    }


def verify_aliyun_open() -> dict[str, object]:
    profile = SimpleNamespace(
        profileId="ali-test",
        token="ali-token",
        extra={"domainId": "demo-domain", "driveId": "drive-demo"},
    )

    def fake_post(url: str, body: dict[str, object], auth: str):
        if url.endswith("/v2/file/list"):
            return 200, {
                "items": [
                    {"file_id": "dir-1", "name": "backup", "type": "folder", "parent_file_id": "root", "size": 0},
                    {
                        "file_id": "file-1",
                        "name": "db.dump",
                        "type": "file",
                        "parent_file_id": "root",
                        "size": 91231345,
                        "content_hash_name": "md5",
                        "content_hash": "0123456789abcdef0123456789abcdef",
                    },
                ]
            }
        if url.endswith("/v2/file/get"):
            return 200, {
                "file_id": "file-1",
                "name": "db.dump",
                "type": "file",
                "parent_file_id": "root",
                "size": 91231345,
                "content_hash_name": "md5",
                "content_hash": "0123456789abcdef0123456789abcdef",
            }
        if url.endswith("/v2/file/create"):
            return 200, {"file_id": "new-dir-1", "parent_file_id": "root", "name": "demo-dir", "type": "folder"}
        raise AssertionError(url)

    with patched_attr(aliyun_open_live, "get_profile", lambda profile_id: profile):
        with patched_attr(aliyun_open_live, "_post_json", fake_post):
            list_result = aliyun_open_live.fetch_aliyun_open_live_list("ali-test", parent_file_id="root", limit=50)
            meta_result = aliyun_open_live.fetch_aliyun_open_live_metadata("ali-test", file_id="file-1")
            create_result = aliyun_open_live.fetch_aliyun_open_create_folder("ali-test", parent_file_id="root", dir_name="demo-dir")
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "metadata_md5": meta_result.payload.get("entry", {}).get("md5", ""),
    }


def verify_189cloud() -> dict[str, object]:
    share_profile = SimpleNamespace(
        profileId="189-test",
        extra={"shareCode": "share-demo", "fileId": "root-file", "pathPrefix": "/189cloud-share"},
    )
    write_profile = SimpleNamespace(
        profileId="189-write-test",
        token="access-token-demo",
        extra={
            "signature": "sig-demo",
            "date": "Sat, 24 May 2026 00:00:00 GMT",
            "fileId": "root-file",
        },
    )

    def fake_share_info(share_code: str):
        return 200, {"res_code": 0, "data": {"shareId": "share-id-1", "shareMode": 1, "fileId": "root-file"}}

    def fake_share_id(share_code: str, access_code: str, share_info: dict[str, object]):
        return 200, "share-id-1"

    def fake_dir_page(
        share_code: str,
        share_id: str,
        share_mode: int,
        file_id: str,
        page_num: int = 1,
        page_size: int = 100,
        access_code: str = "",
    ):
        return 200, {
            "res_code": 0,
            "fileListAO": {
                "folderList": [{"id": "dir-1", "name": "media"}],
                "fileList": [{"id": "file-1", "name": "movie.mkv", "size": 1503238553, "md5": "0123456789abcdef0123456789abcdef"}],
            },
        }

    def fake_get_profile(profile_id: str):
        if profile_id == "189-write-test":
            return write_profile
        return share_profile

    def fake_create_request(access_token: str, signature: str, date_value: str, parent_id: str, dir_name: str):
        return 200, {"res_code": 0, "id": "dir-189-1", "name": dir_name}

    with patched_attr(tianyi_live, "get_profile", fake_get_profile):
        with patched_attr(tianyi_live, "_fetch_share_info", fake_share_info):
            with patched_attr(tianyi_live, "_fetch_share_id", fake_share_id):
                with patched_attr(tianyi_live, "_fetch_dir_page", fake_dir_page):
                    with patched_attr(tianyi_live, "_request_create_folder", fake_create_request):
                        list_result = tianyi_live.fetch_tianyi_live_list("189-test", file_id="root-file", page_size=50)
                        meta_result = tianyi_live.fetch_tianyi_live_metadata("189-test", file_id="file-1")
                        create_result = tianyi_live.fetch_tianyi_create_folder("189-write-test", parent_id="root-file", dir_name="demo-dir")
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "create_mode": create_result.mode,
        "create_file_id": ((create_result.payload or {}).get("item") or {}).get("fileId", ""),
        "metadata_md5": meta_result.payload.get("entry", {}).get("md5", ""),
    }


def verify_123_open() -> dict[str, object]:
    profile = SimpleNamespace(profileId="123-test", token="tok-123", extra={})

    def fake_get(path: str, params: dict[str, object], auth: str):
        return 200, {
            "data": {
                "fileList": [
                    {"fileId": 1, "filename": "backup", "type": 1, "parentFileId": 0, "size": 0},
                    {"fileId": 2, "filename": "db.dump", "type": 0, "parentFileId": 0, "size": 91231345, "etag": "0123456789abcdef0123456789abcdef"},
                ]
            }
        }

    def fake_post(path: str, body: dict[str, object], auth: str):
        return 200, {"data": {"dirID": 3}}

    with patched_attr(pan123_open_live, "get_profile", lambda profile_id: profile):
        with patched_attr(pan123_open_live, "_get_json", fake_get):
            with patched_attr(pan123_open_live, "_post_json", fake_post):
                list_result = pan123_open_live.fetch_123_open_live_list("123-test", parent_file_id="0", limit=50)
                meta_result = pan123_open_live.fetch_123_open_live_metadata("123-test", file_id="2", parent_file_id="0")
                create_result = pan123_open_live.fetch_123_open_create_folder("123-test", parent_file_id="0", dir_name="demo-dir")
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "metadata_md5": meta_result.payload.get("entry", {}).get("md5", ""),
    }


def verify_115_open() -> dict[str, object]:
    profile = SimpleNamespace(profileId="115-test", cookie="UID=1", extra={})

    def fake_get(url: str, params: dict[str, object], cookie_header: str):
        if "files/get_info" in url:
            return 200, {
                "state": True,
                "data": [
                    {"fid": "file-1", "n": "backup.tar", "sha": "0" * 40, "s": 149946368}
                ],
            }
        return 200, {
            "state": True,
            "data": [
                {"cid": "dir-1", "n": "media", "fc": "1", "pid": "0"},
                {"fid": "file-1", "n": "backup.tar", "sha": "0" * 40, "s": 149946368, "pid": "0"},
            ],
        }

    def fake_post(url: str, body: dict[str, object], cookie_header: str):
        return 200, {"state": True, "cid": "new-dir-1"}

    with patched_attr(pan115_open_live, "get_profile", lambda profile_id: profile):
        with patched_attr(pan115_open_live, "_get_json", fake_get):
            with patched_attr(pan115_open_live, "_post_form", fake_post):
                list_result = pan115_open_live.fetch_115_open_live_list("115-test", cid="0", limit=50)
                meta_result = pan115_open_live.fetch_115_open_live_metadata("115-test", file_id="file-1")
                create_result = pan115_open_live.fetch_115_open_create_folder("115-test", parent_id="0", dir_name="demo-dir")
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "metadata_sha1": meta_result.payload.get("entry", {}).get("sha1", ""),
    }


def verify_xunlei() -> dict[str, object]:
    profile = SimpleNamespace(profileId="xl-test", token="token-demo", extra={"deviceId": "dev-1"})

    def fake_get(path: str, params: dict[str, object], auth_headers: dict[str, str]):
        return 200, {
            "files": [
                {"id": "dir-1", "name": "downloads", "kind": "drive#folder", "parent_id": "", "size": 0},
                {"id": "file-1", "name": "linux.iso", "kind": "drive#file", "parent_id": "", "size": 2382364672, "hash": "A" * 40},
            ],
            "next_page_token": "",
        }

    def fake_post(path: str, body: dict[str, object], auth_headers: dict[str, str]):
        return 200, {"id": "new-dir-1", "name": body["name"], "kind": "drive#folder", "parent_id": body.get("parent_id", "")}

    with patched_attr(xunlei_live, "get_profile", lambda profile_id: profile):
        with patched_attr(xunlei_live, "_get_json", fake_get):
            with patched_attr(xunlei_live, "_post_json", fake_post):
                list_result = xunlei_live.fetch_xunlei_live_list("xl-test", parent_id="", limit=50)
                meta_result = xunlei_live.fetch_xunlei_live_metadata("xl-test", file_id="file-1", parent_id="")
                create_result = xunlei_live.fetch_xunlei_create_folder("xl-test", parent_id="", dir_name="demo-dir")
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "metadata_gcid": meta_result.payload.get("entry", {}).get("gcid", ""),
    }


def verify_pikpak() -> dict[str, object]:
    profile = SimpleNamespace(profileId="pk-test", token="token-demo", extra={"deviceId": "dev-1"})

    def fake_get(path: str, params: dict[str, object], auth_headers: dict[str, str]):
        if path == "/drive/v1/files":
            return 200, {
                "files": [
                    {"id": "dir-1", "name": "saved", "kind": "drive#folder", "parent_id": "", "size": 0},
                    {"id": "file-1", "name": "clip.mp4", "kind": "drive#file", "parent_id": "", "size": 18823212, "hash": "A" * 40},
                ],
                "next_page_token": "",
            }
        if path == "/drive/v1/files/file-1":
            return 200, {"id": "file-1", "name": "clip.mp4", "kind": "drive#file", "parent_id": "", "size": 18823212, "hash": "A" * 40}
        raise AssertionError(path)

    def fake_post(path: str, body: dict[str, object], auth_headers: dict[str, str]):
        return 200, {"id": "new-dir-1", "name": body["name"], "kind": "drive#folder", "parent_id": body.get("parent_id", "")}

    with patched_attr(pikpak_live, "get_profile", lambda profile_id: profile):
        with patched_attr(pikpak_live, "_get_json", fake_get):
            with patched_attr(pikpak_live, "_post_json", fake_post):
                list_result = pikpak_live.fetch_pikpak_live_list("pk-test", parent_id="", limit=50)
                meta_result = pikpak_live.fetch_pikpak_live_metadata("pk-test", file_id="file-1")
                create_result = pikpak_live.fetch_pikpak_create_folder("pk-test", parent_id="", dir_name="demo-dir")
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "metadata_gcid": meta_result.payload.get("entry", {}).get("gcid", ""),
    }


def verify_quark() -> dict[str, object]:
    profile = SimpleNamespace(profileId="quark-test", cookie="cookie=1", extra={"pwdId": "pwd-demo"})

    def fake_request(url: str, method: str, headers: dict[str, str], body: dict[str, object] | None = None):
        if "sharepage/token" in url:
            return 200, {"data": {"stoken": "stok-demo"}}
        if "sharepage/detail" in url:
            return 200, {
                "code": 0,
                "data": {
                    "list": [
                        {"fid": "dir-1", "file_name": "docs", "dir": True, "size": 0},
                        {"fid": "file-1", "share_fid_token": "token-1", "file_name": "ebook.epub", "size": 6172839},
                    ],
                    "total": 2,
                },
            }
        if "clouddrive/file/download" in url:
            return 200, {"data": {"items": [{"fid": "file-1", "md5": "0123456789abcdef0123456789abcdef"}]}}
        if "clouddrive/file?" in url:
            return 200, {"code": 0, "data": {"fid": "new-dir-1", "file_name": body["file_name"], "pdir_fid": body["pdir_fid"]}}
        raise AssertionError(url)

    with patched_attr(quark_live, "get_profile", lambda profile_id: profile):
        with patched_attr(quark_live, "_request_json", fake_request):
            list_result = quark_live.fetch_quark_live_list("quark-test", parent_id="0", page_size=50)
            meta_result = quark_live.fetch_quark_live_metadata("quark-test", file_id="file-1", parent_id="0")
            create_result = quark_live.fetch_quark_create_folder("quark-test", parent_id="0", dir_name="demo-dir")
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "metadata_md5": meta_result.payload.get("entry", {}).get("md5", ""),
    }


def verify_uc() -> dict[str, object]:
    profile = SimpleNamespace(profileId="uc-test", cookie="cookie=1", extra={"pwdId": "pwd-demo"})

    def fake_request(url: str, method: str, headers: dict[str, str], body: dict[str, object] | None = None):
        if "sharepage/token" in url:
            return 200, {"data": {"stoken": "stok-demo"}}
        if "sharepage/detail" in url:
            return 200, {
                "code": 0,
                "data": {
                    "list": [
                        {"fid": "dir-1", "file_name": "notes", "dir": True, "size": 0},
                        {"fid": "file-1", "share_fid_token": "token-1", "file_name": "slides.pptx", "size": 8721312},
                    ],
                    "total": 2,
                },
            }
        if "clouddrive/file/download" in url:
            return 200, {"data": {"items": [{"fid": "file-1", "md5": "0123456789abcdef0123456789abcdef"}]}}
        if "clouddrive/file?" in url:
            return 200, {"code": 0, "data": {"fid": "new-dir-1", "file_name": body["file_name"], "pdir_fid": body["pdir_fid"]}}
        raise AssertionError(url)

    with patched_attr(uc_live, "get_profile", lambda profile_id: profile):
        with patched_attr(uc_live, "_request_json", fake_request):
            list_result = uc_live.fetch_uc_live_list("uc-test", parent_id="0", page_size=50)
            meta_result = uc_live.fetch_uc_live_metadata("uc-test", file_id="file-1", parent_id="0")
            create_result = uc_live.fetch_uc_create_folder("uc-test", parent_id="0", dir_name="demo-dir")
    return {
        "list_ok": list_result.ok,
        "metadata_ok": meta_result.ok,
        "create_ok": create_result.ok,
        "metadata_md5": meta_result.payload.get("entry", {}).get("md5", ""),
    }


def verify_probe_and_matrix() -> dict[str, object]:
    def registry_profile(provider_key: str, display_name: str, auth_modes: list[str]) -> SimpleNamespace:
        return SimpleNamespace(
            profile=SimpleNamespace(
                providerKey=provider_key,
                displayName=display_name,
                authModes=auth_modes,
                status="researching",
                conflictPolicies=[],
                supportsOverwrite=False,
                supportsAutoRename=False,
                overwriteBehavior="",
                conflictNotes="",
            )
        )

    provider_profiles = {
        "guangya": SimpleNamespace(profileId="gy-profile", providerKey="guangya"),
        "aliyundrive_open": SimpleNamespace(profileId="ali-profile", providerKey="aliyundrive_open"),
        "189cloud": SimpleNamespace(profileId="189-profile", providerKey="189cloud"),
        "baidu_netdisk": SimpleNamespace(profileId="bd-profile", providerKey="baidu_netdisk"),
        "123_open": SimpleNamespace(profileId="123-profile", providerKey="123_open"),
        "115_open": SimpleNamespace(profileId="115-profile", providerKey="115_open"),
        "xunlei": SimpleNamespace(profileId="xl-profile", providerKey="xunlei"),
        "pikpak": SimpleNamespace(profileId="pk-profile", providerKey="pikpak"),
        "quark": SimpleNamespace(profileId="quark-profile", providerKey="quark"),
        "uc": SimpleNamespace(profileId="uc-profile", providerKey="uc"),
    }

    registry_profiles = [
        registry_profile("guangya", "Guangya", ["manual_token"]),
        registry_profile("aliyundrive_open", "Aliyun Drive Open", ["official_oauth"]),
        registry_profile("189cloud", "189Cloud", ["web_login_capture"]),
        registry_profile("baidu_netdisk", "Baidu Netdisk", ["manual_token"]),
        registry_profile("123_open", "123Pan Open", ["manual_token"]),
        registry_profile("115_open", "115 Open", ["manual_cookie"]),
        registry_profile("xunlei", "Xunlei Drive", ["manual_token"]),
        registry_profile("pikpak", "PikPak", ["manual_token"]),
        registry_profile("quark", "Quark", ["manual_cookie"]),
        registry_profile("uc", "UC Drive", ["manual_cookie"]),
    ]
    registry_profiles[0].profile.conflictPolicies = ["overwrite_existing", "auto_rename_new"]
    registry_profiles[0].profile.supportsAutoRename = True
    registry_profiles[0].profile.overwriteBehavior = "downgrade_to_auto_rename"
    registry_profiles[0].profile.conflictNotes = "guangya note"
    registry_profiles[2].profile.overwriteBehavior = "readonly_auth_blocked"

    research_rows = [{"providerKey": profile.profile.providerKey, "status": "researching"} for profile in registry_profiles]
    saved_probes = [
        {"providerKey": "guangya", "ok": True, "mode": "live"},
        {"providerKey": "aliyundrive_open", "ok": True, "mode": "live"},
        {"providerKey": "189cloud", "ok": True, "mode": "live"},
        {"providerKey": "baidu_netdisk", "ok": True, "mode": "live"},
        {"providerKey": "123_open", "ok": True, "mode": "live"},
        {"providerKey": "115_open", "ok": True, "mode": "live"},
        {"providerKey": "xunlei", "ok": True, "mode": "live"},
        {"providerKey": "pikpak", "ok": True, "mode": "live"},
        {"providerKey": "quark", "ok": True, "mode": "live"},
        {"providerKey": "uc", "ok": True, "mode": "live"},
    ]

    with patched_attr(provider_live_probe, "get_profile", lambda profile_id: provider_profiles[profile_id.replace("-profile", "") if profile_id.endswith("-profile") else profile_id]):
        pass

    results: dict[str, dict[str, object]] = {}

    with ExitStack() as stack:
        stack.enter_context(patched_attr(provider_live_probe, "get_profile", lambda profile_id: provider_profiles.get(profile_id.replace("-profile", ""), provider_profiles.get(profile_id))))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_guangya_live_list", lambda profile_id, parent_id="", page_size=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="guangya list ok", items=[{"fileId": "file-1", "md5": "0123456789abcdef0123456789abcdef"}], profileId="gy-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_guangya_live_metadata", lambda profile_id, file_id: SimpleNamespace(ok=True, mode="live", status=200, error="", note="guangya meta ok", items=[{"fileId": "file-1", "md5": "0123456789abcdef0123456789abcdef", "gcid": "A" * 40}], profileId="gy-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_guangya_create_dir", lambda profile_id, parent_id="", dir_name="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="guangya mkdir ok", items=[{"fileId": "new-dir-1"}], profileId="gy-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_aliyun_open_live_list", lambda profile_id, parent_file_id="root", limit=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="aliyun list ok", payload={"items": [{"fileId": "file-1"}]}, profileId="ali-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_aliyun_open_live_metadata", lambda profile_id, file_id: SimpleNamespace(ok=True, mode="live", status=200, error="", note="aliyun meta ok", payload={"entry": {"md5": "0123456789abcdef0123456789abcdef"}}, profileId="ali-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_aliyun_open_create_folder", lambda profile_id, parent_file_id="root", dir_name="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="aliyun mkdir ok", payload={"item": {"fileId": "new-dir-1"}}, profileId="ali-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_tianyi_live_list", lambda profile_id, file_id="", page_size=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="189 list ok", payload={"items": [{"fileId": "file-1"}]}, profileId="189-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_tianyi_live_metadata", lambda profile_id, file_id="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="189 meta ok", payload={"entry": {"md5": "0123456789abcdef0123456789abcdef"}}, profileId="189-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_tianyi_create_folder", lambda profile_id, parent_id="", dir_name="": SimpleNamespace(ok=False, mode="unsupported_readonly_share_auth", status=0, error="share_auth_readonly", note="189 mkdir not available on current share auth", payload={"requiredAuth": ["AccessToken", "Signature", "Date"]}, profileId="189-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_baidu_live_list", lambda profile_id, dir_path="/", limit=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="baidu list ok", payload={"items": [{"fileId": "22"}]}, profileId="bd-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_baidu_live_metadata", lambda profile_id, file_id="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="baidu meta ok", payload={"entry": {"md5": "0123456789abcdef0123456789abcdef"}}, profileId="bd-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_baidu_create_dir", lambda profile_id, parent_dir="/", dir_name="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="baidu mkdir ok", payload={"item": {"fileId": "33"}}, profileId="bd-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_123_open_live_list", lambda profile_id, parent_file_id="0", limit=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="123 list ok", payload={"items": [{"fileId": "2"}]}, profileId="123-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_123_open_live_metadata", lambda profile_id, file_id, parent_file_id="0": SimpleNamespace(ok=True, mode="live", status=200, error="", note="123 meta ok", payload={"entry": {"md5": "0123456789abcdef0123456789abcdef"}}, profileId="123-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_123_open_create_folder", lambda profile_id, parent_file_id="0", dir_name="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="123 mkdir ok", payload={"item": {"fileId": "3"}}, profileId="123-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_115_open_live_list", lambda profile_id, cid="0", limit=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="115 list ok", payload={"items": [{"fileId": "file-1"}]}, profileId="115-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_115_open_live_metadata", lambda profile_id, file_id: SimpleNamespace(ok=True, mode="live", status=200, error="", note="115 meta ok", payload={"entry": {"sha1": "0" * 40}}, profileId="115-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_115_open_create_folder", lambda profile_id, parent_id="0", dir_name="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="115 mkdir ok", payload={"item": {"fileId": "new-dir-1"}}, profileId="115-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_xunlei_live_list", lambda profile_id, parent_id="", limit=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="xunlei list ok", payload={"items": [{"fileId": "file-1"}]}, profileId="xl-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_xunlei_live_metadata", lambda profile_id, file_id, parent_id="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="xunlei meta ok", payload={"entry": {"gcid": "A" * 40}}, profileId="xl-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_xunlei_create_folder", lambda profile_id, parent_id="", dir_name="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="xunlei mkdir ok", payload={"item": {"fileId": "new-dir"}}, profileId="xl-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_pikpak_live_list", lambda profile_id, parent_id="", limit=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="pikpak list ok", payload={"items": [{"fileId": "file-1"}]}, profileId="pk-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_pikpak_live_metadata", lambda profile_id, file_id: SimpleNamespace(ok=True, mode="live", status=200, error="", note="pikpak meta ok", payload={"entry": {"gcid": "A" * 40}}, profileId="pk-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_pikpak_create_folder", lambda profile_id, parent_id="", dir_name="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="pikpak mkdir ok", payload={"item": {"fileId": "new-dir"}}, profileId="pk-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_quark_live_list", lambda profile_id, parent_id="0", page_size=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="quark list ok", payload={"items": [{"fileId": "file-1"}]}, profileId="quark-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_quark_live_metadata", lambda profile_id, file_id, parent_id="0": SimpleNamespace(ok=True, mode="live", status=200, error="", note="quark meta ok", payload={"entry": {"md5": "0123456789abcdef0123456789abcdef"}}, profileId="quark-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_quark_create_folder", lambda profile_id, parent_id="0", dir_name="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="quark mkdir ok", payload={"item": {"fileId": "new-dir"}}, profileId="quark-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_uc_live_list", lambda profile_id, parent_id="0", page_size=100: SimpleNamespace(ok=True, mode="live", status=200, error="", note="uc list ok", payload={"items": [{"fileId": "file-1"}]}, profileId="uc-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_uc_live_metadata", lambda profile_id, file_id, parent_id="0": SimpleNamespace(ok=True, mode="live", status=200, error="", note="uc meta ok", payload={"entry": {"md5": "0123456789abcdef0123456789abcdef"}}, profileId="uc-profile")))
        stack.enter_context(patched_attr(provider_live_probe, "fetch_uc_create_folder", lambda profile_id, parent_id="0", dir_name="": SimpleNamespace(ok=True, mode="live", status=200, error="", note="uc mkdir ok", payload={"item": {"fileId": "new-dir"}}, profileId="uc-profile")))

        results["guangya"] = provider_live_probe.run_provider_live_probe("guangya", parent_id="dir-root", file_id="file-1", dir_name="demo")
        results["aliyundrive_open"] = provider_live_probe.run_provider_live_probe("aliyundrive_open", parent_id="root", file_id="file-1", dir_name="demo")
        results["189cloud"] = provider_live_probe.run_provider_live_probe("189cloud", file_id="file-1", dir_name="demo")
        results["baidu_netdisk"] = provider_live_probe.run_provider_live_probe("baidu_netdisk", parent_id="/", file_id="22", dir_name="demo")
        results["123_open"] = provider_live_probe.run_provider_live_probe("123_open", parent_id="0", file_id="2", dir_name="demo")
        results["115_open"] = provider_live_probe.run_provider_live_probe("115_open", parent_id="0", file_id="file-1", dir_name="demo")
        results["xunlei"] = provider_live_probe.run_provider_live_probe("xunlei", parent_id="", file_id="file-1", dir_name="demo")
        results["pikpak"] = provider_live_probe.run_provider_live_probe("pikpak", parent_id="", file_id="file-1", dir_name="demo")
        results["quark"] = provider_live_probe.run_provider_live_probe("quark", parent_id="0", file_id="file-1", dir_name="demo")
        results["uc"] = provider_live_probe.run_provider_live_probe("uc", parent_id="0", file_id="file-1", dir_name="demo")

    with patched_attr(provider_status_matrix, "build_provider_registry", lambda: registry_profiles):
        with patched_attr(provider_status_matrix, "build_provider_research_index", lambda: research_rows):
            with patched_attr(provider_status_matrix, "list_live_validations", lambda: []):
                with patched_attr(provider_status_matrix, "list_provider_live_probes", lambda: saved_probes):
                    matrix = provider_status_matrix.build_status_matrix()

    matrix_rows = {row["providerKey"]: row for row in matrix["items"]}
    return {
        "probeChecks": {key: len(value["checks"]) for key, value in results.items()},
        "matrixRows": {
            key: {
                "list_ready": bool(matrix_rows[key]["list_ready"]),
                "metadata_ready": bool(matrix_rows[key]["metadata_ready"]),
                "create_dir_ready": bool(matrix_rows[key]["create_dir_ready"]),
                "live_probe_ok": bool(matrix_rows[key]["live_probe_ok"]),
            }
            for key in matrix_rows
        },
    }


def main() -> None:
    payload = {
        "guangya": verify_guangya(),
        "aliyundrive_open": verify_aliyun_open(),
        "189cloud": verify_189cloud(),
        "baidu_netdisk": verify_baidu(),
        "123_open": verify_123_open(),
        "115_open": verify_115_open(),
        "xunlei": verify_xunlei(),
        "pikpak": verify_pikpak(),
        "quark": verify_quark(),
        "uc": verify_uc(),
        "probe_and_matrix": verify_probe_and_matrix(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
