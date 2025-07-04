"""
Modelos de base de datos optimizados para eCommerce
Implementa normalización completa, foreign keys y índices optimizados
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Decimal as SQLDecimal, DateTime, Boolean, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint, JSON
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from src.config.database import Base
import uuid

class TimestampMixin:
    """Mixin para timestamps automáticos"""
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class SoftDeleteMixin:
    """Mixin para soft delete"""
    deleted_at = Column(DateTime, nullable=True)
    
    @hybrid_property
    def is_deleted(self):
        return self.deleted_at is not None

# ==============================================
# MODELOS DE USUARIOS Y AUTENTICACIÓN
# ==============================================

class User(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de usuario con roles y permisos"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relaciones
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    wishlist_items = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_uuid', 'uuid'),
        Index('idx_users_active', 'is_active'),
        Index('idx_users_created', 'created_at'),
    )
    
    @validates('email')
    def validate_email(self, key, email):
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Email inválido')
        return email.lower()
    
    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Role(Base, TimestampMixin):
    """Modelo de roles del sistema"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    user_roles = relationship("UserRole", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

class Permission(Base, TimestampMixin):
    """Modelo de permisos del sistema"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False)  # products, orders, users, etc.
    action = Column(String(50), nullable=False)    # create, read, update, delete
    
    # Relaciones
    role_permissions = relationship("RolePermission", back_populates="permission")
    
    # Índices
    __table_args__ = (
        Index('idx_permissions_resource_action', 'resource', 'action'),
        UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
    )

class UserRole(Base, TimestampMixin):
    """Tabla de relación usuarios-roles"""
    __tablename__ = 'user_roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    
    # Relaciones
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    
    # Índices y constraints
    __table_args__ = (
        Index('idx_user_roles_user', 'user_id'),
        Index('idx_user_roles_role', 'role_id'),
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )

class RolePermission(Base, TimestampMixin):
    """Tabla de relación roles-permisos"""
    __tablename__ = 'role_permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    
    # Relaciones
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    # Índices y constraints
    __table_args__ = (
        Index('idx_role_permissions_role', 'role_id'),
        Index('idx_role_permissions_permission', 'permission_id'),
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )

# ==============================================
# MODELOS DE CATÁLOGO DE PRODUCTOS
# ==============================================

class Category(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de categorías jerárquicas"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(500), nullable=True)
    
    # Relaciones
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category")
    
    # Índices
    __table_args__ = (
        Index('idx_categories_slug', 'slug'),
        Index('idx_categories_parent', 'parent_id'),
        Index('idx_categories_active', 'is_active'),
        Index('idx_categories_sort', 'sort_order'),
    )

class Brand(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de marcas"""
    __tablename__ = 'brands'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    products = relationship("Product", back_populates="brand")
    
    # Índices
    __table_args__ = (
        Index('idx_brands_slug', 'slug'),
        Index('idx_brands_active', 'is_active'),
    )

class Product(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo principal de productos"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, nullable=False)
    short_description = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # Precios
    price = Column(SQLDecimal(10, 2), nullable=False)
    compare_price = Column(SQLDecimal(10, 2), nullable=True)
    cost_price = Column(SQLDecimal(10, 2), nullable=True)
    
    # Inventario
    track_inventory = Column(Boolean, default=True, nullable=False)
    inventory_quantity = Column(Integer, default=0, nullable=False)
    low_stock_threshold = Column(Integer, default=10, nullable=False)
    
    # Dimensiones y peso
    weight = Column(SQLDecimal(8, 3), nullable=True)
    length = Column(SQLDecimal(8, 2), nullable=True)
    width = Column(SQLDecimal(8, 2), nullable=True)
    height = Column(SQLDecimal(8, 2), nullable=True)
    
    # Estado y configuración
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    requires_shipping = Column(Boolean, default=True, nullable=False)
    is_digital = Column(Boolean, default=False, nullable=False)
    
    # SEO
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(500), nullable=True)
    
    # Relaciones
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    brand_id = Column(Integer, ForeignKey('brands.id', ondelete='SET NULL'), nullable=True)
    
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    
    # Índices
    __table_args__ = (
        Index('idx_products_sku', 'sku'),
        Index('idx_products_slug', 'slug'),
        Index('idx_products_category', 'category_id'),
        Index('idx_products_brand', 'brand_id'),
        Index('idx_products_active', 'is_active'),
        Index('idx_products_featured', 'is_featured'),
        Index('idx_products_price', 'price'),
        Index('idx_products_inventory', 'inventory_quantity'),
        Index('idx_products_created', 'created_at'),
        CheckConstraint('price >= 0', name='ck_product_price_positive'),
        CheckConstraint('inventory_quantity >= 0', name='ck_product_inventory_positive'),
    )
    
    @validates('price', 'compare_price', 'cost_price')
    def validate_prices(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f'{key} debe ser mayor o igual a 0')
        return value
    
    @hybrid_property
    def is_on_sale(self):
        return self.compare_price is not None and self.compare_price > self.price
    
    @hybrid_property
    def discount_percentage(self):
        if self.is_on_sale:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0
    
    @hybrid_property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.inventory_quantity > 0
    
    @hybrid_property
    def is_low_stock(self):
        if not self.track_inventory:
            return False
        return self.inventory_quantity <= self.low_stock_threshold

class ProductImage(Base, TimestampMixin):
    """Modelo de imágenes de productos"""
    __tablename__ = 'product_images'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    
    # Relaciones
    product = relationship("Product", back_populates="images")
    
    # Índices
    __table_args__ = (
        Index('idx_product_images_product', 'product_id'),
        Index('idx_product_images_sort', 'product_id', 'sort_order'),
        Index('idx_product_images_primary', 'product_id', 'is_primary'),
    )

class AttributeGroup(Base, TimestampMixin):
    """Grupos de atributos (Color, Talla, Material, etc.)"""
    __tablename__ = 'attribute_groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    attributes = relationship("Attribute", back_populates="group", cascade="all, delete-orphan")

class Attribute(Base, TimestampMixin):
    """Atributos específicos (Rojo, XL, Algodón, etc.)"""
    __tablename__ = 'attributes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('attribute_groups.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    value = Column(String(100), nullable=False)
    color_code = Column(String(7), nullable=True)  # Para colores hex
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    group = relationship("AttributeGroup", back_populates="attributes")
    product_attributes = relationship("ProductAttribute", back_populates="attribute")
    variant_attributes = relationship("VariantAttribute", back_populates="attribute")
    
    # Índices
    __table_args__ = (
        Index('idx_attributes_group', 'group_id'),
        Index('idx_attributes_active', 'is_active'),
        UniqueConstraint('group_id', 'value', name='uq_attribute_group_value'),
    )

class ProductAttribute(Base, TimestampMixin):
    """Relación productos-atributos"""
    __tablename__ = 'product_attributes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attributes.id', ondelete='CASCADE'), nullable=False)
    
    # Relaciones
    product = relationship("Product", back_populates="attributes")
    attribute = relationship("Attribute", back_populates="product_attributes")
    
    # Índices
    __table_args__ = (
        Index('idx_product_attributes_product', 'product_id'),
        Index('idx_product_attributes_attribute', 'attribute_id'),
        UniqueConstraint('product_id', 'attribute_id', name='uq_product_attribute'),
    )

class ProductVariant(Base, TimestampMixin, SoftDeleteMixin):
    """Variantes de productos (combinaciones de atributos)"""
    __tablename__ = 'product_variants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    
    # Precios específicos de la variante
    price = Column(SQLDecimal(10, 2), nullable=True)  # Si es NULL, usa precio del producto
    compare_price = Column(SQLDecimal(10, 2), nullable=True)
    cost_price = Column(SQLDecimal(10, 2), nullable=True)
    
    # Inventario específico
    inventory_quantity = Column(Integer, default=0, nullable=False)
    
    # Configuración
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    product = relationship("Product", back_populates="variants")
    attributes = relationship("VariantAttribute", back_populates="variant", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="variant")
    
    # Índices
    __table_args__ = (
        Index('idx_product_variants_product', 'product_id'),
        Index('idx_product_variants_sku', 'sku'),
        Index('idx_product_variants_active', 'is_active'),
        CheckConstraint('inventory_quantity >= 0', name='ck_variant_inventory_positive'),
    )
    
    @hybrid_property
    def effective_price(self):
        return self.price if self.price is not None else self.product.price

class VariantAttribute(Base, TimestampMixin):
    """Atributos específicos de cada variante"""
    __tablename__ = 'variant_attributes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    variant_id = Column(Integer, ForeignKey('product_variants.id', ondelete='CASCADE'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attributes.id', ondelete='CASCADE'), nullable=False)
    
    # Relaciones
    variant = relationship("ProductVariant", back_populates="attributes")
    attribute = relationship("Attribute", back_populates="variant_attributes")
    
    # Índices
    __table_args__ = (
        Index('idx_variant_attributes_variant', 'variant_id'),
        Index('idx_variant_attributes_attribute', 'attribute_id'),
        UniqueConstraint('variant_id', 'attribute_id', name='uq_variant_attribute'),
    )

