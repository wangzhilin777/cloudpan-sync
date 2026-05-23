from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import auth_live_validate
from cloudpan_sync.auth_profile_patch import configure_data_dir, patch_auth_profiles


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        data_dir = Path(tmp_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        auth_file = data_dir / "auth_profiles.json"
        auth_file.write_text(
            json.dumps(
                [
                    {
                        "profileId": "gy-smoke-1",
                        "providerKey": "guangya",
                        "authMode": "manual_token",
                        "displayName": "smoke-guangya",
                        "token": "tok_smoke",
                        "cookie": "",
                        "extra": {},
                        "status": "invalid",
                        "lastError": "missing_parent_id",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                    {
                        "profileId": "ali-smoke-1",
                        "providerKey": "aliyundrive_open",
                        "authMode": "manual_token",
                        "displayName": "smoke-aliyun",
                        "token": "tok_aliyun",
                        "cookie": "",
                        "extra": {"domainId": "d-1"},
                        "status": "saved",
                        "lastError": "",
                        "createdAt": "2026-05-23T00:00:00+00:00",
                        "updatedAt": "2026-05-23T00:00:00+00:00",
                    },
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        configure_data_dir(data_dir)

        original_validate = auth_live_validate.validate_profile_object
        original_append = auth_live_validate.append_live_validation
        captured_validations: list[dict[str, object]] = []

        def fake_validate(profile: object) -> dict[str, object]:
            parent_id = str((getattr(profile, "extra", {}) or {}).get("parentId") or "")
            return {
                "ok": bool(parent_id),
                "profileId": getattr(profile, "profileId", ""),
                "providerKey": getattr(profile, "providerKey", ""),
                "providerDisplayName": getattr(profile, "displayName", ""),
                "mode": "live",
                "status": 200 if parent_id else 400,
                "error": "" if parent_id else "missing_parent_id",
                "summary": "patched validation ok" if parent_id else "patched validation failed",
                "checkedAt": "2026-05-23T00:00:00+00:00",
                "checks": [{"kind": "list", "ok": bool(parent_id), "status": 200 if parent_id else 400, "error": "" if parent_id else "missing_parent_id", "note": ""}],
                "parentId": parent_id,
                "fileId": str((getattr(profile, "extra", {}) or {}).get("fileId") or ""),
                "riskHint": "",
                "requiredFieldHints": [] if parent_id else ["extra.parentId"],
            }

        def fake_append(row: dict[str, object]) -> dict[str, object]:
            captured_validations.append(row)
            validation_file = data_dir / "auth_live_validations.json"
            existing = []
            if validation_file.exists():
                existing = json.loads(validation_file.read_text(encoding="utf-8"))
            existing.append(row)
            validation_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
            return row

        auth_live_validate.validate_profile_object = fake_validate
        auth_live_validate.append_live_validation = fake_append
        try:
            result = patch_auth_profiles(
                extra_updates={"parentId": "dir-100", "fileId": "file-9"},
                profile_ids=["gy-smoke-1"],
                write=True,
                revalidate=True,
            )
        finally:
            auth_live_validate.validate_profile_object = original_validate
            auth_live_validate.append_live_validation = original_append

        profiles = json.loads(auth_file.read_text(encoding="utf-8"))
        target = next(item for item in profiles if item["profileId"] == "gy-smoke-1")
        untouched = next(item for item in profiles if item["profileId"] == "ali-smoke-1")
        validations = json.loads((data_dir / "auth_live_validations.json").read_text(encoding="utf-8"))
        print(
            json.dumps(
                {
                    "matchedCount": result["matchedCount"],
                    "writtenCount": result["writtenCount"],
                    "revalidatedCount": result["revalidatedCount"],
                    "targetProfile": {
                        "parentId": target["extra"].get("parentId", ""),
                        "fileId": target["extra"].get("fileId", ""),
                        "status": target["status"],
                        "lastError": target["lastError"],
                    },
                    "untouchedProfile": {
                        "profileId": untouched["profileId"],
                        "extra": untouched["extra"],
                        "status": untouched["status"],
                    },
                    "validationCount": len(validations),
                    "validationProfileIds": [row.get("profileId", "") for row in validations],
                    "changedKeys": ((result.get("items") or [{}])[0]).get("changedKeys", []),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
