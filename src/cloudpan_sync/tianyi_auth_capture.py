from __future__ import annotations

import json
import re


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _extract_from_header_lines(raw_text: str) -> dict[str, str]:
    result = {"accessToken": "", "signature": "", "date": ""}
    if not raw_text.strip():
        return result
    pattern_map = {
        "accessToken": re.compile(r"(?im)^\s*(?:access[_-]?token|accesstoken)\s*:\s*(.+?)\s*$"),
        "signature": re.compile(r"(?im)^\s*signature\s*:\s*(.+?)\s*$"),
        "date": re.compile(r"(?im)^\s*(?:date|timestamp)\s*:\s*(.+?)\s*$"),
    }
    for key, pattern in pattern_map.items():
        match = pattern.search(raw_text)
        if match:
            result[key] = _text(match.group(1)).strip("\"'")
    return result


def _extract_from_curl_headers(raw_text: str) -> dict[str, str]:
    result = {"accessToken": "", "signature": "", "date": ""}
    if not raw_text.strip():
        return result
    headers: list[str] = []
    for match in re.finditer(r"""(?is)(?:^|\s)-H\s+(['"])(.*?)\1""", raw_text):
        headers.append(_text(match.group(2)))
    if not headers:
        return result
    return _extract_from_header_lines("\n".join(headers))


def _extract_from_json_text(raw_text: str) -> dict[str, str]:
    result = {"accessToken": "", "signature": "", "date": ""}
    if "{" not in raw_text or "}" not in raw_text:
        return result
    try:
        payload = json.loads(raw_text)
    except Exception:
        return result
    if not isinstance(payload, dict):
        return result
    key_map = {
        "accessToken": ["accessToken", "AccessToken", "accesstoken", "token"],
        "signature": ["signature", "Signature"],
        "date": ["date", "Date", "timestamp", "Timestamp"],
    }
    for target_key, candidates in key_map.items():
        for candidate in candidates:
            value = _text(payload.get(candidate))
            if value:
                result[target_key] = value
                break
    return result


def extract_189cloud_account_auth(raw_text: str) -> dict[str, str]:
    text = _text(raw_text)
    result = {"accessToken": "", "signature": "", "date": ""}
    for extractor in (_extract_from_curl_headers, _extract_from_header_lines, _extract_from_json_text):
        extracted = extractor(text)
        for key, value in extracted.items():
            if value and not result.get(key):
                result[key] = value
    return result

