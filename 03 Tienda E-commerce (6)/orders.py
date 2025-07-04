"""
Modelos de pedidos, transacciones y sistema de ventas
Implementa normalización completa eliminando duplicación de datos
"""
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Decimal as SQLDecimal, DateTime, Boolean, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from src.config.database import Base
from src.models.catalog import TimestampMixin, SoftDeleteMixin
import uuid

# ==============================================
# ENUMS PARA ESTADOS
# ==============================================

class OrderStatus(Enum):
    """Estados de pedidos"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(Enum):
    """Estados de pagos"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class PaymentMethod(Enum):
    """Métodos de pago"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    MERCADOPAGO = "mercadopago"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"

class ShippingStatus(Enum):
    """Estados de envío"""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"

# ==============================================
# MODELOS DE DIRECCIONES
# ==============================================

class Country(Base, TimestampMixin):
    """Modelo de países"""
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(2), unique=True, nullable=False)  # ISO 3166-1 alpha-2
    name = Column(String(100), nullable=False)
    phone_code = Column(String(10), nullable=True)
    currency_code = Column(String(3), nullable=True)  # ISO 4217
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    states = relationship("State", back_populates="country", cascade="all, delete-orphan")
    addresses = relationship("Address", back_populates="country")

class State(Base, TimestampMixin):
    """Modelo de estados/provincias"""
    __tablename__ = 'states'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey('countries.id', ondelete='CASCADE'), nullable=False)
    code = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    country = relationship("Country", back_populates="states")
    cities = relationship("City", back_populates="state", cascade="all, delete-orphan")
    addresses = relationship("Address", back_populates="state")
    
    # Índices
    __table_args__ = (
        Index('idx_states_country', 'country_id'),
        UniqueConstraint('country_id', 'code', name='uq_state_country_code'),
    )

class City(Base, TimestampMixin):
    """Modelo de ciudades"""
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    state_id = Column(Integer, ForeignKey('states.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    state = relationship("State", back_populates="cities")
    addresses = relationship("Address", back_populates="city")
    
    # Índices
    __table_args__ = (
        Index('idx_cities_state', 'state_id'),
        Index('idx_cities_postal', 'postal_code'),
    )

class Address(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de direcciones normalizadas"""
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Información de dirección
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company = Column(String(100), nullable=True)
    address_line_1 = Column(String(200), nullable=False)
    address_line_2 = Column(String(200), nullable=True)
    
    # Ubicación geográfica
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='RESTRICT'), nullable=False)
    state_id = Column(Integer, ForeignKey('states.id', ondelete='RESTRICT'), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id', ondelete='RESTRICT'), nullable=False)
    postal_code = Column(String(20), nullable=False)
    
    # Configuración
    phone = Column(String(20), nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    address_type = Column(String(20), default='shipping', nullable=False)  # shipping, billing, both
    
    # Relaciones
    user = relationship("User", back_populates="addresses")
    city = relationship("City", back_populates="addresses")
    state = relationship("State", back_populates="addresses")
    country = relationship("Country", back_populates="addresses")
    
    # Índices
    __table_args__ = (
        Index('idx_addresses_user', 'user_id'),
        Index('idx_addresses_city', 'city_id'),
        Index('idx_addresses_default', 'user_id', 'is_default'),
        CheckConstraint("address_type IN ('shipping', 'billing', 'both')", 
                       name='ck_address_type_valid'),
    )
    
    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @hybrid_property
    def full_address(self):
        parts = [self.address_line_1]
        if self.address_line_2:
            parts.append(self.address_line_2)
        parts.extend([self.city.name, self.state.name, self.country.name, self.postal_code])
        return ", ".join(parts)

# ==============================================
# MODELOS DE CARRITO DE COMPRAS
# ==============================================

class Cart(Base, TimestampMixin):
    """Modelo de carrito de compras"""
    __tablename__ = 'carts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    session_id = Column(String(255), nullable=True)  # Para usuarios no registrados
    
    # Relaciones
    user = relationship("User")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_carts_user', 'user_id'),
        Index('idx_carts_session', 'session_id'),
        Index('idx_carts_updated', 'updated_at'),
    )
    
    @hybrid_property
    def total_items(self):
        return sum(item.quantity for item in self.items)
    
    @hybrid_property
    def total_amount(self):
        return sum(item.total_price for item in self.items)

class CartItem(Base, TimestampMixin):
    """Items del carrito de compras"""
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey('carts.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id', ondelete='CASCADE'), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(SQLDecimal(10, 2), nullable=False)  # Precio al momento de agregar
    
    # Relaciones
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    
    # Índices
    __table_args__ = (
        Index('idx_cart_items_cart', 'cart_id'),
        Index('idx_cart_items_product', 'product_id'),
        UniqueConstraint('cart_id', 'product_id', 'variant_id', name='uq_cart_item'),
        CheckConstraint('quantity > 0', name='ck_cart_item_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='ck_cart_item_price_positive'),
    )
    
    @hybrid_property
    def total_price(self):
        return self.quantity * self.unit_price

# ==============================================
# MODELOS DE PEDIDOS
# ==============================================

class Order(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo principal de pedidos"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    
    # Estado del pedido
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # Información de contacto (normalizada)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Direcciones (referencias a direcciones normalizadas)
    billing_address_id = Column(Integer, ForeignKey('addresses.id', ondelete='RESTRICT'), nullable=False)
    shipping_address_id = Column(Integer, ForeignKey('addresses.id', ondelete='RESTRICT'), nullable=False)
    
    # Totales calculados
    subtotal = Column(SQLDecimal(10, 2), nullable=False)
    tax_amount = Column(SQLDecimal(10, 2), default=0, nullable=False)
    shipping_amount = Column(SQLDecimal(10, 2), default=0, nullable=False)
    discount_amount = Column(SQLDecimal(10, 2), default=0, nullable=False)
    total_amount = Column(SQLDecimal(10, 2), nullable=False)
    
    # Información adicional
    notes = Column(Text, nullable=True)
    currency = Column(String(3), default='USD', nullable=False)
    
    # Timestamps específicos
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relaciones
    user = relationship("User", back_populates="orders")
    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_orders_number', 'order_number'),
        Index('idx_orders_user', 'user_id'),
        Index('idx_orders_status', 'status'),
        Index('idx_orders_created', 'created_at'),
        Index('idx_orders_total', 'total_amount'),
        CheckConstraint('subtotal >= 0', name='ck_order_subtotal_positive'),
        CheckConstraint('total_amount >= 0', name='ck_order_total_positive'),
    )
    
    @validates('total_amount')
    def validate_total(self, key, value):
        if value < 0:
            raise ValueError('El total del pedido debe ser mayor o igual a 0')
        return value

class OrderItem(Base, TimestampMixin):
    """Items de pedidos normalizados"""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id', ondelete='RESTRICT'), nullable=True)
    
    # Información del producto al momento de la compra
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(50), nullable=False)
    variant_name = Column(String(200), nullable=True)
    
    # Precios y cantidades
    quantity = Column(Integer, nullable=False)
    unit_price = Column(SQLDecimal(10, 2), nullable=False)
    total_price = Column(SQLDecimal(10, 2), nullable=False)
    
    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("ProductVariant", back_populates="order_items")
    
    # Índices
    __table_args__ = (
        Index('idx_order_items_order', 'order_id'),
        Index('idx_order_items_product', 'product_id'),
        CheckConstraint('quantity > 0', name='ck_order_item_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='ck_order_item_price_positive'),
        CheckConstraint('total_price >= 0', name='ck_order_item_total_positive'),
    )

class OrderStatusHistory(Base, TimestampMixin):
    """Historial de cambios de estado de pedidos"""
    __tablename__ = 'order_status_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    from_status = Column(SQLEnum(OrderStatus), nullable=True)
    to_status = Column(SQLEnum(OrderStatus), nullable=False)
    notes = Column(Text, nullable=True)
    changed_by_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Relaciones
    order = relationship("Order", back_populates="status_history")
    changed_by = relationship("User")
    
    # Índices
    __table_args__ = (
        Index('idx_order_status_history_order', 'order_id'),
        Index('idx_order_status_history_created', 'created_at'),
    )

# ==============================================
# MODELOS DE PAGOS
# ==============================================

class Payment(Base, TimestampMixin):
    """Modelo de pagos"""
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    payment_number = Column(String(50), unique=True, nullable=False)
    
    # Información del pago
    method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    amount = Column(SQLDecimal(10, 2), nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    
    # Información del proveedor de pago
    gateway = Column(String(50), nullable=False)  # stripe, paypal, mercadopago, etc.
    gateway_transaction_id = Column(String(255), nullable=True)
    gateway_response = Column(Text, nullable=True)  # JSON response del gateway
    
    # Timestamps específicos
    processed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    
    # Relaciones
    order = relationship("Order", back_populates="payments")
    refunds = relationship("PaymentRefund", back_populates="payment", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_payments_order', 'order_id'),
        Index('idx_payments_number', 'payment_number'),
        Index('idx_payments_status', 'status'),
        Index('idx_payments_gateway_id', 'gateway_transaction_id'),
        Index('idx_payments_created', 'created_at'),
        CheckConstraint('amount > 0', name='ck_payment_amount_positive'),
    )

class PaymentRefund(Base, TimestampMixin):
    """Modelo de reembolsos"""
    __tablename__ = 'payment_refunds'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey('payments.id', ondelete='CASCADE'), nullable=False)
    refund_number = Column(String(50), unique=True, nullable=False)
    amount = Column(SQLDecimal(10, 2), nullable=False)
    reason = Column(String(500), nullable=True)
    gateway_refund_id = Column(String(255), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Relaciones
    payment = relationship("Payment", back_populates="refunds")
    
    # Índices
    __table_args__ = (
        Index('idx_payment_refunds_payment', 'payment_id'),
        Index('idx_payment_refunds_number', 'refund_number'),
        CheckConstraint('amount > 0', name='ck_refund_amount_positive'),
    )

# ==============================================
# MODELOS DE ENVÍOS
# ==============================================

class ShippingMethod(Base, TimestampMixin):
    """Métodos de envío disponibles"""
    __tablename__ = 'shipping_methods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    carrier = Column(String(100), nullable=False)  # DHL, FedEx, UPS, etc.
    estimated_days_min = Column(Integer, nullable=False)
    estimated_days_max = Column(Integer, nullable=False)
    base_cost = Column(SQLDecimal(10, 2), nullable=False)
    cost_per_kg = Column(SQLDecimal(10, 2), default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    shipments = relationship("Shipment", back_populates="shipping_method")
    
    # Índices
    __table_args__ = (
        Index('idx_shipping_methods_active', 'is_active'),
        Index('idx_shipping_methods_carrier', 'carrier'),
    )

class Shipment(Base, TimestampMixin):
    """Modelo de envíos"""
    __tablename__ = 'shipments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    shipping_method_id = Column(Integer, ForeignKey('shipping_methods.id', ondelete='RESTRICT'), nullable=False)
    
    tracking_number = Column(String(100), unique=True, nullable=True)
    status = Column(SQLEnum(ShippingStatus), default=ShippingStatus.PENDING, nullable=False)
    
    # Costos
    shipping_cost = Column(SQLDecimal(10, 2), nullable=False)
    
    # Información del paquete
    weight = Column(SQLDecimal(8, 3), nullable=True)
    length = Column(SQLDecimal(8, 2), nullable=True)
    width = Column(SQLDecimal(8, 2), nullable=True)
    height = Column(SQLDecimal(8, 2), nullable=True)
    
    # Timestamps específicos
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    estimated_delivery_at = Column(DateTime, nullable=True)
    
    # Relaciones
    order = relationship("Order", back_populates="shipments")
    shipping_method = relationship("ShippingMethod", back_populates="shipments")
    tracking_events = relationship("ShipmentTracking", back_populates="shipment", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_shipments_order', 'order_id'),
        Index('idx_shipments_tracking', 'tracking_number'),
        Index('idx_shipments_status', 'status'),
        Index('idx_shipments_shipped', 'shipped_at'),
    )

class ShipmentTracking(Base, TimestampMixin):
    """Eventos de seguimiento de envíos"""
    __tablename__ = 'shipment_tracking'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(Integer, ForeignKey('shipments.id', ondelete='CASCADE'), nullable=False)
    status = Column(SQLEnum(ShippingStatus), nullable=False)
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    occurred_at = Column(DateTime, nullable=False)
    
    # Relaciones
    shipment = relationship("Shipment", back_populates="tracking_events")
    
    # Índices
    __table_args__ = (
        Index('idx_shipment_tracking_shipment', 'shipment_id'),
        Index('idx_shipment_tracking_occurred', 'occurred_at'),
    )

