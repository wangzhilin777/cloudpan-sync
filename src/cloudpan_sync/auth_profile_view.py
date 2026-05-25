from __future__ import annotations

from .auth_store import masked_profile


PLACEHOLDER_VALUE_MARKERS = (
    "your_",
    "your-",
    "demo",
    "smoke",
    "example",
    "sample",
    "test",
    "placeholder",
)


def profile_extra_value(extra: dict[str, object], keys: list[str]) -> str:
    for key in keys:
        value = str(extra.get(key) or "").strip()
        if value:
            return value
    return ""


def resolved_probe_defaults(profile: object) -> tuple[str, str]:
    provider_key = str(getattr(profile, "providerKey", "") or "")
    extra = getattr(profile, "extra", {}) or {}

    if provider_key == "guangya":
        return (
            profile_extra_value(extra, ["parentId", "parent_id", "parentFileId", "parent_file_id", "dirId", "dir_id", "pid"]),
            profile_extra_value(extra, ["fileId", "file_id", "resId", "res_id"]),
        )
    if provider_key == "aliyundrive_open":
        return profile_extra_value(extra, ["parentFileId"]) or "root", profile_extra_value(extra, ["fileId"])
    if provider_key == "189cloud":
        return "", profile_extra_value(extra, ["fileId"])
    if provider_key == "baidu_netdisk":
        return profile_extra_value(extra, ["path"]) or "/", profile_extra_value(extra, ["fileId"])
    if provider_key == "123_open":
        return profile_extra_value(extra, ["parentFileId"]) or "0", profile_extra_value(extra, ["fileId"])
    if provider_key == "115_open":
        return profile_extra_value(extra, ["parentId", "cid"]) or "0", profile_extra_value(extra, ["fileId"])
    if provider_key == "xunlei":
        return profile_extra_value(extra, ["parentId"]), profile_extra_value(extra, ["fileId"])
    if provider_key == "pikpak":
        return profile_extra_value(extra, ["parentId"]), profile_extra_value(extra, ["fileId"])
    if provider_key == "quark":
        return profile_extra_value(extra, ["parentId"]) or "0", profile_extra_value(extra, ["fileId"])
    if provider_key == "uc":
        return profile_extra_value(extra, ["parentId"]) or "0", profile_extra_value(extra, ["fileId"])
    return "", ""


def profile_missing_field_hints(profile: object) -> list[str]:
    provider_key = str(getattr(profile, "providerKey", "") or "")
    token = str(getattr(profile, "token", "") or "").strip()
    cookie = str(getattr(profile, "cookie", "") or "").strip()
    extra = getattr(profile, "extra", {}) or {}

    missing: list[str] = []
    if provider_key == "guangya":
        if not (token or profile_extra_value(extra, ["authorization", "Authorization", "accessToken", "access_token"])):
            missing.append("token or extra.authorization")
        if not profile_extra_value(extra, ["parentId", "parent_id", "parentFileId", "parent_file_id", "dirId", "dir_id", "pid"]):
            missing.append("extra.parentId (aliases: parent_id/parentFileId/dirId/pid)")
        return missing
    if provider_key == "aliyundrive_open":
        if not (token or profile_extra_value(extra, ["authorization", "Authorization"])):
            missing.append("token or extra.authorization")
        if not profile_extra_value(extra, ["domainId"]):
            missing.append("extra.domainId")
        if not profile_extra_value(extra, ["driveId"]):
            missing.append("extra.driveId")
        return missing
    if provider_key == "189cloud":
        if not profile_extra_value(extra, ["shareCode"]):
            missing.append("extra.shareCode")
        return missing
    if provider_key == "baidu_netdisk":
        if not (token or cookie or profile_extra_value(extra, ["authorization", "Authorization"])):
            missing.append("token or cookie")
        return missing
    if provider_key == "123_open":
        if not (token or profile_extra_value(extra, ["authorization", "Authorization"])):
            missing.append("token or extra.authorization")
        return missing
    if provider_key == "115_open":
        if not (cookie or profile_extra_value(extra, ["cookie", "cookie_header"])):
            missing.append("cookie or extra.cookie_header")
        return missing
    if provider_key == "xunlei":
        if not (token or profile_extra_value(extra, ["authorization", "Authorization"])):
            missing.append("token or extra.authorization")
        if not profile_extra_value(extra, ["deviceId", "x-device-id"]):
            missing.append("extra.deviceId or extra.x-device-id")
        return missing
    if provider_key == "pikpak":
        if not (token or profile_extra_value(extra, ["authorization", "Authorization"])):
            missing.append("token or extra.authorization")
        return missing
    if provider_key == "quark":
        if not (cookie or profile_extra_value(extra, ["cookie", "cookie_header"])):
            missing.append("cookie or extra.cookie_header")
        if not profile_extra_value(extra, ["pwdId", "sharePwdId", "share_id"]):
            missing.append("extra.pwdId or extra.sharePwdId")
        return missing
    if provider_key == "uc":
        if not (cookie or profile_extra_value(extra, ["cookie", "cookie_header"])):
            missing.append("cookie or extra.cookie_header")
        if not profile_extra_value(extra, ["pwdId", "sharePwdId", "share_id"]):
            missing.append("extra.pwdId or extra.sharePwdId")
        return missing
    return missing


def _looks_placeholder_value(value: object) -> bool:
    text = str(value or "").strip().lower()
    if not text:
        return False
    if text in {"your_value", "your_token", "your_cookie", "your_domain_id", "your_drive_id", "your_real_parent_id"}:
        return True
    return any(marker in text for marker in PLACEHOLDER_VALUE_MARKERS)


def profile_placeholder_field_hints(profile: object) -> list[str]:
    provider_key = str(getattr(profile, "providerKey", "") or "")
    token = str(getattr(profile, "token", "") or "").strip()
    cookie = str(getattr(profile, "cookie", "") or "").strip()
    extra = getattr(profile, "extra", {}) or {}

    hints: list[str] = []
    if provider_key == "guangya" and _looks_placeholder_value(token):
        hints.append("token looks like placeholder data; replace tok-demo/tok_smoke with a real Guangya token")
    if provider_key == "aliyundrive_open":
        if _looks_placeholder_value(token):
            hints.append("token looks like placeholder data; replace tok-demo with a real Aliyun OAuth token")
        if _looks_placeholder_value(extra.get("domainId")):
            hints.append("extra.domainId still uses placeholder data; replace domain-demo with a real domainId")
        if _looks_placeholder_value(extra.get("driveId")):
            hints.append("extra.driveId still uses placeholder data; replace drive-demo with a real driveId")
        return hints
    if provider_key in {"quark", "uc", "115_open"} and _looks_placeholder_value(cookie):
        hints.append("cookie looks like placeholder data; replace it with a real captured cookie")
    if provider_key in {"xunlei", "pikpak", "123_open"} and _looks_placeholder_value(token):
        hints.append("token looks like placeholder data; replace it with a real provider token")
    return hints


def profile_placeholder_secret_field_hints(profile: object) -> list[str]:
    provider_key = str(getattr(profile, "providerKey", "") or "")
    token = str(getattr(profile, "token", "") or "").strip()
    cookie = str(getattr(profile, "cookie", "") or "").strip()
    extra = getattr(profile, "extra", {}) or {}

    hints: list[str] = []
    if provider_key == "guangya" and _looks_placeholder_value(token):
        hints.append("token")
    if provider_key == "aliyundrive_open" and _looks_placeholder_value(token):
        hints.append("token")
    if provider_key in {"quark", "uc", "115_open"} and _looks_placeholder_value(cookie):
        hints.append("cookie")
    if provider_key in {"xunlei", "pikpak", "123_open"} and _looks_placeholder_value(token):
        hints.append("token")
    if provider_key == "189cloud" and _looks_placeholder_value(extra.get("accessToken")):
        hints.append("extra.accessToken")
    return hints


def profile_write_readiness(profile: object) -> tuple[bool, list[str], str]:
    provider_key = str(getattr(profile, "providerKey", "") or "")
    token = str(getattr(profile, "token", "") or "").strip()
    extra = getattr(profile, "extra", {}) or {}

    if provider_key == "189cloud":
        has_share_read_auth = bool(profile_extra_value(extra, ["shareCode"]))
        has_account_write_auth = bool(
            token
            or profile_extra_value(extra, ["authorization", "Authorization", "accessToken", "access_token"])
        ) and bool(profile_extra_value(extra, ["signature", "Signature"])) and bool(profile_extra_value(extra, ["date", "Date"]))
        if has_account_write_auth:
            return True, [], ""
        if has_share_read_auth:
            return (
                False,
                ["account-level OAuth write auth: token/accessToken + extra.signature + extra.date"],
                "当前 189Cloud 档案仅具备 shareCode/accessCode 只读能力；createFolder.action 仍需账号级 OAuth 写鉴权。",
            )
        return (
            False,
            ["account-level OAuth write auth: token/accessToken + extra.signature + extra.date"],
            "189Cloud 写目录仍需账号级 OAuth 写鉴权。",
        )
    return True, [], ""


def auth_profile_view(profile: object) -> dict[str, object]:
    data = masked_profile(profile)
    missing = profile_missing_field_hints(profile)
    placeholder_missing = profile_placeholder_field_hints(profile)
    placeholder_secret_missing = profile_placeholder_secret_field_hints(profile)
    resolved_parent_id, resolved_file_id = resolved_probe_defaults(profile)
    write_ready, write_missing, write_blocker_note = profile_write_readiness(profile)
    data["missingFieldHints"] = missing + placeholder_missing
    data["placeholderFieldHints"] = placeholder_missing
    data["placeholderSecretFieldHints"] = placeholder_secret_missing
    data["needsSecretRefresh"] = bool(placeholder_secret_missing)
    data["profileHasPlaceholderValues"] = bool(placeholder_missing)
    data["profileReady"] = not (missing or placeholder_missing)
    data["resolvedParentId"] = resolved_parent_id
    data["resolvedFileId"] = resolved_file_id
    data["writeReady"] = write_ready
    data["writeMissingFieldHints"] = write_missing
    data["writeBlockerNote"] = write_blocker_note
    return data
