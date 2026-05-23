# CloudPan Sync Provider Status Matrix

- GeneratedAt: `2026-05-23T10:44:42.784550+00:00`
- Summary: providerCount=10, authReadyCount=0, createDirReadyCount=9, fastCheckCount=5, liveProbeOkCount=0, conflictAwareProviderCount=1, overwriteReadyCount=0, autoRenameReadyCount=1

| providerKey | supportStatus | auth_ready | list_ready | metadata_ready | create_dir_ready | fast_check | live_probe_ok | supports_overwrite | supports_auto_rename | overwrite_behavior | conflict_policies | fallback_ready |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 115_open | list_ready | False | True | True | True | True | False | False | False | not_implemented | (none) | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |
| 123_open | list_ready | False | True | True | True | False | False | False | False | not_implemented | (none) | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |
| 189cloud | list_ready | False | True | True | False | False | False | False | False | readonly_auth_blocked | (none) | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前 189Cloud 仅验证到 shareCode/accessCode 只读链路，写入链路未就绪，因此不能承诺覆盖或自动重命名。 |  |
| aliyundrive_open | list_ready | False | True | True | True | True | False | False | False | not_implemented | (none) | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |
| baidu_netdisk | list_ready | False | True | True | True | False | False | False | False | not_implemented | (none) | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |
| guangya | list_ready | False | True | True | True | True | False | False | True | downgrade_to_auto_rename | overwrite_existing, auto_rename_new | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前 Guangya fallback 上传链路已接受 overwrite_existing / auto_rename_new，但 overwrite_existing 仍会诚实降级为 auto_rename_new。 |  |
| pikpak | list_ready | False | True | True | True | True | False | False | False | not_implemented | (none) | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |
| quark | list_ready | False | True | True | True | False | False | False | False | not_implemented | (none) | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |
| uc | list_ready | False | True | True | True | False | False | False | False | not_implemented | (none) | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |
| xunlei | list_ready | False | True | True | True | True | False | False | False | not_implemented | (none) | True |
|  | note |  |  |  |  |  |  |  |  |  | 当前任务运行时尚未暴露该 provider 的同名冲突处理链路。 |  |
