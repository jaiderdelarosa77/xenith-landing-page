"""Schemas Pydantic para requests/responses de `user`."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

SYSTEM_MODULES = [
    'dashboard', 'proyectos', 'tareas', 'clientes', 'cotizaciones',
    'inventario', 'productos', 'items', 'grupos', 'rfid', 'movimientos',
    'contratistas', 'conceptos', 'categorias', 'historial'
]


class PermissionIn(BaseModel):
    module: str
    canView: bool = False
    canEdit: bool = False

    @field_validator('module')
    @classmethod
    def validate_module(cls, value: str) -> str:
        if value not in SYSTEM_MODULES:
            raise ValueError('Modulo invalido')
        return value


class PermissionOut(BaseModel):
    id: str
    module: str
    canView: bool
    canEdit: bool


class UserOut(BaseModel):
    id: str
    name: str | None
    email: str
    role: str
    position: str | None
    isActive: bool
    createdAt: datetime
    updatedAt: datetime
    permissions: list[PermissionOut] = []


class UserSelectOut(BaseModel):
    id: str
    name: str | None
    email: str
    image: str | None


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = 'USER'
    position: str | None = Field(default=None, max_length=100)
    permissions: list[PermissionIn] = []

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise ValueError('Debe contener al menos una mayuscula')
        if not any(c.islower() for c in value):
            raise ValueError('Debe contener al menos una minuscula')
        if not any(c.isdigit() for c in value):
            raise ValueError('Debe contener al menos un numero')
        return value


class UpdateUserRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: str | None = None
    position: str | None = Field(default=None, max_length=100)
    isActive: bool | None = None
    permissions: list[PermissionIn] | None = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not any(c.isupper() for c in value):
            raise ValueError('Debe contener al menos una mayuscula')
        if not any(c.islower() for c in value):
            raise ValueError('Debe contener al menos una minuscula')
        if not any(c.isdigit() for c in value):
            raise ValueError('Debe contener al menos un numero')
        return value


class ChangePasswordRequest(BaseModel):
    currentPassword: str = Field(min_length=1)
    newPassword: str = Field(min_length=8, max_length=128)
    confirmPassword: str = Field(min_length=1)

    @field_validator('newPassword')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise ValueError('Debe contener al menos una mayuscula')
        if not any(c.islower() for c in value):
            raise ValueError('Debe contener al menos una minuscula')
        if not any(c.isdigit() for c in value):
            raise ValueError('Debe contener al menos un numero')
        return value

    @field_validator('confirmPassword')
    @classmethod
    def passwords_match(cls, value: str, values) -> str:
        new_password = values.data.get('newPassword')
        if new_password and value != new_password:
            raise ValueError('Las contrasenas no coinciden')
        return value
