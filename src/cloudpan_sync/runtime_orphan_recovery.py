from __future__ import annotations

from datetime import datetime, timezone

from .auth_store import list_profiles
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
                "nextStep": "先按原 runtime profileId 重建一个可复验 auth profile stub，再用真实凭证补字段并重跑 validation / live probe；只有这样，这条历史 runtime success 样本才有机会重新变成当前仓库可复验的证据。",
                "note": "这一步只是把历史 runtime success 样本对应的 profileId 恢复回当前仓库，不会自动把样本算成新的真实完成证据；仍需后续用真实凭证重新验证。",
            }
        )

    summary = {
        "providerCount": len({str(item.get("providerKey") or "") for item in items if str(item.get("providerKey") or "")}),
        "orphanProfileCount": len(items),
        "runtimeSampleCount": sum(int(item.get("sampleCount") or 0) for item in items),
        "providersWithSavedProfiles": len({str(item.get("providerKey") or "") for item in items if int(item.get("existingProviderProfileCount") or 0) > 0}),
        "providersWithoutSavedProfiles": len({str(item.get("providerKey") or "") for item in items if int(item.get("existingProviderProfileCount") or 0) <= 0}),
        "orphanProviders": [str(item.get("providerKey") or "") for item in items if str(item.get("providerKey") or "")],
        "orphanProfiles": [str(item.get("orphanProfileId") or "") for item in items if str(item.get("orphanProfileId") or "")],
        "providersWithSavedProfilesList": [
            str(item.get("providerKey") or "") for item in items if int(item.get("existingProviderProfileCount") or 0) > 0
        ],
        "providersWithoutSavedProfilesList": [
            str(item.get("providerKey") or "") for item in items if int(item.get("existingProviderProfileCount") or 0) <= 0
        ],
    }
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "items": items,
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
        lines.append("")
    if not payload.get("items"):
        lines.append("- none")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
