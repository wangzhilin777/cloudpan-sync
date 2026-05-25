# CloudPan Sync 真实证据状态报告

- 生成时间：`2026-05-25T18:38:55.507447+00:00`
- 汇总： `providerCount=10` `profilesSaved=3` `latestValidationProfileCount=3` `latestProbeProfileCount=4`
- 真实证据覆盖： `auth=0` `list=0` `metadata=0` `create_dir=0` `fully_verified=0` `task_runtime=3` `task_runtime_failed=0` `task_runtime_candidate=0` `task_runtime_probe=0` `runtime_samples=3` `runtime_success=3` `runtime_failed=0` `runtime_candidate=0` `runtime_probe=0` `runtime_blocked_providers=0` `runtime_blocked=0` `runtime_conflict_handled=3`
- providerSummary: `auth=(none)` `list=(none)` `metadata=(none)` `create_dir=(none)` `fully_verified=(none)` `runtime_success=guangya, uc, pikpak` `runtime_failed=(none)` `runtime_candidate=(none)` `runtime_probe=(none)` `runtime_blocked=(none)`

> 说明：本报告只统计当前仓库已保存的最新真实校验/探测证据，不把 mock 成功、静态能力声明或未持久化的临时运行结果算成真实成功。

## guangya - Guangya
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `True` samples=1 success=1 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=1 note=当前已记录到任务运行阶段真实成功样本。
- taskRuntimeProfiles: success=gy-live-1 failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: M4 precheck done; get_file_list, get_res_download_url, create_dir, live fast-upload inventory check, and localPath-driven fallback live attempt in task runtime are available with saved auth profile, but real binary upload and stable online validation still need work.

## aliyundrive_open - Aliyun Drive Open
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `False` samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0 note=当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。
- taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: M5 mock list/metadata online; saved access token plus domainId/driveId can now drive live list/get/create_dir attempts, but real online samples are still pending.

## 115_open - 115 Open
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `False` samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0 note=当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。
- taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: cookie driven live list/metadata(create via webapi.115.com files/get_info/files/add) attempts are online, and task runtime can now drive the full proapi.115.com/open/upload/init plus sign_check plus upload/get_token plus OSS binary upload chain when a usable local file plus sha1 is available; stable real success samples and long-term official open-platform token refresh handling are still pending.

## quark - Quark
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `False` samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0 note=当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。
- taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: share-based live list/metadata(MD5 via file/download) attempts are online from pc-api.uc.cn evidence, cookie-based create_dir attempts are now wired on the Quark PC drive API path, and task runtime can now also drive direct local-file upload by starting with upload/pre + update/hash and continuing into upload/auth + multipart PUT + commit + upload/finish when hash miss occurs; same-name conflicts now support auto_rename_new with overwrite_existing downgraded to auto rename, while stable real online samples are still pending.

## 189cloud - Tianyi 189Cloud
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `False` samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0 note=当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。
- taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: shareCode/accessCode based live list/metadata attempts are online, createFolder.action is now wired for account-level OAuth headers such as AccessToken/Signature/Date, and task runtime can now drive the full createUploadFile -> fileUploadUrl PUT -> getUploadFileStatus -> fileCommitUrl chain when a usable local file plus md5 is available; share-only profiles still remain read-only, while stable real success samples are still pending.

## baidu_netdisk - Baidu Netdisk
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `False` samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0 note=当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。
- taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: access token or cookie can now drive conservative live list/metadata/create_dir attempts on the xpan file API; this provider remains high risk-control and still lacks stable real samples plus fast-transfer evidence.

## uc - UC Drive
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `True` samples=1 success=1 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=1 note=当前已记录到任务运行阶段真实成功样本。
- taskRuntimeProfiles: success=uc-live-1 failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: share-based live list/metadata(MD5 via file/download) attempts are online on the pc-api.uc.cn chain with saved cookie + pwdId, same-stack cookie-based create_dir attempts are now wired, and task runtime can now also drive direct local-file upload by starting with upload/pre + update/hash and continuing into upload/auth + multipart PUT + commit + upload/finish when hash miss occurs; same-name conflicts now support auto_rename_new with overwrite_existing downgraded to auto rename, while stable real online samples are still pending.

## xunlei - Xunlei Drive
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `False` samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0 note=当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。
- taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: token + x-device-id style live list/metadata(parentId-scoped lookup)/create_dir attempts are online from api-pan.xunlei.com evidence, and task runtime can now reuse the same create-by-hash plus resumable binary path for both fast_upload and download_upload items when a usable local file plus gcid is available; same-name conflicts now support auto_rename_new with overwrite_existing downgraded to auto rename, while stable real samples are still pending.

## pikpak - PikPak
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `True` samples=1 success=1 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=1 note=当前已记录到任务运行阶段真实成功样本。
- taskRuntimeProfiles: success=pikpak-live-1 failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: token + optional device headers can now drive live list/metadata/create_dir attempts on api-drive.mypikpak.com, and task runtime can now reuse the same create-by-hash plus resumable binary path for both fast_upload and download_upload items when a usable local file plus gcid is available; same-name conflicts now support auto_rename_new with overwrite_existing downgraded to auto rename, while stable real samples are still pending.

## 123_open - 123Pan Open
- fullyVerified: `False`
- authEvidence: `False` profiles=(none)
- listEvidence: `False` profiles=(none)
- metadataEvidence: `False` profiles=(none)
- createDirEvidence: `False` profiles=(none)
- taskRuntimeEvidence: `False` samples=0 success=0 failed=0 candidate=0 probe=0 blocked=0 conflictHandled=0 note=当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。
- taskRuntimeProfiles: success=(none) failed=(none) candidate=(none) probe=(none)
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- notes: token driven live list/metadata(create via parentFileId-scoped lookup) and create_dir attempts are online; stable real samples and upload chain are still pending.
