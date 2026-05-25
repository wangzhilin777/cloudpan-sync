# CloudPan Sync Auth Live Validation Report

- totalRecords: `5`
- latestProfileCount: `3`
- latestOkCount: `0`
- latestFailedCount: `3`
- latestProviders: `aliyundrive_open, guangya`
- latestProfiles: `ok=(none)` `failed=aliyun-bootstrap, risk-smoke-guangya, smoke-guangya`
- profileSummary: `ok_providers=(none)` `failed_providers=aliyundrive_open, guangya` `failed_modes=live_error, profile_incomplete`

## Latest By Profile

### guangya - smoke-guangya
- checkedAt: `2026-05-23T04:02:12.577675+00:00`
- ok: `False` status: `0`
- mode: `profile_incomplete`
- summary: `Guangya live list requires parentId in request or auth profile extra.parentId.`
- error: `missing_parent_id`

### guangya - risk-smoke-guangya
- checkedAt: `2026-05-23T04:02:12.600529+00:00`
- ok: `False` status: `0`
- mode: `profile_incomplete`
- summary: `Guangya live list requires parentId in request or auth profile extra.parentId.`
- error: `missing_parent_id`

### aliyundrive_open - aliyun-bootstrap
- checkedAt: `2026-05-25T16:45:16.495503+00:00`
- ok: `False` status: `404`
- mode: `live_error`
- summary: `Aliyun Drive Open live list reached the API but was rejected.`
- error: `http_error:404`

## Recent History

### guangya - smoke-guangya
- checkedAt: `2026-05-23T04:00:31.966676+00:00`
- ok: `False` status: `0`
- mode: `profile_incomplete`
- summary: `Guangya live list requires parentId in request or auth profile extra.parentId.`
- error: `missing_parent_id`
- checkCount: `1`

### guangya - risk-smoke-guangya
- checkedAt: `2026-05-23T04:00:31.970200+00:00`
- ok: `False` status: `0`
- mode: `profile_incomplete`
- summary: `Guangya live list requires parentId in request or auth profile extra.parentId.`
- error: `missing_parent_id`
- checkCount: `1`

### guangya - smoke-guangya
- checkedAt: `2026-05-23T04:02:12.577675+00:00`
- ok: `False` status: `0`
- mode: `profile_incomplete`
- summary: `Guangya live list requires parentId in request or auth profile extra.parentId.`
- error: `missing_parent_id`
- checkCount: `1`

### guangya - risk-smoke-guangya
- checkedAt: `2026-05-23T04:02:12.600529+00:00`
- ok: `False` status: `0`
- mode: `profile_incomplete`
- summary: `Guangya live list requires parentId in request or auth profile extra.parentId.`
- error: `missing_parent_id`
- checkCount: `1`

### aliyundrive_open - aliyun-bootstrap
- checkedAt: `2026-05-25T16:45:16.495503+00:00`
- ok: `False` status: `404`
- mode: `live_error`
- probeArgs: `parentId=root` `fileId=`
- summary: `Aliyun Drive Open live list reached the API but was rejected.`
- error: `http_error:404`
- checkCount: `1`
