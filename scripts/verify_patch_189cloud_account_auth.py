from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "patch_189cloud_account_auth.py"


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "189-rem-1",
                        "providerKey": "189cloud",
                        "authMode": "manual_cookie",
                        "displayName": "189-write-smoke",
                        "token": "",
                        "cookie": "",
                        "extra": {"shareCode": "share-demo", "fileId": "root-file"},
                        "status": "invalid",
                        "lastError": "missing_account_level_auth",
                        "createdAt": "2026-05-24T00:00:00+00:00",
                        "updatedAt": "2026-05-24T00:00:00+00:00",
                    }
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        raw_text = "\n".join(
            [
                "POST https://cloud.189.cn/api/open/file/createFolder.action",
                "AccessToken: access-token-demo",
                "Signature: sig-demo",
                "Date: Sat, 24 May 2026 00:00:00 GMT",
            ]
        )

        command = [
            sys.executable,
            str(SCRIPT),
            "--profile-id",
            "189-rem-1",
            "--raw-text",
            raw_text,
            "--write",
            "--data-dir",
            str(data_dir),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=True)
        payload = json.loads(completed.stdout)
        saved_profiles = json.loads((data_dir / "auth_profiles.json").read_text(encoding="utf-8"))
        saved = saved_profiles[0]
        patch_189cloud_account_auth_flow_matches_expected_fields = (
            (payload.get("extracted") or {}).get("accessToken") == "access-token-demo"
            and (payload.get("extracted") or {}).get("signature") == "sig-demo"
            and (payload.get("extracted") or {}).get("date") == "Sat, 24 May 2026 00:00:00 GMT"
            and ((payload.get("result") or {}).get("matchedCount")) == 1
            and ((payload.get("result") or {}).get("writtenCount")) == 1
            and (saved.get("extra") or {}).get("shareCode") == "share-demo"
            and (saved.get("extra") or {}).get("fileId") == "root-file"
            and (saved.get("extra") or {}).get("accessToken") == "access-token-demo"
            and (saved.get("extra") or {}).get("signature") == "sig-demo"
            and (saved.get("extra") or {}).get("date") == "Sat, 24 May 2026 00:00:00 GMT"
        )

        print(
            json.dumps(
                {
                    "extracted": payload.get("extracted"),
                    "matchedCount": ((payload.get("result") or {}).get("matchedCount")),
                    "writtenCount": ((payload.get("result") or {}).get("writtenCount")),
                    "savedExtra": saved.get("extra"),
                    "patch189cloudAccountAuthFlowMatchesExpectedFields": patch_189cloud_account_auth_flow_matches_expected_fields,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
