from __future__ import annotations

import json
import re
from urllib.parse import parse_qs, urlparse

from .auth_profile_view import auth_profile_view
from .auth_store import build_profile
from .models import AuthProfileInput
from .provider_auth_hints import provider_auth_modes
from .tianyi_auth_capture import extract_189cloud_account_auth


def _text(value: object) -> str:
    return str(value or "").strip()


def _try_json(raw_text: str) -> object:
    text = _text(raw_text)
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {}


def _flatten_pairs(payload: object, prefix: str = "") -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            pairs.extend(_flatten_pairs(value, next_prefix))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            next_prefix = f"{prefix}[{index}]"
            pairs.extend(_flatten_pairs(value, next_prefix))
    else:
        text = _text(payload)
        if text:
            pairs.append((prefix, text))
    return pairs


def _find_value(pairs: list[tuple[str, str]], candidate_keys: list[str]) -> str:
    lowered = [str(key or "").lower() for key in candidate_keys if str(key or "")]
    for key, value in pairs:
        key_lower = str(key or "").lower()
        for candidate in lowered:
            if key_lower.endswith(candidate.lower()):
                return value
    return ""


def _extract_urls(raw_text: str, pairs: list[tuple[str, str]]) -> list[str]:
    urls: list[str] = []
    for value in re.findall(r"https?://[^\s\"'<>]+", raw_text or "", flags=re.I):
        text = _text(value)
        if text:
            urls.append(text)
    for _, value in pairs:
        if value.startswith("http://") or value.startswith("https://"):
            urls.append(value)
    deduped: list[str] = []
    for item in urls:
        if item not in deduped:
            deduped.append(item)
    return deduped


def _extract_query_values(urls: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for url in urls:
        parsed = urlparse(url)
        query_map = parse_qs(parsed.query or "", keep_blank_values=False)
        for key, values in query_map.items():
            text = _text(values[0] if values else "")
            if text and key not in result:
                result[key] = text
    return result


def _extract_cookie(raw_text: str, pairs: list[tuple[str, str]]) -> str:
    direct = _find_value(pairs, ["cookie", "document.cookie", "cookies"])
    if direct:
        return direct
    text = _text(raw_text)
    header_match = re.search(r"(?im)^\s*cookie\s*:\s*(.+?)\s*$", text)
    if header_match:
        return _text(header_match.group(1)).strip("\"'")
    if "=" in text and ";" in text and "\n" not in text and "\r" not in text:
        return text
    return ""


def _clean_token(value: str) -> str:
    text = _text(value)
    if text.lower().startswith("bearer "):
        return text[7:].strip()
    return text


def _extract_token(pairs: list[tuple[str, str]]) -> str:
    return _clean_token(
        _find_value(
            pairs,
            [
                "token",
                "accessToken",
                "access_token",
                "authorization",
                "Authorization",
                "refreshToken",
            ],
        )
    )


def _extract_token_from_text(raw_text: str) -> str:
    text = _text(raw_text)
    if not text:
        return ""
    patterns = [
        r"(?im)^\s*authorization\s*:\s*(.+?)\s*$",
        r"(?im)^\s*access[_-]?token\s*:\s*(.+?)\s*$",
        r"""(?is)(?:^|\s)-H\s+['"]Authorization:\s*(.+?)['"]""",
        r"""(?is)(?:^|\s)-H\s+['"]access[_-]?token:\s*(.+?)['"]""",
        r"""(?is)["']access[_-]?token["']\s*[:=]\s*["']([^"']+)["']""",
        r"""(?is)["']token["']\s*[:=]\s*["']([^"']+)["']""",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return _clean_token(_text(match.group(1)).strip("\"'"))
    return ""


def _preferred_auth_mode(provider_key: str, token: str, cookie: str) -> str:
    modes = [str(mode or "") for mode in provider_auth_modes(provider_key) if str(mode or "")]
    if cookie and "manual_cookie" in modes:
        return "manual_cookie"
    if token and "manual_token" in modes:
        return "manual_token"
    if token and "official_oauth" in modes:
        return "official_oauth"
    if cookie and "web_login_capture" in modes:
        return "web_login_capture"
    if modes:
        return modes[0]
    return "manual_token"


def _provider_extra_from_capture(provider_key: str, raw_text: str, pairs: list[tuple[str, str]], query_values: dict[str, str]) -> dict[str, str]:
    extra: dict[str, str] = {}

    def take(*keys: str) -> str:
        for key in keys:
            if key in query_values and _text(query_values[key]):
                return _text(query_values[key])
        return _find_value(pairs, list(keys))

    if provider_key == "guangya":
        if take("parentId", "parent_id", "parentFileId", "pid"):
            extra["parentId"] = take("parentId", "parent_id", "parentFileId", "pid")
        if take("did"):
            extra["did"] = take("did")
        if take("dt"):
            extra["dt"] = take("dt")
    elif provider_key == "aliyundrive_open":
        if take("domainId"):
            extra["domainId"] = take("domainId")
        if take("driveId"):
            extra["driveId"] = take("driveId")
    elif provider_key == "189cloud":
        if take("shareCode", "sharecode"):
            extra["shareCode"] = take("shareCode", "sharecode")
        if take("accessCode", "accesscode"):
            extra["accessCode"] = take("accessCode", "accesscode")
        extracted = extract_189cloud_account_auth(raw_text)
        for key, value in extracted.items():
            if _text(value):
                extra[key] = _text(value)
    elif provider_key == "baidu_netdisk":
        if take("fileId", "fsid"):
            extra["fileId"] = take("fileId", "fsid")
        if take("path"):
            extra["path"] = take("path")
    elif provider_key == "123_open":
        if take("parentFileId", "parent_id"):
            extra["parentFileId"] = take("parentFileId", "parent_id")
    elif provider_key == "115_open":
        if take("parentId", "cid"):
            extra["parentId"] = take("parentId", "cid")
    elif provider_key in {"xunlei", "pikpak"}:
        if take("deviceId", "x-device-id"):
            extra["deviceId"] = take("deviceId", "x-device-id")
    elif provider_key in {"quark", "uc"}:
        if take("pwdId", "sharePwdId", "pwd_id", "share_id"):
            extra["pwdId"] = take("pwdId", "sharePwdId", "pwd_id", "share_id")
        if take("passcode", "accessCode", "code"):
            extra["passcode"] = take("passcode", "accessCode", "code")
    return extra


def parse_auth_capture(provider_key: str, raw_text: str) -> dict[str, object]:
    provider = _text(provider_key)
    raw = _text(raw_text)
    payload = _try_json(raw)
    pairs = _flatten_pairs(payload)
    urls = _extract_urls(raw, pairs)
    query_values = _extract_query_values(urls)
    cookie = _extract_cookie(raw, pairs)
    token = _extract_token(pairs)
    if not token:
        token = _extract_token_from_text(raw)
    extra = _provider_extra_from_capture(provider, raw, pairs, query_values)
    auth_mode = _preferred_auth_mode(provider, token, cookie)
    suggested = AuthProfileInput(
        providerKey=provider,
        authMode=auth_mode,
        displayName=f"{provider}-{auth_mode}",
        token=token,
        cookie=cookie,
        extra=extra,
    )
    view = auth_profile_view(build_profile(suggested, profile_id_override="capture-preview"))
    applied_fields: list[str] = []
    if token:
        applied_fields.append("token")
    if cookie:
        applied_fields.append("cookie")
    applied_fields.extend([f"extra.{key}" for key, value in extra.items() if _text(value)])
    return {
        "providerKey": provider,
        "status": "capture_parsed",
        "rawDetectedUrls": urls,
        "suggestedProfile": {
            "providerKey": suggested.providerKey,
            "authMode": suggested.authMode,
            "displayName": suggested.displayName,
            "token": suggested.token,
            "cookie": suggested.cookie,
            "extra": suggested.extra,
        },
        "appliedFieldNames": applied_fields,
        "stillMissingFieldHints": list(view.get("missingFieldHints") or []),
        "placeholderFieldHints": list(view.get("placeholderFieldHints") or []),
        "profileReady": bool(view.get("profileReady")),
        "writeReady": bool(view.get("writeReady", True)),
        "message": "Parsed the pasted browser capture text and prepared a suggested auth payload. Review the fields, then apply them to the auth form.",
    }
