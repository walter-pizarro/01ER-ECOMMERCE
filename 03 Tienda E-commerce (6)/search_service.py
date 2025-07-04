"""
Servicio de búsqueda avanzada con Elasticsearch.

Este servicio proporciona funcionalidades de búsqueda avanzada para productos
utilizando Elasticsearch como motor de búsqueda. Incluye:
- Búsqueda full-text con relevancia
- Filtros facetados
- Autocompletado
- Corrección de errores ortográficos
- Búsqueda por sinónimos
"""

import os
import json
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from typing import Dict, List, Any, Optional, Union
import logging

# Configurar logger
logger = logging.getLogger(__name__)

class SearchService:
    """Servicio de búsqueda con Elasticsearch para productos."""
    
    def __init__(self):
        """Inicializa la conexión con Elasticsearch."""
        self.es_host = os.environ.get('ELASTICSEARCH_HOST', 'elasticsearch')
        self.es_port = os.environ.get('ELASTICSEARCH_PORT', '9200')
        self.es_user = os.environ.get('ELASTICSEARCH_USER', '')
        self.es_pass = os.environ.get('ELASTICSEARCH_PASSWORD', '')
        
        # Configurar cliente de Elasticsearch
        if self.es_user and self.es_pass:
            self.es = Elasticsearch(
                [f'http://{self.es_host}:{self.es_port}'],
                http_auth=(self.es_user, self.es_pass)
            )
        else:
            self.es = Elasticsearch([f'http://{self.es_host}:{self.es_port}'])
        
        # Índice de productos
        self.index_name = 'products'
        
        # Crear índice si no existe
        self._create_index_if_not_exists()
    
    def _create_index_if_not_exists(self) -> None:
        """Crea el índice de productos si no existe."""
        try:
            if not self.es.indices.exists(index=self.index_name):
                # Definición del mapeo para productos
                mapping = {
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "spanish_analyzer": {
                                    "type": "spanish",
                                    "stopwords": "_spanish_"
                                },
                                "autocomplete": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "autocomplete_filter"]
                                }
                            },
                            "filter": {
                                "autocomplete_filter": {
                                    "type": "edge_ngram",
                                    "min_gram": 1,
                                    "max_gram": 20
                                }
                            }
                        },
                        "number_of_shards": 1,
                        "number_of_replicas": 1
                    },
                    "mappings": {
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {
                                "type": "text",
                                "analyzer": "spanish_analyzer",
                                "fields": {
                                    "autocomplete": {
                                        "type": "text",
                                        "analyzer": "autocomplete"
                                    },
                                    "keyword": {
                                        "type": "keyword"
                                    }
                                }
                            },
                            "description": {
                                "type": "text",
                                "analyzer": "spanish_analyzer"
                            },
                            "sku": {
                                "type": "keyword"
                            },
                            "price": {
                                "type": "float"
                            },
                            "sale_price": {
                                "type": "float"
                            },
                            "category_id": {
                                "type": "integer"
                            },
                            "category_name": {
                                "type": "keyword"
                            },
                            "brand_id": {
                                "type": "integer"
                            },
                            "brand_name": {
                                "type": "keyword"
                            },
                            "tags": {
                                "type": "keyword"
                            },
                            "rating": {
                                "type": "float"
                            },
                            "stock": {
                                "type": "integer"
                            },
                            "is_featured": {
                                "type": "boolean"
                            },
                            "is_new": {
                                "type": "boolean"
                            },
                            "is_sale": {
                                "type": "boolean"
                            },
                            "created_at": {
                                "type": "date"
                            },
                            "updated_at": {
                                "type": "date"
                            },
                            "images": {
                                "type": "nested",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "image_url": {"type": "keyword"},
                                    "alt_text": {"type": "text"}
                                }
                            },
                            "variants": {
                                "type": "nested",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "sku": {"type": "keyword"},
                                    "color": {"type": "keyword"},
                                    "size": {"type": "keyword"},
                                    "price": {"type": "float"},
                                    "stock": {"type": "integer"}
                                }
                            },
                            "attributes": {
                                "type": "nested",
                                "properties": {
                                    "name": {"type": "keyword"},
                                    "value": {"type": "keyword"}
                                }
                            }
                        }
                    }
                }
                
                # Crear índice con mapeo
                self.es.indices.create(index=self.index_name, body=mapping)
                logger.info(f"Índice '{self.index_name}' creado exitosamente")
        except Exception as e:
            logger.error(f"Error al crear índice: {str(e)}")
    
    def index_product(self, product: Dict[str, Any]) -> bool:
        """
        Indexa un producto en Elasticsearch.
        
        Args:
            product: Diccionario con los datos del producto
            
        Returns:
            bool: True si la indexación fue exitosa, False en caso contrario
        """
        try:
            self.es.index(
                index=self.index_name,
                id=product['id'],
                body=product,
                refresh=True
            )
            return True
        except Exception as e:
            logger.error(f"Error al indexar producto {product.get('id')}: {str(e)}")
            return False
    
    def bulk_index_products(self, products: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Indexa múltiples productos en Elasticsearch usando bulk API.
        
        Args:
            products: Lista de diccionarios con los datos de los productos
            
        Returns:
            Dict: Estadísticas de la operación bulk
        """
        if not products:
            return {"total": 0, "success": 0, "failed": 0}
        
        try:
            bulk_data = []
            for product in products:
                # Acción de indexación
                bulk_data.append({"index": {"_index": self.index_name, "_id": product['id']}})
                # Documento a indexar
                bulk_data.append(product)
            
            # Ejecutar operación bulk
            response = self.es.bulk(body=bulk_data, refresh=True)
            
            # Contar éxitos y fallos
            success_count = 0
            failed_count = 0
            
            for item in response['items']:
                if 'index' in item and item['index'].get('status') >= 200 and item['index'].get('status') < 300:
                    success_count += 1
                else:
                    failed_count += 1
            
            return {
                "total": len(products),
                "success": success_count,
                "failed": failed_count
            }
        except Exception as e:
            logger.error(f"Error en bulk indexing: {str(e)}")
            return {"total": len(products), "success": 0, "failed": len(products)}
    
    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto del índice.
        
        Args:
            product_id: ID del producto a eliminar
            
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            self.es.delete(
                index=self.index_name,
                id=product_id,
                refresh=True
            )
            return True
        except NotFoundError:
            logger.warning(f"Producto {product_id} no encontrado en el índice")
            return False
        except Exception as e:
            logger.error(f"Error al eliminar producto {product_id}: {str(e)}")
            return False
    
    def search_products(
        self,
        query: str = None,
        filters: Dict[str, Any] = None,
        sort_by: str = None,
        sort_order: str = 'asc',
        page: int = 1,
        page_size: int = 20,
        include_facets: bool = True
    ) -> Dict[str, Any]:
        """
        Busca productos con filtros avanzados.
        
        Args:
            query: Texto de búsqueda
            filters: Diccionario de filtros (categoría, marca, precio, etc.)
            sort_by: Campo por el cual ordenar
            sort_order: Orden (asc o desc)
            page: Número de página
            page_size: Tamaño de página
            include_facets: Si se deben incluir facetas en los resultados
            
        Returns:
            Dict: Resultados de la búsqueda con productos y facetas
        """
        try:
            # Calcular offset para paginación
            from_val = (page - 1) * page_size
            
            # Construir query base
            search_body = {
                "from": from_val,
                "size": page_size,
                "track_total_hits": True
            }
            
            # Construir query de búsqueda
            must_clauses = []
            filter_clauses = []
            
            # Búsqueda por texto
            if query:
                must_clauses.append({
                    "multi_match": {
                        "query": query,
                        "fields": ["name^3", "name.autocomplete^2", "description", "brand_name", "category_name", "tags"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
            
            # Aplicar filtros
            if filters:
                # Filtro de categoría
                if 'category_id' in filters:
                    filter_clauses.append({"term": {"category_id": filters['category_id']}})
                
                # Filtro de marca
                if 'brand_id' in filters:
                    filter_clauses.append({"term": {"brand_id": filters['brand_id']}})
                
                # Filtro de precio
                if 'price_min' in filters or 'price_max' in filters:
                    price_filter = {"range": {"price": {}}}
                    if 'price_min' in filters:
                        price_filter["range"]["price"]["gte"] = filters['price_min']
                    if 'price_max' in filters:
                        price_filter["range"]["price"]["lte"] = filters['price_max']
                    filter_clauses.append(price_filter)
                
                # Filtro de rating
                if 'rating_min' in filters:
                    filter_clauses.append({"range": {"rating": {"gte": filters['rating_min']}}})
                
                # Filtro de stock
                if 'in_stock' in filters and filters['in_stock']:
                    filter_clauses.append({"range": {"stock": {"gt": 0}}})
                
                # Filtros de estado
                if 'is_featured' in filters:
                    filter_clauses.append({"term": {"is_featured": filters['is_featured']}})
                if 'is_new' in filters:
                    filter_clauses.append({"term": {"is_new": filters['is_new']}})
                if 'is_sale' in filters:
                    filter_clauses.append({"term": {"is_sale": filters['is_sale']}})
                
                # Filtros de atributos (color, tamaño, etc.)
                if 'attributes' in filters and isinstance(filters['attributes'], dict):
                    for attr_name, attr_values in filters['attributes'].items():
                        if isinstance(attr_values, list):
                            filter_clauses.append({
                                "nested": {
                                    "path": "attributes",
                                    "query": {
                                        "bool": {
                                            "must": [
                                                {"term": {"attributes.name": attr_name}},
                                                {"terms": {"attributes.value": attr_values}}
                                            ]
                                        }
                                    }
                                }
                            })
            
            # Construir query completa
            search_body["query"] = {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses
                }
            }
            
            # Ordenamiento
            if sort_by:
                sort_direction = "desc" if sort_order.lower() == 'desc' else "asc"
                search_body["sort"] = [{sort_by: {"order": sort_direction}}]
            
            # Agregar facetas (agregaciones)
            if include_facets:
                search_body["aggs"] = {
                    "categories": {
                        "terms": {"field": "category_name", "size": 30}
                    },
                    "brands": {
                        "terms": {"field": "brand_name", "size": 30}
                    },
                    "price_ranges": {
                        "range": {
                            "field": "price",
                            "ranges": [
                                {"to": 50},
                                {"from": 50, "to": 100},
                                {"from": 100, "to": 200},
                                {"from": 200, "to": 500},
                                {"from": 500}
                            ]
                        }
                    },
                    "ratings": {
                        "range": {
                            "field": "rating",
                            "ranges": [
                                {"from": 4, "to": 5},
                                {"from": 3, "to": 4},
                                {"from": 2, "to": 3},
                                {"from": 1, "to": 2},
                                {"from": 0, "to": 1}
                            ]
                        }
                    },
                    "attributes": {
                        "nested": {"path": "attributes"},
                        "aggs": {
                            "attribute_names": {
                                "terms": {"field": "attributes.name", "size": 20},
                                "aggs": {
                                    "attribute_values": {
                                        "terms": {"field": "attributes.value", "size": 50}
                                    }
                                }
                            }
                        }
                    }
                }
            
            # Ejecutar búsqueda
            response = self.es.search(index=self.index_name, body=search_body)
            
            # Procesar resultados
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            
            # Extraer productos
            products = [hit['_source'] for hit in hits]
            
            # Extraer facetas si se solicitaron
            facets = {}
            if include_facets and 'aggregations' in response:
                aggs = response['aggregations']
                
                # Categorías
                if 'categories' in aggs:
                    facets['categories'] = [
                        {"name": bucket['key'], "count": bucket['doc_count']}
                        for bucket in aggs['categories']['buckets']
                    ]
                
                # Marcas
                if 'brands' in aggs:
                    facets['brands'] = [
                        {"name": bucket['key'], "count": bucket['doc_count']}
                        for bucket in aggs['brands']['buckets']
                    ]
                
                # Rangos de precio
                if 'price_ranges' in aggs:
                    facets['price_ranges'] = [
                        {
                            "from": bucket.get('from'),
                            "to": bucket.get('to'),
                            "count": bucket['doc_count']
                        }
                        for bucket in aggs['price_ranges']['buckets']
                    ]
                
                # Ratings
                if 'ratings' in aggs:
                    facets['ratings'] = [
                        {
                            "from": bucket.get('from'),
                            "to": bucket.get('to'),
                            "count": bucket['doc_count']
                        }
                        for bucket in aggs['ratings']['buckets']
                    ]
                
                # Atributos
                if 'attributes' in aggs and 'attribute_names' in aggs['attributes']:
                    facets['attributes'] = {}
                    for name_bucket in aggs['attributes']['attribute_names']['buckets']:
                        attr_name = name_bucket['key']
                        facets['attributes'][attr_name] = [
                            {"value": value_bucket['key'], "count": value_bucket['doc_count']}
                            for value_bucket in name_bucket['attribute_values']['buckets']
                        ]
            
            # Calcular información de paginación
            total_pages = (total + page_size - 1) // page_size
            
            # Construir respuesta
            result = {
                "products": products,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": total,
                    "total_pages": total_pages
                }
            }
            
            if include_facets:
                result["facets"] = facets
            
            return result
        
        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            return {
                "products": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": 0,
                    "total_pages": 0
                },
                "facets": {},
                "error": str(e)
            }
    
    def autocomplete(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Proporciona sugerencias de autocompletado para la búsqueda.
        
        Args:
            query: Texto parcial para autocompletar
            limit: Número máximo de sugerencias
            
        Returns:
            List: Lista de sugerencias
        """
        try:
            search_body = {
                "size": limit,
                "_source": ["id", "name", "sku", "price", "images"],
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name.autocomplete^3", "name^2", "sku"],
                        "type": "phrase_prefix"
                    }
                }
            }
            
            response = self.es.search(index=self.index_name, body=search_body)
            
            suggestions = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                suggestion = {
                    "id": source['id'],
                    "name": source['name'],
                    "sku": source.get('sku', ''),
                    "price": source.get('price', 0),
                }
                
                # Agregar imagen si existe
                if 'images' in source and len(source['images']) > 0:
                    suggestion['image_url'] = source['images'][0].get('image_url', '')
                
                suggestions.append(suggestion)
            
            return suggestions
        
        except Exception as e:
            logger.error(f"Error en autocompletado: {str(e)}")
            return []
    
    def reindex_all_products(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Reindexar todos los productos (elimina el índice y lo crea de nuevo).
        
        Args:
            products: Lista de productos a indexar
            
        Returns:
            Dict: Estadísticas de la operación
        """
        try:
            # Eliminar índice si existe
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
                logger.info(f"Índice '{self.index_name}' eliminado")
            
            # Crear índice de nuevo
            self._create_index_if_not_exists()
            
            # Indexar productos
            result = self.bulk_index_products(products)
            
            return {
                "success": True,
                "message": f"Reindexación completada. {result['success']} productos indexados, {result['failed']} fallidos.",
                "stats": result
            }
        
        except Exception as e:
            logger.error(f"Error en reindexación: {str(e)}")
            return {
                "success": False,
                "message": f"Error en reindexación: {str(e)}",
                "stats": {"total": len(products), "success": 0, "failed": len(products)}
            }
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un producto por su ID.
        
        Args:
            product_id: ID del producto
            
        Returns:
            Dict: Datos del producto o None si no existe
        """
        try:
            response = self.es.get(index=self.index_name, id=product_id)
            return response['_source']
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error al obtener producto {product_id}: {str(e)}")
            return None
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de Elasticsearch.
        
        Returns:
            Dict: Estado de Elasticsearch
        """
        try:
            health = self.es.cluster.health()
            indices = self.es.cat.indices(index=self.index_name, format="json")
            
            return {
                "status": "ok",
                "elasticsearch": {
                    "status": health['status'],
                    "cluster_name": health['cluster_name'],
                    "nodes": health['number_of_nodes'],
                    "indices": indices
                }
            }
        except Exception as e:
            logger.error(f"Error en health check: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }


# Instancia singleton del servicio
search_service = SearchService()

