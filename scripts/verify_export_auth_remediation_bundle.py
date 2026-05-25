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

from cloudpan_sync.auth_profile_remediation import auth_remediation_bundle_to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_auth_remediation_bundle.py"
SPEC = importlib.util.spec_from_file_location("export_auth_remediation_bundle", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "summary": {
            "profileCount": 3,
            "readyCount": 1,
            "needsFixCount": 2,
            "writeReadyCount": 1,
            "writeNeedsFixCount": 2,
            "needsSecretRefreshCount": 1,
        },
        "items": [
            {
                "profileId": "gy-1",
                "providerKey": "guangya",
                "displayName": "Guangya Primary",
                "profileReady": True,
                "writeReady": True,
                "resolvedParentId": "root-gy",
                "resolvedFileId": "file-gy",
                "missingFieldHints": [],
                "writeMissingFieldHints": [],
                "writeBlockerNote": "",
                "recommendedPatchCommand": "",
            },
            {
                "profileId": "ali-1",
                "providerKey": "aliyundrive_open",
                "displayName": "Aliyun Open",
                "profileReady": False,
                "writeReady": True,
                "resolvedParentId": "",
                "resolvedFileId": "",
                "missingFieldHints": ["domainId", "driveId"],
                "placeholderFieldHints": ["token looks like placeholder data; replace tok-demo with a real Aliyun OAuth token"],
                "placeholderSecretFieldHints": ["token"],
                "needsSecretRefresh": True,
                "writeMissingFieldHints": [],
                "writeBlockerNote": "",
                "recommendedPatchCommand": "",
                "recommendedRecreateProbeCommand": ".\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name Aliyun Open --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe",
            },
            {
                "profileId": "189-share",
                "providerKey": "189cloud",
                "displayName": "189 Share Profile",
                "profileReady": False,
                "writeReady": False,
                "resolvedParentId": "share-parent",
                "resolvedFileId": "",
                "missingFieldHints": ["accessToken"],
                "writeMissingFieldHints": ["signature", "date"],
                "writeBlockerNote": "当前 189Cloud share 档案仍为只读。",
                "recommendedPatchCommand": ".\\.venv\\Scripts\\python.exe scripts\\patch_189cloud_account_auth.py --profile-id 189-share --raw-file captured_189_headers.txt --write --revalidate",
            },
        ],
    }

    original_root = export_script.ROOT
    original_builder = export_script.build_auth_remediation_bundle
    original_renderer = export_script.auth_remediation_bundle_to_markdown
    original_list_profiles = export_script.list_profiles
    original_profile_view_builder = export_script._auth_profile_view

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.list_profiles = lambda: ["gy-1", "ali-1", "189-share"]
        export_script._auth_profile_view = lambda profile: {"profileId": str(profile)}
        export_script.build_auth_remediation_bundle = lambda profile_views: synthetic_payload
        export_script.auth_remediation_bundle_to_markdown = auth_remediation_bundle_to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.build_auth_remediation_bundle = original_builder
            export_script.auth_remediation_bundle_to_markdown = original_renderer
            export_script.list_profiles = original_list_profiles
            export_script._auth_profile_view = original_profile_view_builder

        output_path = tmp_root / "docs" / "09-AUTH_REMEDIATION_GUIDE.md"
        markdown = output_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "exportedFileExists": True,
                "exportedHasTitle": "# 授权补救指南 / Auth Remediation Guide" in markdown,
                "exportedHasSummary": "- profileCount: `3`" in markdown
                and "- readyCount: `1`" in markdown
                and "- needsFixCount: `2`" in markdown
                and "- writeReadyCount: `1`" in markdown
                and "- writeNeedsFixCount: `2`" in markdown
                and "- needsSecretRefreshCount: `1`" in markdown,
                "exportedHasAliyunRecreateProbeCommand": "### Aliyun Open [aliyundrive_open]" in markdown
                and "- missingFieldHints: `domainId, driveId`" in markdown
                and "- placeholderFieldHints: `token looks like placeholder data; replace tok-demo with a real Aliyun OAuth token`" in markdown
                and "- placeholderSecretFieldHints: `token`" in markdown
                and "- recommendedRecreateProbeCommand: `.\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name Aliyun Open --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe`"
                in markdown,
                "exportedHas189ReadonlyDetails": "### 189 Share Profile [189cloud]" in markdown
                and "- writeMissingFieldHints: `signature, date`" in markdown
                and "- writeBlockerNote: 当前 189Cloud share 档案仍为只读。" in markdown
                and "- recommendedPatchCommand: `.\\.venv\\Scripts\\python.exe scripts\\patch_189cloud_account_auth.py --profile-id 189-share --raw-file captured_189_headers.txt --write --revalidate`"
                in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
