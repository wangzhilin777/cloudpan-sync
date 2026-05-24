from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_store import list_profiles


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        configure_data_dir(Path(tmp_dir))
        cmd = [
            str(ROOT / ".venv" / "Scripts" / "python.exe"),
            str(ROOT / "scripts" / "create_auth_profile_stub.py"),
            "--provider-key",
            "aliyundrive_open",
            "--auth-mode",
            "official_oauth",
            "--display-name",
            "aliyun-bootstrap",
            "--token",
            "tok-demo",
            "--set",
            "domainId=domain-demo",
            "--set",
            "driveId=drive-demo",
        ]
        completed = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env={**dict(os.environ), "CLOUDPAN_SYNC_DATA_DIR": tmp_dir},
        )
        payload = json.loads(completed.stdout)
        profiles = list_profiles()
        profile = profiles[0] if profiles else None
        print(
            json.dumps(
                {
                    "written": bool(payload.get("written")),
                    "savedProfileCount": len(profiles),
                    "providerKey": getattr(profile, "providerKey", ""),
                    "authMode": getattr(profile, "authMode", ""),
                    "displayName": getattr(profile, "displayName", ""),
                    "hasDomainId": bool(getattr(profile, "extra", {}).get("domainId") if profile else ""),
                    "hasDriveId": bool(getattr(profile, "extra", {}).get("driveId") if profile else ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
