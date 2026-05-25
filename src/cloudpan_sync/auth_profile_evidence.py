from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from .auth_live_validate import append_live_validation, latest_live_validation_for_profile, validate_profile_object
from .auth_store import update_profile
from .provider_live_probe import run_provider_live_probe
from .provider_live_probe_store import latest_provider_live_probe_for_profile, save_provider_live_probe


def build_auth_profile_evidence(
    *,
    profile: object,
    profile_view: dict[str, object],
) -> dict[str, object]:
    validation = latest_live_validation_for_profile(getattr(profile, "profileId", ""))
    probe = latest_provider_live_probe_for_profile(
        profile_id=getattr(profile, "profileId", ""),
        provider_key=str(getattr(profile, "providerKey", "") or ""),
    )
    return {
        "profile": profile_view,
        "latestValidation": validation,
        "latestProbe": probe,
        "summary": {
            "profileReady": bool(profile_view.get("profileReady")),
            "writeReady": bool(profile_view.get("writeReady", True)),
            "validationOk": bool((validation or {}).get("ok")) if validation is not None else False,
            "probeOk": bool((probe or {}).get("ok")) if probe is not None else False,
            "resolvedParentId": str(profile_view.get("resolvedParentId") or ""),
            "resolvedFileId": str(profile_view.get("resolvedFileId") or ""),
        },
    }


def refresh_auth_profile_evidence(
    *,
    profile: object,
    page_size: int = 100,
    dir_name: str = "",
    persist: bool = True,
    profile_view_builder: Callable[[object], dict[str, object]] | None = None,
) -> dict[str, object]:
    validation = validate_profile_object(profile)
    if bool(validation.get("ok")):
        profile.status = "verified"
        profile.lastError = ""
    else:
        profile.status = "invalid"
        profile.lastError = str(validation.get("error") or validation.get("summary") or "live_validation_failed")
    profile.updatedAt = datetime.now(timezone.utc).isoformat()

    if persist:
        update_profile(profile)
        append_live_validation(validation)

    resolved_parent_id = str(validation.get("parentId") or getattr(profile, "extra", {}).get("parentId") or "")
    resolved_file_id = str(validation.get("fileId") or getattr(profile, "extra", {}).get("fileId") or "")
    probe = run_provider_live_probe(
        profile_id=getattr(profile, "profileId", ""),
        parent_id=resolved_parent_id,
        file_id=resolved_file_id,
        page_size=max(1, int(page_size or 100)),
        dir_name=str(dir_name or getattr(profile, "extra", {}).get("dirName") or "").strip(),
    )
    if persist:
        save_provider_live_probe(probe)

    profile_view = profile_view_builder(profile) if callable(profile_view_builder) else getattr(profile, "model_dump", lambda: {})()
    return build_auth_profile_evidence(profile=profile, profile_view=profile_view)


def auth_profile_evidence_to_markdown(payload: dict[str, object]) -> str:
    profile = dict(payload.get("profile") or {})
    validation = dict(payload.get("latestValidation") or {})
    probe = dict(payload.get("latestProbe") or {})
    summary = dict(payload.get("summary") or {})
    lines: list[str] = []
    lines.append("# Auth Profile Evidence")
    lines.append("")
    lines.append(f"- profileId: `{profile.get('profileId', '')}`")
    lines.append(f"- providerKey: `{profile.get('providerKey', '')}`")
    lines.append(f"- displayName: `{profile.get('displayName', '')}`")
    lines.append(f"- profileReady: `{summary.get('profileReady', False)}`")
    lines.append(f"- writeReady: `{summary.get('writeReady', True)}`")
    lines.append(f"- validationOk: `{summary.get('validationOk', False)}`")
    lines.append(f"- probeOk: `{summary.get('probeOk', False)}`")
    lines.append(f"- resolvedParentId: `{summary.get('resolvedParentId', '')}`")
    lines.append(f"- resolvedFileId: `{summary.get('resolvedFileId', '')}`")
    if profile.get("missingFieldHints"):
        lines.append(f"- missingFieldHints: `{', '.join(profile.get('missingFieldHints', []))}`")
    if profile.get("placeholderFieldHints"):
        lines.append(f"- placeholderFieldHints: `{', '.join(profile.get('placeholderFieldHints', []))}`")
    if profile.get("placeholderSecretFieldHints"):
        lines.append(f"- placeholderSecretFieldHints: `{', '.join(profile.get('placeholderSecretFieldHints', []))}`")
    if profile.get("writeMissingFieldHints"):
        lines.append(f"- writeMissingFieldHints: `{', '.join(profile.get('writeMissingFieldHints', []))}`")
    if profile.get("writeBlockerNote"):
        lines.append(f"- writeBlockerNote: {profile.get('writeBlockerNote', '')}")
    lines.append("")
    lines.append("## Latest Validation")
    lines.append("")
    if validation:
        lines.append(f"- ok: `{validation.get('ok', False)}`")
        lines.append(f"- mode: `{validation.get('mode', '')}`")
        lines.append(f"- status: `{validation.get('status', 0)}`")
        lines.append(f"- error: `{validation.get('error', '')}`")
        lines.append(f"- summary: {validation.get('summary', '')}")
        lines.append(f"- checkedAt: `{validation.get('checkedAt', '')}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Latest Probe")
    lines.append("")
    if probe:
        lines.append(f"- ok: `{probe.get('ok', False)}`")
        lines.append(f"- mode: `{probe.get('mode', '')}`")
        lines.append(f"- summary: {probe.get('summary', '')}")
        lines.append("- checks:")
        for check in probe.get("checks", []):
            row = dict(check or {})
            lines.append(
                f"  - `{row.get('kind', '')}` ok={row.get('ok', False)} status={row.get('status', 0)} error={row.get('error', '')} note={row.get('note', '')}"
            )
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_auth_evidence_bundle(
    *,
    profiles: list[object],
    profile_view_builder: Callable[[object], dict[str, object]],
) -> dict[str, object]:
    items = [
        build_auth_profile_evidence(profile=profile, profile_view=profile_view_builder(profile))
        for profile in profiles
    ]
    return {
        "summary": _auth_evidence_bundle_summary(items),
        "items": items,
    }


def _auth_evidence_bundle_summary(items: list[dict[str, object]]) -> dict[str, object]:
    profile_ready_profiles = sorted(
        {
            str(((item.get("profile") or {}).get("displayName") or (item.get("profile") or {}).get("profileId") or ""))
            for item in items
            if bool((item.get("summary") or {}).get("profileReady"))
            and str(((item.get("profile") or {}).get("displayName") or (item.get("profile") or {}).get("profileId") or ""))
        }
    )
    write_ready_profiles = sorted(
        {
            str(((item.get("profile") or {}).get("displayName") or (item.get("profile") or {}).get("profileId") or ""))
            for item in items
            if bool((item.get("summary") or {}).get("writeReady", True))
            and str(((item.get("profile") or {}).get("displayName") or (item.get("profile") or {}).get("profileId") or ""))
        }
    )
    validation_ok_profiles = sorted(
        {
            str(((item.get("profile") or {}).get("displayName") or (item.get("profile") or {}).get("profileId") or ""))
            for item in items
            if bool((item.get("summary") or {}).get("validationOk"))
            and str(((item.get("profile") or {}).get("displayName") or (item.get("profile") or {}).get("profileId") or ""))
        }
    )
    probe_ok_profiles = sorted(
        {
            str(((item.get("profile") or {}).get("displayName") or (item.get("profile") or {}).get("profileId") or ""))
            for item in items
            if bool((item.get("summary") or {}).get("probeOk"))
            and str(((item.get("profile") or {}).get("displayName") or (item.get("profile") or {}).get("profileId") or ""))
        }
    )
    return {
        "profileCount": len(items),
        "profileReadyCount": sum(1 for item in items if bool((item.get("summary") or {}).get("profileReady"))),
        "writeReadyCount": sum(1 for item in items if bool((item.get("summary") or {}).get("writeReady", True))),
        "validationOkCount": sum(1 for item in items if bool((item.get("summary") or {}).get("validationOk"))),
        "probeOkCount": sum(1 for item in items if bool((item.get("summary") or {}).get("probeOk"))),
        "profileReadyProfiles": profile_ready_profiles,
        "writeReadyProfiles": write_ready_profiles,
        "validationOkProfiles": validation_ok_profiles,
        "probeOkProfiles": probe_ok_profiles,
    }


def refresh_auth_evidence_bundle(
    *,
    profiles: list[object],
    profile_view_builder: Callable[[object], dict[str, object]],
    page_size: int = 100,
    dir_name: str = "",
    persist: bool = True,
) -> dict[str, object]:
    items = [
        refresh_auth_profile_evidence(
            profile=profile,
            page_size=page_size,
            dir_name=dir_name,
            persist=persist,
            profile_view_builder=profile_view_builder,
        )
        for profile in profiles
    ]
    return {
        "summary": _auth_evidence_bundle_summary(items),
        "items": items,
    }


def auth_evidence_bundle_to_markdown(payload: dict[str, object]) -> str:
    summary = dict(payload.get("summary") or {})
    items = list(payload.get("items") or [])
    lines: list[str] = []
    lines.append("# Auth Evidence Bundle")
    lines.append("")
    lines.append(f"- profileCount: `{summary.get('profileCount', 0)}`")
    lines.append(f"- profileReadyCount: `{summary.get('profileReadyCount', 0)}`")
    lines.append(f"- writeReadyCount: `{summary.get('writeReadyCount', 0)}`")
    lines.append(f"- validationOkCount: `{summary.get('validationOkCount', 0)}`")
    lines.append(f"- probeOkCount: `{summary.get('probeOkCount', 0)}`")
    lines.append(
        f"- profileSummary: `profileReady={', '.join(summary.get('profileReadyProfiles', [])) or '(none)'}` "
        f"`writeReady={', '.join(summary.get('writeReadyProfiles', [])) or '(none)'}` "
        f"`validationOk={', '.join(summary.get('validationOkProfiles', [])) or '(none)'}` "
        f"`probeOk={', '.join(summary.get('probeOkProfiles', [])) or '(none)'}`"
    )
    lines.append("")
    lines.append("## Profiles")
    lines.append("")
    for item in items:
        evidence = dict(item or {})
        profile = dict(evidence.get("profile") or {})
        item_summary = dict(evidence.get("summary") or {})
        validation = dict(evidence.get("latestValidation") or {})
        probe = dict(evidence.get("latestProbe") or {})
        lines.append(f"### {profile.get('displayName', '')} [{profile.get('providerKey', '')}]")
        lines.append(f"- profileId: `{profile.get('profileId', '')}`")
        lines.append(f"- profileReady: `{item_summary.get('profileReady', False)}`")
        lines.append(f"- writeReady: `{item_summary.get('writeReady', True)}`")
        lines.append(f"- validationOk: `{item_summary.get('validationOk', False)}`")
        lines.append(f"- probeOk: `{item_summary.get('probeOk', False)}`")
        lines.append(f"- resolvedParentId: `{item_summary.get('resolvedParentId', '')}`")
        lines.append(f"- resolvedFileId: `{item_summary.get('resolvedFileId', '')}`")
        if profile.get("missingFieldHints"):
            lines.append(f"- missingFieldHints: `{', '.join(profile.get('missingFieldHints', []))}`")
        if profile.get("placeholderFieldHints"):
            lines.append(f"- placeholderFieldHints: `{', '.join(profile.get('placeholderFieldHints', []))}`")
        if profile.get("placeholderSecretFieldHints"):
            lines.append(f"- placeholderSecretFieldHints: `{', '.join(profile.get('placeholderSecretFieldHints', []))}`")
        if profile.get("writeMissingFieldHints"):
            lines.append(f"- writeMissingFieldHints: `{', '.join(profile.get('writeMissingFieldHints', []))}`")
        if profile.get("writeBlockerNote"):
            lines.append(f"- writeBlockerNote: {profile.get('writeBlockerNote', '')}")
        if validation:
            lines.append(f"- latestValidation: `{validation.get('summary', '')}`")
        if probe:
            lines.append(f"- latestProbe: `{probe.get('summary', '')}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
