# CloudPan Sync Local Live Adapter Verification

> 本报告来自 `scripts/verify_provider_live_adapters.py` 的本地可控 stub 验证。
> 它证明当前工作树里的适配器逻辑和聚合逻辑可跑通，但不等同于真实网盘在线成功。

- providerCount: `10`
- providerSummary: `all_ok=guangya, aliyundrive_open, 189cloud, baidu_netdisk, 123_open, 115_open, xunlei, pikpak, quark, uc` `md5_ready=guangya, aliyundrive_open, 189cloud, baidu_netdisk, 123_open, quark, uc` `gcid_ready=guangya, xunlei, pikpak` `probe_ready=guangya, aliyundrive_open, 189cloud, baidu_netdisk, 123_open, 115_open, xunlei, pikpak, quark, uc` `matrix_ready=guangya, aliyundrive_open, 189cloud, baidu_netdisk, 123_open, 115_open, xunlei, pikpak, quark, uc` `account_create_mode=189cloud=live_account_auth`

## guangya
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- metadata_md5: `0123456789abcdef0123456789abcdef`
- metadata_gcid: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`

## aliyundrive_open
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- metadata_md5: `0123456789abcdef0123456789abcdef`

## 189cloud
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- create_mode: `live_account_auth`
- create_file_id: `dir-189-1`
- metadata_md5: `0123456789abcdef0123456789abcdef`

## baidu_netdisk
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- metadata_md5: `0123456789abcdef0123456789abcdef`

## 123_open
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- metadata_md5: `0123456789abcdef0123456789abcdef`

## 115_open
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- metadata_sha1: ``

## xunlei
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- metadata_gcid: `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`

## pikpak
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- metadata_gcid: `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`

## quark
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- metadata_md5: `0123456789abcdef0123456789abcdef`

## uc
- list_ok: `True`
- metadata_ok: `True`
- create_ok: `True`
- metadata_md5: `0123456789abcdef0123456789abcdef`

## Probe Checks
- guangya: `3`
- aliyundrive_open: `3`
- 189cloud: `3`
- baidu_netdisk: `3`
- 123_open: `3`
- 115_open: `3`
- xunlei: `3`
- pikpak: `3`
- quark: `3`
- uc: `3`

## Matrix Rows
- 115_open: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
- 123_open: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
- 189cloud: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
- aliyundrive_open: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
- baidu_netdisk: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
- guangya: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
- pikpak: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
- quark: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
- uc: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
- xunlei: `list_ready=True` `metadata_ready=True` `create_dir_ready=True` `live_probe_ok=True`
