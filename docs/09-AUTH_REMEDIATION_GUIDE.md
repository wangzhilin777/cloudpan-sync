# 授权补救指南 / Auth Remediation Guide

- profileCount: `3`
- readyCount: `1`
- needsFixCount: `2`
- writeReadyCount: `3`
- writeNeedsFixCount: `0`

## 档案清单 / Profiles

### smoke-guangya [guangya]
- profileId: `0318479d-4669-415f-9083-7aecc102bf90`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: ``
- resolvedFileId: ``
- missingFieldHints: `extra.parentId (aliases: parent_id/parentFileId/dirId/pid)`
- recommendedPatchCommand: `.\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 0318479d-4669-415f-9083-7aecc102bf90 --set parentId=YOUR_REAL_PARENT_ID --write --revalidate`

### risk-smoke-guangya [guangya]
- profileId: `08684618-ea29-48a4-b603-2e40cdc37c3d`
- profileReady: `False`
- writeReady: `True`
- resolvedParentId: ``
- resolvedFileId: ``
- missingFieldHints: `extra.parentId (aliases: parent_id/parentFileId/dirId/pid)`
- recommendedPatchCommand: `.\.venv\Scripts\python.exe scripts\patch_auth_profile_extra.py --profile-id 08684618-ea29-48a4-b603-2e40cdc37c3d --set parentId=YOUR_REAL_PARENT_ID --write --revalidate`

### aliyun-bootstrap [aliyundrive_open]
- profileId: `22173a49-2206-4da8-8624-9bab7bbbe64b`
- profileReady: `True`
- writeReady: `True`
- resolvedParentId: `root`
- resolvedFileId: ``
