from __future__ import annotations

from .models import ProviderProfile
from .provider import ProviderAdapter


def build_provider_registry() -> list[ProviderAdapter]:
    providers = [
        ProviderProfile(
            providerKey="guangya",
            displayName="Guangya",
            authModes=["web_login_capture", "manual_token"],
            fastUploadInputs=["md5", "size", "name"],
            fallbackModes=["download_upload"],
            status="researching",
        ),
        ProviderProfile(
            providerKey="aliyundrive_open",
            displayName="Aliyun Drive Open",
            authModes=["official_oauth"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            status="researching",
        ),
        ProviderProfile(
            providerKey="115_open",
            displayName="115 Open",
            authModes=["official_oauth", "manual_cookie"],
            fastUploadInputs=["sha1", "size"],
            fallbackModes=["download_upload"],
            status="researching",
        ),
        ProviderProfile(
            providerKey="quark",
            displayName="Quark",
            authModes=["web_login_capture", "manual_cookie"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            status="planned",
        ),
        ProviderProfile(
            providerKey="189cloud",
            displayName="Tianyi 189Cloud",
            authModes=["web_login_capture", "manual_cookie"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            status="planned",
        ),
        ProviderProfile(
            providerKey="baidu_netdisk",
            displayName="Baidu Netdisk",
            authModes=["official_oauth", "manual_cookie"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            status="planned",
        ),
        ProviderProfile(
            providerKey="uc",
            displayName="UC Drive",
            authModes=["web_login_capture", "manual_cookie"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            status="planned",
        ),
        ProviderProfile(
            providerKey="xunlei",
            displayName="Xunlei Drive",
            authModes=["web_login_capture", "manual_cookie"],
            fastUploadInputs=["gcid", "size"],
            fallbackModes=["download_upload"],
            status="planned",
        ),
        ProviderProfile(
            providerKey="pikpak",
            displayName="PikPak",
            authModes=["manual_token", "manual_cookie"],
            fastUploadInputs=["gcid", "size"],
            fallbackModes=["download_upload"],
            status="planned",
        ),
        ProviderProfile(
            providerKey="123_open",
            displayName="123Pan Open",
            authModes=["official_oauth", "manual_token"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            status="planned",
        ),
    ]
    return [ProviderAdapter(profile=item) for item in providers]


def get_provider_profile(provider_key: str) -> ProviderProfile | None:
    for adapter in build_provider_registry():
        if adapter.profile.providerKey == provider_key:
            return adapter.profile
    return None
