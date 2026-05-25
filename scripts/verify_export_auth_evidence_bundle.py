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

from cloudpan_sync.auth_profile_evidence import auth_evidence_bundle_to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_auth_evidence_bundle.py"
SPEC = importlib.util.spec_from_file_location("export_auth_evidence_bundle", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "summary": {
            "profileCount": 2,
            "profileReadyCount": 1,
            "writeReadyCount": 1,
            "validationOkCount": 1,
            "probeOkCount": 1,
        },
        "items": [
            {
                "profile": {
                    "profileId": "gy-1",
                    "providerKey": "guangya",
                    "displayName": "Guangya Primary",
                },
                "summary": {
                    "profileReady": True,
                    "writeReady": True,
                    "validationOk": True,
                    "probeOk": True,
                    "resolvedParentId": "root-gy",
                    "resolvedFileId": "file-gy",
                },
                "latestValidation": {
                    "summary": "cookie refresh succeeded",
                },
                "latestProbe": {
                    "summary": "list/create_dir checks passed",
                },
            },
            {
                "profile": {
                    "profileId": "189-share",
                    "providerKey": "189cloud",
                    "displayName": "189 Share Profile",
                    "missingFieldHints": ["accessToken", "sessionKey"],
                    "placeholderFieldHints": ["token looks like placeholder data; replace tok-demo with a real token"],
                    "placeholderSecretFieldHints": ["token"],
                    "writeMissingFieldHints": ["signature", "date"],
                    "writeBlockerNote": "当前 189Cloud share 档案仍为只读。",
                },
                "summary": {
                    "profileReady": False,
                    "writeReady": False,
                    "validationOk": False,
                    "probeOk": False,
                    "resolvedParentId": "share-parent",
                    "resolvedFileId": "",
                },
                "latestValidation": {
                    "summary": "share auth readonly",
                },
                "latestProbe": {
                    "summary": "create_dir probe blocked by readonly auth",
                },
            },
        ],
    }

    original_root = export_script.ROOT
    original_builder = export_script.build_auth_evidence_bundle
    original_renderer = export_script.auth_evidence_bundle_to_markdown
    original_list_profiles = export_script.list_profiles
    original_profile_view_builder = export_script._auth_profile_view

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.list_profiles = lambda: ["gy-1", "189-share"]
        export_script._auth_profile_view = lambda profile: {"profileId": str(profile)}
        export_script.build_auth_evidence_bundle = lambda profiles, profile_view_builder: synthetic_payload
        export_script.auth_evidence_bundle_to_markdown = auth_evidence_bundle_to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.build_auth_evidence_bundle = original_builder
            export_script.auth_evidence_bundle_to_markdown = original_renderer
            export_script.list_profiles = original_list_profiles
            export_script._auth_profile_view = original_profile_view_builder

        output_path = tmp_root / "docs" / "08-AUTH_EVIDENCE_BUNDLE.md"
        markdown = output_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "exportedFileExists": True,
                "exportedHasTitle": "# Auth Evidence Bundle" in markdown,
                "exportedHasSummary": "- profileCount: `2`" in markdown
                and "- profileReadyCount: `1`" in markdown
                and "- writeReadyCount: `1`" in markdown
                and "- validationOkCount: `1`" in markdown
                and "- probeOkCount: `1`" in markdown,
                "exportedHasGuangyaProfile": "### Guangya Primary [guangya]" in markdown
                and "- profileId: `gy-1`" in markdown
                and "- resolvedParentId: `root-gy`" in markdown
                and "- latestValidation: `cookie refresh succeeded`" in markdown
                and "- latestProbe: `list/create_dir checks passed`" in markdown,
                "exportedHas189HintsAndBlocker": "### 189 Share Profile [189cloud]" in markdown
                and "- missingFieldHints: `accessToken, sessionKey`" in markdown
                and "- placeholderFieldHints: `token looks like placeholder data; replace tok-demo with a real token`" in markdown
                and "- placeholderSecretFieldHints: `token`" in markdown
                and "- writeMissingFieldHints: `signature, date`" in markdown
                and "- writeBlockerNote: 当前 189Cloud share 档案仍为只读。" in markdown
                and "- latestValidation: `share auth readonly`" in markdown
                and "- latestProbe: `create_dir probe blocked by readonly auth`" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
