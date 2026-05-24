# CloudPan Sync 计划完成度审计报告

- 生成时间：`2026-05-24T08:53:35.614176+00:00`
- 汇总：`done=5` `partial=2` `todo=1`
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
- 证据：授权存储、脱敏展示、校验与网页登录引导 API 已实现；授权列表接口现会返回 provider-aware 的 `missingFieldHints / profileReady`，并补充 `resolvedParentId / resolvedFileId`，可在点击 validate 前先暴露档案缺口并直接复用解析后的默认值；现也支持直接编辑已有 auth profile 并重新校验，补字段时无需删除重建。
- 缺口：真实网页登录抓取自动化尚未实现。

### M4 - 光鸭 Provider
- 状态：`partial`
- 证据：光鸭预检（md5/gcid）已实现，目录、metadata、create_dir、live fast-upload inventory check，以及任务运行阶段基于 targetProfileId + localPath 的 fallback live attempt 已支持真实二进制上传链路（guangyaclient file_upload / upload_token + cdn_upload）。上传成功后现会继续尝试 post-upload verify：优先用返回 fileId 做 live metadata 确认，拿不到 fileId 时退回 parentId + 文件名的 live list 确认。失败时会返回更明确的授权/输入/风控/限流类风险提示；save-time/provider-aware 校验已补 `parent_id / parentFileId / dirId / pid` 等常见别名兼容，并会直接返回 `requiredFieldHints`。
- 缺口：仍缺稳定的真实在线联调成功样本，因此 M4 继续保持 partial。

### M5 - 首批常用网盘接入
- 状态：`partial`
- 证据：首批 provider 已补齐到 10 个，研究索引 10 条；其中 aliyundrive_open 已支持基于已保存 access token + domainId/driveId 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；123_open 已支持基于已保存 token 的真实 list/metadata(parentFileId scoped)/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；115_open 已支持基于已保存 cookie 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；xunlei 已支持基于 token + device headers 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；pikpak 已支持基于 token 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；baidu_netdisk 已支持基于 access token 或 cookie 的保守 live list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；quark 与 uc 已支持基于 cookie + pwdId 的分享链路 live list/metadata(MD5 via file/download) 与 create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；189cloud 已支持基于分享参数的真实 list/metadata 尝试，并且任务运行阶段现已接入显式 create_dir blocked probe，会把 shareCode/accessCode 只读限制与 `AccessToken/Signature/Date` 这类账号级写鉴权缺口落成真实 runtime 样本；状态矩阵现已额外显式量化 create_dir 能力以及 task runtime 轨道，当前可区分 `runtime_active / runtime_candidate / runtime_blocked`。
- 缺口：当前仅剩 189Cloud 仍缺真正可写成功的任务运行链路；它虽然已能在 runtime 样本里显式暴露 blocked probe 与所需鉴权头，但仍停留在 shareCode/accessCode 只读链路，尚未接入账号级 OAuth 写接口。Quark/UC 的 upload 链路还未接入，百度与 PikPak 的秒传证据也还缺失。

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
- 证据：已具备本地 mock 验证链路，并新增真实证据状态报告与任务运行真实样本持久化能力，可按 provider 量化当前已保存的 auth/list/metadata/create_dir/task_runtime 真实证据覆盖；其中 Guangya 已接真实上传链路，aliyundrive_open、123_open、115_open、xunlei、pikpak、baidu_netdisk、quark 与 uc 已接任务运行阶段真实 create_dir 写探针，189cloud 也已能落出显式 blocked probe 样本与所需鉴权头。
- 缺口：尚未提供首批 provider 的真实联调成功证据（认证、目录、元数据、秒传/降级路径）；任务运行阶段虽已支持成功/失败样本持久化，但当前仍缺足够的真实成功样本来收敛 P-REAL。
