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
        return f"{base} --set shareCode=YOUR_SHARE_CODE --set accessToken=YOUR_ACCESS_TOKEN --set signature=YOUR_SIGNATURE --set date=YOUR_GMT_DATE --write --revalidate"
    if provider_key == "xunlei":
        return f"{base} --set deviceId=YOUR_DEVICE_ID --write --revalidate"
    if provider_key in {"quark", "uc"}:
        return f"{base} --set pwdId=YOUR_SHARE_PWD_ID --write --revalidate"
    return f"{base} --set key=value --write --revalidate"


def build_auth_remediation_bundle(*, profile_views: list[dict[str, object]]) -> dict[str, object]:
    items: list[dict[str, object]] = []
    for profile in profile_views:
        missing = list(profile.get("missingFieldHints") or [])
        profile_ready = bool(profile.get("profileReady"))
        items.append(
            {
                "profileId": str(profile.get("profileId") or ""),
                "providerKey": str(profile.get("providerKey") or ""),
                "displayName": str(profile.get("displayName") or ""),
                "profileReady": profile_ready,
                "writeReady": bool(profile.get("writeReady", True)),
                "missingFieldHints": missing,
                "writeMissingFieldHints": list(profile.get("writeMissingFieldHints") or []),
                "writeBlockerNote": str(profile.get("writeBlockerNote") or ""),
                "resolvedParentId": str(profile.get("resolvedParentId") or ""),
                "resolvedFileId": str(profile.get("resolvedFileId") or ""),
                "recommendedPatchCommand": "" if profile_ready else _patch_command_for_profile(profile),
            }
        )
    return {
        "summary": {
            "profileCount": len(items),
            "readyCount": sum(1 for item in items if bool(item.get("profileReady"))),
            "needsFixCount": sum(1 for item in items if not bool(item.get("profileReady"))),
            "writeReadyCount": sum(1 for item in items if bool(item.get("writeReady", True))),
            "writeNeedsFixCount": sum(1 for item in items if not bool(item.get("writeReady", True))),
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
        write_missing = list(row.get("writeMissingFieldHints") or [])
        if write_missing:
            lines.append(f"- writeMissingFieldHints: `{', '.join(write_missing)}`")
        if row.get("writeBlockerNote"):
            lines.append(f"- writeBlockerNote: {row.get('writeBlockerNote', '')}")
        if row.get("recommendedPatchCommand"):
            lines.append(f"- recommendedPatchCommand: `{row.get('recommendedPatchCommand', '')}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
