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
        self.profileId = "aliyun-profile-1"
        self.providerKey = "aliyundrive_open"
        self.authMode = "official_oauth"
        self.displayName = "aliyun-bootstrap"
        self.token = "tok-demo"
        self.cookie = ""
        self.extra = {"domainId": "domain-demo", "driveId": "drive-demo"}


def main() -> None:
    original_env = os.environ.get("CLOUDPAN_SYNC_DATA_DIR")
    original_configure = create_auth_profile_stub.configure_data_dir
    original_save_profile = create_auth_profile_stub.save_profile
    original_refresh = create_auth_profile_stub.refresh_auth_profile_evidence
    original_markdown = create_auth_profile_stub.auth_profile_evidence_to_markdown
    original_remediation_builder = create_auth_profile_stub.build_real_evidence_remediation_bundle
    original_profile_view = create_auth_profile_stub._auth_profile_evidence.__globals__.get("_auth_profile_view")

    configured_dirs: list[str] = []
    fake_profile = FakeProfile()

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        evidence_output = tmp_root / "auth-evidence.md"
        os.environ["CLOUDPAN_SYNC_DATA_DIR"] = str(tmp_root / ".cloudpan_sync_data")

        create_auth_profile_stub.configure_data_dir = lambda path: configured_dirs.append(str(path))
        create_auth_profile_stub.save_profile = lambda payload: fake_profile
        create_auth_profile_stub.refresh_auth_profile_evidence = lambda **kwargs: {
            "profile": {
                "profileId": fake_profile.profileId,
                "providerKey": fake_profile.providerKey,
                "displayName": fake_profile.displayName,
            },
            "summary": {
                "profileReady": True,
                "writeReady": True,
                "validationOk": True,
                "probeOk": True,
                "resolvedParentId": "root-demo",
                "resolvedFileId": "file-demo",
            },
            "latestValidation": {
                "ok": True,
                "summary": "validation ok",
            },
            "latestProbe": {
                "ok": True,
                "summary": "probe ok",
            },
        }
        create_auth_profile_stub.auth_profile_evidence_to_markdown = (
            lambda payload: "# Auth Profile Evidence\n\n- profileId: `aliyun-profile-1`\n- summary: `probe ok`\n"
        )
        create_auth_profile_stub.build_real_evidence_remediation_bundle = lambda: {
            "summary": {},
            "items": [
                {
                    "providerKey": "aliyundrive_open",
                    "profileIds": ["aliyun-profile-1"],
                    "nextStep": "先补齐基础证据，再补 runtime。",
                    "recommendedRefreshEvidenceCommand": r".\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id aliyun-profile-1 --write",
                    "recommendedPostRefreshRuntimeCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider aliyundrive_open --target-profile-id aliyun-profile-1 --target-parent-id root --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\aliyundrive_open-live-evidence",
                    "recommendedOverwriteVariantCommand": r".\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider aliyundrive_open --target-profile-id aliyun-profile-1 --target-parent-id root --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\aliyundrive_open-live-evidence",
                }
            ],
        }
        create_auth_profile_stub._auth_profile_evidence.__globals__["_auth_profile_view"] = lambda profile: {
            "profileId": fake_profile.profileId,
            "providerKey": fake_profile.providerKey,
            "displayName": fake_profile.displayName,
            "profileReady": True,
            "writeReady": True,
            "resolvedParentId": "root-demo",
            "resolvedFileId": "file-demo",
        }

        try:
            from io import StringIO
            from contextlib import redirect_stdout

            original_argv = sys.argv[:]
            sys.argv = [
                str(SCRIPT_PATH),
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
                "--probe",
                "--evidence-output",
                str(evidence_output),
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
            create_auth_profile_stub.configure_data_dir = original_configure
            create_auth_profile_stub.save_profile = original_save_profile
            create_auth_profile_stub.refresh_auth_profile_evidence = original_refresh
            create_auth_profile_stub.auth_profile_evidence_to_markdown = original_markdown
            create_auth_profile_stub.build_real_evidence_remediation_bundle = original_remediation_builder
            if original_profile_view is None:
                create_auth_profile_stub._auth_profile_evidence.__globals__.pop("_auth_profile_view", None)
            else:
                create_auth_profile_stub._auth_profile_evidence.__globals__["_auth_profile_view"] = original_profile_view

        print(
            json.dumps(
                {
                    "configuredDataDirFromEnv": configured_dirs == [str(tmp_root / ".cloudpan_sync_data")],
                    "savedProfileId": payload.get("profileId") == "aliyun-profile-1",
                    "savedProviderKey": payload.get("providerKey") == "aliyundrive_open",
                    "savedAuthMode": payload.get("authMode") == "official_oauth",
                    "savedDisplayName": payload.get("displayName") == "aliyun-bootstrap",
                    "savedExtraFields": dict(payload.get("extra") or {}).get("domainId") == "domain-demo"
                    and dict(payload.get("extra") or {}).get("driveId") == "drive-demo",
                    "probeEvidenceIncluded": dict(payload.get("evidence") or {}).get("summary", {}).get("probeOk") is True
                    and dict(payload.get("evidence") or {}).get("latestProbe", {}).get("summary") == "probe ok",
                    "remediationFollowupIncluded": dict(payload.get("remediation") or {}).get("recommendedPostRefreshRuntimeCommand", "").endswith("tmp\\aliyundrive_open-live-evidence")
                    and dict(payload.get("remediation") or {}).get("recommendedOverwriteVariantCommand", "").endswith("tmp\\aliyundrive_open-live-evidence")
                    and dict(payload.get("remediation") or {}).get("nextStep") == "先补齐基础证据，再补 runtime。",
                    "evidenceOutputWritten": payload.get("evidenceOutput") == str(evidence_output.resolve())
                    and evidence_output.exists()
                    and "# Auth Profile Evidence" in evidence_output.read_text(encoding="utf-8"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
