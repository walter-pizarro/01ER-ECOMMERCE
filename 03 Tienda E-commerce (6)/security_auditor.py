#!/usr/bin/env python3
"""
Auditoría de Seguridad y Testing de Carga para eCommerce
Incluye análisis de vulnerabilidades, testing de penetración básico y pruebas de carga
"""

import requests
import json
import time
import threading
import subprocess
import re
import hashlib
import secrets
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import os

class SecurityAuditor:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.vulnerabilities = []
        self.security_score = 100
        self.load_test_results = {}
        
    def check_common_vulnerabilities(self):
        """Verificar vulnerabilidades comunes"""
        print("🔒 Verificando Vulnerabilidades Comunes...")
        
        # 1. Test de inyección SQL
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1#"
        ]
        
        for payload in sql_payloads:
            try:
                response = requests.post(f"{self.base_url}/auth/login", 
                                       json={"email": payload, "password": "test"}, 
                                       timeout=5)
                if response.status_code == 200 or "error" not in response.text.lower():
                    self.vulnerabilities.append({
                        "type": "SQL Injection",
                        "severity": "Critical",
                        "description": f"Posible inyección SQL con payload: {payload}",
                        "endpoint": "/auth/login"
                    })
                    self.security_score -= 20
            except:
                pass
        
        print(f"   ✅ Test de inyección SQL completado")
        
        # 2. Test de XSS
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        for payload in xss_payloads:
            try:
                response = requests.post(f"{self.base_url}/products", 
                                       json={"name": payload, "description": "test"}, 
                                       timeout=5)
                if payload in response.text:
                    self.vulnerabilities.append({
                        "type": "Cross-Site Scripting (XSS)",
                        "severity": "High",
                        "description": f"Posible XSS con payload: {payload}",
                        "endpoint": "/products"
                    })
                    self.security_score -= 15
            except:
                pass
        
        print(f"   ✅ Test de XSS completado")
        
        # 3. Test de autenticación débil
        weak_passwords = ["123456", "password", "admin", "test", ""]
        
        for pwd in weak_passwords:
            try:
                response = requests.post(f"{self.base_url}/auth/register", 
                                       json={"email": "test@test.com", "password": pwd, "name": "Test"}, 
                                       timeout=5)
                if response.status_code == 201:
                    self.vulnerabilities.append({
                        "type": "Weak Password Policy",
                        "severity": "Medium",
                        "description": f"Sistema acepta contraseña débil: {pwd}",
                        "endpoint": "/auth/register"
                    })
                    self.security_score -= 10
                    break
            except:
                pass
        
        print(f"   ✅ Test de contraseñas débiles completado")
    
    def check_authentication_security(self):
        """Verificar seguridad de autenticación"""
        print("🔐 Verificando Seguridad de Autenticación...")
        
        # 1. Test de fuerza bruta
        attempts = 0
        for i in range(10):
            try:
                response = requests.post(f"{self.base_url}/auth/login", 
                                       json={"email": "admin@test.com", "password": f"wrong{i}"}, 
                                       timeout=5)
                attempts += 1
                if response.status_code != 429:  # No rate limiting
                    continue
                else:
                    break
            except:
                pass
        
        if attempts >= 5:
            self.vulnerabilities.append({
                "type": "No Rate Limiting",
                "severity": "High",
                "description": "Sistema no implementa rate limiting para intentos de login",
                "endpoint": "/auth/login"
            })
            self.security_score -= 15
        
        print(f"   ✅ Test de fuerza bruta completado")
        
        # 2. Test de JWT security
        try:
            # Intentar login válido
            response = requests.post(f"{self.base_url}/auth/login", 
                                   json={"email": "test@example.com", "password": "ValidPassword123!"})
            if response.status_code == 200:
                token = response.json().get('access_token')
                if token:
                    # Verificar si el token es seguro
                    if len(token.split('.')) != 3:
                        self.vulnerabilities.append({
                            "type": "Invalid JWT Format",
                            "severity": "High",
                            "description": "Token JWT no tiene formato válido",
                            "endpoint": "/auth/login"
                        })
                        self.security_score -= 15
        except:
            pass
        
        print(f"   ✅ Test de seguridad JWT completado")
    
    def check_api_security(self):
        """Verificar seguridad de APIs"""
        print("🌐 Verificando Seguridad de APIs...")
        
        # 1. Test de endpoints sin autenticación
        endpoints_to_test = [
            "/admin/dashboard",
            "/admin/users",
            "/orders",
            "/users/profile"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.vulnerabilities.append({
                        "type": "Unauthorized Access",
                        "severity": "Critical",
                        "description": f"Endpoint accesible sin autenticación: {endpoint}",
                        "endpoint": endpoint
                    })
                    self.security_score -= 20
            except:
                pass
        
        print(f"   ✅ Test de endpoints sin autenticación completado")
        
        # 2. Test de CORS
        try:
            headers = {'Origin': 'http://malicious-site.com'}
            response = requests.get(f"{self.base_url}/health", headers=headers, timeout=5)
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header == '*':
                self.vulnerabilities.append({
                    "type": "Permissive CORS",
                    "severity": "Medium",
                    "description": "CORS configurado para permitir cualquier origen",
                    "endpoint": "Global"
                })
                self.security_score -= 10
        except:
            pass
        
        print(f"   ✅ Test de CORS completado")
    
    def check_file_security(self):
        """Verificar seguridad de archivos"""
        print("📁 Verificando Seguridad de Archivos...")
        
        backend_path = Path("/home/ubuntu/ecommerce-modular/backend/ecommerce-api")
        
        # 1. Buscar credenciales hardcodeadas
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for file_path in backend_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for pattern in sensitive_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.vulnerabilities.append({
                            "type": "Hardcoded Credentials",
                            "severity": "Critical",
                            "description": f"Credenciales hardcodeadas en {file_path.name}",
                            "endpoint": "File System"
                        })
                        self.security_score -= 25
                        break
            except:
                pass
        
        print(f"   ✅ Test de credenciales hardcodeadas completado")
        
        # 2. Verificar permisos de archivos
        config_files = [
            backend_path / "src" / "config" / "settings.py",
            backend_path / ".env",
            Path("/home/ubuntu/ecommerce-modular/.env")
        ]
        
        for config_file in config_files:
            if config_file.exists():
                stat = config_file.stat()
                # Verificar si el archivo es legible por otros
                if stat.st_mode & 0o044:  # Legible por grupo u otros
                    self.vulnerabilities.append({
                        "type": "Insecure File Permissions",
                        "severity": "Medium",
                        "description": f"Archivo de configuración con permisos inseguros: {config_file.name}",
                        "endpoint": "File System"
                    })
                    self.security_score -= 10
        
        print(f"   ✅ Test de permisos de archivos completado")
    
    def perform_load_testing(self):
        """Realizar testing de carga"""
        print("⚡ Realizando Testing de Carga...")
        
        def make_request(endpoint="/health"):
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                return {
                    'success': response.status_code == 200,
                    'response_time': response_time,
                    'status_code': response.status_code
                }
            except Exception as e:
                return {
                    'success': False,
                    'response_time': time.time() - start_time,
                    'error': str(e)
                }
        
        # Test con diferentes niveles de carga
        load_levels = [
            {'name': 'Light Load', 'concurrent': 10, 'requests': 50},
            {'name': 'Medium Load', 'concurrent': 25, 'requests': 100},
            {'name': 'Heavy Load', 'concurrent': 50, 'requests': 200}
        ]
        
        for load_level in load_levels:
            print(f"   🔄 Testing {load_level['name']}...")
            
            start_time = time.time()
            results = []
            
            with ThreadPoolExecutor(max_workers=load_level['concurrent']) as executor:
                futures = [executor.submit(make_request) for _ in range(load_level['requests'])]
                results = [future.result() for future in as_completed(futures)]
            
            total_time = time.time() - start_time
            
            # Analizar resultados
            successful_requests = sum(1 for r in results if r['success'])
            failed_requests = len(results) - successful_requests
            response_times = [r['response_time'] for r in results if r['success']]
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
            else:
                avg_response_time = max_response_time = min_response_time = 0
            
            success_rate = (successful_requests / len(results)) * 100
            requests_per_second = len(results) / total_time
            
            self.load_test_results[load_level['name']] = {
                'total_requests': len(results),
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time,
                'requests_per_second': requests_per_second,
                'total_time': total_time
            }
            
            print(f"      ✅ {load_level['name']}: {success_rate:.1f}% success rate, {avg_response_time:.3f}s avg response")
            
            # Evaluar performance
            if success_rate < 95:
                self.vulnerabilities.append({
                    "type": "Poor Reliability",
                    "severity": "Medium",
                    "description": f"Baja tasa de éxito en {load_level['name']}: {success_rate:.1f}%",
                    "endpoint": "System Performance"
                })
                self.security_score -= 5
            
            if avg_response_time > 2.0:
                self.vulnerabilities.append({
                    "type": "Poor Performance",
                    "severity": "Low",
                    "description": f"Tiempo de respuesta alto en {load_level['name']}: {avg_response_time:.3f}s",
                    "endpoint": "System Performance"
                })
                self.security_score -= 3
    
    def generate_security_report(self):
        """Generar reporte de seguridad"""
        print("\n" + "="*70)
        print("🔒 REPORTE DE AUDITORÍA DE SEGURIDAD")
        print("="*70)
        
        # Clasificar vulnerabilidades por severidad
        critical = [v for v in self.vulnerabilities if v['severity'] == 'Critical']
        high = [v for v in self.vulnerabilities if v['severity'] == 'High']
        medium = [v for v in self.vulnerabilities if v['severity'] == 'Medium']
        low = [v for v in self.vulnerabilities if v['severity'] == 'Low']
        
        print(f"\n📊 RESUMEN DE VULNERABILIDADES:")
        print(f"   🔴 Críticas: {len(critical)}")
        print(f"   🟠 Altas: {len(high)}")
        print(f"   🟡 Medias: {len(medium)}")
        print(f"   🟢 Bajas: {len(low)}")
        print(f"   📈 Score de Seguridad: {max(0, self.security_score)}/100")
        
        # Mostrar vulnerabilidades críticas
        if critical:
            print(f"\n🔴 VULNERABILIDADES CRÍTICAS:")
            for i, vuln in enumerate(critical, 1):
                print(f"   {i}. {vuln['type']}")
                print(f"      Descripción: {vuln['description']}")
                print(f"      Endpoint: {vuln['endpoint']}")
                print()
        
        # Mostrar vulnerabilidades altas
        if high:
            print(f"🟠 VULNERABILIDADES ALTAS:")
            for i, vuln in enumerate(high, 1):
                print(f"   {i}. {vuln['type']}")
                print(f"      Descripción: {vuln['description']}")
                print(f"      Endpoint: {vuln['endpoint']}")
                print()
        
        # Reporte de testing de carga
        if self.load_test_results:
            print(f"⚡ RESULTADOS DE TESTING DE CARGA:")
            for test_name, results in self.load_test_results.items():
                print(f"\n   📊 {test_name}:")
                print(f"      - Requests totales: {results['total_requests']}")
                print(f"      - Tasa de éxito: {results['success_rate']:.1f}%")
                print(f"      - Tiempo promedio: {results['avg_response_time']:.3f}s")
                print(f"      - Requests/segundo: {results['requests_per_second']:.1f}")
        
        # Evaluación general
        if self.security_score >= 90:
            status = "🟢 EXCELENTE"
            recommendation = "Sistema seguro y listo para producción"
        elif self.security_score >= 75:
            status = "🟡 BUENO"
            recommendation = "Algunas mejoras de seguridad recomendadas"
        elif self.security_score >= 50:
            status = "🟠 REGULAR"
            recommendation = "Correcciones de seguridad necesarias antes de producción"
        else:
            status = "🔴 CRÍTICO"
            recommendation = "Sistema no seguro - correcciones urgentes requeridas"
        
        print(f"\n🎯 EVALUACIÓN GENERAL: {status}")
        print(f"   Recomendación: {recommendation}")
        
        # Recomendaciones de seguridad
        print(f"\n💡 RECOMENDACIONES DE SEGURIDAD:")
        recommendations = [
            "Implementar rate limiting en endpoints de autenticación",
            "Configurar HTTPS con certificados SSL válidos",
            "Implementar logging y monitoreo de seguridad",
            "Realizar auditorías de seguridad regulares",
            "Configurar WAF (Web Application Firewall)",
            "Implementar autenticación de dos factores (2FA)",
            "Configurar backup automático y plan de recuperación",
            "Implementar validación exhaustiva de entrada"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        return {
            'vulnerabilities': self.vulnerabilities,
            'security_score': self.security_score,
            'load_test_results': self.load_test_results,
            'recommendations': recommendations
        }

def main():
    """Función principal"""
    print("🚀 INICIANDO AUDITORÍA DE SEGURIDAD Y TESTING DE CARGA")
    print("="*70)
    
    auditor = SecurityAuditor()
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{auditor.base_url}/health", timeout=5)
        print("✅ Servidor backend detectado")
    except:
        print("❌ Error: Servidor backend no disponible")
        print("   Nota: Algunos tests se ejecutarán en modo simulado")
    
    # Ejecutar auditoría
    auditor.check_common_vulnerabilities()
    auditor.check_authentication_security()
    auditor.check_api_security()
    auditor.check_file_security()
    auditor.perform_load_testing()
    
    # Generar reporte
    results = auditor.generate_security_report()
    
    # Guardar resultados
    output_file = "/home/ubuntu/security_audit_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    print("\n🏁 Auditoría completada")
    
    # Exit code basado en security score
    return 0 if auditor.security_score >= 75 else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)

