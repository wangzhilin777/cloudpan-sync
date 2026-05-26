from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load script module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    patch_and_probe = _load_module("patch_and_probe_auth_profile", ROOT / "scripts" / "patch_and_probe_auth_profile.py")
    runtime_probe = _load_module("create_runtime_probe_task", ROOT / "scripts" / "create_runtime_probe_task.py")
    live_upload = _load_module("create_live_upload_task", ROOT / "scripts" / "create_live_upload_task.py")
    fast_candidate = _load_module("create_fast_upload_candidate_task", ROOT / "scripts" / "create_fast_upload_candidate_task.py")

    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "gy-restored-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "guangya-restored",
                        "token": "YOUR_TOKEN",
                        "cookie": "",
                        "extra": {"parentId": "YOUR_REAL_PARENT_ID"},
                        "status": "unknown",
                        "lastError": "",
                        "createdAt": "2026-05-26T00:00:00+00:00",
                        "updatedAt": "2026-05-26T00:00:00+00:00",
                    },
                    {
                        "profileId": "pikpak-restored-1",
                        "providerKey": "pikpak",
                        "authMode": "manual_token",
                        "displayName": "pikpak-restored",
                        "token": "YOUR_TOKEN",
                        "cookie": "",
                        "extra": {"deviceId": "YOUR_DEVICE_ID"},
                        "status": "unknown",
                        "lastError": "",
                        "createdAt": "2026-05-26T00:00:00+00:00",
                        "updatedAt": "2026-05-26T00:00:00+00:00",
                    },
                    {
                        "profileId": "uc-restored-1",
                        "providerKey": "uc",
                        "authMode": "manual_cookie",
                        "displayName": "uc-restored",
                        "token": "",
                        "cookie": "YOUR_COOKIE",
                        "extra": {"pwdId": "YOUR_SHARE_PWD_ID"},
                        "status": "unknown",
                        "lastError": "",
                        "createdAt": "2026-05-26T00:00:00+00:00",
                        "updatedAt": "2026-05-26T00:00:00+00:00",
                    },
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        configure_data_dir(data_dir)

        empty_builder = lambda: {"summary": {}, "items": []}
        patch_and_probe.build_runtime_orphan_recovery = empty_builder
        runtime_probe.build_runtime_orphan_recovery = empty_builder
        live_upload.build_runtime_orphan_recovery = empty_builder
        fast_candidate.build_runtime_orphan_recovery = empty_builder

        patch_defaults = patch_and_probe._defaults_from_runtime_orphan_profile("gy-restored-1")
        runtime_defaults = runtime_probe._defaults_from_runtime_orphan_profile("gy-restored-1")
        live_defaults = live_upload._defaults_from_runtime_orphan_profile("pikpak-restored-1")
        fast_defaults = fast_candidate._defaults_from_runtime_orphan_profile("uc-restored-1")
        missing_patch_defaults = patch_and_probe._defaults_from_runtime_orphan_profile("missing-restored")

        print(
            json.dumps(
                {
                    "patchFallbackResolved": patch_defaults.get("profileId") == "gy-restored-1"
                    and patch_defaults.get("write") is True
                    and patch_defaults.get("source") == "runtime_orphan:restored_profile",
                    "runtimeProbeFallbackResolved": runtime_defaults.get("targetProfileId") == "gy-restored-1"
                    and runtime_defaults.get("targetProvider") == "guangya"
                    and runtime_defaults.get("source") == "runtime_orphan:restored_profile",
                    "liveUploadFallbackResolved": live_defaults.get("targetProfileId") == "pikpak-restored-1"
                    and live_defaults.get("targetProvider") == "pikpak"
                    and live_defaults.get("source") == "runtime_orphan:restored_profile",
                    "fastCandidateFallbackResolved": fast_defaults.get("targetProfileId") == "uc-restored-1"
                    and fast_defaults.get("targetProvider") == "uc"
                    and fast_defaults.get("source") == "runtime_orphan:restored_profile",
                    "missingStillEmpty": missing_patch_defaults == {},
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
