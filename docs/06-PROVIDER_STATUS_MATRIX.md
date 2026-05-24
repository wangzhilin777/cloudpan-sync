# CloudPan Sync Provider Status Matrix

- GeneratedAt: `2026-05-24T16:21:00.179617+00:00`
- Summary: providerCount=10, authReadyCount=0, createDirReadyCount=10, fastCheckCount=10, liveProbeOkCount=0, conflictAwareProviderCount=1, overwriteReadyCount=0, autoRenameReadyCount=1, overwriteDowngradeCount=1, overwriteSupportedCount=0, autoRenameSupportedCount=1, autoRenameProbeOnlyCount=8, conflictUnsupportedProviderCount=1, taskRuntimeEvidenceProviderCount=0, taskRuntimeFailedProviderCount=0, taskRuntimeSampleCount=0, taskRuntimeSuccessCount=0, taskRuntimeFailedCount=0, taskRuntimeBlockedProviderCount=0, taskRuntimeBlockedEvidenceCount=0, taskRuntimeConflictHandledProviderCount=0, taskRuntimeConflictHandledCount=0, taskRuntimeActiveCount=9, taskRuntimeCandidateCount=1, taskRuntimeBlockedCount=0

| providerKey | supportStatus | auth_ready | list_ready | metadata_ready | create_dir_ready | fast_check | live_probe_ok | task_runtime_track | task_runtime_samples | task_runtime_success | task_runtime_failed | task_runtime_blocked | task_runtime_conflict_handled | supports_overwrite | supports_auto_rename | overwrite_behavior | overwrite_support_status | auto_rename_support_status | conflict_policies | fallback_ready |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 115_open | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | 0 | 0 | False | False | not_implemented | unsupported | probe_only_runtime_write_check | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a 115 Open live create_dir write probe for download_upload items and a probe-only sha1 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 115 Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |
|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 115 Open task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet. |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 115 Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |  |  |
| 123_open | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | 0 | 0 | False | False | not_implemented | unsupported | probe_only_runtime_write_check | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a 123Pan Open live create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 123Pan Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |
|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 123Pan Open task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet. |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 123Pan Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |  |  |
| 189cloud | list_ready | False | True | True | True | True | False | runtime_candidate | 0 | 0 | 0 | 0 | 0 | False | False | readonly_auth_blocked | unsupported | unsupported | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime can now attempt 189Cloud create_dir with account-level OAuth headers and a probe-only md5 fast-upload candidate check when account-level write auth is present, but shareCode/accessCode-only profiles still remain read-only and no successful runtime sample has been verified yet. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 189Cloud 已接入账号级 create_dir 写目录尝试，但 shareCode/accessCode-only 档案仍然只读，真实文件上传与同名冲突处理仍未声明为已支持。 |  |  |  |
|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 189Cloud 已接入账号级 create_dir 写目录尝试，但 shareCode/accessCode-only 档案仍然只读，真实文件上传与同名冲突处理仍未声明为已支持。 |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 189Cloud 已接入账号级 create_dir 写目录尝试，但 shareCode/accessCode-only 档案仍然只读，真实文件上传与同名冲突处理仍未声明为已支持。 |  |  |  |  |  |
| aliyundrive_open | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | 0 | 0 | False | False | not_implemented | unsupported | probe_only_runtime_write_check | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives an Aliyun Drive Open live create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Aliyun Drive Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |
|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Aliyun Drive Open task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet. |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Aliyun Drive Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |  |  |
| baidu_netdisk | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | 0 | 0 | False | False | not_implemented | unsupported | probe_only_runtime_write_check | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live Baidu Netdisk create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Baidu Netdisk 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |
|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Baidu Netdisk task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet. |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Baidu Netdisk 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |  |  |
| guangya | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | 0 | 0 | False | True | downgrade_to_auto_rename | downgrade_to_auto_rename | supported | overwrite_existing, auto_rename_new | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime already drives Guangya live fast-check and fallback upload attempts. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | The current target provider path does not guarantee true overwrite, so overwrite_existing will downgrade to auto_rename_new. |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Guangya fallback 上传链路已接受 overwrite_existing / auto_rename_new，但 overwrite_existing 仍会诚实降级为 auto_rename_new。 |  |  |  |  |  |
| pikpak | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | 0 | 0 | False | False | not_implemented | unsupported | probe_only_runtime_write_check | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live PikPak create_dir write probe for download_upload items and a probe-only gcid fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 PikPak 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |
|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | PikPak task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet. |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 PikPak 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |  |  |
| quark | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | 0 | 0 | False | False | not_implemented | unsupported | probe_only_runtime_write_check | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live Quark create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Quark 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |
|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Quark task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet. |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Quark 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |  |  |
| uc | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | 0 | 0 | False | False | not_implemented | unsupported | probe_only_runtime_write_check | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live UC Drive create_dir write probe for download_upload items and a probe-only md5 fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 UC Drive 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |
|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | UC Drive task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet. |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 UC Drive 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |  |  |
| xunlei | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | 0 | 0 | False | False | not_implemented | unsupported | probe_only_runtime_write_check | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live Xunlei create_dir write probe for download_upload items and a probe-only gcid fast-upload candidate check for fast_upload items; real rapid-upload API execution is still not wired yet. |  |  |  |  |  |  |  |  |  |  |  |
|  | overwrite_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Xunlei 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |
|  | auto_rename_note |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Xunlei task runtime can now perform a live create_dir write probe, but same-name file handling for real file upload is not declared yet. |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Xunlei 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |  |  |  |
