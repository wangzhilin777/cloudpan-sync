from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .auth_store import DATA_DIR, get_profile


VALIDATION_FILE = DATA_DIR / "auth_live_validations.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_rows() -> list[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not VALIDATION_FILE.exists():
        return []
    text = VALIDATION_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        rows = json.loads(text)
    except json.JSONDecodeError:
        return []
    return rows if isinstance(rows, list) else []


def _write_rows(rows: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def list_live_validations() -> list[dict[str, object]]:
    return _read_rows()


@dataclass
class ValidationEndpoint:
    provider_key: str
    url: str
    kind: str


def _resolve_endpoint(provider_key: str) -> ValidationEndpoint | None:
    mapping = {
        "guangya": ValidationEndpoint("guangya", "https://guangyapan.com/", "web_home"),
        "aliyundrive_open": ValidationEndpoint("aliyundrive_open", "https://www.alipan.com/", "web_home"),
        "115_open": ValidationEndpoint("115_open", "https://115.com/", "web_home"),
        "189cloud": ValidationEndpoint("189cloud", "https://cloud.189.cn/", "web_home"),
        "baidu_netdisk": ValidationEndpoint("baidu_netdisk", "https://pan.baidu.com/", "web_home"),
        "quark": ValidationEndpoint("quark", "https://pan.quark.cn/", "web_home"),
        "uc": ValidationEndpoint("uc", "https://drive.uc.cn/", "web_home"),
        "xunlei": ValidationEndpoint("xunlei", "https://pan.xunlei.com/", "web_home"),
        "pikpak": ValidationEndpoint("pikpak", "https://mypikpak.com/", "web_home"),
        "123_open": ValidationEndpoint("123_open", "https://www.123pan.com/", "web_home"),
    }
    return mapping.get(provider_key)


def run_profile_live_validation(profile_id: str) -> dict[str, object]:
    profile = get_profile(profile_id)
    if profile is None:
        return {
            "ok": False,
            "profileId": profile_id,
            "providerKey": "",
            "status": 0,
            "error": "profile_not_found",
            "checkedAt": _now_iso(),
        }
    endpoint = _resolve_endpoint(profile.providerKey)
    if endpoint is None:
        return {
            "ok": False,
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "status": 0,
            "error": "provider_not_supported",
            "checkedAt": _now_iso(),
        }
    headers = {
        "User-Agent": "CloudPanSyncLiveValidate/1.0",
        "Accept": "text/html,application/json,*/*",
    }
    if profile.cookie:
        headers["Cookie"] = profile.cookie
    if profile.token:
        headers["Authorization"] = profile.token
    for k, v in profile.extra.items():
        if k.lower() in {"header", "x-auth-token", "x-device-id"} and v:
            if k.lower() == "header":
                parts = v.split("=", 1)
                if len(parts) == 2:
                    headers[parts[0].strip()] = parts[1].strip()
            else:
                headers[k] = v

    status = 0
    final_url = endpoint.url
    error = ""
    ok = False
    try:
        req = Request(endpoint.url, headers=headers, method="GET")
        with urlopen(req, timeout=10) as resp:
            status = int(getattr(resp, "status", 0) or 0)
            final_url = str(getattr(resp, "url", endpoint.url) or endpoint.url)
            ok = 200 <= status < 400
    except HTTPError as exc:
        status = int(exc.code or 0)
        error = f"http_error:{exc.code}"
    except URLError as exc:
        error = f"url_error:{exc.reason}"
    except Exception as exc:  # pragma: no cover
        error = f"unexpected:{exc}"

    row = {
        "ok": ok,
        "profileId": profile.profileId,
        "providerKey": profile.providerKey,
        "providerDisplayName": profile.displayName,
        "endpointUrl": endpoint.url,
        "endpointKind": endpoint.kind,
        "status": status,
        "finalUrl": final_url,
        "error": error,
        "checkedAt": _now_iso(),
    }
    rows = _read_rows()
    rows.append(row)
    _write_rows(rows)
    return row
