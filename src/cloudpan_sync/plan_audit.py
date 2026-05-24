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
            evidence="授权存储、脱敏展示、校验与网页登录引导 API 已实现；授权列表接口现会返回 provider-aware 的 `missingFieldHints / profileReady`，并补充 `resolvedParentId / resolvedFileId`，可在点击 validate 前先暴露档案缺口并直接复用解析后的默认值；现也支持直接编辑已有 auth profile 并重新校验，补字段时无需删除重建。",
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
            evidence=f"首批 provider 已补齐到 {provider_count} 个，研究索引 {research_count} 条；其中 aliyundrive_open 已支持基于已保存 access token + domainId/driveId 的真实 list/metadata/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；123_open 已支持基于已保存 token 的真实 list/metadata(parentFileId scoped)/create_dir 尝试，并在任务运行阶段补上真实 create_dir 写探针；189cloud 已支持基于分享参数的真实 list/metadata 尝试，并会在 create_dir API/probe 中明确返回当前 shareCode/accessCode 链路为只读、仍需 AccessToken/Signature/Date 这类账号级 OAuth 头；115_open 已支持基于已保存 cookie 的真实 list/metadata/create_dir 尝试，baidu_netdisk 已支持基于 access token 或 cookie 的保守 live list/metadata/create_dir 尝试，xunlei 已支持基于 token + device headers 的真实 list/metadata/create_dir 尝试，pikpak 已支持基于 token 的真实 list/metadata/create_dir 尝试，quark 与 uc 已支持基于 cookie + pwdId 的分享链路 live list/metadata(MD5 via file/download) 与 create_dir 尝试；状态矩阵现已额外显式量化 create_dir 能力以及 task runtime 轨道，当前可区分 `runtime_active / runtime_candidate / runtime_blocked`。",
            gaps="当前除 Guangya、aliyundrive_open 与 123_open 外，115_open、baidu_netdisk、xunlei、pikpak、quark、uc 仍缺真实任务运行写链路与在线成功样本验证；189Cloud 当前仍停留在 shareCode/accessCode 只读链路，尚未接入账号级 OAuth 写接口；Quark/UC 的 upload 链路还未接入，百度与 PikPak 的秒传证据也还缺失。",
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
            evidence="已具备本地 mock 验证链路，并新增真实证据状态报告与任务运行真实样本持久化能力，可按 provider 量化当前已保存的 auth/list/metadata/create_dir/task_runtime 真实证据覆盖；其中 Guangya 已接真实上传链路，aliyundrive_open 与 123_open 已接任务运行阶段真实 create_dir 写探针。",
            gaps="尚未提供首批 provider 的真实联调成功证据（认证、目录、元数据、秒传/降级路径）；任务运行阶段虽已支持成功/失败样本持久化，但当前仍缺足够的真实成功样本来收敛 P-REAL。",
        ),
    ]

    done = sum(1 for x in items if x.status == "done")
    partial = sum(1 for x in items if x.status == "partial")
    todo = sum(1 for x in items if x.status == "todo")

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "done": done,
            "partial": partial,
            "todo": todo,
            "providerCount": provider_count,
            "researchCount": research_count,
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
