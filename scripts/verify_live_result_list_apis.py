from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import webapp
from fastapi.testclient import TestClient


@contextmanager
def patched_attr(target: object, name: str, value: object):
    original = getattr(target, name)
    setattr(target, name, value)
    try:
        yield
    finally:
        setattr(target, name, original)


def _assert_common_shape(payload: dict[str, object], kind: str) -> dict[str, object]:
    assert isinstance(payload.get("items"), list), f"{kind}.items should be a list"
    assert isinstance(payload.get("latestItems"), list), f"{kind}.latestItems should be a list"
    assert isinstance(payload.get("summary"), dict), f"{kind}.summary should be a dict"
    return {
        "historyCount": len(payload.get("items") or []),
        "latestCount": len(payload.get("latestItems") or []),
        "summary": dict(payload.get("summary") or {}),
    }


def main() -> None:
    auth_history = [
        {"profileId": "p1", "providerKey": "guangya", "checkedAt": "2026-05-23T00:00:00+00:00", "ok": False},
        {"profileId": "p1", "providerKey": "guangya", "checkedAt": "2026-05-23T00:05:00+00:00", "ok": True},
        {"profileId": "p2", "providerKey": "123_open", "checkedAt": "2026-05-23T00:10:00+00:00", "ok": False},
    ]
    auth_latest = [
        {"profileId": "p1", "providerKey": "guangya", "checkedAt": "2026-05-23T00:05:00+00:00", "ok": True},
        {"profileId": "p2", "providerKey": "123_open", "checkedAt": "2026-05-23T00:10:00+00:00", "ok": False},
    ]
    auth_summary = {
        "profileCount": 2,
        "okCount": 1,
        "failedCount": 1,
        "providerKeys": ["123_open", "guangya"],
    }

    probe_history = [
        {"profileId": "p1", "providerKey": "guangya", "checkedAt": "2026-05-23T00:00:00+00:00", "ok": False},
        {"profileId": "p1", "providerKey": "guangya", "checkedAt": "2026-05-23T00:05:00+00:00", "ok": False},
        {"profileId": "p3", "providerKey": "aliyundrive_open", "checkedAt": "2026-05-23T00:10:00+00:00", "ok": True},
    ]
    probe_latest = [
        {"profileId": "p1", "providerKey": "guangya", "checkedAt": "2026-05-23T00:05:00+00:00", "ok": False},
        {"profileId": "p3", "providerKey": "aliyundrive_open", "checkedAt": "2026-05-23T00:10:00+00:00", "ok": True},
    ]
    probe_summary = {
        "profileCount": 2,
        "okCount": 1,
        "failedCount": 1,
        "providerKeys": ["aliyundrive_open", "guangya"],
    }

    with patched_attr(webapp, "ADMIN_PASSWORD", "admin123"):
        with patched_attr(webapp, "list_live_validations", lambda: list(auth_history)):
            with patched_attr(webapp, "latest_live_validations", lambda: list(auth_latest)):
                with patched_attr(webapp, "live_validation_summary", lambda: dict(auth_summary)):
                    with patched_attr(webapp, "list_provider_live_probes", lambda: list(probe_history)):
                        with patched_attr(webapp, "latest_provider_live_probes", lambda: list(probe_latest)):
                            with patched_attr(webapp, "provider_live_probe_summary", lambda: dict(probe_summary)):
                                app = webapp.create_app()
                                client = TestClient(app)
                                client.post("/api/login", json={"password": "admin123"})
                                auth_payload = client.get("/api/auth/live_validations").json()
                                probe_payload = client.get("/api/providers/live_probe_results").json()

    auth_result = _assert_common_shape(auth_payload, "auth")
    probe_result = _assert_common_shape(probe_payload, "probe")

    assert auth_result["historyCount"] == 3, "auth history count mismatch"
    assert auth_result["latestCount"] == 2, "auth latest count mismatch"
    assert auth_result["summary"] == auth_summary, "auth summary mismatch"
    assert probe_result["historyCount"] == 3, "probe history count mismatch"
    assert probe_result["latestCount"] == 2, "probe latest count mismatch"
    assert probe_result["summary"] == probe_summary, "probe summary mismatch"

    print(
        json.dumps(
            {
                "auth": auth_result,
                "probe": probe_result,
                "verifiedKeys": ["items", "latestItems", "summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
