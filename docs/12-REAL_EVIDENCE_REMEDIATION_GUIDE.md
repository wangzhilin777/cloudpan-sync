# CloudPan Sync 真实联调补救指南

- providerCount: `10`
- providersWithNoProfiles: `8`
- providersNeedingAuthEvidence: `10`
- providersNeedingListEvidence: `10`
- providersNeedingMetadataEvidence: `10`
- providersNeedingCreateDirEvidence: `10`
- providersNeedingRuntimeSuccess: `2`
- providersWithPatchCommand: `1`
- providersWithPatchProbeCommand: `1`
- providersWithRefreshEvidenceCommand: `1`
- providersWithRuntimeProbeCommand: `0`
- providersWithLiveUploadCommand: `0`
- providersWithFastCandidateCommand: `0`
- providersWithRuntimeSuccessCommand: `0`
- providersWithCreateCommand: `8`
- providersWithBootstrapCommand: `8`
- providersBlockedOnly: `0`
- providersCandidateOnly: `0`
- providersProbeOnly: `0`

## Provider 清单

### guangya - Guangya
- profileCount: `2`
- authReadyProfiles: `0`
- writeReadyProfiles: `2`
- recommendedAuthModes: `web_login_capture, manual_token`
- webLoginUrl: https://guangyapan.com/
- requiredFieldHints: `token or extra.authorization, extra.parentId, optional extra.did, optional extra.dt`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先补齐档案缺字段并重跑 validation / live probe，拿到 auth/list/metadata 最小成功证据。
- recommendedPatchCommand: `.\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate`
- recommendedPatchProbeCommand: `.\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write`

### aliyundrive_open - Aliyun Drive Open
- profileCount: `1`
- authReadyProfiles: `1`
- writeReadyProfiles: `1`
- recommendedAuthModes: `official_oauth`
- officialDocsUrl: https://www.alipan.com/
- requiredFieldHints: `token or extra.authorization, extra.domainId, extra.driveId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 对现有档案重跑 provider live probe，优先补齐 auth/list/metadata/create_dir 成功证据。
- recommendedRefreshEvidenceCommand: `.\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id 22173a49-2206-4da8-8624-9bab7bbbe64b --write`

### 115_open - 115 Open
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `official_oauth, manual_cookie`
- requiredFieldHints: `cookie or extra.cookie_header, optional extra.parentId or extra.cid, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `115_open` 的 auth profile，再执行最小 validation 和 live probe。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 115_open --auth-mode manual_cookie --display-name 115_open-manual_cookie --cookie YOUR_COOKIE --set parentId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 115_open --auth-mode manual_cookie --display-name 115_open-manual_cookie --cookie YOUR_COOKIE --set parentId=YOUR_VALUE --probe`

### quark - Quark
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `web_login_capture, manual_cookie`
- webLoginUrl: https://pan.quark.cn/
- requiredFieldHints: `cookie or extra.cookie_header, extra.pwdId or extra.sharePwdId, optional extra.passcode, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `quark` 的 auth profile，再执行最小 validation 和 live probe。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key quark --auth-mode manual_cookie --display-name quark-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key quark --auth-mode manual_cookie --display-name quark-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE --probe`

### 189cloud - Tianyi 189Cloud
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `web_login_capture, manual_cookie`
- webLoginUrl: https://cloud.189.cn/
- requiredFieldHints: `share-read probe: extra.shareCode, optional extra.accessCode, account write auth: token or extra.accessToken, account write auth: extra.signature, account write auth: extra.date, optional helper: patch_189cloud_account_auth.py from captured headers/curl, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `189cloud` 的 auth profile，再执行最小 validation 和 live probe。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 189cloud --auth-mode manual_cookie --display-name 189cloud-manual_cookie --cookie YOUR_COOKIE --set shareCode=YOUR_VALUE --set accessCode=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 189cloud --auth-mode manual_cookie --display-name 189cloud-manual_cookie --cookie YOUR_COOKIE --set shareCode=YOUR_VALUE --set accessCode=YOUR_VALUE --probe`

### baidu_netdisk - Baidu Netdisk
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `official_oauth, manual_cookie`
- webLoginUrl: https://pan.baidu.com/
- officialDocsUrl: https://pan.baidu.com/
- requiredFieldHints: `token or extra.authorization, or cookie, optional extra.fileId, optional extra.path`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `baidu_netdisk` 的 auth profile，再执行最小 validation 和 live probe。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key baidu_netdisk --auth-mode manual_cookie --display-name baidu_netdisk-manual_cookie --cookie YOUR_COOKIE --set fileId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key baidu_netdisk --auth-mode manual_cookie --display-name baidu_netdisk-manual_cookie --cookie YOUR_COOKIE --set fileId=YOUR_VALUE --probe`

### uc - UC Drive
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `web_login_capture, manual_cookie`
- webLoginUrl: https://drive.uc.cn/
- requiredFieldHints: `cookie or extra.cookie_header, extra.pwdId or extra.sharePwdId, optional extra.passcode, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `uc` 的 auth profile，再执行最小 validation 和 live probe。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key uc --auth-mode manual_cookie --display-name uc-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key uc --auth-mode manual_cookie --display-name uc-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE --probe`

### xunlei - Xunlei Drive
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `web_login_capture, manual_token`
- webLoginUrl: https://pan.xunlei.com/
- requiredFieldHints: `token or extra.authorization, extra.deviceId or extra.x-device-id, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `xunlei` 的 auth profile，再执行最小 validation 和 live probe。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key xunlei --auth-mode manual_token --display-name xunlei-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key xunlei --auth-mode manual_token --display-name xunlei-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE --probe`

### pikpak - PikPak
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `manual_token`
- webLoginUrl: https://mypikpak.com/
- officialDocsUrl: https://mypikpak.com/
- requiredFieldHints: `token or extra.authorization, optional extra.deviceId, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `pikpak` 的 auth profile，再执行最小 validation 和 live probe。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key pikpak --auth-mode manual_token --display-name pikpak-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key pikpak --auth-mode manual_token --display-name pikpak-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE --probe`

### 123_open - 123Pan Open
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `official_oauth, manual_token`
- webLoginUrl: https://www.123pan.com/
- officialDocsUrl: https://www.123pan.com/
- requiredFieldHints: `token or extra.authorization, optional extra.parentFileId, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- nextStep: 先创建 `123_open` 的 auth profile，再执行最小 validation 和 live probe。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 123_open --auth-mode manual_token --display-name 123_open-manual_token --token YOUR_TOKEN --set parentFileId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 123_open --auth-mode manual_token --display-name 123_open-manual_token --token YOUR_TOKEN --set parentFileId=YOUR_VALUE --probe`
