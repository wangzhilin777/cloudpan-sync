from __future__ import annotations

from .provider_research import build_provider_research_index


def _research_row(provider_key: str) -> dict[str, object]:
    for item in build_provider_research_index():
        if str(item.get("providerKey") or "") == str(provider_key or ""):
            return dict(item)
    return {}


def capture_login_url(provider_key: str) -> str:
    row = _research_row(provider_key)
    return str(row.get("webLoginUrl") or "").strip()


def official_docs_url(provider_key: str) -> str:
    row = _research_row(provider_key)
    return str(row.get("officialDocsUrl") or "").strip()


def provider_auth_modes(provider_key: str) -> list[str]:
    row = _research_row(provider_key)
    return [str(mode or "") for mode in list(row.get("authModes") or []) if str(mode or "")]


def capture_field_hints(provider_key: str) -> list[str]:
    mapping = {
        "guangya": ["token or extra.authorization", "extra.parentId", "optional extra.did", "optional extra.dt"],
        "aliyundrive_open": ["token or extra.authorization", "extra.domainId", "extra.driveId"],
        "189cloud": [
            "share-read probe: extra.shareCode",
            "optional extra.accessCode",
            "account write auth: token or extra.accessToken",
            "account write auth: extra.signature",
            "account write auth: extra.date",
            "optional helper: patch_189cloud_account_auth.py from captured headers/curl",
            "optional extra.fileId",
        ],
        "baidu_netdisk": ["token or extra.authorization, or cookie", "optional extra.fileId", "optional extra.path"],
        "123_open": ["token or extra.authorization", "optional extra.parentFileId", "optional extra.fileId"],
        "115_open": ["cookie or extra.cookie_header", "optional extra.parentId or extra.cid", "optional extra.fileId"],
        "xunlei": ["token or extra.authorization", "extra.deviceId or extra.x-device-id", "optional extra.fileId"],
        "pikpak": ["token or extra.authorization", "optional extra.deviceId", "optional extra.fileId"],
        "quark": ["cookie or extra.cookie_header", "extra.pwdId or extra.sharePwdId", "optional extra.passcode", "optional extra.fileId"],
        "uc": ["cookie or extra.cookie_header", "extra.pwdId or extra.sharePwdId", "optional extra.passcode", "optional extra.fileId"],
    }
    return mapping.get(str(provider_key or ""), [])
