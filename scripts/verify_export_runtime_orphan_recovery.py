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

from cloudpan_sync.runtime_orphan_recovery import runtime_orphan_recovery_to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_runtime_orphan_recovery.py"
SPEC = importlib.util.spec_from_file_location("export_runtime_orphan_recovery", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "generatedAt": "2026-05-25T00:00:00+00:00",
        "summary": {
            "providerCount": 2,
            "orphanProfileCount": 2,
            "runtimeSampleCount": 2,
            "providersWithSavedProfiles": 1,
            "providersWithoutSavedProfiles": 1,
            "orphanProviders": ["guangya", "uc"],
            "orphanProfiles": ["gy-orphan", "uc-orphan"],
            "providersWithSavedProfilesList": ["guangya"],
            "providersWithoutSavedProfilesList": ["uc"],
            "recommendedBatchDryRunCommand": r".\.venv\Scripts\python.exe scripts\recreate_runtime_orphan_stubs.py",
            "recommendedBatchWriteMissingCommand": r".\.venv\Scripts\python.exe scripts\recreate_runtime_orphan_stubs.py --write",
            "recommendedBatchOverwriteExistingCommand": r".\.venv\Scripts\python.exe scripts\recreate_runtime_orphan_stubs.py --write --overwrite-existing",
            "providerBatchCommands": [
                {
                    "providerKey": "guangya",
                    "orphanProfileIds": ["gy-orphan"],
                    "dryRunCommand": r".\.venv\Scripts\python.exe scripts\recreate_runtime_orphan_stubs.py --provider-key guangya",
                    "writeMissingCommand": r".\.venv\Scripts\python.exe scripts\recreate_runtime_orphan_stubs.py --write --provider-key guangya",
                    "overwriteExistingCommand": r".\.venv\Scripts\python.exe scripts\recreate_runtime_orphan_stubs.py --write --overwrite-existing --provider-key guangya",
                }
            ],
        },
        "items": [
            {
                "providerKey": "guangya",
                "providerDisplayName": "Guangya",
                "orphanProfileId": "gy-orphan",
                "sampleCount": 1,
                "pathCount": 1,
                "latestSavedAt": "2026-05-25T00:00:00+00:00",
                "runtimeModes": ["binary_upload_multipart"],
                "verifyModes": ["list_by_parent_name"],
                "conflictPolicies": ["overwrite_existing"],
                "conflictActions": ["overwrite_downgraded_to_auto_rename"],
                "existingProviderProfileCount": 1,
                "existingProviderProfileIds": ["saved-guangya-1"],
                "existingProviderProfileNames": ["saved-guangya"],
                "suggestedAuthModes": ["manual_token"],
                "preferredAuthMode": "manual_token",
                "requiredFieldHints": ["token or extra.authorization", "extra.parentId"],
                "webLoginUrl": "https://guangyapan.com/",
                "officialDocsUrl": "",
                "nextStep": "step",
                "note": "note",
                "recommendedCreateCommand": r".\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-orphan --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-orphan --token YOUR_TOKEN --set parentId=YOUR_VALUE --probe",
            }
        ],
    }

    original_root = export_script.ROOT
    original_builder = export_script.build_runtime_orphan_recovery
    original_renderer = export_script.runtime_orphan_recovery_to_markdown

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.build_runtime_orphan_recovery = lambda: synthetic_payload
        export_script.runtime_orphan_recovery_to_markdown = runtime_orphan_recovery_to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.build_runtime_orphan_recovery = original_builder
            export_script.runtime_orphan_recovery_to_markdown = original_renderer

        output_path = tmp_root / "docs" / "13-RUNTIME_ORPHAN_RECOVERY.md"
        markdown = output_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "exportedFileExists": True,
                "exportedHasTitle": "# CloudPan Sync Runtime Orphan Recovery Guide" in markdown,
                "exportedHasSummary": "orphanProfileCount=2" in markdown and "providersWithSavedProfiles=1" in markdown,
                "exportedHasOrphanSummary": "orphanSummary:" in markdown and "profiles=gy-orphan, uc-orphan" in markdown,
                "exportedHasBatchCommands": "batchCommands:" in markdown
                and "recreate_runtime_orphan_stubs.py --write" in markdown
                and "## Batch Recreate Commands" in markdown
                and "--provider-key guangya" in markdown,
                "exportedHasProviderSection": "## guangya - Guangya - gy-orphan" in markdown,
                "exportedHasCreateCommand": "--profile-id gy-orphan" in markdown and "create_auth_profile_stub.py" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
