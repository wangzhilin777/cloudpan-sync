from __future__ import annotations

from .models import FingerprintSet, SourceEntry


def build_fingerprint_set(entry: SourceEntry) -> FingerprintSet:
    raw = dict(entry.raw or {})
    block_list = _normalize_block_list(
        entry.blockListMd5
        or raw.get("blockListMd5")
        or raw.get("block_list_md5")
        or raw.get("block_list")
        or []
    )
    return FingerprintSet(
        md5=_normalize_hash(_pick_first(entry.md5, raw.get("md5"), raw.get("MD5")), lowercase=True),
        sha1=_normalize_hash(_pick_first(entry.sha1, raw.get("sha1"), raw.get("SHA1")), lowercase=True),
        sha256=_normalize_hash(_pick_first(entry.sha256, raw.get("sha256"), raw.get("SHA256")), lowercase=True),
        crc64=_normalize_hash(_pick_first(entry.crc64, raw.get("crc64"), raw.get("CRC64")), lowercase=False),
        gcid=_normalize_hash(_pick_first(entry.gcid, raw.get("gcid"), raw.get("GCID")), lowercase=False),
        etag=_normalize_etag(_pick_first(entry.etag, raw.get("etag"), raw.get("ETag"))),
        pickcode=_normalize_token(_pick_first(entry.pickcode, raw.get("pickcode"), raw.get("pickCode"))),
        blockListMd5=block_list,
        raw=raw,
    )


def available_fast_inputs(fingerprints: FingerprintSet, path: str, size: int) -> list[str]:
    available: list[str] = []
    if int(size or 0) > 0:
        available.append("size")
    if str(path or "").strip():
        available.append("name")
    if fingerprints.md5:
        available.append("md5")
    if fingerprints.sha1:
        available.append("sha1")
    if fingerprints.sha256:
        available.append("sha256")
    if fingerprints.crc64:
        available.append("crc64")
    if fingerprints.gcid:
        available.append("gcid")
    if fingerprints.etag:
        available.append("etag")
    if fingerprints.pickcode:
        available.append("pickcode")
    if fingerprints.blockListMd5:
        available.append("blockListMd5")
    return available


def _pick_first(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _normalize_hash(value: str, lowercase: bool) -> str:
    text = str(value or "").strip().strip('"').strip("'")
    if not text:
        return ""
    normalized = text.replace("-", "").replace(" ", "")
    return normalized.lower() if lowercase else normalized.upper()


def _normalize_etag(value: str) -> str:
    text = str(value or "").strip().strip('"').strip("'")
    return text.lower()


def _normalize_token(value: str) -> str:
    return str(value or "").strip()


def _normalize_block_list(value: object) -> list[str]:
    if isinstance(value, str):
        raw_items = [part.strip() for part in value.replace(";", ",").split(",")]
    elif isinstance(value, list):
        raw_items = [str(item or "").strip() for item in value]
    else:
        raw_items = []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        text = _normalize_hash(item, lowercase=True)
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized
