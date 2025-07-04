#!/usr/bin/env python3
"""
Sistema de testing de integridad de base de datos
Verifica foreign keys, índices y consistencia de datos
"""
import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.database import get_database_url
from models import get_all_models, get_table_names

class DatabaseTester:
    """Tester de integridad de base de datos"""
    
    def __init__(self):
        self.database_url = get_database_url()
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.inspector = inspect(self.engine)
        
        self.tests_passed = 0
        self.tests_failed = 0
        self.warnings = 0
    
    def run_all_tests(self):
        """Ejecuta todos los tests de integridad"""
        try:
            print("🧪 Iniciando tests de integridad de base de datos...")
            print(f"📍 URL de conexión: {self.database_url.split('@')[1]}")
            print()
            
            # Tests de estructura
            self.test_tables_exist()
            self.test_foreign_keys()
            self.test_indexes()
            self.test_constraints()
            
            # Tests de datos
            self.test_data_integrity()
            self.test_orphaned_records()
            self.test_duplicate_data()
            
            # Tests de performance
            self.test_query_performance()
            
            # Resumen final
            self._print_summary()
            
        except Exception as e:
            print(f"❌ Error en tests: {e}")
            raise
        finally:
            self.session.close()
    
    def test_tables_exist(self):
        """Verifica que todas las tablas existan"""
        print("📋 Verificando existencia de tablas...")
        
        expected_tables = set(get_table_names())
        existing_tables = set(self.inspector.get_table_names())
        
        missing_tables = expected_tables - existing_tables
        extra_tables = existing_tables - expected_tables
        
        if missing_tables:
            print(f"❌ Tablas faltantes: {missing_tables}")
            self.tests_failed += 1
        else:
            print(f"✅ Todas las {len(expected_tables)} tablas existen")
            self.tests_passed += 1
        
        if extra_tables:
            print(f"⚠️  Tablas adicionales encontradas: {extra_tables}")
            self.warnings += 1
    
    def test_foreign_keys(self):
        """Verifica foreign keys"""
        print("\n🔗 Verificando foreign keys...")
        
        total_fks = 0
        valid_fks = 0
        
        for table_name in get_table_names():
            try:
                fks = self.inspector.get_foreign_keys(table_name)
                total_fks += len(fks)
                
                for fk in fks:
                    # Verificar que la tabla referenciada existe
                    if fk['referred_table'] in self.inspector.get_table_names():
                        valid_fks += 1
                    else:
                        print(f"❌ FK inválida en {table_name}: {fk['referred_table']} no existe")
                        self.tests_failed += 1
                        
            except Exception as e:
                print(f"⚠️  Error verificando FKs en {table_name}: {e}")
                self.warnings += 1
        
        if total_fks == valid_fks and total_fks > 0:
            print(f"✅ Todas las {total_fks} foreign keys son válidas")
            self.tests_passed += 1
        elif total_fks == 0:
            print("⚠️  No se encontraron foreign keys")
            self.warnings += 1
        else:
            print(f"❌ {total_fks - valid_fks} foreign keys inválidas de {total_fks} total")
            self.tests_failed += 1
    
    def test_indexes(self):
        """Verifica índices importantes"""
        print("\n📊 Verificando índices...")
        
        critical_indexes = [
            ('users', 'email'),
            ('products', 'sku'),
            ('orders', 'order_number'),
            ('categories', 'slug'),
            ('products', 'slug'),
        ]
        
        missing_indexes = []
        
        for table_name, column_name in critical_indexes:
            try:
                indexes = self.inspector.get_indexes(table_name)
                
                # Verificar si existe un índice en la columna
                has_index = any(
                    column_name in idx['column_names'] 
                    for idx in indexes
                )
                
                if not has_index:
                    missing_indexes.append(f"{table_name}.{column_name}")
                    
            except Exception as e:
                print(f"⚠️  Error verificando índices en {table_name}: {e}")
                self.warnings += 1
        
        if missing_indexes:
            print(f"❌ Índices faltantes: {missing_indexes}")
            self.tests_failed += 1
        else:
            print(f"✅ Todos los índices críticos están presentes")
            self.tests_passed += 1
    
    def test_constraints(self):
        """Verifica constraints importantes"""
        print("\n🔒 Verificando constraints...")
        
        # Test de unique constraints
        unique_tests = [
            ("SELECT email, COUNT(*) as cnt FROM users GROUP BY email HAVING cnt > 1", "emails duplicados en users"),
            ("SELECT sku, COUNT(*) as cnt FROM products GROUP BY sku HAVING cnt > 1", "SKUs duplicados en products"),
            ("SELECT order_number, COUNT(*) as cnt FROM orders GROUP BY order_number HAVING cnt > 1", "números de orden duplicados"),
        ]
        
        constraint_violations = 0
        
        for query, description in unique_tests:
            try:
                result = self.session.execute(text(query))
                violations = result.fetchall()
                
                if violations:
                    print(f"❌ Violación de constraint: {description}")
                    for violation in violations:
                        print(f"   {violation}")
                    constraint_violations += 1
                    
            except Exception as e:
                print(f"⚠️  Error verificando constraint ({description}): {e}")
                self.warnings += 1
        
        if constraint_violations == 0:
            print("✅ No se encontraron violaciones de constraints")
            self.tests_passed += 1
        else:
            print(f"❌ {constraint_violations} violaciones de constraints encontradas")
            self.tests_failed += 1
    
    def test_data_integrity(self):
        """Verifica integridad de datos"""
        print("\n🔍 Verificando integridad de datos...")
        
        integrity_tests = [
            # Precios no negativos
            ("SELECT COUNT(*) FROM products WHERE price < 0", "productos con precios negativos"),
            ("SELECT COUNT(*) FROM orders WHERE total_amount < 0", "órdenes con totales negativos"),
            
            # Cantidades válidas
            ("SELECT COUNT(*) FROM products WHERE inventory_quantity < 0", "productos con inventario negativo"),
            ("SELECT COUNT(*) FROM order_items WHERE quantity <= 0", "items de orden con cantidad inválida"),
            
            # Ratings válidos
            ("SELECT COUNT(*) FROM reviews WHERE rating < 1 OR rating > 5", "reseñas con rating inválido"),
            
            # Fechas lógicas
            ("SELECT COUNT(*) FROM orders WHERE created_at > NOW()", "órdenes con fecha futura"),
            ("SELECT COUNT(*) FROM users WHERE created_at > NOW()", "usuarios con fecha futura"),
        ]
        
        integrity_violations = 0
        
        for query, description in integrity_tests:
            try:
                result = self.session.execute(text(query))
                count = result.scalar()
                
                if count > 0:
                    print(f"❌ {count} registros con {description}")
                    integrity_violations += 1
                    
            except Exception as e:
                print(f"⚠️  Error verificando integridad ({description}): {e}")
                self.warnings += 1
        
        if integrity_violations == 0:
            print("✅ Integridad de datos verificada")
            self.tests_passed += 1
        else:
            print(f"❌ {integrity_violations} violaciones de integridad encontradas")
            self.tests_failed += 1
    
    def test_orphaned_records(self):
        """Verifica registros huérfanos"""
        print("\n👻 Verificando registros huérfanos...")
        
        orphan_tests = [
            # Productos sin categoría válida
            ("""
                SELECT COUNT(*) FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id 
                WHERE p.category_id IS NOT NULL AND c.id IS NULL
            """, "productos con categoría inválida"),
            
            # Items de orden sin producto válido
            ("""
                SELECT COUNT(*) FROM order_items oi 
                LEFT JOIN products p ON oi.product_id = p.id 
                WHERE p.id IS NULL
            """, "items de orden sin producto válido"),
            
            # Direcciones sin usuario válido
            ("""
                SELECT COUNT(*) FROM addresses a 
                LEFT JOIN users u ON a.user_id = u.id 
                WHERE u.id IS NULL
            """, "direcciones sin usuario válido"),
            
            # Reseñas sin producto válido
            ("""
                SELECT COUNT(*) FROM reviews r 
                LEFT JOIN products p ON r.product_id = p.id 
                WHERE p.id IS NULL
            """, "reseñas sin producto válido"),
        ]
        
        orphan_count = 0
        
        for query, description in orphan_tests:
            try:
                result = self.session.execute(text(query))
                count = result.scalar()
                
                if count > 0:
                    print(f"❌ {count} {description}")
                    orphan_count += 1
                    
            except Exception as e:
                print(f"⚠️  Error verificando huérfanos ({description}): {e}")
                self.warnings += 1
        
        if orphan_count == 0:
            print("✅ No se encontraron registros huérfanos")
            self.tests_passed += 1
        else:
            print(f"❌ {orphan_count} tipos de registros huérfanos encontrados")
            self.tests_failed += 1
    
    def test_duplicate_data(self):
        """Verifica datos duplicados"""
        print("\n🔄 Verificando datos duplicados...")
        
        duplicate_tests = [
            # Usuarios con mismo email
            ("""
                SELECT email, COUNT(*) as cnt FROM users 
                GROUP BY email HAVING cnt > 1
            """, "usuarios con email duplicado"),
            
            # Productos con mismo SKU
            ("""
                SELECT sku, COUNT(*) as cnt FROM products 
                GROUP BY sku HAVING cnt > 1
            """, "productos con SKU duplicado"),
            
            # Categorías con mismo slug
            ("""
                SELECT slug, COUNT(*) as cnt FROM categories 
                GROUP BY slug HAVING cnt > 1
            """, "categorías con slug duplicado"),
        ]
        
        duplicate_issues = 0
        
        for query, description in duplicate_tests:
            try:
                result = self.session.execute(text(query))
                duplicates = result.fetchall()
                
                if duplicates:
                    print(f"❌ {description}:")
                    for dup in duplicates[:5]:  # Mostrar solo los primeros 5
                        print(f"   {dup}")
                    if len(duplicates) > 5:
                        print(f"   ... y {len(duplicates) - 5} más")
                    duplicate_issues += 1
                    
            except Exception as e:
                print(f"⚠️  Error verificando duplicados ({description}): {e}")
                self.warnings += 1
        
        if duplicate_issues == 0:
            print("✅ No se encontraron datos duplicados")
            self.tests_passed += 1
        else:
            print(f"❌ {duplicate_issues} tipos de datos duplicados encontrados")
            self.tests_failed += 1
    
    def test_query_performance(self):
        """Verifica performance de consultas críticas"""
        print("\n⚡ Verificando performance de consultas...")
        
        performance_tests = [
            # Consultas que deberían ser rápidas con índices apropiados
            ("SELECT * FROM products WHERE sku = 'SKU-12345678' LIMIT 1", "búsqueda por SKU"),
            ("SELECT * FROM users WHERE email = 'admin@ecommerce.local' LIMIT 1", "búsqueda por email"),
            ("SELECT * FROM orders WHERE order_number = 'ORD-12345678' LIMIT 1", "búsqueda por número de orden"),
            ("SELECT COUNT(*) FROM products WHERE is_active = 1", "conteo de productos activos"),
            ("SELECT COUNT(*) FROM orders WHERE status = 'pending'", "conteo de órdenes pendientes"),
        ]
        
        slow_queries = 0
        
        for query, description in performance_tests:
            try:
                start_time = datetime.now()
                result = self.session.execute(text(query))
                result.fetchall()  # Consumir resultados
                end_time = datetime.now()
                
                duration = (end_time - start_time).total_seconds()
                
                if duration > 1.0:  # Más de 1 segundo es lento
                    print(f"🐌 Consulta lenta ({duration:.3f}s): {description}")
                    slow_queries += 1
                elif duration > 0.1:  # Más de 100ms es advertencia
                    print(f"⚠️  Consulta moderada ({duration:.3f}s): {description}")
                    self.warnings += 1
                else:
                    print(f"✅ Consulta rápida ({duration:.3f}s): {description}")
                    
            except Exception as e:
                print(f"⚠️  Error en consulta de performance ({description}): {e}")
                self.warnings += 1
        
        if slow_queries == 0:
            print("✅ Todas las consultas tienen performance aceptable")
            self.tests_passed += 1
        else:
            print(f"❌ {slow_queries} consultas lentas encontradas")
            self.tests_failed += 1
    
    def _print_summary(self):
        """Imprime resumen de tests"""
        print("\n" + "="*60)
        print("📊 RESUMEN DE TESTS DE INTEGRIDAD")
        print("="*60)
        
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests pasados: {self.tests_passed}")
        print(f"❌ Tests fallidos: {self.tests_failed}")
        print(f"⚠️  Advertencias: {self.warnings}")
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 ¡Todos los tests de integridad pasaron!")
            print("   La base de datos está en buen estado.")
        else:
            print(f"\n⚠️  Se encontraron {self.tests_failed} problemas de integridad.")
            print("   Revisa los errores anteriores y corrige los problemas.")
        
        if self.warnings > 0:
            print(f"\n💡 Hay {self.warnings} advertencias que podrían requerir atención.")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Tests de integridad de base de datos')
    parser.add_argument('--verbose', '-v', action='store_true', help='Output detallado')
    
    args = parser.parse_args()
    
    tester = DatabaseTester()
    
    try:
        tester.run_all_tests()
        
        # Código de salida basado en resultados
        if tester.tests_failed > 0:
            sys.exit(1)  # Fallar si hay tests fallidos
        else:
            sys.exit(0)  # Éxito
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests cancelados por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error ejecutando tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

