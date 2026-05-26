from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.provider_status_matrix import build_status_matrix


def _find_row(markdown: str, provider_key: str) -> str:
    prefix = f"| {provider_key} |"
    for line in markdown.splitlines():
        if line.startswith(prefix):
            return line
    return ""


def _find_runtime_profiles(markdown: str, provider_key: str) -> str:
    lines = markdown.splitlines()
    prefix = f"| {provider_key} |"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        for follow in lines[index + 1 :]:
            if follow.startswith("| ") and not follow.startswith("|  |"):
                break
            if follow.startswith("|  | runtime_profiles |"):
                return follow
        break
    return ""


def main() -> None:
    payload = build_status_matrix()
    summary = dict(payload.get("summary") or {})
    markdown = (ROOT / "docs" / "06-PROVIDER_STATUS_MATRIX.md").read_text(encoding="utf-8")

    guangya_row = _find_row(markdown, "guangya")
    uc_row = _find_row(markdown, "uc")
    pikpak_row = _find_row(markdown, "pikpak")
    aliyun_row = _find_row(markdown, "aliyundrive_open")
    quark_row = _find_row(markdown, "quark")
    baidu_row = _find_row(markdown, "baidu_netdisk")
    pan123_row = _find_row(markdown, "123_open")
    guangya_profiles = _find_runtime_profiles(markdown, "guangya")
    uc_profiles = _find_runtime_profiles(markdown, "uc")
    pikpak_profiles = _find_runtime_profiles(markdown, "pikpak")
    aliyun_profiles = _find_runtime_profiles(markdown, "aliyundrive_open")
    quark_profiles = _find_runtime_profiles(markdown, "quark")
    baidu_profiles = _find_runtime_profiles(markdown, "baidu_netdisk")
    pan123_profiles = _find_runtime_profiles(markdown, "123_open")

    print(
        json.dumps(
            {
                "summaryHasCurrentRuntimeCounts": (
                    f"taskRuntimeEvidenceProviderCount={summary.get('taskRuntimeEvidenceProviderCount', 0)}" in markdown
                    and f"taskRuntimeSampleCount={summary.get('taskRuntimeSampleCount', 0)}" in markdown
                    and f"taskRuntimeSuccessCount={summary.get('taskRuntimeSuccessCount', 0)}" in markdown
                    and f"taskRuntimeConflictHandledProviderCount={summary.get('taskRuntimeConflictHandledProviderCount', 0)}" in markdown
                    and f"taskRuntimeConflictHandledCount={summary.get('taskRuntimeConflictHandledCount', 0)}" in markdown
                ),
                "summaryHasCurrentProviderSummary": (
                    f"- providerSummary: `auth_ready={', '.join(summary.get('authReadyProviders', [])) or '(none)'}` `create_dir_ready={', '.join(summary.get('createDirReadyProviders', [])) or '(none)'}` `fast_check={', '.join(summary.get('fastCheckProviders', [])) or '(none)'}` `live_probe_ok={', '.join(summary.get('liveProbeOkProviders', [])) or '(none)'}` `overwrite_downgrade={', '.join(summary.get('overwriteDowngradeProviders', [])) or '(none)'}` `overwrite_supported={', '.join(summary.get('overwriteSupportedProviders', [])) or '(none)'}` `auto_rename_supported={', '.join(summary.get('autoRenameSupportedProviders', [])) or '(none)'}` `auto_rename_probe_only={', '.join(summary.get('autoRenameProbeOnlyProviders', [])) or '(none)'}` `conflict_unsupported={', '.join(summary.get('conflictUnsupportedProviders', [])) or '(none)'}` `runtime_success={', '.join(summary.get('taskRuntimeSuccessProviders', [])) or '(none)'}` `runtime_failed={', '.join(summary.get('taskRuntimeFailedProviders', [])) or '(none)'}` `runtime_candidate={', '.join(summary.get('taskRuntimeCandidateProviders', [])) or '(none)'}` `runtime_probe={', '.join(summary.get('taskRuntimeProbeProviders', [])) or '(none)'}` `runtime_blocked={', '.join(summary.get('taskRuntimeBlockedProviders', [])) or '(none)'}` `runtime_conflict_handled={', '.join(summary.get('taskRuntimeConflictHandledProviders', [])) or '(none)'}` `runtime_orphan={', '.join(summary.get('taskRuntimeOrphanProviders', [])) or '(none)'}` `runtime_orphan_profiles={', '.join(summary.get('taskRuntimeOrphanProfiles', [])) or '(none)'}`" in markdown
                ),
                "summaryShowsCurrentRuntimeSuccessDistribution": (
                    summary.get("taskRuntimeEvidenceProviderCount") == 3
                    and summary.get("taskRuntimeSuccessCount") == 6
                    and summary.get("taskRuntimeSampleCount") == 6
                    and summary.get("taskRuntimeConflictHandledCount") == 6
                    and summary.get("taskRuntimeOrphanProviderCount") == 3
                    and summary.get("taskRuntimeOrphanProfileCount") == 6
                ),
                "summaryShowsCurrentProviderDistribution": (
                    summary.get("authReadyProviders") == []
                    and summary.get("createDirReadyProviders") == ["guangya", "aliyundrive_open", "115_open", "quark", "189cloud", "baidu_netdisk", "uc", "xunlei", "pikpak", "123_open"]
                    and summary.get("fastCheckProviders") == ["guangya", "aliyundrive_open", "115_open", "quark", "189cloud", "baidu_netdisk", "uc", "xunlei", "pikpak", "123_open"]
                    and summary.get("liveProbeOkProviders") == []
                    and summary.get("overwriteDowngradeProviders") == ["guangya", "quark", "baidu_netdisk", "uc", "xunlei", "pikpak", "123_open"]
                    and summary.get("overwriteSupportedProviders") == ["aliyundrive_open"]
                    and summary.get("autoRenameSupportedProviders") == ["guangya", "aliyundrive_open", "quark", "baidu_netdisk", "uc", "xunlei", "pikpak", "123_open"]
                    and summary.get("autoRenameProbeOnlyProviders") == ["115_open"]
                    and summary.get("conflictUnsupportedProviders") == ["189cloud"]
                    and summary.get("taskRuntimeSuccessProviders") == ["guangya", "uc", "pikpak"]
                    and summary.get("taskRuntimeFailedProviders") == []
                    and summary.get("taskRuntimeCandidateProviders") == []
                    and summary.get("taskRuntimeProbeProviders") == []
                    and summary.get("taskRuntimeBlockedProviders") == []
                    and summary.get("taskRuntimeConflictHandledProviders") == ["guangya", "uc", "pikpak"]
                ),
                "guangyaRowShowsRuntimeSuccess": "| guangya |" in guangya_row and "| 4 | 4 | 0 | 0 | 0 | 0 | 4 |" in guangya_row,
                "ucRowShowsRuntimeSuccess": "| uc |" in uc_row and "| 1 | 1 | 0 | 0 | 0 | 0 | 1 |" in uc_row,
                "pikpakRowShowsRuntimeSuccess": "| pikpak |" in pikpak_row and "| 1 | 1 | 0 | 0 | 0 | 0 | 1 |" in pikpak_row,
                "runtimeSuccessRowsShowCurrentProfiles": (
                    f"success={', '.join((next((item for item in payload.get('items', []) if item.get('providerKey') == 'guangya'), {}).get('task_runtime_success_profiles') or [])) or '(none)'}; failed=(none); candidate=(none); probe=(none)" in guangya_profiles
                    and f"success={', '.join((next((item for item in payload.get('items', []) if item.get('providerKey') == 'uc'), {}).get('task_runtime_success_profiles') or [])) or '(none)'}; failed=(none); candidate=(none); probe=(none)" in uc_profiles
                    and f"success={', '.join((next((item for item in payload.get('items', []) if item.get('providerKey') == 'pikpak'), {}).get('task_runtime_success_profiles') or [])) or '(none)'}; failed=(none); candidate=(none); probe=(none)" in pikpak_profiles
                ),
                "aliyunRowShowsNoRuntimeSuccess": "| aliyundrive_open |" in aliyun_row and "| 0 | 0 | 0 | 0 | 0 | 0 |" in aliyun_row,
                "quarkRowShowsNoRuntimeSuccess": "| quark |" in quark_row and "| 0 | 0 | 0 | 0 | 0 | 0 |" in quark_row,
                "baiduRowShowsNoRuntimeSuccess": "| baidu_netdisk |" in baidu_row and "| 0 | 0 | 0 | 0 | 0 | 0 |" in baidu_row,
                "pan123RowShowsNoRuntimeSuccess": "| 123_open |" in pan123_row and "| 0 | 0 | 0 | 0 | 0 | 0 |" in pan123_row,
                "noRuntimeSuccessRowsShowEmptyProfiles": (
                    "success=(none); failed=(none); candidate=(none); probe=(none)" in aliyun_profiles
                    and "success=(none); failed=(none); candidate=(none); probe=(none)" in quark_profiles
                    and "success=(none); failed=(none); candidate=(none); probe=(none)" in baidu_profiles
                    and "success=(none); failed=(none); candidate=(none); probe=(none)" in pan123_profiles
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
