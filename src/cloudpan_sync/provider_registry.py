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
            conflictPolicies=["overwrite_existing", "auto_rename_new"],
            supportsOverwrite=False,
            supportsAutoRename=True,
            overwriteBehavior="downgrade_to_auto_rename",
            conflictNotes="当前 Guangya fallback 上传链路已接受 overwrite_existing / auto_rename_new，但 overwrite_existing 仍会诚实降级为 auto_rename_new。",
            status="researching",
        ),
        ProviderProfile(
            providerKey="aliyundrive_open",
            displayName="Aliyun Drive Open",
            authModes=["official_oauth"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            conflictPolicies=["overwrite_existing", "auto_rename_new"],
            supportsOverwrite=True,
            supportsAutoRename=True,
            overwriteBehavior="provider_managed",
            conflictNotes="当前 Aliyun Drive Open 已接入任务运行阶段真实小文件上传；同名文件可按 overwrite_existing / auto_rename_new 显式选择。",
            status="researching",
        ),
        ProviderProfile(
            providerKey="115_open",
            displayName="115 Open",
            authModes=["official_oauth", "manual_cookie"],
            fastUploadInputs=["sha1", "size"],
            fallbackModes=["download_upload"],
            conflictNotes="当前 115 Open 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。",
            status="researching",
        ),
        ProviderProfile(
            providerKey="quark",
            displayName="Quark",
            authModes=["web_login_capture", "manual_cookie"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            conflictPolicies=["overwrite_existing", "auto_rename_new"],
            supportsOverwrite=False,
            supportsAutoRename=True,
            overwriteBehavior="downgrade_to_auto_rename",
            conflictNotes="当前 Quark 已接入任务运行阶段真实本地文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。",
            status="researching",
        ),
        ProviderProfile(
            providerKey="189cloud",
            displayName="Tianyi 189Cloud",
            authModes=["web_login_capture", "manual_cookie"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            overwriteBehavior="readonly_auth_blocked",
            conflictNotes="当前 189Cloud 已接入账号级 create_dir 写目录尝试，但 shareCode/accessCode-only 档案仍然只读，真实文件上传与同名冲突处理仍未声明为已支持。",
            status="researching",
        ),
        ProviderProfile(
            providerKey="baidu_netdisk",
            displayName="Baidu Netdisk",
            authModes=["official_oauth", "manual_cookie"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            conflictPolicies=["overwrite_existing", "auto_rename_new"],
            supportsOverwrite=False,
            supportsAutoRename=True,
            overwriteBehavior="downgrade_to_auto_rename",
            conflictNotes="当前 Baidu Netdisk 已接入任务运行阶段真实小文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。",
            status="researching",
        ),
        ProviderProfile(
            providerKey="uc",
            displayName="UC Drive",
            authModes=["web_login_capture", "manual_cookie"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            conflictNotes="当前 UC Drive 已接入任务运行阶段的 create_dir 写探针，但真实文件上传场景下的同名文件冲突处理仍未声明为已支持。",
            status="researching",
        ),
        ProviderProfile(
            providerKey="xunlei",
            displayName="Xunlei Drive",
            authModes=["web_login_capture", "manual_token"],
            fastUploadInputs=["gcid", "size"],
            fallbackModes=["download_upload"],
            conflictPolicies=["overwrite_existing", "auto_rename_new"],
            supportsOverwrite=False,
            supportsAutoRename=True,
            overwriteBehavior="downgrade_to_auto_rename",
            conflictNotes="当前 Xunlei 已接入任务运行阶段真实本地文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。",
            status="researching",
        ),
        ProviderProfile(
            providerKey="pikpak",
            displayName="PikPak",
            authModes=["manual_token"],
            fastUploadInputs=["gcid", "size"],
            fallbackModes=["download_upload"],
            conflictPolicies=["overwrite_existing", "auto_rename_new"],
            supportsOverwrite=False,
            supportsAutoRename=True,
            overwriteBehavior="downgrade_to_auto_rename",
            conflictNotes="当前 PikPak 已接入任务运行阶段真实本地文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。",
            status="researching",
        ),
        ProviderProfile(
            providerKey="123_open",
            displayName="123Pan Open",
            authModes=["official_oauth", "manual_token"],
            fastUploadInputs=["md5", "size"],
            fallbackModes=["download_upload"],
            conflictPolicies=["overwrite_existing", "auto_rename_new"],
            supportsOverwrite=False,
            supportsAutoRename=True,
            overwriteBehavior="downgrade_to_auto_rename",
            conflictNotes="当前 123Pan Open 已接入任务运行阶段真实小文件上传；`auto_rename_new` 可直接支持，`overwrite_existing` 会诚实降级为自动改名。",
            status="researching",
        ),
    ]
    return [ProviderAdapter(profile=item) for item in providers]


def get_provider_profile(provider_key: str) -> ProviderProfile | None:
    for adapter in build_provider_registry():
        if adapter.profile.providerKey == provider_key:
            return adapter.profile
    return None
