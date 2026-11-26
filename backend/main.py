"""StayGrid hotel reservation API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.errors import register_exception_handlers
from app.db.database import initialize_database

app = FastAPI(
    title="StayGrid Hotel API",
    description=(
        "Hotel discovery and reservation API. Use `/api/v1/auth/register` and "
        "`/api/v1/auth/login` to obtain a bearer token, then authorize it in Swagger UI. "
        "Admin routes require an account provisioned with the `ADMIN_EMAIL` and "
        "`ADMIN_PASSWORD` environment variables on first startup."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
register_exception_handlers(app)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health", tags=["health"], summary="Check API health")
def health() -> dict[str, str]:
    return {"status": "ok"}
