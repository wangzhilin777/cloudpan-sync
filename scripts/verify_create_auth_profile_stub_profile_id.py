from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SCRIPT_PATH = ROOT / "scripts" / "create_auth_profile_stub.py"
SPEC = importlib.util.spec_from_file_location("create_auth_profile_stub", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
create_auth_profile_stub = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(create_auth_profile_stub)


class FakeProfile:
    def __init__(self) -> None:
        self.profileId = "gy-orphan"
        self.providerKey = "guangya"
        self.authMode = "manual_token"
        self.displayName = "guangya-restore-gy-orphan"
        self.token = "tok-demo"
        self.cookie = ""
        self.extra = {"parentId": "parent-demo"}


def main() -> None:
    original_env = os.environ.get("CLOUDPAN_SYNC_DATA_DIR")
    original_save_profile = create_auth_profile_stub.save_profile

    save_calls: list[dict[str, object]] = []
    fake_profile = FakeProfile()

    with TemporaryDirectory() as tmp_dir:
        os.environ["CLOUDPAN_SYNC_DATA_DIR"] = str(Path(tmp_dir) / ".cloudpan_sync_data")

        def _fake_save_profile(payload, profile_id_override=""):
            save_calls.append({"providerKey": payload.providerKey, "profileIdOverride": profile_id_override})
            return fake_profile

        create_auth_profile_stub.save_profile = _fake_save_profile
        try:
            from contextlib import redirect_stdout
            from io import StringIO

            original_argv = sys.argv[:]
            sys.argv = [
                str(SCRIPT_PATH),
                "--provider-key",
                "guangya",
                "--auth-mode",
                "manual_token",
                "--display-name",
                "guangya-restore-gy-orphan",
                "--profile-id",
                "gy-orphan",
                "--token",
                "tok-demo",
                "--set",
                "parentId=parent-demo",
            ]
            stdout_buffer = StringIO()
            with redirect_stdout(stdout_buffer):
                create_auth_profile_stub.main()
            payload = json.loads(stdout_buffer.getvalue())
        finally:
            sys.argv = original_argv
            if original_env is None:
                os.environ.pop("CLOUDPAN_SYNC_DATA_DIR", None)
            else:
                os.environ["CLOUDPAN_SYNC_DATA_DIR"] = original_env
            create_auth_profile_stub.save_profile = original_save_profile

    print(
        json.dumps(
            {
                "saveProfileCalledWithOverride": save_calls == [{"providerKey": "guangya", "profileIdOverride": "gy-orphan"}],
                "payloadPreservesRequestedProfileId": payload.get("profileId") == "gy-orphan",
                "payloadKeepsProviderAndMode": payload.get("providerKey") == "guangya" and payload.get("authMode") == "manual_token",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
