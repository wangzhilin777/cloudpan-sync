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
            evidence="授权存储、脱敏展示、校验与网页登录引导 API 已实现。",
            gaps="真实网页登录抓取自动化尚未实现。",
        ),
        AuditItem(
            key="M4",
            title="光鸭 Provider",
            status="partial",
            evidence="光鸭预检（md5/gcid）和目录接口已实现。",
            gaps="当前目录接口为 mock，缺真实在线目录读取/上传链路。",
        ),
        AuditItem(
            key="M5",
            title="首批常用网盘接入",
            status="partial",
            evidence=f"首批 provider 已补齐到 {provider_count} 个，研究索引 {research_count} 条。",
            gaps="非光鸭 provider 当前仍以 mock list/metadata 为主，缺实盘授权与真实 API 读写验证。",
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
            status="partial",
            evidence="任务状态机与队列视图已实现。",
            gaps="UI 仍为基础版，二级菜单/授权弹窗/tip 折叠体验未完整对齐计划。",
        ),
        AuditItem(
            key="P-REAL",
            title="真实联调验证",
            status="todo",
            evidence="已具备本地 mock 验证链路。",
            gaps="尚未提供首批 provider 的真实联调成功证据（认证、目录、元数据、秒传/降级路径）。",
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
