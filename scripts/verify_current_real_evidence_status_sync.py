from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.real_evidence_report import build_real_evidence_report


def _section(markdown: str, provider_key: str) -> str:
    marker = f"## {provider_key} - "
    start = markdown.find(marker)
    if start < 0:
        return ""
    next_start = markdown.find("\n## ", start + 1)
    if next_start < 0:
        return markdown[start:]
    return markdown[start:next_start]


def _item(payload: dict[str, object], provider_key: str) -> dict[str, object]:
    for row in list(payload.get("items") or []):
        item = dict(row or {})
        if str(item.get("providerKey") or "") == provider_key:
            return item
    return {}


def main() -> None:
    payload = build_real_evidence_report()
    summary = dict(payload.get("summary") or {})
    guangya_item = _item(payload, "guangya")
    uc_item = _item(payload, "uc")
    pikpak_item = _item(payload, "pikpak")
    markdown = (ROOT / "docs" / "10-REAL_EVIDENCE_STATUS.md").read_text(encoding="utf-8")

    guangya = _section(markdown, "guangya")
    uc = _section(markdown, "uc")
    pikpak = _section(markdown, "pikpak")
    cloud115 = _section(markdown, "115_open")
    cloud189 = _section(markdown, "189cloud")
    xunlei = _section(markdown, "xunlei")
    aliyun = _section(markdown, "aliyundrive_open")
    quark = _section(markdown, "quark")
    baidu = _section(markdown, "baidu_netdisk")
    pan123 = _section(markdown, "123_open")

    print(
        json.dumps(
            {
                "summaryHasCurrentRuntimeCounts": (
                    f"`task_runtime={summary.get('taskRuntimeEvidenceProviderCount', 0)}`" in markdown
                    and f"`task_runtime_failed={summary.get('taskRuntimeFailedProviderCount', 0)}`" in markdown
                    and f"`task_runtime_candidate={summary.get('taskRuntimeCandidateProviderCount', 0)}`" in markdown
                    and f"`task_runtime_probe={summary.get('taskRuntimeProbeProviderCount', 0)}`" in markdown
                    and f"`runtime_samples={summary.get('taskRuntimeSampleCount', 0)}`" in markdown
                    and f"`runtime_success={summary.get('taskRuntimeSuccessCount', 0)}`" in markdown
                    and f"`runtime_failed={summary.get('taskRuntimeFailedCount', 0)}`" in markdown
                    and f"`runtime_candidate={summary.get('taskRuntimeCandidateCount', 0)}`" in markdown
                    and f"`runtime_probe={summary.get('taskRuntimeProbeCount', 0)}`" in markdown
                    and f"`runtime_blocked_providers={summary.get('taskRuntimeBlockedProviderCount', 0)}`" in markdown
                    and f"`runtime_blocked={summary.get('taskRuntimeBlockedCount', 0)}`" in markdown
                    and f"`runtime_conflict_handled={summary.get('taskRuntimeConflictHandledCount', 0)}`" in markdown
                    and f"`runtime_orphan_providers={summary.get('taskRuntimeOrphanProviderCount', 0)}`" in markdown
                    and f"`runtime_orphan_profiles={summary.get('taskRuntimeOrphanProfileCount', 0)}`" in markdown
                ),
                "summaryHasCurrentProviderSummary": (
                    f"- providerSummary: `auth={', '.join(summary.get('authEvidenceProviders', [])) or '(none)'}` `list={', '.join(summary.get('listEvidenceProviders', [])) or '(none)'}` `metadata={', '.join(summary.get('metadataEvidenceProviders', [])) or '(none)'}` `create_dir={', '.join(summary.get('createDirEvidenceProviders', [])) or '(none)'}` `fully_verified={', '.join(summary.get('fullyVerifiedProviders', [])) or '(none)'}` `runtime_success={', '.join(summary.get('taskRuntimeEvidenceProviders', [])) or '(none)'}` `runtime_failed={', '.join(summary.get('taskRuntimeFailedProviders', [])) or '(none)'}` `runtime_candidate={', '.join(summary.get('taskRuntimeCandidateProviders', [])) or '(none)'}` `runtime_probe={', '.join(summary.get('taskRuntimeProbeProviders', [])) or '(none)'}` `runtime_blocked={', '.join(summary.get('taskRuntimeBlockedProviders', [])) or '(none)'}` `runtime_orphan={', '.join(summary.get('taskRuntimeOrphanProviders', [])) or '(none)'}`" in markdown
                ),
                "summaryShowsCurrentRuntimeDistribution": (
                    summary.get("taskRuntimeEvidenceProviderCount") == 3
                    and summary.get("taskRuntimeFailedProviderCount") == 0
                    and summary.get("taskRuntimeCandidateProviderCount") == 0
                    and summary.get("taskRuntimeProbeProviderCount") == 0
                    and summary.get("taskRuntimeSampleCount") == 6
                    and summary.get("taskRuntimeSuccessCount") == 6
                    and summary.get("taskRuntimeFailedCount") == 0
                    and summary.get("taskRuntimeCandidateCount") == 0
                    and summary.get("taskRuntimeProbeCount") == 0
                    and summary.get("taskRuntimeBlockedProviderCount") == 0
                    and summary.get("taskRuntimeBlockedCount") == 0
                    and summary.get("taskRuntimeConflictHandledCount") == 6
                    and summary.get("taskRuntimeOrphanProviderCount") == 3
                    and summary.get("taskRuntimeOrphanProfileCount") == 6
                ),
                "summaryShowsCurrentProviderDistribution": (
                    summary.get("authEvidenceProviders") == []
                    and summary.get("listEvidenceProviders") == []
                    and summary.get("metadataEvidenceProviders") == []
                    and summary.get("createDirEvidenceProviders") == []
                    and summary.get("fullyVerifiedProviders") == []
                    and summary.get("taskRuntimeEvidenceProviders") == ["guangya", "uc", "pikpak"]
                    and summary.get("taskRuntimeFailedProviders") == []
                    and summary.get("taskRuntimeCandidateProviders") == []
                    and summary.get("taskRuntimeProbeProviders") == []
                    and summary.get("taskRuntimeBlockedProviders") == []
                ),
                "guangyaSectionShowsRuntimeSuccess": "samples=4 success=4 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=4 orphanProfiles=4" in guangya,
                "ucSectionShowsRuntimeSuccess": "samples=1 success=1 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=1" in uc,
                "pikpakSectionShowsRuntimeSuccess": "samples=1 success=1 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=1" in pikpak,
                "runtimeSuccessSectionsShowCurrentProfiles": (
                    f"taskRuntimeProfiles: success={', '.join(((guangya_item.get('taskRuntimeEvidence') or {}).get('profiles') or [])) or '(none)'} failed=(none) candidate=(none) probe=(none) orphan={', '.join(((guangya_item.get('taskRuntimeEvidence') or {}).get('orphanProfiles') or [])) or '(none)'}" in guangya
                    and f"taskRuntimeProfiles: success={', '.join(((uc_item.get('taskRuntimeEvidence') or {}).get('profiles') or [])) or '(none)'} failed=(none) candidate=(none) probe=(none) orphan={', '.join(((uc_item.get('taskRuntimeEvidence') or {}).get('orphanProfiles') or [])) or '(none)'}" in uc
                    and f"taskRuntimeProfiles: success={', '.join(((pikpak_item.get('taskRuntimeEvidence') or {}).get('profiles') or [])) or '(none)'} failed=(none) candidate=(none) probe=(none) orphan={', '.join(((pikpak_item.get('taskRuntimeEvidence') or {}).get('orphanProfiles') or [])) or '(none)'}" in pikpak
                ),
                "cloud115SectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in cloud115,
                "cloud189SectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in cloud189,
                "xunleiSectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in xunlei,
                "aliyunSectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in aliyun,
                "quarkSectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in quark,
                "baiduSectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in baidu,
                "pan123SectionShowsNoRuntimeSuccess": "samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0" in pan123,
                "noRuntimeSuccessSectionsShowEmptyProfiles": (
                    "taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none) orphan=(none)" in cloud115
                    and "taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none) orphan=(none)" in cloud189
                    and "taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none) orphan=(none)" in xunlei
                    and "taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none) orphan=(none)" in aliyun
                    and "taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none) orphan=(none)" in quark
                    and "taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none) orphan=(none)" in baidu
                    and "taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none) orphan=(none)" in pan123
                ),
                "noRuntimeSuccessSectionsKeepTodoNote": (
                    "当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。" in cloud115
                    and "当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。" in cloud189
                    and "当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。" in xunlei
                    and "当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。" in aliyun
                    and "当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。" in quark
                    and "当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理." not in markdown
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
