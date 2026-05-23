from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from . import auth_live_validate, auth_store, provider_live_probe_store
from .models import AuthProfile


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def configure_data_dir(data_dir: str | Path) -> None:
    base_dir = Path(data_dir)
    auth_store.DATA_DIR = base_dir
    auth_store.AUTH_FILE = base_dir / "auth_profiles.json"
    auth_live_validate.DATA_DIR = base_dir
    auth_live_validate.VALIDATION_FILE = base_dir / "auth_live_validations.json"
    provider_live_probe_store.DATA_DIR = base_dir
    provider_live_probe_store.PROBE_FILE = base_dir / "provider_live_probes.json"


def _matches_selector(
    profile: AuthProfile,
    profile_ids: set[str],
    provider_key: str,
    display_name_contains: str,
) -> bool:
    if profile_ids and profile.profileId not in profile_ids:
        return False
    if provider_key and profile.providerKey != provider_key:
        return False
    if display_name_contains and display_name_contains not in profile.displayName.lower():
        return False
    return True


def _build_patched_profile(profile: AuthProfile, extra_updates: dict[str, str]) -> AuthProfile:
    merged_extra = dict(profile.extra or {})
    changed_keys: list[str] = []
    for key, value in extra_updates.items():
        text = str(value or "").strip()
        if not text:
            continue
        if merged_extra.get(key) != text:
            changed_keys.append(key)
        merged_extra[key] = text
    updated = profile.model_copy(deep=True)
    updated.extra = merged_extra
    updated.updatedAt = _now_iso()
    return updated


def select_auth_profiles(
    *,
    profile_ids: list[str] | None = None,
    provider_key: str = "",
    display_name_contains: str = "",
) -> list[AuthProfile]:
    normalized_profile_ids = {item.strip() for item in (profile_ids or []) if item.strip()}
    provider_key = provider_key.strip()
    display_name_contains = display_name_contains.strip().lower()
    return [
        profile
        for profile in auth_store.list_profiles()
        if _matches_selector(profile, normalized_profile_ids, provider_key, display_name_contains)
    ]


def patch_auth_profiles(
    *,
    extra_updates: dict[str, str],
    profile_ids: list[str] | None = None,
    provider_key: str = "",
    display_name_contains: str = "",
    write: bool = False,
    revalidate: bool = False,
) -> dict[str, object]:
    selected = select_auth_profiles(
        profile_ids=profile_ids,
        provider_key=provider_key,
        display_name_contains=display_name_contains,
    )
    items: list[dict[str, object]] = []

    for profile in selected:
        before_extra = dict(profile.extra or {})
        updated = _build_patched_profile(profile, extra_updates)
        validation: dict[str, object] | None = None
        if revalidate:
            validation = auth_live_validate.validate_profile_object(updated)
            if bool(validation.get("ok")):
                updated.status = "verified"
                updated.lastError = ""
            else:
                updated.status = "invalid"
                updated.lastError = str(validation.get("error") or validation.get("summary") or "live_validation_failed")
            updated.updatedAt = _now_iso()
        if write:
            auth_store.update_profile(updated)
            if validation is not None:
                auth_live_validate.append_live_validation(validation)
        items.append(
            {
                "profileId": profile.profileId,
                "providerKey": profile.providerKey,
                "displayName": profile.displayName,
                "beforeExtra": before_extra,
                "afterExtra": dict(updated.extra or {}),
                "changedKeys": sorted(
                    key for key in updated.extra.keys() if before_extra.get(key) != updated.extra.get(key)
                ),
                "statusBefore": profile.status,
                "statusAfter": updated.status,
                "lastErrorBefore": profile.lastError,
                "lastErrorAfter": updated.lastError,
                "written": write,
                "revalidated": revalidate,
                "validation": validation,
            }
        )

    return {
        "matchedCount": len(selected),
        "writtenCount": len(selected) if write else 0,
        "revalidatedCount": len(selected) if revalidate else 0,
        "items": items,
    }
