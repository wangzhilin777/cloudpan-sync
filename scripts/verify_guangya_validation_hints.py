from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import auth_live_validate
from cloudpan_sync import guangya_live


@contextmanager
def patched_attr(target: object, name: str, value: object):
    original = getattr(target, name)
    setattr(target, name, value)
    try:
        yield
    finally:
        setattr(target, name, original)


def main() -> None:
    alias_profile = SimpleNamespace(
        profileId="gy-alias-1",
        providerKey="guangya",
        displayName="gy-alias",
        token="",
        extra={
            "authorization": "tok-demo",
            "parentFileId": "parent-demo",
            "file_id": "file-demo",
            "did": "did-demo",
            "dt": "dt-demo",
        },
    )
    missing_profile = SimpleNamespace(
        profileId="gy-missing-1",
        providerKey="guangya",
        displayName="gy-missing",
        token="tok-demo",
        extra={},
    )

    def fake_probe_for_alias(profile: object, parent_id: str = "", file_id: str = "", page_size: int = 100, dir_name: str = ""):
        return {
            "ok": True,
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "mode": "live",
            "summary": "alias probe ok",
            "checks": [
                {"kind": "list", "ok": True, "status": 200, "error": "", "note": "alias list ok"}
            ],
        }

    def fake_probe_for_missing(profile: object, parent_id: str = "", file_id: str = "", page_size: int = 100, dir_name: str = ""):
        return {
            "ok": False,
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "mode": "profile_incomplete",
            "summary": "missing parent",
            "checks": [
                {"kind": "list", "ok": False, "status": 0, "error": "missing_parent_id", "note": "Guangya live list requires parentId in request or auth profile extra.parentId."}
            ],
        }

    with patched_attr(auth_live_validate, "run_provider_live_probe_for_profile", fake_probe_for_alias):
        alias_validation = auth_live_validate.validate_profile_object(alias_profile)

    with patched_attr(auth_live_validate, "run_provider_live_probe_for_profile", fake_probe_for_missing):
        missing_validation = auth_live_validate.validate_profile_object(missing_profile)

    with patched_attr(guangya_live, "get_profile", lambda profile_id: alias_profile if profile_id == alias_profile.profileId else None):
        captured = {}

        class FakeResponse:
            status = 200

            def read(self) -> bytes:
                return json.dumps({"data": {"records": []}}, ensure_ascii=False).encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(request, timeout: int = 15):
            captured["headers"] = dict(request.headers)
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse()

        with patched_attr(guangya_live, "urlopen", fake_urlopen):
            live_result = guangya_live.fetch_guangya_live_list(alias_profile.profileId)

    lower_headers = {str(key).lower(): value for key, value in (captured.get("headers", {}) or {}).items()}

    print(
        json.dumps(
            {
                "aliasValidation": {
                    "parentId": alias_validation.get("parentId"),
                    "fileId": alias_validation.get("fileId"),
                    "requiredFieldHints": alias_validation.get("requiredFieldHints"),
                },
                "missingValidation": {
                    "error": missing_validation.get("error"),
                    "requiredFieldHints": missing_validation.get("requiredFieldHints"),
                    "riskHint": missing_validation.get("riskHint"),
                },
                "guangyaLiveAlias": {
                    "ok": live_result.ok,
                    "parentId": live_result.parentId,
                    "requestParentId": captured.get("body", {}).get("parentId"),
                    "hasDid": bool(lower_headers.get("did")),
                    "hasDt": bool(lower_headers.get("dt")),
                    "authHeader": lower_headers.get("authorization", ""),
                },
                "guangyaValidationHintsFlowMatchesExpectedAliases": (
                    alias_validation.get("parentId") == "parent-demo"
                    and alias_validation.get("fileId") == "file-demo"
                    and list(alias_validation.get("requiredFieldHints") or []) == []
                    and missing_validation.get("error") == "missing_parent_id"
                    and "extra.parentId" in list(missing_validation.get("requiredFieldHints") or [])
                    and "aliases: parent_id/parentFileId/dirId/pid" in list(missing_validation.get("requiredFieldHints") or [])
                    and "optional extra.did" in list(missing_validation.get("requiredFieldHints") or [])
                    and "optional extra.dt" in list(missing_validation.get("requiredFieldHints") or [])
                    and "parentId" in str(missing_validation.get("riskHint") or "")
                    and live_result.ok is True
                    and live_result.parentId == "parent-demo"
                    and captured.get("body", {}).get("parentId") == "parent-demo"
                    and bool(lower_headers.get("did"))
                    and bool(lower_headers.get("dt"))
                    and lower_headers.get("authorization", "") == "Bearer tok-demo"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
