# CloudPan Sync Provider Status Matrix

- GeneratedAt: `2026-05-24T08:23:06.756421+00:00`
- Summary: providerCount=10, authReadyCount=0, createDirReadyCount=9, fastCheckCount=5, liveProbeOkCount=0, conflictAwareProviderCount=1, overwriteReadyCount=0, autoRenameReadyCount=1, taskRuntimeEvidenceProviderCount=0, taskRuntimeFailedProviderCount=0, taskRuntimeSampleCount=0, taskRuntimeSuccessCount=0, taskRuntimeFailedCount=0, taskRuntimeActiveCount=7, taskRuntimeCandidateCount=2, taskRuntimeBlockedCount=1

| providerKey | supportStatus | auth_ready | list_ready | metadata_ready | create_dir_ready | fast_check | live_probe_ok | task_runtime_track | task_runtime_samples | task_runtime_success | task_runtime_failed | supports_overwrite | supports_auto_rename | overwrite_behavior | conflict_policies | fallback_ready |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 115_open | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a 115 Open live create_dir write probe before mock/download fallback completion. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 115 Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| 123_open | list_ready | False | True | True | True | False | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a 123Pan Open live create_dir write probe before mock/download fallback completion. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 123Pan Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| 189cloud | list_ready | False | True | True | False | False | False | runtime_blocked | 0 | 0 | 0 | False | False | readonly_auth_blocked | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current 189Cloud path is still shareCode/accessCode read-only, so task runtime write attempts cannot start yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 189Cloud 仅验证到 shareCode/accessCode 只读链路，写入链路未就绪，因此不能承诺覆盖或自动重命名。 |  |  |
| aliyundrive_open | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives an Aliyun Drive Open live create_dir write probe before mock/download fallback completion. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Aliyun Drive Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| baidu_netdisk | list_ready | False | True | True | True | False | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live Baidu Netdisk create_dir write probe before mock/download fallback completion. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Baidu Netdisk 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| guangya | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | True | downgrade_to_auto_rename | overwrite_existing, auto_rename_new | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime already drives Guangya live fast-check and fallback upload attempts. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Guangya fallback 上传链路已接受 overwrite_existing / auto_rename_new，但 overwrite_existing 仍会诚实降级为 auto_rename_new。 |  |  |
| pikpak | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live PikPak create_dir write probe before mock/download fallback completion. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 PikPak 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
| quark | list_ready | False | True | True | True | False | False | runtime_candidate | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Live list/metadata/create_dir capability is already wired, but task runtime write/upload flow is not connected yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |  |
| uc | list_ready | False | True | True | True | False | False | runtime_candidate | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Live list/metadata/create_dir capability is already wired, but task runtime write/upload flow is not connected yet. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |  |
| xunlei | list_ready | False | True | True | True | True | False | runtime_active | 0 | 0 | 0 | False | False | not_implemented | (none) | True |
|  | runtime_note |  |  |  |  |  |  | Current task runtime now drives a live Xunlei create_dir write probe before mock/download fallback completion. |  |  |  |  |  |  |  |  |
|  | note |  |  |  |  |  |  |  |  |  |  |  |  | 当前 Xunlei 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。 |  |  |
