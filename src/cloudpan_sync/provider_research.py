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
    ]
