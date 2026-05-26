from __future__ import annotations

from datetime import datetime, timezone

from .auth_profile_view import auth_profile_view
from .auth_store import get_profile, list_profiles, save_profile
from .models import AuthProfileInput
from .provider_auth_hints import capture_field_hints, capture_login_url, official_docs_url, provider_auth_modes
from .provider_registry import build_provider_registry
from .task_runtime_evidence_store import latest_task_runtime_evidence


def _provider_display_name(provider_key: str) -> str:
    target = str(provider_key or "")
    for adapter in build_provider_registry():
        profile = getattr(adapter, "profile", None)
        if str(getattr(profile, "providerKey", "") or "") == target:
            return str(getattr(profile, "displayName", "") or target)
    return target


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
        "aliyundrive_open": ("official_oauth",),
    }
    for candidate in provider_first.get(provider_key, ()):
        if candidate in available_modes:
            return candidate
    for candidate in ("manual_token", "manual_cookie", "official_oauth", "web_login_capture"):
        if candidate in available_modes:
            return candidate
    return "manual_token"


def _command_with_field_hints(provider_key: str, profile_id: str, auth_mode: str, field_hints: list[str]) -> str:
    display_name = f"{provider_key}-restore-{profile_id}"
    parts = [
        ".\\.venv\\Scripts\\python.exe",
        "scripts\\create_auth_profile_stub.py",
        f"--profile-id {profile_id}",
        f"--provider-key {provider_key}",
        f"--auth-mode {auth_mode}",
        f"--display-name {display_name}",
    ]
    if auth_mode == "manual_cookie":
        parts.append("--cookie YOUR_COOKIE")
    else:
        parts.append("--token YOUR_TOKEN")
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
            parts.append(f"--set {key}=YOUR_VALUE")
    parts.append("--probe")
    return " ".join(parts)


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


def _refresh_evidence_command(provider_key: str, profile_id: str) -> str:
    del provider_key
    target = str(profile_id or "").strip()
    if not target:
        return ""
    return f".\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --profile-id {target} --write"


def _runtime_probe_command(provider_key: str, profile_id: str) -> str:
    provider = str(provider_key or "").strip()
    target = str(profile_id or "").strip()
    if not provider or not target:
        return ""
    return " ".join(
        [
            ".\\.venv\\Scripts\\python.exe",
            "scripts\\create_runtime_probe_task.py",
            f"--target-provider {provider}",
            f"--target-profile-id {target}",
            "--auto-temp-file",
            "--threshold-mb 1",
            "--conflict-policy auto_rename_new",
            f"--evidence-dir tmp\\{provider}-runtime-orphan-probe-evidence",
        ]
    )


def _fast_candidate_command(provider_key: str, profile_id: str) -> str:
    provider = str(provider_key or "").strip()
    target = str(profile_id or "").strip()
    if not provider or not target or provider == "guangya":
        return ""
    parts = [
        ".\\.venv\\Scripts\\python.exe",
        "scripts\\create_fast_upload_candidate_task.py",
        f"--target-provider {provider}",
        f"--target-profile-id {target}",
    ]
    if provider == "115_open":
        parts.append("--sha1 auto")
    elif provider in {"xunlei", "pikpak"}:
        parts.append("--gcid YOUR_GCID")
    else:
        parts.append("--md5 auto")
    parts.extend(
        [
            "--auto-temp-file",
            "--conflict-policy auto_rename_new",
            f"--evidence-dir tmp\\{provider}-runtime-orphan-success-evidence",
        ]
    )
    return " ".join(parts)


def _live_upload_command(provider_key: str, profile_id: str) -> str:
    provider = str(provider_key or "").strip()
    target = str(profile_id or "").strip()
    if not provider or not target or provider not in {"guangya", "aliyundrive_open", "123_open", "baidu_netdisk", "xunlei", "pikpak", "quark", "uc"}:
        return ""
    return " ".join(
        [
            ".\\.venv\\Scripts\\python.exe",
            "scripts\\create_live_upload_task.py",
            f"--target-provider {provider}",
            f"--target-profile-id {target}",
            "--auto-temp-file",
            "--threshold-mb 1",
            "--conflict-policy auto_rename_new",
            f"--evidence-dir tmp\\{provider}-runtime-orphan-success-evidence",
        ]
    )


def _runtime_success_command(provider_key: str, profile_id: str) -> str:
    live_command = _live_upload_command(provider_key, profile_id)
    if live_command:
        return live_command
    return _fast_candidate_command(provider_key, profile_id)


def _overwrite_variant_command(command: str) -> str:
    text = str(command or "").strip()
    if not text or "--conflict-policy auto_rename_new" not in text:
        return ""
    return text.replace("--conflict-policy auto_rename_new", "--conflict-policy overwrite_existing", 1)


def _exact_runtime_helper(command: str, orphan_profile_id: str) -> str:
    text = str(command or "").strip()
    profile_id = str(orphan_profile_id or "").strip()
    if not text or not profile_id:
        return ""
    if "scripts\\create_runtime_probe_task.py" in text:
        return f".\\.venv\\Scripts\\python.exe scripts\\create_runtime_probe_task.py --from-runtime-orphan-profile {profile_id}"
    if "scripts\\create_live_upload_task.py" in text:
        return f".\\.venv\\Scripts\\python.exe scripts\\create_live_upload_task.py --from-runtime-orphan-profile {profile_id}"
    if "scripts\\create_fast_upload_candidate_task.py" in text:
        return f".\\.venv\\Scripts\\python.exe scripts\\create_fast_upload_candidate_task.py --from-runtime-orphan-profile {profile_id}"
    return ""


def _exact_refresh_helper(command: str, orphan_profile_id: str) -> str:
    text = str(command or "").strip()
    profile_id = str(orphan_profile_id or "").strip()
    if not text or not profile_id:
        return ""
    if "scripts\\patch_and_probe_auth_profile.py" in text:
        return f".\\.venv\\Scripts\\python.exe scripts\\patch_and_probe_auth_profile.py --from-runtime-orphan-profile {profile_id}"
    return ""


def _recommended_primary_command(
    *,
    create_command: str,
    refresh_command: str,
    runtime_probe_command: str,
    runtime_success_command: str,
    has_existing_provider_profiles: bool,
) -> tuple[str, str]:
    create_text = str(create_command or "").strip()
    refresh_text = str(refresh_command or "").strip()
    runtime_probe_text = str(runtime_probe_command or "").strip()
    runtime_success_text = str(runtime_success_command or "").strip()
    if not has_existing_provider_profiles and create_text:
        return ("Recreate Orphan Stub", create_text)
    if refresh_text:
        return ("Refresh Existing Orphan Profile", refresh_text)
    if runtime_probe_text:
        return ("Probe Existing Orphan Profile", runtime_probe_text)
    if runtime_success_text:
        return ("Run Runtime Success Command", runtime_success_text)
    return ("", "")


def build_runtime_orphan_recovery() -> dict[str, object]:
    runtime_rows = latest_task_runtime_evidence()
    saved_profiles = list_profiles()
    saved_profile_ids = {str(profile.profileId or "") for profile in saved_profiles if str(profile.profileId or "")}
    provider_profiles: dict[str, list[object]] = {}
    for profile in saved_profiles:
        provider_profiles.setdefault(str(profile.providerKey or ""), []).append(profile)

    orphan_groups: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in runtime_rows:
        provider_key = str(row.get("providerKey") or "")
        profile_id = str(row.get("profileId") or "")
        if not provider_key or not profile_id or profile_id in saved_profile_ids:
            continue
        if not bool(row.get("success")):
            continue
        if bool(row.get("candidateOnly")) or bool(row.get("probeOnly")):
            continue
        orphan_groups.setdefault((provider_key, profile_id), []).append(dict(row))

    items: list[dict[str, object]] = []
    for (provider_key, profile_id), rows in sorted(orphan_groups.items(), key=lambda item: (item[0][0], item[0][1])):
        auth_modes = provider_auth_modes(provider_key)
        field_hints = capture_field_hints(provider_key)
        preferred_auth_mode = _preferred_stub_auth_mode(provider_key, auth_modes)
        same_provider_profiles = provider_profiles.get(provider_key, [])
        sample_paths = sorted({str(row.get("path") or "") for row in rows if str(row.get("path") or "")})
        runtime_modes = sorted({str(row.get("mode") or "") for row in rows if str(row.get("mode") or "")})
        verify_modes = sorted({str(row.get("verifyMode") or "") for row in rows if str(row.get("verifyMode") or "")})
        conflict_policies = sorted({str(row.get("conflictPolicy") or "") for row in rows if str(row.get("conflictPolicy") or "")})
        conflict_actions = sorted({str(row.get("conflictAction") or "") for row in rows if str(row.get("conflictAction") or "")})
        latest_saved_at = max((str(row.get("savedAt") or "") for row in rows if str(row.get("savedAt") or "")), default="")
        command = _command_with_field_hints(provider_key, profile_id, preferred_auth_mode, field_hints)
        refresh_command = _refresh_evidence_command(provider_key, profile_id)
        runtime_probe_command = _runtime_probe_command(provider_key, profile_id)
        runtime_success_command = _runtime_success_command(provider_key, profile_id)
        primary_label, primary_command = _recommended_primary_command(
            create_command=command,
            refresh_command=refresh_command,
            runtime_probe_command=runtime_probe_command,
            runtime_success_command=runtime_success_command,
            has_existing_provider_profiles=bool(same_provider_profiles),
        )
        items.append(
            {
                "providerKey": provider_key,
                "providerDisplayName": _provider_display_name(provider_key),
                "orphanProfileId": profile_id,
                "sampleCount": len(rows),
                "pathCount": len(sample_paths),
                "paths": sample_paths,
                "runtimeModes": runtime_modes,
                "verifyModes": verify_modes,
                "conflictPolicies": conflict_policies,
                "conflictActions": conflict_actions,
                "latestSavedAt": latest_saved_at,
                "suggestedAuthModes": auth_modes,
                "preferredAuthMode": preferred_auth_mode,
                "requiredFieldHints": field_hints,
                "webLoginUrl": capture_login_url(provider_key),
                "officialDocsUrl": official_docs_url(provider_key),
                "existingProviderProfileCount": len(same_provider_profiles),
                "existingProviderProfileIds": [str(profile.profileId or "") for profile in same_provider_profiles if str(profile.profileId or "")],
                "existingProviderProfileNames": [str(profile.displayName or profile.profileId or "") for profile in same_provider_profiles],
                "recommendedCreateCommand": command,
                "recommendedRefreshEvidenceCommand": refresh_command,
                "recommendedRuntimeProbeCommand": runtime_probe_command,
                "recommendedRuntimeSuccessCommand": runtime_success_command,
                "recommendedOverwriteVariantCommand": _overwrite_variant_command(runtime_success_command or runtime_probe_command),
                "recommendedPrimaryCommandLabel": primary_label,
                "recommendedPrimaryCommand": primary_command,
                "nextStep": "先按原 runtime profileId 重建一个可复验 auth profile stub，再用真实凭证补字段并重跑 validation / live probe；只有这样，这条历史 runtime success 样本才有机会重新变成当前仓库可复验的证据。",
                "note": "这一步只是把历史 runtime success 样本对应的 profileId 恢复回当前仓库，不会自动把样本算成新的真实完成证据；仍需后续用真实凭证重新验证。",
            }
        )

    summary_orphan_providers = sorted(
        {str(item.get("providerKey") or "") for item in items if str(item.get("providerKey") or "")}
    )
    summary_saved_profile_providers = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if int(item.get("existingProviderProfileCount") or 0) > 0 and str(item.get("providerKey") or "")
        }
    )
    summary_missing_profile_providers = sorted(
        {
            str(item.get("providerKey") or "")
            for item in items
            if int(item.get("existingProviderProfileCount") or 0) <= 0 and str(item.get("providerKey") or "")
        }
    )
    summary = {
        "providerCount": len({str(item.get("providerKey") or "") for item in items if str(item.get("providerKey") or "")}),
        "orphanProfileCount": len(items),
        "runtimeSampleCount": sum(int(item.get("sampleCount") or 0) for item in items),
        "providersWithSavedProfiles": len({str(item.get("providerKey") or "") for item in items if int(item.get("existingProviderProfileCount") or 0) > 0}),
        "providersWithoutSavedProfiles": len({str(item.get("providerKey") or "") for item in items if int(item.get("existingProviderProfileCount") or 0) <= 0}),
        "orphanProviders": summary_orphan_providers,
        "orphanProfiles": [str(item.get("orphanProfileId") or "") for item in items if str(item.get("orphanProfileId") or "")],
        "providersWithSavedProfilesList": summary_saved_profile_providers,
        "providersWithoutSavedProfilesList": summary_missing_profile_providers,
    }
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "items": items,
    }


def recreate_runtime_orphan_profile(provider_key: str, orphan_profile_id: str) -> dict[str, object]:
    provider = str(provider_key or "").strip()
    profile_id = str(orphan_profile_id or "").strip()
    if not provider or not profile_id:
        return {"ok": False, "error": "provider_or_profile_missing"}

    existing = get_profile(profile_id)
    if existing is not None:
        refresh_command = _refresh_evidence_command(provider, profile_id)
        runtime_probe_command = _runtime_probe_command(provider, profile_id)
        runtime_success_command = _runtime_success_command(provider, profile_id)
        primary_label, primary_command = _recommended_primary_command(
            create_command="",
            refresh_command=refresh_command,
            runtime_probe_command=runtime_probe_command,
            runtime_success_command=runtime_success_command,
            has_existing_provider_profiles=True,
        )
        return {
            "ok": True,
            "created": False,
            "status": "already_exists",
            "message": "The orphan profileId is already present in the current repository; edit it directly and continue revalidation.",
            "item": auth_profile_view(existing),
            "recommendedRefreshEvidenceCommand": refresh_command,
            "recommendedRuntimeProbeCommand": runtime_probe_command,
            "recommendedRuntimeSuccessCommand": runtime_success_command,
            "recommendedOverwriteVariantCommand": _overwrite_variant_command(runtime_success_command or runtime_probe_command),
            "recommendedPrimaryCommandLabel": primary_label,
            "recommendedPrimaryCommand": primary_command,
        }

    payload = build_runtime_orphan_recovery()
    target_item = None
    for row in payload.get("items", []):
        item = dict(row or {})
        if str(item.get("providerKey") or "") == provider and str(item.get("orphanProfileId") or "") == profile_id:
            target_item = item
            break
    if target_item is None:
        return {"ok": False, "error": "runtime_orphan_not_found"}

    preferred_auth_mode = str(target_item.get("preferredAuthMode") or "").strip() or _preferred_stub_auth_mode(
        provider, provider_auth_modes(provider)
    )
    token, cookie = _placeholder_secret(preferred_auth_mode)
    extra = _extra_stub_fields(list(target_item.get("requiredFieldHints") or []), preferred_auth_mode)
    profile = save_profile(
        AuthProfileInput(
            providerKey=provider,
            authMode=preferred_auth_mode,
            displayName=f"{provider}-restore-{profile_id}",
            token=token,
            cookie=cookie,
            extra=extra,
        ),
        profile_id_override=profile_id,
    )
    refresh_command = _refresh_evidence_command(provider, profile_id)
    runtime_probe_command = _runtime_probe_command(provider, profile_id)
    runtime_success_command = _runtime_success_command(provider, profile_id)
    primary_label, primary_command = _recommended_primary_command(
        create_command="",
        refresh_command=refresh_command,
        runtime_probe_command=runtime_probe_command,
        runtime_success_command=runtime_success_command,
        has_existing_provider_profiles=True,
    )
    return {
        "ok": True,
        "created": True,
        "status": "stub_created",
        "message": "A placeholder auth profile stub was recreated for this runtime orphan. Fill the real credentials, then rerun validation/live probe before treating the old runtime success as re-verifiable evidence.",
        "item": auth_profile_view(profile),
        "requiredFieldHints": list(target_item.get("requiredFieldHints") or []),
        "recommendedCreateCommand": str(target_item.get("recommendedCreateCommand") or ""),
        "recommendedRefreshEvidenceCommand": refresh_command,
        "recommendedRuntimeProbeCommand": runtime_probe_command,
        "recommendedRuntimeSuccessCommand": runtime_success_command,
        "recommendedOverwriteVariantCommand": _overwrite_variant_command(runtime_success_command or runtime_probe_command),
        "recommendedPrimaryCommandLabel": primary_label,
        "recommendedPrimaryCommand": primary_command,
        "nextStep": str(target_item.get("nextStep") or ""),
    }


def runtime_orphan_recovery_to_markdown(payload: dict[str, object]) -> str:
    summary = dict(payload.get("summary") or {})
    lines: list[str] = []
    lines.append("# CloudPan Sync Runtime Orphan Recovery Guide")
    lines.append("")
    lines.append(f"- 生成时间：`{payload.get('generatedAt', '')}`")
    lines.append(
        "- 汇总："
        f" `providerCount={summary.get('providerCount', 0)}`"
        f" `orphanProfileCount={summary.get('orphanProfileCount', 0)}`"
        f" `runtimeSampleCount={summary.get('runtimeSampleCount', 0)}`"
        f" `providersWithSavedProfiles={summary.get('providersWithSavedProfiles', 0)}`"
        f" `providersWithoutSavedProfiles={summary.get('providersWithoutSavedProfiles', 0)}`"
    )
    lines.append(
        "- orphanSummary:"
        f" `providers={', '.join(summary.get('orphanProviders', [])) or '(none)'}`"
        f" `profiles={', '.join(summary.get('orphanProfiles', [])) or '(none)'}`"
        f" `savedProfileProviders={', '.join(summary.get('providersWithSavedProfilesList', [])) or '(none)'}`"
        f" `missingProfileProviders={', '.join(summary.get('providersWithoutSavedProfilesList', [])) or '(none)'}`"
    )
    lines.append("")
    lines.append("> 说明：这里的 recovery command 只是帮助你把历史 runtime success 对应的 `profileId` 重建回当前仓库，便于后续重新验证；它不会自动把旧样本算成新的真实完成证据。")
    lines.append("")
    for row in payload.get("items", []):
        item = dict(row or {})
        lines.append(f"## {item.get('providerKey', '')} - {item.get('providerDisplayName', '')} - {item.get('orphanProfileId', '')}")
        lines.append(f"- orphanProfileId: `{item.get('orphanProfileId', '')}`")
        lines.append(f"- sampleCount: `{item.get('sampleCount', 0)}` pathCount=`{item.get('pathCount', 0)}` latestSavedAt=`{item.get('latestSavedAt', '')}`")
        lines.append(
            f"- runtimeModes: `{', '.join(item.get('runtimeModes', [])) or '(none)'}` "
            f"verifyModes=`{', '.join(item.get('verifyModes', [])) or '(none)'}` "
            f"conflictPolicies=`{', '.join(item.get('conflictPolicies', [])) or '(none)'}` "
            f"conflictActions=`{', '.join(item.get('conflictActions', [])) or '(none)'}`"
        )
        lines.append(
            f"- existingProviderProfiles: count=`{item.get('existingProviderProfileCount', 0)}` "
            f"ids=`{', '.join(item.get('existingProviderProfileIds', [])) or '(none)'}` "
            f"names=`{', '.join(item.get('existingProviderProfileNames', [])) or '(none)'}`"
        )
        lines.append(
            f"- authHints: modes=`{', '.join(item.get('suggestedAuthModes', [])) or '(none)'}` "
            f"preferred=`{item.get('preferredAuthMode', '')}` "
            f"fields=`{' | '.join(item.get('requiredFieldHints', [])) or '(none)'}`"
        )
        if item.get("webLoginUrl"):
            lines.append(f"- webLoginUrl: {item.get('webLoginUrl', '')}")
        if item.get("officialDocsUrl"):
            lines.append(f"- officialDocsUrl: {item.get('officialDocsUrl', '')}")
        lines.append(f"- nextStep: {item.get('nextStep', '')}")
        lines.append(f"- note: {item.get('note', '')}")
        lines.append(f"- recommendedCreateCommand: `{item.get('recommendedCreateCommand', '')}`")
        if item.get("recommendedPrimaryCommand"):
            lines.append(
                f"- recommendedPrimaryCommand: `{item.get('recommendedPrimaryCommand', '')}` "
                f"`label={item.get('recommendedPrimaryCommandLabel', '')}`"
            )
        if item.get("recommendedRefreshEvidenceCommand"):
            lines.append(f"- recommendedRefreshEvidenceCommand: `{item.get('recommendedRefreshEvidenceCommand', '')}`")
            exact_refresh_helper = _exact_refresh_helper(
                str(item.get("recommendedRefreshEvidenceCommand") or ""),
                str(item.get("orphanProfileId") or ""),
            )
            if exact_refresh_helper:
                lines.append(f"- exactRefreshEvidenceHelper: `{exact_refresh_helper}`")
        if item.get("recommendedRuntimeProbeCommand"):
            lines.append(f"- recommendedRuntimeProbeCommand: `{item.get('recommendedRuntimeProbeCommand', '')}`")
            exact_runtime_probe_helper = _exact_runtime_helper(
                str(item.get("recommendedRuntimeProbeCommand") or ""),
                str(item.get("orphanProfileId") or ""),
            )
            if exact_runtime_probe_helper:
                lines.append(f"- exactRuntimeProbeHelper: `{exact_runtime_probe_helper}`")
        if item.get("recommendedRuntimeSuccessCommand"):
            lines.append(f"- recommendedRuntimeSuccessCommand: `{item.get('recommendedRuntimeSuccessCommand', '')}`")
            exact_runtime_success_helper = _exact_runtime_helper(
                str(item.get("recommendedRuntimeSuccessCommand") or ""),
                str(item.get("orphanProfileId") or ""),
            )
            if exact_runtime_success_helper:
                lines.append(f"- exactRuntimeSuccessHelper: `{exact_runtime_success_helper}`")
        if item.get("recommendedOverwriteVariantCommand"):
            lines.append(f"- recommendedOverwriteVariantCommand: `{item.get('recommendedOverwriteVariantCommand', '')}`")
        lines.append("")
    if not payload.get("items"):
        lines.append("- none")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
