# StayGrid Hotel Management System

StayGrid is a hotel discovery and reservation project. The backend provides a FastAPI application with SQLite persistence, account registration and login, hotel search, room availability, customer bookings and cancellations, and administrator management for hotels, rooms, and bookings.

## Backend

See [backend/README.md](backend/README.md) for setup, administrator provisioning, the complete API endpoint list, response examples, and Swagger UI instructions.

From the `backend` directory, install dependencies with `uv sync` and run the API with `uv run fastapi dev main.py`. Swagger UI is available at `http://127.0.0.1:8000/docs`.

## Project layout

- `backend/` - FastAPI application and database
- `frontend/` - Vite and React frontend
