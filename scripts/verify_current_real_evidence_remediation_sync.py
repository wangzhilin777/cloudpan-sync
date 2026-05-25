from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.real_evidence_remediation import build_real_evidence_remediation_bundle


def _section(markdown: str, provider_key: str) -> str:
    marker = f"### {provider_key} - "
    start = markdown.find(marker)
    if start < 0:
        return ""
    next_start = markdown.find("\n### ", start + 1)
    if next_start < 0:
        return markdown[start:]
    return markdown[start:next_start]


def main() -> None:
    payload = build_real_evidence_remediation_bundle()
    summary = dict(payload.get("summary") or {})
    markdown = (ROOT / "docs" / "12-REAL_EVIDENCE_REMEDIATION_GUIDE.md").read_text(encoding="utf-8")

    cloud115 = _section(markdown, "115_open")
    quark = _section(markdown, "quark")
    cloud189 = _section(markdown, "189cloud")
    baidu = _section(markdown, "baidu_netdisk")
    xunlei = _section(markdown, "xunlei")
    pan123 = _section(markdown, "123_open")
    aliyun = _section(markdown, "aliyundrive_open")

    print(
        json.dumps(
            {
                "summaryHasCurrentRemediationCounts": (
                    f"- providersNeedingRuntimeSuccess: `{summary.get('providersNeedingRuntimeSuccess', 0)}`" in markdown
                    and f"- providersWithPostBootstrapRuntimeCommand: `{summary.get('providersWithPostBootstrapRuntimeCommand', 0)}`" in markdown
                    and f"- providersWithOverwriteVariantCommand: `{summary.get('providersWithOverwriteVariantCommand', 0)}`" in markdown
                    and f"- providersWithConflictPolicyNote: `{summary.get('providersWithConflictPolicyNote', 0)}`" in markdown
                    and f"- providersWithDeclaredConflictPolicies: `{summary.get('providersWithDeclaredConflictPolicies', 0)}`" in markdown
                    and f"- providersWithProviderManagedOverwrite: `{summary.get('providersWithProviderManagedOverwrite', 0)}`" in markdown
                    and f"- providersWithOverwriteDowngrade: `{summary.get('providersWithOverwriteDowngrade', 0)}`" in markdown
                    and f"- providersWithConflictUnsupported: `{summary.get('providersWithConflictUnsupported', 0)}`" in markdown
                    and f"- providersWithCreateCommand: `{summary.get('providersWithCreateCommand', 0)}`" in markdown
                    and f"- providersWithBootstrapCommand: `{summary.get('providersWithBootstrapCommand', 0)}`" in markdown
                ),
                "summaryShowsExpectedRuntimeRemediationCounts": (
                    summary.get("providersNeedingRuntimeSuccess") == 7
                    and summary.get("providersWithPostBootstrapRuntimeCommand") == 6
                    and summary.get("providersWithOverwriteVariantCommand") == 6
                    and summary.get("providersWithConflictPolicyNote") == 6
                    and summary.get("providersWithDeclaredConflictPolicies") == 8
                    and summary.get("providersWithProviderManagedOverwrite") == 1
                    and summary.get("providersWithOverwriteDowngrade") == 7
                    and summary.get("providersWithConflictUnsupported") == 1
                    and summary.get("providersWithCreateCommand") == 8
                    and summary.get("providersWithBootstrapCommand") == 8
                ),
                "cloud115SectionKeepsFastPostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in cloud115
                    and "create_fast_upload_candidate_task.py" in cloud115
                    and "--conflict-policy auto_rename_new" in cloud115
                    and "recommendedOverwriteVariantCommand" in cloud115
                    and "--conflict-policy overwrite_existing" in cloud115
                    and "conflictPolicyNote:" in cloud115
                    and "overwrite_existing" in cloud115
                    and "probe_only_runtime_write_check" in cloud115
                    and "providerConflictNotes:" in cloud115
                    and "tmp\\115_open-post-bootstrap-runtime-evidence" in cloud115
                    and "先不要把首条样本建立在 overwrite_existing 上" in cloud115
                ),
                "quarkSectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in quark
                    and "create_live_upload_task.py" in quark
                    and "--conflict-policy auto_rename_new" in quark
                    and "recommendedOverwriteVariantCommand" in quark
                    and "--conflict-policy overwrite_existing" in quark
                    and "conflictPolicyNote:" in quark
                    and "overwrite_existing" in quark
                    and "overwrite=downgrade_to_auto_rename" in quark
                    and "providerConflictNotes:" in quark
                    and "tmp\\quark-post-bootstrap-runtime-evidence" in quark
                    and "会诚实降级为自动改名" in quark
                ),
                "cloud189SectionKeepsFastPostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in cloud189
                    and "create_fast_upload_candidate_task.py" in cloud189
                    and "--conflict-policy auto_rename_new" in cloud189
                    and "recommendedOverwriteVariantCommand" in cloud189
                    and "--conflict-policy overwrite_existing" in cloud189
                    and "conflictPolicyNote:" in cloud189
                    and "overwrite_existing" in cloud189
                    and "conflictSupport: `declared=(none)` `overwrite=unsupported` `auto_rename=unsupported`" in cloud189
                    and "providerConflictNotes:" in cloud189
                    and "tmp\\189cloud-post-bootstrap-runtime-evidence" in cloud189
                ),
                "baiduSectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in baidu
                    and "create_live_upload_task.py" in baidu
                    and "--conflict-policy auto_rename_new" in baidu
                    and "recommendedOverwriteVariantCommand" in baidu
                    and "--conflict-policy overwrite_existing" in baidu
                    and "conflictPolicyNote:" in baidu
                    and "overwrite_existing" in baidu
                    and "conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported`" in baidu
                    and "providerConflictNotes:" in baidu
                    and "tmp\\baidu_netdisk-post-bootstrap-runtime-evidence" in baidu
                ),
                "xunleiSectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in xunlei
                    and "create_live_upload_task.py" in xunlei
                    and "--conflict-policy auto_rename_new" in xunlei
                    and "recommendedOverwriteVariantCommand" in xunlei
                    and "--conflict-policy overwrite_existing" in xunlei
                    and "conflictPolicyNote:" in xunlei
                    and "overwrite_existing" in xunlei
                    and "conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported`" in xunlei
                    and "providerConflictNotes:" in xunlei
                    and "tmp\\xunlei-post-bootstrap-runtime-evidence" in xunlei
                ),
                "pan123SectionUsesLivePostBootstrapHelper": (
                    "recommendedPostBootstrapRuntimeCommand" in pan123
                    and "create_live_upload_task.py" in pan123
                    and "--conflict-policy auto_rename_new" in pan123
                    and "recommendedOverwriteVariantCommand" in pan123
                    and "--conflict-policy overwrite_existing" in pan123
                    and "conflictPolicyNote:" in pan123
                    and "overwrite_existing" in pan123
                    and "conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported`" in pan123
                    and "providerConflictNotes:" in pan123
                    and "tmp\\123_open-post-bootstrap-runtime-evidence" in pan123
                ),
                "aliyunSectionKeepsRefreshEvidencePath": (
                    "recommendedRefreshEvidenceCommand" in aliyun
                    and "patch_and_probe_auth_profile.py" in aliyun
                    and "conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=supported` `auto_rename=supported`" in aliyun
                    and "providerConflictNotes:" in aliyun
                    and "recommendedPostBootstrapRuntimeCommand" not in aliyun
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
