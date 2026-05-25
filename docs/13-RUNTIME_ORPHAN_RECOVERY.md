# CloudPan Sync Runtime Orphan Recovery Guide

- 生成时间：`2026-05-25T19:40:16.671027+00:00`
- 汇总： `providerCount=3` `orphanProfileCount=3` `runtimeSampleCount=3` `providersWithSavedProfiles=1` `providersWithoutSavedProfiles=2`
- orphanSummary: `providers=guangya, pikpak, uc` `profiles=gy-live-1, pikpak-live-1, uc-live-1` `savedProfileProviders=guangya` `missingProfileProviders=pikpak, uc`

> 说明：这里的 recovery command 只是帮助你把历史 runtime success 对应的 `profileId` 重建回当前仓库，便于后续重新验证；它不会自动把旧样本算成新的真实完成证据。

## guangya - Guangya - gy-live-1
- orphanProfileId: `gy-live-1`
- sampleCount: `1` pathCount=`1` latestSavedAt=`2026-05-25T17:14:51.862545+00:00`
- runtimeModes: `binary_upload_multipart` verifyModes=`list_by_parent_name` conflictPolicies=`overwrite_existing` conflictActions=`overwrite_downgraded_to_auto_rename`
- existingProviderProfiles: count=`2` ids=`0318479d-4669-415f-9083-7aecc102bf90, 08684618-ea29-48a4-b603-2e40cdc37c3d` names=`smoke-guangya, risk-smoke-guangya`
- authHints: modes=`web_login_capture, manual_token` preferred=`manual_token` fields=`token or extra.authorization | extra.parentId | optional extra.did | optional extra.dt`
- webLoginUrl: https://guangyapan.com/
- nextStep: 先按原 runtime profileId 重建一个可复验 auth profile stub，再用真实凭证补字段并重跑 validation / live probe；只有这样，这条历史 runtime success 样本才有机会重新变成当前仓库可复验的证据。
- note: 这一步只是把历史 runtime success 样本对应的 profileId 恢复回当前仓库，不会自动把样本算成新的真实完成证据；仍需后续用真实凭证重新验证。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id gy-live-1 --provider-key guangya --auth-mode manual_token --display-name guangya-restore-gy-live-1 --token YOUR_TOKEN --set parentId=YOUR_VALUE --probe`

## pikpak - PikPak - pikpak-live-1
- orphanProfileId: `pikpak-live-1`
- sampleCount: `1` pathCount=`1` latestSavedAt=`2026-05-24T23:51:50.906236+00:00`
- runtimeModes: `binary_upload_after_hash_miss` verifyModes=`metadata_by_file_id` conflictPolicies=`overwrite_existing` conflictActions=`overwrite_downgraded_to_auto_rename`
- existingProviderProfiles: count=`0` ids=`(none)` names=`(none)`
- authHints: modes=`manual_token` preferred=`manual_token` fields=`token or extra.authorization | optional extra.deviceId | optional extra.fileId`
- webLoginUrl: https://mypikpak.com/
- officialDocsUrl: https://mypikpak.com/
- nextStep: 先按原 runtime profileId 重建一个可复验 auth profile stub，再用真实凭证补字段并重跑 validation / live probe；只有这样，这条历史 runtime success 样本才有机会重新变成当前仓库可复验的证据。
- note: 这一步只是把历史 runtime success 样本对应的 profileId 恢复回当前仓库，不会自动把样本算成新的真实完成证据；仍需后续用真实凭证重新验证。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id pikpak-live-1 --provider-key pikpak --auth-mode manual_token --display-name pikpak-restore-pikpak-live-1 --token YOUR_TOKEN --set deviceId=YOUR_VALUE --probe`

## uc - UC Drive - uc-live-1
- orphanProfileId: `uc-live-1`
- sampleCount: `1` pathCount=`1` latestSavedAt=`2026-05-24T23:51:50.907991+00:00`
- runtimeModes: `binary_upload_after_hash_miss` verifyModes=`finish_response` conflictPolicies=`overwrite_existing` conflictActions=`overwrite_downgraded_to_auto_rename`
- existingProviderProfiles: count=`0` ids=`(none)` names=`(none)`
- authHints: modes=`web_login_capture, manual_cookie` preferred=`manual_cookie` fields=`cookie or extra.cookie_header | extra.pwdId or extra.sharePwdId | optional extra.passcode | optional extra.fileId`
- webLoginUrl: https://drive.uc.cn/
- nextStep: 先按原 runtime profileId 重建一个可复验 auth profile stub，再用真实凭证补字段并重跑 validation / live probe；只有这样，这条历史 runtime success 样本才有机会重新变成当前仓库可复验的证据。
- note: 这一步只是把历史 runtime success 样本对应的 profileId 恢复回当前仓库，不会自动把样本算成新的真实完成证据；仍需后续用真实凭证重新验证。
- recommendedCreateCommand: `.\.venv\Scripts\python.exe scripts\create_auth_profile_stub.py --profile-id uc-live-1 --provider-key uc --auth-mode manual_cookie --display-name uc-restore-uc-live-1 --cookie YOUR_COOKIE --set pwdId=YOUR_VALUE --probe`
