"""Adaptador de infraestructura para `users` (persistencia concreta)."""

from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.domain.users.entities import PermissionInput, UserData, UserPermissionData, UserSelectData
from app.domain.users.read_models import UserUpdatePayload
from app.models.user import User, UserPermission, UserRole


class SqlAlchemyUsersRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_select(self) -> list[UserSelectData]:
        users = self._db.scalars(select(User).where(User.is_active.is_(True)).order_by(User.name.asc())).all()
        return [UserSelectData(id=user.id, name=user.name, email=user.email, image=user.image) for user in users]

    def list_all(self) -> list[UserData]:
        users = self._db.scalars(select(User).order_by(User.created_at.desc())).unique().all()
        return [self._to_entity(user) for user in users]

    def find_by_id(self, user_id: str) -> UserData | None:
        user = self._db.scalar(select(User).where(User.id == user_id))
        if not user:
            return None
        return self._to_entity(user)

    def exists_by_email(self, email: str, exclude_user_id: str | None = None) -> bool:
        stmt = select(User).where(User.email == email)
        if exclude_user_id:
            stmt = stmt.where(User.id != exclude_user_id)
        return self._db.scalar(stmt) is not None

    def create_user(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: str,
        position: str | None,
        is_active: bool,
        permissions: list[PermissionInput],
    ) -> str:
        user = User(
            id=str(uuid4()),
            name=name,
            email=email,
            password=password_hash,
            role=UserRole(role),
            position=position,
            is_active=is_active,
        )
        self._db.add(user)
        self._db.flush()

        for perm in permissions:
            self._db.add(
                UserPermission(
                    id=str(uuid4()),
                    user_id=user.id,
                    module=perm.module,
                    can_view=perm.can_view,
                    can_edit=perm.can_edit,
                )
            )
        return user.id

    def update_user(self, user_id: str, updates: UserUpdatePayload) -> None:
        if not updates:
            return

        user = self._db.scalar(select(User).where(User.id == user_id))
        if not user:
            return

        if 'name' in updates:
            user.name = updates['name']
        if 'email' in updates:
            user.email = updates['email']
        if 'role' in updates:
            user.role = UserRole(updates['role'])
        if 'position' in updates:
            user.position = updates['position']
        if 'is_active' in updates:
            user.is_active = updates['is_active']
        if 'password' in updates:
            user.password = updates['password']

    def replace_permissions(self, user_id: str, permissions: list[PermissionInput]) -> None:
        self._db.execute(delete(UserPermission).where(UserPermission.user_id == user_id))
        for perm in permissions:
            self._db.add(
                UserPermission(
                    id=str(uuid4()),
                    user_id=user_id,
                    module=perm.module,
                    can_view=perm.can_view,
                    can_edit=perm.can_edit,
                )
            )

    def deactivate_user(self, user_id: str) -> None:
        user = self._db.scalar(select(User).where(User.id == user_id))
        if user:
            user.is_active = False

    @staticmethod
    def _to_entity(user: User) -> UserData:
        return UserData(
            id=user.id,
            name=user.name,
            email=user.email,
            image=user.image,
            role=user.role.value,
            position=user.position,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            permissions=[
                UserPermissionData(
                    id=perm.id,
                    module=perm.module,
                    can_view=perm.can_view,
                    can_edit=perm.can_edit,
                )
                for perm in user.permissions
            ],
        )
