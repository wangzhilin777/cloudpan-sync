# 授权补救指南 / Auth Remediation Guide

- profileCount: `9`
- readyCount: `0`
- needsFixCount: `9`
- writeReadyCount: `9`
- writeNeedsFixCount: `0`
- needsSecretRefreshCount: `9`
- profileSummary: `ready=(none)` `needsFix=aliyun-bootstrap, guangya-restore-gy-live-1, guangya-restore-gy-live-2, guangya-restore-gy-live-defaults-1, guangya-restore-gy-orphan-live-1, pikpak-restore-pikpak-live-1, risk-smoke-guangya, smoke-guangya, uc-restore-uc-live-1` `writeReady=aliyun-bootstrap, guangya-restore-gy-live-1, guangya-restore-gy-live-2, guangya-restore-gy-live-defaults-1, guangya-restore-gy-orphan-live-1, pikpak-restore-pikpak-live-1, risk-smoke-guangya, smoke-guangya, uc-restore-uc-live-1` `writeNeedsFix=(none)` `needsSecretRefresh=aliyun-bootstrap, guangya-restore-gy-live-1, guangya-restore-gy-live-2, guangya-restore-gy-live-defaults-1, guangya-restore-gy-orphan-live-1, pikpak-restore-pikpak-live-1, risk-smoke-guangya, smoke-guangya, uc-restore-uc-live-1`

## 档案清单 / Profiles

### smoke-guangya [guangya]
- profileId: `0318479d-4669-415f-9083-7aecc102bf90`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: ``
- resolvedFileId: ``
- missingFieldHints: `extra.parentId (aliases: parent_id/parentFileId/dirId/pid), token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderSecretFieldHints: `token`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name smoke-guangya --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe`

### risk-smoke-guangya [guangya]
- profileId: `08684618-ea29-48a4-b603-2e40cdc37c3d`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: ``
- resolvedFileId: ``
- missingFieldHints: `extra.parentId (aliases: parent_id/parentFileId/dirId/pid), token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderSecretFieldHints: `token`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name risk-smoke-guangya --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe`

### aliyun-bootstrap [aliyundrive_open]
- profileId: `22173a49-2206-4da8-8624-9bab7bbbe64b`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: `root`
- resolvedFileId: ``
- missingFieldHints: `token looks like placeholder data; replace tok-demo with a real Aliyun OAuth token, extra.domainId still uses placeholder data; replace domain-demo with a real domainId, extra.driveId still uses placeholder data; replace drive-demo with a real driveId`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo with a real Aliyun OAuth token, extra.domainId still uses placeholder data; replace domain-demo with a real domainId, extra.driveId still uses placeholder data; replace drive-demo with a real driveId`
- placeholderSecretFieldHints: `token`
- liveRejected: profiles=`aliyun-bootstrap` placeholderProfiles=`aliyun-bootstrap` statuses=`404`
- liveRejectedSummaries: `aliyun-bootstrap:404`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe`

### guangya-restore-gy-live-1 [guangya]
- profileId: `gy-live-1`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: `YOUR_VALUE`
- resolvedFileId: ``
- missingFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderSecretFieldHints: `token`
- liveRejected: profiles=`guangya-restore-gy-live-1` placeholderProfiles=`guangya-restore-gy-live-1` statuses=`401`
- liveRejectedSummaries: `guangya-restore-gy-live-1:401`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe`

### guangya-restore-gy-live-2 [guangya]
- profileId: `gy-live-2`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: `YOUR_VALUE`
- resolvedFileId: ``
- missingFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderSecretFieldHints: `token`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-2 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe`

### guangya-restore-gy-live-defaults-1 [guangya]
- profileId: `gy-live-defaults-1`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: `YOUR_VALUE`
- resolvedFileId: ``
- missingFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderSecretFieldHints: `token`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-defaults-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe`

### guangya-restore-gy-orphan-live-1 [guangya]
- profileId: `gy-orphan-live-1`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: `YOUR_VALUE`
- resolvedFileId: ``
- missingFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderSecretFieldHints: `token`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-orphan-live-1 --token YOUR_TOKEN --set parentId=YOUR_REAL_PARENT_ID --probe`

### pikpak-restore-pikpak-live-1 [pikpak]
- profileId: `pikpak-live-1`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: ``
- resolvedFileId: ``
- missingFieldHints: `token looks like placeholder data; replace it with a real provider token`
- placeholderFieldHints: `token looks like placeholder data; replace it with a real provider token`
- placeholderSecretFieldHints: `token`
- liveRejected: profiles=`pikpak-restore-pikpak-live-1` placeholderProfiles=`pikpak-restore-pikpak-live-1` statuses=`401`
- liveRejectedSummaries: `pikpak-restore-pikpak-live-1:401`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key pikpak --auth-mode manual_token --display-name pikpak-restore-pikpak-live-1 --token YOUR_TOKEN --set deviceId=YOUR_DEVICE_ID --probe`

### uc-restore-uc-live-1 [uc]
- profileId: `uc-live-1`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: `0`
- resolvedFileId: ``
- missingFieldHints: `cookie looks like placeholder data; replace it with a real captured cookie`
- placeholderFieldHints: `cookie looks like placeholder data; replace it with a real captured cookie`
- placeholderSecretFieldHints: `cookie`
- liveRejected: profiles=`uc-restore-uc-live-1` placeholderProfiles=`uc-restore-uc-live-1` statuses=`404`
- liveRejectedSummaries: `uc-restore-uc-live-1:404`
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key uc --auth-mode manual_cookie --display-name uc-restore-uc-live-1 --cookie YOUR_COOKIE --set pwdId=YOUR_SHARE_PWD_ID --probe`
