from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import auth_live_validate
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


def main() -> None:
    profile = SimpleNamespace(
        profileId="auth-test-1",
        providerKey="123_open",
        displayName="auth-test-profile",
        extra={"parentFileId": "0", "fileId": "file-1"},
    )

    saved_rows: list[dict[str, object]] = []

    def fake_probe(profile_id: str, parent_id: str = "", file_id: str = "", page_size: int = 100, dir_name: str = ""):
        return {
            "ok": True,
            "profileId": profile_id,
            "providerKey": "123_open",
            "mode": "live",
            "summary": "123 list ok | 123 meta ok",
            "checks": [
                {"kind": "list", "ok": True, "status": 200, "error": "", "note": "123 list ok"},
                {"kind": "metadata", "ok": True, "status": 200, "error": "", "note": "123 meta ok"},
            ],
        }

    def fake_probe_for_profile(profile: object, parent_id: str = "", file_id: str = "", page_size: int = 100, dir_name: str = ""):
        return {
            "ok": True,
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "mode": "live",
            "summary": "123 list ok | 123 meta ok",
            "checks": [
                {"kind": "list", "ok": True, "status": 200, "error": "", "note": "123 list ok"},
                {"kind": "metadata", "ok": True, "status": 200, "error": "", "note": "123 meta ok"},
            ],
        }

    with patched_attr(auth_live_validate, "get_profile", lambda profile_id: profile if profile_id == profile.profileId else None):
        with patched_attr(auth_live_validate, "list_profiles", lambda: [profile]):
            with patched_attr(auth_live_validate, "run_provider_live_probe", fake_probe):
                with patched_attr(auth_live_validate, "run_provider_live_probe_for_profile", fake_probe_for_profile):
                    with patched_attr(auth_live_validate, "_read_rows", lambda: list(saved_rows)):
                        with patched_attr(auth_live_validate, "_write_rows", lambda rows: saved_rows.clear() or saved_rows.extend(rows)):
                            single = auth_live_validate.run_profile_live_validation("auth-test-1")
                            batch = auth_live_validate.run_all_profile_live_validations()

    created_profiles: list[object] = []
    api_saved_rows: list[dict[str, object]] = []

    class FakeProfile:
        def __init__(self, payload):
            self.profileId = "created-1"
            self.providerKey = payload.providerKey
            self.authMode = payload.authMode
            self.displayName = payload.displayName
            self.token = payload.token
            self.cookie = payload.cookie
            self.extra = payload.extra
            self.status = "saved"
            self.lastError = ""
            self.createdAt = "2026-05-23T00:00:00+00:00"
            self.updatedAt = "2026-05-23T00:00:00+00:00"

        def model_dump(self):
            return {
                "profileId": self.profileId,
                "providerKey": self.providerKey,
                "authMode": self.authMode,
                "displayName": self.displayName,
                "token": self.token,
                "cookie": self.cookie,
                "extra": self.extra,
                "status": self.status,
                "lastError": self.lastError,
                "createdAt": self.createdAt,
                "updatedAt": self.updatedAt,
            }

    def fake_validate_profile_object(profile_obj: object):
        return {
            "ok": True,
            "profileId": profile_obj.profileId,
            "providerKey": profile_obj.providerKey,
            "providerDisplayName": profile_obj.displayName,
            "mode": "live",
            "status": 200,
            "error": "",
            "summary": "save-time validation ok",
            "checkedAt": "2026-05-23T00:00:00+00:00",
            "checks": [{"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}],
            "parentId": "0",
            "fileId": "file-1",
        }

    def fake_run_provider_live_probe_for_profile(profile: object, parent_id: str = "", file_id: str = "", page_size: int = 100, dir_name: str = ""):
        return {
            "ok": True,
            "profileId": profile.profileId,
            "providerKey": profile.providerKey,
            "mode": "live",
            "summary": "save-time validation ok",
            "checks": [
                {"kind": "list", "ok": True, "status": 200, "error": "", "note": "list ok"}
            ],
        }

    with patched_attr(webapp, "ADMIN_PASSWORD", "admin123"):
        with patched_attr(webapp, "build_profile", lambda payload: FakeProfile(payload)):
            with patched_attr(webapp, "update_profile", lambda profile_obj: created_profiles.append(profile_obj)):
                with patched_attr(webapp, "append_live_validation", lambda row: api_saved_rows.append(row) or row):
                    with patched_attr(auth_live_validate, "run_provider_live_probe_for_profile", fake_run_provider_live_probe_for_profile):
                        app = webapp.create_app()
                        client = TestClient(app)
                        client.post("/api/login", json={"password": "admin123"})
                        api_response = client.post(
                            "/api/auth/profiles",
                            json={
                                "providerKey": "123_open",
                                "authMode": "manual_token",
                                "displayName": "save-test",
                                "token": "tok-demo",
                                "cookie": "",
                                "extra": {"parentFileId": "0", "fileId": "file-1"},
                            },
                        ).json()
                        with patched_attr(webapp, "list_live_validations", lambda: [{"profileId": "p1", "providerKey": "guangya"}, {"profileId": "p1", "providerKey": "guangya"}, {"profileId": "p2", "providerKey": "123_open"}]):
                            with patched_attr(webapp, "latest_live_validations", lambda: [{"profileId": "p1", "providerKey": "guangya"}, {"profileId": "p2", "providerKey": "123_open"}]):
                                with patched_attr(webapp, "live_validation_summary", lambda: {"profileCount": 2, "okCount": 1, "failedCount": 1, "okProfiles": ["guangya-main"], "failedProfiles": ["123-open-main"], "providerKeys": ["123_open", "guangya"]}):
                                    validations_response = client.get("/api/auth/live_validations").json()
                        with patched_attr(webapp, "list_provider_live_probes", lambda: [{"profileId": "p1", "providerKey": "guangya"}, {"profileId": "p1", "providerKey": "guangya"}, {"profileId": "p2", "providerKey": "123_open"}]):
                            with patched_attr(webapp, "latest_provider_live_probes", lambda: [{"profileId": "p1", "providerKey": "guangya"}, {"profileId": "p2", "providerKey": "123_open"}]):
                                with patched_attr(webapp, "provider_live_probe_summary", lambda: {"profileCount": 2, "okCount": 0, "failedCount": 2, "okProfiles": [], "failedProfiles": ["p1", "p2"], "providerKeys": ["123_open", "guangya"]}):
                                    probes_response = client.get("/api/providers/live_probe_results").json()

    print(
        json.dumps(
            {
                "single": {
                    "ok": single.get("ok"),
                    "providerKey": single.get("providerKey"),
                    "mode": single.get("mode"),
                    "status": single.get("status"),
                    "error": single.get("error"),
                    "summary": single.get("summary"),
                    "checkCount": len(single.get("checks") or []),
                    "parentId": single.get("parentId"),
                    "fileId": single.get("fileId"),
                },
                "batch": {
                    "totalProfiles": batch.get("totalProfiles"),
                    "okProfiles": batch.get("okProfiles"),
                    "failedProfiles": batch.get("failedProfiles"),
                },
                "savedRowCount": len(saved_rows),
                "saveApi": {
                    "status": api_response.get("item", {}).get("status"),
                    "lastError": api_response.get("item", {}).get("lastError"),
                    "validationOk": api_response.get("validation", {}).get("ok"),
                    "savedProfileCount": len(created_profiles),
                    "savedValidationCount": len(api_saved_rows),
                },
                "listApis": {
                    "authHistoryCount": len(validations_response.get("items") or []),
                    "authLatestCount": len(validations_response.get("latestItems") or []),
                    "authSummaryProfiles": (validations_response.get("summary") or {}).get("profileCount"),
                    "authSummaryOkProfiles": (validations_response.get("summary") or {}).get("okProfiles"),
                    "authSummaryFailedProfiles": (validations_response.get("summary") or {}).get("failedProfiles"),
                    "probeHistoryCount": len(probes_response.get("items") or []),
                    "probeLatestCount": len(probes_response.get("latestItems") or []),
                    "probeSummaryProfiles": (probes_response.get("summary") or {}).get("profileCount"),
                    "probeSummaryOkProfiles": (probes_response.get("summary") or {}).get("okProfiles"),
                    "probeSummaryFailedProfiles": (probes_response.get("summary") or {}).get("failedProfiles"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
