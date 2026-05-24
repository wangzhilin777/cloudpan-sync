from __future__ import annotations

from .auth_profile_view import auth_profile_view
from .auth_store import list_profiles
from .provider_auth_hints import capture_field_hints, capture_login_url, official_docs_url, provider_auth_modes
from .real_evidence_report import build_real_evidence_report


def _preferred_stub_auth_mode(provider_key: str, auth_modes: list[str]) -> str:
    available_modes = [str(mode or "") for mode in auth_modes if str(mode or "")]
    provider_first = {
        "guangya": ("manual_token", "web_login_capture"),
        "123_open": ("manual_token", "official_oauth"),
        "xunlei": ("manual_token", "web_login_capture"),
        "pikpak": ("manual_token",),
        "115_open": ("manual_cookie", "official_oauth"),
        "quark": ("manual_cookie", "web_login_capture"),
        "uc": ("manual_cookie", "web_login_capture"),
        "189cloud": ("manual_cookie", "web_login_capture"),
        "baidu_netdisk": ("manual_cookie", "official_oauth"),
    }
    for candidate in provider_first.get(provider_key, ()):
        if candidate in available_modes:
            return candidate
    for candidate in ("manual_token", "manual_cookie", "official_oauth", "web_login_capture"):
        if candidate in available_modes:
            return candidate
    return "manual_token"


def _patch_command_for_profile(profile: dict[str, object]) -> str:
    profile_id = str(profile.get("profileId") or "")
    provider_key = str(profile.get("providerKey") or "")
    base = f".\\.venv\\Scripts\\python.exe scripts\\patch_auth_profile_extra.py --profile-id {profile_id}"
    if not profile_id:
        return ""
    if provider_key == "guangya":
        return f"{base} --set parentId=YOUR_REAL_PARENT_ID --write --revalidate"
    if provider_key == "aliyundrive_open":
        return f"{base} --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write --revalidate"
    if provider_key == "189cloud":
        return f".\\.venv\\Scripts\\python.exe scripts\\patch_189cloud_account_auth.py --profile-id {profile_id} --raw-file captured_189_headers.txt --write --revalidate"
    if provider_key == "xunlei":
        return f"{base} --set deviceId=YOUR_DEVICE_ID --write --revalidate"
    if provider_key in {"quark", "uc"}:
        return f"{base} --set pwdId=YOUR_SHARE_PWD_ID --write --revalidate"
    return f"{base} --set key=value --write --revalidate"


def _patch_probe_command_for_profile(profile: dict[str, object]) -> str:
    profile_id = str(profile.get("profileId") or "")
    provider_key = str(profile.get("providerKey") or "")
    base = f".\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --profile-id {profile_id}"
    if not profile_id:
        return ""
    if provider_key == "guangya":
        return f"{base} --set parentId=YOUR_REAL_PARENT_ID --write"
    if provider_key == "aliyundrive_open":
        return f"{base} --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write"
    if provider_key == "189cloud":
        return f".\\.venv\\Scripts\\python.exe scripts\\patch_189cloud_account_auth.py --profile-id {profile_id} --raw-file captured_189_headers.txt --write --revalidate"
    if provider_key == "xunlei":
        return f"{base} --set deviceId=YOUR_DEVICE_ID --write"
    if provider_key in {"quark", "uc"}:
        return f"{base} --set pwdId=YOUR_SHARE_PWD_ID --write"
    return f"{base} --set key=value --write"


def _refresh_evidence_command_for_profile(profile: dict[str, object]) -> str:
    profile_id = str(profile.get("profileId") or "")
    if not profile_id:
        return ""
    return f".\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --profile-id {profile_id} --write"


def _runtime_probe_command_for_profile(profile: dict[str, object]) -> str:
    profile_id = str(profile.get("profileId") or "")
    provider_key = str(profile.get("providerKey") or "")
    if not profile_id or not provider_key:
        return ""
    parts = [
        ".\\.venv\\Scripts\\python.exe",
        "scripts\\create_runtime_probe_task.py",
        f"--target-provider {provider_key}",
        f"--target-profile-id {profile_id}",
    ]
    resolved_parent_id = str(profile.get("resolvedParentId") or "").strip()
    if resolved_parent_id:
        parts.append(f"--target-parent-id {resolved_parent_id}")
    parts.extend(["--auto-temp-file", "--threshold-mb 1", f"--evidence-dir tmp\\{provider_key}-runtime-probe-evidence"])
    return " ".join(parts)


def _fast_candidate_command_for_profile(profile: dict[str, object]) -> str:
    profile_id = str(profile.get("profileId") or "")
    provider_key = str(profile.get("providerKey") or "")
    if not profile_id or not provider_key or provider_key == "guangya":
        return ""
    parts = [
        ".\\.venv\\Scripts\\python.exe",
        "scripts\\create_fast_upload_candidate_task.py",
        f"--target-provider {provider_key}",
        f"--target-profile-id {profile_id}",
    ]
    resolved_parent_id = str(profile.get("resolvedParentId") or "").strip()
    if resolved_parent_id:
        parts.append(f"--target-parent-id {resolved_parent_id}")
    if provider_key == "115_open":
        parts.append("--sha1 auto")
    elif provider_key in {"xunlei", "pikpak"}:
        parts.append("--gcid YOUR_GCID")
    else:
        parts.append("--md5 auto")
    parts.extend(["--auto-temp-file", f"--evidence-dir tmp\\{provider_key}-fast-candidate-evidence"])
    return " ".join(parts)


def _live_upload_command_for_profile(profile: dict[str, object]) -> str:
    profile_id = str(profile.get("profileId") or "")
    provider_key = str(profile.get("providerKey") or "")
    if not profile_id or provider_key not in {"guangya", "aliyundrive_open", "123_open"}:
        return ""
    parts = [
        ".\\.venv\\Scripts\\python.exe",
        "scripts\\create_live_upload_task.py",
        f"--target-provider {provider_key}",
        f"--target-profile-id {profile_id}",
    ]
    resolved_parent_id = str(profile.get("resolvedParentId") or "").strip()
    if resolved_parent_id:
        parts.append(f"--target-parent-id {resolved_parent_id}")
    parts.extend(
        [
            "--auto-temp-file",
            "--threshold-mb 1",
            f"--evidence-dir tmp\\{provider_key}-live-evidence",
        ]
    )
    return " ".join(parts)


def _create_command_for_provider(
    *,
    provider_key: str,
    auth_modes: list[str],
    field_hints: list[str],
) -> str:
    auth_mode = _preferred_stub_auth_mode(provider_key, auth_modes)
    cmd = [
        ".\\.venv\\Scripts\\python.exe",
        "scripts\\create_auth_profile_stub.py",
        f"--provider-key {provider_key}",
        f"--auth-mode {auth_mode}",
        f"--display-name {provider_key}-{auth_mode}",
    ]
    if auth_mode == "manual_cookie":
        cmd.append("--cookie YOUR_COOKIE")
    else:
        cmd.append("--token YOUR_TOKEN")
    for hint in field_hints[:2]:
        text = str(hint or "")
        if "extra." not in text:
            continue
        key = text.split("extra.", 1)[1].split()[0].split(",")[0].strip()
        if auth_mode == "manual_cookie" and key in {"cookie_header", "cookie", "authorization", "accessToken", "access_token"}:
            continue
        if auth_mode != "manual_cookie" and key in {"authorization", "accessToken", "access_token"}:
            continue
        if key:
            cmd.append(f"--set {key}=YOUR_VALUE")
    return " ".join(cmd)


def _bootstrap_command_for_provider(
    *,
    provider_key: str,
    auth_modes: list[str],
    field_hints: list[str],
) -> str:
    return f"{_create_command_for_provider(provider_key=provider_key, auth_modes=auth_modes, field_hints=field_hints)} --probe"


def _profile_views() -> list[dict[str, object]]:
    return [auth_profile_view(profile) for profile in list_profiles()]


def _next_step(
    *,
    provider_key: str,
    provider_profiles: list[dict[str, object]],
    auth_ok: bool,
    list_ok: bool,
    metadata_ok: bool,
    create_dir_ok: bool,
    runtime_ok: bool,
    runtime_blocked_only: bool,
    runtime_candidate_only: bool,
    runtime_probe_only: bool,
    runtime_live_upload_command: str,
) -> str:
    if not provider_profiles:
        return f"先创建 `{provider_key}` 的 auth profile，再执行最小 validation 和 live probe。"
    if any(not bool(profile.get("profileReady")) for profile in provider_profiles):
        return "先补齐档案缺字段并重跑 validation / live probe，拿到 auth/list/metadata 最小成功证据。"
    if any(not bool(profile.get("writeReady", True)) for profile in provider_profiles) and (not create_dir_ok or not runtime_ok):
        return "当前主要缺写链路鉴权；先补齐 write auth，再重跑 create_dir 或小文件 runtime。"
    if not auth_ok or not list_ok or not metadata_ok or not create_dir_ok:
        return "对现有档案重跑 provider live probe，优先补齐 auth/list/metadata/create_dir 成功证据。"
    if not runtime_ok:
        if runtime_live_upload_command:
            return "当前基础证据已齐，可直接运行 Guangya live upload helper，优先补一条真实传输成功样本并落任务 JSON/Markdown 快照。"
        if runtime_probe_only:
            return "当前只有 probe-only 样本，说明写探针已跑通但尚未形成真实传输成功证据；请在保留探针样本的基础上继续跑小文件真实任务。"
        if runtime_candidate_only:
            return "当前只有 fast-upload candidate 样本，尚未形成真实 rapid-upload/runtime 成功证据；请在保留候选样本的基础上继续跑真实任务。"
        if runtime_blocked_only:
            return "当前已有 blocked 样本但没有成功样本；请降低阈值、改用小文件或补齐写鉴权后再跑一次真实任务。"
        return "现有基础证据已齐，下一步用小文件、低并发跑一次真实任务并落 runtime 成功样本。"
    return "当前 provider 已无明显补救项。"


def build_real_evidence_remediation_bundle(
    *,
    report: dict[str, object] | None = None,
    profile_views: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    payload = report or build_real_evidence_report()
    profiles = profile_views if profile_views is not None else _profile_views()
    items: list[dict[str, object]] = []

    for item in payload.get("items", []):
        row = dict(item or {})
        provider_key = str(row.get("providerKey") or "")
        provider_profiles = [profile for profile in profiles if str(profile.get("providerKey") or "") == provider_key]
        auth_evidence = dict(row.get("authEvidence") or {})
        list_evidence = dict(row.get("listEvidence") or {})
        metadata_evidence = dict(row.get("metadataEvidence") or {})
        create_dir_evidence = dict(row.get("createDirEvidence") or {})
        runtime_evidence = dict(row.get("taskRuntimeEvidence") or {})
        profile_ready = bool(provider_profiles) and all(bool(profile.get("profileReady")) for profile in provider_profiles)
        write_ready = bool(provider_profiles) and all(bool(profile.get("writeReady", True)) for profile in provider_profiles)
        profile_needing_patch = next(
            (
                profile
                for profile in provider_profiles
                if (not bool(profile.get("profileReady"))) or (not bool(profile.get("writeReady", True)))
            ),
            None,
        )
        runtime_blocked_only = bool(runtime_evidence.get("blockedCount")) and not bool(runtime_evidence.get("ok"))
        runtime_candidate_only = bool(runtime_evidence.get("candidateCount")) and not bool(runtime_evidence.get("ok"))
        runtime_probe_only = bool(runtime_evidence.get("probeCount")) and not bool(runtime_evidence.get("ok"))
        runtime_live_upload_command = _live_upload_command_for_profile(provider_profiles[0] if provider_profiles else {})
        item_payload = {
            "providerKey": provider_key,
            "displayName": str(row.get("displayName") or provider_key),
            "profileCount": len(provider_profiles),
            "profileIds": [str(profile.get("profileId") or "") for profile in provider_profiles if str(profile.get("profileId") or "")],
            "authReadyProfiles": sum(1 for profile in provider_profiles if bool(profile.get("profileReady"))),
            "writeReadyProfiles": sum(1 for profile in provider_profiles if bool(profile.get("writeReady", True))),
            "recommendedAuthModes": provider_auth_modes(provider_key),
            "webLoginUrl": capture_login_url(provider_key),
            "officialDocsUrl": official_docs_url(provider_key),
            "requiredFieldHints": capture_field_hints(provider_key),
            "needsAuthEvidence": not bool(auth_evidence.get("ok")),
            "needsListEvidence": not bool(list_evidence.get("ok")),
            "needsMetadataEvidence": not bool(metadata_evidence.get("ok")),
            "needsCreateDirEvidence": not bool(create_dir_evidence.get("ok")),
            "needsRuntimeSuccess": not bool(runtime_evidence.get("ok")),
            "runtimeBlockedOnly": runtime_blocked_only,
            "runtimeCandidateOnly": runtime_candidate_only,
            "runtimeProbeOnly": runtime_probe_only,
            "gaps": list(row.get("gaps") or []),
            "recommendedPatchCommand": _patch_command_for_profile(profile_needing_patch or {}),
            "recommendedPatchProbeCommand": _patch_probe_command_for_profile(profile_needing_patch or {}),
            "recommendedRefreshEvidenceCommand": _refresh_evidence_command_for_profile(provider_profiles[0] if provider_profiles else {})
            if provider_profiles and profile_ready and write_ready and (not bool(auth_evidence.get("ok")) or not bool(list_evidence.get("ok")) or not bool(metadata_evidence.get("ok")) or not bool(create_dir_evidence.get("ok")))
            else "",
            "recommendedRuntimeProbeCommand": _runtime_probe_command_for_profile(provider_profiles[0] if provider_profiles else {})
            if provider_profiles and write_ready and bool(auth_evidence.get("ok")) and bool(list_evidence.get("ok")) and bool(metadata_evidence.get("ok")) and (bool(create_dir_evidence.get("ok")) or runtime_candidate_only or runtime_blocked_only or runtime_probe_only) and not bool(runtime_evidence.get("ok"))
            else "",
            "recommendedLiveUploadCommand": runtime_live_upload_command
            if provider_profiles and profile_ready and write_ready and bool(auth_evidence.get("ok")) and bool(list_evidence.get("ok")) and bool(metadata_evidence.get("ok")) and bool(create_dir_evidence.get("ok")) and not bool(runtime_evidence.get("ok"))
            else "",
            "recommendedFastCandidateCommand": _fast_candidate_command_for_profile(provider_profiles[0] if provider_profiles else {})
            if provider_profiles and profile_ready and write_ready and bool(auth_evidence.get("ok")) and bool(list_evidence.get("ok")) and bool(metadata_evidence.get("ok")) and not bool(runtime_evidence.get("ok"))
            else "",
            "recommendedCreateCommand": _create_command_for_provider(
                provider_key=provider_key,
                auth_modes=provider_auth_modes(provider_key),
                field_hints=capture_field_hints(provider_key),
            )
            if not provider_profiles
            else "",
            "recommendedBootstrapCommand": _bootstrap_command_for_provider(
                provider_key=provider_key,
                auth_modes=provider_auth_modes(provider_key),
                field_hints=capture_field_hints(provider_key),
            )
            if not provider_profiles
            else "",
            "nextStep": _next_step(
                provider_key=provider_key,
                provider_profiles=provider_profiles,
                auth_ok=bool(auth_evidence.get("ok")),
                list_ok=bool(list_evidence.get("ok")),
                metadata_ok=bool(metadata_evidence.get("ok")),
                create_dir_ok=bool(create_dir_evidence.get("ok")),
                runtime_ok=bool(runtime_evidence.get("ok")),
                runtime_blocked_only=runtime_blocked_only,
                runtime_candidate_only=runtime_candidate_only,
                runtime_probe_only=runtime_probe_only,
                runtime_live_upload_command=runtime_live_upload_command,
            ),
        }
        items.append(item_payload)

    return {
        "summary": {
            "providerCount": len(items),
            "providersWithNoProfiles": sum(1 for item in items if int(item.get("profileCount") or 0) == 0),
            "providersNeedingAuthEvidence": sum(1 for item in items if bool(item.get("needsAuthEvidence"))),
            "providersNeedingListEvidence": sum(1 for item in items if bool(item.get("needsListEvidence"))),
            "providersNeedingMetadataEvidence": sum(1 for item in items if bool(item.get("needsMetadataEvidence"))),
            "providersNeedingCreateDirEvidence": sum(1 for item in items if bool(item.get("needsCreateDirEvidence"))),
            "providersNeedingRuntimeSuccess": sum(1 for item in items if bool(item.get("needsRuntimeSuccess"))),
            "providersWithPatchCommand": sum(1 for item in items if str(item.get("recommendedPatchCommand") or "")),
            "providersWithPatchProbeCommand": sum(1 for item in items if str(item.get("recommendedPatchProbeCommand") or "")),
            "providersWithRefreshEvidenceCommand": sum(1 for item in items if str(item.get("recommendedRefreshEvidenceCommand") or "")),
            "providersWithRuntimeProbeCommand": sum(1 for item in items if str(item.get("recommendedRuntimeProbeCommand") or "")),
            "providersWithLiveUploadCommand": sum(1 for item in items if str(item.get("recommendedLiveUploadCommand") or "")),
            "providersWithFastCandidateCommand": sum(1 for item in items if str(item.get("recommendedFastCandidateCommand") or "")),
            "providersWithCreateCommand": sum(1 for item in items if str(item.get("recommendedCreateCommand") or "")),
            "providersWithBootstrapCommand": sum(1 for item in items if str(item.get("recommendedBootstrapCommand") or "")),
            "providersBlockedOnly": sum(1 for item in items if bool(item.get("runtimeBlockedOnly"))),
            "providersCandidateOnly": sum(1 for item in items if bool(item.get("runtimeCandidateOnly"))),
            "providersProbeOnly": sum(1 for item in items if bool(item.get("runtimeProbeOnly"))),
        },
        "items": items,
    }


def real_evidence_remediation_to_markdown(payload: dict[str, object]) -> str:
    summary = dict(payload.get("summary") or {})
    lines: list[str] = []
    lines.append("# CloudPan Sync 真实联调补救指南")
    lines.append("")
    lines.append(f"- providerCount: `{summary.get('providerCount', 0)}`")
    lines.append(f"- providersWithNoProfiles: `{summary.get('providersWithNoProfiles', 0)}`")
    lines.append(f"- providersNeedingAuthEvidence: `{summary.get('providersNeedingAuthEvidence', 0)}`")
    lines.append(f"- providersNeedingListEvidence: `{summary.get('providersNeedingListEvidence', 0)}`")
    lines.append(f"- providersNeedingMetadataEvidence: `{summary.get('providersNeedingMetadataEvidence', 0)}`")
    lines.append(f"- providersNeedingCreateDirEvidence: `{summary.get('providersNeedingCreateDirEvidence', 0)}`")
    lines.append(f"- providersNeedingRuntimeSuccess: `{summary.get('providersNeedingRuntimeSuccess', 0)}`")
    lines.append(f"- providersWithPatchCommand: `{summary.get('providersWithPatchCommand', 0)}`")
    lines.append(f"- providersWithPatchProbeCommand: `{summary.get('providersWithPatchProbeCommand', 0)}`")
    lines.append(f"- providersWithRefreshEvidenceCommand: `{summary.get('providersWithRefreshEvidenceCommand', 0)}`")
    lines.append(f"- providersWithRuntimeProbeCommand: `{summary.get('providersWithRuntimeProbeCommand', 0)}`")
    lines.append(f"- providersWithLiveUploadCommand: `{summary.get('providersWithLiveUploadCommand', 0)}`")
    lines.append(f"- providersWithFastCandidateCommand: `{summary.get('providersWithFastCandidateCommand', 0)}`")
    lines.append(f"- providersWithCreateCommand: `{summary.get('providersWithCreateCommand', 0)}`")
    lines.append(f"- providersWithBootstrapCommand: `{summary.get('providersWithBootstrapCommand', 0)}`")
    lines.append(f"- providersBlockedOnly: `{summary.get('providersBlockedOnly', 0)}`")
    lines.append(f"- providersCandidateOnly: `{summary.get('providersCandidateOnly', 0)}`")
    lines.append(f"- providersProbeOnly: `{summary.get('providersProbeOnly', 0)}`")
    lines.append("")
    lines.append("## Provider 清单")
    lines.append("")
    for item in payload.get("items", []):
        row = dict(item or {})
        lines.append(f"### {row.get('providerKey', '')} - {row.get('displayName', '')}")
        lines.append(f"- profileCount: `{row.get('profileCount', 0)}`")
        lines.append(f"- authReadyProfiles: `{row.get('authReadyProfiles', 0)}`")
        lines.append(f"- writeReadyProfiles: `{row.get('writeReadyProfiles', 0)}`")
        if row.get("recommendedAuthModes"):
            lines.append(f"- recommendedAuthModes: `{', '.join(row.get('recommendedAuthModes') or [])}`")
        if row.get("webLoginUrl"):
            lines.append(f"- webLoginUrl: {row.get('webLoginUrl', '')}")
        if row.get("officialDocsUrl"):
            lines.append(f"- officialDocsUrl: {row.get('officialDocsUrl', '')}")
        if row.get("requiredFieldHints"):
            lines.append(f"- requiredFieldHints: `{', '.join(row.get('requiredFieldHints') or [])}`")
        lines.append(
            f"- needs: `auth={row.get('needsAuthEvidence', False)}` `list={row.get('needsListEvidence', False)}` "
            f"`metadata={row.get('needsMetadataEvidence', False)}` `create_dir={row.get('needsCreateDirEvidence', False)}` "
            f"`runtime={row.get('needsRuntimeSuccess', False)}` `runtimeBlockedOnly={row.get('runtimeBlockedOnly', False)}` `runtimeCandidateOnly={row.get('runtimeCandidateOnly', False)}` `runtimeProbeOnly={row.get('runtimeProbeOnly', False)}`"
        )
        if row.get("gaps"):
            lines.append(f"- gaps: {', '.join(row.get('gaps') or [])}")
        lines.append(f"- nextStep: {row.get('nextStep', '')}")
        if row.get("recommendedCreateCommand"):
            lines.append(f"- recommendedCreateCommand: `{row.get('recommendedCreateCommand', '')}`")
        if row.get("recommendedBootstrapCommand"):
            lines.append(f"- recommendedBootstrapCommand: `{row.get('recommendedBootstrapCommand', '')}`")
        if row.get("recommendedPatchCommand"):
            lines.append(f"- recommendedPatchCommand: `{row.get('recommendedPatchCommand', '')}`")
        if row.get("recommendedPatchProbeCommand"):
            lines.append(f"- recommendedPatchProbeCommand: `{row.get('recommendedPatchProbeCommand', '')}`")
        if row.get("recommendedRefreshEvidenceCommand"):
            lines.append(f"- recommendedRefreshEvidenceCommand: `{row.get('recommendedRefreshEvidenceCommand', '')}`")
        if row.get("recommendedRuntimeProbeCommand"):
            lines.append(f"- recommendedRuntimeProbeCommand: `{row.get('recommendedRuntimeProbeCommand', '')}`")
        if row.get("recommendedLiveUploadCommand"):
            lines.append(f"- recommendedLiveUploadCommand: `{row.get('recommendedLiveUploadCommand', '')}`")
        if row.get("recommendedFastCandidateCommand"):
            lines.append(f"- recommendedFastCandidateCommand: `{row.get('recommendedFastCandidateCommand', '')}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
