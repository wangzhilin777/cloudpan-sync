from __future__ import annotations

import base64
from dataclasses import dataclass

from .models import SourceEntry


@dataclass
class GuangyaFastCheckResult:
    supported: bool
    hashKind: str
    normalizedHash: str
    reason: str
    riskHint: str


def _decode_md5_token(raw_hash: str) -> str:
    text = (raw_hash or "").strip().strip('"')
    if not text:
        return ""
    lower = text.lower()
    if len(lower) == 32 and all(ch in "0123456789abcdef" for ch in lower):
        return lower
    try:
        normalized = text.replace("-", "+").replace("_", "/")
        padded = normalized + "=" * ((4 - (len(normalized) % 4)) % 4)
        data = base64.b64decode(padded)
        if len(data) != 16:
            return ""
        return "".join(f"{b:02x}" for b in data)
    except Exception:
        return ""


def guangya_fast_check(entry: SourceEntry) -> GuangyaFastCheckResult:
    md5 = _decode_md5_token(entry.md5 or entry.etag)
    gcid = (entry.gcid or "").strip().lower()

    if md5:
        return GuangyaFastCheckResult(
            supported=True,
            hashKind="md5",
            normalizedHash=md5,
            reason="MD5 is available and can be used for Guangya fast-upload precheck.",
            riskHint="Use low concurrency and watch for anti-abuse responses.",
        )

    if len(gcid) == 40 and all(ch in "0123456789abcdef" for ch in gcid):
        return GuangyaFastCheckResult(
            supported=True,
            hashKind="gcid",
            normalizedHash=gcid,
            reason="GCID looks valid and can be used for Guangya GCID precheck.",
            riskHint="GCID support depends on current provider-side policy.",
        )

    return GuangyaFastCheckResult(
        supported=False,
        hashKind="missing",
        normalizedHash="",
        reason="Neither valid MD5 nor valid 40-char GCID is available.",
        riskHint="Fallback may require manual confirmation for large files.",
    )


def guangya_mock_list(path: str) -> list[dict[str, object]]:
    base = (path or "/").rstrip("/") or "/"
    return [
        {"name": "docs", "path": f"{base}/docs", "type": "dir"},
        {"name": "photo.jpg", "path": f"{base}/photo.jpg", "type": "file", "size": 1248291},
        {"name": "archive.zip", "path": f"{base}/archive.zip", "type": "file", "size": 20481234},
    ]
