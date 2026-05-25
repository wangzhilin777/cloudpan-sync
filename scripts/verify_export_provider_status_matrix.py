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

from cloudpan_sync.provider_status_matrix import matrix_to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_provider_status_matrix.py"
SPEC = importlib.util.spec_from_file_location("export_provider_status_matrix", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "generatedAt": "2026-05-25T00:00:00+00:00",
        "summary": {
            "providerCount": 2,
            "authReadyCount": 1,
            "createDirReadyCount": 2,
            "fastCheckCount": 2,
            "liveProbeOkCount": 1,
            "conflictAwareProviderCount": 2,
            "overwriteReadyCount": 0,
            "autoRenameReadyCount": 1,
            "overwriteDowngradeCount": 1,
            "overwriteSupportedCount": 0,
            "autoRenameSupportedCount": 1,
            "autoRenameProbeOnlyCount": 0,
            "conflictUnsupportedProviderCount": 1,
            "taskRuntimeEvidenceProviderCount": 1,
            "taskRuntimeFailedProviderCount": 1,
            "taskRuntimeCandidateEvidenceProviderCount": 0,
            "taskRuntimeProbeEvidenceProviderCount": 1,
            "taskRuntimeSampleCount": 3,
            "taskRuntimeSuccessCount": 1,
            "taskRuntimeFailedCount": 1,
            "taskRuntimeCandidateEvidenceCount": 0,
            "taskRuntimeProbeEvidenceCount": 1,
            "taskRuntimeBlockedProviderCount": 1,
            "taskRuntimeBlockedEvidenceCount": 1,
            "taskRuntimeConflictHandledProviderCount": 1,
            "taskRuntimeConflictHandledCount": 1,
            "taskRuntimeActiveCount": 1,
            "taskRuntimeCandidateCount": 0,
            "taskRuntimeBlockedCount": 0,
        },
        "items": [
            {
                "providerKey": "guangya",
                "supportStatus": "metadata_ready",
                "auth_ready": True,
                "list_ready": True,
                "metadata_ready": True,
                "create_dir_ready": True,
                "fast_check": True,
                "live_probe_ok": True,
                "task_runtime_track": "runtime_active",
                "task_runtime_track_note": "Current task runtime already drives Guangya live fast-check and fallback upload attempts.",
                "task_runtime_samples": 1,
                "task_runtime_success": 1,
                "task_runtime_failed": 0,
                "task_runtime_candidate": 0,
                "task_runtime_probe": 0,
                "task_runtime_blocked": 0,
                "task_runtime_conflict_handled": 1,
                "task_runtime_success_profiles": ["Guangya Smoke"],
                "task_runtime_failed_profiles": [],
                "task_runtime_candidate_profiles": [],
                "task_runtime_probe_profiles": [],
                "supportsOverwrite": False,
                "supportsAutoRename": True,
                "overwriteBehavior": "downgrade_to_auto_rename",
                "overwrite_support_status": "downgrade_to_auto_rename",
                "overwrite_support_note": "overwrite_existing 会诚实降级为 auto_rename_new。",
                "auto_rename_support_status": "supported",
                "auto_rename_support_note": "auto_rename_new 可直接支持。",
                "conflictPolicies": ["overwrite_existing", "auto_rename_new"],
                "fallback_ready": True,
                "conflictNotes": "Guangya conflict note",
            },
            {
                "providerKey": "189cloud",
                "supportStatus": "list_ready",
                "auth_ready": False,
                "list_ready": True,
                "metadata_ready": True,
                "create_dir_ready": True,
                "fast_check": True,
                "live_probe_ok": False,
                "task_runtime_track": "runtime_active",
                "task_runtime_track_note": "Current task runtime can attempt 189Cloud create_dir and upload chain, but share profiles remain readonly.",
                "task_runtime_samples": 2,
                "task_runtime_success": 0,
                "task_runtime_failed": 1,
                "task_runtime_candidate": 0,
                "task_runtime_probe": 1,
                "task_runtime_blocked": 1,
                "task_runtime_conflict_handled": 0,
                "task_runtime_success_profiles": [],
                "task_runtime_failed_profiles": ["189 Writer"],
                "task_runtime_candidate_profiles": [],
                "task_runtime_probe_profiles": ["189 Probe"],
                "supportsOverwrite": False,
                "supportsAutoRename": False,
                "overwriteBehavior": "readonly_auth_blocked",
                "overwrite_support_status": "unsupported",
                "overwrite_support_note": "当前 189Cloud 写鉴权不足。",
                "auto_rename_support_status": "unsupported",
                "auto_rename_support_note": "当前 189Cloud 同名冲突策略尚未声明为已支持。",
                "conflictPolicies": [],
                "fallback_ready": True,
                "conflictNotes": "189 conflict note",
            },
        ],
    }

    original_root = export_script.ROOT
    original_builder = export_script.build_status_matrix
    original_renderer = export_script.matrix_to_markdown

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.build_status_matrix = lambda: synthetic_payload
        export_script.matrix_to_markdown = matrix_to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.build_status_matrix = original_builder
            export_script.matrix_to_markdown = original_renderer

        output_path = tmp_root / "docs" / "06-PROVIDER_STATUS_MATRIX.md"
        markdown = output_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "exportedFileExists": True,
                "exportedHasTitle": "# CloudPan Sync Provider Status Matrix" in markdown,
                "exportedHasSummaryCounts": "providerCount=2" in markdown
                and "taskRuntimeSampleCount=3" in markdown
                and "taskRuntimeSuccessCount=1" in markdown
                and "taskRuntimeFailedCount=1" in markdown
                and "taskRuntimeProbeEvidenceCount=1" in markdown
                and "taskRuntimeBlockedEvidenceCount=1" in markdown,
                "exportedHasGuangyaRow": "| guangya | metadata_ready | True | True | True | True | True | True | runtime_active | 1 | 1 | 0 | 0 | 0 | 0 | 1 | False | True | downgrade_to_auto_rename | downgrade_to_auto_rename | supported | overwrite_existing, auto_rename_new | True |" in markdown,
                "exportedHas189Row": "| 189cloud | list_ready | False | True | True | True | True | False | runtime_active | 2 | 0 | 1 | 0 | 1 | 1 | 0 | False | False | readonly_auth_blocked | unsupported | unsupported | (none) | True |" in markdown,
                "exportedHasRuntimeNoteRow": "|  | runtime_note |" in markdown,
                "exportedHasRuntimeProfilesRow": "|  | runtime_profiles |" in markdown
                and "success=Guangya Smoke; failed=(none); candidate=(none); probe=(none)" in markdown
                and "success=(none); failed=189 Writer; candidate=(none); probe=189 Probe" in markdown,
                "exportedHasConflictNoteRows": "|  | overwrite_note |" in markdown and "|  | auto_rename_note |" in markdown and "|  | note |" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
