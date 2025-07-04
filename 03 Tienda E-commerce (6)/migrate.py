#!/usr/bin/env python3
"""
Sistema de migraciones para eCommerce Modular
Crea todas las tablas con índices y foreign keys optimizados
"""
import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.database import get_database_url, Base
from models import get_all_models

class DatabaseMigrator:
    """Gestor de migraciones de base de datos"""
    
    def __init__(self):
        self.database_url = get_database_url()
        self.engine = create_engine(self.database_url, echo=True)
        
    def create_database_if_not_exists(self):
        """Crea la base de datos si no existe"""
        try:
            # Extraer información de la URL
            from urllib.parse import urlparse
            parsed = urlparse(self.database_url)
            
            # Crear conexión sin especificar la base de datos
            admin_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}"
            admin_engine = create_engine(admin_url, echo=False)
            
            database_name = parsed.path.lstrip('/')
            
            with admin_engine.connect() as conn:
                # Verificar si la base de datos existe
                result = conn.execute(text(
                    "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db_name"
                ), {"db_name": database_name})
                
                if not result.fetchone():
                    print(f"Creando base de datos: {database_name}")
                    conn.execute(text(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    conn.commit()
                    print(f"✓ Base de datos '{database_name}' creada exitosamente")
                else:
                    print(f"✓ Base de datos '{database_name}' ya existe")
                    
            admin_engine.dispose()
            
        except Exception as e:
            print(f"Error creando base de datos: {e}")
            raise
    
    def run_migrations(self):
        """Ejecuta todas las migraciones"""
        try:
            print("🚀 Iniciando migraciones de base de datos...")
            print(f"📍 URL de conexión: {self.database_url.split('@')[1]}")  # Ocultar credenciales
            
            # Crear base de datos si no existe
            self.create_database_if_not_exists()
            
            # Crear todas las tablas
            print("\n📋 Creando tablas...")
            Base.metadata.create_all(bind=self.engine)
            
            # Verificar tablas creadas
            self._verify_tables()
            
            # Crear índices adicionales si es necesario
            self._create_additional_indexes()
            
            # Insertar datos básicos del sistema
            self._insert_system_data()
            
            print("\n✅ Migraciones completadas exitosamente!")
            
        except SQLAlchemyError as e:
            print(f"\n❌ Error en migraciones: {e}")
            raise
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            raise
        finally:
            self.engine.dispose()
    
    def _verify_tables(self):
        """Verifica que todas las tablas fueron creadas"""
        print("\n🔍 Verificando tablas creadas...")
        
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'"
            ))
            
            created_tables = [row[0] for row in result.fetchall()]
            expected_tables = [model.__tablename__ for model in get_all_models()]
            
            print(f"📊 Tablas esperadas: {len(expected_tables)}")
            print(f"📊 Tablas creadas: {len(created_tables)}")
            
            missing_tables = set(expected_tables) - set(created_tables)
            if missing_tables:
                print(f"⚠️  Tablas faltantes: {missing_tables}")
            else:
                print("✓ Todas las tablas fueron creadas correctamente")
                
            # Mostrar algunas tablas creadas
            print(f"📋 Algunas tablas creadas: {created_tables[:10]}")
            if len(created_tables) > 10:
                print(f"    ... y {len(created_tables) - 10} más")
    
    def _create_additional_indexes(self):
        """Crea índices adicionales para optimización"""
        print("\n🔧 Creando índices adicionales...")
        
        additional_indexes = [
            # Índices compuestos para consultas frecuentes
            "CREATE INDEX IF NOT EXISTS idx_products_category_active ON products(category_id, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_products_brand_active ON products(brand_id, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_products_price_active ON products(price, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_orders_user_status ON orders(user_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_orders_created_status ON orders(created_at, status)",
            "CREATE INDEX IF NOT EXISTS idx_reviews_product_approved ON reviews(product_id, is_approved)",
            
            # Índices para búsquedas de texto
            "CREATE FULLTEXT INDEX IF NOT EXISTS idx_products_search ON products(name, description)",
            "CREATE FULLTEXT INDEX IF NOT EXISTS idx_categories_search ON categories(name, description)",
            
            # Índices para analytics
            "CREATE INDEX IF NOT EXISTS idx_product_views_date ON product_views(created_at, product_id)",
            "CREATE INDEX IF NOT EXISTS idx_search_queries_date ON search_queries(created_at, query)",
        ]
        
        try:
            with self.engine.connect() as conn:
                for index_sql in additional_indexes:
                    try:
                        conn.execute(text(index_sql))
                        print(f"✓ Índice creado: {index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'índice'}")
                    except Exception as e:
                        print(f"⚠️  Error creando índice: {e}")
                
                conn.commit()
                
        except Exception as e:
            print(f"⚠️  Error en índices adicionales: {e}")
    
    def _insert_system_data(self):
        """Inserta datos básicos del sistema"""
        print("\n📝 Insertando datos básicos del sistema...")
        
        system_data_queries = [
            # Países básicos
            """
            INSERT IGNORE INTO countries (code, name, phone_code, currency_code, is_active) VALUES
            ('US', 'United States', '+1', 'USD', 1),
            ('CL', 'Chile', '+56', 'CLP', 1),
            ('AR', 'Argentina', '+54', 'ARS', 1),
            ('MX', 'Mexico', '+52', 'MXN', 1),
            ('ES', 'Spain', '+34', 'EUR', 1)
            """,
            
            # Estados para Chile
            """
            INSERT IGNORE INTO states (country_id, code, name, is_active) 
            SELECT c.id, 'RM', 'Región Metropolitana', 1 FROM countries c WHERE c.code = 'CL'
            UNION ALL
            SELECT c.id, 'VAL', 'Valparaíso', 1 FROM countries c WHERE c.code = 'CL'
            UNION ALL
            SELECT c.id, 'BIO', 'Biobío', 1 FROM countries c WHERE c.code = 'CL'
            """,
            
            # Roles básicos del sistema
            """
            INSERT IGNORE INTO roles (name, description, is_active) VALUES
            ('admin', 'Administrador del sistema', 1),
            ('manager', 'Gerente de tienda', 1),
            ('customer', 'Cliente', 1),
            ('guest', 'Invitado', 1)
            """,
            
            # Permisos básicos
            """
            INSERT IGNORE INTO permissions (name, description, resource, action) VALUES
            ('products.create', 'Crear productos', 'products', 'create'),
            ('products.read', 'Ver productos', 'products', 'read'),
            ('products.update', 'Actualizar productos', 'products', 'update'),
            ('products.delete', 'Eliminar productos', 'products', 'delete'),
            ('orders.create', 'Crear pedidos', 'orders', 'create'),
            ('orders.read', 'Ver pedidos', 'orders', 'read'),
            ('orders.update', 'Actualizar pedidos', 'orders', 'update'),
            ('users.read', 'Ver usuarios', 'users', 'read'),
            ('users.update', 'Actualizar usuarios', 'users', 'update'),
            ('admin.access', 'Acceso al panel administrativo', 'admin', 'access')
            """,
            
            # Grupos de atributos básicos
            """
            INSERT IGNORE INTO attribute_groups (name, display_name, sort_order, is_active) VALUES
            ('color', 'Color', 1, 1),
            ('size', 'Talla', 2, 1),
            ('material', 'Material', 3, 1),
            ('brand', 'Marca', 4, 1)
            """,
            
            # Métodos de envío básicos
            """
            INSERT IGNORE INTO shipping_methods (name, description, carrier, estimated_days_min, estimated_days_max, base_cost, is_active) VALUES
            ('standard', 'Envío estándar', 'Correos de Chile', 3, 7, 5.00, 1),
            ('express', 'Envío express', 'Chilexpress', 1, 3, 15.00, 1),
            ('pickup', 'Retiro en tienda', 'Tienda', 0, 1, 0.00, 1)
            """,
            
            # Configuraciones básicas del sistema
            """
            INSERT IGNORE INTO settings (`key`, `value`, description, type, is_public, group_name) VALUES
            ('site_name', 'eCommerce Modular', 'Nombre del sitio', 'string', 1, 'general'),
            ('site_description', 'Tienda online moderna y escalable', 'Descripción del sitio', 'string', 1, 'general'),
            ('currency', 'USD', 'Moneda por defecto', 'string', 1, 'general'),
            ('tax_rate', '0.19', 'Tasa de impuesto por defecto', 'decimal', 0, 'tax'),
            ('enable_reviews', 'true', 'Habilitar reseñas de productos', 'boolean', 1, 'features'),
            ('enable_wishlist', 'true', 'Habilitar lista de deseos', 'boolean', 1, 'features'),
            ('enable_coupons', 'true', 'Habilitar cupones de descuento', 'boolean', 1, 'features'),
            ('min_order_amount', '10.00', 'Monto mínimo de pedido', 'decimal', 1, 'orders'),
            ('max_cart_items', '50', 'Máximo de items en carrito', 'integer', 1, 'orders')
            """,
            
            # Plantillas de notificación básicas
            """
            INSERT IGNORE INTO notification_templates (name, subject, body_text, type, event, is_active) VALUES
            ('order_confirmed', 'Pedido Confirmado', 'Tu pedido #{order_number} ha sido confirmado.', 'email', 'order_confirmed', 1),
            ('order_shipped', 'Pedido Enviado', 'Tu pedido #{order_number} ha sido enviado.', 'email', 'order_shipped', 1),
            ('order_delivered', 'Pedido Entregado', 'Tu pedido #{order_number} ha sido entregado.', 'email', 'order_delivered', 1)
            """
        ]
        
        try:
            with self.engine.connect() as conn:
                for query in system_data_queries:
                    try:
                        conn.execute(text(query))
                        print(f"✓ Datos insertados: {query.split('INTO')[1].split('(')[0].strip()}")
                    except Exception as e:
                        print(f"⚠️  Error insertando datos: {e}")
                
                conn.commit()
                print("✓ Datos básicos del sistema insertados")
                
        except Exception as e:
            print(f"⚠️  Error insertando datos del sistema: {e}")
    
    def rollback_migrations(self):
        """Elimina todas las tablas (usar con cuidado)"""
        print("⚠️  ADVERTENCIA: Eliminando todas las tablas...")
        
        try:
            Base.metadata.drop_all(bind=self.engine)
            print("✓ Todas las tablas eliminadas")
        except Exception as e:
            print(f"❌ Error eliminando tablas: {e}")
            raise
        finally:
            self.engine.dispose()

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de migraciones eCommerce')
    parser.add_argument('--rollback', action='store_true', help='Eliminar todas las tablas')
    parser.add_argument('--force', action='store_true', help='Forzar operación sin confirmación')
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator()
    
    if args.rollback:
        if not args.force:
            confirm = input("¿Estás seguro de que quieres eliminar todas las tablas? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Operación cancelada")
                return
        
        migrator.rollback_migrations()
    else:
        migrator.run_migrations()

if __name__ == "__main__":
    main()

