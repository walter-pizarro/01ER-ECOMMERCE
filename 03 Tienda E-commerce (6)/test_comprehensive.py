#!/usr/bin/env python3
"""
Suite de Testing Automatizado para eCommerce Backend
Incluye tests unitarios, de integración y de performance
"""

import pytest
import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics
import sys
import os

# Configuración de testing
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "email": "test@example.com",
    "password": "TestPassword123!",
    "name": "Test User"
}

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.performance_metrics = {}
        
    def add_pass(self):
        self.passed += 1
        
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        
    def add_metric(self, name, value):
        self.performance_metrics[name] = value

results = TestResults()

def test_api_call(method, endpoint, data=None, headers=None, expected_status=200):
    """Helper function para realizar llamadas a la API"""
    try:
        start_time = time.time()
        
        if method.upper() == 'GET':
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers)
        
        response_time = time.time() - start_time
        
        if response.status_code == expected_status:
            results.add_pass()
            return response, response_time
        else:
            results.add_fail(f"{method} {endpoint}", f"Expected {expected_status}, got {response.status_code}")
            return None, response_time
            
    except Exception as e:
        results.add_fail(f"{method} {endpoint}", str(e))
        return None, 0

def test_health_check():
    """Test básico de health check"""
    print("🔍 Testing Health Check...")
    response, response_time = test_api_call('GET', '/health')
    
    if response:
        print(f"✅ Health check passed ({response_time:.3f}s)")
        results.add_metric('health_check_time', response_time)
    else:
        print("❌ Health check failed")

def test_authentication_flow():
    """Test completo del flujo de autenticación"""
    print("🔐 Testing Authentication Flow...")
    
    # Test registro
    register_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "name": TEST_USER["name"]
    }
    
    response, response_time = test_api_call('POST', '/auth/register', register_data, expected_status=201)
    if response:
        print(f"✅ Registration passed ({response_time:.3f}s)")
        results.add_metric('registration_time', response_time)
    else:
        print("❌ Registration failed")
        return None
    
    # Test login
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    response, response_time = test_api_call('POST', '/auth/login', login_data)
    if response:
        token = response.json().get('access_token')
        print(f"✅ Login passed ({response_time:.3f}s)")
        results.add_metric('login_time', response_time)
        return token
    else:
        print("❌ Login failed")
        return None

def test_products_api(token):
    """Test de APIs de productos"""
    print("🛍️ Testing Products API...")
    
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    # Test listar productos
    response, response_time = test_api_call('GET', '/products', headers=headers)
    if response:
        products = response.json()
        print(f"✅ Products list passed ({response_time:.3f}s) - {len(products.get('data', []))} products")
        results.add_metric('products_list_time', response_time)
    else:
        print("❌ Products list failed")
        return
    
    # Test crear producto (si hay token de admin)
    if token:
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 99.99,
            "category_id": 1,
            "stock": 100
        }
        
        response, response_time = test_api_call('POST', '/products', product_data, headers)
        if response:
            product_id = response.json().get('id')
            print(f"✅ Product creation passed ({response_time:.3f}s)")
            results.add_metric('product_creation_time', response_time)
            
            # Test obtener producto específico
            response, response_time = test_api_call('GET', f'/products/{product_id}', headers=headers)
            if response:
                print(f"✅ Product detail passed ({response_time:.3f}s)")
                results.add_metric('product_detail_time', response_time)
            else:
                print("❌ Product detail failed")
        else:
            print("❌ Product creation failed")

def test_search_functionality(token):
    """Test de funcionalidad de búsqueda"""
    print("🔍 Testing Search Functionality...")
    
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    # Test búsqueda básica
    search_params = {'q': 'test', 'limit': 10}
    response, response_time = test_api_call('GET', '/search/products', headers=headers)
    
    if response:
        results_data = response.json()
        print(f"✅ Search passed ({response_time:.3f}s) - {len(results_data.get('results', []))} results")
        results.add_metric('search_time', response_time)
    else:
        print("❌ Search failed")

def test_orders_flow(token):
    """Test del flujo completo de pedidos"""
    print("🛒 Testing Orders Flow...")
    
    if not token:
        print("❌ Orders test skipped - no authentication token")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test crear pedido
    order_data = {
        "items": [
            {"product_id": 1, "quantity": 2, "price": 99.99}
        ],
        "shipping_address": {
            "street": "Test Street 123",
            "city": "Test City",
            "postal_code": "12345"
        }
    }
    
    response, response_time = test_api_call('POST', '/orders', order_data, headers)
    if response:
        order_id = response.json().get('id')
        print(f"✅ Order creation passed ({response_time:.3f}s)")
        results.add_metric('order_creation_time', response_time)
        
        # Test obtener pedido
        response, response_time = test_api_call('GET', f'/orders/{order_id}', headers=headers)
        if response:
            print(f"✅ Order retrieval passed ({response_time:.3f}s)")
            results.add_metric('order_retrieval_time', response_time)
        else:
            print("❌ Order retrieval failed")
    else:
        print("❌ Order creation failed")

def test_concurrent_requests():
    """Test de carga con requests concurrentes"""
    print("⚡ Testing Concurrent Load...")
    
    def make_request():
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/health")
            response_time = time.time() - start_time
            return response_time, response.status_code == 200
        except:
            return 0, False
    
    # Test con 50 requests concurrentes
    num_requests = 50
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        results_list = [future.result() for future in futures]
    
    response_times = [r[0] for r in results_list]
    success_count = sum(1 for r in results_list if r[1])
    
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    print(f"✅ Concurrent load test completed:")
    print(f"   - Requests: {num_requests}")
    print(f"   - Success rate: {success_count/num_requests*100:.1f}%")
    print(f"   - Avg response time: {avg_time:.3f}s")
    print(f"   - Min response time: {min_time:.3f}s")
    print(f"   - Max response time: {max_time:.3f}s")
    
    results.add_metric('concurrent_avg_time', avg_time)
    results.add_metric('concurrent_success_rate', success_count/num_requests)

def test_database_performance():
    """Test de performance de base de datos"""
    print("🗄️ Testing Database Performance...")
    
    # Test múltiples consultas de productos
    times = []
    for i in range(10):
        response, response_time = test_api_call('GET', '/products?limit=100')
        if response:
            times.append(response_time)
    
    if times:
        avg_time = statistics.mean(times)
        print(f"✅ Database performance test completed:")
        print(f"   - Average query time: {avg_time:.3f}s")
        print(f"   - Queries tested: {len(times)}")
        
        results.add_metric('db_avg_query_time', avg_time)
    else:
        print("❌ Database performance test failed")

def test_error_handling():
    """Test de manejo de errores"""
    print("🚨 Testing Error Handling...")
    
    # Test endpoint inexistente
    response, _ = test_api_call('GET', '/nonexistent', expected_status=404)
    if response:
        print("✅ 404 error handling passed")
    
    # Test datos inválidos
    invalid_data = {"invalid": "data"}
    response, _ = test_api_call('POST', '/auth/login', invalid_data, expected_status=400)
    if response:
        print("✅ 400 error handling passed")
    
    # Test sin autenticación
    response, _ = test_api_call('GET', '/admin/dashboard', expected_status=401)
    if response:
        print("✅ 401 error handling passed")

def generate_report():
    """Generar reporte de testing"""
    print("\n" + "="*60)
    print("📊 REPORTE DE TESTING AUTOMATIZADO")
    print("="*60)
    
    total_tests = results.passed + results.failed
    success_rate = (results.passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 RESUMEN GENERAL:")
    print(f"   - Tests ejecutados: {total_tests}")
    print(f"   - Tests exitosos: {results.passed}")
    print(f"   - Tests fallidos: {results.failed}")
    print(f"   - Tasa de éxito: {success_rate:.1f}%")
    
    if results.performance_metrics:
        print(f"\n⚡ MÉTRICAS DE PERFORMANCE:")
        for metric, value in results.performance_metrics.items():
            if 'time' in metric:
                print(f"   - {metric}: {value:.3f}s")
            else:
                print(f"   - {metric}: {value}")
    
    if results.errors:
        print(f"\n❌ ERRORES ENCONTRADOS:")
        for error in results.errors:
            print(f"   - {error}")
    
    # Evaluación general
    print(f"\n🎯 EVALUACIÓN GENERAL:")
    if success_rate >= 90:
        print("   ✅ EXCELENTE - Sistema listo para producción")
    elif success_rate >= 75:
        print("   ⚠️ BUENO - Algunas mejoras recomendadas")
    elif success_rate >= 50:
        print("   🔶 REGULAR - Correcciones necesarias")
    else:
        print("   ❌ CRÍTICO - Sistema no listo para producción")
    
    return success_rate

def main():
    """Función principal de testing"""
    print("🚀 INICIANDO SUITE DE TESTING AUTOMATIZADO")
    print("="*60)
    
    # Verificar que el servidor esté corriendo
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ Servidor backend detectado")
    except:
        print("❌ Error: Servidor backend no disponible")
        print("   Asegúrate de que el backend esté corriendo en http://localhost:5000")
        return
    
    # Ejecutar tests
    test_health_check()
    token = test_authentication_flow()
    test_products_api(token)
    test_search_functionality(token)
    test_orders_flow(token)
    test_error_handling()
    test_concurrent_requests()
    test_database_performance()
    
    # Generar reporte
    success_rate = generate_report()
    
    # Cleanup - eliminar usuario de test
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        test_api_call('DELETE', '/auth/user', headers=headers, expected_status=200)
    
    print("\n🏁 Testing completado")
    
    # Exit code basado en success rate
    sys.exit(0 if success_rate >= 75 else 1)

if __name__ == "__main__":
    main()

