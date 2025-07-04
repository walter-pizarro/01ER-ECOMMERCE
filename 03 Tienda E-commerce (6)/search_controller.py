"""
Controlador de búsqueda avanzada para productos.

Este controlador proporciona endpoints para:
- Búsqueda avanzada de productos con filtros
- Autocompletado de búsqueda
- Reindexación de productos
"""

from flask import Blueprint, request, jsonify
from src.services.search_service import search_service
from src.models.catalog import Product, Category, Brand, ProductImage, ProductVariant, ProductAttribute
from src.middleware.auth_middleware import admin_required, jwt_required
from sqlalchemy.orm import joinedload
from src.config.database import db_session
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear blueprint
search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('/products', methods=['GET'])
def search_products():
    """
    Endpoint para búsqueda avanzada de productos.
    
    Query params:
    - q: Texto de búsqueda
    - category_id: ID de categoría
    - brand_id: ID de marca
    - price_min: Precio mínimo
    - price_max: Precio máximo
    - rating_min: Rating mínimo
    - in_stock: Si solo se muestran productos en stock (true/false)
    - is_featured: Si solo se muestran productos destacados (true/false)
    - is_new: Si solo se muestran productos nuevos (true/false)
    - is_sale: Si solo se muestran productos en oferta (true/false)
    - attributes: Atributos en formato JSON {nombre: [valores]}
    - sort_by: Campo por el cual ordenar
    - sort_order: Orden (asc/desc)
    - page: Número de página
    - page_size: Tamaño de página
    - facets: Si se incluyen facetas (true/false)
    """
    try:
        # Obtener parámetros de búsqueda
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)  # Limitar a 100 máximo
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        include_facets = request.args.get('facets', 'true').lower() == 'true'
        
        # Construir filtros
        filters = {}
        
        # Filtros básicos
        if 'category_id' in request.args:
            filters['category_id'] = int(request.args.get('category_id'))
        
        if 'brand_id' in request.args:
            filters['brand_id'] = int(request.args.get('brand_id'))
        
        if 'price_min' in request.args:
            filters['price_min'] = float(request.args.get('price_min'))
        
        if 'price_max' in request.args:
            filters['price_max'] = float(request.args.get('price_max'))
        
        if 'rating_min' in request.args:
            filters['rating_min'] = float(request.args.get('rating_min'))
        
        if 'in_stock' in request.args:
            filters['in_stock'] = request.args.get('in_stock').lower() == 'true'
        
        if 'is_featured' in request.args:
            filters['is_featured'] = request.args.get('is_featured').lower() == 'true'
        
        if 'is_new' in request.args:
            filters['is_new'] = request.args.get('is_new').lower() == 'true'
        
        if 'is_sale' in request.args:
            filters['is_sale'] = request.args.get('is_sale').lower() == 'true'
        
        # Filtros de atributos (formato JSON)
        if 'attributes' in request.args:
            try:
                import json
                attributes = json.loads(request.args.get('attributes'))
                if isinstance(attributes, dict):
                    filters['attributes'] = attributes
            except Exception as e:
                logger.warning(f"Error al parsear atributos: {str(e)}")
        
        # Realizar búsqueda
        result = search_service.search_products(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            include_facets=include_facets
        )
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        logger.error(f"Error en búsqueda: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@search_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """
    Endpoint para autocompletado de búsqueda.
    
    Query params:
    - q: Texto parcial para autocompletar
    - limit: Número máximo de sugerencias
    """
    try:
        query = request.args.get('q', '')
        limit = min(int(request.args.get('limit', 10)), 20)  # Limitar a 20 máximo
        
        if not query or len(query) < 2:
            return jsonify({
                "success": True,
                "data": []
            })
        
        suggestions = search_service.autocomplete(query, limit)
        
        return jsonify({
            "success": True,
            "data": suggestions
        })
    
    except Exception as e:
        logger.error(f"Error en autocompletado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@search_bp.route('/reindex', methods=['POST'])
@admin_required
def reindex_products():
    """
    Endpoint para reindexar todos los productos.
    Solo accesible para administradores.
    """
    try:
        # Obtener todos los productos con sus relaciones
        products_query = db_session.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images),
            joinedload(Product.variants),
            joinedload(Product.attributes)
        )
        
        products = products_query.all()
        
        # Convertir productos a formato para Elasticsearch
        es_products = []
        
        for product in products:
            es_product = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "sku": product.sku,
                "price": float(product.price),
                "sale_price": float(product.sale_price) if product.sale_price else None,
                "category_id": product.category_id,
                "category_name": product.category.name if product.category else None,
                "brand_id": product.brand_id,
                "brand_name": product.brand.name if product.brand else None,
                "tags": product.tags.split(',') if product.tags else [],
                "rating": float(product.rating) if product.rating else 0.0,
                "stock": product.stock,
                "is_featured": product.is_featured,
                "is_new": product.is_new,
                "is_sale": product.is_sale,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None,
                "images": [
                    {
                        "id": image.id,
                        "image_url": image.image_url,
                        "alt_text": image.alt_text
                    }
                    for image in product.images
                ],
                "variants": [
                    {
                        "id": variant.id,
                        "sku": variant.sku,
                        "color": variant.color,
                        "size": variant.size,
                        "price": float(variant.price),
                        "stock": variant.stock
                    }
                    for variant in product.variants
                ],
                "attributes": [
                    {
                        "name": attr.name,
                        "value": attr.value
                    }
                    for attr in product.attributes
                ]
            }
            
            es_products.append(es_product)
        
        # Reindexar productos
        result = search_service.reindex_all_products(es_products)
        
        return jsonify({
            "success": result['success'],
            "message": result['message'],
            "stats": result['stats']
        })
    
    except Exception as e:
        logger.error(f"Error en reindexación: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@search_bp.route('/index-product/<int:product_id>', methods=['POST'])
@admin_required
def index_product(product_id):
    """
    Endpoint para indexar un producto específico.
    Solo accesible para administradores.
    """
    try:
        # Obtener producto con sus relaciones
        product = db_session.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images),
            joinedload(Product.variants),
            joinedload(Product.attributes)
        ).filter(Product.id == product_id).first()
        
        if not product:
            return jsonify({
                "success": False,
                "error": f"Producto con ID {product_id} no encontrado"
            }), 404
        
        # Convertir producto a formato para Elasticsearch
        es_product = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "sku": product.sku,
            "price": float(product.price),
            "sale_price": float(product.sale_price) if product.sale_price else None,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else None,
            "brand_id": product.brand_id,
            "brand_name": product.brand.name if product.brand else None,
            "tags": product.tags.split(',') if product.tags else [],
            "rating": float(product.rating) if product.rating else 0.0,
            "stock": product.stock,
            "is_featured": product.is_featured,
            "is_new": product.is_new,
            "is_sale": product.is_sale,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
            "images": [
                {
                    "id": image.id,
                    "image_url": image.image_url,
                    "alt_text": image.alt_text
                }
                for image in product.images
            ],
            "variants": [
                {
                    "id": variant.id,
                    "sku": variant.sku,
                    "color": variant.color,
                    "size": variant.size,
                    "price": float(variant.price),
                    "stock": variant.stock
                }
                for variant in product.variants
            ],
            "attributes": [
                {
                    "name": attr.name,
                    "value": attr.value
                }
                for attr in product.attributes
            ]
        }
        
        # Indexar producto
        success = search_service.index_product(es_product)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Producto {product_id} indexado correctamente"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Error al indexar producto {product_id}"
            }), 500
    
    except Exception as e:
        logger.error(f"Error al indexar producto {product_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@search_bp.route('/delete-product/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product_from_index(product_id):
    """
    Endpoint para eliminar un producto del índice.
    Solo accesible para administradores.
    """
    try:
        success = search_service.delete_product(product_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Producto {product_id} eliminado del índice correctamente"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Error al eliminar producto {product_id} del índice"
            }), 500
    
    except Exception as e:
        logger.error(f"Error al eliminar producto {product_id} del índice: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@search_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar el estado del servicio de búsqueda.
    """
    try:
        health = search_service.health_check()
        
        if health['status'] == 'ok':
            return jsonify({
                "success": True,
                "data": health
            })
        else:
            return jsonify({
                "success": False,
                "error": health['message']
            }), 500
    
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

