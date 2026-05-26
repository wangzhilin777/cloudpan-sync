# CloudPan Sync Provider Live Probe Report

- GeneratedAt: `2026-05-26T20:21:49.324462+00:00`
- Summary: providerCount=10, totalChecks=12, okChecks=12, failedChecks=0, profileProbeProviderCount=4, profileProbeOkCount=0, profileProbeFailedCount=4
- profileProbeProfiles: `ok=(none)` `failed=22173a49-2206-4da8-8624-9bab7bbbe64b, gy-live-1, pikpak-live-1, uc-live-1`
- profileProbeProviderSummary: `ok_providers=(none)` `failed_providers=aliyundrive_open, guangya, pikpak, uc` `failed_modes=live_error`

## guangya - Guangya
- web_login: ok=True status=200 url=https://guangyapan.com/ final=https://www.guangyapan.com/ error=
- profile_probe: ok=False mode=live_error checks=1 summary=Guangya live list request reached the API but was rejected.

## aliyundrive_open - Aliyun Drive Open
- official_docs: ok=True status=200 url=https://www.alipan.com/ final=https://www.alipan.com/ error=
- profile_probe: ok=False mode=live_error checks=1 summary=Aliyun Drive Open live list reached the API but was rejected.

## 115_open - 115 Open
- no-check: officialDocsUrl/webLoginUrl missing

## quark - Quark
- web_login: ok=True status=200 url=https://pan.quark.cn/ final=https://h5.sm.cn/blm/mobile-entry-97/index#/ error=

## 189cloud - Tianyi 189Cloud
- web_login: ok=True status=200 url=https://cloud.189.cn/ final=https://cloud.189.cn/web/ error=

## baidu_netdisk - Baidu Netdisk
- official_docs: ok=True status=200 url=https://pan.baidu.com/ final=https://pan.baidu.com/ error=
- web_login: ok=True status=200 url=https://pan.baidu.com/ final=https://pan.baidu.com/ error=

## uc - UC Drive
- web_login: ok=True status=200 url=https://drive.uc.cn/ final=https://broccoli.uc.cn/apps/jQYYbZEQ/routes/Qy6rMHoHy?uc_param_str=dsdnfrpfbivesscpgimibtbmnijblauputogpintnwktprchmt&uc_biz_str=S%3Acustom%7CC%3Atitlebar_hover_2 error=
- profile_probe: ok=False mode=live_error checks=1 summary=UC Drive live list reached the API but was rejected.

## xunlei - Xunlei Drive
- web_login: ok=True status=200 url=https://pan.xunlei.com/ final=https://pan.xunlei.com/ error=

## pikpak - PikPak
- official_docs: ok=True status=200 url=https://mypikpak.com/ final=https://mypikpak.com/en-US error=
- web_login: ok=True status=200 url=https://mypikpak.com/ final=https://mypikpak.com/en-US error=
- profile_probe: ok=False mode=live_error checks=1 summary=PikPak live list reached the API but was rejected.

## 123_open - 123Pan Open
- official_docs: ok=True status=200 url=https://www.123pan.com/ final=https://www.123pan.com/ error=
- web_login: ok=True status=200 url=https://www.123pan.com/ final=https://www.123pan.com/ error=
