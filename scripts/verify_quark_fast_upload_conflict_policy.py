from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import quark_fast_upload_live


def main() -> None:
    original_load_profile = quark_fast_upload_live._load_profile_requirements
    original_request_json = quark_fast_upload_live._request_json
    original_fetch_list = quark_fast_upload_live.fetch_quark_live_list

    file_path = ROOT / "tmp" / "verify-quark-conflict.bin"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"quark-conflict")

    request_calls: list[tuple[str, dict[str, object]]] = []

    def fake_load_profile(profile_id: str):
        profile = type("Profile", (), {"profileId": profile_id, "providerKey": "quark", "extra": {}})()
        return profile, "cookie=demo"

    def fake_fetch_list(profile_id: str, parent_id: str = "0", page_size: int = 200):
        return type(
            "ListResult",
            (),
            {
                "ok": True,
                "payload": {"items": [{"name": "demo.bin"}]},
                "status": 200,
                "error": "",
            },
        )()

    def fake_request_json(url: str, method: str, headers: dict[str, str], body: dict[str, object] | None = None):
        request_calls.append((url, dict(body or {})))
        if "upload/pre" in url:
            return 200, {"code": 0, "data": {"task_id": "task-1", "obj_key": "obj/demo.bin", "bucket": "bucket-qk", "upload_id": "upload-1", "upload_url": "https://bucket-qk.example.invalid/obj/demo.bin", "auth_info": {"token": "x"}, "callback": {"callbackUrl": "https://callback.invalid"}}}
        if "update/hash" in url:
            return 200, {"code": 0, "data": {"finish": True, "fid": "file-1"}}
        if "upload/finish" in url:
            return 200, {"code": 0, "data": {"fid": "file-1", "file_name": "demo (1).bin"}}
        return 200, {"code": 0, "data": {}}

    quark_fast_upload_live._load_profile_requirements = fake_load_profile
    quark_fast_upload_live.fetch_quark_live_list = fake_fetch_list
    quark_fast_upload_live._request_json = fake_request_json
    try:
        result = quark_fast_upload_live.upload_quark_fast_file(
            profile_id="quark-profile-1",
            local_path=str(file_path),
            target_name="demo.bin",
            parent_id="0",
            conflict_policy="overwrite_existing",
        )
        payload = result.to_dict()
        print(
            json.dumps(
                {
                    "ok": payload.get("ok"),
                    "mode": payload.get("mode"),
                    "requestedName": next((body.get("file_name") for url, body in request_calls if "upload/pre" in url), ""),
                    "resolvedTargetName": ((payload.get("payload") or {}).get("resolvedTargetName")),
                    "conflictAction": ((payload.get("payload") or {}).get("conflictAction")),
                    "noteHasDowngrade": "downgraded" in str(payload.get("note") or ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        quark_fast_upload_live._load_profile_requirements = original_load_profile
        quark_fast_upload_live.fetch_quark_live_list = original_fetch_list
        quark_fast_upload_live._request_json = original_request_json
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()


if __name__ == "__main__":
    main()
