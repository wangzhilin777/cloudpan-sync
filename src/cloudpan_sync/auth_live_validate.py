from __future__ import annotations

import json
from datetime import datetime, timezone

from .auth_store import DATA_DIR, get_profile, list_profiles
from .provider_live_probe import run_provider_live_probe, run_provider_live_probe_for_profile


VALIDATION_FILE = DATA_DIR / "auth_live_validations.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_rows() -> list[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not VALIDATION_FILE.exists():
        return []
    text = VALIDATION_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        rows = json.loads(text)
    except json.JSONDecodeError:
        return []
    return rows if isinstance(rows, list) else []


def _write_rows(rows: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def list_live_validations() -> list[dict[str, object]]:
    return _read_rows()


def latest_live_validations() -> list[dict[str, object]]:
    latest_by_profile: dict[str, dict[str, object]] = {}
    for row in _read_rows():
        profile_id = str(row.get("profileId") or "")
        if not profile_id:
            continue
        latest_by_profile[profile_id] = row
    return list(latest_by_profile.values())


def latest_live_validation_for_profile(profile_id: str) -> dict[str, object] | None:
    target = str(profile_id or "")
    if not target:
        return None
    latest: dict[str, object] | None = None
    for row in _read_rows():
        if str(row.get("profileId") or "") == target:
            latest = row
    return latest


def live_validation_summary() -> dict[str, object]:
    rows = latest_live_validations()
    ok_profiles = sorted(
        {
            str(row.get("providerDisplayName") or row.get("profileId") or "")
            for row in rows
            if bool(row.get("ok")) and str(row.get("providerDisplayName") or row.get("profileId") or "")
        }
    )
    failed_profiles = sorted(
        {
            str(row.get("providerDisplayName") or row.get("profileId") or "")
            for row in rows
            if not bool(row.get("ok")) and str(row.get("providerDisplayName") or row.get("profileId") or "")
        }
    )
    return {
        "profileCount": len(rows),
        "okCount": sum(1 for row in rows if bool(row.get("ok"))),
        "failedCount": sum(1 for row in rows if not bool(row.get("ok"))),
        "okProfiles": ok_profiles,
        "failedProfiles": failed_profiles,
        "providerKeys": sorted({str(row.get("providerKey") or "") for row in rows if str(row.get("providerKey") or "")}),
    }


def append_live_validation(row: dict[str, object]) -> dict[str, object]:
    rows = _read_rows()
    rows.append(row)
    _write_rows(rows)
    return row


def _profile_probe_defaults(profile: object) -> tuple[str, str]:
    extra = getattr(profile, "extra", {}) or {}
    provider_key = str(getattr(profile, "providerKey", "") or "")

    if provider_key == "guangya":
        return (
            str(
                extra.get("parentId")
                or extra.get("parent_id")
                or extra.get("parentFileId")
                or extra.get("parent_file_id")
                or extra.get("dirId")
                or extra.get("dir_id")
                or extra.get("pid")
                or ""
            ),
            str(extra.get("fileId") or extra.get("file_id") or extra.get("resId") or extra.get("res_id") or ""),
        )
    if provider_key == "aliyundrive_open":
        return str(extra.get("parentFileId") or "root"), str(extra.get("fileId") or "")
    if provider_key == "189cloud":
        return "", str(extra.get("fileId") or "")
    if provider_key == "baidu_netdisk":
        return str(extra.get("path") or "/"), str(extra.get("fileId") or "")
    if provider_key == "123_open":
        return str(extra.get("parentFileId") or "0"), str(extra.get("fileId") or "")
    if provider_key == "115_open":
        return str(extra.get("parentId") or extra.get("cid") or "0"), str(extra.get("fileId") or "")
    if provider_key == "xunlei":
        return str(extra.get("parentId") or ""), str(extra.get("fileId") or "")
    if provider_key == "pikpak":
        return str(extra.get("parentId") or ""), str(extra.get("fileId") or "")
    if provider_key == "quark":
        return str(extra.get("parentId") or "0"), str(extra.get("fileId") or "")
    if provider_key == "uc":
        return str(extra.get("parentId") or "0"), str(extra.get("fileId") or "")
    return "", ""


def _required_field_hints(provider_key: str, error: str) -> list[str]:
    mapping = {
        ("guangya", "missing_parent_id"): ["extra.parentId", "aliases: parent_id/parentFileId/dirId/pid", "optional extra.did", "optional extra.dt"],
        ("guangya", "missing_file_id"): ["extra.fileId", "aliases: file_id/resId", "extra.parentId for list/create_dir probes"],
        ("guangya", "missing_authorization"): ["token", "or extra.authorization", "aliases: extra.Authorization/extra.accessToken"],
        ("aliyundrive_open", "missing_domain_id"): ["extra.domainId", "extra.driveId"],
        ("quark", "missing_pwd_id"): ["extra.pwdId", "or extra.sharePwdId", "optional extra.passcode"],
        ("uc", "missing_pwd_id"): ["extra.pwdId", "or extra.sharePwdId", "optional extra.passcode"],
    }
    return mapping.get((provider_key, error), [])


def _summarize_check_status(checks: list[dict[str, object]]) -> int:
    best = 0
    for check in checks:
        try:
            status = int(check.get("status", 0) or 0)
        except Exception:
            status = 0
        best = max(best, status)
    return best


def validate_profile_object(profile: object) -> dict[str, object]:
    parent_id, file_id = _profile_probe_defaults(profile)
    probe = run_provider_live_probe_for_profile(
        profile=profile,
        parent_id=parent_id,
        file_id=file_id,
        page_size=100,
        dir_name="",
    )
    checks = [dict(item or {}) for item in probe.get("checks", [])]
    first_error = next((str(check.get("error") or "") for check in checks if str(check.get("error") or "")), "")
    first_risk_hint = next((str(check.get("note") or "") for check in checks if str(check.get("error") or "")), "")
    return {
        "ok": bool(probe.get("ok")),
        "profileId": profile.profileId,
        "providerKey": profile.providerKey,
        "providerDisplayName": profile.displayName,
        "mode": str(probe.get("mode") or ""),
        "status": _summarize_check_status(checks),
        "error": first_error,
        "summary": str(probe.get("summary") or ""),
        "checkedAt": _now_iso(),
        "checks": checks,
        "parentId": parent_id,
        "fileId": file_id,
        "riskHint": first_risk_hint,
        "requiredFieldHints": _required_field_hints(str(profile.providerKey or ""), first_error),
    }


def run_profile_live_validation(profile_id: str) -> dict[str, object]:
    profile = get_profile(profile_id)
    if profile is None:
        row = {
            "ok": False,
            "profileId": profile_id,
            "providerKey": "",
            "providerDisplayName": "",
            "mode": "profile_missing",
            "status": 0,
            "error": "profile_not_found",
            "summary": "Auth profile not found.",
            "checkedAt": _now_iso(),
            "checks": [],
        }
        append_live_validation(row)
        return row

    row = validate_profile_object(profile)
    append_live_validation(row)
    return row


def run_all_profile_live_validations() -> dict[str, object]:
    profiles = list_profiles()
    results: list[dict[str, object]] = []
    ok_count = 0
    for profile in profiles:
        row = run_profile_live_validation(profile.profileId)
        results.append(row)
        if bool(row.get("ok")):
            ok_count += 1
    return {
        "totalProfiles": len(profiles),
        "okProfiles": ok_count,
        "failedProfiles": max(0, len(profiles) - ok_count),
        "results": results,
    }
