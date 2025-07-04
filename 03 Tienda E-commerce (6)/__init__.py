"""
Archivo principal de modelos - Importa todos los modelos y configura relaciones
"""
from src.config.database import Base

# Importar todos los modelos para que SQLAlchemy los registre
from src.models.catalog import (
    User, Role, Permission, UserRole, RolePermission,
    Category, Brand, Product, ProductImage, 
    AttributeGroup, Attribute, ProductAttribute,
    ProductVariant, VariantAttribute
)

from src.models.orders import (
    Country, State, City, Address,
    Cart, CartItem,
    Order, OrderItem, OrderStatusHistory,
    Payment, PaymentRefund,
    ShippingMethod, Shipment, ShipmentTracking
)

from src.models.additional import (
    Review, ReviewHelpfulness,
    WishlistItem,
    Coupon, CouponUsage, CouponProductRestriction, CouponCategoryRestriction,
    Setting, TaxRate,
    NotificationTemplate, Notification,
    ProductView, SearchQuery
)

# Lista de todos los modelos para facilitar importaciones
__all__ = [
    # Usuarios y autenticación
    'User', 'Role', 'Permission', 'UserRole', 'RolePermission',
    
    # Catálogo de productos
    'Category', 'Brand', 'Product', 'ProductImage',
    'AttributeGroup', 'Attribute', 'ProductAttribute',
    'ProductVariant', 'VariantAttribute',
    
    # Ubicaciones geográficas
    'Country', 'State', 'City', 'Address',
    
    # Carrito y pedidos
    'Cart', 'CartItem',
    'Order', 'OrderItem', 'OrderStatusHistory',
    
    # Pagos y envíos
    'Payment', 'PaymentRefund',
    'ShippingMethod', 'Shipment', 'ShipmentTracking',
    
    # Funcionalidades adicionales
    'Review', 'ReviewHelpfulness',
    'WishlistItem',
    'Coupon', 'CouponUsage', 'CouponProductRestriction', 'CouponCategoryRestriction',
    
    # Configuración y sistema
    'Setting', 'TaxRate',
    'NotificationTemplate', 'Notification',
    
    # Analytics
    'ProductView', 'SearchQuery',
    
    # Base para crear nuevos modelos
    'Base'
]

def get_all_models():
    """Retorna una lista de todas las clases de modelo"""
    return [
        User, Role, Permission, UserRole, RolePermission,
        Category, Brand, Product, ProductImage,
        AttributeGroup, Attribute, ProductAttribute,
        ProductVariant, VariantAttribute,
        Country, State, City, Address,
        Cart, CartItem,
        Order, OrderItem, OrderStatusHistory,
        Payment, PaymentRefund,
        ShippingMethod, Shipment, ShipmentTracking,
        Review, ReviewHelpfulness,
        WishlistItem,
        Coupon, CouponUsage, CouponProductRestriction, CouponCategoryRestriction,
        Setting, TaxRate,
        NotificationTemplate, Notification,
        ProductView, SearchQuery
    ]

def get_model_by_name(model_name: str):
    """Obtiene una clase de modelo por su nombre"""
    models_dict = {model.__name__: model for model in get_all_models()}
    return models_dict.get(model_name)

def get_table_names():
    """Retorna una lista de todos los nombres de tablas"""
    return [model.__tablename__ for model in get_all_models()]

