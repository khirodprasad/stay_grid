# StayGrid Project Documentation

## Overview

StayGrid is a hotel discovery and reservation system with a React/Vite frontend and a FastAPI/MySQL backend.

## Project structure

- `frontend/` - React user interface.
- `frontend/src/App.tsx` - Main frontend experience.
- `frontend/src/App.css` - StayGrid layout and styling.
- `backend/` - FastAPI application.
- `backend/app/api/routes/` - Authentication, hotel, room, booking, and admin routes.
- `backend/app/schemas.py` - Request validation models.
- `backend/app/db/database.py` - MySQL connection and schema initialization.
- `backend/app/core/security.py` - Password hashing and access tokens.

## Local setup

Start the backend from `backend/`:

```powershell
$env:ADMIN_EMAIL="admin@example.com"
$env:ADMIN_PASSWORD="AdminPass!234"
uv run fastapi dev main.py --host 127.0.0.1 --port 8000
```

Start the frontend from `frontend/` in a second terminal:

```powershell
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Local URLs:

- Frontend: http://127.0.0.1:5173/
- API: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs

The frontend uses `VITE_API_URL` when set. Otherwise it uses `http://127.0.0.1:8000/api/v1`.

## Main API capabilities

- Customer registration, login, and current-user profile.
- Hotel listing, search, and details.
- Room details and date-based availability.
- Room booking, booking history, and cancellation.
- Admin hotel creation, updates, and deactivation.
- Admin room-type and room management.
- Admin booking listing and status management.

All application endpoints use the `/api/v1` prefix. Admin routes require an account with the `admin` role.

## Configuration

- `ADMIN_EMAIL` and `ADMIN_PASSWORD` provision the first local admin account.
- `TOKEN_SECRET` signs access tokens and should be changed outside development.
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` configure MySQL.
- `VITE_API_URL` changes the frontend API base URL.

Backend environment values are stored in `backend/.env`; use `backend/.env.example` as the template. The real `.env` file is ignored by Git.

## Verification

Build the frontend:

```powershell
cd frontend
npm run build
```

Use Swagger UI to verify authentication, hotel search, room availability, booking, cancellation, and admin flows.

## Development rules

- Keep booking overlap checks transactional.
- Use the shared frontend request helper for API calls and bearer tokens.
- Return clear validation and authorization errors.
- Do not commit credentials, customer data, databases, `__pycache__`, or `.venv`.
