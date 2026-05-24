from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from hashlib import md5, sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_profile_view import auth_profile_view
from cloudpan_sync.auth_store import get_profile
from cloudpan_sync import task_runtime
from cloudpan_sync.models import SourceEntry, TaskCreateRequest
from cloudpan_sync.provider_registry import get_provider_profile


def _ensure_local_file(local_file: str, auto_temp_file: bool) -> tuple[Path, bool]:
    if local_file:
        path = Path(local_file)
        if not path.exists() or not path.is_file():
            raise SystemExit(f"local_file_not_found: {path}")
        return path, False
    if not auto_temp_file:
        raise SystemExit("Either --local-file or --auto-temp-file is required.")
    fd, raw_path = tempfile.mkstemp(prefix="cloudpan-sync-fast-candidate-", suffix=".bin")
    path = Path(raw_path)
    with os.fdopen(fd, "wb") as handle:
        handle.write(b"cloudpan-sync-fast-candidate")
    return path, True


def _provider_root_parent_id(provider_key: str) -> str:
    mapping = {
        "aliyundrive_open": "root",
        "123_open": "0",
        "115_open": "0",
        "quark": "0",
        "uc": "0",
        "baidu_netdisk": "/",
    }
    return str(mapping.get(str(provider_key or ""), ""))


def _resolve_target_parent_id(profile_id: str, target_provider: str, explicit_parent_id: str) -> str:
    if explicit_parent_id:
        return explicit_parent_id
    profile = get_profile(profile_id)
    if profile is None:
        return _provider_root_parent_id(target_provider)
    profile_view = auth_profile_view(profile)
    resolved = str(profile_view.get("resolvedParentId") or "").strip()
    if resolved:
        return resolved
    return _provider_root_parent_id(target_provider)


def _pick_hash(raw_value: str, auto_value: str) -> str:
    value = str(raw_value or "").strip()
    if value.lower() == "auto":
        return auto_value
    return value


def _build_entry(
    *,
    path: Path,
    source_path: str,
    md5_value: str,
    sha1_value: str,
    gcid_value: str,
) -> SourceEntry:
    payload = path.read_bytes()
    auto_md5 = md5(payload).hexdigest()
    auto_sha1 = sha1(payload).hexdigest()
    return SourceEntry(
        path=source_path,
        size=path.stat().st_size,
        md5=_pick_hash(md5_value, auto_md5),
        sha1=_pick_hash(sha1_value, auto_sha1),
        gcid=str(gcid_value or "").strip().upper(),
        localPath=str(path),
    )


def _required_fast_inputs(provider_key: str) -> list[str]:
    profile = get_provider_profile(provider_key)
    if profile is None:
        return []
    return [str(item or "") for item in list(profile.fastUploadInputs or []) if str(item or "")]


def main(argv: list[str] | None = None) -> int:
    custom_data_dir = str(os.environ.get("CLOUDPAN_SYNC_DATA_DIR") or "").strip()
    if custom_data_dir:
        configure_data_dir(custom_data_dir)

    parser = argparse.ArgumentParser(description="Create and run a lightweight fast-upload candidate task.")
    parser.add_argument("--source-provider", default="", help="Source provider. Defaults to target provider.")
    parser.add_argument("--target-provider", required=True, help="Target provider key.")
    parser.add_argument("--target-profile-id", required=True, help="Saved target auth profile id.")
    parser.add_argument("--target-parent-id", default="", help="Optional target parent id.")
    parser.add_argument("--source-path", default="/cloudpan-sync-fast-candidate.bin", help="Logical source path for the candidate item.")
    parser.add_argument("--local-file", default="", help="Existing local file path.")
    parser.add_argument("--auto-temp-file", action="store_true", help="Create a tiny temporary local file automatically.")
    parser.add_argument("--conflict-policy", default="auto_rename_new", help="Conflict policy.")
    parser.add_argument("--md5", default="auto", help='Fingerprint md5. Use "auto" to compute from local file.')
    parser.add_argument("--sha1", default="", help='Fingerprint sha1. Use "auto" to compute from local file.')
    parser.add_argument("--gcid", default="", help="Fingerprint gcid. Required for gcid-based candidate providers.")
    args = parser.parse_args(argv)

    target_provider = str(args.target_provider or "").strip()
    target_profile_id = str(args.target_profile_id or "").strip()
    resolved_target_parent_id = _resolve_target_parent_id(
        target_profile_id,
        target_provider,
        str(args.target_parent_id or "").strip(),
    )
    file_path, is_temp = _ensure_local_file(str(args.local_file or "").strip(), bool(args.auto_temp_file))
    entry = _build_entry(
        path=file_path,
        source_path=str(args.source_path or "/cloudpan-sync-fast-candidate.bin"),
        md5_value=str(args.md5 or ""),
        sha1_value=str(args.sha1 or ""),
        gcid_value=str(args.gcid or ""),
    )
    payload = TaskCreateRequest(
        sourceProvider=str(args.source_provider or target_provider or "").strip(),
        targetProvider=target_provider,
        targetProfileId=target_profile_id,
        targetParentId=resolved_target_parent_id,
        thresholdMB=0,
        conflictPolicy=str(args.conflict_policy or "auto_rename_new"),
        selectedRoots=[],
        entries=[entry],
    )
    task = task_runtime.create_task(payload)
    result = task_runtime.run_task(str(task.get("taskId") or ""))
    output = {
        "taskId": str(result.get("taskId") or ""),
        "state": str(result.get("state") or ""),
        "targetProvider": str(result.get("targetProvider") or ""),
        "targetProfileId": str(result.get("targetProfileId") or ""),
        "resolvedTargetParentId": resolved_target_parent_id,
        "requiredFastInputs": _required_fast_inputs(target_provider),
        "sourceEntries": list(result.get("sourceEntries") or []),
        "results": list(result.get("results") or []),
        "summary": dict(result.get("summary") or {}),
        "usedTempFile": is_temp,
        "localFile": str(file_path),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if is_temp and file_path.exists():
        file_path.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
