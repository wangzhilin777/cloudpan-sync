from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_profile_evidence import auth_profile_evidence_to_markdown, build_auth_profile_evidence, refresh_auth_profile_evidence
from cloudpan_sync.auth_profile_view import auth_profile_view
from cloudpan_sync.auth_store import get_profile
from cloudpan_sync.real_evidence_remediation import build_real_evidence_remediation_bundle, real_evidence_remediation_to_markdown
from cloudpan_sync.real_evidence_report import build_real_evidence_report, real_evidence_to_markdown
from cloudpan_sync.task_runtime_evidence_store import build_task_runtime_evidence_payload, task_runtime_evidence_to_markdown
from cloudpan_sync import task_runtime
from cloudpan_sync.models import SourceEntry, TaskCreateRequest


def _ensure_local_file(local_file: str, auto_temp_file: bool) -> tuple[Path, bool]:
    if local_file:
        path = Path(local_file)
        if not path.exists() or not path.is_file():
            raise SystemExit(f"local_file_not_found: {path}")
        return path, False
    if not auto_temp_file:
        raise SystemExit("Either --local-file or --auto-temp-file is required.")
    fd, raw_path = tempfile.mkstemp(prefix="cloudpan-sync-live-upload-", suffix=".bin")
    path = Path(raw_path)
    with os.fdopen(fd, "wb") as handle:
        handle.write(b"cloudpan-sync-live-upload")
    return path, True


def _resolve_target_parent_id(profile_id: str, explicit_parent_id: str) -> str:
    if explicit_parent_id:
        return explicit_parent_id
    profile = get_profile(profile_id)
    if profile is None:
        return ""
    profile_view = auth_profile_view(profile)
    return str(profile_view.get("resolvedParentId") or "").strip()


def _build_entry(path: Path, remote_path: str) -> SourceEntry:
    return SourceEntry(
        path=remote_path,
        size=path.stat().st_size,
        md5="",
        localPath=str(path),
    )


def _write_optional_text(path_text: str, content: str) -> str:
    output = str(path_text or "").strip()
    if not output:
        return ""
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return str(output_path)


def _resolve_evidence_output_dir(path_text: str) -> Path | None:
    output = str(path_text or "").strip()
    if not output:
        return None
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def _auth_evidence_markdown(profile_id: str, refresh: bool) -> str:
    profile = get_profile(profile_id)
    if profile is None:
        return ""
    if refresh:
        payload = refresh_auth_profile_evidence(
            profile=profile,
            persist=True,
            profile_view_builder=auth_profile_view,
        )
    else:
        payload = build_auth_profile_evidence(profile=profile, profile_view=auth_profile_view(profile))
    return auth_profile_evidence_to_markdown(payload)


def _remediation_followup(profile_id: str) -> dict[str, object]:
    payload = build_real_evidence_remediation_bundle()
    for item in payload.get("items", []):
        row = dict(item or {})
        profile_ids = [str(value or "") for value in (row.get("profileIds") or [])]
        if profile_id not in profile_ids:
            continue
        return {
            "nextStep": str(row.get("nextStep") or ""),
            "recommendedPrimaryCommandLabel": str(row.get("recommendedPrimaryCommandLabel") or ""),
            "recommendedPrimaryCommand": str(row.get("recommendedPrimaryCommand") or ""),
            "recommendedRefreshEvidenceCommand": str(row.get("recommendedRefreshEvidenceCommand") or ""),
            "recommendedPostRefreshRuntimeCommand": str(row.get("recommendedPostRefreshRuntimeCommand") or ""),
            "recommendedRuntimeProbeCommand": str(row.get("recommendedRuntimeProbeCommand") or ""),
            "recommendedLiveUploadCommand": str(row.get("recommendedLiveUploadCommand") or ""),
            "recommendedFastCandidateCommand": str(row.get("recommendedFastCandidateCommand") or ""),
            "recommendedRuntimeSuccessCommand": str(row.get("recommendedRuntimeSuccessCommand") or ""),
            "recommendedOverwriteVariantCommand": str(row.get("recommendedOverwriteVariantCommand") or ""),
        }
    return {}


def main(argv: list[str] | None = None) -> int:
    custom_data_dir = str(os.environ.get("CLOUDPAN_SYNC_DATA_DIR") or "").strip()
    if custom_data_dir:
        configure_data_dir(custom_data_dir)

    parser = argparse.ArgumentParser(
        description="Create and run a live upload task backed by a local file."
    )
    parser.add_argument("--source-provider", default="guangya", help="Source provider. Defaults to guangya.")
    parser.add_argument(
        "--target-provider",
        default="guangya",
        help="Target provider key. Currently supports guangya, aliyundrive_open, 123_open, baidu_netdisk, xunlei, pikpak, quark, and uc.",
    )
    parser.add_argument("--target-profile-id", required=True, help="Saved target auth profile id.")
    parser.add_argument("--target-parent-id", default="", help="Optional target parent id.")
    parser.add_argument("--remote-path", default="/cloudpan-sync-live-upload.bin", help="Remote path for the upload task.")
    parser.add_argument("--local-file", default="", help="Existing local file path.")
    parser.add_argument("--auto-temp-file", action="store_true", help="Create a tiny temporary local file automatically.")
    parser.add_argument("--threshold-mb", type=int, default=1, help="Fallback threshold MB, default 1 to force download_upload when fast inputs are missing.")
    parser.add_argument("--conflict-policy", default="auto_rename_new", help="Conflict policy.")
    parser.add_argument("--acknowledge-download-upload", action="store_true", help="Explicitly acknowledge download_upload fallback risk. Defaults to true for this helper.")
    parser.add_argument("--no-acknowledge-download-upload", action="store_true", help="Do not auto-acknowledge download_upload fallback risk.")
    parser.add_argument("--task-json-output", default="", help="Optional output path for the task JSON snapshot.")
    parser.add_argument("--markdown-output", default="", help="Optional output path for the task markdown snapshot.")
    parser.add_argument("--auth-evidence-output", default="", help="Optional output path for auth profile evidence markdown.")
    parser.add_argument("--evidence-dir", default="", help="Optional output directory for the full evidence bundle.")
    parser.add_argument("--no-refresh-auth-evidence", action="store_true", help="Do not refresh auth validation/probe before exporting auth evidence.")
    parser.add_argument("--runtime-evidence-output", default="", help="Optional output path for runtime evidence markdown.")
    parser.add_argument("--real-evidence-output", default="", help="Optional output path for real evidence markdown.")
    parser.add_argument("--remediation-output", default="", help="Optional output path for remediation markdown.")
    args = parser.parse_args(argv)

    target_provider = str(args.target_provider or "").strip()
    if target_provider not in {"guangya", "aliyundrive_open", "123_open", "baidu_netdisk", "xunlei", "pikpak", "quark", "uc"}:
        raise SystemExit(f"unsupported_live_upload_provider: {target_provider}")

    target_profile_id = str(args.target_profile_id or "").strip()
    resolved_target_parent_id = _resolve_target_parent_id(target_profile_id, str(args.target_parent_id or "").strip())
    file_path, is_temp = _ensure_local_file(str(args.local_file or "").strip(), bool(args.auto_temp_file))
    entry = _build_entry(file_path, str(args.remote_path or "/cloudpan-sync-live-upload.bin"))
    acknowledge_download_upload = True
    if bool(args.no_acknowledge_download_upload):
        acknowledge_download_upload = False
    elif bool(args.acknowledge_download_upload):
        acknowledge_download_upload = True

    payload = TaskCreateRequest(
        sourceProvider=str(args.source_provider or "guangya").strip(),
        targetProvider=target_provider,
        targetProfileId=target_profile_id,
        targetParentId=resolved_target_parent_id,
        thresholdMB=max(0, int(args.threshold_mb or 0)),
        conflictPolicy=str(args.conflict_policy or "auto_rename_new"),
        acknowledgeDownloadUpload=acknowledge_download_upload,
        selectedRoots=[],
        entries=[entry],
    )
    task = task_runtime.create_task(payload)
    result = task_runtime.run_task(str(task.get("taskId") or ""))

    evidence_dir = _resolve_evidence_output_dir(str(args.evidence_dir or "").strip())
    task_json_output = str(args.task_json_output or "").strip()
    markdown_output_arg = str(args.markdown_output or "").strip()
    auth_evidence_output_arg = str(args.auth_evidence_output or "").strip()
    runtime_evidence_output_arg = str(args.runtime_evidence_output or "").strip()
    real_evidence_output_arg = str(args.real_evidence_output or "").strip()
    remediation_output_arg = str(args.remediation_output or "").strip()
    if evidence_dir is not None:
        if not task_json_output:
            task_json_output = str(evidence_dir / "task.json")
        if not markdown_output_arg:
            markdown_output_arg = str(evidence_dir / "task.md")
        if not auth_evidence_output_arg:
            auth_evidence_output_arg = str(evidence_dir / "auth_evidence.md")
        if not runtime_evidence_output_arg:
            runtime_evidence_output_arg = str(evidence_dir / "runtime_evidence.md")
        if not real_evidence_output_arg:
            real_evidence_output_arg = str(evidence_dir / "real_evidence.md")
        if not remediation_output_arg:
            remediation_output_arg = str(evidence_dir / "remediation.md")

    if task_json_output:
        output_path = Path(task_json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    markdown_output = _write_optional_text(markdown_output_arg, task_runtime.task_to_markdown(result))
    refresh_auth_evidence = not bool(args.no_refresh_auth_evidence)
    auth_evidence_output = _write_optional_text(
        auth_evidence_output_arg,
        _auth_evidence_markdown(target_profile_id, refresh_auth_evidence),
    ) if auth_evidence_output_arg else ""
    runtime_evidence_output = _write_optional_text(
        runtime_evidence_output_arg,
        task_runtime_evidence_to_markdown(build_task_runtime_evidence_payload()),
    )
    real_evidence_output = _write_optional_text(
        real_evidence_output_arg,
        real_evidence_to_markdown(build_real_evidence_report()),
    )
    remediation_output = _write_optional_text(
        remediation_output_arg,
        real_evidence_remediation_to_markdown(build_real_evidence_remediation_bundle()),
    )

    output = {
        "taskId": str(result.get("taskId") or ""),
        "state": str(result.get("state") or ""),
        "targetProvider": str(result.get("targetProvider") or ""),
        "targetProfileId": str(result.get("targetProfileId") or ""),
        "resolvedTargetParentId": resolved_target_parent_id,
        "sourceEntries": list(result.get("sourceEntries") or []),
        "results": list(result.get("results") or []),
        "summary": dict(result.get("summary") or {}),
        "usedTempFile": is_temp,
        "localFile": str(file_path),
        "acknowledgedDownloadUpload": acknowledge_download_upload,
        "taskJsonOutput": task_json_output,
        "evidenceDir": str(evidence_dir) if evidence_dir is not None else "",
        "markdownOutput": markdown_output,
        "refreshedAuthEvidence": refresh_auth_evidence,
        "authEvidenceOutput": auth_evidence_output,
        "runtimeEvidenceOutput": runtime_evidence_output,
        "realEvidenceOutput": real_evidence_output,
        "remediationOutput": remediation_output,
        "remediationFollowup": _remediation_followup(target_profile_id),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if is_temp and file_path.exists():
        file_path.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
