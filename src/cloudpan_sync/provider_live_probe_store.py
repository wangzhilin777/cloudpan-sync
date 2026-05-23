from __future__ import annotations

import json

from .auth_store import DATA_DIR


PROBE_FILE = DATA_DIR / "provider_live_probes.json"


def _read_rows() -> list[dict[str, object]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PROBE_FILE.exists():
        return []
    text = PROBE_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        rows = json.loads(text)
    except json.JSONDecodeError:
        return []
    return rows if isinstance(rows, list) else []


def _write_rows(rows: list[dict[str, object]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROBE_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def list_provider_live_probes() -> list[dict[str, object]]:
    return _read_rows()


def latest_provider_live_probes() -> list[dict[str, object]]:
    latest_by_profile: dict[str, dict[str, object]] = {}
    for row in _read_rows():
        profile_id = str(row.get("profileId") or "")
        provider_key = str(row.get("providerKey") or "")
        if not profile_id or not provider_key:
            continue
        latest_by_profile[f"{provider_key}::{profile_id}"] = row
    return list(latest_by_profile.values())


def latest_provider_live_probe_for_profile(profile_id: str, provider_key: str = "") -> dict[str, object] | None:
    target_profile_id = str(profile_id or "")
    target_provider_key = str(provider_key or "")
    if not target_profile_id:
        return None
    latest: dict[str, object] | None = None
    for row in _read_rows():
        row_profile_id = str(row.get("profileId") or "")
        row_provider_key = str(row.get("providerKey") or "")
        if row_profile_id != target_profile_id:
            continue
        if target_provider_key and row_provider_key != target_provider_key:
            continue
        latest = row
    return latest


def provider_live_probe_summary() -> dict[str, object]:
    rows = latest_provider_live_probes()
    return {
        "profileCount": len(rows),
        "okCount": sum(1 for row in rows if bool(row.get("ok"))),
        "failedCount": sum(1 for row in rows if not bool(row.get("ok"))),
        "providerKeys": sorted({str(row.get("providerKey") or "") for row in rows if str(row.get("providerKey") or "")}),
    }


def save_provider_live_probe(row: dict[str, object]) -> dict[str, object]:
    rows = _read_rows()
    profile_id = str(row.get("profileId") or "")
    provider_key = str(row.get("providerKey") or "")
    replaced = False
    for index, existing in enumerate(rows):
        if str(existing.get("profileId") or "") == profile_id and str(existing.get("providerKey") or "") == provider_key:
            rows[index] = row
            replaced = True
            break
    if not replaced:
        rows.append(row)
    _write_rows(rows)
    return row


def delete_provider_live_probe(profile_id: str) -> None:
    rows = _read_rows()
    kept = [row for row in rows if str(row.get("profileId") or "") != str(profile_id or "")]
    _write_rows(kept)
