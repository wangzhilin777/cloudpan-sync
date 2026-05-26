from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync import auth_store, task_runtime_evidence_store, webapp
from cloudpan_sync.models import AuthProfileInput


def main() -> None:
    original_password = webapp.ADMIN_PASSWORD
    original_runtime_file = task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE
    original_auth_file = auth_store.AUTH_FILE
    try:
        with TemporaryDirectory() as tmp_dir:
            task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = Path(tmp_dir) / "task_runtime_evidence.json"
            auth_store.AUTH_FILE = Path(tmp_dir) / "auth_profiles.json"
            auth_store.save_profile(
                AuthProfileInput(
                    providerKey="guangya",
                    authMode="manual_token",
                    displayName="Guangya Existing Profile",
                    token="demo-token",
                ),
                profile_id_override="gy-1",
            )
            task_runtime_evidence_store.save_task_runtime_evidence(
                {
                    "taskId": "task-1",
                    "providerKey": "guangya",
                    "profileId": "gy-1",
                    "path": "/demo.bin",
                    "mode": "binary_upload_multipart",
                    "executionMode": "live",
                    "success": True,
                    "verifyOk": True,
                    "verifyMode": "list_by_parent_name",
                    "verifyNote": "verified by list",
                    "conflictPolicy": "overwrite_existing",
                    "conflictAction": "overwrite_downgraded_to_auto_rename",
                    "resolvedTargetName": "demo (1).bin",
                    "riskHint": "fallback upload required",
                    "savedAt": "2026-05-24T00:00:00+00:00",
                }
            )
            task_runtime_evidence_store.save_task_runtime_evidence(
                {
                    "taskId": "task-2",
                    "providerKey": "189cloud",
                    "profileId": "189-1",
                    "path": "/large.iso",
                    "mode": "download_upload_blocked_by_size_limit",
                    "executionMode": "blocked",
                    "success": False,
                    "verifyOk": False,
                    "verifyMode": "",
                    "verifyNote": "blocked before verification",
                    "conflictPolicy": "auto_rename_new",
                    "conflictAction": "",
                    "resolvedTargetName": "large.iso",
                    "riskHint": "download_upload_size_limit_exceeded",
                    "error": "download_upload_blocked_by_size_limit",
                    "savedAt": "2026-05-25T00:00:00+00:00",
                }
            )
            task_runtime_evidence_store.save_task_runtime_evidence(
                {
                    "taskId": "task-3",
                    "providerKey": "quark",
                    "profileId": "quark-1",
                    "path": "/movie.mkv",
                    "mode": "quark_fast_upload_candidate",
                    "executionMode": "probe",
                    "candidateOnly": True,
                    "success": True,
                    "verifyOk": False,
                    "verifyMode": "fingerprint_candidate",
                    "verifyNote": "candidate only",
                    "conflictPolicy": "auto_rename_new",
                    "conflictAction": "",
                    "resolvedTargetName": "movie.mkv",
                    "riskHint": "",
                    "savedAt": "2026-05-25T01:00:00+00:00",
                }
            )
            payload = task_runtime_evidence_store.build_task_runtime_evidence_payload()
            markdown = task_runtime_evidence_store.task_runtime_evidence_to_markdown(payload)

            webapp.ADMIN_PASSWORD = "admin123"
            app = webapp.create_app()
            client = TestClient(app)
            login = client.post("/api/login", json={"password": "admin123"})
            assert login.status_code == 200, login.text
            api_payload = client.get("/api/task_runtime_evidence").json()
            api_markdown = client.get("/api/task_runtime_evidence_markdown").json()

            print(
                json.dumps(
                    {
                        "apiTaskRuntimeEvidenceMatchesSeededSummary": (
                            dict(payload.get("summary") or {}).get("sampleCount") == 3
                            and dict(payload.get("summary") or {}).get("providerCount") == 3
                            and dict(payload.get("summary") or {}).get("successProviderCount") == 1
                            and dict(payload.get("summary") or {}).get("failedProviderCount") == 1
                            and dict(payload.get("summary") or {}).get("candidateProviderCount") == 1
                            and dict(payload.get("summary") or {}).get("blockedProviderCount") == 1
                            and dict(payload.get("summary") or {}).get("conflictHandledProviderCount") == 1
                            and dict(payload.get("summary") or {}).get("runtimeOrphanProviderCount") == 2
                            and dict(payload.get("summary") or {}).get("runtimeOrphanProfileCount") == 2
                            and dict(payload.get("summary") or {}).get("successProfiles") == ["gy-1"]
                            and dict(payload.get("summary") or {}).get("failedProfiles") == ["189-1"]
                            and dict(payload.get("summary") or {}).get("candidateProfiles") == ["quark-1"]
                            and dict(payload.get("summary") or {}).get("blockedProfiles") == ["189-1"]
                            and dict(payload.get("summary") or {}).get("conflictHandledProfiles") == ["gy-1"]
                            and ((payload.get("latestItems") or [None])[0] or {}).get("providerKey") == "guangya"
                            and ((payload.get("latestItems") or [None])[0] or {}).get("verifyMode") == "list_by_parent_name"
                            and api_payload.get("summary") == payload.get("summary")
                            and "# CloudPan Sync 任务运行真实样本报告" in str(api_markdown.get("markdown") or "")
                        ),
                        "summary": payload.get("summary"),
                        "firstLatestItem": ((payload.get("latestItems") or [None])[0]),
                        "markdownHasTitle": "# CloudPan Sync 任务运行真实样本报告" in markdown,
                        "markdownHasConflictHandledProviderCount": "conflictHandledProviderCount=1" in markdown,
                        "markdownHasRuntimeOrphanCounts": "runtimeOrphanProviderCount=2" in markdown and "runtimeOrphanProfileCount=2" in markdown,
                        "markdownHasSuccessFailedProviderCount": "successProviderCount=1" in markdown and "failedProviderCount=1" in markdown and "candidateProviderCount=1" in markdown,
                        "markdownHasBlockedCounts": "blockedProviderCount=1" in markdown and "blockedCount=1" in markdown,
                        "markdownHasProfileSummary": "profileSummary:" in markdown
                        and "`success=gy-1`" in markdown
                        and "`failed=189-1`" in markdown
                        and "`candidate=quark-1`" in markdown
                        and "`probe=(none)`" in markdown
                        and "`blocked=189-1`" in markdown
                        and "`conflictHandled=gy-1`" in markdown
                        and "`runtimeOrphan=189-1, quark-1`" in markdown,
                        "markdownHasExecutionMode": "executionMode=blocked" in markdown and "executionMode=live" in markdown,
                        "markdownHasCandidateOnly": "candidateOnly=True" in markdown and "candidateCount=1" in markdown,
                        "markdownHasOrphanProfileIds": "orphanProfileId=(none)" in markdown and "orphanProfileId=189-1" in markdown and "orphanProfileId=quark-1" in markdown,
                        "markdownHasRiskHint": "riskHint=fallback upload required" in markdown and "riskHint=download_upload_size_limit_exceeded" in markdown,
                        "markdownHasVerifyNote": "verifyNote=verified by list" in markdown and "verifyNote=blocked before verification" in markdown,
                        "apiSummary": api_payload.get("summary"),
                        "apiMarkdownHasTitle": "# CloudPan Sync 任务运行真实样本报告" in str(api_markdown.get("markdown") or ""),
                        "apiMarkdownHasProfileSummary": "profileSummary:" in str(api_markdown.get("markdown") or "") and "`failed=189-1`" in str(api_markdown.get("markdown") or "") and "`runtimeOrphan=189-1, quark-1`" in str(api_markdown.get("markdown") or ""),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
    finally:
        webapp.ADMIN_PASSWORD = original_password
        task_runtime_evidence_store.RUNTIME_EVIDENCE_FILE = original_runtime_file
        auth_store.AUTH_FILE = original_auth_file


if __name__ == "__main__":
    main()
