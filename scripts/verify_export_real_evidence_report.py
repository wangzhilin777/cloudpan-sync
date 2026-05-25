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

from cloudpan_sync.real_evidence_report import real_evidence_to_markdown

SCRIPT_PATH = ROOT / "scripts" / "export_real_evidence_report.py"
SPEC = importlib.util.spec_from_file_location("export_real_evidence_report", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load script module: {SCRIPT_PATH}")
export_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_script)


def main() -> None:
    synthetic_payload = {
        "summary": {
            "providerCount": 2,
            "profilesSaved": 2,
            "latestValidationProfileCount": 2,
            "latestProbeProfileCount": 2,
            "authEvidenceProviderCount": 1,
            "listEvidenceProviderCount": 1,
            "metadataEvidenceProviderCount": 1,
            "createDirEvidenceProviderCount": 1,
            "taskRuntimeEvidenceProviderCount": 2,
            "taskRuntimeFailedProviderCount": 1,
            "taskRuntimeCandidateProviderCount": 1,
            "taskRuntimeProbeProviderCount": 1,
            "taskRuntimeBlockedProviderCount": 1,
            "taskRuntimeConflictHandledCount": 1,
            "taskRuntimeOrphanProviderCount": 1,
            "taskRuntimeOrphanProfileCount": 1,
            "fullyVerifiedProviderCount": 0,
            "taskRuntimeSampleCount": 4,
            "taskRuntimeSuccessCount": 1,
            "taskRuntimeFailedCount": 1,
            "taskRuntimeCandidateCount": 1,
            "taskRuntimeProbeCount": 1,
            "taskRuntimeBlockedCount": 1,
            "authEvidenceProviders": ["guangya"],
            "listEvidenceProviders": ["guangya"],
            "metadataEvidenceProviders": ["guangya"],
            "createDirEvidenceProviders": ["guangya"],
            "fullyVerifiedProviders": [],
            "taskRuntimeEvidenceProviders": ["guangya"],
            "taskRuntimeFailedProviders": ["189cloud"],
            "taskRuntimeCandidateProviders": ["189cloud"],
            "taskRuntimeProbeProviders": ["189cloud"],
            "taskRuntimeBlockedProviders": ["189cloud"],
            "taskRuntimeOrphanProviders": ["guangya"],
            "taskRuntimeOrphanProfiles": ["gy-orphan"],
        },
        "items": [
            {
                "providerKey": "guangya",
                "displayName": "Guangya",
                "fullyVerified": False,
                "authEvidence": {"ok": True, "profiles": ["gy-1"]},
                "listEvidence": {"ok": True, "profiles": ["gy-1"]},
                "metadataEvidence": {"ok": True, "profiles": ["gy-1"]},
                "createDirEvidence": {"ok": True, "profiles": ["gy-1"]},
                "taskRuntimeEvidence": {
                    "ok": True,
                    "sampleCount": 1,
                    "successCount": 1,
                    "failedCount": 0,
                    "candidateCount": 0,
                    "probeCount": 0,
                    "blockedCount": 0,
                    "conflictHandledCount": 1,
                    "profiles": ["gy-1"],
                    "failedProfiles": [],
                    "candidateProfiles": [],
                    "probeProfiles": [],
                    "orphanProfiles": ["gy-orphan"],
                    "orphanProfileCount": 1,
                    "note": "当前已记录到任务运行阶段真实成功样本。",
                },
                "gaps": ["缺少 fully verified 汇总样本"],
                "notes": "Guangya note",
            },
            {
                "providerKey": "189cloud",
                "displayName": "Tianyi 189Cloud",
                "fullyVerified": False,
                "authEvidence": {"ok": False, "profiles": []},
                "listEvidence": {"ok": False, "profiles": []},
                "metadataEvidence": {"ok": False, "profiles": []},
                "createDirEvidence": {"ok": False, "profiles": []},
                "taskRuntimeEvidence": {
                    "ok": False,
                    "sampleCount": 3,
                    "successCount": 0,
                    "failedCount": 1,
                    "candidateCount": 1,
                    "probeCount": 1,
                    "blockedCount": 1,
                    "conflictHandledCount": 0,
                    "profiles": [],
                    "failedProfiles": ["189-1"],
                    "candidateProfiles": ["189-candidate"],
                    "probeProfiles": ["189-probe"],
                    "note": "已有 failed / candidate / probe / blocked 样本，但尚无成功样本。",
                },
                "gaps": ["缺少通过的 auth validation 证据", "缺少真实 runtime 成功样本"],
                "notes": "189 note",
            },
        ],
    }

    original_root = export_script.ROOT
    original_builder = export_script.build_real_evidence_report
    original_renderer = export_script.real_evidence_to_markdown

    with TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "docs").mkdir(parents=True, exist_ok=True)
        export_script.ROOT = tmp_root
        export_script.build_real_evidence_report = lambda: synthetic_payload
        export_script.real_evidence_to_markdown = real_evidence_to_markdown
        try:
            export_script.main()
        finally:
            export_script.ROOT = original_root
            export_script.build_real_evidence_report = original_builder
            export_script.real_evidence_to_markdown = original_renderer

        output_path = tmp_root / "docs" / "10-REAL_EVIDENCE_STATUS.md"
        markdown = output_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "exportedFileExists": True,
                "exportedHasTitle": "# CloudPan Sync 真实证据状态报告" in markdown,
                "exportedHasSummaryCounts": "runtime_samples=4" in markdown
                and "runtime_success=1" in markdown
                and "runtime_failed=1" in markdown
                and "runtime_candidate=1" in markdown
                and "runtime_probe=1" in markdown
                and "runtime_blocked_providers=1" in markdown
                and "runtime_blocked=1" in markdown
                and "runtime_orphan_providers=1" in markdown
                and "runtime_orphan_profiles=1" in markdown,
                "exportedHasProviderSummary": "- providerSummary: `auth=guangya` `list=guangya` `metadata=guangya` `create_dir=guangya` `fully_verified=(none)` `runtime_success=guangya` `runtime_failed=189cloud` `runtime_candidate=189cloud` `runtime_probe=189cloud` `runtime_blocked=189cloud` `runtime_orphan=guangya`" in markdown,
                "exportedHasGuangyaSuccessRow": "## guangya - Guangya" in markdown
                and "samples=1 success=1 failed=0" in markdown
                and "orphanProfiles=1" in markdown,
                "exportedHas189MixedRuntimeRow": "## 189cloud - Tianyi 189Cloud" in markdown
                and "samples=3 success=0 failed=1 candidate=1 probe=1 blocked=1" in markdown,
                "exportedHasRuntimeProfiles": "taskRuntimeProfiles: success=gy-1 failed=(none) candidate=(none) probe=(none) orphan=gy-orphan" in markdown
                and "taskRuntimeProfiles: success=(none) failed=189-1 candidate=189-candidate probe=189-probe" in markdown,
                "exportedHasGapText": "缺少真实 runtime 成功样本" in markdown,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
