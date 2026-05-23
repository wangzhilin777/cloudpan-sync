# 授权补救指南 / Auth Remediation Guide

- profileCount: `2`
- readyCount: `0`
- needsFixCount: `2`
- writeReadyCount: `2`
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
