"""
APIs de productos para eCommerce Modular
Endpoints para gestión completa del catálogo de productos
"""
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError, validate
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.catalog import Product, Category, Brand, ProductImage, ProductVariant, Attribute, ProductAttribute
from models.additional import Review
from services.auth_service import token_required, role_required, manager_required, rate_limit
from config.database import get_database_url

# Crear blueprint para productos
products_bp = Blueprint('products', __name__, url_prefix='/api/v1/products')

# Configurar base de datos
database_url = get_database_url()
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)

# Esquemas de validación
class ProductCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    slug = fields.Str(validate=validate.Length(max=255), allow_none=True)
    short_description = fields.Str(validate=validate.Length(max=500))
    description = fields.Str()
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    compare_price = fields.Decimal(validate=validate.Range(min=0), allow_none=True)
    cost_price = fields.Decimal(validate=validate.Range(min=0), allow_none=True)
    inventory_quantity = fields.Int(validate=validate.Range(min=0), missing=0)
    category_id = fields.Int(required=True)
    brand_id = fields.Int(allow_none=True)
    is_active = fields.Bool(missing=True)
    is_featured = fields.Bool(missing=False)
    weight = fields.Decimal(validate=validate.Range(min=0), allow_none=True)
    meta_title = fields.Str(validate=validate.Length(max=255))
    meta_description = fields.Str(validate=validate.Length(max=500))

class ProductUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    slug = fields.Str(validate=validate.Length(max=255))
    short_description = fields.Str(validate=validate.Length(max=500))
    description = fields.Str()
    price = fields.Decimal(validate=validate.Range(min=0))
    compare_price = fields.Decimal(validate=validate.Range(min=0), allow_none=True)
    cost_price = fields.Decimal(validate=validate.Range(min=0), allow_none=True)
    inventory_quantity = fields.Int(validate=validate.Range(min=0))
    category_id = fields.Int()
    brand_id = fields.Int(allow_none=True)
    is_active = fields.Bool()
    is_featured = fields.Bool()
    weight = fields.Decimal(validate=validate.Range(min=0), allow_none=True)
    meta_title = fields.Str(validate=validate.Length(max=255))
    meta_description = fields.Str(validate=validate.Length(max=500))

class ProductSearchSchema(Schema):
    q = fields.Str(validate=validate.Length(max=255))  # Query de búsqueda
    category_id = fields.Int()
    brand_id = fields.Int()
    min_price = fields.Decimal(validate=validate.Range(min=0))
    max_price = fields.Decimal(validate=validate.Range(min=0))
    is_featured = fields.Bool()
    is_active = fields.Bool(missing=True)
    sort_by = fields.Str(validate=validate.OneOf(['name', 'price', 'created_at', 'popularity']))
    sort_order = fields.Str(validate=validate.OneOf(['asc', 'desc']), missing='asc')
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=20)

# Instanciar esquemas
product_create_schema = ProductCreateSchema()
product_update_schema = ProductUpdateSchema()
product_search_schema = ProductSearchSchema()

def serialize_product(product, include_variants=False, include_reviews=False):
    """Serializa un producto a diccionario"""
    data = {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'short_description': product.short_description,
        'description': product.description,
        'sku': product.sku,
        'price': float(product.price) if product.price else None,
        'compare_price': float(product.compare_price) if product.compare_price else None,
        'cost_price': float(product.cost_price) if product.cost_price else None,
        'inventory_quantity': product.inventory_quantity,
        'category_id': product.category_id,
        'brand_id': product.brand_id,
        'is_active': product.is_active,
        'is_featured': product.is_featured,
        'weight': float(product.weight) if product.weight else None,
        'meta_title': product.meta_title,
        'meta_description': product.meta_description,
        'created_at': product.created_at.isoformat() if product.created_at else None,
        'updated_at': product.updated_at.isoformat() if product.updated_at else None
    }
    
    # Incluir categoría y marca si están cargadas
    if hasattr(product, 'category') and product.category:
        data['category'] = {
            'id': product.category.id,
            'name': product.category.name,
            'slug': product.category.slug
        }
    
    if hasattr(product, 'brand') and product.brand:
        data['brand'] = {
            'id': product.brand.id,
            'name': product.brand.name,
            'slug': product.brand.slug
        }
    
    # Incluir imágenes si están cargadas
    if hasattr(product, 'images') and product.images:
        data['images'] = [
            {
                'id': img.id,
                'image_url': img.image_url,
                'alt_text': img.alt_text,
                'is_primary': img.is_primary,
                'sort_order': img.sort_order
            }
            for img in sorted(product.images, key=lambda x: x.sort_order)
        ]
    
    # Incluir variantes si se solicita
    if include_variants and hasattr(product, 'variants') and product.variants:
        data['variants'] = [
            {
                'id': variant.id,
                'sku': variant.sku,
                'price': float(variant.price) if variant.price else None,
                'inventory_quantity': variant.inventory_quantity,
                'is_active': variant.is_active
            }
            for variant in product.variants
        ]
    
    # Incluir estadísticas de reseñas si se solicita
    if include_reviews:
        # Esto se calcularía en una consulta separada en producción
        data['review_stats'] = {
            'average_rating': 4.5,  # Placeholder
            'review_count': 10      # Placeholder
        }
    
    return data

@products_bp.route('', methods=['GET'])
@rate_limit(limit=100, window=300)  # 100 requests por 5 minutos
def get_products():
    """
    Obtener lista de productos con filtros y búsqueda
    ---
    tags:
      - Products
    parameters:
      - in: query
        name: q
        type: string
        description: Término de búsqueda
      - in: query
        name: category_id
        type: integer
        description: ID de categoría
      - in: query
        name: brand_id
        type: integer
        description: ID de marca
      - in: query
        name: min_price
        type: number
        description: Precio mínimo
      - in: query
        name: max_price
        type: number
        description: Precio máximo
      - in: query
        name: is_featured
        type: boolean
        description: Solo productos destacados
      - in: query
        name: sort_by
        type: string
        enum: [name, price, created_at, popularity]
        description: Campo de ordenamiento
      - in: query
        name: sort_order
        type: string
        enum: [asc, desc]
        description: Orden de clasificación
      - in: query
        name: page
        type: integer
        description: Número de página
      - in: query
        name: per_page
        type: integer
        description: Productos por página
    responses:
      200:
        description: Lista de productos
        schema:
          type: object
          properties:
            success:
              type: boolean
            products:
              type: array
            pagination:
              type: object
    """
    try:
        # Validar parámetros de búsqueda
        search_params = product_search_schema.load(request.args)
        
        session = Session()
        
        # Construir query base
        query = session.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images)
        )
        
        # Aplicar filtros
        if search_params.get('is_active') is not None:
            query = query.filter(Product.is_active == search_params['is_active'])
        
        if search_params.get('q'):
            search_term = f"%{search_params['q']}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )
        
        if search_params.get('category_id'):
            query = query.filter(Product.category_id == search_params['category_id'])
        
        if search_params.get('brand_id'):
            query = query.filter(Product.brand_id == search_params['brand_id'])
        
        if search_params.get('min_price'):
            query = query.filter(Product.price >= search_params['min_price'])
        
        if search_params.get('max_price'):
            query = query.filter(Product.price <= search_params['max_price'])
        
        if search_params.get('is_featured') is not None:
            query = query.filter(Product.is_featured == search_params['is_featured'])
        
        # Aplicar ordenamiento
        sort_by = search_params.get('sort_by', 'created_at')
        sort_order = search_params.get('sort_order', 'desc')
        
        if sort_by == 'name':
            order_field = Product.name
        elif sort_by == 'price':
            order_field = Product.price
        elif sort_by == 'created_at':
            order_field = Product.created_at
        else:
            order_field = Product.created_at
        
        if sort_order == 'desc':
            query = query.order_by(desc(order_field))
        else:
            query = query.order_by(asc(order_field))
        
        # Paginación
        page = search_params.get('page', 1)
        per_page = search_params.get('per_page', 20)
        
        total = query.count()
        products = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Serializar productos
        products_data = [serialize_product(product, include_reviews=True) for product in products]
        
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
            'products': products_data,
            'pagination': pagination,
            'filters_applied': {k: v for k, v in search_params.items() if v is not None}
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

@products_bp.route('/<int:product_id>', methods=['GET'])
@rate_limit(limit=200, window=300)  # 200 requests por 5 minutos
def get_product(product_id):
    """
    Obtener producto por ID
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
    responses:
      200:
        description: Detalles del producto
      404:
        description: Producto no encontrado
    """
    try:
        session = Session()
        
        product = session.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images),
            joinedload(Product.variants),
            joinedload(Product.attributes)
        ).filter_by(id=product_id).first()
        
        if not product:
            session.close()
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Serializar producto con todos los detalles
        product_data = serialize_product(product, include_variants=True, include_reviews=True)
        
        session.close()
        
        return jsonify({
            'success': True,
            'product': product_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@products_bp.route('', methods=['POST'])
@manager_required
@rate_limit(limit=50, window=3600, per='user')  # 50 productos por hora por usuario
def create_product():
    """
    Crear nuevo producto
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: body
        name: product_data
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            sku:
              type: string
            price:
              type: number
            category_id:
              type: integer
    responses:
      201:
        description: Producto creado exitosamente
      400:
        description: Datos inválidos
      401:
        description: No autorizado
      403:
        description: Permisos insuficientes
    """
    try:
        # Validar datos de entrada
        data = product_create_schema.load(request.json)
        
        session = Session()
        
        # Verificar que la categoría existe
        category = session.query(Category).filter_by(id=data['category_id']).first()
        if not category:
            session.close()
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 400
        
        # Verificar que el SKU no esté en uso
        existing_product = session.query(Product).filter_by(sku=data['sku']).first()
        if existing_product:
            session.close()
            return jsonify({
                'success': False,
                'error': 'SKU already exists'
            }), 400
        
        # Generar slug si no se proporciona
        if not data.get('slug'):
            data['slug'] = data['name'].lower().replace(' ', '-').replace('_', '-')
        
        # Crear producto
        product = Product(**data)
        session.add(product)
        session.commit()
        
        # Recargar con relaciones
        session.refresh(product)
        product = session.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand)
        ).filter_by(id=product.id).first()
        
        product_data = serialize_product(product)
        
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product': product_data
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

@products_bp.route('/<int:product_id>', methods=['PUT'])
@manager_required
@rate_limit(limit=100, window=3600, per='user')  # 100 updates por hora por usuario
def update_product(product_id):
    """
    Actualizar producto existente
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
      - in: body
        name: product_data
        required: true
    responses:
      200:
        description: Producto actualizado exitosamente
      404:
        description: Producto no encontrado
    """
    try:
        # Validar datos de entrada
        data = product_update_schema.load(request.json)
        
        session = Session()
        
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            session.close()
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Verificar categoría si se está actualizando
        if 'category_id' in data:
            category = session.query(Category).filter_by(id=data['category_id']).first()
            if not category:
                session.close()
                return jsonify({
                    'success': False,
                    'error': 'Category not found'
                }), 400
        
        # Actualizar campos
        for key, value in data.items():
            setattr(product, key, value)
        
        session.commit()
        
        # Recargar con relaciones
        product = session.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images)
        ).filter_by(id=product_id).first()
        
        product_data = serialize_product(product)
        
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'product': product_data
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

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@manager_required
@rate_limit(limit=20, window=3600, per='user')  # 20 eliminaciones por hora por usuario
def delete_product(product_id):
    """
    Eliminar producto (soft delete)
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
    responses:
      200:
        description: Producto eliminado exitosamente
      404:
        description: Producto no encontrado
    """
    try:
        session = Session()
        
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            session.close()
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Soft delete - marcar como inactivo
        product.is_active = False
        session.commit()
        
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@products_bp.route('/featured', methods=['GET'])
@rate_limit(limit=100, window=300)
def get_featured_products():
    """
    Obtener productos destacados
    ---
    tags:
      - Products
    parameters:
      - in: query
        name: limit
        type: integer
        description: Número máximo de productos (default: 10)
    responses:
      200:
        description: Lista de productos destacados
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Máximo 50 productos
        
        session = Session()
        
        products = session.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images)
        ).filter(
            Product.is_active == True,
            Product.is_featured == True
        ).order_by(desc(Product.created_at)).limit(limit).all()
        
        products_data = [serialize_product(product, include_reviews=True) for product in products]
        
        session.close()
        
        return jsonify({
            'success': True,
            'products': products_data,
            'count': len(products_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@products_bp.route('/search', methods=['GET'])
@rate_limit(limit=100, window=300)
def search_products():
    """
    Búsqueda avanzada de productos
    ---
    tags:
      - Products
    parameters:
      - in: query
        name: q
        type: string
        required: true
        description: Término de búsqueda
    responses:
      200:
        description: Resultados de búsqueda
    """
    try:
        query_term = request.args.get('q', '').strip()
        
        if not query_term:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        session = Session()
        
        # Búsqueda full-text (simplificada)
        search_term = f"%{query_term}%"
        
        products = session.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images)
        ).filter(
            and_(
                Product.is_active == True,
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )
        ).order_by(desc(Product.created_at)).limit(50).all()
        
        products_data = [serialize_product(product, include_reviews=True) for product in products]
        
        session.close()
        
        return jsonify({
            'success': True,
            'query': query_term,
            'products': products_data,
            'count': len(products_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Manejadores de errores específicos
@products_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@products_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'message': 'The request could not be understood by the server'
    }), 400

