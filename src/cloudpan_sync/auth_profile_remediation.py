from __future__ import annotations


def _patch_command_for_profile(profile: dict[str, object]) -> str:
    profile_id = str(profile.get("profileId") or "")
    provider_key = str(profile.get("providerKey") or "")
    base = f".\\.venv\\Scripts\\python.exe scripts\\patch_auth_profile_extra.py --profile-id {profile_id}"
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


def recreate_probe_command_for_profile(profile: dict[str, object]) -> str:
    provider_key = str(profile.get("providerKey") or "")
    auth_mode = str(profile.get("authMode") or "")
    display_name = str(profile.get("displayName") or f"{provider_key}-{auth_mode}").strip()
    base = f".\\.venv\\Scripts\\python.exe scripts\\create_auth_profile_stub.py --provider-key {provider_key} --auth-mode {auth_mode} --display-name {display_name}"

    if auth_mode == "manual_cookie":
        base = f"{base} --cookie YOUR_COOKIE"
    elif auth_mode in {"manual_token", "official_oauth"}:
        base = f"{base} --token YOUR_TOKEN"

    if provider_key == "guangya":
        return f"{base} --set parentId=YOUR_REAL_PARENT_ID --probe"
    if provider_key == "aliyundrive_open":
        return f"{base} --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --probe"
    if provider_key == "189cloud":
        return f"{base} --set shareCode=YOUR_SHARE_CODE --set accessCode=YOUR_ACCESS_CODE --probe"
    if provider_key == "115_open":
        return f"{base} --set parentId=YOUR_PARENT_ID --probe"
    if provider_key in {"quark", "uc"}:
        return f"{base} --set pwdId=YOUR_SHARE_PWD_ID --probe"
    if provider_key == "xunlei":
        return f"{base} --set deviceId=YOUR_DEVICE_ID --probe"
    if provider_key == "pikpak":
        return f"{base} --set deviceId=YOUR_DEVICE_ID --probe"
    if provider_key == "123_open":
        return f"{base} --set parentFileId=YOUR_PARENT_FILE_ID --probe"
    if provider_key == "baidu_netdisk":
        return f"{base} --set fileId=YOUR_FILE_ID --probe"
    return f"{base} --probe"


def build_auth_remediation_bundle(*, profile_views: list[dict[str, object]]) -> dict[str, object]:
    items: list[dict[str, object]] = []
    for profile in profile_views:
        missing = list(profile.get("missingFieldHints") or [])
        profile_ready = bool(profile.get("profileReady"))
        write_ready = bool(profile.get("writeReady", True))
        needs_secret_refresh = bool(profile.get("needsSecretRefresh"))
        needs_patch = (not profile_ready) or (not write_ready)
        recommended_patch_command = _patch_command_for_profile(profile) if (needs_patch and not needs_secret_refresh) else ""
        recommended_recreate_probe_command = recreate_probe_command_for_profile(profile) if needs_secret_refresh else ""
        items.append(
            {
                "profileId": str(profile.get("profileId") or ""),
                "providerKey": str(profile.get("providerKey") or ""),
                "displayName": str(profile.get("displayName") or ""),
                "profileReady": profile_ready,
                "writeReady": write_ready,
                "missingFieldHints": missing,
                "placeholderFieldHints": list(profile.get("placeholderFieldHints") or []),
                "placeholderSecretFieldHints": list(profile.get("placeholderSecretFieldHints") or []),
                "needsSecretRefresh": needs_secret_refresh,
                "liveRejectedProfiles": list(profile.get("liveRejectedProfiles") or []),
                "placeholderLiveRejectedProfiles": list(profile.get("placeholderLiveRejectedProfiles") or []),
                "liveRejectedStatuses": list(profile.get("liveRejectedStatuses") or []),
                "liveRejectedSummaries": list(profile.get("liveRejectedSummaries") or []),
                "writeMissingFieldHints": list(profile.get("writeMissingFieldHints") or []),
                "writeBlockerNote": str(profile.get("writeBlockerNote") or ""),
                "resolvedParentId": str(profile.get("resolvedParentId") or ""),
                "resolvedFileId": str(profile.get("resolvedFileId") or ""),
                "recommendedPatchCommand": recommended_patch_command,
                "recommendedRecreateProbeCommand": recommended_recreate_probe_command,
            }
        )
    ready_profiles = sorted(
        {
            str(item.get("displayName") or item.get("profileId") or "")
            for item in items
            if bool(item.get("profileReady"))
            and str(item.get("displayName") or item.get("profileId") or "")
        }
    )
    needs_fix_profiles = sorted(
        {
            str(item.get("displayName") or item.get("profileId") or "")
            for item in items
            if not bool(item.get("profileReady"))
            and str(item.get("displayName") or item.get("profileId") or "")
        }
    )
    write_ready_profiles = sorted(
        {
            str(item.get("displayName") or item.get("profileId") or "")
            for item in items
            if bool(item.get("writeReady", True))
            and str(item.get("displayName") or item.get("profileId") or "")
        }
    )
    write_needs_fix_profiles = sorted(
        {
            str(item.get("displayName") or item.get("profileId") or "")
            for item in items
            if not bool(item.get("writeReady", True))
            and str(item.get("displayName") or item.get("profileId") or "")
        }
    )
    needs_secret_refresh_profiles = sorted(
        {
            str(item.get("displayName") or item.get("profileId") or "")
            for item in items
            if bool(item.get("needsSecretRefresh"))
            and str(item.get("displayName") or item.get("profileId") or "")
        }
    )
    return {
        "summary": {
            "profileCount": len(items),
            "readyCount": sum(1 for item in items if bool(item.get("profileReady"))),
            "needsFixCount": sum(1 for item in items if not bool(item.get("profileReady"))),
            "writeReadyCount": sum(1 for item in items if bool(item.get("writeReady", True))),
            "writeNeedsFixCount": sum(1 for item in items if not bool(item.get("writeReady", True))),
            "needsSecretRefreshCount": sum(1 for item in items if bool(item.get("needsSecretRefresh"))),
            "readyProfiles": ready_profiles,
            "needsFixProfiles": needs_fix_profiles,
            "writeReadyProfiles": write_ready_profiles,
            "writeNeedsFixProfiles": write_needs_fix_profiles,
            "needsSecretRefreshProfiles": needs_secret_refresh_profiles,
        },
        "items": items,
    }


def auth_remediation_bundle_to_markdown(payload: dict[str, object]) -> str:
    summary = dict(payload.get("summary") or {})
    items = list(payload.get("items") or [])
    lines: list[str] = []
    lines.append("# 授权补救指南 / Auth Remediation Guide")
    lines.append("")
    lines.append(f"- profileCount: `{summary.get('profileCount', 0)}`")
    lines.append(f"- readyCount: `{summary.get('readyCount', 0)}`")
    lines.append(f"- needsFixCount: `{summary.get('needsFixCount', 0)}`")
    lines.append(f"- writeReadyCount: `{summary.get('writeReadyCount', 0)}`")
    lines.append(f"- writeNeedsFixCount: `{summary.get('writeNeedsFixCount', 0)}`")
    lines.append(f"- needsSecretRefreshCount: `{summary.get('needsSecretRefreshCount', 0)}`")
    lines.append(
        f"- profileSummary: `ready={', '.join(summary.get('readyProfiles', [])) or '(none)'}` "
        f"`needsFix={', '.join(summary.get('needsFixProfiles', [])) or '(none)'}` "
        f"`writeReady={', '.join(summary.get('writeReadyProfiles', [])) or '(none)'}` "
        f"`writeNeedsFix={', '.join(summary.get('writeNeedsFixProfiles', [])) or '(none)'}` "
        f"`needsSecretRefresh={', '.join(summary.get('needsSecretRefreshProfiles', [])) or '(none)'}`"
    )
    lines.append("")
    lines.append("## 档案清单 / Profiles")
    lines.append("")
    for item in items:
        row = dict(item or {})
        lines.append(f"### {row.get('displayName', '')} [{row.get('providerKey', '')}]")
        lines.append(f"- profileId: `{row.get('profileId', '')}`")
        lines.append(f"- profileReady: `{row.get('profileReady', False)}`")
        lines.append(f"- writeReady: `{row.get('writeReady', True)}`")
        lines.append(f"- resolvedParentId: `{row.get('resolvedParentId', '')}`")
        lines.append(f"- resolvedFileId: `{row.get('resolvedFileId', '')}`")
        missing = list(row.get("missingFieldHints") or [])
        if missing:
            lines.append(f"- missingFieldHints: `{', '.join(missing)}`")
        placeholder_missing = list(row.get("placeholderFieldHints") or [])
        if placeholder_missing:
            lines.append(f"- placeholderFieldHints: `{', '.join(placeholder_missing)}`")
        placeholder_secret_missing = list(row.get("placeholderSecretFieldHints") or [])
        if placeholder_secret_missing:
            lines.append(f"- placeholderSecretFieldHints: `{', '.join(placeholder_secret_missing)}`")
        if row.get("placeholderLiveRejectedProfiles") or row.get("liveRejectedProfiles"):
            lines.append(
                f"- liveRejected: profiles=`{', '.join(row.get('liveRejectedProfiles') or []) or '(none)'}` "
                f"placeholderProfiles=`{', '.join(row.get('placeholderLiveRejectedProfiles') or []) or '(none)'}` "
                f"statuses=`{', '.join(row.get('liveRejectedStatuses') or []) or '(none)'}`"
            )
        if row.get("liveRejectedSummaries"):
            lines.append(f"- liveRejectedSummaries: `{ ' | '.join(row.get('liveRejectedSummaries') or []) }`")
        write_missing = list(row.get("writeMissingFieldHints") or [])
        if write_missing:
            lines.append(f"- writeMissingFieldHints: `{', '.join(write_missing)}`")
        if row.get("writeBlockerNote"):
            lines.append(f"- writeBlockerNote: {row.get('writeBlockerNote', '')}")
        if row.get("recommendedPatchCommand"):
            lines.append(f"- recommendedPatchCommand: `{row.get('recommendedPatchCommand', '')}`")
        if row.get("recommendedRecreateProbeCommand"):
            lines.append(f"- recommendedRecreateProbeCommand: `{row.get('recommendedRecreateProbeCommand', '')}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
