# 已完成里程碑

> 仅记录已完成并已提交的里程碑。

## 里程碑清单

### M1 - 独立项目骨架

- 完成日期：`2026-05-23`
- 提交：`46a20a3`
- 完成范围：
  - FastAPI 后端与静态前端骨架
  - 本地管理员密码登录保护
  - 中英 i18n 基础 API 与页面切换
  - Windows 启动脚本（`pwsh` 优先，PowerShell 回退）
- 验证证据：
  - `GET /api/health` 返回 `{"status":"ok"}`
  - `POST /api/login` 默认密码可登录
  - `GET /api/session` 登录后返回 `{"loggedIn":true}`

### M2 - 适配器与能力模型

- 完成日期：`2026-05-23`
- 提交：`a456f54`
- 完成范围：
  - `ProviderAdapter` 抽象与 ProviderProfile 模型
  - Provider registry API（首批能力元数据）
  - mock 互传规划 API（source -> target）
- 验证证据：
  - `GET /api/providers` 返回 provider 能力列表
  - `POST /api/plan/mock`（登录后）返回策略明细和统计

### M3 - 授权系统

- 完成日期：`2026-05-23`
- 提交：`0e0f7ed`
- 完成范围：
  - `AuthProfile` 模型与本地授权存储
  - 授权 API：新增/查询/删除/校验
  - 网页登录抓取引导 API（`capture_pending`）
  - `Auth` 页签授权管理面板
- 验证证据：
  - `POST /api/auth/profiles` 返回脱敏 token（如 `tok_***56`）
  - `GET /api/auth/profiles` 返回当前会话授权列表
  - `POST /api/auth/profiles/{id}/validate` 状态变为 `verified`
  - `POST /api/auth/capture/start` 返回 `capture_pending`
  - `DELETE /api/auth/profiles/{id}` 成功，列表数量回到 `0`

### M4 - 光鸭基础能力

- 完成日期：`2026-05-23`
- 提交：`ed6a170`
- 完成范围：
  - 光鸭 `md5/gcid` 归一化与秒传预检逻辑
  - 光鸭 API：
    - `POST /api/providers/guangya/list`（本地 mock 列表）
    - `POST /api/providers/guangya/fast_check`（本地预检 + 风险提示）
  - 明确标注本里程碑是本地预检，不是实盘全量联调
- 验证证据：
  - `POST /api/providers/guangya/list` 返回 `mode=mock`
  - `POST /api/providers/guangya/fast_check` 同时返回支持/不支持样例

### M5 - 首批常用网盘基础接入

- 完成日期：`2026-05-23`
- 提交：`1d28219`
- 完成范围：
  - provider 研究索引（含 `guangya`、`aliyundrive_open`、`115_open`、`quark`）
  - 通用 provider API：
    - `GET /api/providers/research`
    - `POST /api/providers/{providerKey}/list`（mock）
    - `POST /api/providers/{providerKey}/metadata`（mock + hash）
  - 覆盖首批非光鸭 provider 的可执行接口骨架
- 验证证据：
  - `GET /api/providers/research` 返回 `4` 条研究记录
  - `POST /api/providers/aliyundrive_open/list` 返回 `mode=mock`
  - `POST /api/providers/115_open/metadata` 返回非空 `md5`

### M6 - 互传规划增强

- 完成日期：`2026-05-23`
- 提交：`6f6a9ff`
- 完成范围：
  - 规划输入新增 `selectedRoots`
  - 规划输出新增 `executionGroups` 与 `pendingItems`
  - 实现“顶层顺序 + 最底层优先”执行分组
  - 保留阈值降级策略（`download_upload` / `pending_manual`）
- 验证证据：
  - `POST /api/plan/mock` 传入 `selectedRoots=['/1','/2','/3']` 后，分组根顺序为 `/1,/2,/3`
  - 返回 `pendingItems` 与策略统计
  - 样例结果包含 `fast_upload` / `download_upload` / `pending_manual` 三类

### M7 - 受控执行与队列视图

- 完成日期：`2026-05-23`
- 提交：`db82978`
- 完成范围：
  - 任务状态机：创建/查询 + `run`/`pause`/`resume`/`retry`
  - 风控暂停标记（pending_manual 较高时）
  - 队列 API：
    - `GET /api/tasks`
    - `POST /api/tasks`
    - `GET /api/tasks/{taskId}`
    - `POST /api/tasks/{taskId}/action`
  - 队列页基础操作与进度展示
- 验证证据：
  - pending_manual 较多的任务初始为 `risk_paused`
  - 动作流 `resume -> run -> retry -> pause` 可执行
  - 状态流转包含 `completed`、`ready`、`paused` 且保留 pending 计数

### M8 - 首批 Provider 清单补全（骨架级）

- 完成日期：`2026-05-23`
- 完成范围：
  - 按 `PROJECT_PLAN_MERGED_RAW.md` 首批清单补全 provider registry 到 10 个：
    - `guangya`
    - `aliyundrive_open`
    - `115_open`
    - `189cloud`
    - `baidu_netdisk`
    - `quark`
    - `uc`
    - `xunlei`
    - `pikpak`
    - `123_open`
  - 补全 provider 研究索引为 10 条，统一保留 `authModes/status/lastVerifiedAt/notes`
  - 为新增 provider 接入通用 `list/metadata` mock 能力，便于后续实盘替换
- 验证证据：
  - `GET /api/providers` 返回 `providerCount=10`
  - `GET /api/providers/research` 返回 `researchCount=10`
  - 对新增 `189cloud/baidu_netdisk/uc/xunlei/pikpak/123_open` 逐个验证：
    - `POST /api/providers/{key}/list` 返回非空
    - `POST /api/providers/{key}/metadata` 返回非空 `md5`

### M9 - 计划完成度审计与报告导出

- 完成日期：`2026-05-23`
- 完成范围：
  - 新增计划审计模块 `plan_audit.py`，输出结构化完成度结果
  - 新增审计 API：
    - `GET /api/plan/audit`
    - `GET /api/plan/audit_markdown`
  - 新增报告导出脚本 `scripts/export_plan_audit.py`
  - 生成仓库审计文档：`docs/PLAN_AUDIT_REPORT.md`
- 验证证据：
  - `GET /api/plan/audit` 返回汇总结果：`done=4, partial=3, todo=1`
  - `GET /api/plan/audit_markdown` 返回非空 Markdown
  - 执行导出脚本后生成 `docs/PLAN_AUDIT_REPORT.md`

### M10 - UI 交互补齐（向导/弹窗/tip/折叠）

- 完成日期：`2026-05-23`
- 完成范围：
  - 新增“新建任务”二级步骤条（6 步流程可视）
  - 新增授权弹窗（Web Login Capture）并接入 `capture/start` 指引
  - 授权页新增 tip 提示与高级字段折叠区（`details/summary`）
  - 保持队列页可用，未破坏 `tasks` 相关接口联动
- 验证证据：
  - `POST /api/auth/capture/start` 返回 `capture_pending`
  - 首页 HTML 包含 `wizard-steps` 与 `authModal` 结构
  - `GET /api/tasks` 正常返回（`hasItemsField=true`）

### M11 - 首批 Provider 在线探测验证层

- 完成日期：`2026-05-23`
- 完成范围：
  - 新增 `live_probe` 模块，对 provider 的 `officialDocsUrl/webLoginUrl` 执行在线探测
  - 新增探测 API：
    - `GET /api/providers/live_probe`
    - `GET /api/providers/live_probe_markdown`
  - 新增报告导出脚本：
    - `scripts/export_live_probe_report.py`
  - 生成探测报告文档：
    - `docs/PROVIDER_LIVE_PROBE_REPORT.md`
- 验证证据：
  - `GET /api/providers/live_probe` 返回：
    - `providerCount=10`
    - `totalChecks=12`
    - `failedChecks=0`
  - `GET /api/providers/live_probe_markdown` 返回非空 Markdown
  - 导出脚本成功生成 `docs/PROVIDER_LIVE_PROBE_REPORT.md`

### M12 - 基于授权档案的真实认证验证流程

- 完成日期：`2026-05-23`
- 完成范围：
  - 新增 `auth_live_validate` 模块：
    - 读取 `AuthProfile`
    - 携带 cookie/token/extra header 发起真实请求
    - 记录状态码、错误信息、最终 URL
    - 持久化到 `.cloudpan_sync_data/auth_live_validations.json`
  - 新增 API：
    - `POST /api/auth/live_validate`
    - `GET /api/auth/live_validations`
  - 新增报告导出脚本与文档：
    - `scripts/export_auth_live_validation_report.py`
    - `docs/AUTH_LIVE_VALIDATION_REPORT.md`
- 验证证据：
  - 使用 `baidu_netdisk` 测试授权档案触发真实认证验证：
    - `POST /api/auth/live_validate` 返回 `ok=true`, `status=200`
  - `GET /api/auth/live_validations` 返回记录条数 `records=1`
  - 导出脚本成功生成 `docs/AUTH_LIVE_VALIDATION_REPORT.md`

### M13 - 批量认证验证与结果汇总

- 完成日期：`2026-05-23`
- 完成范围：
  - 新增批量认证验证能力：
    - `POST /api/auth/live_validate_all`
  - 批量遍历所有已保存 `AuthProfile`，逐条执行真实请求验证并汇总结果
  - 验证结果持续写入 `.cloudpan_sync_data/auth_live_validations.json`，用于后续审计追踪
- 验证证据：
  - 批量创建并验证多 provider 测试档案后返回：
    - `totalProfiles=4`
    - `okProfiles=4`
    - `failedProfiles=0`
  - `GET /api/auth/live_validations` 返回累计记录 `validationRecords=5`
  - 导出脚本持续可用并已更新 `docs/AUTH_LIVE_VALIDATION_REPORT.md`

### M14 - Provider 状态矩阵与进度量化

- 完成日期：`2026-05-23`
- 完成范围：
  - 新增 `provider_status_matrix` 模块，聚合：
    - provider registry
    - provider research
    - auth live validation 结果
  - 新增状态矩阵 API：
    - `GET /api/providers/status_matrix`
    - `GET /api/providers/status_matrix_markdown`
  - 新增导出脚本和文档：
    - `scripts/export_provider_status_matrix.py`
    - `docs/PROVIDER_STATUS_MATRIX.md`
- 验证证据：
  - `GET /api/providers/status_matrix` 返回：
    - `providerCount=10`
    - `authReadyCount=3`
    - `fastCheckCount=5`
  - `GET /api/providers/status_matrix_markdown` 返回非空 Markdown
  - 导出脚本成功生成 `docs/PROVIDER_STATUS_MATRIX.md`
