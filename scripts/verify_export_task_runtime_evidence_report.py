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

from cloudpan_sync.task_runtime_evidence_store import task_runtime_evidence_to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_task_runtime_evidence_report.py"
SPEC = importlib.util.spec_from_file_location("export_task_runtime_evidence_report", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "summary": {
            "historyCount": 4,
            "sampleCount": 4,
            "providerCount": 3,
            "profileCount": 3,
            "successProviderCount": 1,
            "failedProviderCount": 1,
            "candidateProviderCount": 1,
            "probeProviderCount": 1,
            "blockedProviderCount": 1,
            "successCount": 1,
            "failedCount": 1,
            "candidateCount": 1,
            "probeCount": 1,
            "blockedCount": 1,
            "verifyOkCount": 1,
            "conflictHandledProviderCount": 1,
            "conflictHandledCount": 1,
            "runtimeOrphanProviderCount": 2,
            "runtimeOrphanProfileCount": 2,
            "runtimeOrphanProviders": ["189cloud", "quark"],
            "runtimeOrphanProfiles": ["189-1", "quark-1"],
            "successProfiles": ["gy-1"],
            "failedProfiles": ["189-1"],
            "candidateProfiles": ["quark-1"],
            "probeProfiles": [],
            "blockedProfiles": ["189-1"],
            "conflictHandledProfiles": ["gy-1"],
        },
        "latestItems": [
            {
                "providerKey": "guangya",
                "profileId": "gy-1",
                "path": "/demo.bin",
                "mode": "binary_upload_multipart",
                "executionMode": "live",
                "success": True,
                "verifyOk": True,
                "verifyMode": "list_by_parent_name",
                "verifyNote": "verified by list",
                "conflictAction": "overwrite_downgraded_to_auto_rename",
                "resolvedTargetName": "demo (1).bin",
                "riskHint": "fallback upload required",
                "requiredAuth": [],
            },
            {
                "providerKey": "189cloud",
                "profileId": "189-1",
                "path": "/large.iso",
                "mode": "download_upload_blocked_by_size_limit",
                "executionMode": "blocked",
                "success": False,
                "verifyOk": False,
                "verifyMode": "",
                "verifyNote": "blocked before verification",
                "conflictAction": "",
                "resolvedTargetName": "large.iso",
                "riskHint": "download_upload_size_limit_exceeded",
                "error": "download_upload_blocked_by_size_limit",
                "requiredAuth": ["AccessToken"],
            },
            {
                "providerKey": "quark",
                "profileId": "quark-1",
                "path": "/movie.mkv",
                "mode": "quark_fast_upload_candidate",
                "executionMode": "probe",
                "success": True,
                "candidateOnly": True,
                "verifyOk": False,
                "verifyMode": "fingerprint_candidate",
                "verifyNote": "candidate only",
                "conflictAction": "",
                "resolvedTargetName": "movie.mkv",
                "riskHint": "",
                "requiredAuth": [],
            },
            {
                "providerKey": "189cloud",
                "profileId": "189-1",
                "path": "/folder-probe",
                "mode": "189cloud_create_dir_probe",
                "executionMode": "probe",
                "success": True,
                "probeOnly": True,
                "verifyOk": False,
                "verifyMode": "",
                "verifyNote": "probe only",
                "conflictAction": "",
                "resolvedTargetName": "folder-probe",
                "riskHint": "",
                "requiredAuth": [],
            },
        ],
        "items": [],
    }

    original_root = export_script.ROOT
    original_builder = export_script.build_task_runtime_evidence_payload
    original_renderer = export_script.task_runtime_evidence_to_markdown

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.build_task_runtime_evidence_payload = lambda: synthetic_payload
        export_script.task_runtime_evidence_to_markdown = task_runtime_evidence_to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.build_task_runtime_evidence_payload = original_builder
            export_script.task_runtime_evidence_to_markdown = original_renderer

        output_path = tmp_root / "docs" / "11-TASK_RUNTIME_EVIDENCE.md"
        markdown = output_path.read_text(encoding="utf-8")
    exported_file_exists = True
    exported_has_title = "# CloudPan Sync 任务运行真实样本报告" in markdown
    exported_has_summary_counts = (
        "successProviderCount=1" in markdown
        and "failedProviderCount=1" in markdown
        and "candidateProviderCount=1" in markdown
        and "blockedProviderCount=1" in markdown
        and "conflictHandledProviderCount=1" in markdown
        and "runtimeOrphanProviderCount=2" in markdown
        and "runtimeOrphanProfileCount=2" in markdown
    )
    exported_has_profile_summary = (
        "profileSummary:" in markdown
        and "`success=gy-1`" in markdown
        and "`failed=189-1`" in markdown
        and "`candidate=quark-1`" in markdown
        and "`probe=(none)`" in markdown
        and "`blocked=189-1`" in markdown
        and "`conflictHandled=gy-1`" in markdown
        and "`runtimeOrphan=189-1, quark-1`" in markdown
    )
    exported_has_blocked_row = (
        "executionMode=blocked" in markdown
        and "riskHint=download_upload_size_limit_exceeded" in markdown
        and "requiredAuth=AccessToken" in markdown
        and "orphanProfileId=189-1" in markdown
    )
    exported_has_candidate_row = (
        "candidateOnly=True" in markdown
        and "verifyMode=fingerprint_candidate" in markdown
        and "orphanProfileId=quark-1" in markdown
    )
    exported_has_probe_row = (
        "probeOnly=True" in markdown
        and "path=/folder-probe" in markdown
        and markdown.count("orphanProfileId=189-1") == 2
    )
    exported_has_conflict_handled_row = (
        "conflictAction=overwrite_downgraded_to_auto_rename" in markdown
        and "orphanProfileId=(none)" in markdown
    )
    export_task_runtime_evidence_report_flow_matches_expected_markdown = (
        exported_file_exists
        and exported_has_title
        and exported_has_summary_counts
        and exported_has_profile_summary
        and exported_has_blocked_row
        and exported_has_candidate_row
        and exported_has_probe_row
        and exported_has_conflict_handled_row
    )

    print(
        json.dumps(
            {
                "exportedFileExists": exported_file_exists,
                "exportedHasTitle": exported_has_title,
                "exportedHasSummaryCounts": exported_has_summary_counts,
                "exportedHasProfileSummary": exported_has_profile_summary,
                "exportedHasBlockedRow": exported_has_blocked_row,
                "exportedHasCandidateRow": exported_has_candidate_row,
                "exportedHasProbeRow": exported_has_probe_row,
                "exportedHasConflictHandledRow": exported_has_conflict_handled_row,
                "exportTaskRuntimeEvidenceReportFlowMatchesExpectedMarkdown": export_task_runtime_evidence_report_flow_matches_expected_markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
