"""Modelos ORM de SQLAlchemy para `catalog_inventory`."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String, nullable=True)
    icon: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    products: Mapped[list['Product']] = relationship('Product', back_populates='category')


class Supplier(Base):
    __tablename__ = 'suppliers'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    nit: Mapped[str | None] = mapped_column(String, nullable=True)
    contact_name: Mapped[str | None] = mapped_column('contactName', String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    country: Mapped[str | None] = mapped_column(String, nullable=True)
    website: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rut_url: Mapped[str | None] = mapped_column('rutUrl', String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    products: Mapped[list['ProductSupplier']] = relationship('ProductSupplier', back_populates='supplier')
    concepts: Mapped[list['Concept']] = relationship('Concept', back_populates='supplier')


class Concept(Base):
    __tablename__ = 'concepts'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    supplier_id: Mapped[str | None] = mapped_column('supplierId', String, ForeignKey('suppliers.id', ondelete='SET NULL'), nullable=True)
    unit_price: Mapped[float | None] = mapped_column('unitPrice', Numeric(10, 2), nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column('isActive', Boolean, nullable=False, default=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    supplier: Mapped[Supplier | None] = relationship('Supplier', back_populates='concepts')


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    sku: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[str] = mapped_column('categoryId', String, ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    brand: Mapped[str | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    unit_price: Mapped[float | None] = mapped_column('unitPrice', Numeric(10, 2), nullable=True)
    rental_price: Mapped[float | None] = mapped_column('rentalPrice', Numeric(10, 2), nullable=True)
    image_url: Mapped[str | None] = mapped_column('imageUrl', String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[DateTime | None] = mapped_column('deletedAt', DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category: Mapped[Category] = relationship('Category', back_populates='products')
    suppliers: Mapped[list['ProductSupplier']] = relationship('ProductSupplier', back_populates='product')
    inventory_items: Mapped[list['InventoryItem']] = relationship('InventoryItem', back_populates='product')


class ProductSupplier(Base):
    __tablename__ = 'product_suppliers'

    product_id: Mapped[str] = mapped_column('productId', String, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
    supplier_id: Mapped[str] = mapped_column('supplierId', String, ForeignKey('suppliers.id', ondelete='CASCADE'), primary_key=True)
    supplier_sku: Mapped[str | None] = mapped_column('supplierSku', String, nullable=True)
    cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_preferred: Mapped[bool] = mapped_column('isPreferred', Boolean, nullable=False, default=False)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())

    product: Mapped[Product] = relationship('Product', back_populates='suppliers')
    supplier: Mapped[Supplier] = relationship('Supplier', back_populates='products')


class InventoryItem(Base):
    __tablename__ = 'inventory_items'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column('productId', String, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    serial_number: Mapped[str | None] = mapped_column('serialNumber', String, nullable=True)
    asset_tag: Mapped[str | None] = mapped_column('assetTag', String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    condition: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    container_id: Mapped[str | None] = mapped_column('containerId', String, ForeignKey('inventory_items.id'), nullable=True)
    purchase_date: Mapped[DateTime | None] = mapped_column('purchaseDate', DateTime(timezone=True), nullable=True)
    purchase_price: Mapped[float | None] = mapped_column('purchasePrice', Numeric(10, 2), nullable=True)
    warranty_expiry: Mapped[DateTime | None] = mapped_column('warrantyExpiry', DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product: Mapped[Product] = relationship('Product', back_populates='inventory_items')
    container: Mapped['InventoryItem | None'] = relationship('InventoryItem', remote_side='InventoryItem.id', back_populates='contents')
    contents: Mapped[list['InventoryItem']] = relationship('InventoryItem', back_populates='container')
    rfid_tag: Mapped['RfidTag | None'] = relationship('RfidTag', back_populates='inventory_item', uselist=False)
    quotation_items: Mapped[list['QuotationItem']] = relationship('QuotationItem', back_populates='inventory_item')
    group_links: Mapped[list['ItemGroupItem']] = relationship('ItemGroupItem', back_populates='inventory_item')


class RfidTag(Base):
    __tablename__ = 'rfid_tags'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    epc: Mapped[str] = mapped_column(String, nullable=False)
    tid: Mapped[str | None] = mapped_column(String, nullable=True)
    inventory_item_id: Mapped[str | None] = mapped_column('inventoryItemId', String, ForeignKey('inventory_items.id', ondelete='SET NULL'), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    first_seen_at: Mapped[DateTime] = mapped_column('firstSeenAt', DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[DateTime] = mapped_column('lastSeenAt', DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    inventory_item: Mapped[InventoryItem | None] = relationship('InventoryItem', back_populates='rfid_tag')
    detections: Mapped[list['RfidDetection']] = relationship('RfidDetection', back_populates='rfid_tag')


class RfidDetection(Base):
    __tablename__ = 'rfid_detections'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    rfid_tag_id: Mapped[str] = mapped_column('rfidTagId', String, ForeignKey('rfid_tags.id', ondelete='CASCADE'), nullable=False)
    reader_id: Mapped[str] = mapped_column('readerId', String, nullable=False)
    reader_name: Mapped[str | None] = mapped_column('readerName', String, nullable=True)
    rssi: Mapped[int | None] = mapped_column(nullable=True)
    direction: Mapped[str | None] = mapped_column(nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    rfid_tag: Mapped[RfidTag] = relationship('RfidTag', back_populates='detections')


class InventoryMovement(Base):
    __tablename__ = 'inventory_movements'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    inventory_item_id: Mapped[str] = mapped_column('inventoryItemId', String, ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    from_status: Mapped[str | None] = mapped_column('fromStatus', String, nullable=True)
    to_status: Mapped[str] = mapped_column('toStatus', String, nullable=False)
    from_location: Mapped[str | None] = mapped_column('fromLocation', String, nullable=True)
    to_location: Mapped[str | None] = mapped_column('toLocation', String, nullable=True)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    reference: Mapped[str | None] = mapped_column(String, nullable=True)
    performed_by: Mapped[str] = mapped_column('performedBy', String, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())

    inventory_item: Mapped[InventoryItem] = relationship('InventoryItem')
