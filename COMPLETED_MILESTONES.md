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
