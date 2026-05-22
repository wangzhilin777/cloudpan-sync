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
    ]
    return [ProviderAdapter(profile=item) for item in providers]


def get_provider_profile(provider_key: str) -> ProviderProfile | None:
    for adapter in build_provider_registry():
        if adapter.profile.providerKey == provider_key:
            return adapter.profile
    return None
