from mysql.connector import Error, IntegrityError

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_error(_: Request, exc: RequestValidationError):
        errors = [{"field": ".".join(str(part) for part in item["loc"]), "message": item["msg"]}
                  for item in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": "Request validation failed", "errors": errors})

    @app.exception_handler(IntegrityError)
    async def integrity_error(_: Request, exc: IntegrityError):
        message = "The requested change conflicts with existing data."
        if getattr(exc, "errno", None) == 1062 and "email" in str(exc).lower():
            message = "An account with this email already exists."
        elif getattr(exc, "errno", None) == 1062 and "uq_room_number" in str(exc):
            message = "That room number already exists in this hotel."
        return JSONResponse(status_code=409, content={"detail": message})

    @app.exception_handler(Error)
    async def database_error(_: Request, exc: Error):
        return JSONResponse(status_code=500, content={"detail": "A database error occurred."})
