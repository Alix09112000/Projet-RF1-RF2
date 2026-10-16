from collections.abc import Callable
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import read_token
from app.db import get_db
from app.models import Role, User

DB = Annotated[Session, Depends(get_db)]


def get_current_user(db: DB, rf_session: Annotated[str | None, Cookie()] = None) -> User:
    user_id = read_token(rf_session) if rf_session else None
    user = db.get(User, user_id) if user_id is not None else None
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session absente ou expirée")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: Role) -> Callable[[User], User]:
    """Dépendance qui laisse passer seulement les rôles indiqués."""

    def dependency(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès réservé")
        return user

    return dependency
