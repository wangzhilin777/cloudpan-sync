from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .auth_store import get_profile


@dataclass
class AliyunOpenResult:
    ok: bool
    mode: str
    usedProfile: bool
    profileId: str
    status: int
    error: str
    note: str
    payload: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "mode": self.mode,
            "usedProfile": self.usedProfile,
            "profileId": self.profileId,
            "status": self.status,
            "error": self.error,
            "note": self.note,
            "payload": self.payload,
        }


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _auth_header(value: str) -> str:
    token = _text(value)
    if not token:
        return ""
    return token if token.lower().startswith("bearer ") else f"Bearer {token}"


def _domain_host(domain_id: str) -> str:
    return f"https://{domain_id}.api.aliyunpds.com"


def _load_profile_requirements(profile_id: str) -> tuple[object | None, str, str, str]:
    profile = get_profile(profile_id)
    if profile is None:
        return None, "", "", ""
    auth = _auth_header(profile.token or profile.extra.get("authorization", ""))
    domain_id = _text(profile.extra.get("domainId") or profile.extra.get("domain_id"))
    drive_id = _text(profile.extra.get("driveId") or profile.extra.get("drive_id"))
    return profile, auth, domain_id, drive_id


def _post_json(url: str, body: dict[str, object], auth: str) -> tuple[int, dict[str, object]]:
    request = Request(
        url=url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "User-Agent": "CloudPanSync/0.1",
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": auth,
        },
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        status = int(getattr(response, "status", 0) or 0)
        text = response.read().decode("utf-8", errors="replace")
    payload = json.loads(text)
    return status, payload if isinstance(payload, dict) else {}


def _normalize_list_items(payload: dict[str, object]) -> list[dict[str, object]]:
    items = payload.get("items")
    if not isinstance(items, list):
        return []
    rows: list[dict[str, object]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        file_id = _text(item.get("file_id"))
        name = _text(item.get("name"))
        if not file_id or not name:
            continue
        item_type = _text(item.get("type")) or "file"
        rows.append(
            {
                "fileId": file_id,
                "parentId": _text(item.get("parent_file_id")),
                "name": name,
                "path": _text(item.get("name_path")) or name,
                "type": item_type,
                "isDir": item_type == "folder",
                "size": int(item.get("size", 0) or 0),
                "md5": _text(item.get("content_hash")) if _text(item.get("content_hash_name")).lower() == "md5" else "",
                "sha1": _text(item.get("content_hash")) if _text(item.get("content_hash_name")).lower() == "sha1" else "",
                "etag": _text(item.get("etag")),
                "raw": item,
            }
        )
    return rows


def _normalize_metadata_entry(payload: dict[str, object]) -> dict[str, object]:
    item_type = _text(payload.get("type")) or "file"
    content_hash = _text(payload.get("content_hash"))
    hash_name = _text(payload.get("content_hash_name")).lower()
    return {
        "path": _text(payload.get("name_path")) or _text(payload.get("name")),
        "size": int(payload.get("size", 0) or 0),
        "md5": content_hash if hash_name == "md5" else "",
        "sha1": content_hash if hash_name == "sha1" else "",
        "sha256": content_hash if hash_name == "sha256" else "",
        "gcid": "",
        "etag": _text(payload.get("etag")),
        "raw": {
            "fileId": _text(payload.get("file_id")),
            "name": _text(payload.get("name")),
            "type": item_type,
            "parentFileId": _text(payload.get("parent_file_id")),
            "contentHashName": hash_name,
            "contentHash": content_hash,
        },
    }


def fetch_aliyun_open_live_list(profile_id: str, parent_file_id: str = "root", limit: int = 100) -> AliyunOpenResult:
    profile, auth, domain_id, drive_id = _load_profile_requirements(profile_id)
    if profile is None:
        return AliyunOpenResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved Aliyun Drive Open auth profile was not found.", {})
    if not auth:
        return AliyunOpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_access_token", "Aliyun live list requires access token in token or extra.authorization.", {})
    if not domain_id or not drive_id:
        return AliyunOpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_domain_or_drive_id", "Aliyun live list requires extra.domainId and extra.driveId.", {})

    body = {
        "drive_id": drive_id,
        "parent_file_id": _text(parent_file_id) or "root",
        "limit": max(1, min(100, int(limit or 100))),
    }
    try:
        status, payload = _post_json(f"{_domain_host(domain_id)}/v2/file/list", body, auth)
        return AliyunOpenResult(True, "live", True, profile.profileId, status, "", "Aliyun Drive Open live list succeeded with saved access token.", {"items": _normalize_list_items(payload), "raw": payload, "domainId": domain_id, "driveId": drive_id})
    except HTTPError as exc:
        return AliyunOpenResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "Aliyun Drive Open live list reached the API but was rejected.", {})
    except URLError as exc:
        return AliyunOpenResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "Aliyun Drive Open live list could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return AliyunOpenResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "Aliyun Drive Open live list returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return AliyunOpenResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "Aliyun Drive Open live list failed unexpectedly.", {})


def fetch_aliyun_open_live_metadata(profile_id: str, file_id: str) -> AliyunOpenResult:
    profile, auth, domain_id, drive_id = _load_profile_requirements(profile_id)
    if profile is None:
        return AliyunOpenResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved Aliyun Drive Open auth profile was not found.", {})
    if not auth:
        return AliyunOpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_access_token", "Aliyun live metadata requires access token in token or extra.authorization.", {})
    if not domain_id or not drive_id:
        return AliyunOpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_domain_or_drive_id", "Aliyun live metadata requires extra.domainId and extra.driveId.", {})
    resolved_file_id = _text(file_id)
    if not resolved_file_id:
        return AliyunOpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_file_id", "Aliyun live metadata requires fileId in the request.", {})

    body = {
        "drive_id": drive_id,
        "file_id": resolved_file_id,
    }
    try:
        status, payload = _post_json(f"{_domain_host(domain_id)}/v2/file/get", body, auth)
        return AliyunOpenResult(True, "live", True, profile.profileId, status, "", "Aliyun Drive Open live metadata request succeeded with saved access token.", {"entry": _normalize_metadata_entry(payload), "raw": payload, "domainId": domain_id, "driveId": drive_id})
    except HTTPError as exc:
        return AliyunOpenResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "Aliyun Drive Open live metadata reached the API but was rejected.", {})
    except URLError as exc:
        return AliyunOpenResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "Aliyun Drive Open live metadata could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return AliyunOpenResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "Aliyun Drive Open live metadata returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return AliyunOpenResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "Aliyun Drive Open live metadata failed unexpectedly.", {})


def fetch_aliyun_open_create_folder(profile_id: str, parent_file_id: str, dir_name: str) -> AliyunOpenResult:
    profile, auth, domain_id, drive_id = _load_profile_requirements(profile_id)
    if profile is None:
        return AliyunOpenResult(False, "profile_missing", False, profile_id, 0, "profile_not_found", "Saved Aliyun Drive Open auth profile was not found.", {})
    if not auth:
        return AliyunOpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_access_token", "Aliyun create folder requires access token in token or extra.authorization.", {})
    if not domain_id or not drive_id:
        return AliyunOpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_domain_or_drive_id", "Aliyun create folder requires extra.domainId and extra.driveId.", {})

    resolved_parent_id = _text(parent_file_id) or "root"
    resolved_dir_name = _text(dir_name)
    if not resolved_dir_name:
        return AliyunOpenResult(False, "profile_incomplete", True, profile.profileId, 0, "missing_dir_name", "Aliyun create folder requires dirName in the request.", {})

    body = {
        "drive_id": drive_id,
        "parent_file_id": resolved_parent_id,
        "name": resolved_dir_name,
        "type": "folder",
        "check_name_mode": "auto_rename",
    }
    try:
        status, payload = _post_json(f"{_domain_host(domain_id)}/v2/file/create", body, auth)
        item = {
            "fileId": _text(payload.get("file_id")),
            "parentId": _text(payload.get("parent_file_id")) or resolved_parent_id,
            "name": _text(payload.get("name")) or resolved_dir_name,
            "path": _text(payload.get("name_path")) or resolved_dir_name,
            "type": "folder",
            "isDir": True,
            "size": 0,
            "raw": payload,
        }
        return AliyunOpenResult(True, "live", True, profile.profileId, status, "", "Aliyun Drive Open live create folder succeeded with saved access token.", {"item": item, "raw": payload, "domainId": domain_id, "driveId": drive_id})
    except HTTPError as exc:
        return AliyunOpenResult(False, "live_error", True, profile.profileId, int(exc.code or 0), f"http_error:{exc.code}", "Aliyun Drive Open create folder reached the API but was rejected.", {})
    except URLError as exc:
        return AliyunOpenResult(False, "live_error", True, profile.profileId, 0, f"url_error:{exc.reason}", "Aliyun Drive Open create folder could not reach the API endpoint.", {})
    except json.JSONDecodeError:
        return AliyunOpenResult(False, "live_error", True, profile.profileId, 200, "invalid_json", "Aliyun Drive Open create folder returned non-JSON content.", {})
    except Exception as exc:  # pragma: no cover
        return AliyunOpenResult(False, "live_error", True, profile.profileId, 0, f"unexpected:{exc}", "Aliyun Drive Open create folder failed unexpectedly.", {})
