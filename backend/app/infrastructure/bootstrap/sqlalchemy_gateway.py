"""Gateway concreto de infraestructura para `bootstrap`."""

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserRole


class SqlAlchemySuperadminGateway:
    def __init__(self, db: Session) -> None:
        self._db = db

    def ensure_superadmin(
        self,
        email: str,
        name: str,
        password: str | None,
        force_password_reset: bool,
    ) -> str:
        user = self._db.scalar(select(User).where(User.email == email))

        if user:
            changed = False
            if user.role != UserRole.SUPERADMIN:
                user.role = UserRole.SUPERADMIN
                changed = True
            if not user.is_active:
                user.is_active = True
                changed = True
            if password and (not user.password or force_password_reset):
                user.password = hash_password(password)
                changed = True

            if changed:
                self._db.flush()
            if changed:
                return 'updated'
            return 'unchanged'

        if not password:
            return 'missing_password'

        self._db.add(
            User(
                id=str(uuid4()),
                name=name,
                email=email,
                password=hash_password(password),
                role=UserRole.SUPERADMIN,
                position='Superadmin',
                is_active=True,
            )
        )
        self._db.flush()
        return 'created'
