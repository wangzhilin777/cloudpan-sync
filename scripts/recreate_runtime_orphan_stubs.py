from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from create_auth_profile_stub import _defaults_from_runtime_orphan_profile, _extract_stub_defaults, _parse_extra

from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_store import get_profile, save_profile
from cloudpan_sync.models import AuthProfileInput
from cloudpan_sync.runtime_orphan_recovery import build_runtime_orphan_recovery


def _normalize_list(values: list[str] | None) -> list[str]:
    return [str(value or "").strip() for value in (values or []) if str(value or "").strip()]


def _matches_filters(item: dict[str, object], provider_keys: set[str], orphan_profile_ids: set[str]) -> bool:
    provider_key = str(item.get("providerKey") or "").strip()
    orphan_profile_id = str(item.get("orphanProfileId") or "").strip()
    if provider_keys and provider_key not in provider_keys:
        return False
    if orphan_profile_ids and orphan_profile_id not in orphan_profile_ids:
        return False
    return True


def _build_profile_payload(defaults: dict[str, object], orphan_profile_id: str) -> AuthProfileInput:
    provider_key = str(defaults.get("providerKey") or "").strip()
    auth_mode = str(defaults.get("authMode") or "").strip()
    display_name = str(defaults.get("displayName") or "").strip() or f"{provider_key}-restore-{orphan_profile_id}"
    token = str(defaults.get("token") or "").strip()
    cookie = str(defaults.get("cookie") or "").strip()
    extra_values = [str(value or "").strip() for value in (defaults.get("extra") or []) if str(value or "").strip()]
    return AuthProfileInput(
        providerKey=provider_key,
        authMode=auth_mode,
        displayName=display_name,
        token=token,
        cookie=cookie,
        extra=_parse_extra(extra_values),
    )


def _defaults_from_item(item: dict[str, object]) -> dict[str, object]:
    command_defaults = _extract_stub_defaults(str(item.get("recommendedCreateCommand") or ""))
    if command_defaults:
        command_defaults["source"] = "runtime_orphan_item:recommendedCreateCommand"
        return command_defaults
    orphan_profile_id = str(item.get("orphanProfileId") or "").strip()
    return _defaults_from_runtime_orphan_profile(orphan_profile_id)


def _build_item_result(
    item: dict[str, object],
    *,
    write: bool,
    overwrite_existing: bool,
) -> dict[str, object]:
    orphan_profile_id = str(item.get("orphanProfileId") or "").strip()
    defaults = _defaults_from_item(item)
    if not defaults:
        return {
            "providerKey": str(item.get("providerKey") or ""),
            "orphanProfileId": orphan_profile_id,
            "selected": True,
            "ok": False,
            "action": "defaults_missing",
            "message": "runtime_orphan_defaults_missing",
        }

    payload = _build_profile_payload(defaults, orphan_profile_id)
    existing = get_profile(orphan_profile_id)
    existing_provider_key = str(getattr(existing, "providerKey", "") or "")

    result: dict[str, object] = {
        "providerKey": payload.providerKey,
        "orphanProfileId": orphan_profile_id,
        "selected": True,
        "ok": True,
        "defaultsSource": str(defaults.get("source") or ""),
        "existingProfile": existing is not None,
        "existingProviderKey": existing_provider_key,
        "authMode": payload.authMode,
        "displayName": payload.displayName,
        "tokenPlaceholder": payload.token,
        "cookiePlaceholder": payload.cookie,
        "extra": dict(payload.extra or {}),
        "recommendedPrimaryCommandLabel": str(item.get("recommendedPrimaryCommandLabel") or ""),
        "recommendedPrimaryCommand": str(item.get("recommendedPrimaryCommand") or ""),
        "recommendedCreateCommand": str(item.get("recommendedCreateCommand") or ""),
        "recommendedRefreshEvidenceCommand": str(item.get("recommendedRefreshEvidenceCommand") or ""),
        "recommendedRuntimeProbeCommand": str(item.get("recommendedRuntimeProbeCommand") or ""),
        "recommendedRuntimeSuccessCommand": str(item.get("recommendedRuntimeSuccessCommand") or ""),
        "recommendedOverwriteVariantCommand": str(item.get("recommendedOverwriteVariantCommand") or ""),
        "exactCreateHelper": str(item.get("exactCreateHelper") or ""),
        "exactRefreshEvidenceHelper": str(item.get("exactRefreshEvidenceHelper") or ""),
        "exactRuntimeProbeHelper": str(item.get("exactRuntimeProbeHelper") or ""),
        "exactRuntimeSuccessHelper": str(item.get("exactRuntimeSuccessHelper") or ""),
        "exactOverwriteVariantHelper": str(item.get("exactOverwriteVariantHelper") or ""),
    }

    if existing is not None and not overwrite_existing:
        result["action"] = "skip_existing"
        result["message"] = "profile_already_exists"
        return result

    result["action"] = "would_write" if not write else "written"
    result["message"] = "profile_stub_ready"
    if write:
        saved = save_profile(payload, profile_id_override=orphan_profile_id)
        result["writtenProfileId"] = saved.profileId
        result["writtenProviderKey"] = saved.providerKey
    return result


def main() -> None:
    custom_data_dir = str(os.environ.get("CLOUDPAN_SYNC_DATA_DIR") or "").strip()
    if custom_data_dir:
        configure_data_dir(custom_data_dir)

    parser = argparse.ArgumentParser(description="Batch recreate local auth profile stubs from runtime orphan recovery.")
    parser.add_argument("--provider-key", action="append", default=[], help="Only include this providerKey. Repeatable.")
    parser.add_argument("--orphan-profile-id", action="append", default=[], help="Only include this orphanProfileId. Repeatable.")
    parser.add_argument("--write", action="store_true", help="Actually recreate the selected local auth profile stubs.")
    parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help="Rewrite an existing local profileId instead of skipping it.",
    )
    args = parser.parse_args()

    provider_keys = set(_normalize_list(args.provider_key))
    orphan_profile_ids = set(_normalize_list(args.orphan_profile_id))

    payload = build_runtime_orphan_recovery()
    selected_items = [
        dict(item or {})
        for item in (payload.get("items") or [])
        if _matches_filters(dict(item or {}), provider_keys, orphan_profile_ids)
    ]

    if not selected_items:
        raise SystemExit("no_runtime_orphan_items_selected")

    items = [
        _build_item_result(
            item,
            write=bool(args.write),
            overwrite_existing=bool(args.overwrite_existing),
        )
        for item in selected_items
    ]

    print(
        json.dumps(
            {
                "write": bool(args.write),
                "overwriteExisting": bool(args.overwrite_existing),
                "filters": {
                    "providerKeys": sorted(provider_keys),
                    "orphanProfileIds": sorted(orphan_profile_ids),
                },
                "selectedCount": len(selected_items),
                "writtenCount": sum(1 for item in items if item.get("action") == "written"),
                "skippedExistingCount": sum(1 for item in items if item.get("action") == "skip_existing"),
                "defaultsMissingCount": sum(1 for item in items if item.get("action") == "defaults_missing"),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
