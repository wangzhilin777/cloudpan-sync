# CloudPan Sync

CloudPan Sync is a transfer console between mainstream cloud providers.

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
cloudpan-sync
```

Open `http://127.0.0.1:8765`.

## Default Admin Password

Use environment variable `CLOUDPAN_SYNC_ADMIN_PASSWORD`.

If missing, default password is `admin123`.
