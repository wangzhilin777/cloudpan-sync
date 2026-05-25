# 已完成里程碑

> 仅记录已经完成并且当前代码/接口可验证的里程碑。
>
> 截至本次核对，`M4 光鸭基础能力`、`M5 首批常用网盘基础接入` 仍存在计划内缺口，因此暂不列入“已完成”。

> 本文件允许记录“未独立成完整里程碑、但已经完成且有当前代码/脚本证据支撑”的补齐项，前提是不把 `partial/todo` 误写成已完成。

## 里程碑清单

### 已完成补齐项 - `2026-05-26`

- 提交：`补充传输队列直接补救动作`
- 完成范围：
  - 已把 `传输队列` 主列表从“只展示 targetProfile 状态、guard、riskHint、requiredAuth 和最近结果”推进成可直接跳转补救；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会在每个任务行旁边直接渲染 `Focus Profile / Refresh Evidence / Run Live Probe / Open Capture`
  - 当前动作会优先按任务自带的 `targetProfileId` 匹配目标档案，匹配不到时再按 `targetProvider` 兜底；因此当任务因为目标档案未就绪、写链路 blocker、鉴权缺失或 liveAttempt 风险而卡住时，可以直接从任务行进入授权补救，而不需要先去设置页或授权列表重新找对应 provider/profile
  - 这次补齐把“传输队列看到任务为什么失败/暂停，但补救动作散落在别处”的流程，推进成“看到任务风险 -> 直接点动作 -> 修复后重试/继续”的产品内闭环，也更贴近计划里对队列与执行控制可操作性的要求
  - 已同步补强 [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py)，把任务行补救动作文本与事件绑定一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_task_list_runtime_ui.py` 已验证 `传输队列` 当前包含 `Focus Profile / Refresh Evidence / Run Live Probe / Open Capture` 文本以及对应绑定
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证任务列表复用的 `refreshRealEvidenceRemediationProfile()`、`probeRealEvidenceRemediationProfile()` 链路未回退
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗与 capture guide 主链路未回退，登录后仍可正常走 `/api/auth/capture/start` 与 `/api/auth/capture/parse`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充待处理列表直接补救动作`
- 完成范围：
  - 已把 `待处理` 面板从“只展示 pending manual / conflict / missing fast inputs 信息”推进成可直接跳转补救；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会在每条待处理项旁边直接渲染 `Focus Profile / Refresh Evidence / Run Live Probe / Open Capture`
  - 当前动作会优先按任务自带的 `targetProfileId` 匹配已保存目标档案，匹配不到时再按 `targetProvider` 兜底；因此用户在看到某条待处理项因为目标鉴权、写链路或补指纹问题被挂起时，可以直接跳到对应授权档案、刷新 evidence、重跑 live probe，或者直接打开 provider 的网页登录抓取引导
  - 这次补齐把“待处理列表只是告诉你为什么卡住，但还要自己再去别处修”的流程，推进成“看到待处理项 -> 直接点动作 -> 修完再回来继续”的产品内闭环，也更贴合计划里对待处理队列可操作性的要求
  - 已同步补强 [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py)，把 pending list 的目标档案承载字段、动作按钮文本与事件绑定一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_task_list_runtime_ui.py` 已验证 pending list 当前会承载 `targetProfileId`，并包含 `Focus Profile / Refresh Evidence / Run Live Probe / Open Capture` 文本及对应绑定
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证待处理区复用的 `refreshRealEvidenceRemediationProfile()`、`probeRealEvidenceRemediationProfile()` 链路未回退
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗与 capture guide 主链路未回退，登录后仍可正常走 `/api/auth/capture/start` 与 `/api/auth/capture/parse`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充任务预览风险直接补救动作`
- 完成范围：
  - 已把 `新建任务 -> Plan Preview` 从“只显示 targetProfile missing/not ready/not write-ready 风险文字”推进成可直接跳转补救；这次补齐后，[index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 新增了 `taskPlanPreviewActions` 区域，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会在预览面板里直接渲染 `Focus Profile / Refresh Evidence / Run Live Probe / Open Capture / Create Stub`
  - 当前动作会基于已选 `targetProfile` 与 `targetProvider` 自动复用已有恢复链路：若已经选中了目标档案，可直接聚焦授权表单、刷新 evidence、重跑 live probe；若当前 provider 还没有档案或需要重新抓取，则可以直接打开网页登录抓取引导，或在支持的场景下直接创建 placeholder stub
  - 这次补齐把“预览已经明确提示任务为什么会被拦住，但用户还要自己切页面修”的流程，推进成“看到风险 -> 直接点动作 -> 修完再回来预览/建任务”的产品内闭环，更贴近计划里对小白用户可操作性的要求
  - 已同步补强 [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py)，把 `taskPlanPreviewActions`、按钮文本与事件绑定一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_queue_plan_preview_ui.py` 已验证 `Plan Preview` 当前包含 `taskPlanPreviewActions` 以及 `Focus Profile / Refresh Evidence / Run Live Probe / Open Capture / Create Stub` 按钮和对应事件绑定
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证预览区复用的 `refreshRealEvidenceRemediationProfile()`、`probeRealEvidenceRemediationProfile()`、`createRemediationProfile()` 链路未回退
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗与 capture guide 主链路未回退，登录后仍可正常走 `/api/auth/capture/start` 与 `/api/auth/capture/parse`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充运行证据样本直接补救动作`
- 完成范围：
  - 已把设置页里的 `Task Runtime Evidence` 从“只展示 success / failed / probe / blocked 样本摘要”推进成可直接触发补救动作；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会为运行证据样本行直接追加 `Focus Profile / Refresh Evidence / Run Live Probe / Open Capture`
  - 当前动作会优先按样本自带的 `profileId` 匹配已保存档案，匹配不到时再按 `providerKey` 兜底；因此用户在看到某条 runtime failed、probe-only、blocked 或 conflict-handled 样本时，可以直接跳到对应授权档案、刷新 auth/list/metadata/create_dir evidence、重跑 live probe，或者直接打开网页登录抓取引导，不再需要自己先抄 sample 里的 provider/profile 信息再切页面
  - 这次补齐让“运行样本 -> 授权补救 -> 重新验证”的闭环也进入产品内可点击状态，继续把 `P-REAL` 当前缺的那部分恢复动作从命令行/文字提示往 UI 闭环方向推进
  - 已同步补强 [verify_task_runtime_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_settings_ui.py)，把 `Task Runtime Evidence` 行内动作按钮文本和事件绑定一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_task_runtime_evidence_settings_ui.py` 已验证 `Task Runtime Evidence` 当前包含 `Focus Profile / Refresh Evidence / Run Live Probe / Open Capture` 文本以及对应绑定
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证底层 `refreshRealEvidenceRemediationProfile()`、`probeRealEvidenceRemediationProfile()` 等复用链路未回退
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗与 capture guide 主链路未回退，登录后仍可正常走 `/api/auth/capture/start` 与 `/api/auth/capture/parse`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充授权档案列表直接打开抓取引导`
- 完成范围：
  - 已把“授权管理”页里的 auth profile 行再往前推进一步；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 不再只是展示 `missing / patch_hint / write_blocker`，当档案存在缺字段、`needsSecretRefresh` 或 `writeReady=false` 时，会直接在该 profile 行旁边渲染 `Open Capture`
  - 现在用户在授权列表里看到某个档案缺少字段、secret 仍像占位值，或者当前写链路被 blocker 卡住时，不需要先切到设置页或手动再选 provider，就可以直接从这条档案打开对应 provider 的网页登录抓取引导
  - 这次补齐把“看到 auth profile 缺口 -> 直接打开抓取引导 -> 补真实凭证 -> 再刷新 evidence / validate / live probe”的入口前移到了授权管理主列表，更贴近普通用户最先接触 auth 问题的位置
  - 已新增 [verify_auth_profile_actions_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_profile_actions_ui.py)，把 auth 列表里的 `Open Capture` 条件、按钮文本与事件绑定一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_profile_actions_ui.py` 已验证 auth 列表当前会基于 `missingFieldHints / needsSecretRefresh / writeReady` 决定是否展示 `Open Capture`，并已绑定 `openCaptureGuideForProvider(item.providerKey)`
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗与 capture guide 主链路未回退，登录后仍可正常走 `/api/auth/capture/start` 与 `/api/auth/capture/parse`
  - `.\.venv\Scripts\python.exe scripts\verify_auth_settings_ui.py` 已验证设置页原有 `Auth Remediation` 聚焦与抓取动作链路未回退
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充网盘能力页真实证据补救动作`
- 完成范围：
  - 已把 `网盘能力` 页里的 `Provider Matrix / Provider Research` 从“能看到 real_evidence_gaps 但基本只读”推进成可直接触发补救动作；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会在 provider 行内直接追加 `Focus Profile / Refresh Evidence / Run Live Probe / Open Capture / Create Stub`
  - 当前动作会按 provider 自动复用已有恢复链路：有已保存档案时可直接聚焦到授权表单并刷新 evidence，支持 live probe 的 provider 还可直接在这一页重跑探测；遇到 `needsSecretRefresh` 或尚未建档时，则可以直接打开网页登录抓取引导，或在支持的场景下一键创建 placeholder stub
  - 这次补齐把之前主要集中在“设置页补救面板”的恢复入口，进一步前移到普通用户更容易先看到的 `网盘能力` 页，让“看到某个 provider 证据缺口 -> 直接补救”不再要求先切多个页面找对应按钮
  - 已同步补强 [verify_provider_real_evidence_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_real_evidence_ui.py)，把 provider 行级补救动作函数、按钮文本和事件绑定一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_provider_real_evidence_ui.py` 已验证 `appendProviderRecoveryActions()`、`Focus Profile / Refresh Evidence / Run Live Probe / Open Capture / Create Stub` 文本以及对应事件绑定已接入 `Provider Matrix / Provider Research`
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证底层设置页补救动作链路未回退，provider 页复用的 `refreshRealEvidenceRemediationProfile()`、`probeRealEvidenceRemediationProfile()`、`createRemediationProfile()` 仍保持可用
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗与 capture guide 主链路未回退，登录后仍可正常走 `/api/auth/capture/start` 与 `/api/auth/capture/parse`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充运行样本脱节打开抓取引导`
- 完成范围：
  - 已把 `Runtime Orphan Recovery` 的设置页恢复动作再往前推进一步；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 不再只给 `Recreate Stub`，每条 orphan 恢复行还会同步带出 `Open Capture`
  - 现在用户在看到 `runtime_orphan` 样本时，可以一边按原 `profileId` 重建 placeholder stub，一边直接打开对应 provider 的网页登录抓取引导，不需要先离开恢复面板再手动切 provider 才能补真实凭证
  - 这次补齐把上一轮 `Runtime Orphan Recovery -> Recreate Stub -> 切回授权页补字段` 的闭环，继续推进成 `Runtime Orphan Recovery -> Recreate Stub / Open Capture -> 补真实凭证 -> 再跑 validation/live probe`，更贴近当前仓库里 `runtime_orphan` 的真实补救节奏
  - 已同步补强 [verify_runtime_orphan_recovery_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_runtime_orphan_recovery_settings_ui.py)，把 orphan 面板里的 `Open Capture` 文本与事件绑定一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_runtime_orphan_recovery_settings_ui.py` 已验证设置页当前包含 `Recreate Stub` 与 `Open Capture` 两个 orphan 恢复动作，以及 `openCaptureGuideForProvider(item.providerKey)` 绑定
  - `.\.venv\Scripts\python.exe scripts\verify_runtime_orphan_recovery.py` 已验证原有 runtime orphan recovery payload / markdown / nextStep 口径未回退
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗与 capture guide 主链路未回退，登录后仍可正常走 `/api/auth/capture/start` 与 `/api/auth/capture/parse`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充真实证据补救面板直接刷新与探测`
- 完成范围：
  - 已把 `Real Evidence Remediation` 从“只显示 recommendedRefreshEvidenceCommand / recommendedRuntimeProbeCommand 文案”继续推进成应用内可执行动作；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会直接从 `item.profileIds` 识别当前 provider 的已保存档案，并在补救行旁边渲染 `Focus Profile / Refresh Evidence / Run Live Probe`
  - `Focus Profile` 会直接复用已有授权页聚焦逻辑，把对应档案载入主授权表单；`Refresh Evidence` 会直接复用现有 `/api/auth/profiles/{profileId}/refresh_evidence` 链路刷新 auth/list/metadata/create_dir 证据；`Run Live Probe` 会直接复用 `/api/providers/live_probe_profile` 对当前档案触发 live probe，不再要求用户自己先抄命令再手动找 profileId
  - 对于 `needsSecretRefresh` 或当前还没有档案、需要先建 stub 的 provider，补救行现在也会直接带出 `Open Capture`，可以一键打开对应 provider 的网页登录抓取引导；已有 `recommendedCreateCommand` 的行仍继续保留 `Create Stub`，因此补救面板当前已经能覆盖“聚焦现有档案 / 刷新证据 / 直接探测 / 打开抓取 / 建立占位档案”这一组最常见恢复动作
  - 这次补齐仍然没有虚报 `P-REAL` 完成，只是把原本散落在设置页、授权页、live probe 和抓取弹窗之间的已有能力进一步串成产品内闭环，让真实证据补齐过程更接近“看到缺口 -> 直接点动作 -> 刷新证据/补凭证/重跑探测”
  - 已同步补强 [verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)，把 `refreshRealEvidenceRemediationProfile()`、`probeRealEvidenceRemediationProfile()`、`Open Capture` 与 `Focus Profile / Refresh Evidence / Run Live Probe` 这组按钮和绑定一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页当前包含 `refreshRealEvidenceRemediationProfile()`、`probeRealEvidenceRemediationProfile()`、`Focus Profile / Refresh Evidence / Run Live Probe / Open Capture / Create Stub` 按钮文本以及对应事件绑定
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 remediation bundle 当前仍会稳定产出 `profileIds / recommendedRefreshEvidenceCommand / recommendedRuntimeProbeCommand / recommendedPrimaryCommand / recommendedOverwriteVariantCommand` 等补救上下文字段，供前端动作复用
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗与 capture guide 主链路未回退，登录后仍可正常走 `/api/auth/capture/start` 与 `/api/auth/capture/parse`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充授权补救聚焦与抓取引导`
- 完成范围：
  - 已补齐 `Auth Remediation` 的前端执行闭环；这次补齐后，设置页不再只有 `needsFix / needsSecretRefresh` 摘要行，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 还会继续渲染逐档案补救行，直接带出 `missing / placeholderSecretHints / writeMissing / patch / recreateProbe` 等当前补救上下文
  - 当前每条授权补救行都新增了 `Focus Profile` 与 `Open Capture` 两个动作：`Focus Profile` 会直接定位到现有 auth profile 并把它载入主授权表单，`Open Capture` 会按对应 provider 自动打开网页登录抓取弹窗并立即加载 capture guide，不再需要用户自己先手动切换 provider 再点弹窗
  - 这次补齐后，`Auth Remediation` 真正形成了“看到缺口 -> 直接跳到对应档案编辑 / 直接打开 provider 抓取引导 -> 补真实凭证 -> 保存再验证”的应用内最小闭环，而不是只剩一串 shell 命令或文字提示
  - 当前补救动作会和已有授权页逻辑复用：聚焦会直接调用现有 `fillAuthForm()`，抓取引导会复用 `openAuthModal()` + `startCaptureGuide()`，因此不会分叉出第二套不一致的授权交互
  - 已同步补强 [verify_auth_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_settings_ui.py)，把 `focusAuthRemediationProfile()`、`openCaptureGuideForProvider()`、逐档案动作按钮绑定以及补救行中的 `placeholderSecretHints / recreateProbe` 展示一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_settings_ui.py` 已验证设置页当前包含 `Focus Profile` / `Open Capture` 动作、`focusAuthRemediationProfile()`、`openCaptureGuideForProvider()` 以及逐档案补救行绑定
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗与 capture guide 主链路未回退，登录后仍可正常走 `/api/auth/capture/start` 与 `/api/auth/capture/parse`
  - `.\.venv\Scripts\python.exe scripts\verify_auth_capture_guide.py` 已验证 `quark / guangya / aliyundrive_open` 当前仍会返回各自 provider-aware 的结构化 capture guide
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充补救面板一键创建档案`
- 完成范围：
  - 已补齐 `Real Evidence Remediation` 的应用内创建动作；这次补齐后，[real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 不再只会为 `noProfiles` provider 输出 `recommendedCreateCommand / recommendedBootstrapCommand`，还可以直接在应用侧按 `providerKey` 创建一个 placeholder auth stub
  - 当前创建链会按 provider 自动带出最小占位字段：例如 `aliyundrive_open` 会预填 `YOUR_TOKEN + domainId + driveId`，`quark / uc` 会预填 `YOUR_COOKIE + pwdId`，`189cloud` 会预填 `shareCode / accessCode / accessToken / signature / date` 等必需占位项，避免“创建后还是空白表单”
  - [webapp.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/webapp.py) 现已新增 `POST /api/real_evidence_remediation/create_profile`，登录后可直接从设置页补救面板触发创建；若当前 provider 已经存在保存档案，接口会诚实返回 `already_exists`，不会重复写入第二份同类 stub
  - 设置页 `Real Evidence Remediation` 面板现已从“只展示 create 命令”推进成“可直接点按钮创建”；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会为带 `recommendedCreateCommand` 的 provider 渲染 `Create Stub` 按钮，点击后直接调 `/api/real_evidence_remediation/create_profile`，刷新 auth/remediation/status 摘要，并自动切到授权页把新建的档案载入表单
  - 这次补齐后，`Real Evidence Remediation` 与前一轮的 `Runtime Orphan Recovery` 形成了两条应用内恢复闭环：`noProfiles -> Create Stub -> 补真凭证`，`runtimeOrphan -> Recreate Stub -> 补真凭证`，不再只停留在 shell 命令层
  - 已新增 [verify_real_evidence_remediation_create_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_create_api.py)，并同步补强 [verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)，把匿名拦截、创建 stub、重复调用 `already_exists`、设置页按钮和前端绑定一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_create_api.py` 已验证匿名访问 `/api/real_evidence_remediation/create_profile` 会被拦截，登录后可直接为 `aliyundrive_open` 创建 placeholder stub，且会保留 `domainId / driveId` 占位字段；重复调用则返回 `already_exists`
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页当前包含 `createRemediationProfile()`、`/api/real_evidence_remediation/create_profile` 调用与 `Create Stub` 按钮绑定
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证原有 remediation bundle/API/Markdown 口径未回退，`recommendedCreateCommand / recommendedBootstrapCommand / recommendedPrimaryCommand` 等字段仍保持同步
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充运行样本脱节一键重建`
- 完成范围：
  - 已补齐应用侧恢复动作；这次补齐后，[runtime_orphan_recovery.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/runtime_orphan_recovery.py) 不再只会汇总 `runtime_orphan` 样本和给出 shell 命令，还能直接按 `providerKey + orphanProfileId` 重建一个带原 `profileId` 的 placeholder auth stub
  - 当前重建链会保留历史 orphan 的原 `profileId`，并按 provider 自动带出最小占位字段：例如 `guangya` 会预填 `YOUR_TOKEN + parentId`，`quark / uc` 会预填 `YOUR_COOKIE + pwdId`，`189cloud` 会预填 `shareCode / accessCode / accessToken / signature / date` 等写链路相关占位项，避免恢复后还是一张完全空白表单
  - [webapp.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/webapp.py) 现已新增 `POST /api/runtime_orphan_recovery/recreate_profile`，登录后可以直接从产品内触发 orphan stub 重建；若当前仓库已存在同 `profileId`，接口会诚实返回 `already_exists`，不会静默覆盖现有档案
  - 设置页的 `Runtime Orphan Recovery` 面板现已从“只展示 recreate 命令”推进成“可直接点按钮恢复”；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会为每条 orphan 样本渲染 `Recreate Stub` 按钮，点击后直接调 `/api/runtime_orphan_recovery/recreate_profile`，刷新授权/恢复摘要，并自动切到授权页把重建出的 stub 档案载入表单，方便继续手工补真实凭证
  - 这次补齐后，`Runtime Orphan Recovery` 真正形成了“发现 runtime orphan -> 应用内重建 stub -> 回到授权表单补真实凭证 -> 再继续 validation/live probe”的闭环，不再只停留在文档和命令提示层
  - 已新增 [verify_runtime_orphan_recreate_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_runtime_orphan_recreate_api.py)，并同步补强 [verify_runtime_orphan_recovery_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_runtime_orphan_recovery_settings_ui.py)，把匿名拦截、stub 重建、重复调用 `already_exists`、设置页恢复按钮和前端恢复动作一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_runtime_orphan_recreate_api.py` 已验证匿名访问 `/api/runtime_orphan_recovery/recreate_profile` 会被拦截，登录后可按原 `profileId=gy-orphan-api` 重建 Guangya orphan stub，重建后当前 recovery 列表会立即移除该 orphan，重复调用则会返回 `already_exists`
  - `.\.venv\Scripts\python.exe scripts\verify_runtime_orphan_recovery.py` 已验证原有 recovery payload/markdown/API 链路未回退，当前仍会输出 `--profile-id gy-orphan / uc-orphan` 这类恢复命令
  - `.\.venv\Scripts\python.exe scripts\verify_runtime_orphan_recovery_settings_ui.py` 已验证设置页当前包含 `recreateRuntimeOrphanProfile()`、`/api/runtime_orphan_recovery/recreate_profile` 调用与 `Recreate Stub` 按钮绑定
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充抓取文本解析与表单回填`
- 完成范围：
  - 已新增应用侧解析模块 [auth_capture_parse.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_capture_parse.py)，把粘贴进来的浏览器抓取文本继续拆成可消费的 `suggestedProfile / appliedFieldNames / stillMissingFieldHints / placeholderFieldHints`，不再只停在“打开登录页自己看着填”
  - 这次补齐后，[webapp.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/webapp.py) 新增 `POST /api/auth/capture/parse`，当前登录后可直接把 storage dump、cookie/header 文本、captured curl、share URL 粘贴给后端解析，再返回 provider-aware 的建议授权档案
  - 当前解析链会按 provider 继续抽取关键字段：例如 `quark / uc` 会从 URL 或文本里带出 `pwdId / passcode`，`guangya` 会带出 `parentId / did / dt`，`189cloud` 会复用 [tianyi_auth_capture.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/tianyi_auth_capture.py) 解析 `accessToken / signature / date`，并同时保留 `shareCode / accessCode`
  - 授权弹窗现已新增 [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 的 `authCaptureRawInput / authParseCaptureBtn / authApplyCaptureBtn`，并在 [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 中补齐 `parseCapturedAuthText()` 与 `applyParsedCaptureSuggestion()`；解析后可以一键把建议值回填到主授权表单，再继续人工检查后保存
  - 当前回填链会同步切换主表单的 `provider / authMode / token / cookie / extra.*` 字段，并把解析出来的 `appliedFields / stillMissing / placeholderHints` 直接渲染到结果框，明确告诉用户“哪些字段已经带出、哪些还缺、哪些仍像占位符”
  - 这次补齐后，网页登录抓取依然没有夸大成“自动抓 Cookie 成功”，但已经从“给结构化步骤”进一步推进成“可粘贴抓取文本 -> 可解析建议 -> 可一键回填授权表单”的最小闭环，更贴近 `M3` 里的 `web_login_capture` 目标
  - 已新增 [verify_auth_capture_parse.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_capture_parse.py)，并同步补强 [verify_ui_smoke_navigation_modal.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_ui_smoke_navigation_modal.py)，把后端解析接口、前端弹窗控件、解析按钮、回填按钮和匿名访问拦截一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_capture_guide.py` 已验证结构化 capture guide 旧链路未回退，`quark / guangya / aliyundrive_open` 仍会返回各自 provider-aware 引导
  - `.\.venv\Scripts\python.exe scripts\verify_auth_capture_parse.py` 已验证 `quark` 当前可从 `cookie + share url` 解析出 `cookie / pwdId / passcode`，`guangya` 可解析出 `token / parentId / did / dt`，`189cloud` 可从 captured curl/header 文本解析出 `shareCode / accessCode / accessToken / signature / date`
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗当前包含 `authCaptureRawInput / authParseCaptureBtn / authApplyCaptureBtn`，匿名访问 `/api/auth/capture/parse` 会被拦截，登录后前端已绑定 `parseCapturedAuthText()` 与 `applyParsedCaptureSuggestion()`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充网页登录抓取结构化引导`
- 完成范围：
  - 已新增应用侧组装模块 [auth_capture_guide.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_capture_guide.py)，把原来只有 `capture_pending + loginUrlHint + requiredFieldHints` 的网页登录抓取提示，补成 provider-aware 的结构化 capture guide
  - 这次补齐后，[webapp.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/webapp.py) 的 `POST /api/auth/capture/start` 会直接返回 `recommendedAuthModes / preferredCaptureMode / pasteTargets / manualSteps / browserConsoleSnippets / networkCaptureTips`，不再只剩一句“自己去登录再手填”
  - 当前 capture guide 会按 provider 区分 `manual_cookie / manual_token / official_oauth` 侧重点；例如 `quark / uc` 会直接提示 `authCookie + authExtraPwdId`，`guangya` 会提示 `authToken + authExtraParentId`，`aliyundrive_open` 会提示 `authToken + authExtraDomainId + authExtraDriveId`
  - 授权弹窗现已新增 [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 的 `Open Login Page` 按钮，并在 [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 里把 capture guide 的 `loginUrl / authModes / pasteTargets / manualSteps / browserConsoleSnippets / networkCaptureTips` 结构化渲染出来；不只是把 JSON 原样塞进结果框
  - 这次补齐后，网页登录抓取仍然没有夸大成“自动抓取成功”，但已经从“纯文本提醒”推进成“可打开登录页 + 可直接复制控制台脚本 + 可按字段回填”的最小自动化入口，更贴近 `M3` 里的 `web_login_capture` 目标
  - 已新增 [verify_auth_capture_guide.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_capture_guide.py)，并同步补强 [verify_ui_smoke_navigation_modal.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_ui_smoke_navigation_modal.py)，把结构化 guide 字段、provider-specific 提示、授权弹窗按钮和前端渲染入口一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_capture_guide.py` 已验证 `quark` 当前会返回 cookie/share 场景的结构化 capture guide，`guangya` 会走 token capture 提示，`aliyundrive_open` 会显式提示 `domainId/driveId`
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证授权弹窗当前包含 `authOpenLoginUrlBtn`，登录后调用 `/api/auth/capture/start` 会返回 `manualSteps / pasteTargets / browserConsoleSnippets / networkCaptureTips`，且前端已绑定 `openCaptureLoginPage()` 与结构化渲染逻辑
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充补救链按原档案恢复命令`
- 完成范围：
  - [real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 现已把 `runtime_orphan` provider 的 `recommendedRecreateProbeCommand` 提升为优先恢复链路；当存在历史成功样本但当前仓库缺少对应 auth profile 时，会优先给出带原 `profileId` 的恢复命令，而不是只停留在泛化的 bootstrap
  - 这次补齐后，[12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 对 `guangya / pikpak / uc` 三个 `runtimeOrphanOnly` provider 都会直接输出 `--profile-id gy-live-1 / pikpak-live-1 / uc-live-1` 的 `recommendedPrimaryCommand / recommendedRecreateProbeCommand`，并保留 provider-aware 的字段占位符，例如 `YOUR_REAL_PARENT_ID / YOUR_DEVICE_ID / YOUR_SHARE_PWD_ID`
  - 当前补救链现在会更诚实地区分“恢复旧 profileId 以便重新验证”和“post-bootstrap runtime helper”；`guangya / pikpak / uc` 会优先提示先把原 orphan profile 恢复回当前仓库，再去补 auth/list/metadata/create_dir 证据，避免把历史 runtime success 误读成当前仓库已可复验完成
  - 已同步补强 [verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 与 [verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)，把 synthetic bundle、当前仓库 Markdown 和 API 输出里的 orphan-specific `recreate_probe` 命令、`providerSummary`、`runtimeOrphanOnly` 列表一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 synthetic remediation bundle/API/Markdown 当前会对 orphan provider 输出 `--profile-id gy-orphan / uc-orphan` 这类恢复命令，并保持 `recreate_probe` 主命令优先级
  - `.\.venv\Scripts\python.exe scripts\export_real_evidence_remediation.py` 已重导出当前 [12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md)
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出的补救指南仍会输出 `primaryCommand / recreateProbe / conflictPolicy` 等现有汇总与分项字段
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前仓库文档中的 `gy-live-1 / pikpak-live-1 / uc-live-1` orphan 恢复命令与 `build_real_evidence_remediation_bundle()` 保持同步
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充运行样本脱节恢复指南`
- 完成范围：
  - 已新增应用侧聚合模块 [runtime_orphan_recovery.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/runtime_orphan_recovery.py)，把当前 `runtime_orphan` 样本正式汇总成可消费的 `summary / items / markdown` 三种形态，不再只停留在 `Real Evidence` 与 `Remediation` 里的旁注
  - 这次补齐后，[13-RUNTIME_ORPHAN_RECOVERY.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/13-RUNTIME_ORPHAN_RECOVERY.md) 会直接列出当前 `gy-live-1 / pikpak-live-1 / uc-live-1` 三条 orphan profile，对每条样本给出 `provider / latestSavedAt / runtimeModes / verifyModes / existingProviderProfiles / suggestedAuthModes / recommendedCreateCommand`
  - 已补齐按原 `profileId` 重建 stub 的底层能力；这次补齐后，[create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_auth_profile_stub.py) 现已支持 `--profile-id`，配合 [auth_store.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_store.py) 的 `profile_id_override` 保存逻辑，可以显式把历史 runtime success 对应的 `profileId` 恢复回当前仓库，而不是只能新建一个完全无关的新 id
  - 已新增 [webapp.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/webapp.py) 接口 `GET /api/runtime_orphan_recovery` 与 `GET /api/runtime_orphan_recovery_markdown`，登录后可直接在产品内读取 orphan recovery 汇总与 Markdown
  - 设置页现已新增 `Runtime Orphan Recovery` 面板；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会在设置页直接显示 `providerCount / orphanProfileCount / runtimeSampleCount / providersWithSavedProfiles / providersWithoutSavedProfiles`，并附带 `orphanProviders / orphanProfilesList / savedProfileProviders / missingProfileProviders` 以及逐 orphan profile 的 `preferredAuthMode / existingProfiles / recreate` 命令摘要
  - 已新增并补强对应校验脚本：[verify_runtime_orphan_recovery.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_runtime_orphan_recovery.py)、[verify_export_runtime_orphan_recovery.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_runtime_orphan_recovery.py)、[verify_current_runtime_orphan_recovery_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_runtime_orphan_recovery_sync.py)、[verify_runtime_orphan_recovery_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_runtime_orphan_recovery_settings_ui.py)、[verify_create_auth_profile_stub_profile_id.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_auth_profile_stub_profile_id.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_create_auth_profile_stub_profile_id.py` 已验证 `create_auth_profile_stub.py` 当前会把 `--profile-id` 传到 `save_profile(..., profile_id_override=...)`，并保留请求的 `profileId`
  - `.\.venv\Scripts\python.exe scripts\verify_runtime_orphan_recovery.py` 已验证 synthetic orphan recovery payload、Markdown 和 API 当前都会输出 `--profile-id gy-orphan / uc-orphan` 这类恢复命令
  - `.\.venv\Scripts\python.exe scripts\verify_export_runtime_orphan_recovery.py` 已验证导出的 orphan recovery 指南会写出 `orphanSummary` 与 `recommendedCreateCommand`
  - `.\.venv\Scripts\python.exe scripts\verify_runtime_orphan_recovery_settings_ui.py` 已验证设置页当前含 `Runtime Orphan Recovery` 面板，并会加载与展示对应 summary/command 字段
  - `.\.venv\Scripts\python.exe scripts\export_runtime_orphan_recovery.py` 已重导出当前 [13-RUNTIME_ORPHAN_RECOVERY.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/13-RUNTIME_ORPHAN_RECOVERY.md)
  - `.\.venv\Scripts\python.exe scripts\verify_current_runtime_orphan_recovery_sync.py` 已验证当前仓库文档中的 `gy-live-1 / pikpak-live-1 / uc-live-1` 与 `build_runtime_orphan_recovery()` 保持同步
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充计划审计脱节阻塞说明`
- 完成范围：
  - [plan_audit.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/plan_audit.py) 现已把 `M4 / M5 / P-REAL` 的缺口说明继续对齐到当前真实证据状态，不再只笼统写“缺真实成功样本”，而是明确写出 `runtime_orphan` 阻塞：`guangya` 的 `gy-live-1`、以及 `pikpak / uc` 的历史 runtime success 记录虽然存在，但对应 auth profile 当前并不在仓库内，因此不能当作可复验完成证据
  - 这次补齐后，[04-PLAN_AUDIT_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/04-PLAN_AUDIT_REPORT.md) 会在 `M4 / M5 / P-REAL` 三段里直接解释为什么 `strictCompletionPercent` 仍停在 `75.0`：不是“完全没样本”，而是现有 `guangya / uc / pikpak` 样本都落在 `runtime_orphan` 场景，缺少当前仓库可复验的 auth profile
  - 已同步补强 [verify_current_plan_audit_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_plan_audit_sync.py) 与 [verify_export_plan_audit.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_plan_audit.py)，把当前仓库文档与 synthetic 导出里的 `runtime_orphan / auth profile 脱节` 解释一起锁进回归，同时保持 `85.7 / 75.0` 两个百分比口径不变
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_plan_audit.py` 已验证导出的计划审计报告会写出 `runtime_orphan` 与 `auth profile 脱节` 说明
  - `.\.venv\Scripts\python.exe scripts\verify_current_plan_audit_sync.py` 已验证当前仓库 [04-PLAN_AUDIT_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/04-PLAN_AUDIT_REPORT.md) 中的 `M4 / M5 / P-REAL` 阻塞说明与 `run_plan_audit()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\verify_plan_audit_progress.py` 已验证 `featureCompletionPercent=85.7` 与 `strictCompletionPercent=75.0` 口径未被这次说明性补丁改乱
  - `.\.venv\Scripts\python.exe scripts\export_plan_audit.py` 已重导出当前 [04-PLAN_AUDIT_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/04-PLAN_AUDIT_REPORT.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充真实证据运行样本脱节诊断`
- 完成范围：
  - [real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_report.py) 现已补齐 `taskRuntimeOrphanProviderCount / taskRuntimeOrphanProfileCount / taskRuntimeOrphanProviders / taskRuntimeOrphanProfiles` 聚合明细，并在逐 provider 的 `taskRuntimeEvidence` 里继续写出 `orphanProfiles / orphanProfileCount`，不再把“已有 runtime 成功样本但当前仓库里没有对应 auth profile”混成普通成功
  - 这次补齐后，[10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md) 现在会明确写出 `runtime_orphan_providers=3`、`runtime_orphan_profiles=3` 和 `runtime_orphan=guangya, uc, pikpak`，并在 `guangya / uc / pikpak` 三个 provider 下直接标出 `orphan=gy-live-1 / uc-live-1 / pikpak-live-1`，同时把“已有 runtime 样本，但对应 auth profile 未保存在当前仓库”列为真实 gap
  - [real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 现已继续区分 `runtimeOrphanOnly / runtimeOrphanProfiles` 与 `providersRuntimeOrphanOnly / providersRuntimeOrphanOnlyList`，让补救逻辑不再误导成“直接补 runtime”即可，而是先明确提示“重建或导入对应 auth profile，再重跑 validation / live probe”
  - 这次补齐后，[12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 现在会明确写出 `providersRuntimeOrphanOnly=3` 与 `runtimeOrphanOnly=guangya, pikpak, uc`，逐 provider 也会继续显示 `runtimeOrphanProfiles`
  - 设置页聚合现已同步吸收上述脱节诊断字段；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会在 `Real Evidence` 面板显示 `runtime_orphan_providers / runtime_orphan_profiles / runtimeOrphanProvidersList / runtimeOrphanProfilesList`，在 `Real Evidence Remediation` 面板显示 `runtimeOrphanOnlyProviders`，并在逐行补救摘要里带出 `runtimeOrphanOnly / runtimeOrphanProfiles`
  - 已同步补强 [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py)、[verify_export_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_report.py)、[verify_real_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_settings_ui.py)、[verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)，把 synthetic payload、导出链、设置页摘要与脱节诊断字段一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_report.py` 已验证 synthetic payload 与 `/api/real_evidence_markdown` 当前会输出 orphan 相关 summary/provider/item 字段，并把缺失 auth profile 场景记为明确 gap
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_report.py` 已验证导出的真实证据状态报告会写出 `runtime_orphan_providers / runtime_orphan_profiles / runtime_orphan`
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_settings_ui.py` 已验证设置页 `Real Evidence` 摘要当前会读取并展示 orphan 相关字段
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页 `Real Evidence Remediation` 摘要与逐 provider 行当前会读取并展示 `runtimeOrphanOnly / runtimeOrphanProfiles`
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_status_sync.py` 已验证当前仓库 [10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md) 中的 orphan 汇总与 `build_real_evidence_report()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py`、`.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py`、`.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证 remediation bundle、导出 markdown 和当前仓库 [12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 中的 `runtimeOrphanOnly` 诊断与补救建议保持同步
  - `.\.venv\Scripts\python.exe scripts\export_real_evidence_report.py`、`.\.venv\Scripts\python.exe scripts\export_real_evidence_remediation.py` 已重导出当前真实证据状态/补救文档
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充本地适配器验证设置页聚合`
- 完成范围：
  - 已新增应用侧聚合模块 [local_live_adapter_verification.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/local_live_adapter_verification.py)，把原本只存在于导出脚本的 `Local Live Adapter Verification` 能力正式抽到 `src` 层，统一提供 `summary / items / markdown` 三种消费形态
  - [webapp.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/webapp.py) 现已新增 `GET /api/local_live_adapter_verification` 与 `GET /api/local_live_adapter_verification_markdown`，登录后可直接从产品内读取本地 stub 验证快照，而不必只靠单独跑导出脚本
  - 设置页现已新增 `Local Live Adapter Verification` 摘要面板；这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会在设置页直接显示 `allOkProviders / md5ReadyProviders / gcidReadyProviders / probeReadyProviders / matrixReadyProviders / accountCreateModeProviders`，并附带逐 provider 的 `list / metadata / create / createMode / probeChecks / matrix` 快照
  - 已新增 [verify_local_live_adapter_verification_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_local_live_adapter_verification_api.py) 与 [verify_local_live_adapter_verification_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_local_live_adapter_verification_settings_ui.py)，把 API、Markdown、设置页 DOM、状态、loader、刷新链路和摘要字段一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_local_live_adapter_verification_api.py` 已验证应用侧 payload 会输出 `summary / items`，API markdown 也会继续保留 `providerSummary` 与 `189cloud create_mode`
  - `.\.venv\Scripts\python.exe scripts\verify_local_live_adapter_verification_settings_ui.py` 已验证设置页当前含 `Local Live Adapter Verification` 面板，并会在刷新后加载与展示对应 summary 字段
  - `.\.venv\Scripts\python.exe scripts\verify_export_local_live_adapter_verification.py` 已验证原有导出链改走应用侧模块后仍保持兼容，导出的 `07-LOCAL_LIVE_ADAPTER_VERIFICATION.md` 结构未回退
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充授权设置页聚合明细`
- 完成范围：
  - 设置页现已新增 `Auth Evidence Bundle` 与 `Auth Remediation Guide` 两个摘要面板，不必先切到授权页再点按钮，登录后即可直接看到当前 auth profile 的 ready/fix 分布
  - 这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会在设置页直接显示 `profileReadyProfiles / writeReadyProfiles / validationOkProfiles / probeOkProfiles` 以及 `readyProfiles / needsFixProfiles / writeNeedsFixProfiles / needsSecretRefreshProfiles`
  - 已新增 [verify_auth_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_settings_ui.py)，把设置页 DOM、状态、loader、刷新链路和 auth bundle/remediation 摘要展示一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_settings_ui.py` 已验证设置页当前含 auth evidence/remediation 面板，并会在刷新后加载与展示对应 summary 字段
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充授权摘要页面聚合明细`
- 完成范围：
  - [auth_profile_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_evidence.py) 现已让 `refresh_auth_evidence_bundle()` 也返回完整 `profileSummary` 名单，不再只剩 count，避免刷新授权证据后页面摘要丢失 profile 级分布
  - 这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 的 `Auth Evidence Bundle` 与 `Auth Remediation Guide` 页面摘要会直接显示 `profileReadyProfiles / writeReadyProfiles / validationOkProfiles / probeOkProfiles` 以及 `readyProfiles / needsFixProfiles / needsSecretRefreshProfiles`
  - 已新增 [verify_auth_bundle_summary_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_bundle_summary_ui.py)，把刷新接口保留 profileSummary 名单和前端摘要展示一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_bundle_summary_ui.py` 已验证 `refresh_auth_evidence_bundle()` 当前会保留 profile 级 summary list，且前端摘要会展示这些字段
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充探针报告聚合明细`
- 完成范围：
  - [live_probe.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/live_probe.py) 现已把 `Provider Live Probe Report` 顶部汇总继续补齐为 provider 级分布，不再只保留 `profileProbeProfiles`
  - 这次补齐后，[05-PROVIDER_LIVE_PROBE_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/05-PROVIDER_LIVE_PROBE_REPORT.md) 现在会额外写出 `profileProbeProviderSummary`，直接汇总当前哪些 provider 的 live probe 成功、哪些失败，以及失败主要落在哪些 mode；设置页 `Provider Live Probe` 摘要也会同步显示 `okProviders / failedProviders / failedModes`
  - 已同步补强 [verify_export_live_probe_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_live_probe_report.py)、[verify_current_live_probe_report_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_live_probe_report_sync.py)、[verify_live_probe_provider_summary_alignment.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_live_probe_provider_summary_alignment.py)、[verify_auth_probe_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_probe_settings_ui.py)，把导出 markdown、当前仓库文档、provider 级 summary 对齐和设置页摘要一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_live_probe_report.py` 已验证导出的 probe 报告会写出 `profileProbeProviderSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_live_probe_report_sync.py` 已验证当前仓库文档中的 `profileProbeProviderSummary` 与 `run_live_probe()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\verify_live_probe_provider_summary_alignment.py` 已验证 provider 级 summary 不会被重复 profile 污染
  - `.\.venv\Scripts\python.exe scripts\verify_auth_probe_settings_ui.py` 已验证设置页摘要当前会读取并展示新的 probe provider/mode 字段
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充联调摘要设置页聚合明细`
- 完成范围：
  - 设置页 `Auth Live Validation` 与 `Provider Live Probe` 摘要面板现已继续吸收各自 summary 里的 profile 名单，不再只显示 `latestOk / latestFailed` 这类计数
  - 这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 现在会在设置页摘要中直接显示 auth/probe 的 `okProfiles / failedProfiles` 与对应 provider 分布，因此当前 UI 已能直接看到授权联调失败主要落在哪些 profile，而不必再切回单独报告文档
  - 已新增并补强对应设置页校验脚本，把这些 auth/probe 摘要字段一起锁进回归
- 当前验证证据：
  - 当前设置页摘要代码已读取并展示 auth/probe profile 级 summary 字段
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充运行样本设置页聚合明细`
- 完成范围：
  - 设置页 `Task Runtime Evidence` 摘要面板现已继续吸收 [task_runtime_evidence_store.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/task_runtime_evidence_store.py) 已有的 `profileSummary` 聚合，不再只显示 `success / failed / candidate / probe / blocked / conflictHandled` 的 count
  - 这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 现在会在设置页摘要中直接显示 `successProfiles / failedProfiles / candidateProfiles / probeProfiles / blockedProfiles / conflictHandledProfiles`，因此当前 UI 已能直接看见 `gy-live-1 / pikpak-live-1 / uc-live-1` 这些已保存运行样本档案
  - 已同步补强 [verify_task_runtime_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_settings_ui.py)，把这些新的设置页摘要字段一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_task_runtime_evidence_settings_ui.py` 已验证设置页摘要当前会读取并展示新的 task runtime profile 级 summary 字段
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充补救设置页聚合明细`
- 完成范围：
  - 设置页 `Real Evidence Remediation` 摘要面板现已继续吸收 [real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 的 provider 级 summary list，不再只显示 count
  - 这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 现在会在设置页摘要中直接显示 `noProfilesProviders / needAuthProviders / needRuntimeProviders / recreateProbeProviders / primaryCommandProviders / overwriteVariantProviders / blockedOnlyProviders / candidateOnlyProviders / probeOnlyProviders`，因此当前 UI 已能直接看见 `needRuntimeProviders`、`recreateProbeProviders` 等真正需要补救的 provider 名单
  - 已同步补强 [verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)，把这些新的设置页摘要字段一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页摘要当前会读取并展示新的 remediation provider 级 summary 字段
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充真实证据设置页聚合明细`
- 完成范围：
  - 设置页 `Real Evidence` 摘要面板现已继续吸收 [real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_report.py) 新增的 provider 级 summary，不再只显示各类 count
  - 这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 现在会在设置页摘要中直接显示 `authProviders / listProviders / metadataProviders / createDirProviders / fullyVerifiedProviders / runtimeSuccessProviders / runtimeFailedProvidersList / runtimeCandidateProvidersList / runtimeProbeProvidersList / runtimeBlockedProvidersList`，因此当前 UI 已能直接看到 `runtimeSuccessProviders=guangya/uc/pikpak`，以及其余 runtime 分组当前仍是 `(none)`
  - 已同步补强 [verify_real_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_settings_ui.py)，把这些新的设置页摘要字段一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_settings_ui.py` 已验证设置页摘要当前会读取并展示新的 real evidence provider 级 summary 字段
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充状态矩阵设置页聚合明细`
- 完成范围：
  - 设置页 `Provider Status Matrix` 摘要面板现已继续吸收 [provider_status_matrix.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/provider_status_matrix.py) 新增的 provider 级 summary，不再只显示 count
  - 这次补齐后，[app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 现在会在设置页摘要中直接显示 `authReadyProviders / createDirProviders / fastCheckProviders / liveProbeOkProviders / overwriteDowngradeProviders / overwriteSupportedProviders / autoRenameSupportedProviders / autoRenameProbeOnlyProviders / conflictUnsupportedProviders / runtimeSuccessProviders / runtimeFailedProvidersList / runtimeCandidateProvidersList / runtimeProbeProvidersList / runtimeBlockedProvidersList / runtimeConflictHandledProvidersList`，因此当前 UI 已能直接看到 `overwriteSupportedProviders=aliyundrive_open`、`conflictUnsupportedProviders=189cloud`、`runtimeSuccessProviders=guangya/uc/pikpak`
  - 已同步补强 [verify_provider_status_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_status_settings_ui.py)，把这些新的设置页摘要字段一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_provider_status_settings_ui.py` 已验证设置页摘要当前会读取并展示新的 provider 级 summary 字段
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充状态矩阵聚合明细`
- 完成范围：
  - [provider_status_matrix.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/provider_status_matrix.py) 的 summary 现已继续补齐 `authReadyProviders / createDirReadyProviders / fastCheckProviders / liveProbeOkProviders / overwriteDowngradeProviders / overwriteSupportedProviders / autoRenameSupportedProviders / autoRenameProbeOnlyProviders / conflictUnsupportedProviders / taskRuntimeSuccessProviders / taskRuntimeFailedProviders / taskRuntimeCandidateProviders / taskRuntimeProbeProviders / taskRuntimeBlockedProviders / taskRuntimeConflictHandledProviders` 聚合明细，不再只返回一组组计数
  - 这次补齐后，[06-PROVIDER_STATUS_MATRIX.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/06-PROVIDER_STATUS_MATRIX.md) 现在会在顶部额外写出 `providerSummary` 行，直接汇总当前哪些 provider 已具备 `create_dir / fast_check`、哪些是 `overwrite_downgrade / overwrite_supported / auto_rename_probe_only / conflict_unsupported`，以及哪些 provider 当前已有 `runtime_success / runtime_failed / runtime_candidate / runtime_probe / runtime_blocked / runtime_conflict_handled`；当前真实仓库会明确显示 `overwrite_supported=aliyundrive_open`、`auto_rename_probe_only=115_open`、`conflict_unsupported=189cloud`、`runtime_success=guangya, uc, pikpak`
  - 已同步补强 [verify_export_provider_status_matrix.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_provider_status_matrix.py) 与 [verify_current_provider_status_matrix_runtime_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_provider_status_matrix_runtime_sync.py)，把 synthetic export 与当前仓库文档里的 `providerSummary` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_provider_status_matrix.py` 已验证导出的状态矩阵会写出 `providerSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_provider_status_matrix_runtime_sync.py` 已验证当前仓库文档中的 `providerSummary` 与 `build_status_matrix()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\export_provider_status_matrix.py` 已重导出当前 [06-PROVIDER_STATUS_MATRIX.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/06-PROVIDER_STATUS_MATRIX.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充授权联调报告聚合明细`
- 完成范围：
  - [auth_live_validate.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_live_validate.py) 的 summary 现已继续补齐 `okProviderKeys / failedProviderKeys / failedModes` 聚合明细，不再只返回 `okProfiles / failedProfiles / providerKeys` 这几组字段
  - 这次补齐后，[03-AUTH_LIVE_VALIDATION_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/03-AUTH_LIVE_VALIDATION_REPORT.md) 现在会在顶部额外写出 `profileSummary` 行，直接汇总最新 auth live validation 中哪些 provider 当前通过、哪些 provider 当前失败，以及失败主要落在哪些 mode；当前真实仓库会明确显示 `ok_providers=(none)`、`failed_providers=aliyundrive_open, guangya`、`failed_modes=live_error, profile_incomplete`
  - 已同步补强 [export_auth_live_validation_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_auth_live_validation_report.py)、[verify_export_auth_live_validation_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_live_validation_report.py)、[verify_current_auth_live_validation_report_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_live_validation_report_sync.py)、[verify_auth_live_validation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_live_validation.py)，把导出 markdown、当前仓库文档和 API summary 里的 `okProviderKeys / failedProviderKeys / failedModes` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_live_validation.py` 已验证 API summary 当前会返回 `okProviderKeys / failedProviderKeys / failedModes`
  - `.\.venv\Scripts\python.exe scripts\verify_export_auth_live_validation_report.py` 已验证导出的 auth live validation 报告会写出 `profileSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_auth_live_validation_report_sync.py` 已验证当前仓库文档中的 `profileSummary` 与 `live_validation_summary()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\export_auth_live_validation_report.py` 已重导出当前 [03-AUTH_LIVE_VALIDATION_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/03-AUTH_LIVE_VALIDATION_REPORT.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充真实证据状态聚合明细`
- 完成范围：
  - [real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_report.py) 的 summary 现已继续补齐 `authEvidenceProviders / listEvidenceProviders / metadataEvidenceProviders / createDirEvidenceProviders / fullyVerifiedProviders / taskRuntimeEvidenceProviders / taskRuntimeFailedProviders / taskRuntimeCandidateProviders / taskRuntimeProbeProviders / taskRuntimeBlockedProviders` 聚合明细，不再只返回各类 provider count
  - 这次补齐后，[10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md) 现在会在顶部额外写出 `providerSummary` 行，直接汇总当前哪些 provider 已有 auth/list/metadata/create_dir 真实证据、哪些已 fully verified，以及哪些 provider 当前已有 runtime success / failed / candidate / probe / blocked 样本；当前真实仓库会明确显示 `runtime_success=guangya, uc, pikpak`，其余 `auth / list / metadata / create_dir / runtime_failed / runtime_candidate / runtime_probe / runtime_blocked` 当前都还是 `(none)`
  - 已同步补强 [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py)、[verify_export_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_report.py)、[verify_current_real_evidence_status_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_status_sync.py)，把 synthetic API/Markdown、导出 markdown 和当前仓库文档里的 `providerSummary` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_report.py` 已验证 synthetic payload 与 `/api/real_evidence_markdown` 当前会输出 `providerSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_report.py` 已验证导出的真实证据状态报告会写出 `providerSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_status_sync.py` 已验证当前仓库文档中的 `providerSummary` 与 `build_real_evidence_report()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\export_real_evidence_report.py` 已重导出当前 [10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`补充本地适配器验证聚合明细`
- 完成范围：
  - [export_local_live_adapter_verification.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_local_live_adapter_verification.py) 的导出汇总现已继续补齐 `providerCount / allOkProviders / md5ReadyProviders / gcidReadyProviders / probeCheckReadyProviders / matrixReadyProviders / accountCreateModeProviders`，不再只输出逐 provider 明细
  - 这次补齐后，[07-LOCAL_LIVE_ADAPTER_VERIFICATION.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/07-LOCAL_LIVE_ADAPTER_VERIFICATION.md) 现在会在顶部额外写出 `providerCount` 与 `providerSummary` 行，直接汇总本地 stub 验证里哪些 provider 当前 `all_ok`、哪些已具备 `md5/gcid` 元数据、哪些 probe/matrix 已全绿，以及哪些 provider 当前存在显式 `account_create_mode`；当前真实仓库会明确显示 `providerCount=10`、`all_ok=guangya, aliyundrive_open, 189cloud, baidu_netdisk, 123_open, 115_open, xunlei, pikpak, quark, uc`、`md5_ready=guangya, aliyundrive_open, 189cloud, baidu_netdisk, 123_open, quark, uc`、`gcid_ready=guangya, xunlei, pikpak`、`account_create_mode=189cloud=live_account_auth`
  - 已同步补强 [verify_export_local_live_adapter_verification.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_local_live_adapter_verification.py) 与 [verify_current_local_live_adapter_verification_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_local_live_adapter_verification_sync.py)，把 synthetic export 与当前仓库文档里的 `providerSummary` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_local_live_adapter_verification.py` 已验证导出的本地适配器验证报告会写出 `providerSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_local_live_adapter_verification_sync.py` 已验证当前仓库文档中的 `providerCount / providerSummary` 与 `build_payload()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\export_local_live_adapter_verification.py` 已重导出当前 [07-LOCAL_LIVE_ADAPTER_VERIFICATION.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/07-LOCAL_LIVE_ADAPTER_VERIFICATION.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [plan_audit.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/plan_audit.py) 的审计 summary 现已继续补齐 `doneKeys / partialKeys / todoKeys` 聚合明细，不再只返回 `done / partial / todo` 三个计数
  - 这次补齐后，[04-PLAN_AUDIT_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/04-PLAN_AUDIT_REPORT.md) 现在会在顶部额外写出 `milestoneSummary` 行，直接汇总当前哪些里程碑已经 `done`、哪些还停在 `partial`、哪些仍是 `todo`；当前真实仓库会明确显示 `done=M1, M2, M3, M6, M7`、`partial=M4, M5`、`todo=P-REAL`
  - 已同步补强 [verify_export_plan_audit.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_plan_audit.py)、[verify_current_plan_audit_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_plan_audit_sync.py)、[verify_plan_audit_progress.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_plan_audit_progress.py)，把 synthetic export、当前仓库文档和纯渲染 markdown 里的 `milestoneSummary` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_plan_audit.py` 已验证导出的计划审计报告会写出 `milestoneSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_plan_audit_sync.py` 已验证当前仓库文档中的 `milestoneSummary` 与 `run_plan_audit()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\verify_plan_audit_progress.py` 已验证纯渲染 markdown 当前也会输出 `milestoneSummary`，且进度百分比说明保持不变
  - `.\.venv\Scripts\python.exe scripts\export_plan_audit.py` 已重导出当前 [04-PLAN_AUDIT_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/04-PLAN_AUDIT_REPORT.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 的补救 summary 现已继续补齐 `providersWithNoProfilesList / providersNeedingAuthEvidenceList / providersNeedingRuntimeSuccessList / providersWithRecreateProbeCommandList / providersWithPrimaryCommandList / providersWithOverwriteVariantCommandList / providersBlockedOnlyList / providersCandidateOnlyList / providersProbeOnlyList` 聚合明细，不再只剩一组 count
  - 这次补齐后，[12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 现在会在顶部额外写出 `providerSummary` 行，直接汇总哪些 provider 还没档案、哪些仍缺 auth、哪些还缺 runtime success、哪些当前走 `recreate_probe`、哪些已有主命令/覆盖变体，以及当前是否存在 `blocked-only / candidate-only / probe-only` provider；当前真实仓库会明确显示 `noProfiles=115_open, 123_open, 189cloud, baidu_netdisk, pikpak, quark, uc, xunlei`、`needRuntime=115_open, 123_open, 189cloud, aliyundrive_open, baidu_netdisk, quark, xunlei`、`recreateProbe=aliyundrive_open, guangya`
  - 已同步补强 [verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)、[verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)、[verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)，把 synthetic bundle、导出 markdown 和当前仓库文档里的 `providerSummary` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 synthetic bundle/API/Markdown 当前会输出 `providerSummary`，并区分 `noProfiles / needAuth / needRuntime / recreateProbe / primaryCommand / overwriteVariant / blockedOnly / candidateOnly / probeOnly`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出的真实联调补救指南会写出 `providerSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前仓库文档中的 `providerSummary` 与 `build_real_evidence_remediation_bundle()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\export_real_evidence_remediation.py` 已重导出当前 [12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [auth_profile_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_remediation.py) 的补救 bundle 汇总现已继续补齐 `readyProfiles / needsFixProfiles / writeReadyProfiles / writeNeedsFixProfiles / needsSecretRefreshProfiles` 聚合明细，不再只返回几组 count
  - 这次补齐后，[09-AUTH_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/09-AUTH_REMEDIATION_GUIDE.md) 现在会在顶部额外写出 `profileSummary` 行，直接汇总哪些 profile 已 ready、哪些仍需补救、哪些已具备写盘条件、哪些仍含占位 secret；当前真实仓库会明确显示 `ready=(none)`、`needsFix=aliyun-bootstrap, risk-smoke-guangya, smoke-guangya`、`writeReady=aliyun-bootstrap, risk-smoke-guangya, smoke-guangya`、`needsSecretRefresh=aliyun-bootstrap, risk-smoke-guangya, smoke-guangya`
  - 已同步补强 [verify_auth_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_remediation_bundle.py)、[verify_export_auth_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_remediation_bundle.py)、[verify_current_auth_remediation_bundle_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_remediation_bundle_sync.py)，把 synthetic bundle、导出 markdown 和当前仓库文档里的 `profileSummary` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_remediation_bundle.py` 已验证 synthetic bundle/API/Markdown 当前会输出 `profileSummary`，并区分 `ready / needsFix / writeReady / writeNeedsFix / needsSecretRefresh`
  - `.\.venv\Scripts\python.exe scripts\verify_export_auth_remediation_bundle.py` 已验证导出的授权补救指南会写出 `profileSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_auth_remediation_bundle_sync.py` 已验证当前仓库文档中的 `profileSummary` 与 `build_auth_remediation_bundle()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\export_auth_remediation_bundle.py` 已重导出当前 [09-AUTH_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/09-AUTH_REMEDIATION_GUIDE.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [auth_profile_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_evidence.py) 的证据 bundle 汇总现已继续补齐 `profileReadyProfiles / writeReadyProfiles / validationOkProfiles / probeOkProfiles` 聚合明细，不再只返回 `profileReadyCount / writeReadyCount / validationOkCount / probeOkCount`
  - 这次补齐后，[08-AUTH_EVIDENCE_BUNDLE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/08-AUTH_EVIDENCE_BUNDLE.md) 现在会在顶部额外写出 `profileSummary` 行，直接汇总当前哪些 profile 已准备好、哪些 profile 已具备写盘条件、哪些 profile 已通过校验或探测；当前真实仓库会明确显示 `profileReady=(none)`、`writeReady=aliyun-bootstrap, risk-smoke-guangya, smoke-guangya`、`validationOk=(none)`、`probeOk=(none)`
  - 已同步补强 [verify_auth_evidence_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_evidence_bundle.py)、[verify_export_auth_evidence_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_evidence_bundle.py)、[verify_current_auth_evidence_bundle_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_evidence_bundle_sync.py)，把 API bundle、导出 markdown 和当前仓库文档中的 `profileSummary` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_evidence_bundle.py` 已验证 synthetic API/bundle 当前会输出 `profileSummary`，并区分 `profileReady / writeReady / validationOk / probeOk`
  - `.\.venv\Scripts\python.exe scripts\verify_export_auth_evidence_bundle.py` 已验证导出的授权证据档案会写出 `profileSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_auth_evidence_bundle_sync.py` 已验证当前仓库文档中的 `profileSummary` 与 `build_auth_evidence_bundle()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\export_auth_evidence_bundle.py` 已重导出当前 [08-AUTH_EVIDENCE_BUNDLE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/08-AUTH_EVIDENCE_BUNDLE.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [provider_live_probe_store.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/provider_live_probe_store.py) 的 summary 现已继续补齐 `okProfiles / failedProfiles`，不再只返回 `profileCount / okCount / failedCount / providerKeys`
  - [live_probe.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/live_probe.py) 生成的 [05-PROVIDER_LIVE_PROBE_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/05-PROVIDER_LIVE_PROBE_REPORT.md) 现在会额外写出 `profileProbeProfiles` 聚合行，直接汇总当前 `profile_probe` 成功/失败对应的 profile；当前真实仓库已明确显示 `ok=(none)` 与 `failed=22173a49-2206-4da8-8624-9bab7bbbe64b, gy-patch-probe-1`
  - 已同步补强 [verify_export_live_probe_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_live_probe_report.py)、[verify_live_probe_provider_summary_alignment.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_live_probe_provider_summary_alignment.py)、新增 [verify_current_live_probe_report_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_live_probe_report_sync.py)，并把 [verify_live_result_list_apis.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_live_result_list_apis.py)、[verify_auth_live_validation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_live_validation.py) 的 probe summary 断言一起补到 `okProfiles / failedProfiles`
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_live_probe_report.py` 已验证导出的 live probe 报告会写出 `profileProbeProfiles`
  - `.\.venv\Scripts\python.exe scripts\verify_live_probe_provider_summary_alignment.py` 已验证 provider 级 profile_probe 汇总继续按最终导出分段口径聚合，并写出对应 failed profile
  - `.\.venv\Scripts\python.exe scripts\verify_current_live_probe_report_sync.py` 已验证当前仓库文档中的 `profileProbeProfiles` 与 `run_live_probe()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\verify_live_result_list_apis.py`、`.\.venv\Scripts\python.exe scripts\verify_auth_live_validation.py` 已验证 `/api/providers/live_probe_results` 的 summary 现也会返回 `okProfiles / failedProfiles`
  - `.\.venv\Scripts\python.exe scripts\export_live_probe_report.py` 已重导出当前 [05-PROVIDER_LIVE_PROBE_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/05-PROVIDER_LIVE_PROBE_REPORT.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [auth_live_validate.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_live_validate.py) 的 summary 现已继续补齐 `okProfiles / failedProfiles` 聚合明细，不再只返回 `okCount / failedCount / providerKeys`
  - [export_auth_live_validation_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_auth_live_validation_report.py) 导出的 [03-AUTH_LIVE_VALIDATION_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/03-AUTH_LIVE_VALIDATION_REPORT.md) 现在会显式写出 `latestProfiles` 行，直接汇总最新 auth live validation 中哪些 profile 通过、哪些 profile 失败；当前真实仓库会明确显示 `ok=(none)` 与 `failed=aliyun-bootstrap, risk-smoke-guangya, smoke-guangya`
  - 已同步补强 [verify_current_auth_live_validation_report_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_live_validation_report_sync.py)、[verify_export_auth_live_validation_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_live_validation_report.py)、[verify_auth_live_validation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_live_validation.py)，把当前文档、导出链和 API summary 的 `okProfiles / failedProfiles` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_current_auth_live_validation_report_sync.py` 已验证当前仓库文档中的 `latestProfiles` 与 `live_validation_summary()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\verify_export_auth_live_validation_report.py` 已验证导出的 auth live validation 报告会写出 `latestProfiles`
  - `.\.venv\Scripts\python.exe scripts\verify_auth_live_validation.py` 已验证 API summary 现也会返回 `okProfiles / failedProfiles`
  - `.\.venv\Scripts\python.exe scripts\export_auth_live_validation_report.py` 已重导出当前 [03-AUTH_LIVE_VALIDATION_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/03-AUTH_LIVE_VALIDATION_REPORT.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [task_runtime_evidence_store.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/task_runtime_evidence_store.py) 的 Markdown 渲染现已继续补齐 `profileSummary` 聚合明细，不再只靠逐条样本长行去人工辨认当前有哪些 `success / failed / candidate / probe / blocked / conflictHandled` profile
  - 这次补齐后，[docs/11-TASK_RUNTIME_EVIDENCE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/11-TASK_RUNTIME_EVIDENCE.md) 现在除了继续保留逐条 runtime 样本行，还会在顶部直接汇总 `success / failed / candidate / probe / blocked / conflictHandled` 对应的 profile；当前真实仓库会明确写出 `success=gy-live-1, pikpak-live-1, uc-live-1` 与 `conflictHandled=gy-live-1, pikpak-live-1, uc-live-1`
  - 已同步补强 [verify_task_runtime_evidence_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_api.py)、[verify_export_task_runtime_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_task_runtime_evidence_report.py)、[verify_current_task_runtime_evidence_report_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_task_runtime_evidence_report_sync.py)，把 API markdown、导出 markdown 和当前仓库文档里的 `profileSummary` 一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_task_runtime_evidence_api.py` 已验证 synthetic API/Markdown 当前会输出 `profileSummary`，并区分 `success / failed / candidate / probe / blocked / conflictHandled`
  - `.\.venv\Scripts\python.exe scripts\verify_export_task_runtime_evidence_report.py` 已验证导出的任务运行样本报告会写出 `profileSummary`
  - `.\.venv\Scripts\python.exe scripts\verify_current_task_runtime_evidence_report_sync.py` 已验证当前仓库文档里的 `profileSummary` 与 `build_task_runtime_evidence_payload()` 保持同步
  - `.\.venv\Scripts\python.exe scripts\export_task_runtime_evidence_report.py` 已重导出当前 [docs/11-TASK_RUNTIME_EVIDENCE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/11-TASK_RUNTIME_EVIDENCE.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [provider_status_matrix.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/provider_status_matrix.py) 的导出矩阵现已继续补齐 `runtime_profiles` 明细，不再只展示 `task_runtime_samples / success / failed / candidate / probe / blocked / conflict_handled` 这些数字；当前会把每个 provider 的 runtime 成功/失败/candidate/probe 样本对应到具体 profile 名
  - 这次补齐后，[docs/06-PROVIDER_STATUS_MATRIX.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/06-PROVIDER_STATUS_MATRIX.md) 现在除了继续量化 `guangya / uc / pikpak` 当前各有 `1` 条 runtime success 外，还能直接看出这些样本当前对应 `gy-live-1 / uc-live-1 / pikpak-live-1`；对 `115_open / 189cloud / aliyundrive_open / quark / baidu_netdisk / 123_open / xunlei` 这些仍无真实 runtime success 的 provider，也会明确保持 `success=(none) failed=(none) candidate=(none) probe=(none)`，避免矩阵只剩计数口径
  - 已同步补强 [verify_export_provider_status_matrix.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_provider_status_matrix.py) 与 [verify_current_provider_status_matrix_runtime_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_provider_status_matrix_runtime_sync.py)，把 synthetic export 与当前仓库导出的 `runtime_profiles` 明细一起锁进回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_provider_status_matrix.py` 已验证导出的矩阵 Markdown 当前会包含 `runtime_profiles` 行，并区分 `success / failed / candidate / probe` 对应的 profile
  - `.\.venv\Scripts\python.exe scripts\verify_current_provider_status_matrix_runtime_sync.py` 已验证当前仓库矩阵中的 `guangya / uc / pikpak` runtime success profile 与 `build_status_matrix()` 同步，且无 runtime success 的 provider 继续保持空 profile 口径
  - `.\.venv\Scripts\python.exe scripts\export_provider_status_matrix.py` 已重导出当前 [docs/06-PROVIDER_STATUS_MATRIX.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/06-PROVIDER_STATUS_MATRIX.md)
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_report.py) 的 markdown 渲染已继续补齐 `taskRuntimeProfiles` 明细，不再只展示 `samples / success / failed / candidate / probe / blocked / conflictHandled` 这类计数，当前会把同一 provider 的 `success / failed / candidate / probe` 样本档案名一起显式写进真实证据报告
  - 这次补齐后，[docs/10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md) 现在不仅能继续诚实展示 `guangya / uc / pikpak` 已有 runtime 成功样本，也能直接看出它们当前各自落到的是哪些已保存 profile；对 `115_open / 189cloud / xunlei / aliyundrive_open / quark / baidu_netdisk / 123_open` 这些仍无 runtime 成功样本的 provider，也会明确保持 `success=(none) failed=(none) candidate=(none) probe=(none)`，避免只剩数字、看不出具体档案分布
  - 已同步补强 [scripts/verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py)、[scripts/verify_export_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_report.py)、[scripts/verify_current_real_evidence_status_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_status_sync.py)，把 API markdown、导出 markdown 和当前仓库文档里的 `taskRuntimeProfiles` 明细一起锁进回归，防止 `P-REAL` 追踪再次退回“只有汇总数字、没有样本名单”
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_report.py` 已验证 synthetic payload 与 `/api/real_evidence_markdown` 当前都会输出 `taskRuntimeProfiles`，并区分 `success / failed / candidate / probe` 样本档案
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_report.py` 已验证导出脚本生成的 `docs/10-REAL_EVIDENCE_STATUS.md` 当前会保留 runtime 样本档案明细
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_status_sync.py` 已验证当前仓库文档里的 runtime 样本分布与 `build_real_evidence_report()` 保持同步
  - 本轮启动的项目 `.venv` `python` verifier / 导出进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_current_real_evidence_status_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_status_sync.py) 已继续补强，不再只校验 [docs/10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md) 的 `task_runtime / runtime_samples / runtime_success / runtime_conflict_handled` 汇总口径
  - 这条 current-sync verifier 现在还会继续锁住 `task_runtime_failed / task_runtime_candidate / task_runtime_probe / runtime_failed / runtime_candidate / runtime_probe / runtime_blocked_providers / runtime_blocked` 这些更容易漂移的真实证据字段，防止 `P-REAL` 状态摘要只更新一半
  - 同一条回归当前还会逐 provider 核对 `guangya / uc / pikpak` 仍保持 `samples=1 success=1` 的 runtime 成功样本口径，以及 `115_open / 189cloud / xunlei / aliyundrive_open / quark / baidu_netdisk / 123_open` 这些 provider 仍然诚实保持 `samples=0 success=0 ...` 和“当前尚未记录到任务运行阶段真实成功样本”的未完成提示
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_status_sync.py` 已验证 `docs/10-REAL_EVIDENCE_STATUS.md` 当前不仅 summary 统计与 `build_real_evidence_report()` 一致，provider 级 runtime 成功/未成功分布与 TODO 提示文案也保持同步
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 里的待处理区现已从普通标题 + 列表改成真实 `details/summary` 折叠结构，新增 `pendingDetails / pendingSummary / pendingFoldHint / pendingSummaryMeta / pending-fold-body`，终于把计划文档 UI smoke 里的 `待处理折叠` 真正落成页面能力
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 现会继续绑定 `panel.pending.fold_hint` 文案，并在 `renderPendingList()` 里根据当前 `state.tasks` 实时刷新 `tasks=... , pending=...` 摘要；没有待处理项时会自动折起，有待处理项时自动展开
  - [app.css](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.css) 也已补上 `pending-fold` 样式与 `展开 / 收起` 状态文案；[i18n.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/i18n.py) 同步新增 `panel.pending.fold_hint` 的中英文文案
  - 已新增 [scripts/verify_pending_fold_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_pending_fold_ui.py)，把待处理折叠的 HTML 结构、JS 文案绑定、摘要计数、折叠开关和 CSS 样式一起锁进静态回归
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_pending_fold_ui.py` 已验证待处理区当前确实包含 `details/summary` 折叠结构、折叠提示文案、`tasks/pending` 摘要更新逻辑，以及 `展开 / 收起` 样式状态
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_error_risk_classification.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_error_risk_classification.py)，把计划文档单元测试里的 `错误码分类` 独立收成一条纯分类回归，不再只靠实现代码和光鸭里程碑描述间接证明
  - 这条 verifier 当前会直接锁住 [guangya_live.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/guangya_live.py) 的 live 请求分类口径：`401 -> auth`、`403 -> risk`、`429 -> rate_limit`、`url_error -> network`、`invalid_json -> api_change`、`unexpected -> unexpected`
  - 同一条回归还会继续验证 [guangya_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/guangya_upload_live.py) 与 [aliyun_open_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/aliyun_open_upload_live.py) 的上传错误分类不会回退，当前会继续把 `local_md5_mismatch` 判成 `input`，把 Aliyun 的 `409` 同名冲突判成 `conflict` 并明确提示改查 `auto_rename_new`
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_error_risk_classification.py` 已验证 Guangya live、Guangya upload、Aliyun upload 当前都会把典型 `401 / 403 / 409 / 429 / 网络失败 / 非 JSON / unexpected` 错误稳定映射为对应的 `riskLevel / riskHint`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_planner_strategy_and_order.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_planner_strategy_and_order.py)，把计划文档单元测试里的 `provider 能力判断 / 秒传策略判断 / fallback 阈值 / 目录底层优先排序` 收成一条独立规划层回归，不再只靠 M6 总结和零散 API verifier 间接证明
  - 这条 verifier 当前会直接锁住 [provider_registry.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/provider_registry.py) 里 `115_open` 的 `fastUploadInputs=["sha1","size"]` 与 `authModes=["official_oauth","manual_cookie"]`，确保 planner 确实按目标 provider 能力来判断秒传条件
  - 同一条回归还会继续验证 [planner.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/planner.py) 在 `thresholdMB=3` 下会把 `sha1` 齐全的小文件判成 `fast_upload`，把缺 `sha1` 但未超阈值的文件判成 `download_upload`，把超阈值的大文件判成 `pending_manual`
  - 执行顺序侧也已同步锁住 `selectedRoots=["/1","/2"]` 时仍保持顶层根顺序 `/1 -> /2`，且每个 root 内部继续按 `deepest_first` 输出，当前 `/1/11/111/movie-fast.bin -> /1/11/112/movie-fallback.bin -> /1/11/archive-large.bin` 的顺序不会被回退成普通扁平队列
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_planner_strategy_and_order.py` 已验证当前 planner 会按 provider 能力判定秒传输入、按 fallback 阈值分流 `fast_upload / download_upload / pending_manual`，并保持“顶层顺序 + 最底层优先”的 `executionGroups`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_auth_profile_masking.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_profile_masking.py)，把计划文档里“授权信息脱敏显示”从已有功能描述补成独立可跑回归，不再只靠旧里程碑文字和零散脚本侧面证明
  - 这条 verifier 当前会直接锁住 [auth_store.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_store.py) 的 `masked_profile()` 仍保持“长 token 保留前 4 后 2、中间脱敏”“长 cookie 保留前 6、中间脱敏”“过短 secret 统一折叠成 `***`”这三条口径，避免后续把真实 secret 直接漏回接口
  - 同一条回归还会继续验证 [auth_profile_view.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_view.py) 与 `/api/auth/profiles` 返回仍会在脱敏后的基础上保留 `resolvedParentId / resolvedFileId`，并对 `tok-demo / domain-demo / drive-demo` 这类占位凭证继续给出 `placeholderFieldHints / placeholderSecretFieldHints / needsSecretRefresh`
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_profile_masking.py` 已验证 `masked_profile()`、`auth_profile_view()` 与 `/api/auth/profiles` 列表当前都会保留脱敏口径，并继续返回解析后的默认目录字段与占位 secret 提示
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_api_plan_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_api_plan_bundle.py)，把计划文档 `API 测试` 段落里最核心的一组接口闭环独立收口，不再只把“登录保护 / 授权保存 / 授权验证 / provider registry / 任务 plan 创建 / 队列状态查询 / 同路径同名文件冲突策略保存与返回”分散在多条 verifier 里间接证明
  - 这条 verifier 当前会同时验证匿名态访问 [webapp.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/webapp.py) 的 `/api/auth/profiles`、`/api/tasks`、`/api/plan/mock` 会统一返回 `401 please_login_first`，错误密码登录会返回 `401 invalid_password`，正确登录后 `/api/session` 会切到 `loggedIn=true`，登出后恢复 `loggedIn=false`
  - 同一条回归还会锁住 `/api/providers` 返回的 provider registry 当前确实包含 `guangya / aliyundrive_open / quark` 等核心 provider，并继续保留 `conflictPolicies / supportsOverwrite / supportsAutoRename / overwriteBehavior` 这些计划相关能力字段
  - 授权链路侧也已一并锁住 `/api/auth/profiles` 保存前会先做最小验证，再持久化为 `verified`，随后 `/api/auth/profiles/{profileId}/validate` 还能再次刷新验证结果；任务链路侧则继续验证 `/api/plan/mock` 与 `/api/tasks` 会保留 `thresholdMB=200`、`conflictPolicy=overwrite_existing`，并在 `/api/tasks` 列表与 `/api/tasks/{taskId}` 详情里继续返回 `awaiting_ack` 队列状态与冲突策略字段
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_api_plan_bundle.py` 已验证当前 API 闭环同时满足登录保护、provider registry 能力字段、授权保存前最小验证、授权验证回刷、任务 plan 创建、队列状态查询，以及同路径同名文件冲突策略保存与返回
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_ui_smoke_navigation_modal.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_ui_smoke_navigation_modal.py)，把计划原文 `UI smoke` 里的 `登录 / Tab 切换 / 授权弹窗 / 任务向导` 收成一条独立前端回归，不再只靠零散静态片段证明 `M10`
  - 这条 verifier 当前会同时检查 [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 里存在 `loginPanel / loginBtn / logoutBtn / tabs / wizardSteps / authModal / advanced-block`，把登录面板、Tab 容器、向导步骤、授权弹窗和高级字段折叠区一次性锁住
  - API 侧也会一起验证 `/api/session` 未登录时返回 `loggedIn=false`，`/api/plan/audit` 与 `/api/auth/capture/start` 在匿名态会返回 `401 please_login_first`，登录后再调用 `capture/start` 会真实返回 `capture_pending`
  - 前端逻辑也已同步锁住 [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 的 `tabKeys` 渲染、`loginPanel/appPanel/logoutBtn` 显隐切换、`renderWizardSteps()`、`openAuthModal()` 与 `startCaptureGuide()` 绑定，以及 `bootstrap()` 里的登录/登出入口
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_ui_smoke_navigation_modal.py` 已验证登录保护、Tab 渲染、任务向导、授权弹窗与 capture guide 入口链路当前全部成立
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_i18n_language_switch.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_i18n_language_switch.py)，把计划文档里明确提到的“基础 i18n / 语言切换”独立锁进回归，不再只在代码和旧里程碑描述里笼统说“有 i18n”
  - 这条 verifier 当前会同时验证 [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 里确实存在 `langSelect`、`zh-CN / en-US` 两个选项，以及初始 `<html lang="zh-CN">`
  - 同一条回归还会继续验证 [webapp.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/webapp.py) 的 `/api/i18n` 在 `zh-CN / en-US / 非法 lang` 三种情况下的返回口径，以及 [i18n.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/i18n.py) 的 fallback 仍会回退到 `zh-CN`
  - 前端侧也已一并锁住 [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 会跟踪 `state.lang`、调用 `loadI18n()`、更新 `document.documentElement.lang`、回写语言下拉，并继续用翻译后的文案渲染 Tab、任务向导标题和步骤说明
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_i18n_language_switch.py` 已验证语言切换链当前会同时满足页面下拉、`/api/i18n` 返回、fallback 规则、以及前端 `loadI18n()/render()` 的中英文渲染逻辑
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 现已把队列页“新建任务时显式选择阈值与同名冲突策略”的 UI 链路锁进回归，不再只验证 Preview 面板和 guard，而漏掉表单本身的 `taskThresholdMB / taskConflictPolicy`
  - verifier 当前会同时检查 [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 里确实存在 `taskThresholdMB` 输入框、`taskConflictPolicy` 选择框，以及 `auto_rename_new / overwrite_existing` 两个显式选项
  - 同一条回归现在还会继续锁住 [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 已从表单读取 `thresholdRaw / conflictPolicy`，并把 `thresholdMB / conflictPolicy` 同时带进 Preview 请求、Preview meta 文案和最终 Create Task 请求，避免后续把“页面可选”又退回成“只在内部默认值里生效”
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_queue_plan_preview_ui.py` 已验证队列页当前会显式渲染 `taskThresholdMB / taskConflictPolicy`，并在 Preview / Create 链路中继续保留 `thresholdMB / conflictPolicy`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_auth_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_remediation_bundle.py) 现在已把 auth remediation synthetic bundle/API/Markdown 回归正式切到当前的 secret-refresh / recreate-probe 口径，不再保留已经过时的 `patch_auth_profile_extra.py` 旧期待
  - verifier 当前会同时锁住 synthetic summary 计数、`smoke-guangya` 与 `aliyun-bootstrap` 的 `recommendedRecreateProbeCommand`、`placeholderSecretFieldHints=[token]`，以及 `189-readonly-share` 仍应继续保留账号写授权补丁命令
  - 这样授权补救链路现在除了 current sync verifier、export verifier 之外，连独立 synthetic bundle verifier 也已经把“先换真 secret 再 probe”和“189 只读档案仍需 patch 写鉴权”这两条现行分流一起锁住了
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_auth_remediation_bundle.py` 已验证当前 synthetic bundle summary、Markdown 和 API 返回会同时满足 `needsSecretRefreshCount=2`、Guangya/Aliyun 的 `recommendedRecreateProbeCommand`，以及 189 的 `patch_189cloud_account_auth.py` 写鉴权补救命令
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py) 现已把 `recreate_probe` 这条导出分支锁进回归，不再只验证旧的 `post_refresh_runtime / bootstrap` 主命令标签
  - synthetic export payload 现在会显式模拟 `guangya` 处于 `needsSecretRefresh=True`、`placeholderSecretFieldHints=[token]` 的场景，并验证导出的 [12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 中会写出 `providersWithRecreateProbeCommand`、`recommendedRecreateProbeCommand` 与 `placeholderSecretFieldHints`
  - 这样 `real_evidence_remediation` 现在不仅有 current sync verifier 和 synthetic bundle verifier，连独立 export verifier 也已经把新补救路径覆盖到了
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证临时导出的 remediation Markdown 当前会同时包含 `providersWithRecreateProbeCommand: 1`、`recommendedRecreateProbeCommand`、`placeholderSecretFieldHints: token` 与 `recommendedPrimaryCommand label=recreate_probe`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [scripts/create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_live_upload_task.py)、[scripts/create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_fast_upload_candidate_task.py)、[scripts/create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_runtime_probe_task.py) 的 remediation follow-up 现已统一补齐 `needsSecretRefresh / placeholderSecretFieldHints / recommendedRecreateProbeCommand`
  - 这样这 3 个 task helper 在返回 `recommendedPrimaryCommandLabel / recommendedPrimaryCommand` 之外，也能把“当前其实应先换真 token/cookie 再 probe”的结构化信号一起带出来，不再只让调用方看到一条命令，却看不到这是 `recreate_probe` 还是普通 runtime follow-up
  - 对应 verifier 已同步补强：[scripts/verify_create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task.py)、[scripts/verify_create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_candidate_task.py)、[scripts/verify_create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_runtime_probe_task.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_create_live_upload_task.py` 已验证 live upload helper 输出当前会同时带 `recommendedPrimaryCommandLabel=recreate_probe`、`recommendedRecreateProbeCommand`、`needsSecretRefresh=true` 与 `placeholderSecretFieldHints=[token]`
  - `.\.venv\Scripts\python.exe scripts\verify_create_fast_upload_candidate_task.py` 已验证 fast candidate helper 输出当前也会带 `recommendedPrimaryCommandLabel=recreate_probe`、`recommendedRecreateProbeCommand`、`needsSecretRefresh=true` 与 `placeholderSecretFieldHints=[cookie]`
  - `.\.venv\Scripts\python.exe scripts\verify_create_runtime_probe_task.py` 已验证 runtime probe helper 输出当前也会带 `recommendedPrimaryCommandLabel=recreate_probe`、`recommendedRecreateProbeCommand`、`needsSecretRefresh=true` 与 `placeholderSecretFieldHints=[token]`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 的 synthetic bundle/API/Markdown 回归现已把 `recreate_probe` 这条新分支正式锁进来，不再只覆盖旧的 `runtime_probe / post_bootstrap_runtime / refresh_evidence` 路径
  - synthetic profile 现会显式模拟 `guangya / aliyundrive_open` 处于 `profileReady=False + needsSecretRefresh=True + placeholderSecretFieldHints=[token]` 的状态，并据此验证 summary 会产出 `providersWithRecreateProbeCommand=2`
  - 同一条 verifier 现在还会继续验证 Markdown 与 API 明细里都能看到 `recommendedRecreateProbeCommand / placeholderSecretFieldHints / recommendedPrimaryCommandLabel=recreate_probe`，避免后续再出现“真实 current sync 已对齐，但 synthetic bundle 回归没覆盖到”的空档
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 当前已验证 bundle summary、Markdown 导出和 API 返回里，`providersWithRecreateProbeCommand`、`recommendedRecreateProbeCommand`、`placeholderSecretFieldHints` 与 `recommendedPrimaryCommandLabel=recreate_probe` 都已同步成立
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [scripts/create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_auth_profile_stub.py) 的 remediation 输出现已补齐 `needsSecretRefresh / placeholderSecretFieldHints / recommendedRecreateProbeCommand`，当新建出来的 profile 仍是 smoke/demo 凭证时，helper 返回结果不再只会给旧的 refresh 路径
  - [scripts/patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/patch_and_probe_auth_profile.py) 的 remediation 输出现也与其他 helper 对齐，已同步回出 `recommendedPrimaryCommandLabel / recommendedPrimaryCommand / recommendedRecreateProbeCommand / needsSecretRefresh / placeholderSecretFieldHints`
  - 这样“建档后 probe”与“补字段后 probe”两条 helper 现在都能直接把“当前其实应该先换真 token/cookie 再 probe”这类结论连同命令一起带回，不再出现 docs/UI 已经切到 `recreate_probe`，但 helper JSON 还是旧 follow-up 字段的割裂
  - 对应 verifier 已同步补强：[scripts/verify_create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_auth_profile_stub.py) 与 [scripts/verify_patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_and_probe_auth_profile.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_create_auth_profile_stub.py` 已验证 `create_auth_profile_stub.py` 当前会把 `recommendedPrimaryCommandLabel=recreate_probe`、`recommendedRecreateProbeCommand`、`needsSecretRefresh=true` 与 `placeholderSecretFieldHints=[token]` 一起写进 remediation 输出
  - `.\.venv\Scripts\python.exe scripts\verify_patch_and_probe_auth_profile.py` 已验证 `patch_and_probe_auth_profile.py` 当前也会把 `recommendedPrimaryCommandLabel=recreate_probe`、`recommendedRecreateProbeCommand`、`needsSecretRefresh=true` 与 `placeholderSecretFieldHints=[token]` 一起写进 remediation 输出
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/web/assets/app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 里的设置页 `Real Evidence Next Steps` 面板现已把最新 remediation bundle 新增字段真正显示出来，不再停留在旧的 `patch / patchProbe / refresh` 口径
  - 当前 summary 行已新增 `recreateProbeCommands=${remediationSummary.providersWithRecreateProbeCommand || 0}`，因此当补救链路把 `guangya / aliyundrive_open` 这类 provider 切到“先重建真凭证再 probe”时，设置页会同步显示这条新的主路径数量
  - provider 行现在也已同步显示 `needsSecretRefresh=${Boolean(item.needsSecretRefresh)}`、`placeholderSecretHints=${placeholderSecretHints}` 与 `recreateProbe=${item.recommendedRecreateProbeCommand}`，不再只看到旧命令，却看不到“为什么要先重建/换真凭证”
  - [scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py) 已同步补强，静态锁住 `providersWithRecreateProbeCommand / recommendedRecreateProbeCommand / needsSecretRefresh / placeholderSecretFieldHints` 这些 UI 消费点
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页 remediation 面板当前确实展示 `recreateProbeCommands` 汇总，以及逐 provider 的 `recreateProbe / needsSecretRefresh / placeholderSecretHints`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/auth_profile_view.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_view.py) 现已把“占位 secret 字段”和“普通缺字段”拆开：会额外给出 `placeholderSecretFieldHints` 与 `needsSecretRefresh`，把 `tok-demo / tok_smoke`、以及需要真实 `cookie/accessToken` 的场景单独标成“必须先换真凭证”
  - [src/cloudpan_sync/auth_profile_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_remediation.py) 已新增 `recommendedRecreateProbeCommand`，对这类仍含占位 secret 的档案，不再继续误导成“只 patch extra 就行”，而是明确改成“重建或补真凭证后直接 probe”
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 已把这条逻辑同步抬到 provider 级 remediation：`guangya` 与 `aliyundrive_open` 当前主命令已从旧的 `patch_probe / refresh_evidence` 切成 `recreate_probe`，summary 也新增 `providersWithRecreateProbeCommand`
  - [src/cloudpan_sync/auth_profile_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_evidence.py) 与当前导出的 [docs/08-AUTH_EVIDENCE_BUNDLE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/08-AUTH_EVIDENCE_BUNDLE.md)、[docs/09-AUTH_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/09-AUTH_REMEDIATION_GUIDE.md)、[docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 已同步写出 `placeholderSecretFieldHints / needsSecretRefreshCount / recommendedRecreateProbeCommand / providersWithRecreateProbeCommand`
  - 对应 verifier 已同步补强：[scripts/verify_current_auth_evidence_bundle_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_evidence_bundle_sync.py)、[scripts/verify_export_auth_evidence_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_evidence_bundle.py)、[scripts/verify_current_auth_remediation_bundle_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_remediation_bundle_sync.py)、[scripts/verify_export_auth_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_remediation_bundle.py)、[scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\export_auth_evidence_bundle.py`、`scripts\export_auth_remediation_bundle.py`、`scripts\export_real_evidence_remediation.py` 已重导出当前真实文档，实际写出了 `needsSecretRefreshCount=3` 与 `providersWithRecreateProbeCommand=2`
  - [docs/09-AUTH_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/09-AUTH_REMEDIATION_GUIDE.md) 当前已把 `smoke-guangya / risk-smoke-guangya / aliyun-bootstrap` 改成 `recommendedRecreateProbeCommand`，不再继续输出旧的 patch-only 命令
  - [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 当前已把 `guangya / aliyundrive_open` 的 `recommendedPrimaryCommandLabel` 切成 `recreate_probe`
  - `.\.venv\Scripts\python.exe scripts\verify_current_auth_evidence_bundle_sync.py`、`scripts\verify_export_auth_evidence_bundle.py`、`scripts\verify_current_auth_remediation_bundle_sync.py`、`scripts\verify_export_auth_remediation_bundle.py`、`scripts\verify_current_real_evidence_remediation_sync.py` 已验证这条“先换真 secret 再 probe”的新口径已同步到当前文档/导出链
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - 这轮不是只补文档，而是先真实执行了 `.\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id 22173a49-2206-4da8-8624-9bab7bbbe64b --write`，实际补到了一条新的线上失败证据：当前 `aliyundrive_open` 档案会在 live list 阶段收到 `http_error:404`
  - 基于这次真实联调结果，已把 [src/cloudpan_sync/auth_profile_view.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_view.py) 补成可识别占位凭证/占位字段，当前会把 `tok-demo / tok_smoke / domain-demo / drive-demo` 这类 smoke/demo 值当成真实缺口暴露到 `missingFieldHints` 与 `placeholderFieldHints`
  - [src/cloudpan_sync/auth_profile_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_evidence.py) 和 [src/cloudpan_sync/auth_profile_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/auth_profile_remediation.py) 已同步把 `placeholderFieldHints` 导出到证据 Markdown / remediation Markdown，不再把这类假档案误写成“已 ready”
  - 当前真实导出的 [docs/08-AUTH_EVIDENCE_BUNDLE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/08-AUTH_EVIDENCE_BUNDLE.md) 已从 `profileReadyCount=1` 收紧为 `0`；[docs/09-AUTH_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/09-AUTH_REMEDIATION_GUIDE.md) 已从 `readyCount=1` 收紧为 `0`；`aliyun-bootstrap` 现在会明确提示必须先替换真实 `token/domainId/driveId`
  - 这次真实联调新增的失败记录也已经回写并重导出 [docs/03-AUTH_LIVE_VALIDATION_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/03-AUTH_LIVE_VALIDATION_REPORT.md)、[docs/05-PROVIDER_LIVE_PROBE_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/05-PROVIDER_LIVE_PROBE_REPORT.md) 和 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md)，当前 remediation 也已把 `aliyundrive_open` 从“refresh evidence”收紧成“先 patch 真实字段”
  - 对应 verifier 已同步补强：[scripts/verify_auth_profile_readiness.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_profile_readiness.py)、[scripts/verify_export_auth_evidence_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_evidence_bundle.py)、[scripts/verify_export_auth_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_remediation_bundle.py)、[scripts/verify_current_auth_evidence_bundle_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_evidence_bundle_sync.py)、[scripts/verify_current_auth_remediation_bundle_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_remediation_bundle_sync.py)、[scripts/verify_current_auth_live_validation_report_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_live_validation_report_sync.py)、[scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\patch_and_probe_auth_profile.py --profile-id 22173a49-2206-4da8-8624-9bab7bbbe64b --write --evidence-output tmp\aliyundrive_open-auth-evidence-live.md` 已实际产出一条新的 `aliyundrive_open` 线上失败证据，错误为 `http_error:404`
  - `.\.venv\Scripts\python.exe scripts\export_auth_evidence_bundle.py`、`scripts\export_auth_remediation_bundle.py`、`scripts\export_auth_live_validation_report.py`、`scripts\export_live_probe_report.py`、`scripts\export_real_evidence_remediation.py` 已重导出当前真实文档
  - `.\.venv\Scripts\python.exe scripts\verify_auth_profile_readiness.py` 已验证占位值会把 Guangya / Aliyun smoke 档案判成 not ready，而真实字段的 Aliyun profile 仍可保持 ready
  - `.\.venv\Scripts\python.exe scripts\verify_export_auth_evidence_bundle.py`、`scripts\verify_export_auth_remediation_bundle.py` 已验证导出链会保留 `placeholderFieldHints`
  - `.\.venv\Scripts\python.exe scripts\verify_current_auth_evidence_bundle_sync.py`、`scripts\verify_current_auth_remediation_bundle_sync.py`、`scripts\verify_current_auth_live_validation_report_sync.py`、`scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前仓库真实导出文档与新的占位值/失败证据口径一致
  - 本轮启动的项目 `.venv` `python` verifier 与联调进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 现在会为每个 provider 统一计算 `recommendedPrimaryCommand` 和 `recommendedPrimaryCommandLabel`，把当前最值得先跑的一条补救命令结构化输出出来
  - 当前优先级已经落到真实 bundle：例如 `guangya` 会先指向 `patch_and_probe_auth_profile.py`，`aliyundrive_open` 会先指向 `recommendedRefreshEvidenceCommand`，而 `115_open / quark / 189cloud / baidu_netdisk / xunlei / 123_open` 这类无现成 profile 的 provider，会直接把首条 `post-bootstrap runtime` helper 作为主命令给出
  - [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 与设置页 remediation 面板已同步展示 `providersWithPrimaryCommand` 汇总，以及逐 provider 的 `recommendedPrimaryCommand` / `label=...`，从“看一堆候选命令”进一步变成“直接抄当前首选下一条”
  - [scripts/create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_auth_profile_stub.py)、[scripts/create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_live_upload_task.py)、[scripts/create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_fast_upload_candidate_task.py)、[scripts/create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_runtime_probe_task.py) 的 remediation follow-up 输出也已带上这组主命令字段，helper 结果不再只给“下一步说明”，还能直接给“当前首选命令”
  - 对应 verifier 已同步补强：[scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)、[scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)、[scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)、[scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)、[scripts/verify_create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_auth_profile_stub.py)、[scripts/verify_create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task.py)、[scripts/verify_create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_candidate_task.py)、[scripts/verify_create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_runtime_probe_task.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 synthetic remediation bundle/API/Markdown 会同步输出 `providersWithPrimaryCommand` 与 `recommendedPrimaryCommand`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出的 Markdown 会写出 `providersWithPrimaryCommand` 与逐 provider 的 `recommendedPrimaryCommand`
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页会显示 `primaryCommands=${remediationSummary.providersWithPrimaryCommand || 0}`，以及 `primary=${item.recommendedPrimaryCommand}` / `primaryLabel=${item.recommendedPrimaryCommandLabel}`
  - `.\.venv\Scripts\python.exe scripts\export_real_evidence_remediation.py` 已重导出当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md)
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前仓库导出的真实 remediation 指南与 `providersWithPrimaryCommand=10` 一致，并锁住 `guangya / aliyundrive_open / 115_open / quark / 189cloud / baidu_netdisk / xunlei / 123_open` 的主命令标签
  - `.\.venv\Scripts\python.exe scripts\verify_create_auth_profile_stub.py`、`scripts\verify_create_live_upload_task.py`、`scripts\verify_create_fast_upload_candidate_task.py`、`scripts\verify_create_runtime_probe_task.py` 已验证 helper JSON 输出现在都能带出 `recommendedPrimaryCommandLabel / recommendedPrimaryCommand`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [scripts/create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_live_upload_task.py)、[scripts/create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_fast_upload_candidate_task.py)、[scripts/create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_runtime_probe_task.py) 的 JSON 输出现在都会直接带上 `remediationFollowup`
  - 当前这三类 task helper 在输出里已能直接给出当前 profile 对应的 `nextStep`，以及最相关的 `recommendedRuntimeProbeCommand / recommendedLiveUploadCommand / recommendedFastCandidateCommand / recommendedRuntimeSuccessCommand / recommendedOverwriteVariantCommand / recommendedPostRefreshRuntimeCommand`
  - 这样从“跑出 live success / candidate-only / probe-only 样本”到“决定下一条继续跑什么”已经不需要再跳回 remediation 文档或 UI 查命令，进一步缩短了 `P-REAL` 的连续执行链路
  - 对应 verifier 已同步补强：[scripts/verify_create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task.py)、[scripts/verify_create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_candidate_task.py)、[scripts/verify_create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_runtime_probe_task.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_create_live_upload_task.py` 已验证 live upload helper 的 JSON 输出包含 `remediationFollowup`
  - `.\.venv\Scripts\python.exe scripts\verify_create_fast_upload_candidate_task.py` 已验证 fast candidate helper 的 JSON 输出包含 `remediationFollowup`
  - `.\.venv\Scripts\python.exe scripts\verify_create_runtime_probe_task.py` 已验证 runtime probe helper 的 JSON 输出包含 `remediationFollowup`
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [scripts/create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_auth_profile_stub.py) 和 [scripts/patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/patch_and_probe_auth_profile.py) 现在在保存/探测完成后，会把当前 profile 对应的 remediation follow-up 一起打印到 JSON 结果里
  - 当前输出已可直接带出 `nextStep / recommendedRefreshEvidenceCommand / recommendedPostRefreshRuntimeCommand / recommendedRuntimeSuccessCommand / recommendedOverwriteVariantCommand`，用户不必再回到 `docs/12` 手工查下一条命令
  - 这让“创建档案并 probe”与“修补档案并 probe”两条 helper，都进一步变成连续可执行链路，而不是只返回一份静态探测结果
  - 对应 verifier 已同步补强：[scripts/verify_create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_auth_profile_stub.py) 与 [scripts/verify_patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_and_probe_auth_profile.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_create_auth_profile_stub.py` 已验证 `create_auth_profile_stub.py` 的 JSON 输出现在包含 remediation follow-up
  - `.\.venv\Scripts\python.exe scripts\verify_patch_and_probe_auth_profile.py` 已验证 `patch_and_probe_auth_profile.py` 的 JSON 输出现在包含 remediation follow-up
  - 本轮启动的项目 `.venv` `python` verifier 进程已主动清理，无残留项目测试进程

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 已新增 `recommendedPostRefreshRuntimeCommand`，专门覆盖“已有 profile、先 refresh/probe、再补首条 runtime 成功样本”的 provider
  - 当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 不再只告诉用户先跑 `recommendedRefreshEvidenceCommand`，还会把 refresh 之后下一条直接可跑的 runtime helper 一并提前准备好
  - 真实仓库当前已能明确给出 `providersWithPostRefreshRuntimeCommand=1`，也就是 `aliyundrive_open` 这种“已有档案但还缺基础联调证据”的路径，现在能少一次手工拼命令
  - 设置页 remediation 面板也已同步展示 `postRefreshRuntimeCommands` 汇总，以及逐 provider 的 `postRefreshRuntime=...` 行，帮助直接从 UI 里抄命令继续补 runtime 样本
  - 对应 verifier 已同步补强：[scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)、[scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)、[scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)、[scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 bundle/API summary 中新增 `providersWithPostRefreshRuntimeCommand`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出 Markdown 会写出 `providersWithPostRefreshRuntimeCommand` 和 `recommendedPostRefreshRuntimeCommand`
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页会显示 `postRefreshRuntimeCommands=${remediationSummary.providersWithPostRefreshRuntimeCommand || 0}` 与 `postRefreshRuntime=${item.recommendedPostRefreshRuntimeCommand}`
  - `.\.venv\Scripts\python.exe scripts\export_real_evidence_remediation.py` 已重导出当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md)
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前仓库里 `aliyundrive_open` 分段继续保留 `recommendedRefreshEvidenceCommand + recommendedPostRefreshRuntimeCommand + recommendedOverwriteVariantCommand` 的联动口径

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 已把 provider 冲突支持状态进一步落到 `nextStep` 文案里，不再只停留在独立字段和命令参数说明
  - 当前对于 `overwrite_existing` 真支持、会降级、仅 probe-only 写探针、以及尚未声明支持的 provider，`nextStep` 会给出不同的实操提示，帮助用户首条真实样本直接避开错误冲突策略
  - 例如当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 已明确提示：`quark` 首条样本建议继续保留默认 `auto_rename_new`；`115_open` 不要把首条样本建立在 `overwrite_existing` 上
  - 这让 remediation guide 从“能看懂命令”进一步变成“知道先怎么跑第一条真实样本”，更贴近 `P-REAL` 当前的实际推进需要
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 remediation bundle/API/Markdown 仍保持当前结构和计数口径
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\export_real_evidence_remediation.py` 已重导出当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md)
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前 `115_open / quark / 189cloud / baidu_netdisk / xunlei / 123_open / aliyundrive_open` 分段继续保留新的冲突策略 `nextStep` 分流提示

### 已完成补齐项 - `2026-05-26`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 的 remediation bundle 现已补出 provider 级冲突能力快照：`declaredConflictPolicies / overwriteSupportStatus / autoRenameSupportStatus / overwriteBehavior / providerConflictNotes`
  - [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 现在不只告诉用户“命令可改成 `overwrite_existing`”，还会明确写出当前 provider 是真支持直接覆盖、会诚实降级成自动改名，还是仍未声明为可安全支持
  - 顶部 summary 也新增了结构化汇总计数：`providersWithDeclaredConflictPolicies=8`、`providersWithProviderManagedOverwrite=1`、`providersWithOverwriteDowngrade=7`、`providersWithConflictUnsupported=1`
  - 设置页 remediation 面板也已同步展示这些 provider 级冲突能力字段和汇总计数，后续做真实联调时，不需要再来回翻状态矩阵才能判断该选 `overwrite_existing` 还是 `auto_rename_new`
  - 对应 verifier 已同步补强：[scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)、[scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)、[scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)、[scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 synthetic bundle/API/Markdown 同步带出新的冲突能力结构字段与 `7 / 1 / 6 / 1` 计数口径
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出 Markdown 会写出新的冲突能力汇总与 provider 分段说明
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页会显示 `directOverwrite / overwriteDowngrade / conflictUnsupported` 汇总，以及 `conflictDeclared / overwriteSupport / autoRenameSupport / providerConflictNotes` 行文案
  - `.\.venv\Scripts\python.exe scripts\export_real_evidence_remediation.py` 已重导出当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md)
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前仓库导出的真实 remediation 指南与 `8 / 1 / 7 / 1` 当前计数一致，并锁住 `115_open / quark / 189cloud / baidu_netdisk / xunlei / 123_open / aliyundrive_open` 的冲突支持分流说明

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 的 remediation summary 已新增 `providersWithConflictPolicyNote`
  - 这样 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 和设置页 remediation summary 现在不仅能按条目看到 `conflictPolicyNote`，还可以直接汇总当前有多少 provider 已经具备这类冲突策略说明
  - 当前真实仓库导出的 remediation summary 已明确量化为 `providersWithConflictPolicyNote=6`；synthetic verifier 覆盖的更广场景则锁到 `9`
  - 对应 verifier 也已同步补强：[scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)、[scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)、[scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)、[scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 synthetic summary 中 `providersWithConflictPolicyNote=9`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出 Markdown 会写出 `providersWithConflictPolicyNote: 6`
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前仓库导出的 remediation summary 与 `providersWithConflictPolicyNote=6` 一致
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页会显示 `conflictPolicyNotes=${remediationSummary.providersWithConflictPolicyNote || 0}`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 的 remediation summary 已新增 `providersWithOverwriteVariantCommand`
  - 这样 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 和设置页 remediation summary 现在不止能逐条看到 overwrite 变体命令，还能直接汇总当前有多少 provider 已经具备这类显式覆盖模式 helper
  - 当前真实仓库导出的 remediation summary 已明确量化为 `providersWithOverwriteVariantCommand=6`；synthetic verifier 覆盖的更广场景则锁到 `9`
  - 对应 verifier 也已同步补强：[scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)、[scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)、[scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)、[scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 synthetic summary 中 `providersWithOverwriteVariantCommand=9`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出 Markdown 会写出 `providersWithOverwriteVariantCommand: 6`
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前仓库导出的 remediation summary 与 `providersWithOverwriteVariantCommand=6` 一致
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页会显示 `overwriteVariantCommands=${remediationSummary.providersWithOverwriteVariantCommand || 0}`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 已新增 `recommendedOverwriteVariantCommand`
  - 当前 remediation provider 只要已经暴露 `recommendedRuntimeSuccessCommand / recommendedPostBootstrapRuntimeCommand / recommendedLiveUploadCommand / recommendedFastCandidateCommand / recommendedRuntimeProbeCommand` 里的任一种 helper，就会额外生成一条 `overwrite_existing` 变体命令，用户不再需要手改原命令里的 `--conflict-policy`
  - 这样 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 和设置页 remediation 面板里，现在同时能看到默认 `auto_rename_new` 命令、显式 `overwrite_existing` 变体命令，以及 provider 不支持覆盖时会诚实降级/提示的说明
  - 对应 verifier 也已同步补强：[scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)、[scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)、[scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)、[scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 bundle/API/Markdown 都带 `recommendedOverwriteVariantCommand`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出 Markdown 也会写出 `recommendedOverwriteVariantCommand`
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页 remediation 行会显示 `overwriteVariant=${item.recommendedOverwriteVariantCommand}`
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 中 `115_open / quark / 189cloud / baidu_netdisk / xunlei / 123_open` 这几条 post-bootstrap helper 现都同步附带 overwrite 变体

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 已新增结构化字段 `conflictPolicyNote`
  - 当前只要 remediation provider 暴露了 `recommendedRuntimeProbeCommand / recommendedLiveUploadCommand / recommendedFastCandidateCommand / recommendedRuntimeSuccessCommand / recommendedPostBootstrapRuntimeCommand` 任意一种 helper，就会同时给出一句固定说明：默认使用 `--conflict-policy auto_rename_new`，如需直接覆盖同名文件，可改成 `overwrite_existing`
  - 这条说明已同步进 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 和设置页 remediation 面板，用户现在不止能看到命令里带了什么参数，也能直接看到该怎么改策略
  - 对应 verifier 也已同步补强：[scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)、[scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)、[scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py)
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 bundle/API/Markdown 都带 `conflictPolicyNote`，并保留 `overwrite_existing`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出 Markdown 也会写出 `conflictPolicyNote`
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 中 `115_open / quark / 189cloud / baidu_netdisk / xunlei / 123_open` 这几条 post-bootstrap helper 都继续附带该说明
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证设置页 remediation 行会显示 `conflictPolicyNote=${item.conflictPolicyNote}`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py) 已补出 `jsRemediationRowsPreserveRuntimeCommandText` 断言
  - 这条前端校验会继续锁住设置页 remediation 面板仍然原样展示 `runtimeSuccess` 与 `postBootstrapRuntime` 两类 helper 命令文本，避免未来 UI 还在显示 remediation 行，但把后端给出的完整命令字符串吞掉或改写
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证 `jsRemediationRowsPreserveRuntimeCommandText=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 已把 remediation bundle 里生成的 `recommendedRuntimeProbeCommand / recommendedLiveUploadCommand / recommendedFastCandidateCommand / recommendedPostBootstrapRuntimeCommand` 统一补成显式 `--conflict-policy auto_rename_new`
  - 这样 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 里的真实取证 helper 不再把“同名文件冲突时怎么处理”藏在脚本默认值里，而是直接把当前默认策略写出来，后续需要覆盖时也能直接改成 `overwrite_existing`
  - 对应 verifier 也已同步补强：[scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)、[scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)、[scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py) 现在都会锁住这些 helper 命令继续显式带 `--conflict-policy auto_rename_new`
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 API/Markdown bundle 中 runtime helper 与 post-bootstrap helper 都显式带 `--conflict-policy auto_rename_new`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出链写出的 Markdown 也显式保留冲突策略选择
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 中 `115_open / quark / 189cloud / baidu_netdisk / xunlei / 123_open` 的 post-bootstrap helper 继续保持这条口径

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_current_local_live_adapter_verification_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_local_live_adapter_verification_sync.py)，直接锁住当前 [docs/07-LOCAL_LIVE_ADAPTER_VERIFICATION.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/07-LOCAL_LIVE_ADAPTER_VERIFICATION.md) 的本地 adapter stub 验证口径
  - 当前这条校验会确认 10 个 provider 的本地 stub adapter 都继续 `list_ok / metadata_ok / create_ok=True`，并且 `Probe Checks` 中每家都是 `3`
  - 同时还锁住 `Matrix Rows` 里 10 家 provider 都保持 `list_ready / metadata_ready / create_dir_ready / live_probe_ok=True`，以及 `189cloud` 继续保留账号级 `live_account_auth` 写目录样本
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_local_live_adapter_verification.py` 已验证本地 live adapter 报告导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_current_local_live_adapter_verification_sync.py` 已验证 `allProviderSectionsPresent=true`、`allAdaptersReportListMetadataCreateOk=true`
  - 同一验证已锁住 `allProbeChecksAreThree=true`、`allMatrixRowsLiveProbeOk=true`、`cloud189KeepsAccountCreateMode=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [docs/11-TASK_RUNTIME_EVIDENCE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/11-TASK_RUNTIME_EVIDENCE.md) 已按当前 `task_runtime_evidence_store` 重新导出，不再停留在 `sampleCount=0` 的旧报告
  - 当前任务运行真实样本报告已同步为 `sampleCount=3`、`providerCount=3`、`successProviderCount=3`、`successCount=3`、`verifyOkCount=3`、`conflictHandledCount=3`
  - 已新增 [scripts/verify_current_task_runtime_evidence_report_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_task_runtime_evidence_report_sync.py)，直接锁住 `pikpak / uc / guangya` 三条当前 runtime success 样本，以及三条同名冲突降级处理记录
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\export_task_runtime_evidence_report.py` 已重导出当前 [docs/11-TASK_RUNTIME_EVIDENCE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/11-TASK_RUNTIME_EVIDENCE.md)
  - `.\.venv\Scripts\python.exe scripts\verify_export_task_runtime_evidence_report.py` 已验证任务运行证据报告导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_current_task_runtime_evidence_report_sync.py` 已验证 `summaryHasCurrentRuntimeCounts=true`、`summaryShowsExpectedRuntimeCounts=true`
  - 同一验证已锁住 `hasPikpakSuccessRow=true`、`hasUcSuccessRow=true`、`hasGuangyaSuccessRow=true`、`allRowsKeepConflictDowngrade=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_current_auth_remediation_bundle_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_remediation_bundle_sync.py)，直接锁住当前 [docs/09-AUTH_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/09-AUTH_REMEDIATION_GUIDE.md) 的当前 remediation 口径
  - 当前这条校验会同时核对 summary 和 profile 分段，确保 `profileCount=3`、`readyCount=1`、`needsFixCount=2`、`writeReadyCount=3`、`writeNeedsFixCount=0` 持续与当前本地 remediation bundle 一致
  - 同时还锁住两条 `guangya` smoke profile 继续走 `patch_auth_profile_extra.py --set parentId=...` 补救路径，以及 `aliyun-bootstrap` 当前已是 `profileReady/writeReady=True` 且 `resolvedParentId=root`
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_auth_remediation_bundle.py` 已验证 auth remediation bundle 导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_current_auth_remediation_bundle_sync.py` 已验证 `summaryHasCurrentAuthRemediationCounts=true`、`summaryShowsExpectedAuthRemediationCounts=true`
  - 同一验证已锁住 `hasSmokeGuangyaPatchCommand=true`、`hasRiskSmokeGuangyaPatchCommand=true`、`hasAliyunBootstrapReadyProfile=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_current_auth_evidence_bundle_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_evidence_bundle_sync.py)，直接锁住当前 [docs/08-AUTH_EVIDENCE_BUNDLE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/08-AUTH_EVIDENCE_BUNDLE.md) 的当前 auth evidence 口径
  - 当前这条校验会同时核对 summary 和 profile 分段，确保 `profileCount=3`、`profileReadyCount=1`、`writeReadyCount=3`、`validationOkCount=0`、`probeOkCount=0` 持续与当前本地 auth evidence bundle 一致
  - 同时还锁住两条 `guangya` smoke profile 的 `missing_parent_id` 缺口口径，以及 `aliyun-bootstrap` 当前已写入 `resolvedParentId=root` 且 `profileReady/writeReady=True`
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_auth_evidence_bundle.py` 已验证 auth evidence bundle 导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_current_auth_evidence_bundle_sync.py` 已验证 `summaryHasCurrentAuthEvidenceCounts=true`、`summaryShowsExpectedAuthEvidenceCounts=true`
  - 同一验证已锁住 `hasSmokeGuangyaProfile=true`、`hasRiskSmokeGuangyaProfile=true`、`hasAliyunBootstrapProfile=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_current_auth_live_validation_report_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_auth_live_validation_report_sync.py)，直接锁住当前 [docs/03-AUTH_LIVE_VALIDATION_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/03-AUTH_LIVE_VALIDATION_REPORT.md) 的当前 validation 口径
  - 当前这条校验会同时核对 summary 和 latest/history 分段，确保 `totalRecords=4`、`latestProfileCount=2`、`latestOkCount=0`、`latestFailedCount=2`、`latestProviders=guangya` 持续与本地已保存 validation 记录一致
  - 同时还锁住两条 latest `guangya` row 继续保持 `profile_incomplete / missing_parent_id` 口径，以及 recent history 里的 `checkCount=1` 记录数
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_auth_live_validation_report.py` 已验证 auth live validation 报告导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_current_auth_live_validation_report_sync.py` 已验证 `summaryHasCurrentValidationCounts=true`、`summaryShowsExpectedValidationCounts=true`
  - 同一验证已锁住 `latestSectionKeepsTwoGuangyaRows=true`、`latestRowsMatchLatestValidationCount=true`、`recentHistoryKeepsCheckCountRows=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/live_probe.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/live_probe.py) 已修正 provider live probe 报告的 summary 口径，不再把同一 provider 下多条 saved profile probe 历史条目误算进最终 provider 级 summary
  - 现在 `run_live_probe()` 会按最终导出的 provider 行重新汇总 `profileProbeProviderCount / profileProbeOkCount / profileProbeFailedCount`，从而与 [docs/05-PROVIDER_LIVE_PROBE_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/05-PROVIDER_LIVE_PROBE_REPORT.md) 的 markdown 分段保持同一口径
  - 已新增 [scripts/verify_live_probe_provider_summary_alignment.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_live_probe_provider_summary_alignment.py)，专门锁住“同一 provider 存在多条 latest profile probe 时，summary 只能按 provider 计 1 条，并采用该 provider 最后一条 probe 内容写入 markdown”
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_live_probe_report.py` 已验证 live probe 报告导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_live_probe_provider_summary_alignment.py` 已验证 `profileProbeProviderCountIsProviderScoped=true`、`profileProbeFailedCountIsProviderScoped=true`
  - 同一验证已锁住 `guangyaUsesLatestProfileProbe=true` 与 `markdownHasSingleGuangyaProfileProbeRow=true`
  - `.\.venv\Scripts\python.exe scripts\export_live_probe_report.py` 已把当前 [docs/05-PROVIDER_LIVE_PROBE_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/05-PROVIDER_LIVE_PROBE_REPORT.md) 同步到修正后的 summary 口径

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_current_plan_audit_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_plan_audit_sync.py)，直接锁住当前 [docs/04-PLAN_AUDIT_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/04-PLAN_AUDIT_REPORT.md) 的当前审计口径
  - 当前这条校验会同时核对顶部 summary 与关键里程碑分段，确保 `done=5 / partial=2 / todo=1`、`featureCompletionPercent=85.7`、`strictCompletionPercent=75.0` 持续与当前 plan audit 结果一致
  - 同时还锁住 `M4` 继续保持 `partial`、`M5` 继续保持 `partial`、`P-REAL` 继续保持 `todo`，避免后续因为补了文档/校验链就把严格进度误抬高
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_plan_audit.py` 已验证计划审计导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_plan_audit_progress.py` 已验证审计公式和 `85.7 / 75.0` 进度口径仍正确
  - `.\.venv\Scripts\python.exe scripts\verify_current_plan_audit_sync.py` 已验证 `summaryHasCurrentAuditCounts=true`、`summaryShowsExpectedAuditCounts=true`
  - 同一验证已锁住 `m4SectionStillPartial=true`、`m5SectionStillPartial=true`、`prealSectionStillTodo=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_current_real_evidence_remediation_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_remediation_sync.py)，直接锁住当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 的当前补救口径
  - 当前这条校验会同时核对顶部 summary 与关键 provider 分段，确保 `providersNeedingRuntimeSuccess=7`、`providersWithPostBootstrapRuntimeCommand=6`、`providersWithCreateCommand=8`、`providersWithBootstrapCommand=8` 持续与当前 bundle 一致
  - 同时还锁住 `115_open / 189cloud` 继续走 fast-candidate 型 post-bootstrap helper，`quark / baidu_netdisk / xunlei / 123_open` 继续走 live-upload 型 post-bootstrap helper，而 `aliyundrive_open` 当前仍保持 refresh-evidence 路径、不误长出 post-bootstrap helper
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证真实联调补救指南导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_remediation_sync.py` 已验证 `summaryHasCurrentRemediationCounts=true`、`summaryShowsExpectedRuntimeRemediationCounts=true`
  - 同一验证已锁住 `115_open / quark / 189cloud / baidu_netdisk / xunlei / 123_open / aliyundrive_open` 的当前 helper 分流

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增 [scripts/verify_current_real_evidence_status_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_real_evidence_status_sync.py)，直接锁住当前 [docs/10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md) 的 runtime 真实口径
  - 当前这条校验会同时核对顶部 summary 与 provider 分段，确保当前仓库里只有 `guangya / uc / pikpak` 三家被视为 runtime success provider，并确认 `aliyundrive_open / quark / baidu_netdisk / 123_open` 仍是 `0`
  - 这样 `docs/10` 不再只靠上次导出同步和 synthetic export verifier 兜底，后续如果真实状态报告又被误写回旧的 `6`，当前态校验会第一时间报出来
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_report.py` 已验证真实证据状态报告导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_current_real_evidence_status_sync.py` 已验证 `summaryHasCurrentRuntimeCounts=true`、`summaryShowsThreeRuntimeSuccessProviders=true`
  - 同一验证已锁住 `guangya / uc / pikpak` 的 success 分段，以及 `aliyundrive_open / quark / baidu_netdisk / 123_open` 的 no-success 分段

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [docs/06-PROVIDER_STATUS_MATRIX.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/06-PROVIDER_STATUS_MATRIX.md) 已按当前 `task_runtime_evidence_store` 重新导出，回收了旧矩阵把 runtime 统计高估到 `6` 的过期口径
  - 当前 matrix 顶部 summary 已与当前真实 evidence 状态重新一致：`taskRuntimeEvidenceProviderCount / taskRuntimeSampleCount / taskRuntimeSuccessCount / taskRuntimeConflictHandledProviderCount / taskRuntimeConflictHandledCount` 现都收敛到 `3`
  - 已新增 [scripts/verify_current_provider_status_matrix_runtime_sync.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_current_provider_status_matrix_runtime_sync.py)，直接锁住当前导出的 `docs/06` 只能把 `guangya / uc / pikpak` 视为 runtime success provider，并确认 `aliyundrive_open / quark / baidu_netdisk / 123_open` 当前仍是 `0`
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\export_provider_status_matrix.py` 已重导出当前 [docs/06-PROVIDER_STATUS_MATRIX.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/06-PROVIDER_STATUS_MATRIX.md)
  - `.\.venv\Scripts\python.exe scripts\verify_export_provider_status_matrix.py` 已验证 matrix 导出链仍正常
  - `.\.venv\Scripts\python.exe scripts\verify_current_provider_status_matrix_runtime_sync.py` 已验证 `summaryHasCurrentRuntimeCounts=true`、`summaryShowsThreeRuntimeSuccessProviders=true`
  - 同一验证已锁住 `guangya / uc / pikpak` 的 success 行，以及 `aliyundrive_open / quark / baidu_netdisk / 123_open` 的 no-success 行

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 已把 remediation bundle 里四类 helper summary 从“只打印当前值”补成显式 expected-count 断言
  - 当前 bundle 验证现在会单独锁住 `providersWithLiveUploadCommand=3`、`providersWithFastCandidateCommand=3`、`providersWithRuntimeSuccessCommand=4`、`providersWithPostBootstrapRuntimeCommand=5`，并继续校验 API 返回 summary 与 bundle 本体一致
  - [scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py) 也同步补上导出 Markdown 的 `providersWithLiveUploadCommand=4` 与 `providersWithFastCandidateCommand=1` 计数断言，不再只盯 runtime/post-bootstrap 两项
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 `summaryHasExpectedLiveUploadCount=true`、`summaryHasExpectedFastCandidateCount=true`、`summaryHasExpectedRuntimeSuccessCount=true`、`summaryHasExpectedPostBootstrapCount=true`
  - 同一验证已验证 `apiHasExpectedLiveUploadSummaryCount=true`、`apiHasExpectedFastCandidateSummaryCount=true`、`apiHasExpectedRuntimeSuccessSummaryCount=true`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证 `exportedHasLiveUploadSummary=true`、`exportedHasFastCandidateSummary=true`、`exportedHasRuntimeSuccessSummary=true`、`exportedHasPostBootstrapRuntimeSummary=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py) 已把 remediation 面板里另外三类关键动作也拆成专项断言，不再只单独盯 `postBootstrap`
  - 当前 UI 验证现在会单独锁住 summary 里的 `liveUploadCommands / fastCandidateCommands / runtimeSuccessCommands`，以及 provider 简讯里的 `liveUpload / fastCandidate / runtimeSuccess`
  - 这样如果前端后续只回退其中一种 helper 展示，诊断输出也能直接指出是哪一类，而不是继续埋在总布尔里
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证 `jsRemediationSummaryShowsLiveUploadCount=true`、`jsRemediationSummaryShowsFastCandidateCount=true`、`jsRemediationSummaryShowsRuntimeSuccessCount=true`
  - 同一验证已验证 `jsRemediationRowsShowLiveUploadCommand=true`、`jsRemediationRowsShowFastCandidateCommand=true`、`jsRemediationRowsShowRuntimeSuccessCommand=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py) 已补出两个更明确的 `postBootstrap` 专项断言，不再只把相关字段埋在一个超长总布尔里
  - 当前 UI 验证现在会单独锁住设置页 summary 行里的 `postBootstrapRuntimeCommands=...`，以及 provider 简讯里的 `postBootstrapRuntime=...`
  - 这样如果前端以后把 `post-bootstrap` 计数或命令展示回退，诊断输出会更直接，不必再从 `jsSettingsRenderUsesRemediation=false` 里手工拆原因
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_ui.py` 已验证 `jsRemediationSummaryShowsPostBootstrapCount=true`
  - 同一验证已验证 `jsRemediationRowsShowPostBootstrapCommand=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 已进一步收口 synthetic 场景，让 `baidu_netdisk` 也真实进入 post-bootstrap 分支，而不是停留在“已建档不触发 helper”的旧状态
  - 当前 bundle 验证里的 post-bootstrap 汇总已抬到 `5`，并且 `apiHasBaiduPostBootstrapRuntimeCommand` 现在是正向真覆盖，不再是反向占位式判断
  - 这样 `baidu_netdisk` 这条 live-upload 型 post-bootstrap helper 现在同时被导出验证和 bundle 验证覆盖，和当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 保持一致
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 `apiHasBaiduPostBootstrapRuntimeCommand=true`
  - 同一验证已验证 `apiHasPostBootstrapRuntimeSummary=true`，并把该 synthetic 场景下的 post-bootstrap 汇总锁到 `5`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 已补强 synthetic 场景，不再只围绕旧的单个 post-bootstrap helper 走回归
  - 当前 bundle 验证已能同时覆盖 `189cloud` 的 fast-candidate 型 post-bootstrap helper，以及 `quark / xunlei / 123_open` 的 live-upload 型 post-bootstrap helper，并保留 `aliyundrive_open` 的 probe-only、`115_open` 的 candidate-only 路径
  - 这样 remediation bundle 的 API/Markdown 验证也和当前 helper 分流保持一致，不再出现“导出 verifier 已更新，但 bundle verifier 还在旧场景”的割裂
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 `apiHasPostBootstrapRuntimeSummary=true`
  - 同一验证已确认 `markdownHasExpandedPostBootstrapHelpers=true`，并锁住 `apiHasQuarkPostBootstrapRuntimeCommand=true`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [scripts/verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py) 已从旧口径补强到当前 remediation 导出能力，不再只验证单个 `189cloud` post-bootstrap helper
  - 当前导出验证已覆盖 `providersWithPostBootstrapRuntimeCommand = 6` 的摘要口径，并同时锁住 `quark / baidu_netdisk / xunlei / 123_open` 这几条新的 live-helper 型 post-bootstrap runtime 命令
  - 这样 `export_real_evidence_remediation.py` 不再落后于当前代码与文档状态，后续如果 post-bootstrap runtime 覆盖面回退，导出链会第一时间报出来
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出文件包含 `providersWithPostBootstrapRuntimeCommand: 6`
  - 同一验证还已锁住 `tmp\\quark-post-bootstrap-runtime-evidence`、`tmp\\baidu_netdisk-post-bootstrap-runtime-evidence`、`tmp\\xunlei-post-bootstrap-runtime-evidence`、`tmp\\123_open-post-bootstrap-runtime-evidence`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 已把 `recommendedPostBootstrapRuntimeCommand` 从只覆盖 `115_open / 189cloud` 扩到更多已接真实上传链路但当前仍缺 runtime success 的 provider
  - 当前 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 里的 post-bootstrap runtime helper 数量已从 `2` 提升到 `6`，新增覆盖 `quark / baidu_netdisk / xunlei / 123_open`；其中 `115_open / 189cloud` 继续保留 fast-candidate helper，其余新覆盖 provider 直接给 live-upload helper
  - 这样“先建档并 probe，再继续补第一条 runtime success”不再只对两家成立，首批 runtime 缺口更大的几家现在也都有更短的落地命令，离 `P-REAL` 更近了一步
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 `quark / xunlei` 的 post-bootstrap helper 会分流到 `create_live_upload_task.py`，而 `115_open` 仍保持 `create_fast_upload_candidate_task.py --sha1 auto`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证 remediation 导出链仍正常
  - `git diff -- docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md` 已确认 `providersWithPostBootstrapRuntimeCommand` 从 `2` 提升到 `6`，并新增 `quark / baidu_netdisk / xunlei / 123_open` 的命令行

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [docs/10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md) 已按当前 `task_runtime_evidence_store` 重新导出，纠正了旧报告把多条历史 runtime 成功样本高估到 `6` 个 provider 的问题
  - 当前真实证据状态报告已与仓库内现存最新样本对齐：runtime success provider 现明确收敛为 `guangya / uc / pikpak` 三个，`aliyundrive_open / quark / baidu_netdisk / 123_open` 等之前被旧文档写成成功的 provider 已回到“尚无成功样本”的诚实状态
  - 这样 `docs/10` 与 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 的 runtime 口径重新一致，后续继续推进 `P-REAL` 时不会再被旧成功数误导
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_report.py` 已验证 `export_real_evidence_report.py` 导出链仍正常
  - `git diff -- docs/10-REAL_EVIDENCE_STATUS.md` 已确认本次同步把 `task_runtime/runtime_success` 从 `6` 校正到 `3`，并逐个回收旧文档里误记为成功的 provider 行

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [src/cloudpan_sync/real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/real_evidence_remediation.py) 已补强 `nextStep` 生成逻辑：对于 `115_open / 189cloud` 这类会暴露 `recommendedPostBootstrapRuntimeCommand` 的 provider，不再只提示“先建档再 probe”，而是明确要求拿到真实 `profileId` 后立刻继续补第一条 runtime success 样本
  - 这样补救指南从“命令在下面但提示语没跟上”收成了一条更连贯的真实取证链，用户按 `docs/12` 执行时更容易直接推进到 `P-REAL` 所需的 runtime success 证据
  - remediation bundle 与 Markdown 导出验证也已同步锁住这条新口径，避免后续又退回成泛化 next step
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 Markdown/API 中 `189cloud` 的 `recommendedPostBootstrapRuntimeCommand` 对应 `nextStep` 会明确提到 `post-bootstrap runtime helper` 与 `runtime success`
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出的 [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 也保留这条后续动作提示

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 已按当前 `real_evidence_remediation.py` 重新导出，不再停留在旧口径
  - 当前补救指南已同步反映“还缺 runtime success 的 provider”真实数量，并把 `115_open / 189cloud` 的 `recommendedPostBootstrapRuntimeCommand` 一起写回最终 Markdown
  - 这样真实取证补救链不再出现“代码和 verifier 已有新 helper，但仓库内导出文档仍是旧摘要”的割裂，后续按文档执行 `P-REAL` 时会更贴近当前代码状态
- 当前验证证据：
  - `.\.venv\Scripts\python.exe scripts\verify_real_evidence_remediation_bundle.py` 已验证 bundle/API/Markdown 仍带 `recommendedRuntimeSuccessCommand / recommendedPostBootstrapRuntimeCommand` 等字段
  - `.\.venv\Scripts\python.exe scripts\verify_export_real_evidence_remediation.py` 已验证导出链会把新的 runtime success / post-bootstrap runtime 字段写入最终 Markdown
  - `git diff -- docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md` 已确认本次同步把 `providersNeedingRuntimeSuccess` 从 `2` 校正到 `7`，并补出 `providersWithPostBootstrapRuntimeCommand: 2`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [verify_create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task.py) 已从“验证能自动解析 parentId 并落 evidence bundle”补强为同时覆盖显式 `--target-parent-id` 覆盖自动解析、`--no-refresh-auth-evidence` 分支，以及 `--no-acknowledge-download-upload`
  - 当前 `create_live_upload_task.py` 这条 helper 不再只锁默认 happy path，还会验证“明确指定目标目录”“只导出 auth evidence、不刷新最新证据”以及“显式关闭 download_upload 风险确认”这几类实际使用场景
  - 这样 `recommendedLiveUploadCommand / recommendedRuntimeSuccessCommand` 走 live helper 时也有更完整的边界回归保护
- 当前验证证据：
  - [verify_create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task.py) 已验证显式 `--target-parent-id manual-live-parent` 会覆盖已保存档案里的解析结果
  - 同一验证已锁住 `--no-refresh-auth-evidence` 时不会再次刷新 auth evidence，显式 `--task-json-output / --auth-evidence-output` 都会真实落盘，并确认 `--no-acknowledge-download-upload` 会把 `acknowledgedDownloadUpload` 关闭

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [verify_create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_candidate_task.py) 已从“验证能自动解析 parentId 并落 evidence bundle”补强为同时覆盖显式 `--target-parent-id` 覆盖自动解析，以及 `--no-refresh-auth-evidence` 分支
  - 当前 `create_fast_upload_candidate_task.py` 这条 helper 不再只锁默认 happy path，还会验证“明确指定目标目录”与“只导出 auth evidence、不刷新最新证据”这两类实际使用场景
  - 这样 `recommendedFastCandidateCommand / recommendedRuntimeSuccessCommand` 走 fast helper 时也有更完整的边界回归保护
- 当前验证证据：
  - [verify_create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_candidate_task.py) 已验证显式 `--target-parent-id manual-fast-parent` 会覆盖已保存档案里的解析结果
  - 同一验证已锁住 `--no-refresh-auth-evidence` 时不会再次刷新 auth evidence，并且显式 `--task-json-output / --auth-evidence-output` 都会真实落盘

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [verify_create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_runtime_probe_task.py) 已从“验证能自动解析 parentId 并落 evidence bundle”补强为同时覆盖显式 `--target-parent-id` 覆盖自动解析，以及 `--no-refresh-auth-evidence` 分支
  - 当前 `create_runtime_probe_task.py` 这条 helper 不再只锁默认 happy path，还会验证“明确指定目标目录”与“只导出 auth evidence、不刷新最新证据”这两类实际使用场景
  - 这样 `recommendedRuntimeProbeCommand` 对应的落地动作现在也有更完整的边界回归保护
- 当前验证证据：
  - [verify_create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_runtime_probe_task.py) 已验证显式 `--target-parent-id manual-parent` 会覆盖已保存档案里的解析结果
  - 同一验证已锁住 `--no-refresh-auth-evidence` 时不会再次刷新 auth evidence，并且显式 `--task-json-output / --auth-evidence-output` 都会真实落盘

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [verify_patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_and_probe_auth_profile.py) 已从“验证能补字段并刷新一条 probe”补强为同时覆盖 `--dir-name / --page-size` 透传、CLI JSON 输出，以及缺失 profile 的诚实报错
  - 当前 `patch_and_probe_auth_profile.py` 这条 helper 不再只锁 happy path，还会验证“补字段并立即留证”和“零补字段仅刷新证据”两条实际使用路径
  - 这样 `recommendedPatchProbeCommand / recommendedRefreshEvidenceCommand` 对应的两类落地动作现在都有更完整的回归保护
- 当前验证证据：
  - [verify_patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_and_probe_auth_profile.py) 已验证 `dirName=verify-dir / pageSize=7` 会真实透传到 live probe 调用，且首轮 CLI JSON 会带 `written / validation / probe / evidenceOutput`
  - 同一验证已锁住“零补字段仅刷新证据”仍可工作，以及缺失 profile 时会抛出 `profile_not_found: missing-profile`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [verify_create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_auth_profile_stub.py) 已从“只验证能建出档案”补强为覆盖 `--probe / --evidence-output / CLOUDPAN_SYNC_DATA_DIR`
  - 当前 `create_auth_profile_stub.py` 这条 helper 不再只验证最基础的保存动作，还会锁住“建档案后立刻刷新 validation/probe 证据并输出单档案 Markdown”这条真实取证起手路径
  - 这样 `recommendedCreateCommand / recommendedBootstrapCommand` 对应的两个落地阶段现在都有更贴近真实使用方式的回归保护
- 当前验证证据：
  - [verify_create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_auth_profile_stub.py) 已验证环境变量 `CLOUDPAN_SYNC_DATA_DIR` 会被消费，且 `domainId / driveId` 等 extra 字段会随建档案结果一起写入输出 JSON
  - 同一验证已锁住 `--probe` 返回的 evidence 摘要，以及 `--evidence-output` 会真实落出 `Auth Profile Evidence` Markdown 文件

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - `real_evidence_remediation.py` 现已新增 `recommendedPostBootstrapRuntimeCommand` 与 `providersWithPostBootstrapRuntimeCommand`：针对 `115_open / 189cloud` 这类“当前还没 profile、但后续一定还要补 runtime success”的 provider，补救指南不再只停在 `create_auth_profile_stub.py --probe`
  - 当前 `Real Evidence Remediation` 会在“先建档案/跑 probe”之后，继续直接给出下一条占位式 runtime helper，提示用户在拿到真实 `profileId` 后如何立刻进入 `create_fast_upload_candidate_task.py` 收集真实 runtime 样本
  - settings 页 remediation 简讯、Markdown 导出与 API bundle 现在都已同步带出这条字段，真实取证准备链路从“建档案”延伸到了“建完后怎么继续跑 runtime”
- 当前验证证据：
  - [verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 已验证 bundle/API/Markdown 都带 `recommendedPostBootstrapRuntimeCommand` 与 `providersWithPostBootstrapRuntimeCommand`
  - [verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py) 已验证 `12-REAL_EVIDENCE_REMEDIATION_GUIDE.md` 导出文件包含新的 summary 与 `189cloud` 的 post-bootstrap runtime helper
  - [verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py) 已验证 settings 页 remediation 面板已消费 `recommendedPostBootstrapRuntimeCommand / providersWithPostBootstrapRuntimeCommand`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - [verify_patch_refresh_export_auth_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_refresh_export_auth_bundle.py) 已进一步补强，不再只验证“批量补字段后能落文件”，还会同时校验 selector 命中范围、非命中档案不被误改，以及 CLI 输出 JSON 摘要
  - 当前 `patch_refresh_export_auth_bundle.py` 这条“批量补档案 -> 刷新 evidence -> 导出 bundle”链路，已经同时锁住选择器过滤、副作用边界和输出摘要，不再只覆盖 happy path
  - 这样批量 patch/export helper 的验收口径也更接近真实使用场景：既要改对命中的档案，也要保证不会误伤旁边的其他 provider/profile
- 当前验证证据：
  - [verify_patch_refresh_export_auth_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_refresh_export_auth_bundle.py) 已验证 `providerKey=guangya + displayName contains smoke` 只会命中 `gy-batch-1 / gy-batch-2`
  - 同一验证已锁住 `bundleSummary / profileIds / bundleOutput` JSON 输出，以及未命中的 `aliyundrive_open` 档案不会被误写入 `parentId/fileId`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增独立导出验证脚本 [verify_export_local_live_adapter_verification.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_local_live_adapter_verification.py)，把 `07-LOCAL_LIVE_ADAPTER_VERIFICATION.md` 这条本地 live adapter 导出链锁进回归
  - 当前 local live adapter 报告现在不只验证文件存在，还覆盖了顶部“stub 验证、不等同真实在线成功”的提示文案、provider 分段、Probe Checks 与 Matrix Rows 聚合结果
  - 这样本地 adapter 验证报告也已补齐为独立 export verifier，不再只依赖 `verify_provider_live_adapters.py` 本身的 JSON 输出人工对账
- 当前验证证据：
  - [verify_export_local_live_adapter_verification.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_local_live_adapter_verification.py) 已验证导出文件包含标题和两条提示文案
  - 同一验证已锁住 `guangya / 189cloud` 的 provider 行、`Probe Checks` 摘要以及 `Matrix Rows` 中的 readiness / live_probe_ok 聚合结果

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增独立验证脚本 [verify_export_auth_profile_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_profile_evidence.py)，把 `export_auth_profile_evidence.py` 这条单 profile CLI 导出链锁进回归
  - 当前 auth profile evidence 入口现在不只验证“能不能跑”，还覆盖了 `--data-dir` 配置、`--output` 文件导出，以及 profile 缺失时的诚实报错
  - 至此 `auth` 相关几条主要导出链已全部具备独立 verifier：`auth live validation / auth evidence bundle / auth remediation bundle / auth profile evidence`
- 当前验证证据：
  - [verify_export_auth_profile_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_profile_evidence.py) 已验证 `--data-dir` 会调用 `configure_data_dir()`，命中 profile 时会输出 `Auth Profile Evidence` Markdown 到指定 `--output`
  - 同一验证已锁住 `189cloud` 只读 share 档案的 `missingFieldHints / writeMissingFieldHints / writeBlockerNote / Latest Validation / Latest Probe`，并验证缺失 profile 时会抛出 `profile_not_found: missing-profile`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增独立导出验证脚本 [verify_export_auth_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_remediation_bundle.py)，把 `09-AUTH_REMEDIATION_GUIDE.md` 的摘要统计、profile 级缺口、只读写阻断说明与推荐 patch 命令锁进回归
  - 当前 auth remediation bundle 导出链现在也具备与 `auth evidence bundle / auth live validation / live probe / plan audit / provider status / real evidence / task runtime` 同级的独立 export verifier
  - 这条验证同时覆盖了“普通缺字段修补”和“189Cloud share 只读补救”两类补救路径，避免导出链只锁最简单的 remediation 文案
- 当前验证证据：
  - [verify_export_auth_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_remediation_bundle.py) 已验证导出文件包含 `profileCount / readyCount / needsFixCount / writeReadyCount / writeNeedsFixCount`
  - 同一验证已锁住 `aliyundrive_open` 的 `missingFieldHints + recommendedPatchCommand`，以及 `189cloud` 的 `writeMissingFieldHints / writeBlockerNote / recommendedPatchCommand`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - 已新增独立导出验证脚本 [verify_export_auth_evidence_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_evidence_bundle.py)，把 `08-AUTH_EVIDENCE_BUNDLE.md` 的摘要统计、profile 行、鉴权缺口提示、写阻断说明与 latest validation/probe 摘要锁进回归
  - 当前 auth evidence bundle 导出链现在也具备与 `auth live validation / live probe / plan audit / provider status / real evidence / task runtime` 同级的独立 export verifier，不再只靠人工打开 Markdown 对账
  - 这条验证同时覆盖“可写成功档案”和“只读受阻档案”两类代表性场景，避免导出链只锁 happy path
- 当前验证证据：
  - [verify_export_auth_evidence_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_evidence_bundle.py) 已验证导出文件包含 `profileCount / profileReadyCount / writeReadyCount / validationOkCount / probeOkCount`
  - 同一验证已锁住 `guangya` 的 ready profile 行，以及 `189cloud` 的 `missingFieldHints / writeMissingFieldHints / writeBlockerNote / latestValidation / latestProbe`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - `export_auth_live_validation_report.py` 现已统一使用模块级 `ROOT` 输出 `docs/03-AUTH_LIVE_VALIDATION_REPORT.md`，不再在 `main()` 内重复按 `__file__` 计算根目录；这样和其余导出脚本保持一致，也能被临时目录 verifier 稳定接管
  - 已新增独立导出验证脚本 [verify_export_auth_live_validation_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_live_validation_report.py)，把 auth live validation 导出链的标题、摘要、Latest By Profile 和 Recent History 关键字段锁进回归
  - 当前 auth live validation 报告导出链现在也具备与 `plan audit / provider status / real evidence / task runtime / live probe` 同级的独立 export verifier
- 当前验证证据：
  - [verify_export_auth_live_validation_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_auth_live_validation_report.py) 已验证导出文件包含 `totalRecords / latestProfileCount / latestOkCount / latestFailedCount / latestProviders`
  - 同一验证已锁住 `guangya` 的成功型 latest row、`189cloud` 的失败型 latest row，以及 Recent History 中的 `probeArgs / endpoint / finalUrl / checkCount`

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - `export_live_probe_report.py` 现已收口到统一的模块级 `ROOT` 输出路径，不再在 `main()` 里重新按 `__file__` 计算根目录；这样和仓库里其余导出脚本保持一致，也能被临时目录 verifier 稳定接管
  - 已新增独立导出验证脚本 [verify_export_live_probe_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_live_probe_report.py)，把 `05-PROVIDER_LIVE_PROBE_REPORT.md` 的标题、摘要统计、provider 检查行以及 `profile_probe` 行锁进回归
  - 当前 live probe 导出链现在不只依赖运行时人工查看，已经具备和 `plan audit / provider status / real evidence / task runtime` 同类的独立 export verifier
- 当前验证证据：
  - [verify_export_live_probe_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_live_probe_report.py) 已验证导出文件包含 `providerCount / totalChecks / okChecks / failedChecks / profileProbeProviderCount / profileProbeOkCount / profileProbeFailedCount`
  - 同一验证已锁住 `guangya` 的 `official_docs / web_login` 检查行、`189cloud` 的失败型 `profile_probe` 行，以及 `115_open` 在 `checkCount=0` 时不会误写空 `profile_probe` 行

### 已完成补齐项 - `2026-05-25`

- 提交：`本次提交`
- 完成范围：
  - `xunlei` 的 `download_upload` 已从 `create_dir` 写探针升级为真实本地文件上传：运行期会复用现有 `create-by-hash -> resumable binary fallback` 链路，命中 hash miss 时继续完成二进制上传，而不是再退回 mock/download fallback
  - `pikpak` 的 `download_upload` 也已同样升级为真实本地文件上传：运行期会复用现有 `create-by-hash -> resumable binary fallback` 链路，命中 hash miss 时继续完成二进制上传
  - 两条链路现在都已补上同名文件冲突策略：`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名，并把 `resolvedTargetName / conflictAction` 写入任务结果与 `task_runtime_evidence`
  - provider registry / planner / runtime 口径已同步对齐：`xunlei`、`pikpak` 现在都声明支持 `overwrite_existing / auto_rename_new`，其中 overwrite 会落成 `downgrade_to_auto_rename`
- 当前验证证据：
  - [verify_xunlei_pikpak_fast_upload_conflict_policy.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_xunlei_pikpak_fast_upload_conflict_policy.py) 已验证 `xunlei / pikpak` 在目标目录已有同名文件时，会把请求名改成 `demo (1).bin`，并返回 `conflictAction=overwrite_downgraded_to_auto_rename`
  - [verify_xunlei_pikpak_download_upload_runtime.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_xunlei_pikpak_download_upload_runtime.py) 已验证 `download_upload` 任务运行会产出 `executionMode=live`、`completionKind=real_transfer`、`liveAttempt.mode=binary_upload_after_hash_miss`，并把 `resolvedTargetName / conflictAction / verifyMode` 写入运行期证据

### 已完成补齐项 - `2026-05-25`（Quark）

- 提交：`本次提交`
- 完成范围：
  - `quark` 的 `download_upload` 已从 `create_dir` 写探针升级为真实本地文件上传：运行期会复用现有 `upload/pre -> update/hash -> upload/auth -> multipart PUT -> commit -> upload/finish` 链路，命中 hash miss 时继续完成二进制上传，而不是再退回 mock/download fallback
  - `quark` 现已补上同名文件冲突策略：`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名，并把 `resolvedTargetName / conflictAction` 写入任务结果与 `task_runtime_evidence`
  - provider registry / planner / runtime / research note 口径已同步对齐：`quark` 现在声明支持 `overwrite_existing / auto_rename_new`，其中 overwrite 会落成 `downgrade_to_auto_rename`
- 当前验证证据：
  - [verify_quark_fast_upload_conflict_policy.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_quark_fast_upload_conflict_policy.py) 已验证 Quark 在目标目录已有同名文件时，会把请求名改成 `demo (1).bin`，并返回 `conflictAction=overwrite_downgraded_to_auto_rename`
  - [verify_quark_download_upload_runtime.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_quark_download_upload_runtime.py) 已验证 `download_upload` 任务运行会产出 `executionMode=live`、`completionKind=real_transfer`、`liveAttempt.mode=binary_upload_after_hash_miss`，并把 `resolvedTargetName / conflictAction / verifyMode` 写入运行期证据

### 已完成补齐项 - `2026-05-25`（UC）

- 提交：`本次提交`
- 完成范围：
  - `uc` 的 `download_upload` 已从 `create_dir` 写探针升级为真实本地文件上传：运行期会复用现有 `upload/pre -> update/hash -> upload/auth -> multipart PUT -> commit -> upload/finish` 链路，命中 hash miss 时继续完成二进制上传，而不是再退回 mock/download fallback
  - `uc` 现已补上同名文件冲突策略：`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名，并把 `resolvedTargetName / conflictAction` 写入任务结果与 `task_runtime_evidence`
  - provider registry / planner / runtime / research note 口径已同步对齐：`uc` 现在声明支持 `overwrite_existing / auto_rename_new`，其中 overwrite 会落成 `downgrade_to_auto_rename`
- 当前验证证据：
  - [verify_uc_fast_upload_conflict_policy.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_uc_fast_upload_conflict_policy.py) 已验证 UC 在目标目录已有同名文件时，会把请求名改成 `demo (1).bin`，并返回 `conflictAction=overwrite_downgraded_to_auto_rename`
  - [verify_uc_download_upload_runtime.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_uc_download_upload_runtime.py) 已验证 `download_upload` 任务运行会产出 `executionMode=live`、`completionKind=real_transfer`、`liveAttempt.mode=binary_upload_after_hash_miss`，并把 `resolvedTargetName / conflictAction / verifyMode` 写入运行期证据

### 已完成补齐项 - `2026-05-25`（189Cloud）

- 提交：`本次提交`
- 完成范围：
  - `189cloud` 的 `fast_upload` 已从“只尝试 `createUploadFile -> fileCommitUrl` 秒传命中”升级为完整本地文件上传链路：当 `fileDataExists != 1` 时，会继续走 `fileUploadUrl PUT -> getUploadFileStatus -> fileCommitUrl`
  - 该链路现在会把 `binaryUploadResponse / statusResponse / statusView / commitResponse` 写入 payload，运行期可区分“命中秒传”和“hash miss 后已完成二进制上传”
  - 当前成功校验口径仍保持诚实：本轮是依据 provider 的最终 commit XML 回包确认上传成功，不伪装成目录回查或已有真实在线样本
- 当前验证证据：
  - [verify_189cloud_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_fast_upload_live.py) 已验证 `fileDataExists=1` 时会走 `rapid_upload_by_hash`，并以 `commit_response_xml` 作为成功校验
  - [verify_189cloud_fast_upload_binary_fallback.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_fast_upload_binary_fallback.py) 已验证 `fileDataExists=0` 时会继续执行 `fileUploadUrl PUT -> getUploadFileStatus -> fileCommitUrl`，并返回 `mode=binary_upload_put_then_commit`、`verifyMode=commit_response_xml_after_binary_put`

### 已完成补齐项 - `2026-05-25`（115 Open）

- 提交：`本次提交`
- 完成范围：
  - `115_open` 的 `fast_upload` 已从“只尝试 `open/upload/init + sign_check` 秒传命中”升级为完整本地文件上传链路：当秒传未命中时，会继续执行 `upload/get_token + OSS binary upload`
  - 当前 fallback 已同时覆盖单分片与 multipart 两种 OSS 上传路径，并把 `uploadTokenResponse / uploadSession / binaryUpload` 写入 payload，运行期可区分“命中秒传”和“hash miss 后已完成二进制上传”
  - 当前成功校验口径仍保持诚实：本轮是依据上传后的 `metadata_by_file_id / list_by_parent_name` 回查结果确认成功，不伪装成已有真实在线样本
- 当前验证证据：
  - [verify_115_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_115_fast_upload_live.py) 已验证 `status=7 -> sign_check -> status=2` 的秒传命中路径仍然成立，并返回 `mode=rapid_upload_by_hash`
  - [verify_115_fast_upload_binary_fallback.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_115_fast_upload_binary_fallback.py) 已验证 hash miss 时会继续请求 `upload/get_token` 并执行 OSS 上传，返回 `mode=binary_upload_after_hash_miss`、`verifyMode=list_by_parent_name`

### 已完成补齐项 - `2026-05-25`（Live Helper 覆盖补齐）

- 提交：`本次提交`
- 完成范围：
  - 统一真实取证 helper [create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_live_upload_task.py) 现已从 `guangya / aliyundrive_open / 123_open / baidu_netdisk` 扩展到 `xunlei / pikpak / quark / uc`
  - 这 4 个 provider 现在也可以直接通过同一条 helper 命令生成固定 evidence bundle：`task.json / task.md / auth_evidence.md / runtime_evidence.md / real_evidence.md / remediation.md`
  - `real_evidence_remediation.py` 的下一步建议也已同步对齐：当这些 provider 已具备基础 auth/list/metadata/create_dir 证据但仍缺 runtime success 时，不再只给出 generic fast candidate 提示，而是可以给出统一 live upload helper 命令
- 当前验证证据：
  - [verify_create_live_upload_task_xunlei_pikpak.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task_xunlei_pikpak.py) 已验证 `create_live_upload_task.py` 对 `xunlei / pikpak` 会产出 `state=completed`、`completionKind=real_transfer`、`hasRealTransferSuccess=true`，并写出固定文件名 evidence bundle
  - [verify_create_live_upload_task_quark_uc.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task_quark_uc.py) 已验证 `create_live_upload_task.py` 对 `quark / uc` 会产出 `state=completed`、`completionKind=real_transfer`、`hasRealTransferSuccess=true`，并写出固定文件名 evidence bundle
  - [verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 已继续验证 remediation markdown/API 仍能正常生成，并保留 `recommendedLiveUploadCommand / recommendedFastCandidateCommand / recommendedRuntimeProbeCommand` 等字段

### 已完成补齐项 - `2026-05-25`（Runtime Success 命令收口）

- 提交：`本次提交`
- 完成范围：
  - `real_evidence_remediation.py` 现已新增统一字段 `recommendedRuntimeSuccessCommand`，用于给“基础证据已齐但还缺 runtime success”的 provider 直接推荐下一条最应该跑的真实成功命令
  - 该字段会优先选择 `create_live_upload_task.py`，若当前 provider 没有 live helper 但已经具备 fast/runtime 上传链路，则会自动回退到 `create_fast_upload_candidate_task.py`
  - 这样 `115_open / 189cloud` 这类 fast provider 也不再只有 generic 文案，而能拿到更直接的下一步命令；`guangya / xunlei / pikpak / quark / uc` 等 provider 则继续优先走统一 live helper
- 当前验证证据：
  - [verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 已验证 remediation summary 现新增 `providersWithRuntimeSuccessCommand`
  - 同一脚本还验证了 `115_open` 会把 `recommendedRuntimeSuccessCommand` 回退到 `create_fast_upload_candidate_task.py`，而 `guangya` 会优先保留 `create_live_upload_task.py`
  - [docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md) 已随导出同步带出新的 `recommendedRuntimeSuccessCommand` 字段

### 已完成补齐项 - `2026-05-25`（115/189 Fast Helper 取证覆盖）

- 提交：`本次提交`
- 完成范围：
  - 已新增 [verify_create_fast_upload_task_115.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_task_115.py)，补齐 `115_open` 在统一 helper `create_fast_upload_candidate_task.py` 下的 real-transfer evidence bundle 验证
  - 已新增 [verify_create_fast_upload_task_189cloud.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_task_189cloud.py)，补齐 `189cloud` 在统一 helper 下的 real-transfer evidence bundle 验证
  - 两个 fast provider 现在都已有与 `quark / uc` 同口径的 helper 级回归脚本，可直接验证 helper 会把 live result 收口为 `state=completed`、`completionKind=real_transfer`、`hasRealTransferSuccess=true`，并稳定写出固定文件名 evidence bundle
- 当前验证证据：
  - [verify_create_fast_upload_task_115.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_task_115.py) 已验证 `create_fast_upload_candidate_task.py --target-provider 115_open --auto-temp-file --sha1 auto` 会产出 `executionMode=live`、`verifyMode=metadata_by_file_id` 的 real-transfer 结果，并落出 `task.json / task.md / runtime_evidence.md`
  - [verify_create_fast_upload_task_189cloud.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_task_189cloud.py) 已验证 `create_fast_upload_candidate_task.py --target-provider 189cloud --auto-temp-file` 会产出 `executionMode=live`、`verifyMode=commit_response_xml` 的 real-transfer 结果，并落出 `task.json / task.md / runtime_evidence.md`

### 已完成补齐项 - `2026-05-25`（Runtime Success 设置页收口）

- 提交：`本次提交`
- 完成范围：
  - settings 页 `Real Evidence Remediation` 摘要现已补上 `providersWithRuntimeSuccessCommand` 聚合计数，不再只有后端 summary 和 Markdown 导出知道这条字段
  - settings 页 remediation provider 简讯现也已直接展示 `recommendedRuntimeSuccessCommand`，这样 `115_open / 189cloud` 这类 provider 在前端就能直接看到下一条推荐的真实成功命令，不必再只去翻导出文档
  - 前端 remediation 收口口径现在已与后端 `real_evidence_remediation.py`、导出文档 `12-REAL_EVIDENCE_REMEDIATION_GUIDE.md` 保持一致
- 当前验证证据：
  - [verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py) 已验证 settings 页 remediation 面板会消费 `recommendedRuntimeSuccessCommand / providersWithRuntimeSuccessCommand`

### 已完成补齐项 - `2026-05-25`（Runtime Success 导出链补齐）

- 提交：`本次提交`
- 完成范围：
  - 已新增 [verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py)，补齐 `export_real_evidence_remediation.py` 的落盘导出验证
  - 该验证现在会直接跑导出脚本，把 `12-REAL_EVIDENCE_REMEDIATION_GUIDE.md` 写到临时目录，并确认 `providersWithRuntimeSuccessCommand` 与每个 provider 的 `recommendedRuntimeSuccessCommand` 都确实进入最终 Markdown，而不只是停留在 bundle/API/UI
  - 这样 `real_evidence_remediation.py` 这条链路现在已经覆盖到 bundle、settings UI 和 Markdown export 三个出口
- 当前验证证据：
  - [verify_export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_remediation.py) 已验证导出文件包含 `providersWithRuntimeSuccessCommand` 汇总、`guangya` 的 live helper 型 `recommendedRuntimeSuccessCommand`、`115_open` 的 fast helper 型 `recommendedRuntimeSuccessCommand`，并保留 `runtimeCandidateOnly=True` 标记

### 已完成补齐项 - `2026-05-25`（Runtime Success API 验证补强）

- 提交：`本次提交`
- 完成范围：
  - 已补强 [verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py)，不再只校验 remediation bundle 的内存结果和 Markdown 标题
  - 该脚本现在会把 synthetic remediation bundle 直接挂到 `webapp` 的 `GET /api/real_evidence_remediation_bundle` 与 `GET /api/real_evidence_remediation_markdown` 路径上，明确验证 API summary 里也带 `providersWithRuntimeSuccessCommand`
  - 同一验证还会继续检查 provider 级 API item：`guangya` 会暴露 live helper 型 `recommendedRuntimeSuccessCommand`，`115_open` 会暴露 fast helper 型 `recommendedRuntimeSuccessCommand`，并确认 Markdown API 端也保留该字段
- 当前验证证据：
  - [verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 已验证 API summary / item / markdown 三条出口都会带 `recommendedRuntimeSuccessCommand` 相关字段

### 已完成补齐项 - `2026-05-25`（Live Helper 证据包验证补强）

- 提交：`本次提交`
- 完成范围：
  - 已补强 [verify_create_live_upload_task_xunlei_pikpak.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task_xunlei_pikpak.py) 与 [verify_create_live_upload_task_quark_uc.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task_quark_uc.py)
  - 这两组 grouped verifier 现在不再只盯 `task.json / task.md / runtime_evidence.md`，而是和 Guangya 那条 helper 验证对齐，明确要求 `auth_evidence.md / real_evidence.md / remediation.md` 也同时产出并具备正确标题
  - `xunlei / pikpak / quark / uc` 这四个 provider 的统一 live helper 现在都已有“6 份固定文件名证据包”级别的回归保护
- 当前验证证据：
  - [verify_create_live_upload_task_xunlei_pikpak.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task_xunlei_pikpak.py) 已验证 `xunlei / pikpak` 的 helper 证据包同时包含 `task.json / task.md / auth_evidence.md / runtime_evidence.md / real_evidence.md / remediation.md`
  - [verify_create_live_upload_task_quark_uc.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task_quark_uc.py) 已验证 `quark / uc` 的 helper 证据包也同样满足 6 份固定文件名与标题校验

### 已完成补齐项 - `2026-05-25`（Real Evidence 导出链验证补齐）

- 提交：`本次提交`
- 完成范围：
  - 已新增 [verify_export_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_report.py)，补齐 `export_real_evidence_report.py` 的落盘导出验证
  - 该验证会直接跑导出脚本，把 `10-REAL_EVIDENCE_STATUS.md` 写到临时目录，并确认最终 Markdown 里真实保留 `runtime_success / runtime_failed / runtime_candidate / runtime_probe / runtime_blocked` 等 runtime 统计
  - 同时也会继续校验 provider 级内容：既能看到 `guangya` 的 success 样本行，也能看到 `189cloud` 的 mixed runtime 行与 gap 文案，避免导出链只剩标题和总表
- 当前验证证据：
  - [verify_export_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_real_evidence_report.py) 已验证导出文件包含运行期 summary 统计、provider 级 runtime 明细和 gap 文案

### 已完成补齐项 - `2026-05-25`（Task Runtime Evidence 导出链验证补齐）

- 提交：`本次提交`
- 完成范围：
  - 已新增 [verify_export_task_runtime_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_task_runtime_evidence_report.py)，补齐 `export_task_runtime_evidence_report.py` 的落盘导出验证
  - 该验证会直接跑导出脚本，把 `11-TASK_RUNTIME_EVIDENCE.md` 写到临时目录，并确认最终 Markdown 里真实保留 `blocked / candidateOnly / probeOnly / conflictHandled` 等关键 runtime 样本与汇总统计
  - 这样 `task_runtime_evidence` 这条链路现在也已经覆盖到 API 与 Markdown export 两个出口，不再只验证在线接口
- 当前验证证据：
  - [verify_export_task_runtime_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_task_runtime_evidence_report.py) 已验证导出文件包含 summary 统计、blocked 行、candidate 行、probe 行和 conflictHandled 行

### 已完成补齐项 - `2026-05-25`（Provider Status Matrix 导出链验证补齐）

- 提交：`本次提交`
- 完成范围：
  - 已新增 [verify_export_provider_status_matrix.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_provider_status_matrix.py)，补齐 `export_provider_status_matrix.py` 的落盘导出验证
  - 该验证会直接跑导出脚本，把 `06-PROVIDER_STATUS_MATRIX.md` 写到临时目录，并确认最终 Markdown 里不只保留 summary，还保留 provider 主行、`runtime_note` 行、`overwrite_note / auto_rename_note / note` 行
  - 这样 `provider_status_matrix` 这条链路现在也已经覆盖到 API、settings UI 和 Markdown export 三个出口，不再只验证在线接口与页面摘要
- 当前验证证据：
  - [verify_export_provider_status_matrix.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_provider_status_matrix.py) 已验证导出文件包含 summary 统计、`guangya/189cloud` provider 行、runtime note 行和冲突 note 行

### 已完成补齐项 - `2026-05-25`（Plan Audit 导出链验证补齐）

- 提交：`本次提交`
- 完成范围：
  - 已新增 [verify_export_plan_audit.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_plan_audit.py)，补齐 `export_plan_audit.py` 的落盘导出验证
  - 该验证会直接跑导出脚本，把 `04-PLAN_AUDIT_REPORT.md` 写到临时目录，并确认最终 Markdown 里真实保留 `done / partial / todo`、`featureCompletionPercent / strictCompletionPercent`、公式说明以及关键里程碑状态行
  - 这样计划审计这条链路现在也已经覆盖到 API、settings UI 和 Markdown export 三个出口，不再只验证在线摘要
- 当前验证证据：
  - [verify_export_plan_audit.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_plan_audit.py) 已验证导出文件包含 summary、双口径进度、公式说明、provider 覆盖统计以及 `M5 / P-REAL` 状态行

### M1 - 独立项目骨架

- 完成日期：`2026-05-23`
- 提交：`46a20a3`
- 完成范围：
  - FastAPI 后端与静态前端骨架
  - 本地管理员密码登录保护
  - 中英 i18n 基础接口
  - Windows 启动脚本（`pwsh` 优先，PowerShell 回退）
- 当前验证证据：
  - `GET /api/health` 返回 `{"status":"ok"}`
  - `POST /api/login` 默认密码 `admin123` 可登录
  - `GET /api/session` 登录后返回 `{"loggedIn":true}`

### M2 - 适配器与能力模型

- 完成日期：`2026-05-23`
- 提交：`a456f54`
- 完成范围：
  - `ProviderAdapter` 抽象与 `ProviderProfile` 模型
  - `FingerprintSet` 模型与归一化输出：已统一收口 `md5 / sha1 / sha256 / crc64 / gcid / etag / pickcode / blockListMd5 / raw`
  - provider registry API
  - mock 互传规划 API
- 当前验证证据：
  - `GET /api/providers` 返回 `providerCount=10`
  - `POST /api/plan/mock` 返回策略明细、分组与统计
  - [verify_fingerprint_set_normalization.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_fingerprint_set_normalization.py) 已验证 `POST /api/plan/mock` 会返回标准化 `normalizedFingerprints`，例如把原始 `MD5/etag/pickCode/block_list_md5` 归一化成统一字段，并返回 `availableFastInputs`

### M3 - 授权系统

- 完成日期：`2026-05-23`
- 提交：`0e0f7ed`
- 完成范围：
  - `AuthProfile` 模型与本地授权存储
  - 授权 API：新增、查询、删除、校验
  - 网页登录抓取引导 API（`capture_pending`）
  - 授权信息脱敏显示
  - 认证校验已升级为 provider-aware 最小 live validation：不再只检查 token/cookie 是否非空，而是优先走对应 provider 的最小 live probe
  - Guangya 认证校验默认参数已补别名兼容：`parent_id / parentFileId / dirId / pid` 可映射为 `parentId`，`file_id / resId` 可映射为 `fileId`
  - 授权列表接口现在会直接返回 provider-aware `missingFieldHints / profileReady`，可在未点击 validate 前先暴露档案缺口
  - 授权列表接口现在还会返回 `resolvedParentId / resolvedFileId`，任务表单与 live probe 可直接复用解析后的默认值，不必依赖录入时使用的具体字段名
  - 已支持编辑现有 auth profile 并重新校验；补 Guangya `parentId` 这类字段时无需删除重建，`token/cookie` 留空会保留原值
  - 已新增本地脚本 [patch_auth_profile_extra.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/patch_auth_profile_extra.py)，可按 `profileId / providerKey / displayName` 选择已有档案，安全补写 `extra.parentId / fileId / did / dt` 等字段，并可选立即重验后写回状态
  - 已新增一键脚本 [patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/patch_and_probe_auth_profile.py)，可在补写现有档案字段后立刻串行执行 provider-aware validation 与 live probe，并在需要时把验证/探测结果一起落盘，方便为真实 Guangya 样例留证据
  - 已新增单档案证据摘要接口 `GET /api/auth/profiles/{id}/evidence`、Markdown 接口 `GET /api/auth/profiles/{id}/evidence_markdown`、刷新接口 `POST /api/auth/profiles/{id}/refresh_evidence` 与导出脚本 [export_auth_profile_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_auth_profile_evidence.py)，可把 profile readiness、最新 validation、最新 probe 汇总成单份 Markdown 证据，并在需要时先重跑 validation/probe
  - [patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/patch_and_probe_auth_profile.py) 现已支持 `--evidence-output`，可在补字段、重验、live probe 后直接输出单档案证据 Markdown 文件
  - 已新增 auth evidence bundle 接口 `GET /api/auth/evidence_bundle`、Markdown 接口 `GET /api/auth/evidence_bundle_markdown`、刷新接口 `POST /api/auth/refresh_evidence_bundle` 与导出脚本 [export_auth_evidence_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_auth_evidence_bundle.py)，可汇总当前全部已保存 auth profile 的 readiness / validation / probe 证据到 [08-AUTH_EVIDENCE_BUNDLE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/08-AUTH_EVIDENCE_BUNDLE.md)，并在需要时先重跑全部 profile 的 validation/probe
  - 已新增批量脚本 [patch_refresh_export_auth_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/patch_refresh_export_auth_bundle.py)，可按 `profileId/providerKey/displayName` 选择一批已保存档案，统一补字段、刷新 evidence bundle，并直接导出 Markdown，总体上就是把当前 Guangya smoke 档案的“批量补 `parentId/fileId` -> 刷新证据 -> 导出总览”收成一条命令
  - 已新增 auth remediation bundle 接口 `GET /api/auth/remediation_bundle`、Markdown 接口 `GET /api/auth/remediation_bundle_markdown` 与导出脚本 [export_auth_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_auth_remediation_bundle.py)，可把当前全部 auth profile 的 readiness 缺口和建议补字段命令汇总到 [09-AUTH_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/09-AUTH_REMEDIATION_GUIDE.md)，方便为 Guangya/阿里/夸克等 provider 的真实联调先补齐最关键字段
  - auth profile 视图、单档案 evidence 与 remediation bundle 现已区分 `profileReady` 与 `writeReady`：像 `189cloud` 这类当前仅具备 shareCode/accessCode 只读链路的档案，会明确返回 `writeReady=false`、`writeMissingFieldHints` 与 `writeBlockerNote`，不再把“能读但不能写”混成一个 readiness 状态
  - `189cloud` 当前已把“只读 share 链路”和“账号级写鉴权”拆开提示：capture hints、remediation patch 命令与前端本地 patch hint 都会明确写出 `shareCode` 只覆盖读探测，而写目录仍需 `token/accessToken + signature + date`
  - 已新增本地脚本 [patch_189cloud_account_auth.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/patch_189cloud_account_auth.py)，可直接从抓包 header / curl / JSON 文本里提取 `accessToken / signature / date`，并按已有 `profileId` 回填 189Cloud 档案，不必再手工逐项抄写账号级写鉴权字段
  - `189cloud` remediation bundle 与前端本地 patch hint 现已切到专用 helper：即使档案已经 `profileReady=true` 但仍 `writeReady=false`，也会继续显示 `patch_189cloud_account_auth.py` 推荐命令，不会再因为“读 ready”而把写鉴权补救命令隐藏掉
  - `189cloud` 当前已接入账号级 `createFolder.action` 写目录尝试：当档案具备 `token/accessToken + signature + date` 时，会走账号级 headers 发起真实 create_dir 请求；若仍是 shareCode/accessCode-only 档案，则继续诚实返回只读阻断
  - `189cloud` 现已额外补上 `fast_upload` 任务分支的候选探针：只有当档案具备账号级 `AccessToken / Signature / Date` 且文件已有 `md5 + size` 时，运行期才会产出 `executionMode=probe`、`liveAttempt.mode=189cloud_fast_upload_candidate` 的 runtime 样本；share-only 或缺写鉴权时会诚实返回缺鉴权阻断
  - `189cloud` 现已进一步补上真实 rapid-upload API 尝试：`fast_upload` 项在具备 `localPath + md5 + targetProfileId` 且档案带有账号级写鉴权时，不再只停留在候选探针，而是会先用 `accessToken` 刷出 `sessionKey/sessionSecret`，再对 `POST https://api.cloud.189.cn/createUploadFile.action` 发起 live create 请求；命中 `fileDataExists=1` 时会继续调用返回的 `fileCommitUrl` 完成秒传提交，并记录 `executionMode=live`、`liveAttempt.mode=rapid_upload_by_hash`
  - 该 189Cloud rapid-upload live attempt 现会先复算本地 `md5`，避免把错误 fingerprint 直接打到线上；由于当前仓内还没有账号级 `list/metadata` 回查能力，所以成功校验会诚实落在 `verifyMode=commit_response_xml`，表示本轮是依据 provider 的 `createUploadFile + fileCommitUrl` 响应链确认秒传成功，而不是伪装成目录回查已验证；若 `fileDataExists!=1` 也会明确落为“仍需后续二进制上传 fallback”
- 当前验证证据：
  - `POST /api/auth/profiles` 现会在保存时同步返回结构化 `validation` 结果，并据此写入 profile `status`
  - `POST /api/auth/profiles/{id}/validate` 现会返回结构化 `validation` 结果，并据此更新 profile `status`
  - `POST /api/auth/capture/start` 返回 `capture_pending`，并带真实 `loginUrlHint` 与 `requiredFieldHints`
  - `DELETE /api/auth/profiles/{id}` 返回 `{"ok":true}`
  - [verify_auth_live_validation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_live_validation.py) 已覆盖保存时自动校验与单条/批量认证验证
  - [verify_guangya_validation_hints.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_guangya_validation_hints.py) 已验证 Guangya save-time/provider-aware 校验可识别 `parentFileId/file_id/authorization` 别名输入
  - [verify_auth_profile_readiness.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_profile_readiness.py) 已验证 `/api/auth/profiles` 会把缺 `parentId` 的 Guangya 档案标记为 `profileReady=false`
  - [verify_auth_profile_resolved_defaults.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_profile_resolved_defaults.py) 已验证 Guangya 仅填 `parentFileId/file_id` 时，`/api/auth/profiles` 会返回 `resolvedParentId/resolvedFileId`
  - [verify_auth_profile_update.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_profile_update.py) 已验证 `PUT /api/auth/profiles/{id}` 可保留原 token，仅补 `extra.parentId` 后重新校验成功
  - [verify_patch_auth_profile_extra.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_auth_profile_extra.py) 已验证本地 patch 脚本只更新命中的目标档案、可写回 `extra.parentId/fileId`、并在 `--revalidate` 时同步写回验证结果
  - [verify_patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_and_probe_auth_profile.py) 已验证一键脚本会把 `extra.parentId/fileId` 写回目标档案，并在同一流程内产出 validation 记录和 provider live probe 记录
  - [verify_auth_profile_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_profile_evidence.py) 已验证单档案 evidence API、`/evidence_markdown` 与 Markdown 导出会同时带出 `profileReady/validationOk/probeOk/resolvedParentId/resolvedFileId`
  - [verify_refresh_auth_profile_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_refresh_auth_profile_evidence.py) 已验证 `/refresh_evidence` 会返回刷新后的 evidence 与 Markdown
  - [verify_patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_and_probe_auth_profile.py) 现还额外验证了 `--evidence-output` 会真实落出证据 Markdown 文件
  - [verify_auth_evidence_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_evidence_bundle.py) 已验证 bundle API、`/evidence_bundle_markdown` 与多档案 Markdown 汇总会返回正确的 profile 数量与总览内容
  - [verify_refresh_auth_evidence_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_refresh_auth_evidence_bundle.py) 已验证 `/refresh_evidence_bundle` 会返回刷新后的 bundle 与 Markdown
  - [verify_patch_refresh_export_auth_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_refresh_export_auth_bundle.py) 已验证批量脚本可同时命中 `2` 个 Guangya smoke 档案，统一写回 `parentId/fileId`，并落出 bundle Markdown 文件
  - [verify_auth_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_remediation_bundle.py) 已验证 remediation bundle API、`/remediation_bundle_markdown` 与 Markdown 导出会同时带出 `profileCount/readyCount/needsFixCount` 和建议补字段命令
  - [verify_auth_profile_write_readiness.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_profile_write_readiness.py) 已验证 `189cloud` share-only 档案在 `/api/auth/profiles`、单档案 evidence API 与 Markdown 导出里都会暴露 `writeReady=false`、`writeMissingFieldHints` 与 `writeBlockerNote`
  - [verify_189cloud_write_auth_ui_hints.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_write_auth_ui_hints.py) 已验证 189Cloud 授权表单已暴露 `accessToken/signature/date` 字段，capture hints 与 remediation patch 命令也会明确提示账号级写鉴权所需字段
  - [verify_patch_189cloud_account_auth.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_189cloud_account_auth.py) 已验证 `patch_189cloud_account_auth.py` 可从原始 header 文本提取 `accessToken/signature/date`，并按 `profileId` 真实写回 189Cloud 档案的 `extra`
  - [verify_189cloud_account_auth_create_dir.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_account_auth_create_dir.py) 已验证 `tianyi_live.fetch_tianyi_create_folder()` 会按 `POST https://cloud.189.cn/api/open/file/createFolder.action` 发起请求，并带上 `AccessToken/Accesstoken/Signature/Date` 头与 `parentFolderId/folderName` 表单体
  - [verify_189cloud_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_fast_upload_candidate_evidence.py) 已验证 `189cloud` 任务运行会在 `fast_upload` 分支产出 `executionMode=probe`、`liveAttempt.mode=189cloud_fast_upload_candidate`、`hashKind=md5` 的候选样本，并把该 probe-only 证据写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_189cloud_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_fast_upload_live.py) 已验证 `189cloud` 的 live rapid-upload 路径会先刷新 `sessionKey/sessionSecret`，再发起 `createUploadFile`，并在 `fileDataExists=1` 时继续调用 `fileCommitUrl`，最终产出 `mode=rapid_upload_by_hash`、`verifyMode=commit_response_xml` 的最小闭环样本
  - [verify_189cloud_runtime_fast_upload_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_runtime_fast_upload_evidence.py) 已验证 `189cloud` 任务运行会在 `fast_upload` 分支产出 `executionMode=live`、`liveAttempt.mode=rapid_upload_by_hash`、`verifyMode=commit_response_xml` 的真实运行样本，并把该样本落入 `task_runtime_evidence` 与 `real_evidence_report`
  - 当前本地两个 Guangya smoke 档案已可通过 `POST /api/auth/profiles/{id}/validate` 被判定为 `status=invalid`、`lastError=missing_parent_id`
  - 当前本地 `2` 个 Guangya smoke 档案也已可通过 `patch_auth_profile_extra.py --provider-key guangya --display-name-contains smoke --set parentId=...` 被 dry-run 命中，后续拿到真实 `parentId` 后可直接批量回填

### M6 - 互传任务规划

- 完成日期：`2026-05-23`
- 提交：`6f6a9ff`
- 完成范围：
  - 秒传优先与 fallback 阈值策略
  - `selectedRoots` 输入
  - `executionGroups` 与 `pendingItems` 输出
  - “顶层顺序 + 最底层优先”执行分组
  - 任务级同名文件冲突策略 `conflictPolicy`：当前已支持 `overwrite_existing / auto_rename_new`，并会随 mock plan 与任务创建结果一起保存和返回
  - `conflictPolicy` 当前已收成受控枚举，非法值不会被静默接受
  - mock plan 现在还会在每个 `items / executionGroups / pendingItems` 行里显式返回 `conflictSupportStatus / conflictNote`，用于提前说明目标 provider 上该冲突策略是“已支持 / 会诚实降级 / 当前未承诺”
  - mock plan 现在还会在每个 `items` 行里返回 `normalizedFingerprints / availableFastInputs / missingFastInputs`，用于直接解释秒传判断为什么命中或缺失
  - 队列页现在已支持先预览 plan：可在真正创建任务前直接查看 `strategyCounts`、每条 `normalizedFingerprints`、`availableFastInputs/missingFastInputs` 与 `conflictSupportStatus/conflictNote`
- 当前验证证据：
  - `POST /api/plan/mock` 传入 `selectedRoots=["/1","/2","/3"]` 后，返回根顺序 `/1,/2,/3`
  - 结果同时包含 `fast_upload`、`download_upload`、`pending_manual`
  - 返回 `pendingItems` 数量为 `1`
  - [verify_fingerprint_set_normalization.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_fingerprint_set_normalization.py) 已验证 `POST /api/plan/mock` 在 `115_open` 目标下会把输入里的 `md5/sha1/etag/pickCode/block_list_md5` 归一化，并据此返回 `availableFastInputs=["size","name","md5","sha1","etag","pickcode","blockListMd5"]`
  - [verify_task_conflict_policy.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_conflict_policy.py) 已验证 `/api/plan/mock` 与任务创建结果会保留 `conflictPolicy=overwrite_existing`
  - [verify_plan_conflict_support.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_plan_conflict_support.py) 已验证 `POST /api/plan/mock` 在 `guangya + overwrite_existing` 时会返回 `conflictSupportStatus=downgrade_to_auto_rename`，在 `189cloud + auto_rename_new` 时会返回 `conflictSupportStatus=unsupported`
  - [verify_task_conflict_policy_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_conflict_policy_api.py) 已验证 `POST /api/tasks` 创建任务与 `POST /api/tasks/{id}/action` 运行任务时，HTTP 返回会保留 `conflictPolicy`，并把 `conflictAction/resolvedTargetName` 回写到结果
  - [verify_task_conflict_support.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_conflict_support.py) 已验证 `POST /api/tasks` 创建任务后，`plan.items[].conflictSupportStatus` 会继续透传到运行结果 `results[].conflictSupportStatus`，例如当前 `guangya + overwrite_existing` 会稳定回显 `downgrade_to_auto_rename`
  - [verify_task_conflict_policy_validation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_conflict_policy_validation.py) 已验证 `/api/plan/mock` 与 `/api/tasks` 会拒绝非法 `conflictPolicy`
  - 任务明细现已补上 Markdown 导出：`GET /api/tasks/{id}/markdown` 会把任务选中的 `conflictPolicy`、计划项 `conflictSupportStatus/conflictNote`、以及运行期 `conflictAction/resolvedTargetName` 一起导出，方便直接对账“选了覆盖还是自动重命名、provider 是否诚实降级、最终落成了哪个目标文件名”
  - [verify_task_markdown_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_markdown_api.py) 已验证任务 Markdown 已包含 `selectedPolicy=overwrite_existing`、计划项冲突支持状态、运行期 `conflictAction=overwrite_downgraded_to_auto_rename` 与 `resolvedTargetName=demo (1).bin`
  - 已新增导出脚本 [export_task_markdown.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_task_markdown.py)：可按当前进程内 `--task-id` 或离线任务快照 `--task-json` 导出任务详情 Markdown，并支持 `--output` 直接落本地文件，真实联调跑出任务后不必再手工从 API 响应复制证据
  - [verify_export_task_markdown.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_export_task_markdown.py) 已验证导出脚本会真实写出 Markdown 文件，且内容已包含 `selectedPolicy=overwrite_existing`、`conflictSupportStatus=downgrade_to_auto_rename`、`conflictAction=overwrite_downgraded_to_auto_rename` 与 `resolvedTargetName=demo (1).bin`

### M7 - 受控执行与 UI

- 完成日期：`2026-05-23`
- 提交：`db82978`
- 当前补齐：`working tree`
- 完成范围：
  - 任务状态机：创建、查询、`run`、`pause`、`resume`、`retry`
  - 风控暂停与 pending 汇总
  - 主页面六个页签全部有实际面板：新建任务、授权管理、传输队列、待处理、网盘能力、设置
  - 授权弹窗、tip、折叠区、步骤二级导航与中英文页面文案
  - 授权页现在会直接显示保存结果、手动验证结果、capture guide 与 live probe 摘要，并在列表里显示每个档案最近一次 validation/probe 结论
  - 授权表单会根据当前 provider 自动切换 `authMode` 选项并显示 `authModes` 提示；授权列表中的 live probe 按钮已放开到当前 10 个已接 provider
  - 队列页轻量任务表单：`targetProfileId`、`localPath`、阈值输入与结果风险提示展示
  - 队列页现已支持选择同名文件冲突策略 `overwrite_existing / auto_rename_new`
  - 队列页任务结果和待处理列表现在会回显 `conflictSupportStatus`，可直接看到当前策略在目标 provider 上是已支持、诚实降级，还是当前未承诺
  - 队列页现已新增 `Preview Plan` 按钮与预览面板；创建任务前可先看到 `strategyCounts`、每条 `normalizedFingerprints`、`availableFastInputs/missingFastInputs` 与 `conflictSupportStatus/conflictNote`
  - 队列页 `targetProfileId` 现会按当前 `targetProvider` 自动过滤，只保留同 provider 的授权档案；切换目标 provider 时会同时清空旧预览，避免错把上一个目标的档案/预览继续带到新目标
  - plan 预览面板现已新增风险提示区：当存在 `pending_manual`、`download_upload` 或冲突策略 `unsupported` 时，会直接给出更直白的原因和操作提示
  - plan 预览面板现在还会直接显示当前 `targetProfile` 的 `profileReady/writeReady`；当目标档案缺字段或当前不可写时，会在预览风险区提前给出 `missingFieldHints / writeMissingFieldHints / writeBlockerNote`
  - `Create Task` 现在会在前端自动重跑一次最新 plan 校验；如果当前 `targetProfile.writeReady === false`，或 plan 中存在 `conflictSupportStatus=unsupported`，会先阻断创建并把原因显示在页面提示框里
  - 对于 `pending_manual`、`download_upload` 这类“可继续但有明显风险”的情况，队列页现在还要求用户先勾选确认框再允许创建任务，不再只是提示文字
  - 服务端任务创建现在也会统一产出 `guard` 结果，并把前端同类规则下沉为后端权威判断：当前已覆盖 `targetProfile.writeReady`、`conflictSupportStatus=unsupported`、以及 `pending_manual/download_upload` 的确认需求；命中硬阻断时，任务状态会直接落成 `blocked`
  - soft-risk 现在还被收成显式服务端状态流：未确认时任务状态会落成 `awaiting_ack`，`run` 不会越过它继续执行；调用 `acknowledge_risk` 后才会转回 `ready/risk_paused`
  - 任务列表动作现已按 `state` 收紧：`awaiting_ack` 优先显示 `acknowledge_risk/retry`，`blocked` 仅保留 `retry`，`running/paused/ready/completed_with_errors` 等状态也只显示各自合理动作，不再所有按钮一股脑同时出现
  - 任务列表现在还会把状态和 guard 摘要做成更直观的 pill：`awaiting_ack / blocked / risk_paused / running / completed_with_errors` 更容易一眼识别，`guard=hard_blocked / blocking / warnings / ack=...` 也不再只是一整行长文本
  - `/api/tasks/{id}/action` 现在也已具备服务端状态机约束：后端会按当前任务 `state` 校验 `run/pause/resume/retry/acknowledge_risk` 是否允许，非法动作不会被静默接受，而是会把 `lastActionError.action/reason/at` 写回任务
  - 任务列表现在还会直接展示 `lastActionError`：被服务端拒绝的动作会显示成单独错误 pill 和时间戳说明，不必再靠猜测按钮为什么没生效
  - 任务对象现在还会统一带 `summary`：已收口 `state / allowedActions / hardBlocked / blockingCount / warningCount / requiresAcknowledgement / acknowledged / awaitingAcknowledgement / riskPaused / riskReason / hasLastActionError / lastActionError`，前端任务列表也已优先消费这个摘要而不是继续散读原始对象
  - `/api/tasks/{id}/action` 现在会明确返回 `action / actionApplied / actionError / allowedActions`，前端任务按钮也已切到服务端 `summary.allowedActions`，不再自己再维护一套并行动作白名单
  - 任务 API 现在已开始分离“原始对象 / 列表视图 / 详情视图”合同：`GET /api/tasks` 会同时返回 `items + listItems`，`POST /api/tasks`、`GET /api/tasks/{id}`、`POST /api/tasks/{id}/action` 会同时返回 `item + listView + detailView`，方便前端列表与详情直接消费稳定结构
  - 任务结果现已显式区分 `executionMode=live/mock/manual/blocked`；像非 Guangya 的当前 mock/download fallback、待人工处理、以及当前 runtime 主动阻断的大文件 fallback，都不再只能靠 `note` 猜测，队列摘要会直接显示执行模式
  - 设置页认证验证 / provider probe 统计已改为直接读取后端 `items/latestItems/summary` 返回，不再把 `latestItems` 误当成 history 数量
  - 授权列表现会直接显示 `profileReady/missingFieldHints` 与最近一次 validation `riskHint`，方便在真正联调前先补档案缺口
  - 任务表单和授权列表现会优先使用档案返回的 `resolvedParentId/resolvedFileId`，降低别名字段场景下的手工映射成本
  - 授权列表现已支持直接进入编辑态；更新现有档案后会自动重新校验并刷新 readiness/validation 摘要
  - 编辑态现会明确提示当前正在编辑的档案，以及 `token/cookie` 留空时会保留原值，降低补字段时误清空密钥的风险
  - 授权列表在缺字段档案上现会直接显示本地 `patch_auth_profile_extra.py` 命令提示，方便按 `profileId` 回填真实 `parentId/domainId/pwdId` 等缺失字段
  - 授权列表现会额外显示 `write_ready / write_missing / write_blocker`，可直接区分“当前读链路可用”与“当前写链路仍受限”的档案，尤其是 `189cloud` share-only 场景
  - 授权高级字段现已直接暴露 `189cloud` 的 `accessToken / signature / date` 输入框；编辑已有档案时也会自动回填这些字段，前端本地 patch hint 也不再把 189Cloud 误导成只补 `shareCode` 就能写
  - 授权列表现已支持直接查看单档案 `Refresh Evidence`，会调用 `/api/auth/profiles/{id}/refresh_evidence` 并在现有结果区显示刷新后的摘要和 Markdown
  - 授权页工具栏现已支持直接查看 `Evidence Bundle`，会调用 `/api/auth/refresh_evidence_bundle` 并在现有结果区显示当前全部 auth profile 的刷新后证据总览
  - 授权页工具栏现已支持直接查看 `Remediation Guide`，会调用 `/api/auth/remediation_bundle` 与 `/api/auth/remediation_bundle_markdown` 并在现有结果区显示当前全部 auth profile 的补字段建议总览
  - Guangya 任务运行阶段已接入真实 fallback 上传链路入口：库存 miss 后可继续尝试本地文件二进制上传
  - Guangya fallback 真上传成功后，现会继续做 post-upload verify：优先使用返回 `fileId` 做 live metadata 确认，拿不到 `fileId` 时退回 `parentId + 文件名` 的 live list 确认
  - Guangya fallback 真上传前现在会先检查目标目录同名文件；若用户选择 `auto_rename_new` 则自动改名上传，若用户选择 `overwrite_existing` 但当前链路不支持真覆盖，则会诚实降级为自动改名，并把降级动作写回任务结果
  - `189cloud` 当前已补上显式 runtime blocked probe 分支：即使 shareCode/accessCode 链路仍然只读，运行期结果与 task runtime evidence 也会明确落出 `189cloud_create_dir_probe`、`share_auth_readonly` 与所需 `AccessToken/Signature/Date`
  - `189cloud` 当前也已支持账号级写目录 success path：`/api/providers/189cloud/create_dir` 在档案具备 `token/accessToken + signature + date` 时可返回 `mode=live`，provider 状态矩阵则改为 `runtime_candidate`，表示代码链路已可尝试但仍缺真实成功样本
- 当前验证证据：
  - 任务动作流 `resume -> run -> retry -> pause` 返回状态依次可用
  - [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 包含 `pendingPanel`、`providersPanel`、`settingsPanel`
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 已接入 `loadProviderResearch`、`loadStatusMatrix`、`loadLiveValidations`、`renderPendingList`、`renderSettingsPanel`
  - 授权页已新增 `authValidationSummary` 摘要区，保存/验证/probe 后会展示结构化结论；授权列表也会显示最近一次 validation/probe 摘要
  - 授权页已新增 `authModeHint`，并会按当前 provider 的 `authModes` 自动刷新 `authMode` 下拉；`official_oauth` 已可在支持的 provider 上直接选择
  - 队列页已包含 `taskTargetProfile`、`taskLocalPath`、`taskCreateBtn`，且任务结果可回显 `liveAttempt.riskHint`
  - [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 与 [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 已新增 `taskConflictPolicy` 选择与任务列表冲突策略回显
  - [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 已验证首页 HTML 已带 `taskPreviewBtn/taskPlanPreviewPanel/taskPlanPreviewSummary`，静态脚本已带 `previewTaskPlan/renderTaskPlanPreview` 并完成按钮绑定
  - [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 现还额外验证了 `taskPlanPreviewRisk`、`taskTargetProvider -> onTaskTargetProviderChange` 绑定、按 `providerKey === targetProvider` 过滤档案，以及 `pending_manual/download_upload/conflict unsupported` 风险提示文本
  - [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 现还额外验证了预览区已包含 `targetProfile not ready` / `targetProfile not write-ready` 风险提示逻辑，以及 `profileReady/writeReady` 元信息展示
  - [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 现还额外验证了 `taskCreateGuard`、`fetchTaskPlanPreview()`、以及 `Create Task` 对 `targetProfile.writeReady === false` 和 `conflictSupportStatus=unsupported` 的前端阻断逻辑
  - [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 现还额外验证了 `taskPlanPreviewAck/taskPlanPreviewAckWrap`、`resetTaskPlanAck()`，以及 `pending_manual/download_upload` 场景下“未勾选确认框则不允许创建任务”的前端确认逻辑
  - [verify_task_server_guard.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_server_guard.py) 已验证服务端在 `189cloud` share-only 目标档案 + `auto_rename_new` 冲突策略场景下会把任务创建成 `state=blocked`、`risk.reason=guard_blocked`，并把 `hardBlocked/blockingReasons/targetProfile.writeReady=false` 写入任务 `guard`
  - 同一脚本也已验证普通 `guangya` fallback 任务在服务端会留下 `guard.requiresAcknowledgement.downloadUpload=true` 与 `warningReasons=["download_upload requires explicit confirmation"]`，说明 soft-risk 也已下沉成服务端权威结果
  - 同一脚本现还额外验证了普通 `guangya` fallback 任务在服务端创建后会先进入 `state=awaiting_ack`、`risk.reason=awaiting_acknowledgement`，调用 `acknowledge_task_risk()` 后会转成 `state=ready`
  - `node --check src/cloudpan_sync/web/assets/app.js` 已通过，当前前端脚本语法有效
  - [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 现还额外验证了前端已接入 `acknowledge_risk` 动作按钮逻辑，能承接服务端 `awaiting_ack` 状态
  - 同一脚本现还额外验证了前端已收成 `taskActionsForState(task)` 动作规则 helper，并覆盖 `awaiting_ack/blocked/running/paused` 等状态分支
  - 同一脚本现还额外验证了前端已接入 `appendTaskStatusPill()/appendTaskGuardPill()` helper，以及 `guard=hard_blocked / warnings= / downloadUpload:` 这类 guard 摘要 pill 逻辑
  - [verify_task_action_guards.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_action_guards.py) 已验证 `blocked` 任务执行 `resume` 时会保留 `state=blocked` 并写回 `lastActionError.reason=resume_not_allowed_from_blocked`；`awaiting_ack` 任务执行 `run` 时会保留 `state=awaiting_ack` 并写回 `lastActionError.reason=run_not_allowed_until_acknowledge_risk`
  - 同一脚本也已验证 `awaiting_ack` 任务执行 `acknowledge_risk` 后会转成 `state=ready`，且可用动作重新回到 `run/pause/retry`
  - [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 现还额外验证了前端已接入 `lastActionError=` pill 和 `task-action-error` 文本展示逻辑
  - [verify_task_summary_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_summary_api.py) 已验证 `blocked / awaiting_ack / acknowledge_risk 后 ready` 三种任务状态都会返回同步更新的 `summary`，其中 `allowedActions / awaitingAcknowledgement / riskReason` 等关键字段会随状态转换正确变化
  - [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 现还额外验证了前端已开始优先读取 `task.summary`，包括 `summary.state` 与 `summary.lastActionError`
  - [verify_189cloud_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_runtime_probe_evidence.py) 已验证 `189cloud` runtime 分支会落出 `executionMode=probe` 的失败样本，并把 `189cloud_create_dir_probe / share_auth_readonly / requiredAuth=[AccessToken,Signature,Date]` 同步写入 task runtime evidence、real evidence report 与 provider status matrix
  - [verify_189cloud_create_dir_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_create_dir_api.py) 现已同时验证 `189cloud` 的只读 share 场景会返回 `unsupported_readonly_share_auth`，而账号级写鉴权场景会返回 `mode=live` 与新目录 `fileId`
  - [verify_task_action_guards.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_action_guards.py) 现还额外验证了 `POST /api/tasks/{id}/action` 在 `awaiting_ack` 任务上返回 `actionApplied=false`、结构化 `actionError`，并同步返回当前 `allowedActions=["acknowledge_risk","retry"]`
  - [verify_queue_plan_preview_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_queue_plan_preview_ui.py) 现还额外验证了前端任务按钮来源已切到 `task.summary.allowedActions`
  - [verify_task_views_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_views_api.py) 已验证 `POST /api/tasks` 会返回 `item + listView + detailView`，`GET /api/tasks` 会返回 `items + listItems`，`GET /api/tasks/{id}` 与 `POST /api/tasks/{id}/action` 会继续返回 `listView/detailView`，且 `detailView` 已稳定带出 `planSummary / executionGroups / pendingItems / results / sourceEntries`；当前 mock 执行分支还会显式回传 `results[].executionMode=mock`
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 的任务结果摘要现会直接显示 `executionMode`，例如 `done [mock]` 或 `failed [live]`，避免把任务已运行误读成真实互传已完成
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 的任务结果摘要与待处理列表现会额外显示 `conflictSupportStatus/conflictNote`
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 的设置页统计现已读取后端返回的 `summary/historyCount`，不会再把最新结果集误显示为历史总量
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 的授权列表现会显示 `profileReady=false` 和缺失字段提示，例如 Guangya smoke 档案会直接提示缺 `extra.parentId`
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 的任务表单预填、live probe 请求与 demo task 现会优先使用 `resolvedParentId/resolvedFileId`
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 已新增 auth profile 编辑/取消编辑流程，保存时会按新增或更新自动切换
  - [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 与 [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 已接入 `authEditHint`，编辑态会提示“留空保留原 token/cookie”
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 已新增 `patch_hint` 摘要，缺字段时会显示可直接执行的本地补字段命令模板
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 的授权列表、evidence 摘要与 remediation 摘要现会显示 `writeReady/writeNeedsFixCount` 等写链路状态，方便直接识别 `189cloud` 这种“可读不可写”档案
  - [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 已新增 `Refresh Evidence` 按钮与 evidence 摘要展示逻辑，可直接刷新并查看单档案 Markdown 证据
  - [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 与 [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 已新增 `Evidence Bundle` 按钮与 bundle 摘要展示逻辑，可直接刷新并查看全部 auth profile 的 Markdown 证据总览
  - [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 与 [app.js](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/assets/app.js) 已新增 `Remediation Guide` 按钮与摘要展示逻辑，可直接查看全部 auth profile 的建议补字段命令总览
  - 运行时已验证 `download_upload` 项在 mocked live fast-check miss 后，可进入 `binary_upload_multipart` 成功分支
  - [verify_guangya_upload_post_verify.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_guangya_upload_post_verify.py) 已验证 Guangya 直传成功后可走 `metadata_by_file_id`，multipart fallback 成功后可走 `list_by_parent_name`，并会把同名冲突处理动作回写成 `conflictAction/resolvedTargetName`
  - [verify_task_runtime_guangya_verify_fields.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_guangya_verify_fields.py) 已验证任务运行在 Guangya `binary_upload_multipart` 成功分支下会把 `verifyOk/verifyMode/verifyNote` 透传到 `results[].liveAttempt`
  - [verify_task_conflict_policy.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_conflict_policy.py) 已验证 `overwrite_existing` 会从 plan/task 透传到 runtime，并在当前 Guangya fallback 链路不支持真覆盖时诚实降级为 `overwrite_downgraded_to_auto_rename`，同时回显 `resolvedTargetName`

### M8 - 首批 Provider 清单补全（骨架级）

- 完成日期：`2026-05-23`
- 提交：`6fc85ba`
- 完成范围：
  - provider registry 补齐首批 `10` 个 provider
  - provider 研究索引补齐到 `10` 条
  - 为新增 provider 接入通用 `list/metadata` mock 能力
- 当前验证证据：
  - `GET /api/providers` 返回 `providerCount=10`
  - `GET /api/providers/research` 返回 `researchCount=10`
  - `POST /api/providers/189cloud/list` 返回 `mode=mock`
  - `POST /api/providers/115_open/metadata` 返回非空 `md5`

### M9 - 计划完成度审计与报告导出

- 完成日期：`2026-05-23`
- 提交：`339b17e`
- 完成范围：
  - `plan_audit.py` 结构化审计模块
  - 审计 API：
    - `GET /api/plan/audit`
    - `GET /api/plan/audit_markdown`
  - 报告导出脚本 `scripts/export_plan_audit.py`
  - 审计文档 `docs/04-PLAN_AUDIT_REPORT.md`
- 当前验证证据：
  - `GET /api/plan/audit` 返回 `done=5, partial=2, todo=1`
  - `GET /api/plan/audit_markdown` 返回非空 Markdown
  - [04-PLAN_AUDIT_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/04-PLAN_AUDIT_REPORT.md) 已存在

### M10 - UI 交互补齐（向导/弹窗/tip/折叠）

- 完成日期：`2026-05-23`
- 提交：`df4b2f7`
- 完成范围：
  - 新建任务步骤条
  - 授权弹窗（Web Login Capture）
  - tip 提示与高级字段折叠区
- 当前验证证据：
  - `POST /api/auth/capture/start` 返回 `capture_pending`
  - [index.html](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/web/index.html) 包含 `wizard-steps`
  - 同文件包含 `authModal` 与 `<details class="advanced-block">`

### M11 - 首批 Provider 在线探测验证层

- 完成日期：`2026-05-23`
- 提交：`5450476`
- 当前补齐：`working tree`
- 完成范围：
  - `live_probe` 模块
  - 探测 API：
    - `GET /api/providers/live_probe`
    - `GET /api/providers/live_probe_markdown`
  - 报告导出脚本 `scripts/export_live_probe_report.py`
  - 本地可控验证导出脚本 `scripts/export_local_live_adapter_verification.py`
  - 探测报告文档 `docs/05-PROVIDER_LIVE_PROBE_REPORT.md`
  - 本地可控验证文档 `docs/07-LOCAL_LIVE_ADAPTER_VERIFICATION.md`
  - `guangya`、`aliyundrive_open`、`189cloud`、`baidu_netdisk`、`123_open`、`115_open`、`xunlei`、`pikpak`、`quark`、`uc` 都已接入 profile 级 live probe；其中 Guangya、阿里云盘 Open、百度、迅雷、PikPak、123、115、Quark、UC 当前覆盖到 `list / metadata / create_dir`，`189cloud` 现也已补上账号级 `create_dir` 尝试，而 share-only 档案仍会在 `create_dir` 探测里明确返回只读阻断
  - 已新增 `POST /api/providers/189cloud/create_dir` 的双轨行为：share-only 档案会诚实返回 `unsupported_readonly_share_auth` 与 `AccessToken/Signature/Date` 提示，账号级鉴权齐备时则会走 `createFolder.action` 尝试真实写目录
  - 已新增 `POST /api/providers/quark/create_dir` 与 `POST /api/providers/uc/create_dir`，可基于已保存 cookie 直接尝试 live 建目录，并把结果返回给前端或脚本侧调用方
- 当前验证证据：
  - `GET /api/providers/live_probe` 返回 `providerCount=10, totalChecks=12, failedChecks=0`
  - `GET /api/providers/live_probe_markdown` 返回非空 Markdown
  - `GET /api/providers/live_probe_results` 现会返回 `items/latestItems/summary`
  - [verify_live_result_list_apis.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_live_result_list_apis.py) 已单独回归验证 `GET /api/providers/live_probe_results` 的 `items/latestItems/summary` 结构
  - [05-PROVIDER_LIVE_PROBE_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/05-PROVIDER_LIVE_PROBE_REPORT.md) 已存在
  - 当前报告 summary 已记录 `profileProbeProviderCount=2`、`profileProbeOkCount=0`、`profileProbeFailedCount=2`
  - 当前本地两个 Guangya smoke 档案已留下 profile probe 记录，失败原因均为 `missing_parent_id`
  - [verify_provider_live_adapters.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_live_adapters.py) 可重复输出当前本地可控验证结果
  - [07-LOCAL_LIVE_ADAPTER_VERIFICATION.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/07-LOCAL_LIVE_ADAPTER_VERIFICATION.md) 可落盘保存当前本地可控验证快照
  - 本地可控验证已覆盖 `guangya` 的 `3` 个 probe checks 并返回 `probe_ok=True`
  - 本地可控验证已覆盖 `aliyundrive_open` 的 `3` 个 probe checks 并返回 `probe_ok=True`
  - 本地可控验证已覆盖 `189cloud` 的 `3` 个 probe checks，其中 share profile 下 `list/metadata` 返回成功，账号级鉴权 profile 下 `create_dir` 可返回 `create_ok=True`
  - 本地可控验证已覆盖 `baidu_netdisk` 的 `3` 个 probe checks 并返回 `probe_ok=True`
  - 本地可控验证已覆盖 `123_open` 的 `3` 个 probe checks 并返回 `probe_ok=True`
  - 本地可控验证已覆盖 `115_open` 的 `3` 个 probe checks 并返回 `probe_ok=True`
  - 本地可控验证已覆盖 `xunlei` 的 `3` 个 probe checks 并返回 `probe_ok=True`
  - 本地可控验证已覆盖 `pikpak` 的 `3` 个 probe checks 并返回 `probe_ok=True`
  - 本地可控验证已覆盖 `quark` 的 `3` 个 probe checks 并返回 `probe_ok=True`，对应 `create_ok=True`
  - 本地可控验证已覆盖 `uc` 的 `3` 个 probe checks 并返回 `probe_ok=True`，对应 `create_ok=True`
  - [verify_provider_create_dir_apis.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_create_dir_apis.py) 已验证 Quark / UC 的 `create_dir` HTTP API 会返回 `mode=live` 与新目录 `fileId`

### M12 - 基于授权档案的真实认证验证流程

- 完成日期：`2026-05-23`
- 提交：`d1c944d`
- 完成范围：
  - `auth_live_validate` 模块
  - API：
    - `POST /api/auth/live_validate`
    - `GET /api/auth/live_validations`
  - 验证记录持久化
  - 报告导出脚本与文档
  - provider-aware 最小 live validation 默认复用已接入的 provider live probe，而不是仅请求 provider 首页
  - 对缺字段的校验结果已补充 `requiredFieldHints / riskHint`，前端可直接显示下一步该补哪些字段
- 当前验证证据：
  - [verify_auth_live_validation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_live_validation.py) 可重复验证 `POST /api/auth/live_validate` 的 provider-aware 结构化结果
  - `GET /api/auth/live_validations` 现会返回 `items/latestItems/summary`
  - [verify_live_result_list_apis.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_live_result_list_apis.py) 已单独回归验证 `GET /api/auth/live_validations` 的 `items/latestItems/summary` 结构
  - [verify_guangya_validation_hints.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_guangya_validation_hints.py) 已验证 Guangya 缺 `parentId` 时会返回 `requiredFieldHints`，并保留 `riskHint`
  - [03-AUTH_LIVE_VALIDATION_REPORT.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/03-AUTH_LIVE_VALIDATION_REPORT.md) 已存在
  - 当前报告已记录 `4` 条 Guangya 实际验证结果，失败原因为 `missing_parent_id`
  - 当前报告已额外汇总 `latestProfileCount=2`、`latestOkCount=0`、`latestFailedCount=2`，并把每个 profile 的最新结果与历史记录分开展示

### M13 - 批量认证验证与结果汇总

- 完成日期：`2026-05-23`
- 提交：`0dbe40a`
- 完成范围：
  - 批量认证验证 API：`POST /api/auth/live_validate_all`
  - 遍历全部已保存 `AuthProfile` 并汇总结果
  - 持续写入认证验证记录
- 当前验证证据：
  - `POST /api/auth/live_validate_all` 可按已保存档案返回 `totalProfiles / okProfiles / failedProfiles`
  - [verify_auth_live_validation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_auth_live_validation.py) 已覆盖批量汇总返回 `totalProfiles / okProfiles / failedProfiles`
  - 验证结果会持续写入 `GET /api/auth/live_validations` 对应的数据文件，并可通过 `latestItems/summary` 直接读取当前最新状态
  - 以当前本地 `2` 个 Guangya 档案实际执行批量认证验证时，返回 `totalProfiles=2`、`okProfiles=0`、`failedProfiles=2`

### M14 - Provider 状态矩阵与进度量化

- 完成日期：`2026-05-23`
- 提交：`3e6ec79`
- 当前补齐：`working tree`
- 完成范围：
  - `provider_status_matrix` 聚合模块
  - API：
  - `GET /api/providers/status_matrix`
  - `GET /api/providers/status_matrix_markdown`
  - 导出脚本 `scripts/export_provider_status_matrix.py`
  - 状态矩阵文档 `docs/06-PROVIDER_STATUS_MATRIX.md`
  - live ready 集合已补进 `guangya`、`aliyundrive_open`、`189cloud`、`baidu_netdisk`、`123_open`、`115_open`、`xunlei`、`pikpak`、`quark`、`uc`，状态矩阵现可同时反映其 `list_ready / metadata_ready / create_dir_ready`
  - provider registry、状态矩阵 API、状态矩阵 Markdown 与“网盘能力”面板现都会显式暴露同名冲突处理能力：`conflictPolicies / supportsOverwrite / supportsAutoRename / overwriteBehavior / conflictNotes`
  - 当前 `guangya` 已诚实标注为“接受 `overwrite_existing / auto_rename_new`，但现阶段 `overwrite_existing` 会降级成 `auto_rename_new`”；当前 `189cloud` 已诚实标注为“当前 shareCode/accessCode 链路只读，不能承诺覆盖或自动重命名”
  - 已新增真实证据状态聚合模块 `real_evidence_report`、API `GET /api/real_evidence` / `GET /api/real_evidence_markdown`、导出脚本 [export_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_real_evidence_report.py) 与文档 [10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md)，可按 provider 汇总当前已保存的 `auth / list / metadata / create_dir` 真实证据覆盖，并明确哪些缺口还停留在 `P-REAL`
  - 任务运行阶段现已新增 `task_runtime_evidence` 持久化：当像 Guangya fallback 上传这类真实运行链路成功时，会把 `providerKey / profileId / mode / verifyOk / verifyMode / conflictAction / resolvedTargetName` 落盘，`real_evidence_report` 也会把它计入 `taskRuntimeEvidence`
  - 设置页现已新增 `Real Evidence` 摘要区，会直接读取 `GET /api/real_evidence` 的 summary，并显示 `auth / list / metadata / create_dir / task_runtime / fully_verified` 覆盖数，不必再只靠看导出的 Markdown
  - 已新增任务运行真实样本明细 API `GET /api/task_runtime_evidence` / `GET /api/task_runtime_evidence_markdown`、导出脚本 [export_task_runtime_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_task_runtime_evidence_report.py) 与文档 [11-TASK_RUNTIME_EVIDENCE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/11-TASK_RUNTIME_EVIDENCE.md)，可直接查看 runtime 真实样本明细、`verifyOk` 数量和冲突处理样本数
  - provider 面板现也已直接接入真实证据摘要：每个 provider 都会显示 `auth / list / metadata / create_dir / task_runtime / fully_verified` 六项真实证据状态，以及 `real_evidence_gaps` 缺口说明，不用再切去设置页或单看导出文档
  - provider 面板里的 `real_evidence task_runtime` 摘要现也会直接显示 `conflict=...`，可以看出当前某个 provider 已经累计留下了多少条真实运行冲突处理样本
  - 设置页现已新增 `Task Runtime Evidence` 摘要区，会直接读取 `GET /api/task_runtime_evidence` 的 summary，并显示 `sampleCount / providerCount / profileCount / successProviderCount / failedProviderCount / successCount / failedCount / verifyOkCount / conflictHandledProviderCount / conflictHandledCount`，以及最近几条 runtime 样本简讯；最新样本行当前也会直接显示 `success=...`
  - `task_runtime_evidence` 现已不只记录成功样本，也会持久化真实失败样本，并区分 `successCount / failedCount`、错误码、风险提示和运行 note，后续排查 `P-REAL` 缺口时不必只看成功案例
  - `real_evidence_report` 现也会显式吸收 runtime 失败样本：若某个 provider 已经出现真实运行失败但还没有成功样本，会在 `taskRuntimeEvidence` 中显示 `sampleCount / successCount / failedCount / failedProfiles`，并把“已有 task runtime 失败样本，但尚无成功样本”写进缺口提示
  - provider 面板里的 `task_runtime` 现也已升级成 success/failed 计数展示，例如 `task_runtime=false(0/1)`，不再只是布尔值，能更直观看到“已经失败过几次、是否出现过成功样本”
  - `real_evidence_report` summary 与设置页 `Real Evidence` 摘要现也已显式量化 `taskRuntimeFailedProviderCount`，可直接看到当前有多少 provider 已进入“真实运行失败但尚未成功”的阶段
  - `real_evidence_report` summary 与设置页 `Real Evidence` 摘要现还已显式量化全局 runtime 样本总量：`taskRuntimeSampleCount / taskRuntimeSuccessCount / taskRuntimeFailedCount`，可以直接看到当前累计了多少真实运行样本、其中成功/失败各有多少
  - `real_evidence_report` summary 与设置页 `Real Evidence` 摘要现还已显式量化 `taskRuntimeConflictHandledCount`，并且每个 provider 的 `taskRuntimeEvidence` 也会带 `conflictHandledCount`
  - `provider_status_matrix` 现也已吸收 runtime 真实样本计数：每个 provider 都会带 `task_runtime_samples / task_runtime_success / task_runtime_failed`，summary 也会带 `taskRuntimeEvidenceProviderCount / taskRuntimeFailedProviderCount / taskRuntimeSampleCount / taskRuntimeSuccessCount / taskRuntimeFailedCount`
  - `provider_status_matrix` 现还会继续吸收 runtime 同名冲突处理样本：每个 provider 都会额外带 `task_runtime_conflict_handled`，summary 也会带 `taskRuntimeConflictHandledProviderCount / taskRuntimeConflictHandledCount`
  - `provider_status_matrix` 现还会显式量化每个 provider 距离“接入真实运行写链路”还差多远：新增 `task_runtime_track=runtime_active/runtime_candidate/runtime_blocked/runtime_planned` 与 `task_runtime_track_note`，并在 summary 中汇总 `taskRuntimeActiveCount / taskRuntimeCandidateCount / taskRuntimeBlockedCount`
  - `provider_status_matrix` 的 `fast_check` 现已不再只覆盖早期少数 provider，而是改为按“已声明 `fastUploadInputs` 且当前 `metadata_ready=true`”自动推导；首批 10 个 provider 现在都会在矩阵中诚实显示 `fast_check=true`
  - `provider_status_matrix` 现还会把两条计划内同名冲突策略分开量化：每个 provider 都会额外暴露 `overwrite_support_status / overwrite_support_note` 与 `auto_rename_support_status / auto_rename_support_note`，并在 summary 中汇总 `overwriteDowngradeCount / overwriteSupportedCount / autoRenameSupportedCount / autoRenameProbeOnlyCount / conflictUnsupportedProviderCount`
  - provider 面板现也会直接展示 `task_runtime_track` 与说明文本，可一眼区分“Guangya / aliyundrive_open / 123_open / 115_open / xunlei / pikpak / baidu_netdisk / quark / uc 已在 runtime_active”“189cloud 当前 runtime_candidate”
  - provider 面板里的 `task_runtime_track` 现也会直接显示 `conflictHandled=...`，可以看出某个 provider 当前已经累计留下了多少条真实运行冲突处理样本
  - provider 面板里的 conflict 摘要现也会直接展示 `overwriteSupport=... / autoRenameSupport=...`，可以把 `supported / downgrade_to_auto_rename / probe_only_runtime_write_check / unsupported` 当场看出来，不必再回头翻 plan 结果
  - provider 面板摘要卡片现也会直接显示 `autoRenameProbeOnly` 与 `conflictUnsupported` 计数，可一眼看出当前有多少 provider 仍停留在“仅写探针、未声明真实同名处理”和“当前两条冲突策略都还不支持”的状态
  - provider 面板摘要卡片现还会直接显示 `runtimeConflictHandled` 总数，可一眼看到当前累计沉淀了多少条真实运行冲突处理样本
  - `aliyundrive_open` 现已从 `runtime_candidate` 推进到 `runtime_active`：任务运行阶段遇到 `download_upload` 项且存在本地文件时，会先执行真实 `create_dir` 写探针，并把结果按 `mode=aliyundrive_open_create_dir_probe` 落入 `task_runtime_evidence`
  - 该 Aliyun runtime 写探针会明确标成 `executionMode=probe`，并在任务结果说明里写清“真实 create_dir 写探针成功，但当前文件传输仍由 mock/download fallback 完成”，避免把写探针误写成文件上传成功
  - `aliyundrive_open` 现已额外补上 `fast_upload` 任务分支的候选探针：当规划命中 `md5 + size` 时，运行期会产出 `executionMode=probe`、`liveAttempt.mode=aliyundrive_open_fast_upload_candidate` 的 runtime 样本，并明确写清“当前仅确认秒传候选条件，不代表真实 rapid-upload API 已执行成功”
  - `aliyundrive_open` 现已进一步补上真实本地文件上传链路：`download_upload` 项在具备 `localPath + targetProfileId` 时不再只做 `create_dir` 探针，而是按 `create -> upload_url PUT -> complete` 发起真实单分片上传，并把结果按 `executionMode=live`、`liveAttempt.mode=binary_upload_single_part` 落入任务结果与 `task_runtime_evidence`
  - 该 Aliyun live upload 链路现已显式接住同名冲突策略：`auto_rename_new` 会透传为 provider 侧自动改名，`overwrite_existing` 会透传为 provider 侧 overwrite 模式；上传成功后还会继续尝试 `metadata_by_file_id`，拿不到时再退回 `list_by_parent_name` 做 post-upload verify，并把 `verifyMode / conflictAction / resolvedTargetName` 一并回写
  - `123_open` 现也已从 `runtime_candidate` 推进到 `runtime_active`：任务运行阶段遇到 `download_upload` 项且存在本地文件时，会先执行真实 `create_dir` 写探针，并把结果按 `mode=123_open_create_dir_probe` 落入 `task_runtime_evidence`
  - 该 123Pan runtime 写探针同样会明确标成 `executionMode=probe`，并在任务结果说明里写清“真实 create_dir 写探针成功，但当前文件传输仍由 mock/download fallback 完成”，避免把写探针误写成文件上传成功
  - `123_open` 现已额外补上 `fast_upload` 任务分支的候选探针：当规划命中 `md5 + size` 时，运行期会产出 `executionMode=probe`、`liveAttempt.mode=123_open_fast_upload_candidate` 的 runtime 样本，并明确写清“当前仅确认秒传候选条件，不代表真实 rapid-upload API 已执行成功”
  - `123_open` 现已进一步补上真实本地文件上传链路：`download_upload` 项在具备 `localPath + targetProfileId` 时不再只做 `create_dir` 探针，而是按官方 `create -> get_upload_url -> PUT -> upload_complete -> upload_async_result` 发起真实单分片上传，并把结果按 `executionMode=live`、`liveAttempt.mode=binary_upload_single_part` 落入任务结果与 `task_runtime_evidence`
  - 该 123Pan live upload 链路现已显式接住同名冲突策略：`auto_rename_new` 会在运行前基于 live list 先找不冲突的新名字；`overwrite_existing` 当前会诚实降级为自动改名，并把 `conflictAction=overwrite_downgraded_to_auto_rename` 与最终 `resolvedTargetName` 写回任务结果；上传成功后还会继续尝试 `metadata_by_file_id`，拿不到时再退回 `list_by_parent_name` 做 post-upload verify
  - `115_open` 现也已从 `runtime_candidate` 推进到 `runtime_active`：任务运行阶段遇到 `download_upload` 项且存在本地文件时，会先执行真实 `create_dir` 写探针，并把结果按 `mode=115_open_create_dir_probe` 落入 `task_runtime_evidence`
  - 该 115 Open runtime 写探针同样会明确标成 `executionMode=probe`，并在任务结果说明里写清“真实 create_dir 写探针成功，但当前文件传输仍由 mock/download fallback 完成”，避免把写探针误写成文件上传成功
  - `115_open` 现已额外补上 `fast_upload` 任务分支的候选探针：当规划命中 `sha1 + size` 时，运行期会产出 `executionMode=probe`、`liveAttempt.mode=115_open_fast_upload_candidate` 的 runtime 样本，并明确写清“当前仅确认秒传候选条件，不代表真实 rapid-upload API 已执行成功”
  - `115_open` 现已进一步补上真实 rapid-upload API 尝试：`fast_upload` 项在具备 `localPath + sha1 + targetProfileId` 时，不再只停留在候选探针，而是会对 `POST https://proapi.115.com/open/upload/init` 发起 live init 请求；命中 `status=2` 时会记录 `executionMode=live`、`liveAttempt.mode=rapid_upload_by_hash`，若返回 `status in {6,7,8}` 还会继续补发带 `sign_key/sign_val` 的二次校验请求
  - 该 115 Open rapid-upload live attempt 现还会先复算本地完整 `sha1` 与前 `128KB` 的 `preid`，避免把错误 fingerprint 直接打到线上；命中后会优先尝试 `metadata_by_file_id`，拿不到再退回 `list_by_parent_name` 做 post-upload verify，并把 `target / fileId / pickCode / responseStatus / resolvedTargetName` 一并写入任务结果与 `task_runtime_evidence`；若线上返回“仍需后续二进制上传”也会诚实落为未命中，而不会伪装成完整上传成功
  - `xunlei` 现也已从 `runtime_candidate` 推进到 `runtime_active`：任务运行阶段遇到 `download_upload` 项且存在本地文件时，会先执行真实 `create_dir` 写探针，并把结果按 `mode=xunlei_create_dir_probe` 落入 `task_runtime_evidence`
  - 该 Xunlei runtime 写探针同样会明确标成 `executionMode=probe`，并在任务结果说明里写清“真实 create_dir 写探针成功，但当前文件传输仍由 mock/download fallback 完成”，避免把写探针误写成文件上传成功
  - `xunlei` 现已额外补上 `fast_upload` 任务分支的候选探针：当规划命中 `gcid + size` 时，运行期会产出 `executionMode=probe`、`liveAttempt.mode=xunlei_fast_upload_candidate` 的 runtime 样本，并明确写清“当前仅确认秒传候选条件，不代表真实 rapid-upload API 已执行成功”
  - `xunlei` 现已进一步补上真实 rapid-upload API 尝试：`fast_upload` 项在具备 `localPath + gcid + targetProfileId` 时，不再只停留在候选探针，而是会对 `POST /drive/v1/files` 发起 live create-by-hash 请求；命中秒传时会记录 `executionMode=live`、`liveAttempt.mode=rapid_upload_by_hash`，未命中时也会诚实区分为“返回 resumable，仍需后续真实二进制上传 fallback”
  - 该 Xunlei rapid-upload live attempt 现还会先复算本地 `gcid`，避免把错误 fingerprint 直接打到线上；命中后会优先尝试 `metadata_by_file_id`，拿不到再退回 `list_by_parent_name` 做 post-upload verify，并把 `uploadType / fileId / resolvedTargetName` 一并写入任务结果与 `task_runtime_evidence`
  - `pikpak` 现也已从 `runtime_candidate` 推进到 `runtime_active`：任务运行阶段遇到 `download_upload` 项且存在本地文件时，会先执行真实 `create_dir` 写探针，并把结果按 `mode=pikpak_create_dir_probe` 落入 `task_runtime_evidence`
  - 该 PikPak runtime 写探针同样会明确标成 `executionMode=probe`，并在任务结果说明里写清“真实 create_dir 写探针成功，但当前文件传输仍由 mock/download fallback 完成”，避免把写探针误写成文件上传成功
  - `pikpak` 现已进一步补上真实 rapid-upload API 尝试：`fast_upload` 项在具备 `localPath + gcid + targetProfileId` 时，不再只停留在候选探针，而是会对 `POST /drive/v1/files` 发起 live create-by-hash 请求；命中秒传时会记录 `executionMode=live`、`liveAttempt.mode=rapid_upload_by_hash`，未命中时也会诚实区分为“返回 resumable，仍需后续真实二进制上传 fallback”
  - 该 PikPak rapid-upload live attempt 现还会先复算本地 `gcid`，避免把错误 fingerprint 直接打到线上；命中后会优先尝试 `metadata_by_file_id`，拿不到再退回 `list_by_parent_name` 做 post-upload verify，并把 `uploadType / fileId / resolvedTargetName` 一并写入任务结果与 `task_runtime_evidence`
  - `baidu_netdisk` 现也已从 `runtime_candidate` 推进到 `runtime_active`：任务运行阶段遇到 `download_upload` 项且存在本地文件时，会先执行真实 `create_dir` 写探针，并把结果按 `mode=baidu_netdisk_create_dir_probe` 落入 `task_runtime_evidence`
  - 该 Baidu Netdisk runtime 写探针同样会明确标成 `executionMode=probe`，并在任务结果说明里写清“真实 create_dir 写探针成功，但当前文件传输仍由 mock/download fallback 完成”，避免把写探针误写成文件上传成功
  - `pikpak` 现已额外补上 `fast_upload` 任务分支的候选探针：当规划命中 `gcid + size` 时，运行期会产出 `executionMode=probe`、`liveAttempt.mode=pikpak_fast_upload_candidate` 的 runtime 样本，并明确写清“当前仅确认秒传候选条件，不代表真实 rapid-upload API 已执行成功”
  - `baidu_netdisk` 现已额外补上 `fast_upload` 任务分支的候选探针：当规划命中 `md5 + size` 时，运行期会产出 `executionMode=probe`、`liveAttempt.mode=baidu_netdisk_fast_upload_candidate` 的 runtime 样本，并明确写清“当前仅确认秒传候选条件，不代表真实 rapid-upload API 已执行成功”
  - `quark` 现已额外补上 `fast_upload` 任务分支的候选探针：当规划命中 `md5 + size` 时，运行期会产出 `executionMode=probe`、`liveAttempt.mode=quark_fast_upload_candidate` 的 runtime 样本，并明确写清“当前仅确认秒传候选条件，不代表真实 rapid-upload API 已执行成功”
  - `uc` 现已额外补上 `fast_upload` 任务分支的候选探针：当规划命中 `md5 + size` 时，运行期会产出 `executionMode=probe`、`liveAttempt.mode=uc_fast_upload_candidate` 的 runtime 样本，并明确写清“当前仅确认秒传候选条件，不代表真实 rapid-upload API 已执行成功”
  - `quark` 现也已从 `runtime_candidate` 推进到 `runtime_active`：任务运行阶段遇到 `download_upload` 项且存在本地文件时，会先执行真实 `create_dir` 写探针，并把结果按 `mode=quark_create_dir_probe` 落入 `task_runtime_evidence`
  - 该 Quark runtime 写探针同样会明确标成 `executionMode=probe`，并在任务结果说明里写清“真实 create_dir 写探针成功，但当前文件传输仍由 mock/download fallback 完成”，避免把写探针误写成文件上传成功
  - `uc` 现也已从 `runtime_candidate` 推进到 `runtime_active`：任务运行阶段遇到 `download_upload` 项且存在本地文件时，会先执行真实 `create_dir` 写探针，并把结果按 `mode=uc_create_dir_probe` 落入 `task_runtime_evidence`
  - 该 UC Drive runtime 写探针同样会明确标成 `executionMode=probe`，并在任务结果说明里写清“真实 create_dir 写探针成功，但当前文件传输仍由 mock/download fallback 完成”，避免把写探针误写成文件上传成功
- 当前验证证据：
  - `GET /api/providers/status_matrix` 返回结构化 summary 与 provider 明细，并区分真实 `list / metadata / create_dir` 绑定状态
  - `GET /api/providers/status_matrix_markdown` 返回非空 Markdown
  - [06-PROVIDER_STATUS_MATRIX.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/06-PROVIDER_STATUS_MATRIX.md) 已存在
  - [verify_provider_conflict_capabilities.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_conflict_capabilities.py) 已验证 `GET /api/providers` 与 `GET /api/providers/status_matrix` 会同时暴露 `guangya` 的 `overwriteBehavior=downgrade_to_auto_rename`、`supportsAutoRename=true`，以及 `189cloud` 的 `overwriteBehavior=readonly_auth_blocked`
  - [verify_provider_live_adapters.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_live_adapters.py) 会同步输出这些 provider 的 `list_ready / metadata_ready / create_dir_ready / live_probe_ok`
  - 当前导出矩阵 summary 已记录 `createDirReadyCount=9`
  - 当前导出矩阵 summary 已记录 `conflictAwareProviderCount=1`、`overwriteReadyCount=0`、`autoRenameReadyCount=1`
  - 本地可控验证显示 `guangya` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=True`
  - 本地可控验证显示 `guangya` 行的 `conflictPolicies=overwrite_existing,auto_rename_new`、`supportsOverwrite=False`、`supportsAutoRename=True`、`overwriteBehavior=downgrade_to_auto_rename`
  - 本地可控验证显示 `aliyundrive_open` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=True`
  - 本地可控验证显示 `189cloud` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=False`
  - 本地可控验证显示 `189cloud` 行的 `conflictPolicies=[]`、`supportsOverwrite=False`、`supportsAutoRename=False`、`overwriteBehavior=readonly_auth_blocked`
  - 本地可控验证显示 `baidu_netdisk` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=True`
  - 本地可控验证显示 `123_open` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=True`
  - 本地可控验证显示 `115_open` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=True`
  - 本地可控验证显示 `xunlei` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=True`
  - 本地可控验证显示 `pikpak` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=True`
  - 本地可控验证显示 `quark` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=True`
  - 本地可控验证显示 `uc` 行的 `list_ready=True`、`metadata_ready=True`、`create_dir_ready=True`
  - [verify_189cloud_create_dir_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_create_dir_api.py) 已验证 `POST /api/providers/189cloud/create_dir` 会返回 `mode=unsupported_readonly_share_auth`、`fallbackReason=share_auth_readonly` 和所需 `requiredAuth`
  - [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py) 已验证真实证据聚合会分别统计 `authEvidence / listEvidence / metadataEvidence / createDirEvidence / taskRuntimeEvidence`，并且 `GET /api/real_evidence` 与 `GET /api/real_evidence_markdown` 会返回对应 summary 与 Markdown 报告
  - [verify_task_runtime_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence.py) 已验证 Guangya `binary_upload_multipart` 成功后会把 runtime 真实样本落进 `task_runtime_evidence`，并被 `real_evidence_report` 计成 `taskRuntimeEvidenceProviderCount=1`
  - [verify_real_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_settings_ui.py) 已验证设置页已接入 `Real Evidence` 面板、`loadRealEvidenceSummary()`、登出清理、以及 `auth/list/metadata/create_dir/task_runtime/fully_verified` 摘要展示
  - [10-REAL_EVIDENCE_STATUS.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/10-REAL_EVIDENCE_STATUS.md) 当前已落盘，能直接看见 `providerCount / profilesSaved / latestValidationProfileCount / latestProbeProfileCount` 以及各 provider 的真实证据缺口
  - [verify_task_runtime_evidence_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_api.py) 已验证 `GET /api/task_runtime_evidence` 与 `GET /api/task_runtime_evidence_markdown` 会返回 `sampleCount / providerCount / profileCount / successProviderCount / failedProviderCount / verifyOkCount / conflictHandledProviderCount / conflictHandledCount` 和样本明细
  - [11-TASK_RUNTIME_EVIDENCE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/11-TASK_RUNTIME_EVIDENCE.md) 当前已落盘；若真实环境尚未产生 runtime 样本，它会诚实显示 `sampleCount=0`
  - [verify_provider_real_evidence_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_real_evidence_ui.py) 已验证 provider 面板已接入 `realEvidenceReport`、`realEvidenceByProvider()`、真实证据摘要和 `real_evidence_gaps` 缺口展示
  - [verify_provider_real_evidence_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_real_evidence_ui.py) 现还额外验证了 provider 面板 `real_evidence task_runtime` 已带 `conflict=...`
  - [verify_task_runtime_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_settings_ui.py) 已验证设置页已接入 `Task Runtime Evidence` 面板、`loadTaskRuntimeEvidence()`、登出清理、以及 runtime 样本摘要展示；当前还会直接显示 `successProviders=`、`failedProviders=`、`success=`、`failed=`、`conflictHandledProviders=`，最近样本简讯也会显示 `success=...`
  - [verify_task_runtime_failure_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_failure_evidence.py) 已验证 Guangya 真实运行失败样本也会写入 `task_runtime_evidence`，并在 summary 中体现为 `failedCount=1`
  - [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py) 现还额外验证了当 provider 只有 runtime 失败样本时，`taskRuntimeEvidence.failedCount`、`failedProfiles` 与缺口提示都会同步出现
  - [verify_provider_real_evidence_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_real_evidence_ui.py) 现还额外验证了 provider 面板 `task_runtime` 已带 `successCount/failedCount` 计数展示
  - [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py) 现还额外验证了 report summary 与 Markdown 已带 `taskRuntimeFailedProviderCount / task_runtime_failed`
  - [verify_real_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_settings_ui.py) 现还额外验证了设置页 `Real Evidence` 摘要已展示 `task_runtime_failed`
  - [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py) 现还额外验证了 report summary 与 Markdown 已带 `taskRuntimeSampleCount / taskRuntimeSuccessCount / taskRuntimeFailedCount`
  - [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py) 现还额外验证了 report summary 与 Markdown 已带 `taskRuntimeConflictHandledCount / runtime_conflict_handled`
  - [verify_real_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_settings_ui.py) 现还额外验证了设置页 `Real Evidence` 摘要已展示 `runtime_samples / runtime_success / runtime_failed`
  - [verify_real_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_settings_ui.py) 现还额外验证了设置页 `Real Evidence` 摘要已展示 `runtime_conflict_handled`
  - [verify_provider_conflict_capabilities.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_conflict_capabilities.py) 现还额外验证了 `GET /api/providers/status_matrix` summary 已带 `taskRuntimeEvidenceProviderCount / taskRuntimeFailedProviderCount / taskRuntimeSampleCount / taskRuntimeSuccessCount / taskRuntimeFailedCount`，并且 `guangya/189cloud` 行都已暴露 `task_runtime_samples / task_runtime_success / task_runtime_failed`
  - [verify_provider_conflict_capabilities.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_conflict_capabilities.py) 现还额外验证了状态矩阵 summary 已带 `taskRuntimeConflictHandledProviderCount / taskRuntimeConflictHandledCount`，并且 `guangya/189cloud` 行都会暴露 `task_runtime_conflict_handled`
  - [verify_provider_fast_check_matrix.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_fast_check_matrix.py) 已验证状态矩阵中的 `fastCheckCount` 已推进到 `10`，并且首批 `guangya / aliyundrive_open / 115_open / 189cloud / baidu_netdisk / quark / uc / xunlei / pikpak / 123_open` 都会在 `metadata_ready=true` 时显示 `fast_check=true`
  - [verify_provider_conflict_capabilities.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_conflict_capabilities.py) 现还额外验证了 `guangya`/`189cloud` 行都会暴露 `task_runtime_track`，可区分 `runtime_active` 与 `runtime_candidate`
  - [verify_provider_conflict_capabilities.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_conflict_capabilities.py) 当前还可验证状态矩阵 summary 已推进到 `taskRuntimeActiveCount=9`、`taskRuntimeCandidateCount=1`、`taskRuntimeBlockedCount=0`
  - [verify_provider_conflict_capabilities.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_conflict_capabilities.py) 现还额外验证了 `guangya`、`123_open`、`baidu_netdisk` 行都会暴露 `overwrite_support_status=downgrade_to_auto_rename`、`auto_rename_support_status=supported`，`aliyundrive_open` 行会暴露 `overwrite_support_status=supported`、`auto_rename_support_status=supported`，`189cloud` 行会暴露 `overwrite_support_status=unsupported`、`auto_rename_support_status=unsupported`，并且 summary 已推进到 `overwriteDowngradeCount=3`、`overwriteSupportedCount=1`、`autoRenameSupportedCount=4`、`autoRenameProbeOnlyCount=5`、`conflictUnsupportedProviderCount=1`
  - [verify_provider_real_evidence_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_real_evidence_ui.py) 现还额外验证了 provider 面板已显示 `task_runtime_track=...`，并会带 `conflictHandled=...`
  - [verify_provider_real_evidence_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_real_evidence_ui.py) 现还额外验证了 provider 面板摘要卡片已接入 `autoRenameProbeOnly`、`conflictUnsupported` 与 `runtimeConflictHandled` 三个冲突/运行计数
  - [verify_aliyun_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_aliyun_runtime_probe_evidence.py) 已验证 `aliyundrive_open` 任务运行会在 `download_upload` 分支执行真实 `create_dir` 写探针，返回 `results[].executionMode=probe`、`liveAttempt.mode=aliyundrive_open_create_dir_probe`，并把样本落入 `task_runtime_evidence`
  - [verify_aliyun_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_aliyun_fast_upload_candidate_evidence.py) 已验证 `aliyundrive_open` 任务运行会在 `fast_upload` 分支产出 `executionMode=probe`、`liveAttempt.mode=aliyundrive_open_fast_upload_candidate`、`hashKind=md5` 的候选样本，并把该 probe-only 证据写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_123_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_123_runtime_probe_evidence.py) 已验证 `123_open` 任务运行会在 `download_upload` 分支执行真实 `create_dir` 写探针，返回 `results[].executionMode=probe`、`liveAttempt.mode=123_open_create_dir_probe`，并把样本落入 `task_runtime_evidence`
  - [verify_123_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_123_fast_upload_candidate_evidence.py) 已验证 `123_open` 任务运行会在 `fast_upload` 分支产出 `executionMode=probe`、`liveAttempt.mode=123_open_fast_upload_candidate`、`hashKind=md5` 的候选样本，并把该 probe-only 证据写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_115_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_115_runtime_probe_evidence.py) 已验证 `115_open` 任务运行会在 `download_upload` 分支执行真实 `create_dir` 写探针，返回 `results[].executionMode=probe`、`liveAttempt.mode=115_open_create_dir_probe`，并把样本落入 `task_runtime_evidence`
  - [verify_115_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_115_fast_upload_candidate_evidence.py) 已验证 `115_open` 任务运行会在 `fast_upload` 分支产出 `executionMode=probe`、`liveAttempt.mode=115_open_fast_upload_candidate`、`hashKind=sha1` 的候选样本，并把该 probe-only 证据写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_115_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_115_fast_upload_live.py) 已验证 `115_open` 的 live rapid-upload init 路径会先打一次 `upload/init`，遇到 `status=7` 时再补发带 `sign_key/sign_val` 的二次请求，并最终产出 `mode=rapid_upload_by_hash`、`requestCount=2`、`firstStatus=7`、`secondStatus=2` 的最小闭环样本
  - [verify_115_runtime_fast_upload_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_115_runtime_fast_upload_evidence.py) 已验证 `115_open` 任务运行会在 `fast_upload` 分支产出 `executionMode=live`、`liveAttempt.mode=rapid_upload_by_hash`、`verifyMode=metadata_by_file_id` 的真实运行样本，并把该样本落入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_xunlei_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_xunlei_runtime_probe_evidence.py) 已验证 `xunlei` 任务运行会在 `download_upload` 分支执行真实 `create_dir` 写探针，返回 `results[].executionMode=probe`、`liveAttempt.mode=xunlei_create_dir_probe`，并把样本落入 `task_runtime_evidence`
  - [verify_xunlei_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_xunlei_fast_upload_candidate_evidence.py) 已验证 `xunlei` 任务运行会在 `fast_upload` 分支产出 `executionMode=probe`、`liveAttempt.mode=xunlei_fast_upload_candidate`、`hashKind=gcid` 的候选样本，并把该 probe-only 证据写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_xunlei_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_xunlei_fast_upload_live.py) 已验证 `xunlei_fast_upload_live` 会对 `/drive/v1/files` 发起 create-by-hash live 请求，并在秒传命中时返回 `mode=rapid_upload_by_hash`
  - `xunlei_fast_upload_live` 现已继续补上 hash miss 后的真实 resumable 二进制上传兜底：当 create-by-hash 返回 `resumable` 会话时，会继续复用返回的 S3-compatible 临时凭证完成二进制上传，而不再把“秒传未命中”直接当作整次 live 尝试失败
  - [verify_xunlei_fast_upload_binary_fallback.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_xunlei_fast_upload_binary_fallback.py) 已验证 `xunlei` 的 hash miss 分支会真实进入 resumable upload fallback，并把结果标记为 `mode=binary_upload_after_hash_miss`、`verifyMode=metadata_after_resumable_upload`
  - [verify_xunlei_runtime_fast_upload_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_xunlei_runtime_fast_upload_evidence.py) 已验证 `xunlei` 任务运行会在 `fast_upload` 分支产出 `executionMode=live`、`liveAttempt.mode=rapid_upload_by_hash` 的真实样本，并把成功样本写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_pikpak_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_pikpak_runtime_probe_evidence.py) 已验证 `pikpak` 任务运行会在 `download_upload` 分支执行真实 `create_dir` 写探针，返回 `results[].executionMode=probe`、`liveAttempt.mode=pikpak_create_dir_probe`，并把样本落入 `task_runtime_evidence`
  - [verify_baidu_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_baidu_runtime_probe_evidence.py) 已验证 `baidu_netdisk` 任务运行会在 `download_upload` 分支执行真实 `create_dir` 写探针，返回 `results[].executionMode=probe`、`liveAttempt.mode=baidu_netdisk_create_dir_probe`，并把样本落入 `task_runtime_evidence`
  - [verify_pikpak_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_pikpak_fast_upload_candidate_evidence.py) 已验证 `pikpak` 任务运行会在 `fast_upload` 分支产出 `executionMode=probe`、`liveAttempt.mode=pikpak_fast_upload_candidate`、`hashKind=gcid` 的候选样本，并把该 probe-only 证据写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_pikpak_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_pikpak_fast_upload_live.py) 已验证 `pikpak_fast_upload_live` 会对 `/drive/v1/files` 发起 create-by-hash live 请求，并在秒传命中时返回 `mode=rapid_upload_by_hash`
  - `pikpak_fast_upload_live` 现已继续补上 hash miss 后的真实 resumable 二进制上传兜底：当 create-by-hash 返回 `resumable` 会话时，会继续复用返回的 S3-compatible 临时凭证完成二进制上传，而不再把“秒传未命中”直接当作整次 live 尝试失败
  - [verify_pikpak_fast_upload_binary_fallback.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_pikpak_fast_upload_binary_fallback.py) 已验证 `pikpak` 的 hash miss 分支会真实进入 resumable upload fallback，并把结果标记为 `mode=binary_upload_after_hash_miss`、`verifyMode=metadata_after_resumable_upload`
  - [verify_pikpak_runtime_fast_upload_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_pikpak_runtime_fast_upload_evidence.py) 已验证 `pikpak` 任务运行会在 `fast_upload` 分支产出 `executionMode=live`、`liveAttempt.mode=rapid_upload_by_hash` 的真实样本，并把成功样本写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_baidu_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_baidu_fast_upload_candidate_evidence.py) 已验证 `baidu_netdisk` 任务运行会在 `fast_upload` 分支产出 `executionMode=probe`、`liveAttempt.mode=baidu_netdisk_fast_upload_candidate`、`hashKind=md5` 的候选样本，并把该 probe-only 证据写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_quark_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_quark_fast_upload_candidate_evidence.py) 已验证 `quark` 任务运行会在 `fast_upload` 分支产出 `executionMode=probe`、`liveAttempt.mode=quark_fast_upload_candidate`、`hashKind=md5` 的候选样本，并把该 probe-only 证据写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_uc_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_uc_fast_upload_candidate_evidence.py) 已验证 `uc` 任务运行会在 `fast_upload` 分支产出 `executionMode=probe`、`liveAttempt.mode=uc_fast_upload_candidate`、`hashKind=md5` 的候选样本，并把该 probe-only 证据写入 `task_runtime_evidence` 与 `real_evidence_report`
  - [verify_quark_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_quark_runtime_probe_evidence.py) 已验证 `quark` 任务运行会在 `download_upload` 分支执行真实 `create_dir` 写探针，返回 `results[].executionMode=probe`、`liveAttempt.mode=quark_create_dir_probe`，并把样本落入 `task_runtime_evidence`
  - [verify_uc_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_uc_runtime_probe_evidence.py) 已验证 `uc` 任务运行会在 `download_upload` 分支执行真实 `create_dir` 写探针，返回 `results[].executionMode=probe`、`liveAttempt.mode=uc_create_dir_probe`，并把样本落入 `task_runtime_evidence`
  - [06-PROVIDER_STATUS_MATRIX.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/06-PROVIDER_STATUS_MATRIX.md) 现已导出 runtime 样本列；若真实环境暂未积累样本，会诚实显示全 `0`
  - `task_runtime_evidence` 现会额外持久化 `executionMode`；像运行期因当前 512MB 下载上传上限被拦下的样本，也会以 `executionMode=blocked` + `mode=download_upload_blocked_by_size_limit` 落盘，不再只剩一条泛化失败记录
  - `task_runtime_evidence` summary / Markdown / 设置页 `Task Runtime Evidence` 摘要现已补齐 `blockedProviderCount / blockedCount`，最近样本简讯也会直接显示 `executionMode=...`
  - `real_evidence_report` summary、Markdown、设置页 `Real Evidence` 摘要与 provider 面板中的 `task_runtime` 计数现也都会同步显示 `runtime_blocked_providers / runtime_blocked` 与 provider 级 `blockedCount`
  - [verify_task_runtime_blocked_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_blocked_evidence.py) 已验证 `quark` 在 `download_upload` 大文件场景会返回 `results[].executionMode=blocked`、`liveAttempt.mode=download_upload_blocked_by_size_limit`，并把该 blocked 样本写入 `task_runtime_evidence`
  - [verify_task_runtime_evidence_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_api.py) 现还额外验证了 `GET /api/task_runtime_evidence` / `GET /api/task_runtime_evidence_markdown` 已返回 `blockedProviderCount / blockedCount`，且 Markdown 样本行已带 `executionMode=live|blocked`
  - [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py) 现还额外验证了 `GET /api/real_evidence` / Markdown 已返回 `taskRuntimeBlockedProviderCount / taskRuntimeBlockedCount`，并且 provider 级 `taskRuntimeEvidence.blockedCount` 会同步写出
  - [verify_task_runtime_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_settings_ui.py) 现还额外验证了设置页 `Task Runtime Evidence` 摘要已显示 `blockedProviders / blocked`，最近样本行已显示 `executionMode=...`
  - [verify_real_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_settings_ui.py) 现还额外验证了设置页 `Real Evidence` 摘要已显示 `runtime_blocked_providers / runtime_blocked`
  - [verify_provider_real_evidence_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_real_evidence_ui.py) 现还额外验证了 provider / research 面板中的 `task_runtime` 文案已带 `blocked=...`
  - `provider_status_matrix` 现也已同步吸收 runtime blocked 样本：每个 provider 都会额外暴露 `task_runtime_blocked`，summary 也会带 `taskRuntimeBlockedProviderCount / taskRuntimeBlockedEvidenceCount`
  - Provider 状态矩阵导出 [06-PROVIDER_STATUS_MATRIX.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/06-PROVIDER_STATUS_MATRIX.md) 现已补上 `task_runtime_blocked` 列；即使当前真实环境样本仍为 `0`，导出也会诚实保留该列
  - [verify_provider_conflict_capabilities.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_conflict_capabilities.py) 现还额外验证了 `GET /api/providers/status_matrix` summary 已带 `taskRuntimeBlockedProviderCount / taskRuntimeBlockedEvidenceCount`，并且 `189cloud` 行会暴露 `task_runtime_blocked=1`
  - [verify_provider_real_evidence_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_real_evidence_ui.py) 现还额外验证了 provider 面板 `task_runtime_track` 文案已显示 `blocked=...`
  - Provider 面板顶部摘要卡片现也已把状态矩阵里的 blocked runtime 计数抬出来，新增 `runtimeBlocked` 卡片，方便直接看到当前被运行期阻断的真实样本总数
  - 设置页现也已新增 `Provider Status Matrix` 面板，会直接读取当前 `statusMatrix.summary`，展示 `providers / authReady / createDir / fastCheck`、`runtimeBlockedProviders / runtimeBlocked / runtimeConflictHandled`、以及 `runtimeActive / runtimeCandidate / runtimeTrackBlocked / conflictUnsupported`
  - `loadStatusMatrix()` 现会在刷新 provider 面板的同时同步重绘设置页，因此状态矩阵相关摘要不需要切换页签或重新登录才更新
  - [verify_provider_status_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_status_settings_ui.py) 已验证设置页已接入 `Provider Status Matrix` 面板、`loadStatusMatrix()` 会触发 `renderSettingsPanel()`，并且摘要中已包含 blocked/runtime track 相关字段
  - 设置页 `Provider Status Matrix` 面板现还额外补上同名冲突能力摘要：会直接显示 `conflictAware / overwriteDowngrade / overwriteSupported / autoRenameSupported / autoRenameProbeOnly / conflictUnsupported`
  - [verify_provider_status_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_status_settings_ui.py) 现还额外验证了设置页状态矩阵摘要已包含上述冲突能力统计字段
  - 设置页 `Audit` 面板现也已补上 `researchCount`，与审计 API / Markdown 中已有的 `providerCount + researchCount` 覆盖摘要保持一致
  - [verify_audit_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_audit_settings_ui.py) 已验证设置页审计摘要已包含 `done / partial / todo / providerCount / researchCount`
  - 计划审计现已正式拆成双口径进度：`featureCompletionPercent` 只按 `M1-M7` 主功能里程碑按 `done=1 / partial=0.5` 计分，`strictCompletionPercent` 则把 `P-REAL` 一并纳入总验收，后续再看进度时不会把“功能完成度”和“真实联调完成度”混成一个百分比
  - [verify_audit_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_audit_settings_ui.py) 现还额外验证了设置页审计摘要已显示 `featureCompletionPercent / strictCompletionPercent`
  - 已新增真实联调补救指南模块 `real_evidence_remediation`、API `GET /api/real_evidence_remediation_bundle` / `GET /api/real_evidence_remediation_markdown`、导出脚本 [export_real_evidence_remediation.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/export_real_evidence_remediation.py) 与文档 [12-REAL_EVIDENCE_REMEDIATION_GUIDE.md](E:/Workspace/VSCode/CloudPan%20Sync/docs/12-REAL_EVIDENCE_REMEDIATION_GUIDE.md)，可按 provider 汇总当前 `P-REAL` 还缺哪类证据、是否缺档案、是否仅剩 blocked runtime 样本，以及下一步建议动作
  - 设置页现已新增 `Real Evidence Next Steps` 摘要区，会直接读取 `GET /api/real_evidence_remediation_bundle` 的 summary，并展示 `noProfiles / needAuth / needList / needMetadata / needCreateDir / needRuntime / blockedOnly`，不必再人工对着多份 report 自己归纳下一步
  - `Real Evidence Next Steps` 现还会继续带出每个 provider 的 `recommendedAuthModes / webLoginUrl(or officialDocsUrl) / requiredFieldHints`，即使当前还没有建档案，也能直接看到建议授权方式、登录入口和最小字段提示，不必再来回翻研究索引和 capture guide
  - 已新增本地 helper [create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_auth_profile_stub.py)，可直接按 `providerKey/authMode/token|cookie/extra` 创建本地 auth profile；`Real Evidence Next Steps` 现在也会为“当前尚无档案”的 provider 直接生成 `recommendedCreateCommand`
  - [create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_auth_profile_stub.py) 现还已支持 `--probe / --page-size / --dir-name / --evidence-output`，建档案后可直接刷新 validation + live probe 证据；`Real Evidence Next Steps` 现在也会继续生成更接近真实留证的 `recommendedBootstrapCommand`
  - `Real Evidence Next Steps` 现也会为“已有档案但尚未 ready”的 provider 直接生成 `recommendedPatchProbeCommand`，把“补字段”和“立刻落 validation/probe 证据”收成一条命令，不再只剩 `patch_auth_profile_extra.py`
  - `patch_and_probe_auth_profile.py` 现已允许“零补字段”直接刷新证据；`Real Evidence Next Steps` 现在也会为“已有档案且已 ready，但仍缺 auth/list/metadata/create_dir 成功证据”的 provider 生成 `recommendedRefreshEvidenceCommand`
  - 已新增本地 helper [create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_runtime_probe_task.py)，可按 `targetProvider / targetProfileId` 自动创建小文件任务并直接运行；`Real Evidence Next Steps` 现在也会为“基础证据已齐、但还缺 runtime 成功样本”的 provider 生成 `recommendedRuntimeProbeCommand`
  - [create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_runtime_probe_task.py) 现会优先复用已保存 auth profile 的 `resolvedParentId`，若档案里没有再按 provider 根目录默认值补齐 `targetParentId`；并且现也支持 `--evidence-dir` 一次性落出 `task.json / task.md / auth_evidence.md / runtime_evidence.md / real_evidence.md / remediation.md` 六类固定文件。补救指南里的 `recommendedRuntimeProbeCommand` 也会在已有解析结果时直接把 `--target-parent-id` 与 `--evidence-dir` 带出来，进一步减少真实 runtime 起手时的手填量
  - 已新增本地 helper [create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_fast_upload_candidate_task.py)，可按 `targetProvider / targetProfileId` 自动创建 `fast_upload` 候选探针任务并直接运行；当前会复用已保存档案的 `resolvedParentId`，并支持按 provider 自动补 `md5/sha1` 或手传 `gcid`，方便给 Aliyun/123/115/Quark/UC/Baidu/Xunlei/PikPak/189Cloud 这类“已有候选探针分支、但还没接真实 rapid-upload API”的 provider 留下真实 candidate 样本
  - `create_fast_upload_candidate_task.py` 现也支持 `--evidence-dir` 一次性落出 `task.json / task.md / auth_evidence.md / runtime_evidence.md / real_evidence.md / remediation.md` 六类固定文件；`Real Evidence Next Steps` 现在也会继续为“基础 auth/list/metadata 已齐、但还缺 task runtime 成功样本”的非 Guangya provider 生成 `recommendedFastCandidateCommand`，并默认带上 `--evidence-dir`。像 `115_open` 会直接给出 `--sha1 auto`，`xunlei/pikpak` 会明确提示补 `--gcid YOUR_GCID`，已有 `resolvedParentId` 时也会一并带上 `--target-parent-id`
  - `Real Evidence Next Steps` 现在也已接上 Guangya 真实上传 helper：当 `guangya` 已有 ready 档案且 `auth/list/metadata/create_dir` 基础证据已齐、但还缺 runtime success 时，会直接生成 `recommendedLiveUploadCommand`，把“继续跑真实任务”收成更短的 `create_live_upload_task.py --evidence-dir ...` 命令，并默认带上 `--auto-temp-file`、已解析的 `--target-parent-id`；helper 会在该目录下自动生成同一流程里刷新后的 auth validation/probe evidence、任务 `JSON/Markdown` 快照，以及 `runtime/real/remediation` 聚合证据
  - `fast_upload candidate` 样本现在已从“真实 runtime 成功样本”里正式拆口径：运行期证据会单独落 `candidateOnly=true`，`real_evidence_report / task_runtime_evidence / provider_status_matrix / 设置页摘要` 也会独立统计 `task_runtime_candidate / runtime_candidate / candidateCount`，不再把“仅候选命中、未真实 rapid-upload 成功”的 probe-only 样本误算成 `taskRuntimeEvidence.ok=true` 或 `runtime_success`
  - `Real Evidence Next Steps` 现在还会把 `candidate-only` 状态单独抬出来：摘要新增 `providersCandidateOnly`，单 provider 行会显式带 `runtimeCandidateOnly=true/false`；对于“已有 fast-upload candidate 样本但还没真实 runtime 成功样本”的 provider，即使 `create_dir` 证据尚未齐，也会继续给出 `recommendedRuntimeProbeCommand`，让下一步从“看懂缺口”变成“直接有一条能继续落真实样本的命令”
  - `Real Evidence Next Steps` 现在也会把 `probe-only` 状态单独抬出来：摘要新增 `providersProbeOnly`，单 provider 行会显式带 `runtimeProbeOnly=true/false`；对于“已有 create_dir probe 样本但还没真实传输成功样本”的 provider，会明确提示“写探针已跑通但尚未形成真实传输成功证据”，并继续保留 `recommendedRuntimeProbeCommand`
  - `recommendedCreateCommand / recommendedBootstrapCommand` 现在会按 provider 的真实写鉴权特征优先选更贴近“可直接手填”的 authMode：`115_open / quark / uc / 189cloud / baidu_netdisk` 会优先生成 `manual_cookie`，`guangya / 123_open / xunlei / pikpak` 会优先生成 `manual_token`；同时还会跳过和主鉴权重复的 `cookie_header / authorization / accessToken` 这类 extra，避免产出“看起来能跑、实际上重复或不贴手”的建档案命令
  - [verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 已验证 remediation bundle 会为 `guangya` / `189cloud` 这类 provider 生成 `nextStep / recommendedPatchCommand`，并且 API / Markdown 端点已可用
  - 同一脚本现还额外验证了 remediation Markdown 已带 `recommendedAuthModes / webLoginUrl / requiredFieldHints`
  - 同一脚本现还额外验证了 remediation Markdown 已带 `recommendedCreateCommand`
  - 同一脚本现还额外验证了 remediation Markdown 已带 `recommendedBootstrapCommand`，并会显式包含 `--probe`
  - 同一脚本现还额外验证了 remediation Markdown 已带 `recommendedPatchProbeCommand`，并会显式包含 `patch_and_probe_auth_profile.py`
  - 同一脚本现还额外验证了 remediation Markdown 已带 `recommendedRefreshEvidenceCommand`
  - 同一脚本现还额外验证了 remediation Markdown 已带 `recommendedRuntimeProbeCommand`，并会显式包含 `create_runtime_probe_task.py`
  - 同一脚本现还额外验证了 remediation summary / Markdown 已带 `providersWithLiveUploadCommand / recommendedLiveUploadCommand`，`providersWithLiveUploadCommand` 现已推进到 `3`，对应 `guangya / 123_open / baidu_netdisk`；其中 live upload 命令也都已收成 `--evidence-dir ...` 目录模式，同时保留已解析的 `--target-parent-id`
  - 同一脚本现还额外验证了 remediation summary / Markdown 已带 `providersProbeOnly / runtimeProbeOnly`，并且 `probe-only` provider 仍会继续保留 `recommendedRuntimeProbeCommand`
  - [verify_create_auth_profile_stub.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_auth_profile_stub.py) 已验证 `create_auth_profile_stub.py` 可真实写入 `aliyundrive_open` auth profile，并保留 `domainId / driveId`
  - [verify_patch_and_probe_auth_profile.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_patch_and_probe_auth_profile.py) 现还额外验证了 `patch_and_probe_auth_profile.py` 在不传 `--set` 时也可直接刷新已有档案的 validation / probe 证据
  - [verify_create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_runtime_probe_task.py) 已验证 `create_runtime_probe_task.py` 支持 `--target-profile-id / --auto-temp-file / --threshold-mb`，并会真实输出任务结果 JSON
  - 同一脚本现还额外验证了 `create_runtime_probe_task.py` 会从已保存档案自动解析 `resolvedTargetParentId`，并支持 `--evidence-dir` 落六类固定文件名证据包且会刷新最新 auth evidence
  - 已新增 Guangya 真上传 helper [create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_live_upload_task.py)：可直接基于已保存的 `targetProfileId + local file` 创建并运行 live upload 任务，默认自动确认 `download_upload` 风险，并支持用 `--evidence-dir` 一次性落出 `task.json / task.md / auth_evidence.md / runtime_evidence.md / real_evidence.md / remediation.md` 六类固定文件；在导出前还会先刷新最新 auth validation/probe 证据，进一步收紧真实样本取证闭环
  - [verify_create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task.py) 已验证该 helper 会产出 `state=completed`、`completionKind=real_transfer`、`hasRealTransferSuccess=true` 的 Guangya live 任务结果，并会在 `--evidence-dir` 下写出六类固定文件名证据包；其中任务 Markdown 已带 `conflictAction=overwrite_downgraded_to_auto_rename` 与最终 `resolvedTargetName`
  - [create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_live_upload_task.py) 现也已支持 `aliyundrive_open`：可直接基于已保存的 `targetProfileId + local file` 创建并运行 Aliyun live upload 任务，同样支持 `--evidence-dir` 固定证据包模式，并在导出 auth evidence 前刷新最新 validation/probe 证据
  - [verify_aliyun_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_aliyun_upload_live.py) 已验证 `aliyundrive_open` 上传模块会按 `check_name_mode=auto_rename` 发起 `create`，随后执行真实 `upload_url` PUT 与 `complete`，并把 `verifyMode=metadata_by_file_id`、`conflictAction=auto_rename_new` 与最终 `resolvedTargetName` 回写
  - [verify_create_live_upload_task_aliyun.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task_aliyun.py) 已验证 `create_live_upload_task.py --target-provider aliyundrive_open` 会产出 `state=completed`、`completionKind=real_transfer`、`hasRealTransferSuccess=true` 的 Aliyun live 任务结果，并会在 `--evidence-dir` 下写出固定文件名证据包
  - [verify_aliyun_runtime_live_upload_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_aliyun_runtime_live_upload_evidence.py) 已验证 `aliyundrive_open` 的真实上传成功样本会以 `executionMode=live`、`mode=binary_upload_single_part`、`verifyMode=metadata_by_file_id` 写入 `task_runtime_evidence`，并被 `real_evidence_report` 计入 `taskRuntimeEvidence.successCount`
  - [create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_live_upload_task.py) 现也已支持 `123_open`：可直接基于已保存的 `targetProfileId + local file` 创建并运行 123Pan live upload 任务，同样支持 `--evidence-dir` 固定证据包模式，并在导出 auth evidence 前刷新最新 validation/probe 证据
  - [verify_123_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_123_upload_live.py) 已验证 `123_open` 上传模块会按官方链路执行 `create / get_upload_url / PUT / upload_complete / upload_async_result`，并把 `verifyMode=metadata_by_file_id`、`conflictAction=overwrite_downgraded_to_auto_rename` 与最终 `resolvedTargetName` 回写
  - [verify_create_live_upload_task_123.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task_123.py) 已验证 `create_live_upload_task.py --target-provider 123_open` 会产出 `state=completed`、`completionKind=real_transfer`、`hasRealTransferSuccess=true` 的 123Pan live 任务结果，并会在 `--evidence-dir` 下写出固定文件名证据包
  - [verify_123_runtime_live_upload_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_123_runtime_live_upload_evidence.py) 已验证 `123_open` 的真实上传成功样本会以 `executionMode=live`、`mode=binary_upload_single_part`、`verifyMode=metadata_by_file_id` 写入 `task_runtime_evidence`，并被 `real_evidence_report` 计入 `taskRuntimeEvidence.successCount`
  - [create_live_upload_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/create_live_upload_task.py) 现也已支持 `baidu_netdisk`：可直接基于已保存的 `targetProfileId + local file` 创建并运行百度网盘 live upload 任务，同样支持 `--evidence-dir` 固定证据包模式，并在导出 auth evidence 前刷新最新 validation/probe 证据
  - [verify_baidu_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_baidu_upload_live.py) 已验证 `baidu_netdisk` 上传模块会按官方小文件链路执行 `precreate / superfile2 / create`，并把 `verifyMode=metadata_by_file_id`、`conflictAction=overwrite_downgraded_to_auto_rename` 与最终 `resolvedTargetName` 回写
  - [verify_create_live_upload_task_baidu.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_live_upload_task_baidu.py) 已验证 `create_live_upload_task.py --target-provider baidu_netdisk` 会产出 `state=completed`、`completionKind=real_transfer`、`hasRealTransferSuccess=true` 的百度网盘 live 任务结果，并会在 `--evidence-dir` 下写出固定文件名证据包
  - [verify_baidu_runtime_live_upload_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_baidu_runtime_live_upload_evidence.py) 已验证 `baidu_netdisk` 的真实上传成功样本会以 `executionMode=live`、`mode=binary_upload_single_part`、`verifyMode=metadata_by_file_id` 写入 `task_runtime_evidence`，并被 `real_evidence_report` 计入 `taskRuntimeEvidence.successCount`
  - 已新增 Quark rapid-upload 模块 [quark_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/quark_fast_upload_live.py)：当 `fast_upload` 项具备可用本地文件和 `md5/sha1` 指纹时，任务运行阶段不再只做候选探针，而是会按 `upload/pre -> update/hash -> upload/finish` 发起真实 rapid-upload API 尝试，并把完成结果按 `executionMode=live` 落入任务结果与 `task_runtime_evidence`
  - [verify_quark_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_quark_fast_upload_live.py) 已验证 Quark rapid-upload 模块会真实走 `upload/pre / update/hash / upload/finish` 三段调用，并把 `verifyMode=finish_response` 与最终 `resolvedTargetName` 回写
  - Quark rapid-upload 模块现已继续补上 hash miss 后的真实二进制上传兜底：当 `update/hash` 未命中秒传时，会继续请求 `upload/auth`、执行 OSS multipart `PUT`、提交 `commit XML`，最后再走 `upload/finish`，不再把“秒传未命中”直接当作整次 live 尝试失败
  - [verify_quark_fast_upload_binary_fallback.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_quark_fast_upload_binary_fallback.py) 已验证 Quark hash miss 分支会真实触发 `upload/auth`、OSS `PUT/POST` 与 `upload/finish`，并把结果标记为 `mode=binary_upload_after_hash_miss`、`verifyMode=finish_response_after_binary_upload`
  - [verify_create_fast_upload_task_quark.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_task_quark.py) 已验证 `create_fast_upload_candidate_task.py --target-provider quark --auto-temp-file --sha1 auto` 在具备本地文件时会产出 `state=completed`、`completionKind=real_transfer`、`hasRealTransferSuccess=true` 的 Quark fast task 结果，并会在 `--evidence-dir` 下写出固定文件名证据包
  - [verify_quark_runtime_fast_upload_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_quark_runtime_fast_upload_evidence.py) 已验证 Quark 的 rapid-upload 成功样本会以 `executionMode=live`、`mode=rapid_upload_by_hash`、`verifyMode=finish_response` 写入 `task_runtime_evidence`，并被 `real_evidence_report` 计入 `taskRuntimeEvidence.successCount`
  - 已新增 UC rapid-upload 模块 [uc_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/src/cloudpan_sync/uc_fast_upload_live.py)：当 `fast_upload` 项具备可用本地文件和 `md5/sha1` 指纹时，任务运行阶段不再只做候选探针，而是会按 `upload/pre -> update/hash -> upload/finish` 发起真实 rapid-upload API 尝试，并把完成结果按 `executionMode=live` 落入任务结果与 `task_runtime_evidence`
  - [verify_uc_fast_upload_live.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_uc_fast_upload_live.py) 已验证 UC rapid-upload 模块会真实走 `upload/pre / update/hash / upload/finish` 三段调用，并把 `verifyMode=finish_response` 与最终 `resolvedTargetName` 回写
  - UC rapid-upload 模块现也已继续补上 hash miss 后的真实二进制上传兜底：当 `update/hash` 未命中秒传时，会继续请求 `upload/auth`、执行 OSS multipart `PUT`、提交 `commit XML`，最后再走 `upload/finish`，不再把“秒传未命中”直接当作整次 live 尝试失败
  - [verify_uc_fast_upload_binary_fallback.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_uc_fast_upload_binary_fallback.py) 已验证 UC hash miss 分支会真实触发 `upload/auth`、OSS `PUT/POST` 与 `upload/finish`，并把结果标记为 `mode=binary_upload_after_hash_miss`、`verifyMode=finish_response_after_binary_upload`
  - [verify_create_fast_upload_task_uc.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_task_uc.py) 已验证 `create_fast_upload_candidate_task.py --target-provider uc --auto-temp-file --sha1 auto` 在具备本地文件时会产出 `state=completed`、`completionKind=real_transfer`、`hasRealTransferSuccess=true` 的 UC fast task 结果，并会在 `--evidence-dir` 下写出固定文件名证据包
  - [verify_uc_runtime_fast_upload_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_uc_runtime_fast_upload_evidence.py) 已验证 UC 的 rapid-upload 成功样本会以 `executionMode=live`、`mode=rapid_upload_by_hash`、`verifyMode=finish_response` 写入 `task_runtime_evidence`，并被 `real_evidence_report` 计入 `taskRuntimeEvidence.successCount`
  - [verify_create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_candidate_task.py) 已验证 `create_fast_upload_candidate_task.py` 支持 `--sha1 / --gcid / --auto-temp-file`，会按已保存档案自动解析 `resolvedTargetParentId`，并能真实输出候选任务结果 JSON
  - 同一脚本现还额外验证了 `create_fast_upload_candidate_task.py` 支持 `--evidence-dir` 落六类固定文件名证据包，且会在导出 auth evidence 前真实刷新一次最新 auth validation / provider probe 证据
  - [verify_189cloud_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_189cloud_fast_upload_candidate_evidence.py) 与 [verify_quark_fast_upload_candidate_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_quark_fast_upload_candidate_evidence.py) 现已验证 candidate 样本会落出 `candidateOnly=true / candidateCount=1`，但不会再被 `real_evidence_report` 误记为真实 runtime success
  - `download_upload` 分支里的 `create_dir probe` 样本现在也已从“真实 runtime 成功/失败样本”里拆口径：运行期证据会单独落 `probeOnly=true`，`task_runtime_evidence / real_evidence_report / provider_status_matrix / 设置页摘要` 也会独立统计 `task_runtime_probe / runtime_probe / probeCount`，不再把“仅完成写探针、尚未真实传文件”的 probe-only 样本误算成 `runtime_success` 或 `runtime_failed`
  - `real_evidence_report` 的 provider 缺口提示现也会把 `probe-only` 单独写出来：当某个 provider 已经落到 `create_dir probe` 样本但还没有真实传输成功样本时，会明确提示“已有 probe-only 样本，但尚未记录到真实传输成功样本”，避免把“已探通写链路”和“已完成真实传输”混为一谈
  - [verify_aliyun_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_aliyun_runtime_probe_evidence.py) 现已验证 `aliyundrive_open_create_dir_probe` 样本会落出 `probeOnly=true / probeCount=1`，并且不会再被 `real_evidence_report` 误记为真实 `taskRuntimeEvidence.ok=true`
  - [verify_real_evidence_remediation_bundle.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_bundle.py) 现还额外验证了 `115_open / quark / baidu_netdisk` 的起手建档案命令会优先选 `manual_cookie`，`xunlei / pikpak` 会优先选 `manual_token`，并且不再把 `cookie_header / authorization` 这类重复鉴权字段继续塞进 stub 命令
  - [verify_real_evidence_remediation_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_remediation_ui.py) 已验证设置页已接入 `Real Evidence Next Steps` 面板、`loadRealEvidenceRemediationSummary()`、登录刷新和登出清理逻辑
  - 同一脚本现还额外验证了设置页摘要已消费 `recommendedAuthModes / webLoginUrl / requiredFieldHints / recommendedCreateCommand / recommendedBootstrapCommand / recommendedPatchProbeCommand / recommendedRefreshEvidenceCommand / recommendedRuntimeProbeCommand / recommendedFastCandidateCommand / providersCandidateOnly / runtimeCandidateOnly`
  - [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py)、[verify_task_runtime_evidence_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_api.py)、[verify_provider_status_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_status_settings_ui.py)、[verify_real_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_settings_ui.py) 与 [verify_task_runtime_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_settings_ui.py) 现还额外验证了 candidate 样本已在报告/API/设置页中走独立统计字段，不再混入 `runtime_success / task_runtime`
  - [verify_real_evidence_report.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_report.py) 现还额外验证了 `probe-only` 样本已在报告/API 中走独立统计字段：摘要会带 `taskRuntimeProbeProviderCount / taskRuntimeProbeCount`，单 provider 行也会带 `probeCount / probeProfiles`
  - 设置页 `Real Evidence` 摘要现也已补上 `latestValidationProfiles / latestProbeProfiles`，可直接看出当前真实证据汇总是基于多少个最新 validation / probe 档案样本得出的
  - [verify_real_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_real_evidence_settings_ui.py) 现还额外验证了设置页 `Real Evidence` 摘要已显示 `latestValidationProfiles / latestProbeProfiles`
  - 设置页 `Provider Status Matrix` 面板现还额外补上 `liveProbeOk / runtimeEvidenceProviders / runtimeFailedProviders`，可以直接看出当前有多少 provider 已经跑出 live probe 成功样本、真实 runtime 成功样本与失败样本
  - [verify_provider_status_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_status_settings_ui.py) 现还额外验证了设置页状态矩阵摘要已显示上述 probe/runtime provider 级聚合字段
  - 设置页 `Provider Status Matrix` 面板现还额外补上 `runtimeProbeProviders / runtimeProbe`，可以直接区分“已经有 probe-only 运行样本”与“已经有真实传输成功/失败样本”
  - 设置页 `Provider Status Matrix` 面板现还额外补上 `overwriteReady / autoRenameReady`，与状态矩阵 summary / 导出文档中的冲突能力就绪计数保持一致
  - [verify_provider_status_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_status_settings_ui.py) 现还额外验证了设置页状态矩阵摘要已显示 `overwriteReady / autoRenameReady`
  - 设置页 `Provider Status Matrix` 面板现还额外补上 `runtimeSuccess / runtimeFailed`，与状态矩阵 summary 中已有的真实运行样本成功/失败总数保持一致
  - [verify_provider_status_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_status_settings_ui.py) 现还额外验证了设置页状态矩阵摘要已显示 `runtimeSuccess / runtimeFailed`
  - 设置页 `Provider Status Matrix` 面板现还额外补上 `runtimeConflictHandledProviders`，可以直接看出当前有多少 provider 已经产出真实运行期冲突处理样本
  - [verify_provider_status_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_provider_status_settings_ui.py) 现还额外验证了设置页状态矩阵摘要已显示 `runtimeConflictHandledProviders`
  - 设置页 `Task Runtime Evidence` 最近样本简讯现还额外补上 `requiredAuth / error`，失败或 blocked 样本不必再只靠 `mode/executionMode` 猜测缺什么鉴权或哪一步报错
  - [verify_task_runtime_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_settings_ui.py) 现还额外验证了设置页 runtime 简讯已显示 `requiredAuth / error`
  - 设置页 `Task Runtime Evidence` 摘要与最近样本简讯现还额外补上 `probeProviders / probe / probeOnly`，方便直接识别“这是探针留证，不是实际文件已完成传输”
  - 任务运行摘要现也已把 `probe-only / candidate-only / real_transfer` 拆开：`build_task_summary()` 会额外返回 `probeOnlyCount / candidateOnlyCount / liveSuccessCount / liveFailedCount / completionKind / hasRealTransferSuccess`，像 `aliyundrive_open_create_dir_probe` 这类仅探针成功的任务会明确显示 `completionKind=probe_only`，不再只剩一个笼统的 `completed`
  - [verify_aliyun_runtime_probe_evidence.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_aliyun_runtime_probe_evidence.py) 现还额外验证了真实 `detailView.summary` 已带 `probeOnlyCount=1` 与 `completionKind=probe_only`
  - 任务终态现也已按完成口径拆开：全量 `probe-only` 结果会落成 `completed_probe_only`，全量 `candidate-only` 结果会落成 `completed_candidate_only`，而真实传输成功仍保持 `completed`；这样脚本输出、API 明细和队列页状态不会再把“只留到探针/候选证据”的任务混成真正传输完成
  - [verify_create_runtime_probe_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_runtime_probe_task.py) 现已验证 `create_runtime_probe_task.py` 输出会带 `state=completed_probe_only` 与 `summary.completionKind=probe_only`；[verify_create_fast_upload_candidate_task.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_create_fast_upload_candidate_task.py) 也同步验证了 `state=completed_candidate_only` 与 `summary.completionKind=candidate_only`
  - `listView / detailView` 现也已把 `completionKind / hasRealTransferSuccess` 直接抬到顶层，`detailView` 还额外补回顶层 `state`；脚本或前端如果只想看“当前是什么完成口径”，不必每次再深入 `summary`
  - [verify_task_views_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_views_api.py) 现还额外验证了 `detailView.state`、`detailView.completionKind` 已返回，且顶层 `state` 会和 `summary.state` 保持一致
  - 设置页 `Task Runtime Evidence` 最近样本简讯现还额外补上 `verifyMode`，可直接看出真实运行样本是靠哪条 verify 路径落证据
  - [verify_task_runtime_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_settings_ui.py) 现还额外验证了设置页 runtime 简讯已显示 `verifyMode`
  - 设置页 `Task Runtime Evidence` 最近样本简讯现还额外补上 `path / resolvedTargetName`，排查同名冲突改名或目标落点时不必再只靠 `conflictAction` 猜文件最终写到哪里
  - [verify_task_runtime_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_settings_ui.py) 现还额外验证了设置页 runtime 简讯已显示 `path / resolvedTargetName`
  - 设置页 `Task Runtime Evidence` 最近样本简讯现还额外补上 `riskHint`，blocked 或失败样本可直接看到当前运行判定出来的风险提示
  - [verify_task_runtime_evidence_settings_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_settings_ui.py) 现还额外验证了设置页 runtime 简讯已显示 `riskHint`
  - `Task Runtime Evidence` Markdown / 导出链最近样本行现也已补上 `riskHint / verifyNote`，离线对账 blocked、失败或已完成验证样本时不必再只靠 `error / verifyMode` 猜测运行期上下文
  - [verify_task_runtime_evidence_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_runtime_evidence_api.py) 现还额外验证了 `GET /api/task_runtime_evidence_markdown` 样本行已带 `riskHint / verifyNote`
  - 队列页任务最近结果简讯现也已补上 `requiredAuth / error`，像 `189cloud` 只读阻断或缺写鉴权场景可直接在任务列表看到缺哪些鉴权以及后端返回的错误标识
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 已验证队列页 `renderTaskList()` 最近结果行已显示 `requiredAuth / error`
  - 队列页任务最近结果简讯现还额外补上 `verifyNote`，probe-only、post-verify 成功或尚未进入验证的样本可直接在列表看出当前验证说明
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了队列页 `renderTaskList()` 最近结果行已显示 `verifyNote`
  - 队列页任务状态 pill 现也已补上 `probe=`、`candidate=` 与 `completion=`，即使 `state=completed`，也能一眼看出这次完成的是 `probe_only` 还是 `real_transfer`
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了队列页 `renderTaskList()` 已显示 `probe / candidate / completion` 三个摘要 pill
  - 队列页任务状态 pill 现还额外补上 `live=` 与 `liveFailed=`，用户看到 `done=1/1` 时也能同时知道其中到底有多少条是真实传输成功、多少条是真实传输失败，不再把“有探针/候选结果的 done”误读成真实传输完成
  - 队列页状态 pill 样式现也已补上 `completed_probe_only / completed_candidate_only`，这两类“留到证据但未真实传输完成”的终态会沿用 warning 色系，避免在视觉上和真正的 `completed` 绿态混在一起
  - 队列页当前已改为优先消费 `/api/tasks` 返回的 `listItems / latestResults` 视图，不再把详情态 `results` 当成列表页唯一数据源，最近结果简讯终于能稳定显示真实运行样本
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了 `loadTasks()` 已优先读取 `listItems`，且 `renderTaskList()` 已优先显示 `latestResults`
  - 列表视图 `build_task_list_view()` 现也已补回 `pendingItems`，待处理页在切到轻量 `listItems` 后不再因为缺少 `plan.pendingItems` 而丢失待处理条目
  - [verify_task_views_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_views_api.py) 现还额外验证了 `/api/tasks` 的 `listItems[].pendingItems` 已返回，且列表视图仍保留 `latestResults`
  - 待处理页现也已把 `pendingItems` 里的 `conflictSupportStatus / conflictNote` 真正透传到渲染层，不再只在代码里准备显示文案却因为 `rows` 丢字段而始终空白
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了待处理页 `renderPendingList()` 已携带并显示 `conflictSupportStatus / conflictNote`
  - `pendingItems` 现还额外补回 `availableFastInputs`，待处理页可直接同时看到“当前已有指纹”和“仍缺哪些 fast-upload 输入”，不再只剩一侧 `missing`
  - [verify_task_views_api.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_views_api.py) 现还额外验证了真实 `pending_manual` 任务的 `listItems[].pendingItems[].availableFastInputs` 已返回；[verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 也同步验证了待处理页已显示 `available / missing`
  - 队列页任务守卫行现也已直接显示 `riskReason`，可一眼看出当前是 `guard_blocked`、`awaiting_acknowledgement` 还是 `too_many_pending_manual_items`，不必再只靠 state / warning 猜测
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了队列页 `renderTaskList()` 已显示 `riskReason`
  - 队列页任务守卫行现还额外补上 `awaitingAcknowledgement / riskPaused`，可直接区分“当前仍待确认才能继续”与“已因风险暂停”的状态位
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了队列页 `renderTaskList()` 已显示 `awaitingAcknowledgement / riskPaused`
  - 队列页任务守卫行现也已把 `guard.targetProfile` 的 `profileReady / writeReady` 与缺口提示抬出来，像 `189cloud` share-only 档案这类“目标档案不可写”场景不必再点回授权页才能看懂为什么被硬拦住
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了队列页 `renderTaskList()` 已显示 `targetProfileReady / targetWriteReady` 以及对应缺口提示
  - 队列页任务 detail 行现也已直接显示 `targetProfile` 名称与 `profileReady / writeReady` 摘要，不再只剩 `targetProfileId` 这种需要用户自己反查的内部标识
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了队列页 `renderTaskList()` detail 行已显示 `targetProfile` 名称与 readiness 摘要
  - 待处理页 meta 行现也已补上 `conflictPolicy`，用户查看待处理项时可直接知道当前是按 `overwrite_existing` 还是 `auto_rename_new` 在评估，不必再回任务表单反查
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了待处理页 `renderPendingList()` 已携带并显示 `conflictPolicy`
  - 队列页任务 detail 行现对 `profileReady / writeReady` 改成诚实显示：只有 `guard.targetProfile` 真返回这两个状态位时才显示 `true/false`，否则显示 `(unknown)`，不再把“没有目标档案信息”误渲染成 `true`
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了队列页 `renderTaskList()` detail 行已改为通过 `profileReadyText / writeReadyText` 诚实渲染 readiness 摘要
  - 队列页最近结果简讯现也已补上 `row.note`，像 probe-only 命中、fallback 未命中、blocked 原因或“当前仍走 mock/download fallback”的解释性说明可直接在列表层看到
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了队列页 `renderTaskList()` 最近结果行已显示 `row.note`
  - 待处理页 meta 行现也已补上所属任务的 `state / riskReason`，看单条 pending 项时不必再切回队列页才能知道它当前是 `ready`、`awaiting_acknowledgement` 还是被哪类风险原因拦住
  - [verify_task_list_runtime_ui.py](E:/Workspace/VSCode/CloudPan%20Sync/scripts/verify_task_list_runtime_ui.py) 现还额外验证了待处理页 `renderPendingList()` 已携带并显示所属任务的 `state / riskReason`
