# CloudPan Sync 计划完成度审计报告

- 生成时间：`2026-05-24T18:18:22.683448+00:00`
- 汇总：`done=5` `partial=2` `todo=1`
- 进度口径：`featureCompletionPercent=85.7` `strictCompletionPercent=75.0`
  - `featureCompletionPercent` = 只按 `M1-M7` 主功能里程碑计分，`done=1`、`partial=0.5`。
  - `strictCompletionPercent` = 把 `P-REAL` 真实联调一起纳入总验收后计分，`done=1`、`partial=0.5`。
- Provider覆盖：`providerCount=10` `researchCount=10`

## 审计明细

### M1 - 独立项目骨架
- 状态：`done`
- 证据：后端/前端/登录/i18n/启动脚本已存在并可运行。
- 缺口：无

### M2 - ProviderAdapter 与能力模型
- 状态：`done`
- 证据：ProviderAdapter、provider registry、mock plan API 已实现。
- 缺口：无

### M3 - 授权系统
- 状态：`done`
- 证据：授权存储、脱敏展示、校验与网页登录引导 API 已实现；授权列表接口现会返回 provider-aware 的 `missingFieldHints / profileReady`，并补充 `resolvedParentId / resolvedFileId`，可在点击 validate 前先暴露档案缺口并直接复用解析后的默认值；现也支持直接编辑已有 auth profile 并重新校验，补字段时无需删除重建；其中 189Cloud 账号级写鉴权现已额外支持从 captured headers/curl 文本提取 `accessToken/signature/date` 后回填现有档案。
- 缺口：真实网页登录抓取自动化尚未实现。

### M4 - 光鸭 Provider
- 状态：`partial`
- 证据：光鸭预检（md5/gcid）已实现，目录、metadata、create_dir、live fast-upload inventory check，以及任务运行阶段基于 targetProfileId + localPath 的 fallback live attempt 已支持真实二进制上传链路（guangyaclient file_upload / upload_token + cdn_upload）。上传成功后现会继续尝试 post-upload verify：优先用返回 fileId 做 live metadata 确认，拿不到 fileId 时退回 parentId + 文件名的 live list 确认。失败时会返回更明确的授权/输入/风控/限流类风险提示；save-time/provider-aware 校验已补 `parent_id / parentFileId / dirId / pid` 等常见别名兼容，并会直接返回 `requiredFieldHints`。
- 缺口：仍缺稳定的真实在线联调成功样本，因此 M4 继续保持 partial。

### M5 - 首批常用网盘接入
- 状态：`partial`
- 证据：首批 provider 已补齐到 10 个，研究索引 10 条；其中 aliyundrive_open 已支持基于已保存 access token + domainId/driveId 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实小文件上传链路：当前可按 `overwrite_existing / auto_rename_new` 选择同名处理，通过 `create -> upload_url PUT -> complete` 完成 Aliyun Drive Open 本地文件直传，并在成功后继续做 `metadata_by_file_id / list_by_parent_name` 校验；123_open 已支持基于已保存 token 的真实 list/metadata(parentFileId scoped)/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；115_open 已支持基于已保存 cookie 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；xunlei 已支持基于 token + device headers 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；pikpak 已支持基于 token 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；baidu_netdisk 已支持基于 access token 或 cookie 的保守 live list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；quark 与 uc 已支持基于 cookie + pwdId 的分享链路 live list/metadata(MD5 via file/download) 与 create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；189cloud 已支持基于分享参数的真实 list/metadata 尝试，且 `createFolder.action` 现已接入账号级 `AccessToken/Signature/Date` 写目录尝试，share-only 场景仍会诚实返回只读阻断；状态矩阵现已额外显式量化 create_dir 能力、fast_check 能力、同名冲突策略支持状态、task runtime 轨道以及 runtime 冲突处理样本计数，当前首批 10 个 provider 都已能在矩阵中量化为 `fast_check=true`，并区分 `overwrite_existing`/`auto_rename_new` 的 `supported / downgrade_to_auto_rename / probe_only_runtime_write_check / unsupported`。
- 缺口：189Cloud 目前仍缺真实在线成功样本；账号级写鉴权虽已补到 captured headers/curl 提取与回填脚本，且现在也已补到 runtime fast-upload 候选探针证据，但稳定可复用的真实来源样本仍缺，shareCode/accessCode-only 档案依旧不可写。123Pan Open、115 Open、Xunlei、Quark、UC 的真实 upload 链路还未接入；百度、PikPak、Aliyun Drive Open、123Pan Open、115 Open、Xunlei、Quark、UC、189Cloud 的真实秒传 API 成功样本仍缺。

### M6 - 互传任务规划
- 状态：`done`
- 证据：selectedRoots、executionGroups、pendingItems 与阈值策略已实现。
- 缺口：无

### M7 - 受控执行与 UI
- 状态：`done`
- 证据：任务状态机、队列/待处理/网盘能力/设置页签、授权弹窗、tip、折叠区与中英文文案已接入当前页面；授权列表会直接显示 `profileReady/missingFieldHints` 与最近一次 validation riskHint，任务表单和 live probe 请求会优先使用档案返回的 `resolvedParentId / resolvedFileId`，并支持进入编辑态更新现有档案。
- 缺口：无

### P-REAL - 真实联调验证
- 状态：`todo`
- 证据：已具备本地 mock 验证链路，并新增真实证据状态报告与任务运行真实样本持久化能力，可按 provider 量化当前已保存的 auth/list/metadata/create_dir/task_runtime 真实证据覆盖；其中 Guangya 已接真实上传链路，aliyundrive_open 现也已接任务运行阶段真实本地文件上传链路，123_open、115_open、xunlei、pikpak、baidu_netdisk、quark 与 uc 已接任务运行阶段真实 create_dir 写探针，189cloud 也已能在 share-only 场景落出 blocked probe 样本，并在账号级鉴权齐备时发起 createFolder.action 写目录尝试。
- 缺口：尚未提供首批 provider 的真实联调成功证据（认证、目录、元数据、秒传/降级路径）；任务运行阶段虽已支持成功/失败样本持久化，但当前仍缺足够的真实成功样本来收敛 P-REAL。
