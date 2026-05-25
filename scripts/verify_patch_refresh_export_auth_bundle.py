from __future__ import annotations

import importlib.util
import json
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import auth_profile_evidence
from cloudpan_sync.auth_profile_patch import configure_data_dir

SCRIPT_PATH = ROOT / "scripts" / "patch_refresh_export_auth_bundle.py"
SPEC = importlib.util.spec_from_file_location("patch_refresh_export_auth_bundle", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
patch_refresh_export_auth_bundle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patch_refresh_export_auth_bundle)


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "auth_profiles.json").write_text(
            json.dumps(
                [
                    {
                        "profileId": "gy-batch-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "smoke-guangya",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {},
                        "status": "invalid",
                        "lastError": "missing_parent_id",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                    {
                        "profileId": "gy-batch-2",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "risk-smoke-guangya",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {},
                        "status": "invalid",
                        "lastError": "missing_parent_id",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                    {
                        "profileId": "ali-batch-1",
                        "providerKey": "aliyundrive_open",
                        "authMode": "manual_token",
                        "displayName": "other-provider",
                        "token": "ali_tok",
                        "cookie": "",
                        "extra": {"driveId": "drive-1"},
                        "status": "verified",
                        "lastError": "",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        configure_data_dir(data_dir)

        original_refresh_bundle = auth_profile_evidence.refresh_auth_evidence_bundle
        original_markdown = auth_profile_evidence.auth_evidence_bundle_to_markdown

        def fake_refresh_auth_evidence_bundle(*, profiles: list[object], profile_view_builder, page_size: int = 100, dir_name: str = "", persist: bool = True):
            items = []
            for profile in profiles:
                view = profile_view_builder(profile)
                items.append(
                    {
                        "profile": view,
                        "latestValidation": {"ok": True, "summary": "validation ok"},
                        "latestProbe": {"ok": True, "summary": "probe ok"},
                        "summary": {
                            "profileReady": True,
                            "validationOk": True,
                            "probeOk": True,
                            "resolvedParentId": str(view.get("resolvedParentId") or ""),
                            "resolvedFileId": str(view.get("resolvedFileId") or ""),
                        },
                    }
                )
            return {
                "summary": {
                    "profileCount": len(items),
                    "profileReadyCount": len(items),
                    "validationOkCount": len(items),
                    "probeOkCount": len(items),
                },
                "items": items,
            }

        def fake_markdown(payload: dict[str, object]) -> str:
            return "# Auth Evidence Bundle\n\n- fake: `true`\n"

        auth_profile_evidence.refresh_auth_evidence_bundle = fake_refresh_auth_evidence_bundle
        auth_profile_evidence.auth_evidence_bundle_to_markdown = fake_markdown
        patch_refresh_export_auth_bundle.refresh_auth_evidence_bundle = fake_refresh_auth_evidence_bundle
        patch_refresh_export_auth_bundle.auth_evidence_bundle_to_markdown = fake_markdown
        try:
            output_path = data_dir / "bundle.md"
            stdout_buffer = io.StringIO()
            with redirect_stdout(stdout_buffer):
                patch_refresh_export_auth_bundle.main(
                    [
                        "--provider-key",
                        "guangya",
                        "--display-name-contains",
                        "smoke",
                        "--set",
                        "parentId=dir-100",
                        "--set",
                        "fileId=file-9",
                        "--write",
                        "--data-dir",
                        str(data_dir),
                        "--bundle-output",
                        str(output_path),
                    ]
                )
        finally:
            auth_profile_evidence.refresh_auth_evidence_bundle = original_refresh_bundle
            auth_profile_evidence.auth_evidence_bundle_to_markdown = original_markdown
            patch_refresh_export_auth_bundle.refresh_auth_evidence_bundle = original_refresh_bundle
            patch_refresh_export_auth_bundle.auth_evidence_bundle_to_markdown = original_markdown

        profiles = json.loads((data_dir / "auth_profiles.json").read_text(encoding="utf-8"))
        payload = json.loads(stdout_buffer.getvalue())
        guangya_profiles = [row for row in profiles if row.get("providerKey") == "guangya"]
        untouched_profiles = [row for row in profiles if row.get("providerKey") != "guangya"]
        print(
            json.dumps(
                {
                    "patchedCount": len(guangya_profiles),
                    "allMatchedHaveParentId": all((row.get("extra") or {}).get("parentId") == "dir-100" for row in guangya_profiles),
                    "allMatchedHaveFileId": all((row.get("extra") or {}).get("fileId") == "file-9" for row in guangya_profiles),
                    "nonMatchedUntouched": all((row.get("extra") or {}).get("parentId", "") == "" for row in untouched_profiles)
                    and all((row.get("extra") or {}).get("fileId", "") == "" for row in untouched_profiles),
                    "bundleFileExists": output_path.exists(),
                    "bundleHasTitle": "# Auth Evidence Bundle" in output_path.read_text(encoding="utf-8"),
                    "jsonHasProfileIds": payload.get("profileIds") == ["gy-batch-1", "gy-batch-2"],
                    "jsonHasBundleSummary": dict(payload.get("bundleSummary") or {}).get("profileCount") == 2
                    and dict(payload.get("bundleSummary") or {}).get("profileReadyCount") == 2
                    and dict(payload.get("bundleSummary") or {}).get("validationOkCount") == 2
                    and dict(payload.get("bundleSummary") or {}).get("probeOkCount") == 2,
                    "jsonHasBundleOutput": payload.get("bundleOutput") == str(output_path.resolve()),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
