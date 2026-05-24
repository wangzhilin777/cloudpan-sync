# CloudPan Sync 真实联调补救指南

- providerCount: `10`
- providersWithNoProfiles: `9`
- providersNeedingAuthEvidence: `10`
- providersNeedingListEvidence: `10`
- providersNeedingMetadataEvidence: `10`
- providersNeedingCreateDirEvidence: `10`
- providersNeedingRuntimeSuccess: `10`
- providersWithPatchCommand: `1`
- providersBlockedOnly: `0`

## Provider 清单

### guangya - Guangya
- profileCount: `2`
- authReadyProfiles: `0`
- writeReadyProfiles: `2`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先补齐档案缺字段并重跑 validation / live probe，拿到 auth/list/metadata 最小成功证据。
- recommendedPatchCommand: `.\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate`

### aliyundrive_open - Aliyun Drive Open
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `aliyundrive_open` 的 auth profile，再执行最小 validation 和 live probe。

### 115_open - 115 Open
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `115_open` 的 auth profile，再执行最小 validation 和 live probe。

### quark - Quark
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `quark` 的 auth profile，再执行最小 validation 和 live probe。

### 189cloud - Tianyi 189Cloud
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `189cloud` 的 auth profile，再执行最小 validation 和 live probe。

### baidu_netdisk - Baidu Netdisk
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `baidu_netdisk` 的 auth profile，再执行最小 validation 和 live probe。

### uc - UC Drive
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `uc` 的 auth profile，再执行最小 validation 和 live probe。

### xunlei - Xunlei Drive
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `xunlei` 的 auth profile，再执行最小 validation 和 live probe。

### pikpak - PikPak
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `pikpak` 的 auth profile，再执行最小 validation 和 live probe。

### 123_open - 123Pan Open
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `123_open` 的 auth profile，再执行最小 validation 和 live probe。
