from __future__ import annotations

from .provider_auth_hints import capture_field_hints, capture_login_url, official_docs_url, provider_auth_modes


def _preferred_capture_mode(provider_key: str, auth_modes: list[str]) -> str:
    available = [str(mode or "") for mode in auth_modes if str(mode or "")]
    provider_first = {
        "guangya": ("manual_token", "web_login_capture"),
        "aliyundrive_open": ("official_oauth",),
        "189cloud": ("manual_cookie", "web_login_capture"),
        "baidu_netdisk": ("manual_cookie", "official_oauth"),
        "123_open": ("manual_token", "official_oauth"),
        "115_open": ("manual_cookie",),
        "xunlei": ("manual_token", "web_login_capture"),
        "pikpak": ("manual_token",),
        "quark": ("manual_cookie", "web_login_capture"),
        "uc": ("manual_cookie", "web_login_capture"),
    }
    for candidate in provider_first.get(provider_key, ()):
        if candidate in available:
            return candidate
    for candidate in ("web_login_capture", "manual_cookie", "manual_token", "official_oauth"):
        if candidate in available:
            return candidate
    return available[0] if available else "web_login_capture"


def _paste_targets(provider_key: str, capture_mode: str) -> list[str]:
    mapping = {
        "guangya": ["authToken <- captured token/header", "authExtraParentId <- parentId"],
        "aliyundrive_open": ["authToken <- access token", "authExtraDomainId <- domainId", "authExtraDriveId <- driveId"],
        "189cloud": ["authCookie <- browser cookie", "authExtraShareCode <- shareCode", "authExtraAccessCode <- accessCode", "authExtraAccessToken/authExtraSignature/authExtraDate <- captured write headers if you need create_dir/upload"],
        "baidu_netdisk": ["authCookie or authToken <- captured credential", "authExtraFileId <- optional fileId for metadata probe"],
        "123_open": ["authToken <- access token", "authExtraParentId <- parentFileId if needed"],
        "115_open": ["authCookie <- browser cookie", "authExtraParentId <- parentId/cid if needed"],
        "xunlei": ["authToken <- access token", "authExtraDevice <- deviceId"],
        "pikpak": ["authToken <- access token", "authExtraDevice <- deviceId if the current token is device-scoped"],
        "quark": ["authCookie <- browser cookie", "authExtraPwdId <- pwdId/sharePwdId", "authExtraPasscode <- optional passcode"],
        "uc": ["authCookie <- browser cookie", "authExtraPwdId <- pwdId/sharePwdId", "authExtraPasscode <- optional passcode"],
    }
    targets = list(mapping.get(provider_key, []))
    if not targets:
        if capture_mode == "manual_cookie":
            targets.append("authCookie <- browser cookie")
        else:
            targets.append("authToken <- captured token")
    return targets


def _manual_steps(provider_key: str, capture_mode: str, login_url: str) -> list[str]:
    steps = [
        f"打开登录页并完成账号登录：{login_url or 'provider login page'}",
        "登录完成后不要立刻关闭页面，保留当前标签页或分享页上下文。",
    ]
    if capture_mode == "manual_cookie":
        steps.append("先在浏览器控制台执行复制 cookie 的脚本，再把结果粘贴回授权表单。")
    else:
        steps.append("先在浏览器控制台执行 storage dump 脚本；如果没看到 token，再到 DevTools Network 里找 Authorization/access_token。")
    if provider_key in {"quark", "uc", "189cloud"}:
        steps.append("如果 provider 依赖分享页参数，顺手记录当前 URL 里的 shareCode/pwdId/passcode。")
    if provider_key == "aliyundrive_open":
        steps.append("Aliyun Open 除了 token，还需要 domainId/driveId；优先从当前成功请求或已有配置里一起补齐。")
    if provider_key == "guangya":
        steps.append("Guangya 至少还要补 parentId；拿不到时可先保留空值，随后在授权列表 edit/patch。")
    steps.append("回填凭证后立即点击 Save Auth 或 Validate，确认最小 live validation 能通过。")
    return steps


def _browser_console_snippets(provider_key: str, capture_mode: str) -> list[dict[str, str]]:
    snippets = [
        {
            "label": "Copy Current URL",
            "purpose": "记录当前登录/分享页 URL，便于提取 shareCode、pwdId、passcode 等参数。",
            "code": "copy(location.href)",
        }
    ]
    if capture_mode == "manual_cookie":
        snippets.append(
            {
                "label": "Copy Cookie",
                "purpose": "复制当前站点 cookie，适合 Quark/UC/115/189Cloud 等 cookie 驱动场景。",
                "code": "copy(document.cookie)",
            }
        )
    snippets.append(
        {
            "label": "Dump Storage",
            "purpose": "导出 localStorage / sessionStorage，方便查找 access token、refresh token、deviceId 等字段。",
            "code": 'copy(JSON.stringify({ localStorage: { ...localStorage }, sessionStorage: { ...sessionStorage } }, null, 2))',
        }
    )
    if provider_key in {"xunlei", "pikpak"}:
        snippets.append(
            {
                "label": "Dump Device Context",
                "purpose": "快速导出 deviceId 和 storage 快照，便于回填设备相关字段。",
                "code": 'copy(JSON.stringify({ url: location.href, deviceId: localStorage.deviceId || sessionStorage.deviceId || "", localStorage: { ...localStorage }, sessionStorage: { ...sessionStorage } }, null, 2))',
            }
        )
    if provider_key in {"quark", "uc", "189cloud"}:
        snippets.append(
            {
                "label": "Copy Share Hints",
                "purpose": "从当前 URL 快速提取分享页参数，减少手工抄录。",
                "code": 'copy(JSON.stringify({ url: location.href, search: location.search, hash: location.hash }, null, 2))',
            }
        )
    return snippets


def _network_tips(provider_key: str, capture_mode: str) -> list[str]:
    tips = [
        "如果控制台脚本里没有直接出现 token/cookie，请打开 DevTools Network，刷新一次页面后查看最近成功请求的 Request Headers / Response。",
    ]
    if capture_mode != "manual_cookie":
        tips.append("优先关注 Authorization、access_token、token、refresh_token、x-device-id 这类字段。")
    if provider_key == "189cloud":
        tips.append("如果你要验证 create_dir / upload，除了 cookie/shareCode，还要额外记录 AccessToken、Signature、Date。")
    if provider_key == "aliyundrive_open":
        tips.append("Aliyun Open 的 token 常常不够，需要和 domainId、driveId 成对保存。")
    return tips


def build_auth_capture_guide(provider_key: str) -> dict[str, object]:
    provider = str(provider_key or "").strip()
    login_url = capture_login_url(provider) or f"https://{provider}.example.com/login"
    auth_modes = provider_auth_modes(provider)
    preferred_mode = _preferred_capture_mode(provider, auth_modes)
    return {
        "providerKey": provider,
        "status": "capture_pending",
        "loginUrlHint": login_url,
        "officialDocsUrl": official_docs_url(provider),
        "recommendedAuthModes": auth_modes,
        "preferredCaptureMode": preferred_mode,
        "requiredFieldHints": capture_field_hints(provider),
        "pasteTargets": _paste_targets(provider, preferred_mode),
        "manualSteps": _manual_steps(provider, preferred_mode, login_url),
        "browserConsoleSnippets": _browser_console_snippets(provider, preferred_mode),
        "networkCaptureTips": _network_tips(provider, preferred_mode),
        "message": "Open the provider login page, complete login, copy the suggested browser data, then paste token/cookie and the required extra fields back into the auth form.",
    }
