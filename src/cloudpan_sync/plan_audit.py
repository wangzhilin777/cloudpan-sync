from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .provider_registry import build_provider_registry
from .provider_research import build_provider_research_index


@dataclass
class AuditItem:
    key: str
    title: str
    status: str
    evidence: str
    gaps: str

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "title": self.title,
            "status": self.status,
            "evidence": self.evidence,
            "gaps": self.gaps,
        }


def run_plan_audit() -> dict[str, object]:
    provider_count = len(build_provider_registry())
    research_count = len(build_provider_research_index())

    items = [
        AuditItem(
            key="M1",
            title="独立项目骨架",
            status="done",
            evidence="后端/前端/登录/i18n/启动脚本已存在并可运行。",
            gaps="无",
        ),
        AuditItem(
            key="M2",
            title="ProviderAdapter 与能力模型",
            status="done",
            evidence="ProviderAdapter、provider registry、mock plan API 已实现。",
            gaps="无",
        ),
        AuditItem(
            key="M3",
            title="授权系统",
            status="done",
            evidence="授权存储、脱敏展示、校验与网页登录引导 API 已实现；授权列表接口现会返回 provider-aware 的 `missingFieldHints / profileReady`，并补充 `resolvedParentId / resolvedFileId`，可在点击 validate 前先暴露档案缺口并直接复用解析后的默认值；现也支持直接编辑已有 auth profile 并重新校验，补字段时无需删除重建；其中 189Cloud 账号级写鉴权现已额外支持从 captured headers/curl 文本提取 `accessToken/signature/date` 后回填现有档案。",
            gaps="真实网页登录抓取自动化尚未实现。",
        ),
        AuditItem(
            key="M4",
            title="光鸭 Provider",
            status="partial",
            evidence="光鸭预检（md5/gcid）已实现，目录、metadata、create_dir、live fast-upload inventory check，以及任务运行阶段基于 targetProfileId + localPath 的 fallback live attempt 已支持真实二进制上传链路（guangyaclient file_upload / upload_token + cdn_upload）。上传成功后现会继续尝试 post-upload verify：优先用返回 fileId 做 live metadata 确认，拿不到 fileId 时退回 parentId + 文件名的 live list 确认。失败时会返回更明确的授权/输入/风控/限流类风险提示；save-time/provider-aware 校验已补 `parent_id / parentFileId / dirId / pid` 等常见别名兼容，并会直接返回 `requiredFieldHints`。",
            gaps="仍缺稳定的真实在线联调成功样本，因此 M4 继续保持 partial。",
        ),
        AuditItem(
            key="M5",
            title="首批常用网盘接入",
            status="partial",
            evidence=f"首批 provider 已补齐到 {provider_count} 个，研究索引 {research_count} 条；其中 aliyundrive_open 已支持基于已保存 access token + domainId/driveId 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实小文件上传链路：当前可按 `overwrite_existing / auto_rename_new` 选择同名处理，通过 `create -> upload_url PUT -> complete` 完成 Aliyun Drive Open 本地文件直传，并在成功后继续做 `metadata_by_file_id / list_by_parent_name` 校验；123_open 已支持基于已保存 token 的真实 list/metadata(parentFileId scoped)/create_dir 尝试，并在任务运行阶段补上真实小文件上传链路：当前可通过 `create -> get_upload_url -> PUT -> upload_complete -> upload_async_result` 完成直传，`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名，并在成功后继续做 `metadata_by_file_id / list_by_parent_name` 校验；baidu_netdisk 已支持基于 access token 或 cookie 的保守 live list/metadata/create_dir 尝试，并在任务运行阶段补上真实小文件上传链路：当前可通过 `precreate -> superfile2 tmpfile -> create` 完成直传，`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名，并在成功后继续做 `metadata_by_file_id / list_by_parent_name` 校验；115_open 已支持基于已保存 cookie 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针，以及基于 `open/upload/init + sign_check` 的真实 rapid-upload API 尝试：当存在 `localPath + sha1` 时会发起 live init call，并区分“秒传命中”与“仍需后续二进制上传”两类结果；xunlei 已支持基于 token + device headers 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上本地文件直传链路：当前会先走 `/drive/v1/files` create-by-hash，再在 hash miss 时继续进入返回的 S3-compatible resumable binary upload session，`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名；pikpak 已支持基于 token 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上本地文件直传链路：当前会先走 `/drive/v1/files` create-by-hash，再在 hash miss 时继续进入返回的 S3-compatible resumable binary upload session，`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名；quark 已支持基于 cookie + pwdId 的分享链路 live list/metadata(MD5 via file/download) 与 create_dir 尝试，并在任务运行阶段补上先走 `upload/pre -> update/hash`，再在 hash miss 时继续 `upload/auth -> multipart PUT -> commit -> upload/finish` 的真实本地文件上传兜底；uc 已支持基于 cookie + pwdId 的分享链路 live list/metadata(MD5 via file/download) 与 create_dir 尝试，并在任务运行阶段补上先走 `upload/pre -> update/hash`，再在 hash miss 时继续 `upload/auth -> multipart PUT -> commit -> upload/finish` 的真实本地文件上传兜底；189cloud 已支持基于分享参数的真实 list/metadata 尝试，且 `createFolder.action` 现已接入账号级 `AccessToken/Signature/Date` 写目录尝试，并在任务运行阶段补上基于 `createUploadFile -> fileCommitUrl` 的真实 rapid-upload API 尝试：当存在 `localPath + md5 + account-level write auth` 时会发起 live create/commit call，并区分“秒传命中”与“仍需后续二进制上传”两类结果；状态矩阵现已额外显式量化 create_dir 能力、fast_check 能力、同名冲突策略支持状态、task runtime 轨道以及 runtime 冲突处理样本计数，当前首批 10 个 provider 都已能在矩阵中量化为 `fast_check=true`，并区分 `overwrite_existing`/`auto_rename_new` 的 `supported / downgrade_to_auto_rename / probe_only_runtime_write_check / unsupported`。",
            gaps="189Cloud 目前仍缺真实在线成功样本；账号级写鉴权虽已补到 captured headers/curl 提取与回填脚本，且现在也已补到真实 rapid-upload API 尝试，但稳定可复用的真实来源样本仍缺，shareCode/accessCode-only 档案依旧不可写，完整二进制上传 fallback 也仍未接入。115 Open 虽已补上真实 rapid-upload API 尝试，但完整二进制上传 fallback 仍未接入；Quark 与 UC 虽已补上 hash-miss 后的二进制上传兜底，但 download_upload 策略仍未升级成直接本地文件上传链路；PikPak、Aliyun Drive Open、123Pan Open、Baidu Netdisk、115 Open、Xunlei、Quark、UC、189Cloud 的真实秒传 API 成功样本仍缺。",
        ),
        AuditItem(
            key="M6",
            title="互传任务规划",
            status="done",
            evidence="selectedRoots、executionGroups、pendingItems 与阈值策略已实现。",
            gaps="无",
        ),
        AuditItem(
            key="M7",
            title="受控执行与 UI",
            status="done",
            evidence="任务状态机、队列/待处理/网盘能力/设置页签、授权弹窗、tip、折叠区与中英文文案已接入当前页面；授权列表会直接显示 `profileReady/missingFieldHints` 与最近一次 validation riskHint，任务表单和 live probe 请求会优先使用档案返回的 `resolvedParentId / resolvedFileId`，并支持进入编辑态更新现有档案。",
            gaps="无",
        ),
        AuditItem(
            key="P-REAL",
            title="真实联调验证",
            status="todo",
            evidence="已具备本地 mock 验证链路，并新增真实证据状态报告与任务运行真实样本持久化能力，可按 provider 量化当前已保存的 auth/list/metadata/create_dir/task_runtime 真实证据覆盖；其中 Guangya 已接真实上传链路，aliyundrive_open、123_open、baidu_netdisk、xunlei 与 pikpak 现也已接任务运行阶段真实本地文件上传链路，quark、uc、115_open 与 189cloud 现也已接任务运行阶段真实 rapid-upload API 尝试，189cloud 也已能在 share-only 场景落出 blocked probe 样本，并在账号级鉴权齐备时发起 createFolder.action 写目录尝试。",
            gaps="尚未提供首批 provider 的真实联调成功证据（认证、目录、元数据、秒传/降级路径）；任务运行阶段虽已支持成功/失败样本持久化，但当前仍缺足够的真实成功样本来收敛 P-REAL。",
        ),
    ]

    done = sum(1 for x in items if x.status == "done")
    partial = sum(1 for x in items if x.status == "partial")
    todo = sum(1 for x in items if x.status == "todo")
    feature_items = [item for item in items if item.key != "P-REAL"]
    feature_done = sum(1 for item in feature_items if item.status == "done")
    feature_partial = sum(1 for item in feature_items if item.status == "partial")
    feature_completion_percent = round(((feature_done + feature_partial * 0.5) / len(feature_items)) * 100, 1)
    strict_completion_percent = round(((done + partial * 0.5) / len(items)) * 100, 1)

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "done": done,
            "partial": partial,
            "todo": todo,
            "providerCount": provider_count,
            "researchCount": research_count,
            "featureMilestoneCount": len(feature_items),
            "strictMilestoneCount": len(items),
            "featureCompletionPercent": feature_completion_percent,
            "strictCompletionPercent": strict_completion_percent,
        },
        "items": [item.to_dict() for item in items],
    }


def to_markdown(audit: dict[str, object]) -> str:
    summary = dict(audit.get("summary") or {})
    lines: list[str] = []
    lines.append("# CloudPan Sync 计划完成度审计报告")
    lines.append("")
    lines.append(f"- 生成时间：`{audit.get('generatedAt', '')}`")
    lines.append(
        f"- 汇总：`done={summary.get('done', 0)}` `partial={summary.get('partial', 0)}` `todo={summary.get('todo', 0)}`"
    )
    lines.append(
        f"- 进度口径：`featureCompletionPercent={summary.get('featureCompletionPercent', 0)}` `strictCompletionPercent={summary.get('strictCompletionPercent', 0)}`"
    )
    lines.append(
        f"  - `featureCompletionPercent` = 只按 `M1-M7` 主功能里程碑计分，`done=1`、`partial=0.5`。"
    )
    lines.append(
        f"  - `strictCompletionPercent` = 把 `P-REAL` 真实联调一起纳入总验收后计分，`done=1`、`partial=0.5`。"
    )
    lines.append(
        f"- Provider覆盖：`providerCount={summary.get('providerCount', 0)}` `researchCount={summary.get('researchCount', 0)}`"
    )
    lines.append("")
    lines.append("## 审计明细")
    lines.append("")
    for item in audit.get("items", []):
        row = dict(item or {})
        lines.append(f"### {row.get('key', '')} - {row.get('title', '')}")
        lines.append(f"- 状态：`{row.get('status', '')}`")
        lines.append(f"- 证据：{row.get('evidence', '')}")
        lines.append(f"- 缺口：{row.get('gaps', '')}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
