from __future__ import annotations

from .aliyun_open_live import fetch_aliyun_open_live_list, fetch_aliyun_open_live_metadata, fetch_aliyun_open_create_folder
from .auth_store import get_profile
from .baidu_netdisk_live import fetch_baidu_create_dir, fetch_baidu_live_list, fetch_baidu_live_metadata
from .guangya_live import fetch_guangya_live_list, fetch_guangya_live_metadata, fetch_guangya_create_dir
from .pan115_open_live import fetch_115_open_create_folder, fetch_115_open_live_list, fetch_115_open_live_metadata
from .pan123_open_live import fetch_123_open_create_folder, fetch_123_open_live_list, fetch_123_open_live_metadata
from .pikpak_live import fetch_pikpak_create_folder, fetch_pikpak_live_list, fetch_pikpak_live_metadata
from .quark_live import fetch_quark_live_list, fetch_quark_live_metadata, fetch_quark_create_folder
from .tianyi_live import fetch_tianyi_live_list, fetch_tianyi_live_metadata, fetch_tianyi_create_folder
from .uc_live import fetch_uc_live_list, fetch_uc_live_metadata, fetch_uc_create_folder
from .xunlei_live import fetch_xunlei_create_folder, fetch_xunlei_live_list, fetch_xunlei_live_metadata


def _run_provider_live_probe_with_profile(
    profile: object,
    parent_id: str = "",
    file_id: str = "",
    page_size: int = 100,
    dir_name: str = "",
) -> dict[str, object]:
    provider_key = profile.providerKey
    checks: list[dict[str, object]] = []

    if provider_key == "guangya":
        live = fetch_guangya_live_list(profile_id=profile.profileId, parent_id=parent_id, page_size=page_size)
        checks.append(
            {
                "kind": "list",
                "ok": live.ok,
                "mode": live.mode,
                "status": live.status,
                "error": live.error,
                "itemCount": len(live.items),
                "note": live.note,
            }
        )
        overall_ok = live.ok
        summary = live.note
        mode = live.mode
        if file_id:
            live_meta = fetch_guangya_live_metadata(profile_id=profile.profileId, file_id=file_id)
            checks.append(
                {
                    "kind": "metadata",
                    "ok": live_meta.ok,
                    "mode": live_meta.mode,
                    "status": live_meta.status,
                    "error": live_meta.error,
                    "hasMd5": bool((live_meta.items[0] if live_meta.items else {}).get("md5")),
                    "hasGcid": bool((live_meta.items[0] if live_meta.items else {}).get("gcid")),
                    "note": live_meta.note,
                }
            )
            overall_ok = overall_ok and live_meta.ok
            summary = f"{live.note} | {live_meta.note}"
            mode = "live" if live.ok and live_meta.ok else (live_meta.mode if not live_meta.ok else live.mode)
        if dir_name:
            create_dir = fetch_guangya_create_dir(profile_id=profile.profileId, parent_id=parent_id, dir_name=dir_name)
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": (create_dir.items[0] if create_dir.items else {}).get("fileId", ""),
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)
        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    if provider_key == "aliyundrive_open":
        live_list = fetch_aliyun_open_live_list(
            profile_id=profile.profileId,
            parent_file_id=parent_id or "root",
            limit=page_size,
        )
        checks.append(
            {
                "kind": "list",
                "ok": live_list.ok,
                "mode": live_list.mode,
                "status": live_list.status,
                "error": live_list.error,
                "itemCount": len(live_list.payload.get("items", [])) if live_list.ok else 0,
                "note": live_list.note,
            }
        )
        overall_ok = live_list.ok
        summary = live_list.note
        mode = live_list.mode

        if file_id:
            live_meta = fetch_aliyun_open_live_metadata(profile_id=profile.profileId, file_id=file_id)
            checks.append(
                {
                    "kind": "metadata",
                    "ok": live_meta.ok,
                    "mode": live_meta.mode,
                    "status": live_meta.status,
                    "error": live_meta.error,
                    "hasMd5": bool((live_meta.payload.get("entry") or {}).get("md5")) if live_meta.ok else False,
                    "note": live_meta.note,
                }
            )
            overall_ok = overall_ok and live_meta.ok
            summary = f"{live_list.note} | {live_meta.note}"
            mode = "live" if live_list.ok and live_meta.ok else (live_meta.mode if not live_meta.ok else live_list.mode)
        if dir_name:
            create_dir = fetch_aliyun_open_create_folder(
                profile_id=profile.profileId,
                parent_file_id=parent_id or "root",
                dir_name=dir_name,
            )
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": ((create_dir.payload.get("item") or {}).get("fileId", "")) if create_dir.ok else "",
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)

        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    if provider_key == "189cloud":
        live_list = fetch_tianyi_live_list(
            profile_id=profile.profileId,
            file_id=file_id,
            page_size=page_size,
        )
        checks.append(
            {
                "kind": "list",
                "ok": live_list.ok,
                "mode": live_list.mode,
                "status": live_list.status,
                "error": live_list.error,
                "itemCount": len(live_list.payload.get("items", [])) if live_list.ok else 0,
                "note": live_list.note,
            }
        )
        overall_ok = live_list.ok
        summary = live_list.note
        mode = live_list.mode

        live_meta = fetch_tianyi_live_metadata(profile_id=profile.profileId, file_id=file_id)
        checks.append(
            {
                "kind": "metadata",
                "ok": live_meta.ok,
                "mode": live_meta.mode,
                "status": live_meta.status,
                "error": live_meta.error,
                "hasMd5": bool((live_meta.payload.get("entry") or {}).get("md5")) if live_meta.ok else False,
                "note": live_meta.note,
            }
        )
        overall_ok = overall_ok and live_meta.ok
        summary = f"{summary} | {live_meta.note}"
        mode = "live" if overall_ok else (live_meta.mode if not live_meta.ok else live_list.mode)
        if dir_name:
            create_dir = fetch_tianyi_create_folder(
                profile_id=profile.profileId,
                parent_id=parent_id,
                dir_name=dir_name,
            )
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": ((create_dir.payload.get("item") or {}).get("fileId", "")) if create_dir.ok else "",
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)

        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    if provider_key == "baidu_netdisk":
        live_list = fetch_baidu_live_list(
            profile_id=profile.profileId,
            dir_path=parent_id or "/",
            limit=page_size,
        )
        checks.append(
            {
                "kind": "list",
                "ok": live_list.ok,
                "mode": live_list.mode,
                "status": live_list.status,
                "error": live_list.error,
                "itemCount": len(live_list.payload.get("items", [])) if live_list.ok else 0,
                "note": live_list.note,
            }
        )
        overall_ok = live_list.ok
        summary = live_list.note
        mode = live_list.mode

        if file_id:
            live_meta = fetch_baidu_live_metadata(
                profile_id=profile.profileId,
                file_id=file_id,
            )
            checks.append(
                {
                    "kind": "metadata",
                    "ok": live_meta.ok,
                    "mode": live_meta.mode,
                    "status": live_meta.status,
                    "error": live_meta.error,
                    "hasMd5": bool((live_meta.payload.get("entry") or {}).get("md5")) if live_meta.ok else False,
                    "note": live_meta.note,
                }
            )
            overall_ok = overall_ok and live_meta.ok
            summary = f"{summary} | {live_meta.note}"
            mode = "live" if overall_ok else (live_meta.mode if not live_meta.ok else live_list.mode)

        if dir_name:
            create_dir = fetch_baidu_create_dir(
                profile_id=profile.profileId,
                parent_dir=parent_id or "/",
                dir_name=dir_name,
            )
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": ((create_dir.payload.get("item") or {}).get("fileId", "")) if create_dir.ok else "",
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)

        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    if provider_key == "123_open":
        live_list = fetch_123_open_live_list(
            profile_id=profile.profileId,
            parent_file_id=parent_id or "0",
            limit=page_size,
        )
        checks.append(
            {
                "kind": "list",
                "ok": live_list.ok,
                "mode": live_list.mode,
                "status": live_list.status,
                "error": live_list.error,
                "itemCount": len(live_list.payload.get("items", [])) if live_list.ok else 0,
                "note": live_list.note,
            }
        )
        overall_ok = live_list.ok
        summary = live_list.note
        mode = live_list.mode
        if file_id:
            live_meta = fetch_123_open_live_metadata(
                profile_id=profile.profileId,
                file_id=file_id,
                parent_file_id=parent_id or "0",
            )
            checks.append(
                {
                    "kind": "metadata",
                    "ok": live_meta.ok,
                    "mode": live_meta.mode,
                    "status": live_meta.status,
                    "error": live_meta.error,
                    "hasMd5": bool((live_meta.payload.get("entry") or {}).get("md5")) if live_meta.ok else False,
                    "note": live_meta.note,
                }
            )
            overall_ok = overall_ok and live_meta.ok
            summary = f"{summary} | {live_meta.note}"
            mode = "live" if overall_ok else (live_meta.mode if not live_meta.ok else mode)
        if dir_name:
            create_dir = fetch_123_open_create_folder(
                profile_id=profile.profileId,
                parent_file_id=parent_id or "0",
                dir_name=dir_name,
            )
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": ((create_dir.payload.get("item") or {}).get("fileId", "")) if create_dir.ok else "",
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)
        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    if provider_key == "115_open":
        live_list = fetch_115_open_live_list(
            profile_id=profile.profileId,
            cid=parent_id or "0",
            limit=page_size,
        )
        checks.append(
            {
                "kind": "list",
                "ok": live_list.ok,
                "mode": live_list.mode,
                "status": live_list.status,
                "error": live_list.error,
                "itemCount": len(live_list.payload.get("items", [])) if live_list.ok else 0,
                "note": live_list.note,
            }
        )
        overall_ok = live_list.ok
        summary = live_list.note
        mode = live_list.mode
        if file_id:
            live_meta = fetch_115_open_live_metadata(
                profile_id=profile.profileId,
                file_id=file_id,
            )
            checks.append(
                {
                    "kind": "metadata",
                    "ok": live_meta.ok,
                    "mode": live_meta.mode,
                    "status": live_meta.status,
                    "error": live_meta.error,
                    "hasSha1": bool((live_meta.payload.get("entry") or {}).get("sha1")) if live_meta.ok else False,
                    "note": live_meta.note,
                }
            )
            overall_ok = overall_ok and live_meta.ok
            summary = f"{summary} | {live_meta.note}"
            mode = "live" if overall_ok else (live_meta.mode if not live_meta.ok else mode)
        if dir_name:
            create_dir = fetch_115_open_create_folder(
                profile_id=profile.profileId,
                parent_id=parent_id or "0",
                dir_name=dir_name,
            )
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": ((create_dir.payload.get("item") or {}).get("fileId", "")) if create_dir.ok else "",
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)
        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    if provider_key == "xunlei":
        live_list = fetch_xunlei_live_list(
            profile_id=profile.profileId,
            parent_id=parent_id,
            limit=page_size,
        )
        checks.append(
            {
                "kind": "list",
                "ok": live_list.ok,
                "mode": live_list.mode,
                "status": live_list.status,
                "error": live_list.error,
                "itemCount": len(live_list.payload.get("items", [])) if live_list.ok else 0,
                "note": live_list.note,
            }
        )
        overall_ok = live_list.ok
        summary = live_list.note
        mode = live_list.mode
        if file_id:
            live_meta = fetch_xunlei_live_metadata(
                profile_id=profile.profileId,
                file_id=file_id,
                parent_id=parent_id,
            )
            checks.append(
                {
                    "kind": "metadata",
                    "ok": live_meta.ok,
                    "mode": live_meta.mode,
                    "status": live_meta.status,
                    "error": live_meta.error,
                    "hasGcid": bool((live_meta.payload.get("entry") or {}).get("gcid")) if live_meta.ok else False,
                    "note": live_meta.note,
                }
            )
            overall_ok = overall_ok and live_meta.ok
            summary = f"{summary} | {live_meta.note}"
            mode = "live" if overall_ok else (live_meta.mode if not live_meta.ok else mode)
        if dir_name:
            create_dir = fetch_xunlei_create_folder(
                profile_id=profile.profileId,
                parent_id=parent_id,
                dir_name=dir_name,
            )
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": ((create_dir.payload.get("item") or {}).get("fileId", "")) if create_dir.ok else "",
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)
        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    if provider_key == "pikpak":
        live_list = fetch_pikpak_live_list(
            profile_id=profile.profileId,
            parent_id=parent_id,
            limit=page_size,
        )
        checks.append(
            {
                "kind": "list",
                "ok": live_list.ok,
                "mode": live_list.mode,
                "status": live_list.status,
                "error": live_list.error,
                "itemCount": len(live_list.payload.get("items", [])) if live_list.ok else 0,
                "note": live_list.note,
            }
        )
        overall_ok = live_list.ok
        summary = live_list.note
        mode = live_list.mode
        if file_id:
            live_meta = fetch_pikpak_live_metadata(
                profile_id=profile.profileId,
                file_id=file_id,
            )
            checks.append(
                {
                    "kind": "metadata",
                    "ok": live_meta.ok,
                    "mode": live_meta.mode,
                    "status": live_meta.status,
                    "error": live_meta.error,
                    "hasGcid": bool((live_meta.payload.get("entry") or {}).get("gcid")) if live_meta.ok else False,
                    "hasMd5": bool((live_meta.payload.get("entry") or {}).get("md5")) if live_meta.ok else False,
                    "note": live_meta.note,
                }
            )
            overall_ok = overall_ok and live_meta.ok
            summary = f"{summary} | {live_meta.note}"
            mode = "live" if overall_ok else (live_meta.mode if not live_meta.ok else mode)
        if dir_name:
            create_dir = fetch_pikpak_create_folder(
                profile_id=profile.profileId,
                parent_id=parent_id,
                dir_name=dir_name,
            )
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": ((create_dir.payload.get("item") or {}).get("fileId", "")) if create_dir.ok else "",
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)
        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    if provider_key == "quark":
        live_list = fetch_quark_live_list(
            profile_id=profile.profileId,
            parent_id=parent_id or "0",
            page_size=page_size,
        )
        checks.append(
            {
                "kind": "list",
                "ok": live_list.ok,
                "mode": live_list.mode,
                "status": live_list.status,
                "error": live_list.error,
                "itemCount": len(live_list.payload.get("items", [])) if live_list.ok else 0,
                "note": live_list.note,
            }
        )
        overall_ok = live_list.ok
        summary = live_list.note
        mode = live_list.mode
        if file_id:
            live_meta = fetch_quark_live_metadata(
                profile_id=profile.profileId,
                file_id=file_id,
                parent_id=parent_id or "0",
            )
            checks.append(
                {
                    "kind": "metadata",
                    "ok": live_meta.ok,
                    "mode": live_meta.mode,
                    "status": live_meta.status,
                    "error": live_meta.error,
                    "hasMd5": bool((live_meta.payload.get("entry") or {}).get("md5")) if live_meta.ok else False,
                    "note": live_meta.note,
                }
            )
            overall_ok = overall_ok and live_meta.ok
            summary = f"{summary} | {live_meta.note}"
            mode = "live" if overall_ok else (live_meta.mode if not live_meta.ok else mode)
        if dir_name:
            create_dir = fetch_quark_create_folder(
                profile_id=profile.profileId,
                parent_id=parent_id or "0",
                dir_name=dir_name,
            )
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": ((create_dir.payload.get("item") or {}).get("fileId", "")) if create_dir.ok else "",
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)
        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    if provider_key == "uc":
        live_list = fetch_uc_live_list(
            profile_id=profile.profileId,
            parent_id=parent_id or "0",
            page_size=page_size,
        )
        checks.append(
            {
                "kind": "list",
                "ok": live_list.ok,
                "mode": live_list.mode,
                "status": live_list.status,
                "error": live_list.error,
                "itemCount": len(live_list.payload.get("items", [])) if live_list.ok else 0,
                "note": live_list.note,
            }
        )
        overall_ok = live_list.ok
        summary = live_list.note
        mode = live_list.mode
        if file_id:
            live_meta = fetch_uc_live_metadata(
                profile_id=profile.profileId,
                file_id=file_id,
                parent_id=parent_id or "0",
            )
            checks.append(
                {
                    "kind": "metadata",
                    "ok": live_meta.ok,
                    "mode": live_meta.mode,
                    "status": live_meta.status,
                    "error": live_meta.error,
                    "hasMd5": bool((live_meta.payload.get("entry") or {}).get("md5")) if live_meta.ok else False,
                    "note": live_meta.note,
                }
            )
            overall_ok = overall_ok and live_meta.ok
            summary = f"{summary} | {live_meta.note}"
            mode = "live" if overall_ok else (live_meta.mode if not live_meta.ok else mode)
        if dir_name:
            create_dir = fetch_uc_create_folder(
                profile_id=profile.profileId,
                parent_id=parent_id or "0",
                dir_name=dir_name,
            )
            checks.append(
                {
                    "kind": "create_dir",
                    "ok": create_dir.ok,
                    "mode": create_dir.mode,
                    "status": create_dir.status,
                    "error": create_dir.error,
                    "createdDirId": ((create_dir.payload.get("item") or {}).get("fileId", "")) if create_dir.ok else "",
                    "note": create_dir.note,
                }
            )
            overall_ok = overall_ok and create_dir.ok
            summary = f"{summary} | {create_dir.note}"
            mode = "live" if overall_ok else (create_dir.mode if not create_dir.ok else mode)
        return {
            "ok": overall_ok,
            "profileId": profile.profileId,
            "providerKey": provider_key,
            "mode": mode,
            "summary": summary,
            "checks": checks,
        }

    return {
        "ok": False,
        "profileId": profile.profileId,
        "providerKey": provider_key,
        "mode": "unsupported",
        "summary": "This provider does not have a live probe adapter yet.",
        "checks": [],
    }


def run_provider_live_probe_for_profile(
    profile: object,
    parent_id: str = "",
    file_id: str = "",
    page_size: int = 100,
    dir_name: str = "",
) -> dict[str, object]:
    return _run_provider_live_probe_with_profile(
        profile=profile,
        parent_id=parent_id,
        file_id=file_id,
        page_size=page_size,
        dir_name=dir_name,
    )


def run_provider_live_probe(
    profile_id: str,
    parent_id: str = "",
    file_id: str = "",
    page_size: int = 100,
    dir_name: str = "",
) -> dict[str, object]:
    profile = get_profile(profile_id)
    if profile is None:
        return {
            "ok": False,
            "profileId": profile_id,
            "providerKey": "",
            "mode": "profile_missing",
            "summary": "Auth profile not found.",
            "checks": [],
        }

    return _run_provider_live_probe_with_profile(
        profile=profile,
        parent_id=parent_id,
        file_id=file_id,
        page_size=page_size,
        dir_name=dir_name,
    )
