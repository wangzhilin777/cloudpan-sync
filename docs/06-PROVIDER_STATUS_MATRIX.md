# CloudPan Sync Provider Status Matrix

- GeneratedAt: `2026-05-24T11:57:36.596914+00:00`
- Summary: providerCount=10, authReadyCount=0, createDirReadyCount=10, fastCheckCount=10, liveProbeOkCount=0, conflictAwareProviderCount=1, overwriteReadyCount=0, autoRenameReadyCount=1, taskRuntimeEvidenceProviderCount=0, taskRuntimeFailedProviderCount=0, taskRuntimeSampleCount=0, taskRuntimeSuccessCount=0, taskRuntimeFailedCount=0, taskRuntimeActiveCount=9, taskRuntimeCandidateCount=1, taskRuntimeBlockedCount=0

| providerKey | supportStatus | auth_ready | list_ready | metadata_ready | create_dir_ready | fast_check | live_probe_ok | task_runtime_track | task_runtime_samples | task_runtime_success | task_runtime_failed | supports_overwrite | supports_auto_rename | overwrite_behavior | conflict_policies | fallback_ready |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 115_open | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a 115 Open live create_dir write probe for download_upload items and a probe-only sha1 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 115 Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| 123_open | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a 123Pan Open live create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 123Pan Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| 189cloud | list_ready | False | True | True | True | True | False | runtime_candidate | 0 | 0 | 0 | False | False | readonly_auth_blocked | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime can now attempt 189Cloud create_dir with account-level OAuth headers and a probe-only md5 fast-upload candidate check when account-level write auth is present, but shareCode/accessCode-only profiles still remain read-only and no successful runtime sample has been verified yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 189Cloud 已接入账号级 create_dir 写目录尝试，但 shareCode/accessCode-only 档案仍然只读，真实文件上传与同名冲突处理仍未声明为已支持。 |  |  |
| aliyundrive_open | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives an Aliyun Drive Open live create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Aliyun Drive Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| baidu_netdisk | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live Baidu Netdisk create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Baidu Netdisk 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| guangya | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | True | downgrade_to_auto_rename | overwrite_existing, auto_rename_new | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime already drives Guangya live fast-check and fallback upload attempts. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Guangya fallback 上传链路已接受 overwrite_existing / auto_rename_new，但 overwrite_existing 仍会诚实降级为 auto_rename_new。 |  |  |
| pikpak | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live PikPak create_dir write probe for download_upload items and a probe-only gcid fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 PikPak 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| quark | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live Quark create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Quark 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| uc | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live UC Drive create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 UC Drive 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| xunlei | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live Xunlei create_dir write probe for download_upload items and a probe-only gcid fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Xunlei 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
