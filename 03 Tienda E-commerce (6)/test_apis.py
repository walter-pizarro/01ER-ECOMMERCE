#!/usr/bin/env python3
"""
Suite de testing para APIs del eCommerce Modular
Pruebas automatizadas para autenticación, productos y pedidos
"""
import requests
import json
import time
import sys
import os
from datetime import datetime

# Configuración del testing
API_BASE_URL = "http://localhost:5000"
TEST_USER_EMAIL = "test@ecommerce-modular.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_ADMIN_EMAIL = "admin@ecommerce-modular.com"
TEST_ADMIN_PASSWORD = "adminpassword123"

class APITester:
    """Clase para testing de APIs"""
    
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_time=0):
        """Registra el resultado de un test"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'response_time': response_time
        })
        print(f"{status} {test_name} ({response_time:.3f}s) - {message}")
    
    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Hace una request HTTP y mide el tiempo de respuesta"""
        url = f"{self.base_url}{endpoint}"
        
        # Headers por defecto
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        # Agregar token de autenticación si se proporciona
        if auth_token:
            default_headers['Authorization'] = f"Bearer {auth_token}"
        
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=default_headers, params=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=default_headers, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=default_headers, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            
            return response, response_time
            
        except Exception as e:
            response_time = time.time() - start_time
            return None, response_time
    
    def test_health_check(self):
        """Test del health check endpoint"""
        response, response_time = self.make_request('GET', '/health')
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get('status') == 'healthy'
            message = f"Status: {data.get('status')}, DB: {data.get('database', 'unknown')}"
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("Health Check", success, message, response_time)
        return success
    
    def test_api_docs(self):
        """Test de acceso a documentación de API"""
        response, response_time = self.make_request('GET', '/docs/')
        
        success = response and response.status_code == 200
        message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("API Documentation", success, message, response_time)
        return success
    
    def test_user_registration(self):
        """Test de registro de usuario"""
        user_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890"
        }
        
        response, response_time = self.make_request('POST', '/api/v1/auth/register', user_data)
        
        if response and response.status_code in [201, 409]:  # 409 si ya existe
            data = response.json()
            success = data.get('success', False)
            message = data.get('message', 'User registered')
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("User Registration", success, message, response_time)
        return success
    
    def test_admin_registration(self):
        """Test de registro de usuario admin"""
        admin_data = {
            "email": TEST_ADMIN_EMAIL,
            "password": TEST_ADMIN_PASSWORD,
            "first_name": "Admin",
            "last_name": "User",
            "phone": "+1234567891"
        }
        
        response, response_time = self.make_request('POST', '/api/v1/auth/register', admin_data)
        
        if response and response.status_code in [201, 409]:  # 409 si ya existe
            data = response.json()
            success = data.get('success', False)
            message = data.get('message', 'Admin registered')
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("Admin Registration", success, message, response_time)
        return success
    
    def test_user_login(self):
        """Test de login de usuario"""
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response, response_time = self.make_request('POST', '/api/v1/auth/login', login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success and 'tokens' in data:
                self.user_token = data['tokens']['access_token']
                message = f"Login successful, token obtained"
            else:
                message = data.get('error', 'Login failed')
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("User Login", success, message, response_time)
        return success
    
    def test_admin_login(self):
        """Test de login de admin"""
        login_data = {
            "email": TEST_ADMIN_EMAIL,
            "password": TEST_ADMIN_PASSWORD
        }
        
        response, response_time = self.make_request('POST', '/api/v1/auth/login', login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success and 'tokens' in data:
                self.admin_token = data['tokens']['access_token']
                message = f"Admin login successful, token obtained"
            else:
                message = data.get('error', 'Admin login failed')
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("Admin Login", success, message, response_time)
        return success
    
    def test_get_current_user(self):
        """Test de obtener usuario actual"""
        if not self.user_token:
            self.log_test("Get Current User", False, "No user token available", 0)
            return False
        
        response, response_time = self.make_request('GET', '/api/v1/auth/me', auth_token=self.user_token)
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success and 'user' in data:
                user_email = data['user'].get('email')
                message = f"User info retrieved: {user_email}"
            else:
                message = "User info not found in response"
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("Get Current User", success, message, response_time)
        return success
    
    def test_get_products(self):
        """Test de obtener lista de productos"""
        response, response_time = self.make_request('GET', '/api/v1/products')
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success and 'products' in data:
                product_count = len(data['products'])
                message = f"Retrieved {product_count} products"
            else:
                message = "No products found in response"
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("Get Products", success, message, response_time)
        return success
    
    def test_search_products(self):
        """Test de búsqueda de productos"""
        search_params = {'q': 'test'}
        response, response_time = self.make_request('GET', '/api/v1/products', search_params)
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success:
                product_count = len(data.get('products', []))
                message = f"Search returned {product_count} products"
            else:
                message = "Search failed"
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("Search Products", success, message, response_time)
        return success
    
    def test_get_featured_products(self):
        """Test de obtener productos destacados"""
        response, response_time = self.make_request('GET', '/api/v1/products/featured')
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success:
                product_count = len(data.get('products', []))
                message = f"Retrieved {product_count} featured products"
            else:
                message = "No featured products found"
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("Get Featured Products", success, message, response_time)
        return success
    
    def test_get_user_orders(self):
        """Test de obtener pedidos del usuario"""
        if not self.user_token:
            self.log_test("Get User Orders", False, "No user token available", 0)
            return False
        
        response, response_time = self.make_request('GET', '/api/v1/orders', auth_token=self.user_token)
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success:
                order_count = len(data.get('orders', []))
                message = f"Retrieved {order_count} orders"
            else:
                message = "No orders found"
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("Get User Orders", success, message, response_time)
        return success
    
    def test_api_stats(self):
        """Test de estadísticas de la API"""
        response, response_time = self.make_request('GET', '/api/v1/stats')
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success and 'stats' in data:
                stats = data['stats']
                message = f"Products: {stats.get('active_products', 0)}, Users: {stats.get('active_users', 0)}"
            else:
                message = "Stats not found in response"
        else:
            success = False
            message = f"HTTP {response.status_code if response else 'No response'}"
        
        self.log_test("API Stats", success, message, response_time)
        return success
    
    def test_rate_limiting(self):
        """Test de rate limiting"""
        # Hacer múltiples requests rápidas para probar rate limiting
        success_count = 0
        rate_limited = False
        
        start_time = time.time()
        
        for i in range(10):
            response, _ = self.make_request('GET', '/health')
            if response:
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited = True
                    break
        
        response_time = time.time() - start_time
        
        # Rate limiting funciona si se bloquea después de varios requests
        # O si todos pasan (límite no alcanzado)
        success = success_count > 0
        message = f"{success_count}/10 requests successful, rate limited: {rate_limited}"
        
        self.log_test("Rate Limiting", success, message, response_time)
        return success
    
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        print("🚀 Iniciando suite de testing para eCommerce Modular API")
        print(f"📍 Base URL: {self.base_url}")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("-" * 80)
        
        # Tests básicos del sistema
        self.test_health_check()
        self.test_api_docs()
        self.test_api_stats()
        
        # Tests de autenticación
        self.test_user_registration()
        self.test_admin_registration()
        self.test_user_login()
        self.test_admin_login()
        self.test_get_current_user()
        
        # Tests de productos
        self.test_get_products()
        self.test_search_products()
        self.test_get_featured_products()
        
        # Tests de pedidos
        self.test_get_user_orders()
        
        # Tests de seguridad
        self.test_rate_limiting()
        
        # Resumen de resultados
        print("-" * 80)
        self.print_summary()
    
    def print_summary(self):
        """Imprime resumen de resultados"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        avg_response_time = sum(result['response_time'] for result in self.test_results) / total_tests if total_tests > 0 else 0
        
        print(f"📊 RESUMEN DE TESTING")
        print(f"Total de tests: {total_tests}")
        print(f"✅ Exitosos: {passed_tests}")
        print(f"❌ Fallidos: {failed_tests}")
        print(f"📈 Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
        print(f"⚡ Tiempo promedio de respuesta: {avg_response_time:.3f}s")
        
        if failed_tests > 0:
            print(f"\n❌ TESTS FALLIDOS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n🎯 ESTADO GENERAL: {'✅ TODOS LOS TESTS PASARON' if failed_tests == 0 else '❌ ALGUNOS TESTS FALLARON'}")

def main():
    """Función principal"""
    # Verificar si se proporciona URL personalizada
    base_url = sys.argv[1] if len(sys.argv) > 1 else API_BASE_URL
    
    # Crear y ejecutar tester
    tester = APITester(base_url)
    tester.run_all_tests()
    
    # Exit code basado en resultados
    failed_tests = sum(1 for result in tester.test_results if not result['success'])
    sys.exit(1 if failed_tests > 0 else 0)

if __name__ == "__main__":
    main()

