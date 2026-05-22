# Completed Milestones

> This file tracks completed milestones only.

## Milestone List

### M1 - Independent Skeleton

- Completed on: 2026-05-23
- Scope:
  - FastAPI backend and static web skeleton
  - Local admin password login guard
  - CN/EN i18n base API and UI toggle
  - Windows launcher scripts (`pwsh` preferred with PowerShell fallback)
- Verification evidence:
  - `GET /api/health` on `http://127.0.0.1:8876` returned `{"status":"ok"}`
  - `POST /api/login` with default password succeeded
  - `GET /api/session` after login returned `{"loggedIn":true}`

### M2 - Adapter and Capability Model

- Completed on: 2026-05-23
- Scope:
  - `ProviderAdapter` abstraction and provider profile model
  - Provider registry API with first-wave provider metadata
  - Mock transfer planner API for source/target strategy output
- Verification evidence:
  - `GET /api/providers` returned provider capability list
  - `POST /api/plan/mock` (after login) returned per-file strategies with summary counts

### M3 - Auth System

- Completed on: 2026-05-23
- Scope:
  - `AuthProfile` model and local auth profile store
  - Auth profile APIs: create/list/delete/validate
  - Web login capture starter API (`capture_pending` guidance flow)
  - Auth management UI panel in `Auth` tab
- Verification evidence:
  - `POST /api/auth/profiles` returned masked token (e.g. `tok_***56`)
  - `GET /api/auth/profiles` returned profile list for current session
  - `POST /api/auth/profiles/{id}/validate` changed status to `verified`
  - `POST /api/auth/capture/start` returned `capture_pending`
  - `DELETE /api/auth/profiles/{id}` succeeded and list count returned to `0`

### M4 - Guangya Provider Foundation

- Completed on: 2026-05-23
- Scope:
  - Added Guangya hash normalization and precheck logic (`md5` / `gcid`)
  - Added Guangya provider APIs:
    - `POST /api/providers/guangya/list` (mock list for local flow)
    - `POST /api/providers/guangya/fast_check` (local precheck with risk hints)
  - Added explicit notes that this milestone is local/mock precheck only (not full live Guangya API binding)
- Verification evidence:
  - `POST /api/providers/guangya/list` returned `mode=mock` with item list
  - `POST /api/providers/guangya/fast_check` returned mixed results:
    - supported (`md5` / `gcid`) entries
    - unsupported entry when fast-upload fingerprints are missing
