# 授权补救指南 / Auth Remediation Guide

- profileCount: `3`
- readyCount: `0`
- needsFixCount: `3`
- writeReadyCount: `3`
- writeNeedsFixCount: `0`

## 档案清单 / Profiles

### smoke-guangya [guangya]
- profileId: `0318479d-4669-415f-9083-7aecc102bf90`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: ``
- resolvedFileId: ``
- missingFieldHints: `extra.parentId (aliases: parent_id/parentFileId/dirId/pid), token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- recommendedPatchCommand: `.\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate`

### risk-smoke-guangya [guangya]
- profileId: `08684618-ea29-48a4-b603-2e40cdc37c3d`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: ``
- resolvedFileId: ``
- missingFieldHints: `extra.parentId (aliases: parent_id/parentFileId/dirId/pid), token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token`
- recommendedPatchCommand: `.\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 08684618-ea29-48a4-b603-2e40cdc37c3d --set parentId=YOUR_REAL_PARENT_ID --write --revalidate`

### aliyun-bootstrap [aliyundrive_open]
- profileId: `22173a49-2206-4da8-8624-9bab7bbbe64b`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: `root`
- resolvedFileId: ``
- missingFieldHints: `token looks like placeholder data; replace tok-demo with a real Aliyun OAuth token, extra.domainId still uses placeholder data; replace domain-demo with a real domainId, extra.driveId still uses placeholder data; replace drive-demo with a real driveId`
- placeholderFieldHints: `token looks like placeholder data; replace tok-demo with a real Aliyun OAuth token, extra.domainId still uses placeholder data; replace domain-demo with a real domainId, extra.driveId still uses placeholder data; replace drive-demo with a real driveId`
- recommendedPatchCommand: `.\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 22173a49-2206-4da8-8624-9bab7bbbe64b --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write --revalidate`
