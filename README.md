# CloudPan Sync

CloudPan Sync is a cross-provider cloud transfer console.

CloudPan Sync 是一个面向常用网盘之间互传的控制台，当前重点是把“授权、目录读取、元数据/Fingerprint 获取、互传规划、受控 fallback、风险阻断、证据导出”先做扎实，而不是过早宣称所有 provider 都已经稳定可用。

## Overview

- `Goal / 目标`
  Build a practical console for transfers between mainstream cloud providers, not a single-target uploader.
- `Current focus / 当前重点`
  Fast-upload planning first, guarded fallback second, evidence-first validation throughout.
- `Current status / 当前状态`
  Core project skeleton, auth system, planner, guarded task flow, and multi-provider live-attempt adapters are in place.
- `Current boundary / 当前边界`
  Some providers already have live attempt paths, but real stable end-to-end success evidence is still incomplete; the repo does not overclaim `P-REAL`.

## Progress Snapshot

- Plan audit status: `done=5` `partial=2` `todo=1`
- Feature completion ratio: about `85.7%`
- Strict completion ratio: about `75.0%`
- Current incomplete high-value gaps:
  - `M4` Guangya still lacks stable real online success samples
  - `M5` first-batch providers still lack enough real success evidence
  - `P-REAL` real cross-provider validation is not complete yet

See:

- [Plan Audit Report](E:/Workspace/VSCode/CloudPan%20Sync/docs/04-PLAN_AUDIT_REPORT.md)
- [Completed Milestones](E:/Workspace/VSCode/CloudPan%20Sync/docs/02-COMPLETED_MILESTONES.md)
- [Merged Project Plan](E:/Workspace/VSCode/CloudPan%20Sync/docs/01-PROJECT_PLAN_MERGED_RAW.md)

## What Works Now

- Provider registry and capability model for current `10` providers
- Fingerprint normalization: `md5 / sha1 / sha256 / crc64 / gcid / etag / pickcode / blockListMd5 / raw`
- Provider-aware auth validation and readiness hints
- Mock transfer planning with:
  - `selectedRoots`
  - `executionGroups`
  - `pendingItems`
  - conflict policy preview
  - fast-upload input explanation
- Task conflict policy:
  - `overwrite_existing`
  - `auto_rename_new`
- Honest downgrade when a target path cannot guarantee true overwrite
- Frontend queue preview, task guard, acknowledgement flow, and task action state machine
- Evidence export and remediation docs for saved auth profiles
- Task detail Markdown export via `GET /api/tasks/{id}/markdown` or `scripts/export_task_markdown.py --task-json <task-snapshot.json>`
- Guangya live upload helper via `scripts/create_live_upload_task.py --evidence-dir <dir>` for refreshing latest auth validation/probe evidence and producing a fixed-file evidence bundle
- Runtime probe and fast-candidate helpers now also support `--evidence-dir <dir>` for producing the same fixed-file evidence bundle shape

## Honest Boundaries

- `189cloud` current share-based path is still read-only for write operations
- Guangya current overwrite path is still an honest downgrade to auto rename, not verified in-place overwrite
- Real provider success is not claimed unless there is current code or script evidence
- This repo currently prefers controlled fallback and explicit warning states over silent “best effort”

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
cloudpan-sync
```

Open `http://127.0.0.1:8765`.

Recommended local verification order:

```powershell
.venv\Scripts\python.exe scripts\verify_auth_live_validation.py
.venv\Scripts\python.exe scripts\verify_queue_plan_preview_ui.py
.venv\Scripts\python.exe scripts\verify_task_action_guards.py
.venv\Scripts\python.exe scripts\verify_task_views_api.py
.venv\Scripts\python.exe scripts\verify_export_task_markdown.py
.venv\Scripts\python.exe scripts\verify_create_live_upload_task.py
```

## Default Admin Password

Use environment variable `CLOUDPAN_SYNC_ADMIN_PASSWORD`.

If missing, default password is `admin123`.

## Auth Validation

`POST /api/auth/profiles/{profileId}/validate` now runs a provider-aware minimal live validation instead of only checking whether token or cookie text exists.

`POST /api/auth/profiles` now also runs the same minimal validation during save and returns both the masked profile and the structured `validation` result.

Current behavior:

- it reuses the repo's live probe adapters and provider-specific default fields from the saved auth profile
- it attempts the smallest safe read path first, usually `list`, and includes `metadata` only when the saved profile already contains `extra.fileId`
- it writes a structured record to `GET /api/auth/live_validations`
- `GET /api/auth/live_validations` now returns `items`, `latestItems`, and `summary`
- it also updates the auth profile status to `verified` or `invalid` using the returned live result
- the auth form now switches `authMode` options from the selected provider's real `authModes` list, including `official_oauth` where supported
- the auth list now exposes live probe actions for the current 10-provider live-attempt set

For a repeatable local verification of this flow, run:

```powershell
.venv\Scripts\python.exe scripts\verify_auth_live_validation.py
```

## Guangya Live List

The Guangya provider keeps local mock listing as the safe default.

If you want to try a real Guangya directory listing, save an auth profile with:

- `token` or `extra.authorization`
- `extra.did`
- `extra.dt`
- `extra.parentId`
- optional `extra.pageSize`
- optional `extra.fileId`
- optional `extra.dirName`

Then call `POST /api/providers/guangya/list` with `profileId` and `preferLive=true`.

If you also provide `extra.fileId`, you can call:

- `POST /api/providers/guangya/metadata` with `profileId`, `fileId`, and `preferLive=true`
- `POST /api/providers/guangya/create_dir` with `profileId`, `parentId`, and `dirName`

When live listing fails, the API falls back to mock mode and returns the fallback reason instead of pretending the live request succeeded.

## Guangya Live Fast-Upload Check

The `guangya` provider now also exposes a live fast-upload inventory check when the saved auth profile includes:

- `token` or `extra.authorization`
- `extra.parentId`
- optional `extra.did`
- optional `extra.dt`

Then call `POST /api/providers/guangya/live_fast_check` with:

```json
{
  "profileId": "saved-guangya-profile-id",
  "parentId": "optional-parent-id",
  "entries": [
    {
      "path": "/demo.bin",
      "size": 123,
      "md5": "e10adc3949ba59abbe56e057f20f883e",
      "gcid": ""
    }
  ]
}
```

Behavior notes:

- MD5 rows try `get_res_center_token` and report a provider-side instant-hit when code `156` is returned.
- GCID rows continue to `check_can_flash_upload` when the first step returns a `taskId`.
- Missed temporary upload tasks are cleaned with `delete_upload_task` when possible.
- This is a real online attempt, not the local-only `fast_check` hash normalization result.

## Aliyun Drive Open Live List and Metadata

The `aliyundrive_open` provider now supports a real list/get attempt when the saved auth profile includes:

- `token` or `extra.authorization`
- `extra.domainId`
- `extra.driveId`

Then you can call:

- `POST /api/providers/aliyundrive_open/list` with `profileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/aliyundrive_open/metadata` with `profileId`, `fileId`, and `preferLive=true`
- `POST /api/providers/aliyundrive_open/create_dir` with `profileId`, optional `parentId`, and `dirName`

If the live API rejects the request or required fields are missing, the backend falls back to mock data and returns the fallback reason.

## 189Cloud Live List and Metadata

The `189cloud` provider now supports a real share-based read attempt when the saved auth profile includes:

- `extra.shareCode`
- optional `extra.accessCode`
- optional `extra.fileId`
- optional `extra.pathPrefix`

Then you can call:

- `POST /api/providers/189cloud/list` with `profileId`, optional `fileId`, and `preferLive=true`
- `POST /api/providers/189cloud/metadata` with `profileId`, `fileId`, and `preferLive=true`

## Baidu Netdisk Conservative Live List, Metadata, and Create Folder

The `baidu_netdisk` provider now supports conservative live attempts when the saved auth profile includes:

- `token` or `extra.authorization`, or
- `cookie`, or `extra.cookie_header`
- optional `extra.fileId`
- optional `extra.path`

Then you can call:

- `POST /api/providers/baidu_netdisk/list` with `profileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/baidu_netdisk/metadata` with `profileId`, optional `fileId`, optional `path`, and `preferLive=true`
- `POST /api/providers/baidu_netdisk/create_dir` with `profileId`, optional `parentId`, and `dirName`

Current boundary:

- this path currently targets a conservative `pan.baidu.com/rest/2.0/xpan/file` live attempt
- metadata prefers direct lookup and can fall back to parent-directory search when only path is available
- this provider remains high risk-control and the repo does not claim stable real-world coverage yet

## 123Pan Open Live List, Metadata, and Create Folder

The `123_open` provider now supports token-based live attempts when the saved auth profile includes:

- `token` or `extra.authorization`
- optional `extra.parentFileId`
- optional `extra.fileId`

Then you can call:

- `POST /api/providers/123_open/list` with `profileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/123_open/metadata` with `profileId`, `fileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/123_open/create_dir` with `profileId`, optional `parentId`, and `dirName`

Current boundary:

- metadata currently resolves the file by scanning the provided `parentFileId` page
- this is a real API attempt path, but stable real-world samples are still pending

## 115 Live List, Metadata, and Create Folder

The `115_open` provider now supports cookie-based live attempts when the saved auth profile includes:

- `cookie`, or `extra.cookie_header`
- optional `extra.fileId`
- optional `extra.parentId` or `extra.cid`

Then you can call:

- `POST /api/providers/115_open/list` with `profileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/115_open/metadata` with `profileId`, `fileId`, and `preferLive=true`
- `POST /api/providers/115_open/create_dir` with `profileId`, optional `parentId`, and `dirName`

Current boundary:

- this path uses observed web APIs (`webapi.115.com/files`, `files/get_info`, `files/add`) rather than a fully validated official open-platform binding
- stable real-world samples are still pending

## Xunlei Live List, Metadata, and Create Folder

The `xunlei` provider now supports header-based live attempts when the saved auth profile includes:

- `token` or `extra.authorization`
- `extra.deviceId` or `extra.x-device-id`
- optional `extra.captchaToken`
- optional `extra.clientId`

Then you can call:

- `POST /api/providers/xunlei/list` with `profileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/xunlei/metadata` with `profileId`, `fileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/xunlei/create_dir` with `profileId`, optional `parentId`, and `dirName`

Current boundary:

- metadata currently resolves the file by scanning the provided `parentId` page
- upload chain is not connected yet

## PikPak Live List, Metadata, and Create Folder

The `pikpak` provider now supports token-based live attempts when the saved auth profile includes:

- `token` or `extra.authorization`
- optional `extra.deviceId`
- optional `extra.captchaToken`
- optional `extra.fileId`

Then you can call:

- `POST /api/providers/pikpak/list` with `profileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/pikpak/metadata` with `profileId`, `fileId`, and `preferLive=true`
- `POST /api/providers/pikpak/create_dir` with `profileId`, optional `parentId`, and `dirName`

Current boundary:

- this path currently targets the observed `api-drive.mypikpak.com` drive APIs
- metadata currently reads direct file detail and can surface `gcid` when the provider returns it
- stable real-world samples and fast-transfer evidence are still pending

## Quark Share Live List and Metadata

The `quark` provider now supports share-based live attempts when the saved auth profile includes:

- `cookie`, or `extra.cookie_header`
- `extra.pwdId` or `extra.sharePwdId`
- optional `extra.passcode`
- optional `extra.fileId`

Then you can call:

- `POST /api/providers/quark/list` with `profileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/quark/metadata` with `profileId`, `fileId`, optional `parentId`, and `preferLive=true`

Current boundary:

- this path is currently based on Quark share APIs instead of a general logged-in personal-drive adapter
- metadata MD5 comes from the `file/download` lookup after share detail succeeds
- `create_dir` and upload chain are not connected yet

## UC Share Live List and Metadata

The `uc` provider now supports share-based live attempts when the saved auth profile includes:

- `cookie`, or `extra.cookie_header`
- `extra.pwdId` or `extra.sharePwdId`
- optional `extra.passcode`
- optional `extra.fileId`

Then you can call:

- `POST /api/providers/uc/list` with `profileId`, optional `parentId`, and `preferLive=true`
- `POST /api/providers/uc/metadata` with `profileId`, `fileId`, optional `parentId`, and `preferLive=true`

Current boundary:

- this path is currently based on UC share APIs instead of a general logged-in personal-drive adapter
- metadata MD5 comes from the `file/download` lookup after share detail succeeds
- `create_dir` and upload chain are not connected yet

## Unified Provider Live Probe

For providers that already have a live adapter, you can call:

- `POST /api/providers/live_probe_profile`
- `GET /api/providers/live_probe_results`

Request body:

```json
{
  "profileId": "saved-profile-id",
  "parentId": "optional-parent-id",
  "fileId": "optional-file-id",
  "pageSize": 100,
  "dirName": "optional-live-create-dir-name"
}
```

Current support:

- `guangya`: live list probe, live metadata probe when `fileId` is provided, live create_dir probe when `dirName` is provided
- `aliyundrive_open`: live list probe, live metadata probe when `fileId` is provided, live create_dir probe when `dirName` is provided
- `189cloud`: live list probe and share-page metadata probe using saved `shareCode`, optional `accessCode`, and optional `fileId`
- `baidu_netdisk`: conservative live list probe, metadata probe, and live create_dir probe
- `123_open`: live list probe, parent-scoped metadata probe, and live create_dir probe
- `115_open`: live list probe, metadata probe, and live create_dir probe
- `xunlei`: live list probe, parent-scoped metadata probe, and live create_dir probe
- `pikpak`: live list probe, direct metadata probe, and live create_dir probe
- `quark`: share-based live list probe and MD5-aware metadata probe
- `uc`: share-based live list probe and MD5-aware metadata probe

`GET /api/providers/live_probe_results` now returns `items`, `latestItems`, and `summary` for the saved profile-level probe records.

For the current local controllable verification bundle, run:

```powershell
.venv\Scripts\python.exe scripts\verify_provider_live_adapters.py
.venv\Scripts\python.exe scripts\export_local_live_adapter_verification.py
```

This script replays the repository's stub-backed checks for the current 10-provider live-attempt set (`guangya`, `aliyundrive_open`, `189cloud`, `baidu_netdisk`, `123_open`, `115_open`, `xunlei`, `pikpak`, `quark`, `uc`) and prints the expected probe counts plus status-matrix-ready flags.
The export script writes the current Markdown snapshot to `docs/07-LOCAL_LIVE_ADAPTER_VERIFICATION.md`.

## Task Runtime Live Fast-Upload Attempt

`POST /api/tasks` now accepts optional `targetProfileId`.

When all of these are true:

- `targetProvider` is `guangya`
- `targetProfileId` points to a saved Guangya auth profile
- the planned item strategy is `fast_upload`

the current task runtime will try `guangya live_fast_check` during `run` instead of treating `fast_upload` as a mock-only completed step.

Behavior notes:

- live hit rows are marked `done`
- inventory miss rows are marked `failed`
- per-item outcomes are returned in `item.results`
- tasks without `targetProfileId` keep the existing lightweight mock/runtime behavior

`SourceEntry` also accepts optional `localPath`.

When all of these are true:

- the task item strategy is `download_upload`
- `targetProvider` is `guangya`
- `targetProfileId` is provided
- `entries[*].localPath` points to an existing local file

the current runtime will verify the local file, derive MD5 when needed, and try a Guangya fallback live metadata import before declaring the item blocked.

Current boundary:

- provider inventory hit: mark the item `done`
- provider inventory miss: mark the item `failed`
- real binary upload after the miss is still not implemented yet

## Queue UI Task Form

The queue page now exposes a lightweight task form for runtime smoke checks.

Current form fields:

- `sourceProvider`
- `targetProvider`
- `targetProfileId`
- `targetParentId`
- `sourcePath`
- `localPath`
- `md5`
- `size`
- `thresholdMB`

Current behavior notes:

- `targetProfileId` is echoed back in task rows and is used by Guangya runtime live attempts
- `targetParentId` can override `auth profile extra.parentId` for Guangya binary upload
- `localPath` is passed through to `entries[*].localPath` so Guangya fallback can inspect a real local file
- task result rows now surface live-attempt risk hints instead of only a generic failed note

## Guangya Binary Upload Fallback

For `download_upload` task items targeting `guangya`, the runtime now does this:

1. Try Guangya live fast-upload inventory check first.
2. If inventory misses and `entries[*].localPath` points to a real local file, try real Guangya binary upload.
3. Prefer `guangyaclient.file_upload`.
4. If the direct path returns `400`, fall back to `upload_token -> check_can_flash_upload -> cdn_upload -> upload_info`.

Current requirements:

- installed `guangyaclient>=0.0.2`
- saved Guangya auth profile with `token` or `extra.authorization`
- `targetProfileId`
- `localPath`
- `extra.parentId` on the auth profile, or another way to provide the Guangya target parent directory

Current boundary:

- this is a real upload chain, not a mock completion
- the repo still does not claim stable real-world success coverage until live authenticated samples are preserved
