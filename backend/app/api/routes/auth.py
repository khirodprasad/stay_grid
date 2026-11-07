from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.schemas import LoginInput, RegisterInput

router = APIRouter()


@router.post("/register", status_code=201, summary="Register a customer account", responses={409: {"description": "Email already registered"}})
def register(payload: RegisterInput, db=Depends(get_db)):
    cursor = db.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                        (payload.name, payload.email.lower(), hash_password(payload.password)))
    return {"id": cursor.lastrowid, "name": payload.name, "email": payload.email.lower(), "role": "customer"}


@router.post("/login", summary="Log in and receive a bearer token")
def login(payload: LoginInput, db=Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE email=?", (payload.email,)).fetchone()
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return {"access_token": create_access_token(user["id"], user["role"]), "token_type": "bearer",
            "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}}


@router.get("/me", summary="Get the current account")
def me(user=Depends(current_user)):
    return user
