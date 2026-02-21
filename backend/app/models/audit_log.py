"""Modelos ORM de SQLAlchemy para `audit_log`."""

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    module: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    entity_type: Mapped[str] = mapped_column('entityType', String, nullable=False)
    entity_id: Mapped[str | None] = mapped_column('entityId', String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column('metadata', JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column('ipAddress', String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column('userAgent', Text, nullable=True)
    performed_by: Mapped[str] = mapped_column('performedBy', String, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
