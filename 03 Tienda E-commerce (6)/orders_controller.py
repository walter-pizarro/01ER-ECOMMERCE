"""
APIs de pedidos para eCommerce Modular
Endpoints para gestión completa de pedidos y transacciones
"""
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError, validate
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from datetime import datetime, timezone
from decimal import Decimal

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.orders import Order, OrderItem, OrderStatusHistory, Payment, PaymentRefund, Shipment, ShipmentTracking
from models.catalog import Product, User
from services.auth_service import token_required, role_required, manager_required, rate_limit
from config.database import get_database_url

# Crear blueprint para pedidos
orders_bp = Blueprint('orders', __name__, url_prefix='/api/v1/orders')

# Configurar base de datos
database_url = get_database_url()
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)

# Esquemas de validación
class OrderItemSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unit_price = fields.Decimal(validate=validate.Range(min=0), allow_none=True)

class OrderCreateSchema(Schema):
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))
    shipping_address_id = fields.Int(required=True)
    billing_address_id = fields.Int(allow_none=True)
    shipping_method_id = fields.Int(required=True)
    notes = fields.Str(validate=validate.Length(max=1000))
    coupon_code = fields.Str(validate=validate.Length(max=50))

class OrderUpdateSchema(Schema):
    status = fields.Str(validate=validate.OneOf(['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']))
    notes = fields.Str(validate=validate.Length(max=1000))

class PaymentCreateSchema(Schema):
    order_id = fields.Int(required=True)
    payment_method = fields.Str(required=True, validate=validate.OneOf(['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash']))
    amount = fields.Decimal(required=True, validate=validate.Range(min=0))
    currency = fields.Str(missing='USD', validate=validate.Length(equal=3))
    transaction_id = fields.Str(validate=validate.Length(max=255))
    gateway_response = fields.Dict()

# Instanciar esquemas
order_create_schema = OrderCreateSchema()
order_update_schema = OrderUpdateSchema()
payment_create_schema = PaymentCreateSchema()

def serialize_order(order, include_items=True, include_payments=False, include_shipments=False):
    """Serializa un pedido a diccionario"""
    data = {
        'id': order.id,
        'order_number': order.order_number,
        'user_id': order.user_id,
        'status': order.status,
        'subtotal': float(order.subtotal) if order.subtotal else None,
        'tax_amount': float(order.tax_amount) if order.tax_amount else None,
        'shipping_amount': float(order.shipping_amount) if order.shipping_amount else None,
        'discount_amount': float(order.discount_amount) if order.discount_amount else None,
        'total_amount': float(order.total_amount) if order.total_amount else None,
        'currency': order.currency,
        'notes': order.notes,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'updated_at': order.updated_at.isoformat() if order.updated_at else None
    }
    
    # Incluir información del usuario si está cargada
    if hasattr(order, 'user') and order.user:
        data['user'] = {
            'id': order.user.id,
            'email': order.user.email,
            'first_name': order.user.first_name,
            'last_name': order.user.last_name
        }
    
    # Incluir items del pedido
    if include_items and hasattr(order, 'items') and order.items:
        data['items'] = []
        for item in order.items:
            item_data = {
                'id': item.id,
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price) if item.unit_price else None,
                'total_price': float(item.total_price) if item.total_price else None
            }
            
            # Incluir información del producto si está cargada
            if hasattr(item, 'product') and item.product:
                item_data['product'] = {
                    'id': item.product.id,
                    'name': item.product.name,
                    'sku': item.product.sku,
                    'image_url': item.product.images[0].image_url if item.product.images else None
                }
            
            data['items'].append(item_data)
    
    # Incluir pagos si se solicita
    if include_payments and hasattr(order, 'payments') and order.payments:
        data['payments'] = [
            {
                'id': payment.id,
                'payment_method': payment.payment_method,
                'amount': float(payment.amount) if payment.amount else None,
                'status': payment.status,
                'transaction_id': payment.transaction_id,
                'created_at': payment.created_at.isoformat() if payment.created_at else None
            }
            for payment in order.payments
        ]
    
    # Incluir envíos si se solicita
    if include_shipments and hasattr(order, 'shipments') and order.shipments:
        data['shipments'] = [
            {
                'id': shipment.id,
                'tracking_number': shipment.tracking_number,
                'carrier': shipment.carrier,
                'status': shipment.status,
                'shipped_at': shipment.shipped_at.isoformat() if shipment.shipped_at else None,
                'delivered_at': shipment.delivered_at.isoformat() if shipment.delivered_at else None
            }
            for shipment in order.shipments
        ]
    
    return data

def calculate_order_totals(items, shipping_amount=0, tax_rate=0.1, discount_amount=0):
    """Calcula los totales del pedido"""
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = subtotal * Decimal(str(tax_rate))
    total_amount = subtotal + tax_amount + Decimal(str(shipping_amount)) - Decimal(str(discount_amount))
    
    return {
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'shipping_amount': Decimal(str(shipping_amount)),
        'discount_amount': Decimal(str(discount_amount)),
        'total_amount': total_amount
    }

@orders_bp.route('', methods=['GET'])
@token_required
@rate_limit(limit=100, window=300, per='user')
def get_orders():
    """
    Obtener pedidos del usuario actual
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        description: Filtrar por estado
      - in: query
        name: page
        type: integer
        description: Número de página
      - in: query
        name: per_page
        type: integer
        description: Pedidos por página
    responses:
      200:
        description: Lista de pedidos del usuario
    """
    try:
        # Parámetros de consulta
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        session = Session()
        
        # Construir query
        query = session.query(Order).options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product)
        ).filter(Order.user_id == request.current_user.id)
        
        # Filtrar por estado si se especifica
        if status:
            query = query.filter(Order.status == status)
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(desc(Order.created_at))
        
        # Paginación
        total = query.count()
        orders = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Serializar pedidos
        orders_data = [serialize_order(order, include_items=True) for order in orders]
        
        # Información de paginación
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page * per_page < total
        }
        
        session.close()
        
        return jsonify({
            'success': True,
            'orders': orders_data,
            'pagination': pagination
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@token_required
@rate_limit(limit=200, window=300, per='user')
def get_order(order_id):
    """
    Obtener detalles de un pedido específico
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
    responses:
      200:
        description: Detalles del pedido
      404:
        description: Pedido no encontrado
      403:
        description: Sin permisos para ver este pedido
    """
    try:
        session = Session()
        
        # Obtener pedido con todas las relaciones
        order = session.query(Order).options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.payments),
            joinedload(Order.shipments)
        ).filter_by(id=order_id).first()
        
        if not order:
            session.close()
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        # Verificar permisos (usuario propietario o admin/manager)
        user_roles = request.current_user_roles
        if order.user_id != request.current_user.id and not any(role in user_roles for role in ['admin', 'manager']):
            session.close()
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        # Serializar pedido con todos los detalles
        order_data = serialize_order(order, include_items=True, include_payments=True, include_shipments=True)
        
        session.close()
        
        return jsonify({
            'success': True,
            'order': order_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@orders_bp.route('', methods=['POST'])
@token_required
@rate_limit(limit=10, window=3600, per='user')  # 10 pedidos por hora por usuario
def create_order():
    """
    Crear nuevo pedido
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - in: body
        name: order_data
        required: true
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                  quantity:
                    type: integer
            shipping_address_id:
              type: integer
            shipping_method_id:
              type: integer
    responses:
      201:
        description: Pedido creado exitosamente
      400:
        description: Datos inválidos
    """
    try:
        # Validar datos de entrada
        data = order_create_schema.load(request.json)
        
        session = Session()
        
        # Verificar que todos los productos existen y están disponibles
        product_ids = [item['product_id'] for item in data['items']]
        products = session.query(Product).filter(
            Product.id.in_(product_ids),
            Product.is_active == True
        ).all()
        
        if len(products) != len(product_ids):
            session.close()
            return jsonify({
                'success': False,
                'error': 'One or more products are not available'
            }), 400
        
        # Crear diccionario de productos para fácil acceso
        products_dict = {p.id: p for p in products}
        
        # Verificar inventario y calcular precios
        order_items_data = []
        for item_data in data['items']:
            product = products_dict[item_data['product_id']]
            
            # Verificar inventario
            if product.inventory_quantity < item_data['quantity']:
                session.close()
                return jsonify({
                    'success': False,
                    'error': f'Insufficient inventory for product {product.name}'
                }), 400
            
            # Usar precio actual del producto si no se especifica
            unit_price = item_data.get('unit_price', product.price)
            
            order_items_data.append({
                'product_id': product.id,
                'quantity': item_data['quantity'],
                'unit_price': unit_price,
                'total_price': unit_price * item_data['quantity']
            })
        
        # Calcular totales del pedido
        totals = calculate_order_totals(order_items_data, shipping_amount=10.00)  # $10 shipping por defecto
        
        # Generar número de pedido único
        import uuid
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear pedido
        order = Order(
            order_number=order_number,
            user_id=request.current_user.id,
            status='pending',
            subtotal=totals['subtotal'],
            tax_amount=totals['tax_amount'],
            shipping_amount=totals['shipping_amount'],
            discount_amount=totals['discount_amount'],
            total_amount=totals['total_amount'],
            currency='USD',
            notes=data.get('notes')
        )
        
        session.add(order)
        session.flush()  # Para obtener el ID del pedido
        
        # Crear items del pedido
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                **item_data
            )
            session.add(order_item)
        
        # Actualizar inventario de productos
        for item_data in order_items_data:
            product = products_dict[item_data['product_id']]
            product.inventory_quantity -= item_data['quantity']
        
        # Crear historial de estado
        status_history = OrderStatusHistory(
            order_id=order.id,
            status='pending',
            notes='Order created'
        )
        session.add(status_history)
        
        session.commit()
        
        # Recargar pedido con relaciones
        order = session.query(Order).options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product)
        ).filter_by(id=order.id).first()
        
        order_data = serialize_order(order, include_items=True)
        
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': order_data
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@manager_required
@rate_limit(limit=100, window=3600, per='user')
def update_order_status(order_id):
    """
    Actualizar estado del pedido (solo managers/admins)
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
      - in: body
        name: status_data
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [pending, confirmed, processing, shipped, delivered, cancelled]
            notes:
              type: string
    responses:
      200:
        description: Estado actualizado exitosamente
      404:
        description: Pedido no encontrado
    """
    try:
        # Validar datos de entrada
        data = order_update_schema.load(request.json)
        
        session = Session()
        
        order = session.query(Order).filter_by(id=order_id).first()
        if not order:
            session.close()
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        # Actualizar estado
        old_status = order.status
        order.status = data['status']
        if 'notes' in data:
            order.notes = data['notes']
        
        # Crear historial de estado
        status_history = OrderStatusHistory(
            order_id=order.id,
            status=data['status'],
            notes=data.get('notes', f'Status changed from {old_status} to {data["status"]}')
        )
        session.add(status_history)
        
        session.commit()
        
        # Recargar pedido
        order = session.query(Order).options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product)
        ).filter_by(id=order_id).first()
        
        order_data = serialize_order(order, include_items=True)
        
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully',
            'order': order_data
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@token_required
@rate_limit(limit=5, window=3600, per='user')  # 5 cancelaciones por hora
def cancel_order(order_id):
    """
    Cancelar pedido (solo si está en estado pending o confirmed)
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
    responses:
      200:
        description: Pedido cancelado exitosamente
      400:
        description: No se puede cancelar el pedido
      404:
        description: Pedido no encontrado
    """
    try:
        session = Session()
        
        order = session.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product)
        ).filter_by(id=order_id).first()
        
        if not order:
            session.close()
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        # Verificar permisos
        user_roles = request.current_user_roles
        if order.user_id != request.current_user.id and not any(role in user_roles for role in ['admin', 'manager']):
            session.close()
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        # Verificar que se puede cancelar
        if order.status not in ['pending', 'confirmed']:
            session.close()
            return jsonify({
                'success': False,
                'error': f'Cannot cancel order with status: {order.status}'
            }), 400
        
        # Actualizar estado
        order.status = 'cancelled'
        
        # Restaurar inventario
        for item in order.items:
            item.product.inventory_quantity += item.quantity
        
        # Crear historial de estado
        status_history = OrderStatusHistory(
            order_id=order.id,
            status='cancelled',
            notes='Order cancelled by user'
        )
        session.add(status_history)
        
        session.commit()
        
        order_data = serialize_order(order, include_items=True)
        
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Order cancelled successfully',
            'order': order_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@orders_bp.route('/admin', methods=['GET'])
@manager_required
@rate_limit(limit=100, window=300, per='user')
def get_all_orders():
    """
    Obtener todos los pedidos (solo managers/admins)
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        description: Filtrar por estado
      - in: query
        name: user_id
        type: integer
        description: Filtrar por usuario
      - in: query
        name: page
        type: integer
        description: Número de página
      - in: query
        name: per_page
        type: integer
        description: Pedidos por página
    responses:
      200:
        description: Lista de todos los pedidos
    """
    try:
        # Parámetros de consulta
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        session = Session()
        
        # Construir query
        query = session.query(Order).options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product)
        )
        
        # Aplicar filtros
        if status:
            query = query.filter(Order.status == status)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(desc(Order.created_at))
        
        # Paginación
        total = query.count()
        orders = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Serializar pedidos
        orders_data = [serialize_order(order, include_items=True) for order in orders]
        
        # Información de paginación
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page * per_page < total
        }
        
        session.close()
        
        return jsonify({
            'success': True,
            'orders': orders_data,
            'pagination': pagination
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Manejadores de errores específicos
@orders_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': 'The requested order was not found'
    }), 404

@orders_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 'Forbidden',
        'message': 'Insufficient permissions to access this order'
    }), 403

