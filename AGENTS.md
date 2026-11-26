# StayGrid agent rules

## Commands

Backend (`backend/`):

```powershell
uv run fastapi dev main.py --host 127.0.0.1 --port 8000
```

Frontend (`frontend/`):

```powershell
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

See `docs/PROJECT_DOCUMENTATION.md` for architecture, endpoints, configuration, and setup details.

Keep backend routes in `backend/app/api/routes/`, use `/api/v1`, preserve transactional booking checks, and use the shared frontend auth request helper. Do not commit credentials, databases, `__pycache__`, or `.venv`.

## Verify

```powershell
cd frontend
npm run build
```
