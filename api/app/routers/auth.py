from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.auth.deps import DB, CurrentUser
from app.auth.security import COOKIE_NAME, create_token, verify_password
from app.config import settings
from app.models import User
from app.schemas import LoginIn, UserOut

router = APIRouter(prefix="/auth", tags=["authentification"])


@router.post("/login", response_model=UserOut)
def login(body: LoginIn, response: Response, db: DB) -> User:
    email = body.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiant ou mot de passe incorrect")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiant ou mot de passe incorrect")
    response.set_cookie(
        COOKIE_NAME,
        create_token(user.id),
        max_age=settings.session_hours * 3600,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    return user
