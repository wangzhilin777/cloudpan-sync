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
            "notes": "M4 precheck done; get_file_list, get_res_download_url, create_dir, live fast-upload inventory check, and localPath-driven fallback live attempt in task runtime are available with saved auth profile, but real binary upload and stable online validation still need work.",
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
            "notes": "M5 mock list/metadata online; saved access token plus domainId/driveId can now drive live list/get/create_dir attempts, but real online samples are still pending.",
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
            "notes": "cookie driven live list/metadata(create via webapi.115.com files/get_info/files/add) attempts are online, and task runtime can now also attempt live rapid upload through proapi.115.com/open/upload/init plus sign_check follow-up when a usable local file plus sha1 is available; stable real success samples, full binary upload fallback, and long-term official open-platform token refresh handling are still pending.",
        },
        {
            "providerKey": "quark",
            "displayName": "Quark",
            "officialDocsUrl": "",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
                "C:/Users/ChowYu/Desktop/新建文件夹 (3)/秒传.js",
            ],
            "webLoginUrl": "https://pan.quark.cn/",
            "authModes": ["web_login_capture", "manual_cookie"],
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "share-based live list/metadata(MD5 via file/download) attempts are online from pc-api.uc.cn evidence, cookie-based create_dir attempts are now wired on the Quark PC drive API path, and task runtime can now also attempt rapid upload through upload/pre + update/hash + upload/finish when a usable local file plus md5/sha1 context is available; stable real online samples and ordinary upload chain are still pending.",
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
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "shareCode/accessCode based live list/metadata attempts are online, and createFolder.action is now wired for account-level OAuth headers such as AccessToken/Signature/Date; share-only profiles still remain read-only, and stable real success samples are still pending.",
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
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "access token or cookie can now drive conservative live list/metadata/create_dir attempts on the xpan file API; this provider remains high risk-control and still lacks stable real samples plus fast-transfer evidence.",
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
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "share-based live list/metadata(MD5 via file/download) attempts are online on the pc-api.uc.cn chain with saved cookie + pwdId, same-stack cookie-based create_dir attempts are now wired, and task runtime can now also attempt rapid upload through upload/pre + update/hash + upload/finish when a usable local file plus md5/sha1 context is available; stable real online samples and ordinary upload chain are still pending.",
        },
        {
            "providerKey": "xunlei",
            "displayName": "Xunlei Drive",
            "officialDocsUrl": "",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
                "https://github.com/AlistGo/alist",
                "C:/Users/ChowYu/Desktop/新建文件夹 (3)/秒传.js",
            ],
            "webLoginUrl": "https://pan.xunlei.com/",
            "authModes": ["web_login_capture", "manual_token"],
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "token + x-device-id style live list/metadata(parentId-scoped lookup)/create_dir attempts are online from api-pan.xunlei.com evidence, and task runtime can now also attempt rapid upload through the live /drive/v1/files create-by-hash call when a usable local file plus gcid is available; stable real samples and full resumable upload fallback are still pending.",
        },
        {
            "providerKey": "pikpak",
            "displayName": "PikPak",
            "officialDocsUrl": "https://mypikpak.com/",
            "openSourceRefs": [
                "https://github.com/OpenListTeam/OpenList",
            ],
            "webLoginUrl": "https://mypikpak.com/",
            "authModes": ["manual_token"],
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "token + optional device headers can now drive live list/metadata/create_dir attempts on api-drive.mypikpak.com, and task runtime can now also attempt rapid upload through the live /drive/v1/files create-by-hash call when a usable local file plus gcid is available; stable real samples and full resumable upload fallback are still pending.",
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
            "status": "researching",
            "lastVerifiedAt": today,
            "notes": "token driven live list/metadata(create via parentFileId-scoped lookup) and create_dir attempts are online; stable real samples and upload chain are still pending.",
        },
    ]
