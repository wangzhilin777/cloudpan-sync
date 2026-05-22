# CloudPan Sync Project Plan

## 1. Project Positioning

CloudPan Sync is a transfer console between mainstream cloud drives.

The core goal is not "multiple drives to Guangya", but transfer between any supported providers. Guangya is only one of the first-wave providers.

The strategy is "fast upload first". If fast upload fails, fallback behavior is decided by a configurable file-size threshold:

- within threshold: optional automatic download+upload fallback
- over threshold: move to pending queue for manual confirmation

## 2. Core Principles

- Build as an independent new project.
- Every cloud drive is a peer `ProviderAdapter`.
- AList/OpenList are references for ideas and field hints, not runtime kernel dependencies.
- Provider capability must be evidence-based and independently verified.
- UI should be beginner-friendly: grouped tabs, guided modals, tips, and collapsible advanced details.
- Milestone-based delivery with Chinese commit messages.

## 3. Provider Architecture

### 3.1 Adapter Interface

Each provider implements:

```text
ProviderAdapter
- auth
- validateAuth
- list
- getMetadata
- fastUpload
- download
- upload
- createFolder
- checkQuota
- riskPolicy
```

Each provider advertises one of:

```text
bidirectional
sourceOnly
targetOnly
experimental
```

### 3.2 Fingerprint Model

Keep these fields in English:

```text
md5
sha1
sha256
crc64
gcid
etag
pickcode
blockListMd5
raw
```

Fast-upload decision is provider-specific via `fastUploadInputs`, not a one-rule-fits-all check.

## 4. Auth Strategy

### 4.1 Supported Auth Modes

```text
official_oauth
web_login_capture
manual_cookie
manual_token
openlist_style_reference
```

### 4.2 Auth Flow

1. Select provider
2. Open auth modal wizard
3. Complete one supported mode (web capture / token / cookie / advanced fields)
4. Run minimum validation (profile/root list/token refresh check)
5. Save local auth profile with masked display

Auth failure must return readable reasons:

- session expired
- missing required headers/cookies/tokens
- verification challenge/risk-control interruption
- endpoint changed

## 5. Fast Upload and Fallback

### 5.1 Execution Priority

```text
1. collect source metadata + fingerprints
2. match target fast-upload requirements
3. try fast upload
4. fallback by threshold policy
5. queue pending/manual items
```

### 5.2 Threshold Policy

Examples:

- `0MB`: always manual confirmation on fallback
- `200MB`: auto fallback for <=200MB
- `1GB`: auto fallback for <=1GB

### 5.3 Risk Control

- low default concurrency
- batch interval and retry backoff
- circuit-break on repeated failures
- pause on risk-control-like responses
- no infinite retries

## 6. Folder Execution Order

For selected top-level folders:

1. process selected top-level folders by selection order
2. inside each top-level folder, process deepest subfolders first
3. then roll upward to parent folders
4. move to next selected top-level folder

Example tree:

```text
1
├─ 11
│  ├─ 111
│  ├─ 112
│  └─ 113
2
├─ 21
│  ├─ 211
│  ├─ 212
│  └─ 213
```

Expected order:

```text
1/11/111
1/11/112
1/11/113
1/11
1
2/21/211
2/21/212
2/21/213
2/21
2
```

## 7. UI Requirements

Main tabs:

- New Task
- Auth Management
- Transfer Queue
- Pending
- Provider Capability
- Settings

UX rules:

- avoid dense all-in-one pages
- use wizard modal for auth
- keep advanced details collapsible
- default to tips/hover guidance for non-critical text
- show important alerts inline by default

## 8. I18N Rules

- default language: Chinese
- full English mode available
- technical/provider-specific field names remain English (`md5`, `gcid`, `rapid upload`, `fallback`, `token`, `cookie`)

## 9. Provider Scope

### 9.1 First-Wave Must-Have Providers

| Provider | Key | Priority Reason | First-Wave Goal |
|---|---|---|---|
| Guangya | `guangya` | required by user | auth + list + md5/gcid fast-check + fallback upload |
| Aliyun Drive Open | `aliyundrive_open` | common and documented | oauth + list + metadata + fast capability check |
| 115 | `115` / `115_open` | common with rich fast-upload references | auth + list + fast capability research |
| Tianyi 189 | `189cloud` | common operator drive | auth + list + metadata hash extraction |
| Baidu Netdisk | `baidu_netdisk` | common but high risk-control complexity | auth + conservative fallback policy |
| Quark | `quark` | increasingly common | cookie auth + list + metadata |
| UC | `uc` | similar ecosystem with Quark | cookie auth + list + metadata |
| Xunlei | `xunlei` | high `gcid` relevance | auth + list + gcid extraction |
| PikPak | `pikpak` | common cross-transfer demand | auth + list + hash capability research |
| 123 Pan | `123pan` / `123_open` | common use with open platform path | token auth + list + upload/fast research |

### 9.2 Second-Wave Providers

- `139yun`
- `wopan`
- `weiyun`
- `lanzou` / `new_lanzou`
- `google_drive`
- `onedrive`
- `dropbox`
- `mega`
- `webdav`
- `s3`

## 10. Provider Status Lifecycle

```text
planned
researching
auth_ready
list_ready
metadata_ready
fast_check
fast_ready
fallback_ready
risky
experimental
```

## 11. Milestones

### M1. Independent Skeleton

- FastAPI + static frontend
- local admin password login
- i18n base
- Windows launcher scripts

Commit:

`初始化 CloudPan Sync 独立互传项目`

### M2. Adapter + Capability Model

- `ProviderAdapter` abstraction
- `FingerprintSet` model
- provider registry
- mock providers for source<->target planning validation

Commit:

`建立多网盘互传能力模型`

### M3. Auth System

- `AuthProfile`
- token/cookie/manual and web-capture support
- masked storage and auth validation API

Commit:

`建立多网盘授权模型`

### M4. Guangya Provider

- extract Guangya logic with reference to:
  - `C:\Users\ChowYu\Desktop\新建文件夹 (3)\秒传.js`
- auth/list/fast-check/error mapping/risk hints

Commit:

`接入光鸭网盘基础能力`

### M5. First-Wave Common Providers

- onboard 2-3 providers iteratively
- for each: auth + list + metadata first, then fast/upload execution

Commit examples:

- `补充首批常用网盘能力研究`
- `接入某网盘目录与元数据能力`

### M6. Transfer Planner

- fast-first strategy
- fallback threshold strategy
- pending queue
- bottom-up folder-order execution planner

Commit:

`实现网盘互传任务规划`

### M7. Controlled Runtime + UX Polish

- pause/resume/retry
- risk-control pause
- queue status visibility
- tabs/submenus/modals/tips/collapsible details polish
- complete CN/EN copy

Commit:

`完成受控互传执行与易用页面`

## 12. Testing Strategy

Run tests milestone-by-milestone instead of after every tiny change.

Unit tests:

- capability matching
- fingerprint normalization
- fast/fallback decision
- folder execution order
- auth masking and state handling
- error classification

API tests:

- login guard
- auth save/validate
- provider registry
- transfer plan creation
- queue status query

UI smoke:

- login
- tab navigation
- auth modal flow
- new task flow
- pending collapsible details
- language switch

Live validation principles:

- small sample first
- low concurrency first
- explicit distinction between mock success and real provider success

## 13. Explicit Non-Goals

- Do not make this product "many providers to Guangya only".
- Do not use AList/OpenList as runtime kernel.
- Do not default to aggressive unattended bulk fallback.
- Do not claim provider fast-upload support without evidence.
- Do not run full test suites on every tiny code change.

