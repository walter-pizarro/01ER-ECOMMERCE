"""
Modelos adicionales: reseñas, wishlist, cupones y configuración
Completa el sistema de base de datos normalizado
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

# ==============================================
# ENUMS ADICIONALES
# ==============================================

class CouponType(Enum):
    """Tipos de cupones"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_SHIPPING = "free_shipping"

class DiscountTarget(Enum):
    """Objetivo del descuento"""
    ORDER = "order"
    PRODUCT = "product"
    CATEGORY = "category"
    SHIPPING = "shipping"

# ==============================================
# MODELOS DE RESEÑAS Y CALIFICACIONES
# ==============================================

class Review(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de reseñas de productos"""
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='SET NULL'), nullable=True)
    
    # Contenido de la reseña
    rating = Column(Integer, nullable=False)  # 1-5 estrellas
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Estado y moderación
    is_approved = Column(Boolean, default=False, nullable=False)
    is_verified_purchase = Column(Boolean, default=False, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    approved_by_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Utilidad de la reseña
    helpful_count = Column(Integer, default=0, nullable=False)
    not_helpful_count = Column(Integer, default=0, nullable=False)
    
    # Relaciones
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews", foreign_keys=[user_id])
    order = relationship("Order")
    approved_by = relationship("User", foreign_keys=[approved_by_user_id])
    helpfulness_votes = relationship("ReviewHelpfulness", back_populates="review", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_reviews_product', 'product_id'),
        Index('idx_reviews_user', 'user_id'),
        Index('idx_reviews_rating', 'rating'),
        Index('idx_reviews_approved', 'is_approved'),
        Index('idx_reviews_verified', 'is_verified_purchase'),
        Index('idx_reviews_created', 'created_at'),
        UniqueConstraint('product_id', 'user_id', 'order_id', name='uq_review_product_user_order'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='ck_review_rating_valid'),
        CheckConstraint('helpful_count >= 0', name='ck_review_helpful_positive'),
        CheckConstraint('not_helpful_count >= 0', name='ck_review_not_helpful_positive'),
    )
    
    @validates('rating')
    def validate_rating(self, key, rating):
        if rating < 1 or rating > 5:
            raise ValueError('La calificación debe estar entre 1 y 5')
        return rating
    
    @hybrid_property
    def helpfulness_ratio(self):
        total_votes = self.helpful_count + self.not_helpful_count
        if total_votes == 0:
            return 0
        return self.helpful_count / total_votes

class ReviewHelpfulness(Base, TimestampMixin):
    """Votos de utilidad de reseñas"""
    __tablename__ = 'review_helpfulness'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_helpful = Column(Boolean, nullable=False)
    
    # Relaciones
    review = relationship("Review", back_populates="helpfulness_votes")
    user = relationship("User")
    
    # Índices
    __table_args__ = (
        Index('idx_review_helpfulness_review', 'review_id'),
        Index('idx_review_helpfulness_user', 'user_id'),
        UniqueConstraint('review_id', 'user_id', name='uq_review_helpfulness'),
    )

# ==============================================
# MODELOS DE WISHLIST
# ==============================================

class WishlistItem(Base, TimestampMixin):
    """Items de lista de deseos"""
    __tablename__ = 'wishlist_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id', ondelete='CASCADE'), nullable=True)
    
    # Relaciones
    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")
    variant = relationship("ProductVariant")
    
    # Índices
    __table_args__ = (
        Index('idx_wishlist_items_user', 'user_id'),
        Index('idx_wishlist_items_product', 'product_id'),
        Index('idx_wishlist_items_created', 'created_at'),
        UniqueConstraint('user_id', 'product_id', 'variant_id', name='uq_wishlist_item'),
    )

# ==============================================
# MODELOS DE CUPONES Y DESCUENTOS
# ==============================================

class Coupon(Base, TimestampMixin, SoftDeleteMixin):
    """Modelo de cupones de descuento"""
    __tablename__ = 'coupons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Tipo y valor del descuento
    type = Column(SQLEnum(CouponType), nullable=False)
    value = Column(SQLDecimal(10, 2), nullable=False)  # Porcentaje o monto fijo
    target = Column(SQLEnum(DiscountTarget), default=DiscountTarget.ORDER, nullable=False)
    
    # Restricciones de uso
    minimum_amount = Column(SQLDecimal(10, 2), nullable=True)
    maximum_discount = Column(SQLDecimal(10, 2), nullable=True)
    usage_limit = Column(Integer, nullable=True)  # NULL = ilimitado
    usage_limit_per_user = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0, nullable=False)
    
    # Fechas de validez
    starts_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    usages = relationship("CouponUsage", back_populates="coupon", cascade="all, delete-orphan")
    product_restrictions = relationship("CouponProductRestriction", back_populates="coupon", cascade="all, delete-orphan")
    category_restrictions = relationship("CouponCategoryRestriction", back_populates="coupon", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_coupons_code', 'code'),
        Index('idx_coupons_active', 'is_active'),
        Index('idx_coupons_dates', 'starts_at', 'expires_at'),
        Index('idx_coupons_type', 'type'),
        CheckConstraint('value > 0', name='ck_coupon_value_positive'),
        CheckConstraint('used_count >= 0', name='ck_coupon_used_count_positive'),
    )
    
    @validates('value')
    def validate_value(self, key, value):
        if self.type == CouponType.PERCENTAGE and value > 100:
            raise ValueError('El porcentaje de descuento no puede ser mayor a 100')
        if value <= 0:
            raise ValueError('El valor del descuento debe ser mayor a 0')
        return value
    
    @hybrid_property
    def is_valid(self):
        now = datetime.now(timezone.utc)
        return (self.is_active and 
                self.starts_at <= now and 
                (self.expires_at is None or self.expires_at >= now) and
                (self.usage_limit is None or self.used_count < self.usage_limit))

class CouponUsage(Base, TimestampMixin):
    """Registro de uso de cupones"""
    __tablename__ = 'coupon_usages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey('coupons.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    discount_amount = Column(SQLDecimal(10, 2), nullable=False)
    
    # Relaciones
    coupon = relationship("Coupon", back_populates="usages")
    user = relationship("User")
    order = relationship("Order")
    
    # Índices
    __table_args__ = (
        Index('idx_coupon_usages_coupon', 'coupon_id'),
        Index('idx_coupon_usages_user', 'user_id'),
        Index('idx_coupon_usages_order', 'order_id'),
        Index('idx_coupon_usages_created', 'created_at'),
        UniqueConstraint('coupon_id', 'order_id', name='uq_coupon_usage_order'),
    )

class CouponProductRestriction(Base, TimestampMixin):
    """Restricciones de cupones por producto"""
    __tablename__ = 'coupon_product_restrictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey('coupons.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    is_included = Column(Boolean, default=True, nullable=False)  # True = incluido, False = excluido
    
    # Relaciones
    coupon = relationship("Coupon", back_populates="product_restrictions")
    product = relationship("Product")
    
    # Índices
    __table_args__ = (
        Index('idx_coupon_product_restrictions_coupon', 'coupon_id'),
        Index('idx_coupon_product_restrictions_product', 'product_id'),
        UniqueConstraint('coupon_id', 'product_id', name='uq_coupon_product_restriction'),
    )

class CouponCategoryRestriction(Base, TimestampMixin):
    """Restricciones de cupones por categoría"""
    __tablename__ = 'coupon_category_restrictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey('coupons.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    is_included = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    coupon = relationship("Coupon", back_populates="category_restrictions")
    category = relationship("Category")
    
    # Índices
    __table_args__ = (
        Index('idx_coupon_category_restrictions_coupon', 'coupon_id'),
        Index('idx_coupon_category_restrictions_category', 'category_id'),
        UniqueConstraint('coupon_id', 'category_id', name='uq_coupon_category_restriction'),
    )

# ==============================================
# MODELOS DE CONFIGURACIÓN DEL SISTEMA
# ==============================================

class Setting(Base, TimestampMixin):
    """Configuraciones del sistema"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    type = Column(String(20), default='string', nullable=False)  # string, integer, boolean, json
    is_public = Column(Boolean, default=False, nullable=False)  # Si es accesible desde el frontend
    group_name = Column(String(50), nullable=True)  # Para agrupar configuraciones
    
    # Índices
    __table_args__ = (
        Index('idx_settings_key', 'key'),
        Index('idx_settings_group', 'group_name'),
        Index('idx_settings_public', 'is_public'),
        CheckConstraint("type IN ('string', 'integer', 'boolean', 'json', 'decimal')", 
                       name='ck_setting_type_valid'),
    )

class TaxRate(Base, TimestampMixin):
    """Tasas de impuestos por ubicación"""
    __tablename__ = 'tax_rates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    rate = Column(SQLDecimal(5, 4), nullable=False)  # Ej: 0.1900 para 19%
    
    # Ubicación geográfica
    country_id = Column(Integer, ForeignKey('countries.id', ondelete='CASCADE'), nullable=False)
    state_id = Column(Integer, ForeignKey('states.id', ondelete='CASCADE'), nullable=True)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=True)
    
    # Configuración
    is_active = Column(Boolean, default=True, nullable=False)
    applies_to_shipping = Column(Boolean, default=False, nullable=False)
    
    # Relaciones
    country = relationship("Country")
    state = relationship("State")
    city = relationship("City")
    
    # Índices
    __table_args__ = (
        Index('idx_tax_rates_country', 'country_id'),
        Index('idx_tax_rates_state', 'state_id'),
        Index('idx_tax_rates_city', 'city_id'),
        Index('idx_tax_rates_active', 'is_active'),
        CheckConstraint('rate >= 0 AND rate <= 1', name='ck_tax_rate_valid'),
    )

# ==============================================
# MODELOS DE NOTIFICACIONES
# ==============================================

class NotificationTemplate(Base, TimestampMixin):
    """Plantillas de notificaciones"""
    __tablename__ = 'notification_templates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    subject = Column(String(200), nullable=False)
    body_text = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # email, sms, push
    event = Column(String(100), nullable=False)  # order_confirmed, shipped, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    notifications = relationship("Notification", back_populates="template")
    
    # Índices
    __table_args__ = (
        Index('idx_notification_templates_event', 'event'),
        Index('idx_notification_templates_type', 'type'),
        Index('idx_notification_templates_active', 'is_active'),
    )

class Notification(Base, TimestampMixin):
    """Notificaciones enviadas"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey('notification_templates.id', ondelete='SET NULL'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Contenido
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    
    # Estado
    is_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Información adicional
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relaciones
    template = relationship("NotificationTemplate", back_populates="notifications")
    user = relationship("User")
    
    # Índices
    __table_args__ = (
        Index('idx_notifications_user', 'user_id'),
        Index('idx_notifications_sent', 'is_sent'),
        Index('idx_notifications_read', 'is_read'),
        Index('idx_notifications_created', 'created_at'),
        Index('idx_notifications_type', 'type'),
    )

# ==============================================
# MODELOS DE ANALYTICS Y MÉTRICAS
# ==============================================

class ProductView(Base, TimestampMixin):
    """Registro de visualizaciones de productos"""
    __tablename__ = 'product_views'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    session_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)
    
    # Relaciones
    product = relationship("Product")
    user = relationship("User")
    
    # Índices
    __table_args__ = (
        Index('idx_product_views_product', 'product_id'),
        Index('idx_product_views_user', 'user_id'),
        Index('idx_product_views_session', 'session_id'),
        Index('idx_product_views_created', 'created_at'),
        Index('idx_product_views_ip', 'ip_address'),
    )

class SearchQuery(Base, TimestampMixin):
    """Registro de búsquedas realizadas"""
    __tablename__ = 'search_queries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    session_id = Column(String(255), nullable=True)
    results_count = Column(Integer, default=0, nullable=False)
    clicked_product_id = Column(Integer, ForeignKey('products.id', ondelete='SET NULL'), nullable=True)
    
    # Relaciones
    user = relationship("User")
    clicked_product = relationship("Product")
    
    # Índices
    __table_args__ = (
        Index('idx_search_queries_query', 'query'),
        Index('idx_search_queries_user', 'user_id'),
        Index('idx_search_queries_session', 'session_id'),
        Index('idx_search_queries_created', 'created_at'),
        Index('idx_search_queries_results', 'results_count'),
    )

