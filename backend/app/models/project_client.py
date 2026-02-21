"""Modelos ORM de SQLAlchemy para `project_client`."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Client(Base):
    __tablename__ = 'clients'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    country: Mapped[str | None] = mapped_column(String, nullable=True)
    nit: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rut_url: Mapped[str | None] = mapped_column('rutUrl', String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    projects: Mapped[list['Project']] = relationship('Project', back_populates='client')
    quotations: Mapped[list['Quotation']] = relationship('Quotation', back_populates='client')


class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    client_id: Mapped[str] = mapped_column('clientId', String, ForeignKey('clients.id', ondelete='RESTRICT'), nullable=False)
    assigned_to: Mapped[str] = mapped_column('assignedTo', String, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    start_date: Mapped[DateTime | None] = mapped_column('startDate', DateTime(timezone=True), nullable=True)
    end_date: Mapped[DateTime | None] = mapped_column('endDate', DateTime(timezone=True), nullable=True)
    budget: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    priority: Mapped[str] = mapped_column(String, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    client: Mapped[Client] = relationship('Client', back_populates='projects')
    assigned_user: Mapped['User'] = relationship('User', foreign_keys=[assigned_to])
    tasks: Mapped[list['Task']] = relationship('Task', back_populates='project')
    quotations: Mapped[list['Quotation']] = relationship('Quotation', back_populates='project')


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column('projectId', String, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    assigned_to: Mapped[str | None] = mapped_column('assignedTo', String, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    due_date: Mapped[DateTime | None] = mapped_column('dueDate', DateTime(timezone=True), nullable=True)
    priority: Mapped[str] = mapped_column(String, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped[Project] = relationship('Project', back_populates='tasks')
    assigned_user: Mapped['User | None'] = relationship('User', foreign_keys=[assigned_to])


class Quotation(Base):
    __tablename__ = 'quotations'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    quotation_number: Mapped[str] = mapped_column('quotationNumber', String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column('createdBy', String, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    valid_until: Mapped[DateTime] = mapped_column('validUntil', DateTime(timezone=True), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tax: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    client_id: Mapped[str] = mapped_column('clientId', String, ForeignKey('clients.id', ondelete='RESTRICT'), nullable=False)
    project_id: Mapped[str | None] = mapped_column('projectId', String, ForeignKey('projects.id', ondelete='SET NULL'), nullable=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    client: Mapped[Client] = relationship('Client', back_populates='quotations')
    project: Mapped[Project | None] = relationship('Project', back_populates='quotations')
    created_by_user: Mapped['User'] = relationship('User', foreign_keys=[created_by])
    items: Mapped[list['QuotationItem']] = relationship('QuotationItem', back_populates='quotation')
    groups: Mapped[list['QuotationGroup']] = relationship('QuotationGroup', back_populates='quotation')


class QuotationItem(Base):
    __tablename__ = 'quotation_items'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    quotation_id: Mapped[str] = mapped_column('quotationId', String, ForeignKey('quotations.id', ondelete='CASCADE'), nullable=False)
    inventory_item_id: Mapped[str | None] = mapped_column('inventoryItemId', String, ForeignKey('inventory_items.id', ondelete='SET NULL'), nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[float] = mapped_column('unitPrice', Numeric(10, 2), nullable=False)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    order: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    quotation: Mapped[Quotation] = relationship('Quotation', back_populates='items')
    inventory_item: Mapped['InventoryItem | None'] = relationship('InventoryItem', back_populates='quotation_items')


class ItemGroup(Base):
    __tablename__ = 'item_groups'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items: Mapped[list['ItemGroupItem']] = relationship('ItemGroupItem', back_populates='group')
    quotations: Mapped[list['QuotationGroup']] = relationship('QuotationGroup', back_populates='group')


class ItemGroupItem(Base):
    __tablename__ = 'item_group_items'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    group_id: Mapped[str] = mapped_column('groupId', String, ForeignKey('item_groups.id', ondelete='CASCADE'), nullable=False)
    inventory_item_id: Mapped[str] = mapped_column('inventoryItemId', String, ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())

    group: Mapped[ItemGroup] = relationship('ItemGroup', back_populates='items')
    inventory_item: Mapped['InventoryItem'] = relationship('InventoryItem', back_populates='group_links')


class QuotationGroup(Base):
    __tablename__ = 'quotation_groups'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    quotation_id: Mapped[str] = mapped_column('quotationId', String, ForeignKey('quotations.id', ondelete='CASCADE'), nullable=False)
    group_id: Mapped[str] = mapped_column('groupId', String, ForeignKey('item_groups.id', ondelete='RESTRICT'), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_price: Mapped[float] = mapped_column('unitPrice', Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    order: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    quotation: Mapped[Quotation] = relationship('Quotation', back_populates='groups')
    group: Mapped[ItemGroup] = relationship('ItemGroup', back_populates='quotations')
