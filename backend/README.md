# StayGrid API

FastAPI backend for hotel search, room availability, reservations, and administrator management. The API uses MySQL and publishes interactive API documentation at `/docs`.

## Run locally

From this directory, install the project with `uv sync` and start the development server with `uv run uvicorn main:app --host 127.0.0.1 --port 8001`. The API listens at `http://127.0.0.1:8001`.

The backend loads these settings from `backend/.env` using `python-dotenv`: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` (defaults: `127.0.0.1`, `3306`, `root`, empty password, and `staygrid`). The database is created automatically when the MySQL user has permission to create databases. Copy `.env.example` to `.env` and use private values outside local development. Before deployment, set a long, random `TOKEN_SECRET`. Access tokens last one hour by default; set `TOKEN_TTL_SECONDS` to change that.

Create a MySQL user/database manually when automatic creation is not permitted:

```sql
CREATE DATABASE staygrid CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'staygrid'@'localhost' IDENTIFIED BY 'change-this-password';
GRANT ALL PRIVILEGES ON staygrid.* TO 'staygrid'@'localhost';
FLUSH PRIVILEGES;
```

Then configure the backend before startup:

```powershell
$env:MYSQL_USER="staygrid"
$env:MYSQL_PASSWORD="change-this-password"
$env:MYSQL_DATABASE="staygrid"
```

To provision the first administrator, set `ADMIN_EMAIL` and `ADMIN_PASSWORD` before the first startup. The account is created once if that email is not already registered. Public registration always creates a customer account. Do not use a default or shared administrator password.

## Swagger UI

Open `http://127.0.0.1:8001/docs` after starting the server.

1. Call `POST /api/v1/auth/register` with `name`, `email`, and a password of at least eight characters.
2. Call `POST /api/v1/auth/login` and copy `access_token` from the response.
3. Select **Authorize** and enter the token. Swagger's bearer scheme adds the `Bearer` prefix.
4. Try hotel search, room availability, bookings, and cancellation. Admin endpoints require the provisioned administrator account.

## Endpoints

All application routes are prefixed with `/api/v1`. Successful JSON responses are returned directly; errors use a `detail` string, and request validation errors also include an `errors` array of field/message objects.

| Method | Path | Access | Result |
|---|---|---|---|
| GET | `/health` | Public | `{"status":"ok"}` |
| POST | `/auth/register` | Public | New customer account; `201` |
| POST | `/auth/login` | Public | Access token and account |
| GET | `/auth/me` | Customer or admin | Current account |
| GET | `/hotels` | Public | Paginated hotel list; filters: `city`, `q`, `check_in`, `check_out`, `guests` |
| GET | `/categories` | Public | MySQL-backed product categories with live counts |
| GET | `/hotels/{hotel_id}` | Public | Hotel details and its rooms |
| GET | `/rooms/availability` | Public | Available rooms for date range, guest count, and optional hotel |
| GET | `/rooms/{room_id}` | Public | Room and hotel details |
| POST | `/bookings` | Customer or admin | Create a confirmed booking; `201` |
| GET | `/bookings` | Customer or admin | Current user's bookings |
| DELETE | `/bookings/{booking_id}` | Owner or admin | Cancel a confirmed booking |
| POST | `/admin/hotels` | Admin | Create a hotel; `201` |
| PUT | `/admin/hotels/{hotel_id}` | Admin | Replace hotel details |
| DELETE | `/admin/hotels/{hotel_id}` | Admin | Deactivate a hotel |
| GET | `/admin/room-types` | Admin | List room types |
| POST | `/admin/room-types` | Admin | Create a room type; `201` |
| POST | `/admin/rooms` | Admin | Create a room; `201` |
| PUT | `/admin/rooms/{room_id}` | Admin | Replace room details |
| DELETE | `/admin/rooms/{room_id}` | Admin | Deactivate a room |
| GET | `/admin/bookings` | Admin | List bookings; optional `status` filter |
| PATCH | `/admin/bookings/{booking_id}/status?status=...` | Admin | Set booking status |

## Response and error examples

Login response:

```json
{
  "access_token": "<signed-token>",
  "token_type": "bearer",
  "user": {"id": 1, "name": "A Guest", "email": "guest@example.com", "role": "customer"}
}
```

Booking response:

```json
{
  "id": 1,
  "room_id": 3,
  "check_in": "2030-06-10",
  "check_out": "2030-06-12",
  "guests": 2,
  "total_amount": 240.0,
  "status": "confirmed"
}
```

Validation error (`422`):

```json
{
  "detail": "Request validation failed",
  "errors": [{"field": "body.email", "message": "value is not a valid email address"}]
}
```

Other common responses: `401` for missing/invalid credentials, `403` for non-admin access to admin routes, `404` for unknown or inaccessible resources, `409` for duplicate data or unavailable rooms, and `422` for invalid input. Booking creation checks date overlaps inside a write transaction to prevent double booking.
