from __future__ import annotations

from .models import SourceEntry


def provider_mock_list(provider_key: str, path: str) -> list[dict[str, object]]:
    base = (path or "/").rstrip("/") or "/"
    if provider_key == "aliyundrive_open":
        return [
            {"name": "projects", "path": f"{base}/projects", "type": "dir"},
            {"name": "video.mp4", "path": f"{base}/video.mp4", "type": "file", "size": 73400320},
        ]
    if provider_key == "115_open":
        return [
            {"name": "media", "path": f"{base}/media", "type": "dir"},
            {"name": "backup.tar", "path": f"{base}/backup.tar", "type": "file", "size": 149946368},
        ]
    if provider_key == "quark":
        return [
            {"name": "docs", "path": f"{base}/docs", "type": "dir"},
            {"name": "ebook.epub", "path": f"{base}/ebook.epub", "type": "file", "size": 6172839},
        ]
    if provider_key == "189cloud":
        return [
            {"name": "work", "path": f"{base}/work", "type": "dir"},
            {"name": "report.xlsx", "path": f"{base}/report.xlsx", "type": "file", "size": 3291823},
        ]
    if provider_key == "baidu_netdisk":
        return [
            {"name": "share", "path": f"{base}/share", "type": "dir"},
            {"name": "movie.mkv", "path": f"{base}/movie.mkv", "type": "file", "size": 1503238553},
        ]
    if provider_key == "uc":
        return [
            {"name": "notes", "path": f"{base}/notes", "type": "dir"},
            {"name": "slides.pptx", "path": f"{base}/slides.pptx", "type": "file", "size": 8721312},
        ]
    if provider_key == "xunlei":
        return [
            {"name": "downloads", "path": f"{base}/downloads", "type": "dir"},
            {"name": "linux.iso", "path": f"{base}/linux.iso", "type": "file", "size": 2382364672},
        ]
    if provider_key == "pikpak":
        return [
            {"name": "saved", "path": f"{base}/saved", "type": "dir"},
            {"name": "clip.mp4", "path": f"{base}/clip.mp4", "type": "file", "size": 18823212},
        ]
    if provider_key == "123_open":
        return [
            {"name": "backup", "path": f"{base}/backup", "type": "dir"},
            {"name": "db.dump", "path": f"{base}/db.dump", "type": "file", "size": 91231345},
        ]
    return []


def provider_mock_metadata(provider_key: str, path: str) -> SourceEntry:
    file_name = path.rsplit("/", 1)[-1] or "file.bin"
    seed = f"{provider_key}:{file_name}"
    fake_md5 = (seed.encode("utf-8").hex() + "0" * 32)[:32]
    return SourceEntry(
        path=path,
        size=max(128, len(seed) * 1024),
        md5=fake_md5,
        sha1=("0" * 40) if provider_key == "115_open" else "",
        sha256="",
        gcid=("a" * 40) if provider_key in {"xunlei", "pikpak"} else "",
        etag=fake_md5,
    )
