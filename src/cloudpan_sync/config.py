from __future__ import annotations

import os


HOST = os.getenv("CLOUDPAN_SYNC_HOST", "127.0.0.1")
PORT = int(os.getenv("CLOUDPAN_SYNC_PORT", "8765"))
ADMIN_PASSWORD = os.getenv("CLOUDPAN_SYNC_ADMIN_PASSWORD", "admin123")
SESSION_SECRET = os.getenv("CLOUDPAN_SYNC_SESSION_SECRET", "cloudpan-sync-dev-secret")
SESSION_COOKIE = "cloudpan_sync_session"
