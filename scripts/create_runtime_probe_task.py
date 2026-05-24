from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from hashlib import md5
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


def _ensure_local_file(local_file: str, auto_temp_file: bool) -> tuple[Path, bool]:
    if local_file:
        path = Path(local_file)
        if not path.exists() or not path.is_file():
            raise SystemExit(f"local_file_not_found: {path}")
        return path, False
    if not auto_temp_file:
        raise SystemExit("Either --local-file or --auto-temp-file is required.")
    fd, raw_path = tempfile.mkstemp(prefix="cloudpan-sync-runtime-", suffix=".bin")
    path = Path(raw_path)
    with os.fdopen(fd, "wb") as handle:
        handle.write(b"cloudpan-sync-runtime-probe")
    return path, True


def _build_entry(path: Path, remote_path: str, include_md5: bool) -> SourceEntry:
    payload = path.read_bytes()
    return SourceEntry(
        path=remote_path,
        size=path.stat().st_size,
        md5=md5(payload).hexdigest() if include_md5 else "",
        localPath=str(path),
    )


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


def main(argv: list[str] | None = None) -> int:
    custom_data_dir = str(os.environ.get("CLOUDPAN_SYNC_DATA_DIR") or "").strip()
    if custom_data_dir:
        configure_data_dir(custom_data_dir)

    parser = argparse.ArgumentParser(description="Create and run a lightweight runtime probe task.")
    parser.add_argument("--source-provider", default="", help="Source provider. Defaults to target provider.")
    parser.add_argument("--target-provider", required=True, help="Target provider key.")
    parser.add_argument("--target-profile-id", required=True, help="Saved target auth profile id.")
    parser.add_argument("--target-parent-id", default="", help="Optional target parent id.")
    parser.add_argument("--remote-path", default="/cloudpan-sync-runtime-probe.bin", help="Remote path for the probe entry.")
    parser.add_argument("--local-file", default="", help="Existing local file path.")
    parser.add_argument("--auto-temp-file", action="store_true", help="Create a tiny temporary local file automatically.")
    parser.add_argument("--threshold-mb", type=int, default=1, help="Fallback threshold MB, default 1 to prefer download_upload probe.")
    parser.add_argument("--conflict-policy", default="auto_rename_new", help="Conflict policy.")
    parser.add_argument("--include-md5", action="store_true", help="Include md5 in source entry to allow fast_upload planning if desired.")
    args = parser.parse_args(argv)

    target_provider = str(args.target_provider or "").strip()
    target_profile_id = str(args.target_profile_id or "").strip()
    resolved_target_parent_id = _resolve_target_parent_id(
        target_profile_id,
        target_provider,
        str(args.target_parent_id or "").strip(),
    )
    file_path, is_temp = _ensure_local_file(str(args.local_file or "").strip(), bool(args.auto_temp_file))
    entry = _build_entry(file_path, str(args.remote_path or "/cloudpan-sync-runtime-probe.bin"), bool(args.include_md5))
    payload = TaskCreateRequest(
        sourceProvider=str(args.source_provider or target_provider or "").strip(),
        targetProvider=target_provider,
        targetProfileId=target_profile_id,
        targetParentId=resolved_target_parent_id,
        thresholdMB=max(0, int(args.threshold_mb or 0)),
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
