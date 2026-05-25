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
    def __init__(self, profile_id: str, provider_key: str, auth_mode: str, display_name: str, token: str, cookie: str, extra: dict[str, str]) -> None:
        self.profileId = profile_id
        self.providerKey = provider_key
        self.authMode = auth_mode
        self.displayName = display_name
        self.token = token
        self.cookie = cookie
        self.extra = extra


def _run_with(argv: list[str], save_calls: list[dict[str, object]]) -> dict[str, object]:
    from contextlib import redirect_stdout
    from io import StringIO

    original_argv = sys.argv[:]
    sys.argv = argv
    stdout_buffer = StringIO()
    with redirect_stdout(stdout_buffer):
        create_auth_profile_stub.main()
    sys.argv = original_argv
    return json.loads(stdout_buffer.getvalue())


def main() -> None:
    original_env = os.environ.get("CLOUDPAN_SYNC_DATA_DIR")
    original_save_profile = create_auth_profile_stub.save_profile
    original_remediation_builder = create_auth_profile_stub.build_real_evidence_remediation_bundle
    original_runtime_orphan_builder = create_auth_profile_stub.build_runtime_orphan_recovery
    original_refresh = create_auth_profile_stub.refresh_auth_profile_evidence
    original_profile_view = create_auth_profile_stub._auth_profile_evidence.__globals__.get("_auth_profile_view")

    save_calls: list[dict[str, object]] = []

    with TemporaryDirectory() as tmp_dir:
        os.environ["CLOUDPAN_SYNC_DATA_DIR"] = str(Path(tmp_dir) / ".cloudpan_sync_data")

        def _fake_save_profile(payload, profile_id_override=""):
            save_calls.append(
                {
                    "providerKey": payload.providerKey,
                    "authMode": payload.authMode,
                    "displayName": payload.displayName,
                    "token": payload.token,
                    "cookie": payload.cookie,
                    "extra": dict(payload.extra or {}),
                    "profileIdOverride": profile_id_override,
                }
            )
            return FakeProfile(
                profile_id=str(profile_id_override or "generated-profile"),
                provider_key=payload.providerKey,
                auth_mode=payload.authMode,
                display_name=payload.displayName,
                token=payload.token,
                cookie=payload.cookie,
                extra=dict(payload.extra or {}),
            )

        create_auth_profile_stub.save_profile = _fake_save_profile
        create_auth_profile_stub.refresh_auth_profile_evidence = lambda **kwargs: {
            "profile": {
                "profileId": str(kwargs.get("profile").profileId),
                "providerKey": str(kwargs.get("profile").providerKey),
            },
            "summary": {
                "probeOk": True,
            },
            "latestProbe": {
                "ok": True,
                "summary": "probe ok",
            },
        }
        create_auth_profile_stub._auth_profile_evidence.__globals__["_auth_profile_view"] = lambda profile: {
            "profileId": str(profile.profileId),
            "providerKey": str(profile.providerKey),
            "displayName": str(profile.displayName),
        }
        create_auth_profile_stub.build_real_evidence_remediation_bundle = lambda: {
            "summary": {},
            "items": [
                {
                    "providerKey": "aliyundrive_open",
                    "recommendedPrimaryCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe",
                }
            ],
        }
        create_auth_profile_stub.build_runtime_orphan_recovery = lambda: {
            "summary": {},
            "items": [
                {
                    "providerKey": "guangya",
                    "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-live-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe",
                }
            ],
        }

        try:
            remediation_payload = _run_with(
                [
                    str(SCRIPT_PATH),
                    "--from-remediation-provider",
                    "aliyundrive_open",
                ],
                save_calls,
            )
            orphan_payload = _run_with(
                [
                    str(SCRIPT_PATH),
                    "--from-runtime-orphan-provider",
                    "guangya",
                ],
                save_calls,
            )
        finally:
            if original_env is None:
                os.environ.pop("CLOUDPAN_SYNC_DATA_DIR", None)
            else:
                os.environ["CLOUDPAN_SYNC_DATA_DIR"] = original_env
            create_auth_profile_stub.save_profile = original_save_profile
            create_auth_profile_stub.build_real_evidence_remediation_bundle = original_remediation_builder
            create_auth_profile_stub.build_runtime_orphan_recovery = original_runtime_orphan_builder
            create_auth_profile_stub.refresh_auth_profile_evidence = original_refresh
            if original_profile_view is None:
                create_auth_profile_stub._auth_profile_evidence.__globals__.pop("_auth_profile_view", None)
            else:
                create_auth_profile_stub._auth_profile_evidence.__globals__["_auth_profile_view"] = original_profile_view

    print(
        json.dumps(
            {
                "remediationDefaultsResolved": remediation_payload.get("providerKey") == "aliyundrive_open"
                and remediation_payload.get("authMode") == "official_oauth"
                and remediation_payload.get("displayName") == "aliyun-bootstrap"
                and dict(remediation_payload.get("extra") or {}).get("domainId") == "YOUR_DOMAIN_ID"
                and dict(remediation_payload.get("extra") or {}).get("driveId") == "YOUR_DRIVE_ID"
                and remediation_payload.get("defaultsSource") == "remediation:recommendedPrimaryCommand",
                "runtimeOrphanDefaultsResolved": orphan_payload.get("profileId") == "gy-live-1"
                and orphan_payload.get("providerKey") == "guangya"
                and orphan_payload.get("authMode") == "manual_token"
                and orphan_payload.get("displayName") == "guangya-restore-gy-live-1"
                and dict(orphan_payload.get("extra") or {}).get("parentId") == "YOUR_REAL_PARENT_ID"
                and orphan_payload.get("defaultsSource") == "runtime_orphan:recommendedCreateCommand",
                "saveCallsKeepResolvedDefaults": save_calls == [
                    {
                        "providerKey": "aliyundrive_open",
                        "authMode": "official_oauth",
                        "displayName": "aliyun-bootstrap",
                        "token": "YOUR_TOKEN",
                        "cookie": "",
                        "extra": {"domainId": "YOUR_DOMAIN_ID", "driveId": "YOUR_DRIVE_ID"},
                        "profileIdOverride": "",
                    },
                    {
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "guangya-restore-gy-live-1",
                        "token": "YOUR_TOKEN",
                        "cookie": "",
                        "extra": {"parentId": "YOUR_REAL_PARENT_ID"},
                        "profileIdOverride": "gy-live-1",
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
