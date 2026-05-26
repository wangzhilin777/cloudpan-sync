# CloudPan Sync 真实联调补救指南

- providerCount: `10`
- providersWithNoProfiles: `8`
- providersNeedingAuthEvidence: `10`
- providersNeedingListEvidence: `10`
- providersNeedingMetadataEvidence: `10`
- providersNeedingCreateDirEvidence: `10`
- providersNeedingRuntimeSuccess: `7`
- providersWithPatchCommand: `2`
- providersWithPatchProbeCommand: `2`
- providersWithRecreateProbeCommand: `4`
- providersWithRefreshEvidenceCommand: `0`
- providersWithPostRefreshRuntimeCommand: `0`
- providersWithRuntimeProbeCommand: `0`
- providersWithLiveUploadCommand: `0`
- providersWithFastCandidateCommand: `0`
- providersWithRuntimeSuccessCommand: `0`
- providersWithPostBootstrapRuntimeCommand: `6`
- providersWithPrimaryCommand: `10`
- providersWithOverwriteVariantCommand: `6`
- providersWithConflictPolicyNote: `6`
- providersWithDeclaredConflictPolicies: `8`
- providersWithProviderManagedOverwrite: `1`
- providersWithOverwriteDowngrade: `7`
- providersWithConflictUnsupported: `1`
- providersWithCreateCommand: `8`
- providersWithBootstrapCommand: `8`
- providersBlockedOnly: `0`
- providersCandidateOnly: `0`
- providersProbeOnly: `0`
- providersRuntimeOrphanOnly: `3`
- providerSummary: `noProfiles=115_open, 123_open, 189cloud, baidu_netdisk, pikpak, quark, uc, xunlei` `needAuth=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, guangya, pikpak, quark, uc, xunlei` `needRuntime=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, quark, xunlei` `recreateProbe=aliyundrive_open, guangya, pikpak, uc` `primaryCommand=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, guangya, pikpak, quark, uc, xunlei` `overwriteVariant=115_open, 123_open, 189cloud, baidu_netdisk, quark, xunlei` `blockedOnly=(none)` `candidateOnly=(none)` `probeOnly=(none)` `runtimeOrphanOnly=guangya, pikpak, uc`

## Provider 清单

### guangya - Guangya
- profileCount: `2`
- authReadyProfiles: `0`
- writeReadyProfiles: `2`
- recommendedAuthModes: `web_login_capture, manual_token`
- webLoginUrl: https://guangyapan.com/
- requiredFieldHints: `token or extra.authorization, extra.parentId, optional extra.did, optional extra.dt`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=True`
- runtimeOrphanProfiles: `gy-live-1, gy-live-defaults-1`
- conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported` `supportsOverwrite=False` `supportsAutoRename=True` `overwriteBehavior=downgrade_to_auto_rename`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据, 已有 runtime 样本，但对应 auth profile 未保存在当前仓库
- placeholderSecretFieldHints: `token`
- providerConflictNotes: 当前 Guangya fallback 上传链路已接受 overwrite_existing / auto_rename_new，但 overwrite_existing 仍会诚实降级为 auto_rename_new。
- nextStep: 当前档案仍含占位 token/cookie 等 secret 字段；先用真实凭证重建或编辑档案，再重跑 validation / live probe。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-live-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe` `label=recreate_probe`
- recommendedPatchCommand: `.\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate`
- recommendedPatchProbeCommand: `.\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-live-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe`
- recommendedRecreateProbeCommands: count=`2`
  - [1] `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-live-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe`
  - [2] `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-live-defaults-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-defaults-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe`
- exactRecreateHelper: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --from-remediation-orphan-profile gy-live-defaults-1`

### aliyundrive_open - Aliyun Drive Open
- profileCount: `1`
- authReadyProfiles: `0`
- writeReadyProfiles: `1`
- recommendedAuthModes: `official_oauth`
- officialDocsUrl: https://www.alipan.com/
- requiredFieldHints: `token or extra.authorization, extra.domainId, extra.driveId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=False`
- conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=supported` `auto_rename=supported` `supportsOverwrite=True` `supportsAutoRename=True` `overwriteBehavior=provider_managed`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- placeholderSecretFieldHints: `token`
- providerConflictNotes: 当前 Aliyun Drive Open 已接入任务运行阶段真实小文件上传；同名文件可按 overwrite_existing / auto_rename_new 显式选择。
- nextStep: 当前档案仍含占位 token/cookie 等 secret 字段；先用真实凭证重建或编辑档案，再重跑 validation / live probe。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe` `label=recreate_probe`
- recommendedPatchCommand: `.\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 22173a49-2206-4da8-8624-9bab7bbbe64b --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write --revalidate`
- recommendedPatchProbeCommand: `.\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id 22173a49-2206-4da8-8624-9bab7bbbe64b --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe`

### 115_open - 115 Open
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `official_oauth, manual_cookie`
- requiredFieldHints: `cookie or extra.cookie_header, optional extra.parentId or extra.cid, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=False`
- conflictSupport: `declared=(none)` `overwrite=unsupported` `auto_rename=probe_only_runtime_write_check` `supportsOverwrite=False` `supportsAutoRename=False` `overwriteBehavior=not_implemented`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- providerConflictNotes: 当前 115 Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。
- nextStep: 先创建 `115_open` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。当前 auto_rename_new 仍停留在 probe-only 写探针口径，先不要把首条样本建立在 overwrite_existing 上。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id YOUR_PROFILE_ID --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-post-bootstrap-runtime-evidence` `label=post_bootstrap_runtime`
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 115_open --auth-mode manual_cookie --display-name 115_open-manual_cookie --cookie YOUR_COOKIE --set parentId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 115_open --auth-mode manual_cookie --display-name 115_open-manual_cookie --cookie YOUR_COOKIE --set parentId=YOUR_VALUE --probe`
- recommendedPostBootstrapRuntimeCommand: `.\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id YOUR_PROFILE_ID --sha1 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\115_open-post-bootstrap-runtime-evidence`
- recommendedOverwriteVariantCommand: `.\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 115_open --target-profile-id YOUR_PROFILE_ID --sha1 auto --auto-temp-file --conflict-policy overwrite_existing --evidence-dir tmp\115_open-post-bootstrap-runtime-evidence`
- conflictPolicyNote: 当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。

### quark - Quark
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `web_login_capture, manual_cookie`
- webLoginUrl: https://pan.quark.cn/
- requiredFieldHints: `cookie or extra.cookie_header, extra.pwdId or extra.sharePwdId, optional extra.passcode, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=False`
- conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported` `supportsOverwrite=False` `supportsAutoRename=True` `overwriteBehavior=downgrade_to_auto_rename`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- providerConflictNotes: 当前 Quark 已接入任务运行阶段真实本地文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。
- nextStep: 先创建 `quark` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。首条样本建议继续保留默认 auto_rename_new；overwrite_existing 当前会诚实降级为自动改名。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider quark --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\quark-post-bootstrap-runtime-evidence` `label=post_bootstrap_runtime`
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key quark --auth-mode manual_cookie --display-name quark-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key quark --auth-mode manual_cookie --display-name quark-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE --probe`
- recommendedPostBootstrapRuntimeCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider quark --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\quark-post-bootstrap-runtime-evidence`
- recommendedOverwriteVariantCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider quark --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\quark-post-bootstrap-runtime-evidence`
- conflictPolicyNote: 当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。

### 189cloud - Tianyi 189Cloud
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `web_login_capture, manual_cookie`
- webLoginUrl: https://cloud.189.cn/
- requiredFieldHints: `share-read probe: extra.shareCode, optional extra.accessCode, account write auth: token or extra.accessToken, account write auth: extra.signature, account write auth: extra.date, optional helper: patch_189cloud_account_auth.py from captured headers/curl, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=False`
- conflictSupport: `declared=(none)` `overwrite=unsupported` `auto_rename=unsupported` `supportsOverwrite=False` `supportsAutoRename=False` `overwriteBehavior=readonly_auth_blocked`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- providerConflictNotes: 当前 189Cloud 已接入账号级 create_dir 写目录尝试，但 shareCode/accessCode-only 档案仍然只读，真实文件上传与同名冲突处理仍未声明为已支持。
- nextStep: 先创建 `189cloud` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。当前同名冲突处理仍未声明为可安全支持，首条样本请先避开目标目录同名文件。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 189cloud --target-profile-id YOUR_PROFILE_ID --md5 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\189cloud-post-bootstrap-runtime-evidence` `label=post_bootstrap_runtime`
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 189cloud --auth-mode manual_cookie --display-name 189cloud-manual_cookie --cookie YOUR_COOKIE --set shareCode=YOUR_VALUE --set accessCode=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 189cloud --auth-mode manual_cookie --display-name 189cloud-manual_cookie --cookie YOUR_COOKIE --set shareCode=YOUR_VALUE --set accessCode=YOUR_VALUE --probe`
- recommendedPostBootstrapRuntimeCommand: `.\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 189cloud --target-profile-id YOUR_PROFILE_ID --md5 auto --auto-temp-file --conflict-policy auto_rename_new --evidence-dir tmp\189cloud-post-bootstrap-runtime-evidence`
- recommendedOverwriteVariantCommand: `.\.venv\Scripts\python.exe scripts\create_fast_upload_candidate_task.py --target-provider 189cloud --target-profile-id YOUR_PROFILE_ID --md5 auto --auto-temp-file --conflict-policy overwrite_existing --evidence-dir tmp\189cloud-post-bootstrap-runtime-evidence`
- conflictPolicyNote: 当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。

### baidu_netdisk - Baidu Netdisk
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `official_oauth, manual_cookie`
- webLoginUrl: https://pan.baidu.com/
- officialDocsUrl: https://pan.baidu.com/
- requiredFieldHints: `token or extra.authorization, or cookie, optional extra.fileId, optional extra.path`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=False`
- conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported` `supportsOverwrite=False` `supportsAutoRename=True` `overwriteBehavior=downgrade_to_auto_rename`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- providerConflictNotes: 当前 Baidu Netdisk 已接入任务运行阶段真实小文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。
- nextStep: 先创建 `baidu_netdisk` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。首条样本建议继续保留默认 auto_rename_new；overwrite_existing 当前会诚实降级为自动改名。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider baidu_netdisk --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\baidu_netdisk-post-bootstrap-runtime-evidence` `label=post_bootstrap_runtime`
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key baidu_netdisk --auth-mode manual_cookie --display-name baidu_netdisk-manual_cookie --cookie YOUR_COOKIE --set fileId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key baidu_netdisk --auth-mode manual_cookie --display-name baidu_netdisk-manual_cookie --cookie YOUR_COOKIE --set fileId=YOUR_VALUE --probe`
- recommendedPostBootstrapRuntimeCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider baidu_netdisk --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\baidu_netdisk-post-bootstrap-runtime-evidence`
- recommendedOverwriteVariantCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider baidu_netdisk --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\baidu_netdisk-post-bootstrap-runtime-evidence`
- conflictPolicyNote: 当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。

### uc - UC Drive
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `web_login_capture, manual_cookie`
- webLoginUrl: https://drive.uc.cn/
- requiredFieldHints: `cookie or extra.cookie_header, extra.pwdId or extra.sharePwdId, optional extra.passcode, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=True`
- runtimeOrphanProfiles: `uc-live-1`
- conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported` `supportsOverwrite=False` `supportsAutoRename=True` `overwriteBehavior=downgrade_to_auto_rename`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据, 已有 runtime 样本，但对应 auth profile 未保存在当前仓库
- providerConflictNotes: 当前 UC Drive 已接入任务运行阶段真实本地文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。
- nextStep: 当前已存在 runtime 成功样本，但对应 auth profile 未保存在当前仓库；先重建可复用 auth profile，再重跑 validation / live probe，把 auth/list/metadata/create_dir 证据补齐。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id uc-live-1 --provider-key uc --auth-mode manual_cookie --display-name uc-restore-uc-live-1 --cookie YOUR_COOKIE --set pwdId=YOUR_SHARE_PWD_ID --probe` `label=recreate_probe`
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key uc --auth-mode manual_cookie --display-name uc-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key uc --auth-mode manual_cookie --display-name uc-manual_cookie --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE --probe`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id uc-live-1 --provider-key uc --auth-mode manual_cookie --display-name uc-restore-uc-live-1 --cookie YOUR_COOKIE --set pwdId=YOUR_SHARE_PWD_ID --probe`

### xunlei - Xunlei Drive
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `web_login_capture, manual_token`
- webLoginUrl: https://pan.xunlei.com/
- requiredFieldHints: `token or extra.authorization, extra.deviceId or extra.x-device-id, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=False`
- conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported` `supportsOverwrite=False` `supportsAutoRename=True` `overwriteBehavior=downgrade_to_auto_rename`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- providerConflictNotes: 当前 Xunlei 已接入任务运行阶段真实本地文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。
- nextStep: 先创建 `xunlei` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。首条样本建议继续保留默认 auto_rename_new；overwrite_existing 当前会诚实降级为自动改名。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider xunlei --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\xunlei-post-bootstrap-runtime-evidence` `label=post_bootstrap_runtime`
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key xunlei --auth-mode manual_token --display-name xunlei-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key xunlei --auth-mode manual_token --display-name xunlei-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE --probe`
- recommendedPostBootstrapRuntimeCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider xunlei --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\xunlei-post-bootstrap-runtime-evidence`
- recommendedOverwriteVariantCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider xunlei --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\xunlei-post-bootstrap-runtime-evidence`
- conflictPolicyNote: 当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。

### pikpak - PikPak
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `manual_token`
- webLoginUrl: https://mypikpak.com/
- officialDocsUrl: https://mypikpak.com/
- requiredFieldHints: `token or extra.authorization, optional extra.deviceId, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=False` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=True`
- runtimeOrphanProfiles: `pikpak-live-1`
- conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported` `supportsOverwrite=False` `supportsAutoRename=True` `overwriteBehavior=downgrade_to_auto_rename`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据, 已有 runtime 样本，但对应 auth profile 未保存在当前仓库
- providerConflictNotes: 当前 PikPak 已接入任务运行阶段真实本地文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。
- nextStep: 当前已存在 runtime 成功样本，但对应 auth profile 未保存在当前仓库；先重建可复用 auth profile，再重跑 validation / live probe，把 auth/list/metadata/create_dir 证据补齐。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id pikpak-live-1 --provider-key pikpak --auth-mode manual_token --display-name pikpak-restore-pikpak-live-1 --token YOUR_TOKEN --set deviceId=YOUR_DEVICE_ID --probe` `label=recreate_probe`
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key pikpak --auth-mode manual_token --display-name pikpak-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key pikpak --auth-mode manual_token --display-name pikpak-manual_token --token YOUR_TOKEN --set deviceId=YOUR_VALUE --probe`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id pikpak-live-1 --provider-key pikpak --auth-mode manual_token --display-name pikpak-restore-pikpak-live-1 --token YOUR_TOKEN --set deviceId=YOUR_DEVICE_ID --probe`

### 123_open - 123Pan Open
- profileCount: `0`
- authReadyProfiles: `0`
- writeReadyProfiles: `0`
- recommendedAuthModes: `official_oauth, manual_token`
- webLoginUrl: https://www.123pan.com/
- officialDocsUrl: https://www.123pan.com/
- requiredFieldHints: `token or extra.authorization, optional extra.parentFileId, optional extra.fileId`
- needs: `auth=True` `list=True` `metadata=True` `create_dir=True` `runtime=True` `runtimeBlockedOnly=False` `runtimeCandidateOnly=False` `runtimeProbeOnly=False` `runtimeOrphanOnly=False`
- conflictSupport: `declared=overwrite_existing, auto_rename_new` `overwrite=downgrade_to_auto_rename` `auto_rename=supported` `supportsOverwrite=False` `supportsAutoRename=True` `overwriteBehavior=downgrade_to_auto_rename`
- gaps: 缺少通过的 auth validation 证据, 缺少通过的 live list 证据, 缺少通过的 live metadata 证据, 缺少通过的 live create_dir 证据
- providerConflictNotes: 当前 123Pan Open 已接入任务运行阶段真实小文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。
- nextStep: 先创建 `123_open` 的 auth profile 并完成最小 validation / live probe；拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。首条样本建议继续保留默认 auto_rename_new；overwrite_existing 当前会诚实降级为自动改名。
- recommendedPrimaryCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider 123_open --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\123_open-post-bootstrap-runtime-evidence` `label=post_bootstrap_runtime`
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 123_open --auth-mode manual_token --display-name 123_open-manual_token --token YOUR_TOKEN --set parentFileId=YOUR_VALUE`
- recommendedBootstrapCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key 123_open --auth-mode manual_token --display-name 123_open-manual_token --token YOUR_TOKEN --set parentFileId=YOUR_VALUE --probe`
- recommendedPostBootstrapRuntimeCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider 123_open --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy auto_rename_new --evidence-dir tmp\123_open-post-bootstrap-runtime-evidence`
- recommendedOverwriteVariantCommand: `.\.venv\Scripts\python.exe scripts\create_live_upload_task.py --target-provider 123_open --target-profile-id YOUR_PROFILE_ID --auto-temp-file --threshold-mb 1 --conflict-policy overwrite_existing --evidence-dir tmp\123_open-post-bootstrap-runtime-evidence`
- conflictPolicyNote: 当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。
