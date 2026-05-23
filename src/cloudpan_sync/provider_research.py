from __future__ import annotations

from datetime import date


def build_provider_research_index() -> list[dict[str, object]]:
    today = date.today().isoformat()
    return [
        {
            "providerKey": "guangya",
            "displayName": "Guangya",
            "officialDocsUrl": "",
            "openSourceRefs": [
                "C:/Users/ChowYu/Desktop/新建文件夹 (3)/秒传.js",
            ],
            "webLoginUrl": "https://guangyapan.com/",
            "authModes": ["web_login_capture", "manual_token"],
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "M4 local precheck done; live API binding pending.",
        },
        {
            "providerKey": "aliyundrive_open",
            "displayName": "Aliyun Drive Open",
            "officialDocsUrl": "https://www.alipan.com/",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
                "https://github.com/AlistGo/alist",
            ],
            "webLoginUrl": "",
            "authModes": ["official_oauth"],
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "M5 mock list/metadata online; live OAuth wiring pending.",
        },
        {
            "providerKey": "115_open",
            "displayName": "115 Open",
            "officialDocsUrl": "",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
                "https://github.com/AlistGo/alist",
            ],
            "webLoginUrl": "",
            "authModes": ["official_oauth", "manual_cookie"],
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "M5 mock list/metadata online; live auth/session binding pending.",
        },
        {
            "providerKey": "quark",
            "displayName": "Quark",
            "officialDocsUrl": "",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
            ],
            "webLoginUrl": "https://pan.quark.cn/",
            "authModes": ["web_login_capture", "manual_cookie"],
            "status": "planned",
            "lastVerifiedAt": today,
            "notes": "M5 mock list/metadata online; real API evidence needs refresh.",
        },
        {
            "providerKey": "189cloud",
            "displayName": "Tianyi 189Cloud",
            "officialDocsUrl": "",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
            ],
            "webLoginUrl": "https://cloud.189.cn/",
            "authModes": ["web_login_capture", "manual_cookie"],
            "status": "planned",
            "lastVerifiedAt": today,
            "notes": "Provider scaffold online; live list/metadata binding pending.",
        },
        {
            "providerKey": "baidu_netdisk",
            "displayName": "Baidu Netdisk",
            "officialDocsUrl": "https://pan.baidu.com/",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
                "https://github.com/AlistGo/alist",
            ],
            "webLoginUrl": "https://pan.baidu.com/",
            "authModes": ["official_oauth", "manual_cookie"],
            "status": "planned",
            "lastVerifiedAt": today,
            "notes": "High risk-control provider; keep fallback conservative.",
        },
        {
            "providerKey": "uc",
            "displayName": "UC Drive",
            "officialDocsUrl": "",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
            ],
            "webLoginUrl": "https://drive.uc.cn/",
            "authModes": ["web_login_capture", "manual_cookie"],
            "status": "planned",
            "lastVerifiedAt": today,
            "notes": "Provider scaffold online; API evidence refresh pending.",
        },
        {
            "providerKey": "xunlei",
            "displayName": "Xunlei Drive",
            "officialDocsUrl": "",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
                "https://github.com/AlistGo/alist",
            ],
            "webLoginUrl": "https://pan.xunlei.com/",
            "authModes": ["web_login_capture", "manual_cookie"],
            "status": "planned",
            "lastVerifiedAt": today,
            "notes": "Prioritize GCID-focused fast-check path.",
        },
        {
            "providerKey": "pikpak",
            "displayName": "PikPak",
            "officialDocsUrl": "https://mypikpak.com/",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
            ],
            "webLoginUrl": "https://mypikpak.com/",
            "authModes": ["manual_token", "manual_cookie"],
            "status": "planned",
            "lastVerifiedAt": today,
            "notes": "Provider scaffold online; real auth flow pending.",
        },
        {
            "providerKey": "123_open",
            "displayName": "123Pan Open",
            "officialDocsUrl": "https://www.123pan.com/",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
                "https://github.com/AlistGo/alist",
            ],
            "webLoginUrl": "https://www.123pan.com/",
            "authModes": ["official_oauth", "manual_token"],
            "status": "planned",
            "lastVerifiedAt": today,
            "notes": "Provider scaffold online; OAuth/token live binding pending.",
        },
    ]
