from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import webapp


def main() -> None:
    app = webapp.create_app()
    client = TestClient(app)
    client.post("/api/login", json={"password": webapp.ADMIN_PASSWORD})

    quark_raw = """
cookie: sid=abc123; kps=xyz789
https://pan.quark.cn/s/abcd1234?pwdId=pwd-demo-1&passcode=7788
"""
    guangya_raw = """
{
  "token": "Bearer gy-token-live-001",
  "parentId": "gy-parent-001",
  "did": "device-gy-1",
  "dt": "dt-gy-1"
}
"""
    tianyi_raw = """
curl 'https://cloud.189.cn/api/open/file/createFolder.action' \
  -H 'AccessToken: tianyi-token-1' \
  -H 'Signature: sig-189-1' \
  -H 'Date: Tue, 20 May 2026 12:00:00 GMT'
https://cloud.189.cn/web/share?shareCode=share-189-1&accessCode=2468
"""

    quark = client.post("/api/auth/capture/parse", json={"providerKey": "quark", "rawText": quark_raw}).json()
    guangya = client.post("/api/auth/capture/parse", json={"providerKey": "guangya", "rawText": guangya_raw}).json()
    tianyi = client.post("/api/auth/capture/parse", json={"providerKey": "189cloud", "rawText": tianyi_raw}).json()

    print(
        json.dumps(
            {
                "quarkParsesCookieAndShareHints": (
                    quark.get("status") == "capture_parsed"
                    and quark.get("suggestedProfile", {}).get("authMode") == "manual_cookie"
                    and quark.get("suggestedProfile", {}).get("cookie") == "sid=abc123; kps=xyz789"
                    and quark.get("suggestedProfile", {}).get("extra", {}).get("pwdId") == "pwd-demo-1"
                    and quark.get("suggestedProfile", {}).get("extra", {}).get("passcode") == "7788"
                    and "cookie" in (quark.get("appliedFieldNames") or [])
                ),
                "guangyaParsesTokenParentAndDeviceHints": (
                    guangya.get("status") == "capture_parsed"
                    and guangya.get("suggestedProfile", {}).get("authMode") == "manual_token"
                    and guangya.get("suggestedProfile", {}).get("token") == "gy-token-live-001"
                    and guangya.get("suggestedProfile", {}).get("extra", {}).get("parentId") == "gy-parent-001"
                    and guangya.get("suggestedProfile", {}).get("extra", {}).get("did") == "device-gy-1"
                    and guangya.get("suggestedProfile", {}).get("extra", {}).get("dt") == "dt-gy-1"
                    and guangya.get("profileReady") is True
                ),
                "tianyiParsesShareAndWriteHeaders": (
                    tianyi.get("status") == "capture_parsed"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("shareCode") == "share-189-1"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("accessCode") == "2468"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("accessToken") == "tianyi-token-1"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("signature") == "sig-189-1"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("date") == "Tue, 20 May 2026 12:00:00 GMT"
                ),
                "authCaptureParseFlowMatchesExpectedProviders": (
                    quark.get("status") == "capture_parsed"
                    and quark.get("suggestedProfile", {}).get("authMode") == "manual_cookie"
                    and quark.get("suggestedProfile", {}).get("cookie") == "sid=abc123; kps=xyz789"
                    and quark.get("suggestedProfile", {}).get("extra", {}).get("pwdId") == "pwd-demo-1"
                    and quark.get("suggestedProfile", {}).get("extra", {}).get("passcode") == "7788"
                    and "cookie" in (quark.get("appliedFieldNames") or [])
                    and guangya.get("status") == "capture_parsed"
                    and guangya.get("suggestedProfile", {}).get("authMode") == "manual_token"
                    and guangya.get("suggestedProfile", {}).get("token") == "gy-token-live-001"
                    and guangya.get("suggestedProfile", {}).get("extra", {}).get("parentId") == "gy-parent-001"
                    and guangya.get("suggestedProfile", {}).get("extra", {}).get("did") == "device-gy-1"
                    and guangya.get("suggestedProfile", {}).get("extra", {}).get("dt") == "dt-gy-1"
                    and guangya.get("profileReady") is True
                    and tianyi.get("status") == "capture_parsed"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("shareCode") == "share-189-1"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("accessCode") == "2468"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("accessToken") == "tianyi-token-1"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("signature") == "sig-189-1"
                    and tianyi.get("suggestedProfile", {}).get("extra", {}).get("date") == "Tue, 20 May 2026 12:00:00 GMT"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
