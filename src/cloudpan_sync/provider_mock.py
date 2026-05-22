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
    return []


def provider_mock_metadata(provider_key: str, path: str) -> SourceEntry:
    file_name = path.rsplit("/", 1)[-1] or "file.bin"
    seed = f"{provider_key}:{file_name}"
    fake_md5 = (seed.encode("utf-8").hex() + "0" * 32)[:32]
    return SourceEntry(
        path=path,
        size=max(128, len(seed) * 1024),
        md5=fake_md5,
        sha1="",
        sha256="",
        gcid="",
        etag=fake_md5,
    )
