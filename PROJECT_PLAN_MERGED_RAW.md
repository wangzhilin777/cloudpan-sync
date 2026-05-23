# CloudPan Sync 多网盘互传计划文档

## 1. 项目定位

`CloudPan Sync` 是一个常用网盘之间的互传控制台。

核心目标不是“多个网盘传到光鸭”，而是支持常用网盘之间互相传输。光鸭网盘只是首批重点支持的 provider 之一，不能作为唯一目标端或项目中心。

项目优先支持秒传。秒传失败后，根据用户配置的文件大小阈值决定是否自动下载后上传；超过阈值或疑似封控时进入待处理队列，由用户确认。

## 2. 核心原则

- 独立新项目，不继承 `CloudPan Bridge` 的产品结构。
- 每个网盘都是同级 `ProviderAdapter`，既可能作为来源，也可能作为目标。
- AList/OpenList 只作为授权方式、driver 思路和字段经验的参考，不作为项目内核。
- 网盘 API 优先找官方文档；没有官方文档时，参考最新开源项目、浏览器脚本、网页请求和逆向项目。
- 秒传能力必须按网盘单独确认，不假设所有网盘都支持同一套 hash。
- 页面面向小白用户，默认展示关键操作和状态，复杂字段用 tip、折叠区、弹窗向导承载。
- 每个可验证里程碑单独提交，中文 commit message。

## 3. Provider 设计

### 3.1 ProviderAdapter

每个网盘实现统一适配器：

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

适配器能力按实际情况声明：

```text
bidirectional   可作为来源，也可作为目标
sourceOnly      只能作为来源
targetOnly      只能作为目标
experimental    资料未完全验证或接口可能不稳定
```

### 3.2 FingerprintSet

秒传和校验相关字段统一归一化保存，但字段名保持英文：

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

不同网盘声明自己秒传需要的字段，例如：

```text
fastUploadInputs:
- md5
- size
- name
```

或：

```text
fastUploadInputs:
- gcid
- size
```

## 4. 授权方案

### 4.1 授权模式

支持多种授权来源：

```text
official_oauth          官方 OAuth 或开放平台授权
web_login_capture       打开网页登录页，用户登录后抓取必要 cookie/header/localStorage
manual_cookie           手动粘贴 cookie
manual_token            手动粘贴 token
openlist_style_reference 参考 AList/OpenList 配置字段
```

### 4.2 授权流程

- 用户在页面选择网盘。
- 弹出授权向导。
- 根据 provider 推荐方式展示网页登录、手动 token、手动 cookie 或高级字段。
- 保存前做最小验证，例如读取用户信息或列根目录。
- 授权信息本地保存，页面脱敏显示。
- 授权失败时显示明确原因：未登录、cookie 过期、缺少 header、验证码、风控、接口变更。

## 5. 秒传与 fallback 策略

### 5.1 执行优先级

```text
1. 尝试获取来源文件元数据和 fingerprint
2. 判断目标网盘是否支持对应秒传字段
3. 支持则优先秒传
4. 秒传失败后按 fallback 策略处理
5. 不满足条件则进入待处理队列
```

### 5.2 fallback 配置

用户可配置下载后上传阈值：

```text
0MB      全部手动确认
200MB    小于等于 200MB 自动下载后上传
1GB      小于等于 1GB 自动下载后上传
```

超过阈值的文件进入待处理队列。

### 5.3 封控保护

默认策略：

- 低并发。
- 批次间隔。
- 连续失败自动暂停。
- 疑似风控响应自动暂停。
- 大文件 fallback 需要确认。
- 不做无限重试。
- 不绕过验证码、风控或账号安全限制。

## 6. 文件夹传输顺序

用户勾选多个顶层文件夹时，按勾选顺序处理。

每个顶层文件夹内部先处理最底层目录，再向上处理。

示例：

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

执行顺序：

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

这个顺序作为核心测试要求，不允许后续被改成普通扁平队列。

## 7. 页面设计

### 7.1 页面分组

主页面使用 Tab 分组：

```text
新建任务
授权管理
传输队列
待处理
网盘能力
设置
```

### 7.2 新建任务流程

新建任务分步骤展示：

```text
选择来源网盘
选择目标网盘
选择来源文件夹
扫描分析
确认策略
执行任务
```

### 7.3 易用性要求

- 不做一页密密麻麻的信息堆叠。
- 复杂信息默认折叠。
- 字段说明尽量用 hover tip。
- 授权流程用弹窗向导。
- 错误信息要能让普通用户看懂。
- 技术字段保持英文，解释文字支持中文和英文。

## 8. 中英文支持

默认中文界面，支持英文切换。

保留英文专用名称：

```text
Provider
Adapter
Fingerprint
md5
sha1
gcid
etag
pickcode
rapid upload
fallback
token
cookie
header
```

普通说明文案提供中英文：

```text
zh: 当前文件缺少目标网盘秒传所需的 md5。
en: This file is missing the md5 required by the target provider for rapid upload.
```

## 9. Provider 研究流程

每个网盘单独建立研究记录：

```text
provider name
official docs
latest open-source references
web request evidence
auth fields
list API
metadata API
fast upload API
upload API
risk notes
last verified date
support status
```

资料优先级：

```text
1. 官方 API 文档
2. 最新开源项目
3. 网页端请求
4. 浏览器脚本
5. 旧项目资料
```

资料太旧或没有真实验证时，标记为 `experimental`。

## 10. 首批里程碑

### Milestone 1：独立项目骨架

目标：

- 创建 FastAPI + 静态前端项目。
- 增加本地 admin 登录密码。
- 增加基础 i18n。
- 增加 Windows 启动脚本。

提交：

```text
初始化 CloudPan Sync 独立互传项目
```

### Milestone 2：ProviderAdapter 与能力模型

目标：

- 实现 `ProviderAdapter` 抽象。
- 实现 `FingerprintSet`。
- 实现 provider registry。
- 用 mock provider 验证任意来源到任意目标的 transfer plan。

提交：

```text
建立多网盘互传能力模型
```

### Milestone 3：授权系统

目标：

- 实现 `AuthProfile`。
- 支持手动 cookie/token。
- 支持网页登录抓取授权。
- 授权信息脱敏显示。
- 授权保存前做最小验证。

提交：

```text
建立多网盘授权模型
```

### Milestone 4：光鸭 provider

目标：

- 参考 `C:\Users\ChowYu\Desktop\新建文件夹 (3)\秒传.js`。
- 实现光鸭授权验证。
- 实现目录读取。
- 实现 md5/gcid 秒传预检。
- 实现错误码和风控提示。

提交：

```text
接入光鸭网盘基础能力
```

### Milestone 5：首批常用网盘研究与接入

目标：

- 选择 2-3 个常用网盘。
- 查找官方文档或最新开源/逆向项目。
- 先完成授权、列目录、元数据获取。
- 再判断是否支持真实秒传。

提交示例：

```text
补充首批常用网盘能力研究
接入某网盘目录与元数据能力
```

### Milestone 6：互传任务规划

目标：

- 实现秒传优先策略。
- 实现 fallback 大小阈值。
- 实现待处理队列。
- 实现底层优先文件夹执行顺序。

提交：

```text
实现网盘互传任务规划
```

### Milestone 7：受控执行与 UI 打磨

目标：

- 实现暂停、继续、重试。
- 实现封控暂停。
- 实现队列状态展示。
- 完善 Tab、二级菜单、弹窗授权、tip、折叠区。
- 完成中英文文案。

提交：

```text
完成受控互传执行与易用页面
```

## 11. 测试策略

不改一点就全量测试，按里程碑测试。

### 单元测试

覆盖：

```text
provider 能力判断
fingerprint 归一化
秒传策略判断
fallback 阈值
目录底层优先排序
授权字段脱敏
错误码分类
```

### API 测试

覆盖：

```text
登录保护
授权保存
授权验证
provider registry
任务 plan 创建
队列状态查询
```

### UI smoke

覆盖：

```text
登录
Tab 切换
授权弹窗
任务向导
待处理折叠
语言切换
```

### 真实联调

原则：

```text
小文件
少量目录
低并发
先预检
再执行
明确区分 mock 成功和真实网盘成功
```

## 12. 明确不做

- 不把项目做成“多网盘到光鸭”。
- 不直接拿 AList/OpenList 当内核。
- 不默认全自动大批量下载上传。
- 不绕过验证码或风控。
- 不把未验证的秒传能力写成已支持。
- 不在每个小改动后跑全量测试浪费 token。


---

# CloudPan Sync 网盘支持范围补充

## 首批必做 Provider

这些作为第一阶段核心目标，先做到“授权 + 列目录 + 元数据/hash 获取 + 互传规划”，再逐个补真实秒传和上传执行。

| 网盘 | Provider Key | 优先原因 | 首期能力目标 |
|---|---|---|---|
| 光鸭网盘 | `guangya` | 用户明确要求，新出的网盘，需要单独支持 | 网页授权、列目录、`md5/gcid` 秒传预检、上传 fallback |
| 阿里云盘 Open | `aliyundrive_open` | 常用，OpenList/AList 资料较多 | OAuth/refresh token、列目录、hash 能力判断、秒传研究 |
| 115 网盘 | `115` / `115_open` | 常用，秒传资料较多 | Cookie/扫码或 Open API、列目录、秒传能力研究 |
| 天翼云盘 189 | `189cloud` | 常用，已有生态参考 | 登录授权、列目录、`hash_info.md5` 类字段提取 |
| 百度网盘 | `baidu_netdisk` | 常用，但封控和限速风险高 | OAuth/cookie 授权、列目录、保守 fallback、秒传能力研究 |
| 夸克网盘 | `quark` | 近年常用，网页端/API 逆向资料多 | Cookie 授权、列目录、元数据提取 |
| UC 网盘 | `uc` | 与夸克体系接近，适合一起研究 | Cookie 授权、列目录、元数据提取 |
| 迅雷云盘 | `xunlei` | `gcid` 相关秒传价值高 | 登录授权、列目录、`gcid` 提取、秒传研究 |
| PikPak | `pikpak` | 与迅雷生态相关，常见跨盘需求 | 账号授权、列目录、`gcid/hash` 研究 |
| 123 云盘 | `123pan` / `123_open` | 有开放平台和常用个人盘场景 | OAuth/token、列目录、上传/秒传能力研究 |

## 第二批 Provider

这些放在基础架构稳定后接入，避免第一阶段摊太大。

| 网盘 | Provider Key | 首期定位 |
|---|---|---|
| 中国移动云盘 | `139yun` | 常用运营商网盘，先做授权和目录 |
| 沃家云盘 / 联通云盘 | `wopan` | 常用运营商网盘，先做授权和目录 |
| 腾讯微云 | `weiyun` | 常用但接口稳定性需研究 |
| 蓝奏云 / 新蓝奏云 | `lanzou` / `new_lanzou` | 轻量分享盘，适合做分享资源导入 |
| Google Drive | `google_drive` | 国际常用盘，API 清晰 |
| OneDrive | `onedrive` | 国际常用盘，API 清晰 |
| Dropbox | `dropbox` | 国际常用盘，API 清晰 |
| MEGA | `mega` | 常用国际盘，先做研究候选 |
| WebDAV | `webdav` | 很多私有网盘兼容，性价比高 |
| S3 兼容存储 | `s3` | 适合对象存储互传，不等同普通网盘 |

## 首批实现顺序

1. `guangya`：先按你给的 `秒传.js` 做，拿到真实光鸭路径。
2. `aliyundrive_open`：优先官方/Open API，适合作为规范化 provider 样板。
3. `115`：重点研究秒传和跨盘复制资料。
4. `189cloud`：常用且适合和光鸭、阿里做互传验证。
5. `quark` + `uc`：同体系一起研究网页登录抓取。
6. `xunlei` + `pikpak`：重点研究 `gcid`、离线/秒传能力。
7. `baidu_netdisk`：最后放入首批执行，原因是封控、限速、授权复杂度更高。

## Provider 状态标记

每个网盘都必须有状态，不允许页面直接写“已支持”但背后没验证。

```text
planned        已列入计划，未接入
researching    正在查官方文档/开源项目/网页请求
auth_ready     授权可用
list_ready     可列目录
metadata_ready 可获取文件元数据/hash
fast_check     可做秒传预检
fast_ready     真实秒传已小样本验证
fallback_ready 下载后上传已验证
risky          容易封控或接口不稳定
experimental   资料不足或未真实联调
```

## 每个 Provider 的研究记录字段

```text
providerKey
displayName
officialDocsUrl
openSourceRefs
webLoginUrl
authModes
listApiEvidence
metadataApiEvidence
fastUploadEvidence
requiredFingerprints
fallbackModes
riskNotes
lastVerifiedAt
supportStatus
```

## 资料依据

- OpenList 当前 driver 目录明确列出阿里云盘、115、百度、189、139、沃盘、123、蓝奏、腾讯微云、PikPak、迅雷、夸克、UC、WebDAV、S3、Google Drive、Dropbox、MEGA 等存储类型，可作为“有哪些常见 provider 值得研究”的参考：[OpenList Storage Drivers](https://oplist.org/guide/drivers/)
- OpenList 的 115 文档提到 115 与阿里云盘 Open 的增强秒传/复制场景，可作为 115 秒传研究入口，但只参考，不作为 CloudPan Sync 内核：[115 Cloud / Share - OpenList Docs](https://doc.openlist.team/guide/drivers/115)
- AList 文档也列出类似常用盘范围，并说明它是多存储文件列表程序，可作为 provider 名单和授权字段参考：[AList Introduction](https://alistgo.com/guide/)

