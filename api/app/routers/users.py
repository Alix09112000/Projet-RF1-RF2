from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.auth.deps import DB, require_roles
from app.auth.security import hash_password
from app.models import Role, User
from app.schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["utilisateurs"])

Admin = Annotated[User, Depends(require_roles(Role.admin))]


@router.get("", response_model=list[UserOut])
def list_users(_: Admin, db: DB) -> list[User]:
    return list(db.scalars(select(User).order_by(User.full_name)))


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, _: Admin, db: DB) -> User:
    email = body.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Un compte existe déjà avec cet identifiant"
        )
    user = User(
        email=email,
        full_name=body.full_name.strip(),
        password_hash=hash_password(body.password),
        role=body.role,
        direction=body.direction,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
