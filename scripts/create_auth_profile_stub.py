from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.auth_profile_evidence import auth_profile_evidence_to_markdown, refresh_auth_profile_evidence
from cloudpan_sync.auth_profile_patch import configure_data_dir
from cloudpan_sync.auth_live_validate import run_profile_live_validation
from cloudpan_sync.auth_store import save_profile
from cloudpan_sync.models import AuthProfileInput
from cloudpan_sync.real_evidence_remediation import build_real_evidence_remediation_bundle
from cloudpan_sync.runtime_orphan_recovery import build_runtime_orphan_recovery
from cloudpan_sync.webapp import _auth_profile_evidence


def _parse_extra(values: list[str]) -> dict[str, str]:
    extra: dict[str, str] = {}
    for value in values:
        text = str(value or "").strip()
        if not text or "=" not in text:
            continue
        key, raw = text.split("=", 1)
        key = key.strip()
        raw = raw.strip()
        if key and raw:
            extra[key] = raw
    return extra


def _remediation_followup(profile_id: str) -> dict[str, object]:
    payload = build_real_evidence_remediation_bundle()
    for item in payload.get("items", []):
        row = dict(item or {})
        profile_ids = [str(value or "") for value in (row.get("profileIds") or [])]
        if profile_id not in profile_ids:
            continue
        return {
            "nextStep": str(row.get("nextStep") or ""),
            "needsSecretRefresh": bool(row.get("needsSecretRefresh")),
            "placeholderSecretFieldHints": list(row.get("placeholderSecretFieldHints") or []),
            "recommendedPrimaryCommandLabel": str(row.get("recommendedPrimaryCommandLabel") or ""),
            "recommendedPrimaryCommand": str(row.get("recommendedPrimaryCommand") or ""),
            "recommendedRecreateProbeCommand": str(row.get("recommendedRecreateProbeCommand") or ""),
            "recommendedRefreshEvidenceCommand": str(row.get("recommendedRefreshEvidenceCommand") or ""),
            "recommendedPostRefreshRuntimeCommand": str(row.get("recommendedPostRefreshRuntimeCommand") or ""),
            "recommendedRuntimeSuccessCommand": str(row.get("recommendedRuntimeSuccessCommand") or ""),
            "recommendedOverwriteVariantCommand": str(row.get("recommendedOverwriteVariantCommand") or ""),
        }
    return {}


def _extract_stub_defaults(command: str) -> dict[str, object]:
    text = str(command or "").strip()
    if not text or "create_auth_profile_stub.py" not in text:
        return {}
    tokens = shlex.split(text, posix=False)
    defaults: dict[str, object] = {"extra": []}
    index = 0
    while index < len(tokens):
        token = str(tokens[index] or "").strip()
        next_value = str(tokens[index + 1] or "").strip() if index + 1 < len(tokens) else ""
        if token == "--provider-key" and next_value:
            defaults["providerKey"] = next_value
            index += 2
            continue
        if token == "--auth-mode" and next_value:
            defaults["authMode"] = next_value
            index += 2
            continue
        if token == "--display-name" and next_value:
            defaults["displayName"] = next_value
            index += 2
            continue
        if token == "--profile-id" and next_value:
            defaults["profileId"] = next_value
            index += 2
            continue
        if token == "--token" and next_value:
            defaults["token"] = next_value
            index += 2
            continue
        if token == "--cookie" and next_value:
            defaults["cookie"] = next_value
            index += 2
            continue
        if token == "--set" and next_value:
            casted = defaults.get("extra")
            if isinstance(casted, list):
                casted.append(next_value)
            index += 2
            continue
        if token == "--probe":
            defaults["probe"] = True
        if token == "--validate":
            defaults["validate"] = True
        index += 1
    return defaults


def _command_profile_id(command: str) -> str:
    defaults = _extract_stub_defaults(command)
    return str(defaults.get("profileId") or "").strip()


def _defaults_from_commands(
    commands: list[str],
    *,
    source_prefix: str,
    source_key: str,
    profile_id: str = "",
) -> dict[str, object]:
    target_profile_id = str(profile_id or "").strip()
    fallback: dict[str, object] = {}
    for command in commands:
        defaults = _extract_stub_defaults(str(command or ""))
        if not defaults:
            continue
        if not fallback:
            fallback = dict(defaults)
        if target_profile_id and _command_profile_id(str(command or "")) != target_profile_id:
            continue
        defaults["source"] = f"{source_prefix}:{source_key}"
        return defaults
    if fallback and not target_profile_id:
        fallback["source"] = f"{source_prefix}:{source_key}"
        return fallback
    return {}


def _defaults_from_remediation_provider(provider_key: str) -> dict[str, object]:
    target = str(provider_key or "").strip()
    if not target:
        return {}
    payload = build_real_evidence_remediation_bundle()
    for item in payload.get("items", []):
        row = dict(item or {})
        if str(row.get("providerKey") or "").strip() != target:
            continue
        for candidate_key in (
            "recommendedPrimaryCommand",
            "recommendedBootstrapCommand",
            "recommendedCreateCommand",
            "recommendedRecreateProbeCommand",
        ):
            defaults = _defaults_from_commands(
                [str(row.get(candidate_key) or "")],
                source_prefix="remediation",
                source_key=candidate_key,
            )
            if defaults:
                return defaults
    return {}


def _defaults_from_remediation_orphan_profile(profile_id: str) -> dict[str, object]:
    target = str(profile_id or "").strip()
    if not target:
        return {}
    payload = build_real_evidence_remediation_bundle()
    for item in payload.get("items", []):
        row = dict(item or {})
        orphan_profiles = [str(value or "").strip() for value in (row.get("runtimeOrphanProfiles") or []) if str(value or "").strip()]
        if target not in orphan_profiles:
            continue
        recreate_defaults = _defaults_from_commands(
            [str(value or "") for value in (row.get("recommendedRecreateProbeCommands") or [])],
            source_prefix="remediation_orphan",
            source_key="recommendedRecreateProbeCommands",
            profile_id=target,
        )
        if recreate_defaults:
            return recreate_defaults
        for candidate_key in ("recommendedRecreateProbeCommand", "recommendedPrimaryCommand"):
            defaults = _defaults_from_commands(
                [str(row.get(candidate_key) or "")],
                source_prefix="remediation_orphan",
                source_key=candidate_key,
                profile_id=target,
            )
            if defaults:
                return defaults
    return {}


def _defaults_from_runtime_orphan_provider(provider_key: str) -> dict[str, object]:
    target = str(provider_key or "").strip()
    if not target:
        return {}
    payload = build_runtime_orphan_recovery()
    for item in payload.get("items", []):
        row = dict(item or {})
        if str(row.get("providerKey") or "").strip() != target:
            continue
        defaults = _defaults_from_commands(
            [str(row.get("recommendedCreateCommand") or "")],
            source_prefix="runtime_orphan",
            source_key="recommendedCreateCommand",
        )
        if defaults:
            return defaults
    return {}


def _defaults_from_runtime_orphan_profile(profile_id: str) -> dict[str, object]:
    target = str(profile_id or "").strip()
    if not target:
        return {}
    payload = build_runtime_orphan_recovery()
    for item in payload.get("items", []):
        row = dict(item or {})
        if str(row.get("orphanProfileId") or "").strip() != target:
            continue
        defaults = _defaults_from_commands(
            [str(row.get("recommendedCreateCommand") or "")],
            source_prefix="runtime_orphan_profile",
            source_key="recommendedCreateCommand",
            profile_id=target,
        )
        if defaults:
            return defaults
    return {}


def main() -> None:
    custom_data_dir = str(os.environ.get("CLOUDPAN_SYNC_DATA_DIR") or "").strip()
    if custom_data_dir:
        configure_data_dir(custom_data_dir)
    parser = argparse.ArgumentParser(description="Create a local auth profile stub for CloudPan Sync.")
    parser.add_argument("--provider-key", default="", help="Provider key, such as guangya or aliyundrive_open.")
    parser.add_argument("--auth-mode", default="", help="Auth mode, such as manual_token or manual_cookie.")
    parser.add_argument("--display-name", default="", help="Display name. Defaults to providerKey-authMode.")
    parser.add_argument("--profile-id", default="", help="Optional explicit profileId. Useful when recreating a historical runtime profile.")
    parser.add_argument("--token", default="", help="Optional token value.")
    parser.add_argument("--cookie", default="", help="Optional cookie value.")
    parser.add_argument("--set", dest="extra", action="append", default=[], help="Extra field in key=value form.")
    parser.add_argument("--from-remediation-provider", default="", help="Autofill defaults from the remediation bundle for this provider.")
    parser.add_argument("--from-remediation-orphan-profile", default="", help="Autofill exact orphan-profile defaults from the remediation bundle.")
    parser.add_argument("--from-runtime-orphan-provider", default="", help="Autofill defaults from runtime orphan recovery for this provider.")
    parser.add_argument("--from-runtime-orphan-profile", default="", help="Autofill exact orphan-profile defaults from runtime orphan recovery.")
    parser.add_argument("--validate", action="store_true", help="Run provider-aware live validation after saving.")
    parser.add_argument("--probe", action="store_true", help="Run validation + live probe evidence refresh after saving.")
    parser.add_argument("--page-size", type=int, default=100, help="Optional live probe page size.")
    parser.add_argument("--dir-name", default="", help="Optional create_dir probe name.")
    parser.add_argument("--evidence-output", default="", help="Optional markdown evidence output file path.")
    args = parser.parse_args()

    defaults: dict[str, object] = {}
    defaults_source = ""
    if args.from_runtime_orphan_profile:
        defaults = _defaults_from_runtime_orphan_profile(str(args.from_runtime_orphan_profile or "").strip())
        defaults_source = str(defaults.get("source") or "")
    elif args.from_remediation_orphan_profile:
        defaults = _defaults_from_remediation_orphan_profile(str(args.from_remediation_orphan_profile or "").strip())
        defaults_source = str(defaults.get("source") or "")
    elif args.from_runtime_orphan_provider:
        defaults = _defaults_from_runtime_orphan_provider(str(args.from_runtime_orphan_provider or "").strip())
        defaults_source = str(defaults.get("source") or "")
    elif args.from_remediation_provider:
        defaults = _defaults_from_remediation_provider(str(args.from_remediation_provider or "").strip())
        defaults_source = str(defaults.get("source") or "")

    provider_key = str(args.provider_key or defaults.get("providerKey") or "").strip()
    auth_mode = str(args.auth_mode or defaults.get("authMode") or "").strip()
    if not provider_key or not auth_mode:
        raise SystemExit("provider_key_and_auth_mode_required")

    default_profile_id = str(defaults.get("profileId") or "").strip()
    default_display_name = str(defaults.get("displayName") or "").strip()
    default_token = str(defaults.get("token") or "").strip()
    default_cookie = str(defaults.get("cookie") or "").strip()
    default_extra = [str(value or "").strip() for value in (defaults.get("extra") or []) if str(value or "").strip()]
    explicit_extra = [str(value or "").strip() for value in list(args.extra or []) if str(value or "").strip()]
    merged_extra = default_extra + explicit_extra

    payload = AuthProfileInput(
        providerKey=provider_key,
        authMode=auth_mode,
        displayName=str(args.display_name).strip() or default_display_name or f"{provider_key}-{auth_mode}",
        token=str(args.token or "").strip() or default_token,
        cookie=str(args.cookie or "").strip() or default_cookie,
        extra=_parse_extra(merged_extra),
    )
    profile_id_override = str(args.profile_id or "").strip() or default_profile_id
    if profile_id_override:
        profile = save_profile(payload, profile_id_override=profile_id_override)
    else:
        profile = save_profile(payload)
    result: dict[str, object] = {
        "profileId": profile.profileId,
        "providerKey": profile.providerKey,
        "authMode": profile.authMode,
        "displayName": profile.displayName,
        "extra": dict(profile.extra or {}),
        "written": True,
        "defaultsSource": defaults_source,
    }
    probe_flag = bool(args.probe or defaults.get("probe"))
    validate_flag = bool(args.validate or defaults.get("validate"))
    if probe_flag:
        evidence = refresh_auth_profile_evidence(
            profile=profile,
            page_size=max(1, int(args.page_size or 100)),
            dir_name=str(args.dir_name or "").strip(),
            persist=True,
            profile_view_builder=_auth_profile_evidence.__globals__["_auth_profile_view"],
        )
        result["evidence"] = evidence
        if args.evidence_output:
            output_path = Path(args.evidence_output)
            output_path.write_text(auth_profile_evidence_to_markdown(evidence), encoding="utf-8")
            result["evidenceOutput"] = str(output_path.resolve())
    elif validate_flag:
        result["validation"] = run_profile_live_validation(profile.profileId)
    result["remediation"] = _remediation_followup(profile.profileId)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
