# 授权补救指南 / Auth Remediation Guide

- profileCount: `3`
- readyCount: `0`
- needsFixCount: `3`
- writeReadyCount: `3`
- writeNeedsFixCount: `0`
- needsSecretRefreshCount: `3`
- profileSummary: `ready=(none)` `needsFix=aliyun-bootstrap, risk-smoke-guangya, smoke-guangya` `writeReady=aliyun-bootstrap, risk-smoke-guangya, smoke-guangya` `writeNeedsFix=(none)` `needsSecretRefresh=aliyun-bootstrap, risk-smoke-guangya, smoke-guangya`

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
- recommendedRecreateProbeCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --provider-key aliyundrive_open --auth-mode official_oauth --display-name aliyun-bootstrap --token YOUR_TOKEN --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe`
