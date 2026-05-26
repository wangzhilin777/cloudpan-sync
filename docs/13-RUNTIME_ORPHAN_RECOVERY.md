# CloudPan Sync Runtime Orphan Recovery Guide

- 生成时间：`2026-05-26T13:34:34.194648+00:00`
- 汇总： `providerCount=0` `orphanProfileCount=0` `runtimeSampleCount=0` `providersWithSavedProfiles=0` `providersWithoutSavedProfiles=0`
- orphanSummary: `providers=(none)` `profiles=(none)` `savedProfileProviders=(none)` `missingProfileProviders=(none)`
- batchCommands: `dryRun=.\.venv\Scripts\python.exe scripts\recreate_runtime_orphan_stubs.py` `writeMissing=.\.venv\Scripts\python.exe scripts\recreate_runtime_orphan_stubs.py --write` `overwriteExisting=.\.venv\Scripts\python.exe scripts\recreate_runtime_orphan_stubs.py --write --overwrite-existing`

> 说明：这里的 recovery command 只是帮助你把历史 runtime success 对应的 `profileId` 重建回当前仓库，便于后续重新验证；它不会自动把旧样本算成新的真实完成证据。

- none
