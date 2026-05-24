from __future__ import annotations

from datetime import datetime, timezone

from .auth_live_validate import latest_live_validations
from .auth_store import list_profiles
from .provider_live_probe_store import latest_provider_live_probes
from .provider_registry import build_provider_registry
from .provider_research import build_provider_research_index
from .task_runtime_evidence_store import latest_task_runtime_evidence


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _provider_display_map() -> dict[str, str]:
    display_map: dict[str, str] = {}
    for adapter in build_provider_registry():
        key = str(adapter.profile.providerKey or "")
        if key:
            display_map[key] = str(adapter.profile.displayName or key)
    for item in build_provider_research_index():
        key = str(item.get("providerKey") or "")
        if key and key not in display_map:
            display_map[key] = str(item.get("displayName") or key)
    return display_map


def _provider_notes_map() -> dict[str, str]:
    notes: dict[str, str] = {}
    for item in build_provider_research_index():
        key = str(item.get("providerKey") or "")
        if key:
            notes[key] = str(item.get("notes") or "")
    return notes


def _profile_map() -> dict[str, object]:
    return {str(profile.profileId or ""): profile for profile in list_profiles() if str(profile.profileId or "")}


def _profile_label(profile_map: dict[str, object], profile_id: str) -> str:
    profile = profile_map.get(str(profile_id or ""))
    if profile is None:
        return str(profile_id or "")
    return str(getattr(profile, "displayName", "") or getattr(profile, "profileId", "") or profile_id or "")


def _ok_profile_labels_from_validations(
    rows: list[dict[str, object]],
    profile_map: dict[str, object],
) -> list[str]:
    labels = []
    for row in rows:
        if bool(row.get("ok")):
            labels.append(_profile_label(profile_map, str(row.get("profileId") or "")))
    return sorted(set(labels))


def _ok_profile_labels_from_probe_kind(
    rows: list[dict[str, object]],
    profile_map: dict[str, object],
    kind: str,
) -> list[str]:
    labels: list[str] = []
    for row in rows:
        checks = list(row.get("checks") or [])
        matched = next((dict(check or {}) for check in checks if str((check or {}).get("kind") or "") == kind), {})
        if bool(matched.get("ok")):
            labels.append(_profile_label(profile_map, str(row.get("profileId") or "")))
    return sorted(set(labels))


def _ok_profile_labels_from_runtime(
    rows: list[dict[str, object]],
    profile_map: dict[str, object],
) -> list[str]:
    labels: list[str] = []
    for row in rows:
        if bool(row.get("success")):
            labels.append(_profile_label(profile_map, str(row.get("profileId") or "")))
    return sorted(set(labels))


def _runtime_profile_labels(
    rows: list[dict[str, object]],
    profile_map: dict[str, object],
    success: bool,
) -> list[str]:
    labels: list[str] = []
    for row in rows:
        if bool(row.get("success")) is success:
            labels.append(_profile_label(profile_map, str(row.get("profileId") or "")))
    return sorted(set(labels))


def build_real_evidence_report() -> dict[str, object]:
    display_map = _provider_display_map()
    notes_map = _provider_notes_map()
    profile_map = _profile_map()
    validations = list(latest_live_validations())
    probes = list(latest_provider_live_probes())
    runtime_rows = list(latest_task_runtime_evidence())

    provider_keys = list(display_map.keys())
    items: list[dict[str, object]] = []

    auth_evidence_provider_count = 0
    list_evidence_provider_count = 0
    metadata_evidence_provider_count = 0
    create_dir_evidence_provider_count = 0
    fully_verified_provider_count = 0
    task_runtime_evidence_provider_count = 0
    task_runtime_failed_provider_count = 0
    task_runtime_conflict_handled_count = 0

    for provider_key in provider_keys:
        provider_validations = [row for row in validations if str(row.get("providerKey") or "") == provider_key]
        provider_probes = [row for row in probes if str(row.get("providerKey") or "") == provider_key]
        provider_runtime_rows = [row for row in runtime_rows if str(row.get("providerKey") or "") == provider_key]

        auth_ok_labels = _ok_profile_labels_from_validations(provider_validations, profile_map)
        list_ok_labels = _ok_profile_labels_from_probe_kind(provider_probes, profile_map, "list")
        metadata_ok_labels = _ok_profile_labels_from_probe_kind(provider_probes, profile_map, "metadata")
        create_dir_ok_labels = _ok_profile_labels_from_probe_kind(provider_probes, profile_map, "create_dir")
        runtime_ok_labels = _ok_profile_labels_from_runtime(provider_runtime_rows, profile_map)
        runtime_failed_labels = _runtime_profile_labels(provider_runtime_rows, profile_map, success=False)

        auth_ok = bool(auth_ok_labels)
        list_ok = bool(list_ok_labels)
        metadata_ok = bool(metadata_ok_labels)
        create_dir_ok = bool(create_dir_ok_labels)
        runtime_ok = bool(runtime_ok_labels)
        runtime_failed = bool(runtime_failed_labels)
        runtime_conflict_handled = sum(1 for row in provider_runtime_rows if str(row.get("conflictAction") or ""))

        if auth_ok:
            auth_evidence_provider_count += 1
        if list_ok:
            list_evidence_provider_count += 1
        if metadata_ok:
            metadata_evidence_provider_count += 1
        if create_dir_ok:
            create_dir_evidence_provider_count += 1
        if runtime_ok:
            task_runtime_evidence_provider_count += 1
        if runtime_failed:
            task_runtime_failed_provider_count += 1
        task_runtime_conflict_handled_count += runtime_conflict_handled
        if auth_ok and list_ok and metadata_ok and create_dir_ok:
            fully_verified_provider_count += 1

        gaps: list[str] = []
        if not auth_ok:
            gaps.append("缺少通过的 auth validation 证据")
        if not list_ok:
            gaps.append("缺少通过的 live list 证据")
        if not metadata_ok:
            gaps.append("缺少通过的 live metadata 证据")
        if not create_dir_ok:
            gaps.append("缺少通过的 live create_dir 证据")
        if runtime_failed and not runtime_ok:
            gaps.append("已有 task runtime 失败样本，但尚无成功样本")

        items.append(
            {
                "providerKey": provider_key,
                "displayName": display_map.get(provider_key, provider_key),
                "notes": notes_map.get(provider_key, ""),
                "latestValidationProfileCount": len(provider_validations),
                "latestProbeProfileCount": len(provider_probes),
                "authEvidence": {
                    "ok": auth_ok,
                    "okProfileCount": len(auth_ok_labels),
                    "profiles": auth_ok_labels,
                },
                "listEvidence": {
                    "ok": list_ok,
                    "okProfileCount": len(list_ok_labels),
                    "profiles": list_ok_labels,
                },
                "metadataEvidence": {
                    "ok": metadata_ok,
                    "okProfileCount": len(metadata_ok_labels),
                    "profiles": metadata_ok_labels,
                },
                "createDirEvidence": {
                    "ok": create_dir_ok,
                    "okProfileCount": len(create_dir_ok_labels),
                    "profiles": create_dir_ok_labels,
                },
                "taskRuntimeEvidence": {
                    "ok": runtime_ok,
                    "sampleCount": len(provider_runtime_rows),
                    "successCount": sum(1 for row in provider_runtime_rows if bool(row.get("success"))),
                    "failedCount": sum(1 for row in provider_runtime_rows if not bool(row.get("success"))),
                    "conflictHandledCount": runtime_conflict_handled,
                    "okProfileCount": len(runtime_ok_labels),
                    "profiles": runtime_ok_labels,
                    "failedProfiles": runtime_failed_labels,
                    "note": (
                        "当前已记录到任务运行阶段真实成功样本。"
                        if runtime_ok
                        else (
                            "当前已记录到任务运行阶段真实失败样本，但尚未出现成功样本。"
                            if runtime_failed
                            else "当前尚未记录到任务运行阶段真实成功样本，因此此项仍按未完成处理。"
                        )
                    ),
                },
                "fullyVerified": auth_ok and list_ok and metadata_ok and create_dir_ok,
                "gaps": gaps,
            }
        )

    return {
        "generatedAt": _now(),
        "summary": {
            "providerCount": len(items),
            "profilesSaved": len(profile_map),
            "latestValidationProfileCount": len(validations),
            "latestProbeProfileCount": len(probes),
            "authEvidenceProviderCount": auth_evidence_provider_count,
            "listEvidenceProviderCount": list_evidence_provider_count,
            "metadataEvidenceProviderCount": metadata_evidence_provider_count,
            "createDirEvidenceProviderCount": create_dir_evidence_provider_count,
            "fullyVerifiedProviderCount": fully_verified_provider_count,
            "taskRuntimeEvidenceProviderCount": task_runtime_evidence_provider_count,
            "taskRuntimeFailedProviderCount": task_runtime_failed_provider_count,
            "taskRuntimeSampleCount": len(runtime_rows),
            "taskRuntimeSuccessCount": sum(1 for row in runtime_rows if bool(row.get("success"))),
            "taskRuntimeFailedCount": sum(1 for row in runtime_rows if not bool(row.get("success"))),
            "taskRuntimeConflictHandledCount": task_runtime_conflict_handled_count,
        },
        "items": items,
    }


def real_evidence_to_markdown(payload: dict[str, object]) -> str:
    summary = dict(payload.get("summary") or {})
    lines: list[str] = []
    lines.append("# CloudPan Sync 真实证据状态报告")
    lines.append("")
    lines.append(f"- 生成时间：`{payload.get('generatedAt', '')}`")
    lines.append(
        "- 汇总："
        f" `providerCount={summary.get('providerCount', 0)}`"
        f" `profilesSaved={summary.get('profilesSaved', 0)}`"
        f" `latestValidationProfileCount={summary.get('latestValidationProfileCount', 0)}`"
        f" `latestProbeProfileCount={summary.get('latestProbeProfileCount', 0)}`"
    )
    lines.append(
        "- 真实证据覆盖："
        f" `auth={summary.get('authEvidenceProviderCount', 0)}`"
        f" `list={summary.get('listEvidenceProviderCount', 0)}`"
        f" `metadata={summary.get('metadataEvidenceProviderCount', 0)}`"
        f" `create_dir={summary.get('createDirEvidenceProviderCount', 0)}`"
        f" `fully_verified={summary.get('fullyVerifiedProviderCount', 0)}`"
        f" `task_runtime={summary.get('taskRuntimeEvidenceProviderCount', 0)}`"
        f" `task_runtime_failed={summary.get('taskRuntimeFailedProviderCount', 0)}`"
        f" `runtime_samples={summary.get('taskRuntimeSampleCount', 0)}`"
        f" `runtime_success={summary.get('taskRuntimeSuccessCount', 0)}`"
        f" `runtime_failed={summary.get('taskRuntimeFailedCount', 0)}`"
        f" `runtime_conflict_handled={summary.get('taskRuntimeConflictHandledCount', 0)}`"
    )
    lines.append("")
    lines.append("> 说明：本报告只统计当前仓库已保存的最新真实校验/探测证据，不把 mock 成功、静态能力声明或未持久化的临时运行结果算成真实成功。")
    lines.append("")
    for item in payload.get("items", []):
        row = dict(item or {})
        lines.append(f"## {row.get('providerKey', '')} - {row.get('displayName', '')}")
        lines.append(f"- fullyVerified: `{row.get('fullyVerified', False)}`")
        lines.append(
            f"- authEvidence: `{((row.get('authEvidence') or {}).get('ok', False))}` "
            f"profiles={', '.join((row.get('authEvidence') or {}).get('profiles', [])) or '(none)'}"
        )
        lines.append(
            f"- listEvidence: `{((row.get('listEvidence') or {}).get('ok', False))}` "
            f"profiles={', '.join((row.get('listEvidence') or {}).get('profiles', [])) or '(none)'}"
        )
        lines.append(
            f"- metadataEvidence: `{((row.get('metadataEvidence') or {}).get('ok', False))}` "
            f"profiles={', '.join((row.get('metadataEvidence') or {}).get('profiles', [])) or '(none)'}"
        )
        lines.append(
            f"- createDirEvidence: `{((row.get('createDirEvidence') or {}).get('ok', False))}` "
            f"profiles={', '.join((row.get('createDirEvidence') or {}).get('profiles', [])) or '(none)'}"
        )
        lines.append(
            f"- taskRuntimeEvidence: `{((row.get('taskRuntimeEvidence') or {}).get('ok', False))}` "
            f"samples={((row.get('taskRuntimeEvidence') or {}).get('sampleCount', 0))} "
            f"success={((row.get('taskRuntimeEvidence') or {}).get('successCount', 0))} "
            f"failed={((row.get('taskRuntimeEvidence') or {}).get('failedCount', 0))} "
            f"conflictHandled={((row.get('taskRuntimeEvidence') or {}).get('conflictHandledCount', 0))} "
            f"note={str((row.get('taskRuntimeEvidence') or {}).get('note') or '')}"
        )
        if row.get("gaps"):
            lines.append(f"- gaps: {', '.join(row.get('gaps') or [])}")
        if row.get("notes"):
            lines.append(f"- notes: {row.get('notes')}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
