from __future__ import annotations

from .auth_profile_remediation import recreate_probe_command_for_profile
from .auth_profile_view import auth_profile_view
from .auth_store import get_profile, list_profiles, save_profile
from .models import AuthProfileInput
from .planner import _resolve_conflict_support
from .provider_auth_hints import capture_field_hints, capture_login_url, official_docs_url, provider_auth_modes
from .provider_registry import get_provider_profile
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


def _placeholder_secret(auth_mode: str) -> tuple[str, str]:
    mode = str(auth_mode or "").strip()
    if mode == "manual_cookie":
        return "", "YOUR_COOKIE"
    return "YOUR_TOKEN", ""


def _placeholder_extra_value(key: str) -> str:
    mapping = {
        "parentId": "YOUR_REAL_PARENT_ID",
        "parentFileId": "YOUR_PARENT_FILE_ID",
        "did": "YOUR_DID",
        "dt": "YOUR_DT",
        "domainId": "YOUR_DOMAIN_ID",
        "driveId": "YOUR_DRIVE_ID",
        "shareCode": "YOUR_SHARE_CODE",
        "accessCode": "YOUR_ACCESS_CODE",
        "accessToken": "YOUR_ACCESS_TOKEN",
        "signature": "YOUR_SIGNATURE",
        "date": "YOUR_DATE",
        "fileId": "YOUR_FILE_ID",
        "path": "YOUR_PATH",
        "cid": "YOUR_PARENT_ID",
        "deviceId": "YOUR_DEVICE_ID",
        "pwdId": "YOUR_SHARE_PWD_ID",
        "sharePwdId": "YOUR_SHARE_PWD_ID",
        "passcode": "YOUR_PASSCODE",
    }
    return mapping.get(str(key or "").strip(), "YOUR_VALUE")


def _extra_stub_fields(field_hints: list[str], auth_mode: str) -> dict[str, str]:
    extra: dict[str, str] = {}
    for hint in field_hints:
        text = str(hint or "")
        if "extra." not in text:
            continue
        key = text.split("extra.", 1)[1].split()[0].split(",")[0].strip()
        if not key:
            continue
        if auth_mode == "manual_cookie" and key in {"cookie_header", "cookie"}:
            continue
        if key in {"authorization", "Authorization", "access_token"}:
            continue
        normalized = "pwdId" if key == "sharePwdId" else key
        extra.setdefault(normalized, _placeholder_extra_value(normalized))
    return extra


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
    parts.extend(
        [
            "--auto-temp-file",
            "--threshold-mb 1",
            "--conflict-policy auto_rename_new",
            f"--evidence-dir tmp\\{provider_key}-runtime-probe-evidence",
        ]
    )
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
    parts.extend(
        [
            "--auto-temp-file",
            "--conflict-policy auto_rename_new",
            f"--evidence-dir tmp\\{provider_key}-fast-candidate-evidence",
        ]
    )
    return " ".join(parts)


def _live_upload_command_for_profile(profile: dict[str, object]) -> str:
    profile_id = str(profile.get("profileId") or "")
    provider_key = str(profile.get("providerKey") or "")
    if not profile_id or provider_key not in {"guangya", "aliyundrive_open", "123_open", "baidu_netdisk", "xunlei", "pikpak", "quark", "uc"}:
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
            "--conflict-policy auto_rename_new",
            f"--evidence-dir tmp\\{provider_key}-live-evidence",
        ]
    )
    return " ".join(parts)


def _runtime_success_command_for_profile(profile: dict[str, object]) -> str:
    live_command = _live_upload_command_for_profile(profile)
    if live_command:
        return live_command
    return _fast_candidate_command_for_profile(profile)


def _post_bootstrap_runtime_command_for_provider(provider_key: str) -> str:
    provider = str(provider_key or "").strip()
    if provider in {"aliyundrive_open", "123_open", "baidu_netdisk", "xunlei", "pikpak", "quark", "uc", "guangya"}:
        return " ".join(
            [
                ".\\.venv\\Scripts\\python.exe",
                "scripts\\create_live_upload_task.py",
                f"--target-provider {provider}",
                "--target-profile-id YOUR_PROFILE_ID",
                "--auto-temp-file",
                "--threshold-mb 1",
                "--conflict-policy auto_rename_new",
                f"--evidence-dir tmp\\{provider}-post-bootstrap-runtime-evidence",
            ]
        )
    if provider in {"115_open", "189cloud"}:
        parts = [
            ".\\.venv\\Scripts\\python.exe",
            "scripts\\create_fast_upload_candidate_task.py",
            f"--target-provider {provider}",
            "--target-profile-id YOUR_PROFILE_ID",
        ]
        if provider == "115_open":
            parts.append("--sha1 auto")
        else:
            parts.append("--md5 auto")
        parts.extend(
            [
                "--auto-temp-file",
                "--conflict-policy auto_rename_new",
                f"--evidence-dir tmp\\{provider}-post-bootstrap-runtime-evidence",
            ]
        )
        return " ".join(parts)
    return ""


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


def _orphan_recreate_probe_command_for_provider(
    *,
    provider_key: str,
    orphan_profile_id: str,
    auth_modes: list[str],
    field_hints: list[str],
) -> str:
    profile_id = str(orphan_profile_id or "").strip()
    if not profile_id:
        return ""
    auth_mode = _preferred_stub_auth_mode(provider_key, auth_modes)
    display_name = f"{provider_key}-restore-{profile_id}"
    del field_hints
    base = recreate_probe_command_for_profile(
        {
            "providerKey": provider_key,
            "authMode": auth_mode,
            "displayName": display_name,
        }
    )
    marker = "scripts\\create_auth_profile_stub.py "
    if marker not in base:
        return base
    return base.replace(marker, f"{marker}--profile-id {profile_id} ", 1)


def _orphan_recreate_probe_commands_for_provider(
    *,
    provider_key: str,
    orphan_profile_ids: list[str],
    auth_modes: list[str],
    field_hints: list[str],
) -> list[str]:
    commands: list[str] = []
    seen: set[str] = set()
    for orphan_profile_id in orphan_profile_ids:
        command = _orphan_recreate_probe_command_for_provider(
            provider_key=provider_key,
            orphan_profile_id=orphan_profile_id,
            auth_modes=auth_modes,
            field_hints=field_hints,
        )
        text = str(command or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        commands.append(text)
    return commands


def _profile_commands(
    profiles: list[dict[str, object]],
    command_builder,
) -> list[str]:
    commands: list[str] = []
    seen: set[str] = set()
    for profile in profiles:
        command = command_builder(profile)
        text = str(command or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        commands.append(text)
    return commands


def _exact_recreate_helper(orphan_profile_id: str) -> str:
    profile_id = str(orphan_profile_id or "").strip()
    if not profile_id:
        return ""
    return f".\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --from-remediation-orphan-profile {profile_id}"


def _profile_views() -> list[dict[str, object]]:
    return [auth_profile_view(profile) for profile in list_profiles()]


def _conflict_policy_note(*commands: str) -> str:
    if not any(str(command or "").strip() for command in commands):
        return ""
    return "当前 helper 默认使用 --conflict-policy auto_rename_new；如需尝试直接覆盖同名文件，可改成 overwrite_existing；若 provider 不支持覆盖，运行结果会诚实降级或直接提示原因。"


def _overwrite_variant_command(command: str) -> str:
    text = str(command or "").strip()
    if not text or "--conflict-policy auto_rename_new" not in text:
        return ""
    return text.replace("--conflict-policy auto_rename_new", "--conflict-policy overwrite_existing", 1)


def _exact_patch_probe_helper(profile_id: str) -> str:
    target = str(profile_id or "").strip()
    if not target:
        return ""
    return f".\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-remediation-profile-id {target}"


def _exact_runtime_helper(command: str, profile_id: str) -> str:
    text = str(command or "").strip()
    target = str(profile_id or "").strip()
    if not text or not target:
        return ""
    if "scripts\\create_runtime_probe_task.py" in text:
        return f".\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py --from-remediation-profile-id {target}"
    if "scripts\\create_live_upload_task.py" in text:
        return f".\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-remediation-profile-id {target}"
    if "scripts\\create_fast_upload_candidate_task.py" in text:
        return f".\\.venv\\Scripts\\python.exe scripts\\create_fast_upload_candidate_task.py --from-remediation-profile-id {target}"
    return ""


def _provider_conflict_snapshot(provider_key: str) -> dict[str, object]:
    profile = get_provider_profile(provider_key)
    overwrite_status, _ = _resolve_conflict_support(
        conflict_policy="overwrite_existing",
        provider_key=provider_key,
    )
    auto_rename_status, _ = _resolve_conflict_support(
        conflict_policy="auto_rename_new",
        provider_key=provider_key,
    )
    return {
        "declaredConflictPolicies": list(getattr(profile, "conflictPolicies", []) or []),
        "supportsOverwrite": bool(getattr(profile, "supportsOverwrite", False)),
        "supportsAutoRename": bool(getattr(profile, "supportsAutoRename", False)),
        "overwriteBehavior": str(getattr(profile, "overwriteBehavior", "") or ""),
        "overwriteSupportStatus": overwrite_status,
        "autoRenameSupportStatus": auto_rename_status,
        "providerConflictNotes": str(getattr(profile, "conflictNotes", "") or ""),
    }


def _conflict_next_step_suffix(*, overwrite_support_status: str, auto_rename_support_status: str) -> str:
    overwrite_status = str(overwrite_support_status or "")
    auto_rename_status = str(auto_rename_support_status or "")
    if overwrite_status == "supported":
        return "如需顺手验证同名覆盖，可直接改用 overwrite_existing。"
    if overwrite_status == "downgrade_to_auto_rename":
        return "首条样本建议继续保留默认 auto_rename_new；overwrite_existing 当前会诚实降级为自动改名。"
    if auto_rename_status == "probe_only_runtime_write_check":
        return "当前 auto_rename_new 仍停留在 probe-only 写探针口径，先不要把首条样本建立在 overwrite_existing 上。"
    if overwrite_status == "unsupported" and auto_rename_status == "unsupported":
        return "当前同名冲突处理仍未声明为可安全支持，首条样本请先避开目标目录同名文件。"
    return ""


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
    runtime_orphan_only: bool,
    runtime_success_command: str,
    post_bootstrap_runtime_command: str,
    overwrite_support_status: str,
    auto_rename_support_status: str,
) -> str:
    conflict_suffix = _conflict_next_step_suffix(
        overwrite_support_status=overwrite_support_status,
        auto_rename_support_status=auto_rename_support_status,
    )
    if not provider_profiles:
        if runtime_orphan_only:
            return "当前已存在 runtime 成功样本，但对应 auth profile 未保存在当前仓库；先重建可复用 auth profile，再重跑 validation / live probe，把 auth/list/metadata/create_dir 证据补齐。"
        if post_bootstrap_runtime_command and not runtime_ok:
            return (
                f"先创建 `{provider_key}` 的 auth profile 并完成最小 validation / live probe；"
                f"拿到真实 profileId 后立刻继续跑 post-bootstrap runtime helper，补第一条 runtime success 样本。{conflict_suffix}".strip()
            )
        return f"先创建 `{provider_key}` 的 auth profile，再执行最小 validation 和 live probe。"
    if any(bool(profile.get("needsSecretRefresh")) for profile in provider_profiles):
        return "当前档案仍含占位 token/cookie 等 secret 字段；先用真实凭证重建或编辑档案，再重跑 validation / live probe。"
    if any(not bool(profile.get("profileReady")) for profile in provider_profiles):
        return "先补齐档案缺字段并重跑 validation / live probe，拿到 auth/list/metadata 最小成功证据。"
    if any(not bool(profile.get("writeReady", True)) for profile in provider_profiles) and (not create_dir_ok or not runtime_ok):
        return "当前主要缺写链路鉴权；先补齐 write auth，再重跑 create_dir 或小文件 runtime。"
    if not auth_ok or not list_ok or not metadata_ok or not create_dir_ok:
        return "对现有档案重跑 provider live probe，优先补齐 auth/list/metadata/create_dir 成功证据。"
    if not runtime_ok:
        if runtime_success_command:
            return f"当前基础证据已齐，可直接运行统一的 runtime success helper，优先补一条真实传输成功样本并落任务 JSON/Markdown 快照。{conflict_suffix}".strip()
        if runtime_probe_only:
            return "当前只有 probe-only 样本，说明写探针已跑通但尚未形成真实传输成功证据；请在保留探针样本的基础上继续跑小文件真实任务。"
        if runtime_candidate_only:
            return "当前只有 fast-upload candidate 样本，尚未形成真实 rapid-upload/runtime 成功证据；请在保留候选样本的基础上继续跑真实任务。"
        if runtime_blocked_only:
            return "当前已有 blocked 样本但没有成功样本；请降低阈值、改用小文件或补齐写鉴权后再跑一次真实任务。"
        return "现有基础证据已齐，下一步用小文件、低并发跑一次真实任务并落 runtime 成功样本。"
    return "当前 provider 已无明显补救项。"


def _recommended_primary_command(item_payload: dict[str, object]) -> tuple[str, str]:
    candidates = [
        ("recreate_probe", str(item_payload.get("recommendedRecreateProbeCommand") or "")),
        ("patch_probe", str(item_payload.get("recommendedPatchProbeCommand") or "")),
        ("refresh_evidence", str(item_payload.get("recommendedRefreshEvidenceCommand") or "")),
        ("post_refresh_runtime", str(item_payload.get("recommendedPostRefreshRuntimeCommand") or "")),
        ("runtime_probe", str(item_payload.get("recommendedRuntimeProbeCommand") or "")),
        ("runtime_success", str(item_payload.get("recommendedRuntimeSuccessCommand") or "")),
        ("live_upload", str(item_payload.get("recommendedLiveUploadCommand") or "")),
        ("fast_candidate", str(item_payload.get("recommendedFastCandidateCommand") or "")),
        ("post_bootstrap_runtime", str(item_payload.get("recommendedPostBootstrapRuntimeCommand") or "")),
        ("bootstrap", str(item_payload.get("recommendedBootstrapCommand") or "")),
        ("create", str(item_payload.get("recommendedCreateCommand") or "")),
        ("patch", str(item_payload.get("recommendedPatchCommand") or "")),
    ]
    for label, command in candidates:
        if command:
            return label, command
    return "", ""


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
        profiles_needing_patch = [
            profile
            for profile in provider_profiles
            if (not bool(profile.get("profileReady"))) or (not bool(profile.get("writeReady", True)))
        ]
        runtime_blocked_only = bool(runtime_evidence.get("blockedCount")) and not bool(runtime_evidence.get("ok"))
        runtime_candidate_only = bool(runtime_evidence.get("candidateCount")) and not bool(runtime_evidence.get("ok"))
        runtime_probe_only = bool(runtime_evidence.get("probeCount")) and not bool(runtime_evidence.get("ok"))
        runtime_orphan_only = int(runtime_evidence.get("orphanProfileCount", 0) or 0) > 0
        runtime_orphan_profiles = [str(value or "").strip() for value in (runtime_evidence.get("orphanProfiles") or []) if str(value or "").strip()]
        runtime_orphan_recreate_probe_commands = _orphan_recreate_probe_commands_for_provider(
            provider_key=provider_key,
            orphan_profile_ids=runtime_orphan_profiles,
            auth_modes=provider_auth_modes(provider_key),
            field_hints=capture_field_hints(provider_key),
        )
        runtime_orphan_recreate_probe_command = runtime_orphan_recreate_probe_commands[0] if runtime_orphan_recreate_probe_commands else ""
        patch_commands = _profile_commands(profiles_needing_patch, _patch_command_for_profile)
        patch_probe_commands = _profile_commands(profiles_needing_patch, _patch_probe_command_for_profile)
        runtime_live_upload_command = _live_upload_command_for_profile(provider_profiles[0] if provider_profiles else {})
        runtime_success_command = _runtime_success_command_for_profile(provider_profiles[0] if provider_profiles else {})
        post_bootstrap_runtime_command = _post_bootstrap_runtime_command_for_provider(provider_key)
        conflict_snapshot = _provider_conflict_snapshot(provider_key)
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
            "runtimeOrphanOnly": runtime_orphan_only,
            "runtimeOrphanProfiles": runtime_orphan_profiles,
            "recommendedRecreateProbeCommands": runtime_orphan_recreate_probe_commands,
            "declaredConflictPolicies": list(conflict_snapshot.get("declaredConflictPolicies") or []),
            "supportsOverwrite": bool(conflict_snapshot.get("supportsOverwrite")),
            "supportsAutoRename": bool(conflict_snapshot.get("supportsAutoRename")),
            "overwriteBehavior": str(conflict_snapshot.get("overwriteBehavior") or ""),
            "overwriteSupportStatus": str(conflict_snapshot.get("overwriteSupportStatus") or ""),
            "autoRenameSupportStatus": str(conflict_snapshot.get("autoRenameSupportStatus") or ""),
            "providerConflictNotes": str(conflict_snapshot.get("providerConflictNotes") or ""),
            "gaps": list(row.get("gaps") or []),
            "needsSecretRefresh": any(bool(profile.get("needsSecretRefresh")) for profile in provider_profiles),
            "placeholderSecretFieldHints": sorted(
                {
                    str(value or "")
                    for profile in provider_profiles
                    for value in (profile.get("placeholderSecretFieldHints") or [])
                    if str(value or "")
                }
            ),
            "recommendedRecreateProbeCommand": runtime_orphan_recreate_probe_command
            if runtime_orphan_recreate_probe_command
            else (
                recreate_probe_command_for_profile(profile_needing_patch or {})
                if profile_needing_patch and bool(profile_needing_patch.get("needsSecretRefresh"))
                else ""
            ),
            "recommendedPatchCommands": patch_commands,
            "recommendedPatchProbeCommands": patch_probe_commands,
            "recommendedPatchCommand": patch_commands[0] if patch_commands else "",
            "recommendedPatchProbeCommand": patch_probe_commands[0] if patch_probe_commands else "",
            "recommendedRefreshEvidenceCommand": _refresh_evidence_command_for_profile(provider_profiles[0] if provider_profiles else {})
            if provider_profiles and profile_ready and write_ready and (not bool(auth_evidence.get("ok")) or not bool(list_evidence.get("ok")) or not bool(metadata_evidence.get("ok")) or not bool(create_dir_evidence.get("ok")))
            else "",
            "recommendedPostRefreshRuntimeCommand": runtime_success_command
            if provider_profiles
            and profile_ready
            and write_ready
            and not bool(runtime_evidence.get("ok"))
            and str(runtime_success_command or "")
            and (not bool(auth_evidence.get("ok")) or not bool(list_evidence.get("ok")) or not bool(metadata_evidence.get("ok")) or not bool(create_dir_evidence.get("ok")))
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
            "recommendedRuntimeSuccessCommand": runtime_success_command
            if provider_profiles and profile_ready and write_ready and bool(auth_evidence.get("ok")) and bool(list_evidence.get("ok")) and bool(metadata_evidence.get("ok")) and bool(create_dir_evidence.get("ok")) and not bool(runtime_evidence.get("ok"))
            else "",
            "recommendedPostBootstrapRuntimeCommand": post_bootstrap_runtime_command
            if (not provider_profiles) and not bool(runtime_evidence.get("ok"))
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
                runtime_orphan_only=runtime_orphan_only,
                runtime_success_command=runtime_success_command,
                post_bootstrap_runtime_command=post_bootstrap_runtime_command if not provider_profiles else "",
                overwrite_support_status=str(conflict_snapshot.get("overwriteSupportStatus") or ""),
                auto_rename_support_status=str(conflict_snapshot.get("autoRenameSupportStatus") or ""),
            ),
        }
        item_payload["recommendedOverwriteVariantCommand"] = _overwrite_variant_command(
            str(
                item_payload.get("recommendedRuntimeSuccessCommand")
                or item_payload.get("recommendedPostRefreshRuntimeCommand")
                or item_payload.get("recommendedPostBootstrapRuntimeCommand")
                or item_payload.get("recommendedLiveUploadCommand")
                or item_payload.get("recommendedFastCandidateCommand")
                or item_payload.get("recommendedRuntimeProbeCommand")
                or ""
            )
        )
        exact_profile_id = str((item_payload.get("profileIds") or [""])[0] or "")
        exact_orphan_profile_id = runtime_orphan_profiles[0] if runtime_orphan_profiles else ""
        item_payload["exactPatchHelper"] = _exact_patch_probe_helper(exact_profile_id) if len(patch_probe_commands) > 1 else ""
        item_payload["exactRecreateHelper"] = _exact_recreate_helper(exact_orphan_profile_id) if str(item_payload.get("recommendedRecreateProbeCommand") or "") else ""
        item_payload["exactRefreshEvidenceHelper"] = _exact_patch_probe_helper(exact_profile_id) if str(item_payload.get("recommendedRefreshEvidenceCommand") or "") else ""
        item_payload["exactRuntimeProbeHelper"] = _exact_runtime_helper(
            str(item_payload.get("recommendedRuntimeProbeCommand") or ""),
            exact_profile_id,
        )
        item_payload["exactRuntimeSuccessHelper"] = _exact_runtime_helper(
            str(item_payload.get("recommendedRuntimeSuccessCommand") or ""),
            exact_profile_id,
        )
        item_payload["exactOverwriteVariantHelper"] = _exact_runtime_helper(
            str(item_payload.get("recommendedOverwriteVariantCommand") or ""),
            exact_profile_id,
        )
        item_payload["conflictPolicyNote"] = _conflict_policy_note(
            str(item_payload.get("recommendedPostRefreshRuntimeCommand") or ""),
            str(item_payload.get("recommendedRuntimeProbeCommand") or ""),
            str(item_payload.get("recommendedLiveUploadCommand") or ""),
            str(item_payload.get("recommendedFastCandidateCommand") or ""),
            str(item_payload.get("recommendedRuntimeSuccessCommand") or ""),
            str(item_payload.get("recommendedPostBootstrapRuntimeCommand") or ""),
        )
        primary_label, primary_command = _recommended_primary_command(item_payload)
        item_payload["recommendedPrimaryCommandLabel"] = primary_label
        item_payload["recommendedPrimaryCommand"] = primary_command
        items.append(item_payload)

    providers_with_no_profiles = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if int(item.get("profileCount") or 0) == 0 and str(item.get("providerKey") or "")
        }
    )
    providers_needing_auth_evidence = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if bool(item.get("needsAuthEvidence")) and str(item.get("providerKey") or "")
        }
    )
    providers_needing_runtime_success = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if bool(item.get("needsRuntimeSuccess")) and str(item.get("providerKey") or "")
        }
    )
    providers_with_recreate_probe_command = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if str(item.get("recommendedRecreateProbeCommand") or "") and str(item.get("providerKey") or "")
        }
    )
    providers_with_primary_command = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if str(item.get("recommendedPrimaryCommand") or "") and str(item.get("providerKey") or "")
        }
    )
    providers_with_overwrite_variant_command = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if str(item.get("recommendedOverwriteVariantCommand") or "") and str(item.get("providerKey") or "")
        }
    )
    providers_blocked_only = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if bool(item.get("runtimeBlockedOnly")) and str(item.get("providerKey") or "")
        }
    )
    providers_candidate_only = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if bool(item.get("runtimeCandidateOnly")) and str(item.get("providerKey") or "")
        }
    )
    providers_probe_only = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if bool(item.get("runtimeProbeOnly")) and str(item.get("providerKey") or "")
        }
    )
    providers_runtime_orphan_only = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if bool(item.get("runtimeOrphanOnly")) and str(item.get("providerKey") or "")
        }
    )

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
            "providersWithRecreateProbeCommand": sum(1 for item in items if str(item.get("recommendedRecreateProbeCommand") or "")),
            "providersWithRefreshEvidenceCommand": sum(1 for item in items if str(item.get("recommendedRefreshEvidenceCommand") or "")),
            "providersWithPostRefreshRuntimeCommand": sum(1 for item in items if str(item.get("recommendedPostRefreshRuntimeCommand") or "")),
            "providersWithRuntimeProbeCommand": sum(1 for item in items if str(item.get("recommendedRuntimeProbeCommand") or "")),
            "providersWithLiveUploadCommand": sum(1 for item in items if str(item.get("recommendedLiveUploadCommand") or "")),
            "providersWithFastCandidateCommand": sum(1 for item in items if str(item.get("recommendedFastCandidateCommand") or "")),
            "providersWithRuntimeSuccessCommand": sum(1 for item in items if str(item.get("recommendedRuntimeSuccessCommand") or "")),
            "providersWithPostBootstrapRuntimeCommand": sum(1 for item in items if str(item.get("recommendedPostBootstrapRuntimeCommand") or "")),
            "providersWithPrimaryCommand": sum(1 for item in items if str(item.get("recommendedPrimaryCommand") or "")),
            "providersWithOverwriteVariantCommand": sum(1 for item in items if str(item.get("recommendedOverwriteVariantCommand") or "")),
            "providersWithConflictPolicyNote": sum(1 for item in items if str(item.get("conflictPolicyNote") or "")),
            "providersWithDeclaredConflictPolicies": sum(1 for item in items if list(item.get("declaredConflictPolicies") or [])),
            "providersWithProviderManagedOverwrite": sum(1 for item in items if str(item.get("overwriteSupportStatus") or "") == "supported"),
            "providersWithOverwriteDowngrade": sum(1 for item in items if str(item.get("overwriteSupportStatus") or "") == "downgrade_to_auto_rename"),
            "providersWithConflictUnsupported": sum(
                1
                for item in items
                if str(item.get("overwriteSupportStatus") or "") == "unsupported"
                and str(item.get("autoRenameSupportStatus") or "") == "unsupported"
            ),
            "providersWithCreateCommand": sum(1 for item in items if str(item.get("recommendedCreateCommand") or "")),
            "providersWithBootstrapCommand": sum(1 for item in items if str(item.get("recommendedBootstrapCommand") or "")),
            "providersBlockedOnly": sum(1 for item in items if bool(item.get("runtimeBlockedOnly"))),
            "providersCandidateOnly": sum(1 for item in items if bool(item.get("runtimeCandidateOnly"))),
            "providersProbeOnly": sum(1 for item in items if bool(item.get("runtimeProbeOnly"))),
            "providersRuntimeOrphanOnly": sum(1 for item in items if bool(item.get("runtimeOrphanOnly"))),
            "providersWithNoProfilesList": providers_with_no_profiles,
            "providersNeedingAuthEvidenceList": providers_needing_auth_evidence,
            "providersNeedingRuntimeSuccessList": providers_needing_runtime_success,
            "providersWithRecreateProbeCommandList": providers_with_recreate_probe_command,
            "providersWithPrimaryCommandList": providers_with_primary_command,
            "providersWithOverwriteVariantCommandList": providers_with_overwrite_variant_command,
            "providersBlockedOnlyList": providers_blocked_only,
            "providersCandidateOnlyList": providers_candidate_only,
            "providersProbeOnlyList": providers_probe_only,
            "providersRuntimeOrphanOnlyList": providers_runtime_orphan_only,
        },
        "items": items,
    }


def create_remediation_profile(provider_key: str) -> dict[str, object]:
    provider = str(provider_key or "").strip()
    if not provider:
        return {"ok": False, "error": "provider_missing"}

    payload = build_real_evidence_remediation_bundle()
    target_item = None
    for row in payload.get("items", []):
        item = dict(row or {})
        if str(item.get("providerKey") or "") == provider:
            target_item = item
            break
    if target_item is None:
        return {"ok": False, "error": "provider_not_found"}

    if int(target_item.get("profileCount") or 0) > 0:
        existing_id = str((target_item.get("profileIds") or [""])[0] or "")
        existing = get_profile(existing_id) if existing_id else None
        existing_view = auth_profile_view(existing) if existing is not None else None
        refresh_command = _refresh_evidence_command_for_profile(existing_view or {})
        runtime_probe_command = _runtime_probe_command_for_profile(existing_view or {})
        runtime_success_command = _runtime_success_command_for_profile(existing_view or {})
        overwrite_variant_command = _overwrite_variant_command(runtime_success_command or runtime_probe_command) or str(target_item.get("recommendedOverwriteVariantCommand") or "")
        exact_recreate_helper = _exact_recreate_helper(str(((target_item.get("runtimeOrphanProfiles") or [""])[0]) or ""))
        return {
            "ok": True,
            "created": False,
            "status": "already_exists",
            "message": "This provider already has a saved auth profile in the current repository; edit that profile directly and continue remediation.",
            "item": existing_view,
            "nextStep": str(target_item.get("nextStep") or ""),
            "recommendedBootstrapCommand": str(target_item.get("recommendedBootstrapCommand") or ""),
            "recommendedRefreshEvidenceCommand": refresh_command or str(target_item.get("recommendedRefreshEvidenceCommand") or ""),
            "recommendedRuntimeProbeCommand": runtime_probe_command or str(target_item.get("recommendedRuntimeProbeCommand") or ""),
            "recommendedRuntimeSuccessCommand": runtime_success_command or str(target_item.get("recommendedRuntimeSuccessCommand") or ""),
            "recommendedPostBootstrapRuntimeCommand": str(target_item.get("recommendedPostBootstrapRuntimeCommand") or ""),
            "recommendedOverwriteVariantCommand": overwrite_variant_command,
            "exactRecreateHelper": exact_recreate_helper,
            "exactRefreshEvidenceHelper": _exact_patch_probe_helper(existing_id),
            "exactRuntimeProbeHelper": _exact_runtime_helper(runtime_probe_command, existing_id),
            "exactRuntimeSuccessHelper": _exact_runtime_helper(runtime_success_command, existing_id),
            "exactOverwriteVariantHelper": _exact_runtime_helper(overwrite_variant_command, existing_id),
        }

    auth_modes = list(target_item.get("recommendedAuthModes") or [])
    field_hints = list(target_item.get("requiredFieldHints") or [])
    auth_mode = _preferred_stub_auth_mode(provider, auth_modes)
    token, cookie = _placeholder_secret(auth_mode)
    extra = _extra_stub_fields(field_hints, auth_mode)
    profile = save_profile(
        AuthProfileInput(
            providerKey=provider,
            authMode=auth_mode,
            displayName=f"{provider}-{auth_mode}",
            token=token,
            cookie=cookie,
            extra=extra,
        )
    )
    profile_view = auth_profile_view(profile)
    profile_id = str(profile_view.get("profileId") or "")
    refresh_command = _refresh_evidence_command_for_profile(profile_view)
    runtime_probe_command = _runtime_probe_command_for_profile(profile_view)
    runtime_success_command = _runtime_success_command_for_profile(profile_view)
    overwrite_variant_command = _overwrite_variant_command(runtime_success_command or runtime_probe_command) or str(target_item.get("recommendedOverwriteVariantCommand") or "")
    exact_recreate_helper = _exact_recreate_helper(str(((target_item.get("runtimeOrphanProfiles") or [""])[0]) or ""))
    return {
        "ok": True,
        "created": True,
        "status": "stub_created",
        "message": "A placeholder auth profile stub was created for this provider. Fill the real credentials, then rerun validation/live probe before using it for runtime evidence recovery.",
        "item": profile_view,
        "requiredFieldHints": field_hints,
        "recommendedCreateCommand": str(target_item.get("recommendedCreateCommand") or ""),
        "recommendedBootstrapCommand": str(target_item.get("recommendedBootstrapCommand") or ""),
        "recommendedRefreshEvidenceCommand": refresh_command or str(target_item.get("recommendedRefreshEvidenceCommand") or ""),
        "recommendedRuntimeProbeCommand": runtime_probe_command or str(target_item.get("recommendedRuntimeProbeCommand") or ""),
        "recommendedRuntimeSuccessCommand": runtime_success_command or str(target_item.get("recommendedRuntimeSuccessCommand") or ""),
        "recommendedPostBootstrapRuntimeCommand": str(target_item.get("recommendedPostBootstrapRuntimeCommand") or ""),
        "recommendedOverwriteVariantCommand": overwrite_variant_command,
        "exactRecreateHelper": exact_recreate_helper,
        "exactRefreshEvidenceHelper": _exact_patch_probe_helper(profile_id),
        "exactRuntimeProbeHelper": _exact_runtime_helper(runtime_probe_command, profile_id),
        "exactRuntimeSuccessHelper": _exact_runtime_helper(runtime_success_command, profile_id),
        "exactOverwriteVariantHelper": _exact_runtime_helper(overwrite_variant_command, profile_id),
        "nextStep": str(target_item.get("nextStep") or ""),
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
    lines.append(f"- providersWithRecreateProbeCommand: `{summary.get('providersWithRecreateProbeCommand', 0)}`")
    lines.append(f"- providersWithRefreshEvidenceCommand: `{summary.get('providersWithRefreshEvidenceCommand', 0)}`")
    lines.append(f"- providersWithPostRefreshRuntimeCommand: `{summary.get('providersWithPostRefreshRuntimeCommand', 0)}`")
    lines.append(f"- providersWithRuntimeProbeCommand: `{summary.get('providersWithRuntimeProbeCommand', 0)}`")
    lines.append(f"- providersWithLiveUploadCommand: `{summary.get('providersWithLiveUploadCommand', 0)}`")
    lines.append(f"- providersWithFastCandidateCommand: `{summary.get('providersWithFastCandidateCommand', 0)}`")
    lines.append(f"- providersWithRuntimeSuccessCommand: `{summary.get('providersWithRuntimeSuccessCommand', 0)}`")
    lines.append(f"- providersWithPostBootstrapRuntimeCommand: `{summary.get('providersWithPostBootstrapRuntimeCommand', 0)}`")
    lines.append(f"- providersWithPrimaryCommand: `{summary.get('providersWithPrimaryCommand', 0)}`")
    lines.append(f"- providersWithOverwriteVariantCommand: `{summary.get('providersWithOverwriteVariantCommand', 0)}`")
    lines.append(f"- providersWithConflictPolicyNote: `{summary.get('providersWithConflictPolicyNote', 0)}`")
    lines.append(f"- providersWithDeclaredConflictPolicies: `{summary.get('providersWithDeclaredConflictPolicies', 0)}`")
    lines.append(f"- providersWithProviderManagedOverwrite: `{summary.get('providersWithProviderManagedOverwrite', 0)}`")
    lines.append(f"- providersWithOverwriteDowngrade: `{summary.get('providersWithOverwriteDowngrade', 0)}`")
    lines.append(f"- providersWithConflictUnsupported: `{summary.get('providersWithConflictUnsupported', 0)}`")
    lines.append(f"- providersWithCreateCommand: `{summary.get('providersWithCreateCommand', 0)}`")
    lines.append(f"- providersWithBootstrapCommand: `{summary.get('providersWithBootstrapCommand', 0)}`")
    lines.append(f"- providersBlockedOnly: `{summary.get('providersBlockedOnly', 0)}`")
    lines.append(f"- providersCandidateOnly: `{summary.get('providersCandidateOnly', 0)}`")
    lines.append(f"- providersProbeOnly: `{summary.get('providersProbeOnly', 0)}`")
    lines.append(f"- providersRuntimeOrphanOnly: `{summary.get('providersRuntimeOrphanOnly', 0)}`")
    lines.append(
        f"- providerSummary: `noProfiles={', '.join(summary.get('providersWithNoProfilesList', [])) or '(none)'}` "
        f"`needAuth={', '.join(summary.get('providersNeedingAuthEvidenceList', [])) or '(none)'}` "
        f"`needRuntime={', '.join(summary.get('providersNeedingRuntimeSuccessList', [])) or '(none)'}` "
        f"`recreateProbe={', '.join(summary.get('providersWithRecreateProbeCommandList', [])) or '(none)'}` "
        f"`primaryCommand={', '.join(summary.get('providersWithPrimaryCommandList', [])) or '(none)'}` "
        f"`overwriteVariant={', '.join(summary.get('providersWithOverwriteVariantCommandList', [])) or '(none)'}` "
        f"`blockedOnly={', '.join(summary.get('providersBlockedOnlyList', [])) or '(none)'}` "
        f"`candidateOnly={', '.join(summary.get('providersCandidateOnlyList', [])) or '(none)'}` "
        f"`probeOnly={', '.join(summary.get('providersProbeOnlyList', [])) or '(none)'}` "
        f"`runtimeOrphanOnly={', '.join(summary.get('providersRuntimeOrphanOnlyList', [])) or '(none)'}`"
    )
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
            f"`runtime={row.get('needsRuntimeSuccess', False)}` `runtimeBlockedOnly={row.get('runtimeBlockedOnly', False)}` `runtimeCandidateOnly={row.get('runtimeCandidateOnly', False)}` `runtimeProbeOnly={row.get('runtimeProbeOnly', False)}` `runtimeOrphanOnly={row.get('runtimeOrphanOnly', False)}`"
        )
        if row.get("runtimeOrphanProfiles"):
            lines.append(f"- runtimeOrphanProfiles: `{', '.join(row.get('runtimeOrphanProfiles') or [])}`")
        if row.get("declaredConflictPolicies"):
            lines.append(
                f"- conflictSupport: `declared={', '.join(row.get('declaredConflictPolicies') or [])}` "
                f"`overwrite={row.get('overwriteSupportStatus', '')}` `auto_rename={row.get('autoRenameSupportStatus', '')}` "
                f"`supportsOverwrite={row.get('supportsOverwrite', False)}` `supportsAutoRename={row.get('supportsAutoRename', False)}` "
                f"`overwriteBehavior={row.get('overwriteBehavior', '')}`"
            )
        else:
            lines.append(
                f"- conflictSupport: `declared=(none)` `overwrite={row.get('overwriteSupportStatus', '')}` "
                f"`auto_rename={row.get('autoRenameSupportStatus', '')}` `supportsOverwrite={row.get('supportsOverwrite', False)}` "
                f"`supportsAutoRename={row.get('supportsAutoRename', False)}` `overwriteBehavior={row.get('overwriteBehavior', '')}`"
            )
        if row.get("gaps"):
            lines.append(f"- gaps: {', '.join(row.get('gaps') or [])}")
        if row.get("placeholderSecretFieldHints"):
            lines.append(f"- placeholderSecretFieldHints: `{', '.join(row.get('placeholderSecretFieldHints') or [])}`")
        if row.get("providerConflictNotes"):
            lines.append(f"- providerConflictNotes: {row.get('providerConflictNotes', '')}")
        lines.append(f"- nextStep: {row.get('nextStep', '')}")
        if row.get("recommendedPrimaryCommand"):
            lines.append(
                f"- recommendedPrimaryCommand: `{row.get('recommendedPrimaryCommand', '')}` "
                f"`label={row.get('recommendedPrimaryCommandLabel', '')}`"
            )
        if row.get("recommendedCreateCommand"):
            lines.append(f"- recommendedCreateCommand: `{row.get('recommendedCreateCommand', '')}`")
        if row.get("recommendedBootstrapCommand"):
            lines.append(f"- recommendedBootstrapCommand: `{row.get('recommendedBootstrapCommand', '')}`")
        if row.get("recommendedPatchCommand"):
            lines.append(f"- recommendedPatchCommand: `{row.get('recommendedPatchCommand', '')}`")
        if row.get("recommendedPatchProbeCommand"):
            lines.append(f"- recommendedPatchProbeCommand: `{row.get('recommendedPatchProbeCommand', '')}`")
        patch_commands = [str(value or "") for value in (row.get("recommendedPatchCommands") or []) if str(value or "")]
        if len(patch_commands) > 1:
            lines.append(f"- recommendedPatchCommands: count=`{len(patch_commands)}`")
            for index, command in enumerate(patch_commands, start=1):
                lines.append(f"  - [{index}] `{command}`")
        patch_probe_commands = [str(value or "") for value in (row.get("recommendedPatchProbeCommands") or []) if str(value or "")]
        if len(patch_probe_commands) > 1:
            lines.append(f"- recommendedPatchProbeCommands: count=`{len(patch_probe_commands)}`")
            for index, command in enumerate(patch_probe_commands, start=1):
                lines.append(f"  - [{index}] `{command}`")
            exact_patch_helper = str(row.get("exactPatchHelper") or "")
            if exact_patch_helper:
                lines.append(f"- exactPatchHelper: `{exact_patch_helper}`")
        if row.get("recommendedRecreateProbeCommand"):
            lines.append(f"- recommendedRecreateProbeCommand: `{row.get('recommendedRecreateProbeCommand', '')}`")
            exact_recreate_helper = str(row.get("exactRecreateHelper") or "")
            if not exact_recreate_helper:
                orphan_profiles = [str(value or "") for value in (row.get("runtimeOrphanProfiles") or []) if str(value or "")]
                exact_recreate_helper = _exact_recreate_helper(orphan_profiles[0] if orphan_profiles else "")
            if exact_recreate_helper:
                lines.append(f"- exactRecreateHelper: `{exact_recreate_helper}`")
        recreate_commands = [str(value or "") for value in (row.get("recommendedRecreateProbeCommands") or []) if str(value or "")]
        if len(recreate_commands) > 1:
            lines.append(f"- recommendedRecreateProbeCommands: count=`{len(recreate_commands)}`")
            for index, command in enumerate(recreate_commands, start=1):
                lines.append(f"  - [{index}] `{command}`")
        if row.get("recommendedRefreshEvidenceCommand"):
            lines.append(f"- recommendedRefreshEvidenceCommand: `{row.get('recommendedRefreshEvidenceCommand', '')}`")
            exact_refresh_helper = str(row.get("exactRefreshEvidenceHelper") or "")
            if exact_refresh_helper:
                lines.append(f"- exactRefreshEvidenceHelper: `{exact_refresh_helper}`")
        if row.get("recommendedPostRefreshRuntimeCommand"):
            lines.append(f"- recommendedPostRefreshRuntimeCommand: `{row.get('recommendedPostRefreshRuntimeCommand', '')}`")
        if row.get("recommendedRuntimeProbeCommand"):
            lines.append(f"- recommendedRuntimeProbeCommand: `{row.get('recommendedRuntimeProbeCommand', '')}`")
            exact_runtime_probe_helper = str(row.get("exactRuntimeProbeHelper") or "")
            if exact_runtime_probe_helper:
                lines.append(f"- exactRuntimeProbeHelper: `{exact_runtime_probe_helper}`")
        if row.get("recommendedLiveUploadCommand"):
            lines.append(f"- recommendedLiveUploadCommand: `{row.get('recommendedLiveUploadCommand', '')}`")
        if row.get("recommendedFastCandidateCommand"):
            lines.append(f"- recommendedFastCandidateCommand: `{row.get('recommendedFastCandidateCommand', '')}`")
        if row.get("recommendedRuntimeSuccessCommand"):
            lines.append(f"- recommendedRuntimeSuccessCommand: `{row.get('recommendedRuntimeSuccessCommand', '')}`")
            exact_runtime_success_helper = str(row.get("exactRuntimeSuccessHelper") or "")
            if exact_runtime_success_helper:
                lines.append(f"- exactRuntimeSuccessHelper: `{exact_runtime_success_helper}`")
        if row.get("recommendedPostBootstrapRuntimeCommand"):
            lines.append(f"- recommendedPostBootstrapRuntimeCommand: `{row.get('recommendedPostBootstrapRuntimeCommand', '')}`")
        if row.get("recommendedOverwriteVariantCommand"):
            lines.append(f"- recommendedOverwriteVariantCommand: `{row.get('recommendedOverwriteVariantCommand', '')}`")
            exact_overwrite_variant_helper = str(row.get("exactOverwriteVariantHelper") or "")
            if exact_overwrite_variant_helper:
                lines.append(f"- exactOverwriteVariantHelper: `{exact_overwrite_variant_helper}`")
        if row.get("conflictPolicyNote"):
            lines.append(f"- conflictPolicyNote: {row.get('conflictPolicyNote', '')}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
