from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import current_user
from app.core.config import ADMIN_SIGNUP_CODE
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.schemas import AdminRegisterInput, ForgotPasswordInput, HotelAdminRegisterInput, LoginInput, RegisterInput, ResetPasswordInput

router = APIRouter()


def _assign_role(db, user_id: int, role: str) -> None:
    db.execute("INSERT IGNORE INTO user_roles(user_id,role_id) SELECT ?,id FROM roles WHERE name=?", (user_id, role))


@router.post("/register", status_code=201, summary="Register a customer account", responses={409: {"description": "Email already registered"}})
def register(payload: RegisterInput, db=Depends(get_db)):
    cursor = db.execute("INSERT INTO users(name,email,password_hash,role,account_status) VALUES(?,?,?,'user','active')",
                        (payload.name, payload.email.lower(), hash_password(payload.password)))
    _assign_role(db, cursor.lastrowid, "user")
    return {"id": cursor.lastrowid, "name": payload.name, "email": payload.email.lower(), "role": "user"}


@router.post("/hotel-admin/register", status_code=201, summary="Apply for a hotel administrator account")
def register_hotel_admin(payload: HotelAdminRegisterInput, db=Depends(get_db)):
    cursor = db.execute("INSERT INTO users(name,email,password_hash,role,account_status,business_name,phone) VALUES(?,?,?,'hotel_admin','pending',?,?)",
                        (payload.name, payload.email.lower(), hash_password(payload.password), payload.business_name, payload.phone))
    _assign_role(db, cursor.lastrowid, "hotel_admin")
    return {"id": cursor.lastrowid, "name": payload.name, "email": payload.email.lower(), "role": "hotel_admin", "account_status": "pending"}


@router.post("/admin/register", status_code=201, summary="Create an admin account with the configured invite code")
def register_admin(payload: AdminRegisterInput, db=Depends(get_db)):
    if not ADMIN_SIGNUP_CODE or not secrets.compare_digest(payload.admin_code, ADMIN_SIGNUP_CODE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin invite code")
    cursor = db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'admin') ON DUPLICATE KEY UPDATE name=VALUES(name),password_hash=VALUES(password_hash),role='admin'",
                        (payload.name, payload.email.lower(), hash_password(payload.password)))
    user = db.execute("SELECT id FROM users WHERE email=?", (payload.email.lower(),)).fetchone()
    _assign_role(db, user["id"], "admin")
    return {"id": cursor.lastrowid, "name": payload.name, "email": payload.email.lower(), "role": "admin"}


@router.post("/login", summary="Log in and receive a bearer token")
def login(payload: LoginInput, db=Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE email=?", (payload.email.lower(),)).fetchone()
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if user["account_status"] == "pending":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your hotel administrator application is awaiting admin approval")
    if user["account_status"] in {"blocked", "suspended"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is suspended or blocked")
    return {"access_token": create_access_token(user["id"], user["role"]), "token_type": "bearer",
            "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}}


@router.post("/forgot-password", summary="Create a short-lived password reset token")
def forgot_password(payload: ForgotPasswordInput, db=Depends(get_db)):
    user = db.execute("SELECT id FROM users WHERE email=?", (payload.email.lower(),)).fetchone()
    response = {"message": "If an account exists for that email, a reset link has been created."}
    if not user:
        return response
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires = (datetime.now(timezone.utc) + timedelta(minutes=15)).replace(tzinfo=None)
    db.execute("UPDATE password_reset_tokens SET used_at=NOW() WHERE user_id=? AND used_at IS NULL", (user["id"],))
    db.execute("INSERT INTO password_reset_tokens(user_id,token_hash,expires_at) VALUES(?,?,?)", (user["id"], token_hash, expires))
    # The token is returned for this local application; production should email it instead.
    response["reset_token"] = raw_token
    return response


@router.post("/reset-password", summary="Set a new password using a reset token")
def reset_password(payload: ResetPasswordInput, db=Depends(get_db)):
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    row = db.execute("SELECT id,user_id FROM password_reset_tokens WHERE token_hash=? AND used_at IS NULL AND expires_at>NOW()", (token_hash,)).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token is invalid or expired")
    db.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(payload.password), row["user_id"]))
    db.execute("UPDATE password_reset_tokens SET used_at=NOW() WHERE id=?", (row["id"],))
    return {"message": "Password reset successfully. You can now sign in."}


@router.get("/me", summary="Get the current account")
def me(user=Depends(current_user)):
    return user
