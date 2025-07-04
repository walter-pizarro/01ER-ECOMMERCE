#!/usr/bin/env python3
"""
Análisis de Performance y Optimización del Sistema eCommerce
Incluye análisis de bundle, queries, memoria y recomendaciones
"""

import os
import json
import time
import psutil
import subprocess
import sqlite3
from pathlib import Path
import re

class PerformanceAnalyzer:
    def __init__(self):
        self.results = {
            'frontend': {},
            'backend': {},
            'database': {},
            'system': {},
            'recommendations': []
        }
        
    def analyze_frontend_bundle(self):
        """Analizar el bundle del frontend"""
        print("📦 Analizando Bundle del Frontend...")
        
        frontend_path = Path("/home/ubuntu/ecommerce-modular/frontend/ecommerce-frontend")
        
        # Verificar si existe package.json
        package_json = frontend_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                package_data = json.load(f)
                
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            
            self.results['frontend']['dependencies_count'] = len(dependencies)
            self.results['frontend']['dev_dependencies_count'] = len(dev_dependencies)
            
            # Analizar dependencias pesadas
            heavy_deps = []
            for dep, version in dependencies.items():
                if any(heavy in dep.lower() for heavy in ['chart', 'moment', 'lodash', 'material']):
                    heavy_deps.append(dep)
            
            self.results['frontend']['heavy_dependencies'] = heavy_deps
            
            print(f"   ✅ Dependencias: {len(dependencies)}")
            print(f"   ✅ Dev Dependencies: {len(dev_dependencies)}")
            if heavy_deps:
                print(f"   ⚠️ Dependencias pesadas detectadas: {', '.join(heavy_deps)}")
        
        # Analizar tamaño de archivos
        src_path = frontend_path / "src"
        if src_path.exists():
            total_size = 0
            file_count = 0
            large_files = []
            
            for file_path in src_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                    size = file_path.stat().st_size
                    total_size += size
                    file_count += 1
                    
                    if size > 50000:  # Archivos > 50KB
                        large_files.append((str(file_path), size))
            
            self.results['frontend']['total_source_size'] = total_size
            self.results['frontend']['file_count'] = file_count
            self.results['frontend']['large_files'] = large_files
            
            print(f"   ✅ Archivos fuente: {file_count}")
            print(f"   ✅ Tamaño total: {total_size / 1024:.1f} KB")
            
            if large_files:
                print(f"   ⚠️ Archivos grandes detectados:")
                for file_path, size in large_files[:3]:
                    print(f"      - {Path(file_path).name}: {size / 1024:.1f} KB")
    
    def analyze_backend_performance(self):
        """Analizar performance del backend"""
        print("🔧 Analizando Performance del Backend...")
        
        backend_path = Path("/home/ubuntu/ecommerce-modular/backend/ecommerce-api")
        
        # Analizar archivos Python
        src_path = backend_path / "src"
        if src_path.exists():
            total_lines = 0
            file_count = 0
            complex_files = []
            
            for file_path in src_path.rglob("*.py"):
                if file_path.is_file():
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        line_count = len(lines)
                        total_lines += line_count
                        file_count += 1
                        
                        # Detectar archivos complejos (>200 líneas)
                        if line_count > 200:
                            complex_files.append((str(file_path), line_count))
                        
                        # Analizar imports
                        imports = [line.strip() for line in lines if line.strip().startswith('import') or line.strip().startswith('from')]
                        
            self.results['backend']['total_lines'] = total_lines
            self.results['backend']['file_count'] = file_count
            self.results['backend']['complex_files'] = complex_files
            
            print(f"   ✅ Archivos Python: {file_count}")
            print(f"   ✅ Líneas totales: {total_lines}")
            
            if complex_files:
                print(f"   ⚠️ Archivos complejos detectados:")
                for file_path, lines in complex_files[:3]:
                    print(f"      - {Path(file_path).name}: {lines} líneas")
        
        # Analizar requirements.txt
        requirements_file = backend_path / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file) as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            self.results['backend']['requirements_count'] = len(requirements)
            print(f"   ✅ Dependencias Python: {len(requirements)}")
    
    def analyze_database_queries(self):
        """Analizar queries de base de datos"""
        print("🗄️ Analizando Queries de Base de Datos...")
        
        # Buscar archivos con queries SQL
        backend_path = Path("/home/ubuntu/ecommerce-modular/backend/ecommerce-api/src")
        
        query_patterns = [
            r'SELECT\s+.*\s+FROM',
            r'INSERT\s+INTO',
            r'UPDATE\s+.*\s+SET',
            r'DELETE\s+FROM'
        ]
        
        total_queries = 0
        potential_issues = []
        
        for file_path in backend_path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for pattern in query_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        total_queries += len(matches)
                        
                        # Detectar queries potencialmente problemáticas
                        for match in matches:
                            if 'SELECT *' in match.upper():
                                potential_issues.append(f"SELECT * detectado en {file_path.name}")
                            if 'WHERE' not in match.upper() and 'DELETE' in match.upper():
                                potential_issues.append(f"DELETE sin WHERE en {file_path.name}")
                
                except Exception as e:
                    continue
        
        self.results['database']['total_queries'] = total_queries
        self.results['database']['potential_issues'] = potential_issues
        
        print(f"   ✅ Queries SQL detectadas: {total_queries}")
        if potential_issues:
            print(f"   ⚠️ Problemas potenciales:")
            for issue in potential_issues[:3]:
                print(f"      - {issue}")
    
    def analyze_system_resources(self):
        """Analizar recursos del sistema"""
        print("💻 Analizando Recursos del Sistema...")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / (1024**3)  # GB
        
        # Disco
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_free = disk.free / (1024**3)  # GB
        
        self.results['system'] = {
            'cpu_percent': cpu_percent,
            'cpu_count': cpu_count,
            'memory_percent': memory_percent,
            'memory_available_gb': memory_available,
            'disk_percent': disk_percent,
            'disk_free_gb': disk_free
        }
        
        print(f"   ✅ CPU: {cpu_percent}% ({cpu_count} cores)")
        print(f"   ✅ Memoria: {memory_percent}% usado ({memory_available:.1f} GB disponible)")
        print(f"   ✅ Disco: {disk_percent}% usado ({disk_free:.1f} GB libre)")
    
    def generate_recommendations(self):
        """Generar recomendaciones de optimización"""
        print("💡 Generando Recomendaciones...")
        
        recommendations = []
        
        # Frontend recommendations
        if self.results['frontend'].get('heavy_dependencies'):
            recommendations.append({
                'category': 'Frontend',
                'priority': 'High',
                'issue': 'Dependencias pesadas detectadas',
                'solution': 'Considerar alternativas más ligeras o lazy loading',
                'impact': 'Reducción de 20-40% en bundle size'
            })
        
        if self.results['frontend'].get('large_files'):
            recommendations.append({
                'category': 'Frontend',
                'priority': 'Medium',
                'issue': 'Archivos grandes detectados',
                'solution': 'Dividir componentes grandes en módulos más pequeños',
                'impact': 'Mejor tree-shaking y code splitting'
            })
        
        # Backend recommendations
        if self.results['backend'].get('complex_files'):
            recommendations.append({
                'category': 'Backend',
                'priority': 'Medium',
                'issue': 'Archivos complejos detectados',
                'solution': 'Refactorizar en módulos más pequeños y específicos',
                'impact': 'Mejor mantenibilidad y testing'
            })
        
        # Database recommendations
        if self.results['database'].get('potential_issues'):
            recommendations.append({
                'category': 'Database',
                'priority': 'High',
                'issue': 'Queries potencialmente problemáticas',
                'solution': 'Optimizar queries y añadir índices apropiados',
                'impact': 'Mejora de 50-80% en tiempo de respuesta'
            })
        
        # System recommendations
        system = self.results['system']
        if system.get('memory_percent', 0) > 80:
            recommendations.append({
                'category': 'System',
                'priority': 'High',
                'issue': 'Alto uso de memoria',
                'solution': 'Optimizar uso de memoria o aumentar recursos',
                'impact': 'Mejor estabilidad del sistema'
            })
        
        if system.get('cpu_percent', 0) > 70:
            recommendations.append({
                'category': 'System',
                'priority': 'Medium',
                'issue': 'Alto uso de CPU',
                'solution': 'Optimizar algoritmos o implementar cache',
                'impact': 'Mejor tiempo de respuesta'
            })
        
        # Performance recommendations generales
        recommendations.extend([
            {
                'category': 'Performance',
                'priority': 'High',
                'issue': 'Implementar cache distribuido',
                'solution': 'Configurar Redis para cache de queries y sesiones',
                'impact': 'Reducción de 60-80% en tiempo de respuesta'
            },
            {
                'category': 'Performance',
                'priority': 'Medium',
                'issue': 'Optimizar imágenes',
                'solution': 'Implementar WebP, lazy loading y CDN',
                'impact': 'Reducción de 40-60% en tiempo de carga'
            },
            {
                'category': 'Performance',
                'priority': 'Medium',
                'issue': 'Implementar code splitting',
                'solution': 'Dividir bundle en chunks más pequeños',
                'impact': 'Mejora de 30-50% en First Contentful Paint'
            }
        ])
        
        self.results['recommendations'] = recommendations
        
        print(f"   ✅ {len(recommendations)} recomendaciones generadas")
    
    def generate_report(self):
        """Generar reporte completo"""
        print("\n" + "="*70)
        print("📊 REPORTE DE ANÁLISIS DE PERFORMANCE")
        print("="*70)
        
        # Frontend Analysis
        print("\n📦 ANÁLISIS DEL FRONTEND:")
        frontend = self.results['frontend']
        if frontend:
            print(f"   - Dependencias: {frontend.get('dependencies_count', 0)}")
            print(f"   - Archivos fuente: {frontend.get('file_count', 0)}")
            print(f"   - Tamaño total: {frontend.get('total_source_size', 0) / 1024:.1f} KB")
            
            if frontend.get('heavy_dependencies'):
                print(f"   ⚠️ Dependencias pesadas: {len(frontend['heavy_dependencies'])}")
        
        # Backend Analysis
        print("\n🔧 ANÁLISIS DEL BACKEND:")
        backend = self.results['backend']
        if backend:
            print(f"   - Archivos Python: {backend.get('file_count', 0)}")
            print(f"   - Líneas de código: {backend.get('total_lines', 0)}")
            print(f"   - Dependencias: {backend.get('requirements_count', 0)}")
            
            if backend.get('complex_files'):
                print(f"   ⚠️ Archivos complejos: {len(backend['complex_files'])}")
        
        # Database Analysis
        print("\n🗄️ ANÁLISIS DE BASE DE DATOS:")
        database = self.results['database']
        if database:
            print(f"   - Queries detectadas: {database.get('total_queries', 0)}")
            
            if database.get('potential_issues'):
                print(f"   ⚠️ Problemas potenciales: {len(database['potential_issues'])}")
        
        # System Analysis
        print("\n💻 ANÁLISIS DEL SISTEMA:")
        system = self.results['system']
        if system:
            print(f"   - CPU: {system.get('cpu_percent', 0):.1f}% ({system.get('cpu_count', 0)} cores)")
            print(f"   - Memoria: {system.get('memory_percent', 0):.1f}% usado")
            print(f"   - Disco: {system.get('disk_percent', 0):.1f}% usado")
        
        # Recommendations
        print("\n💡 RECOMENDACIONES DE OPTIMIZACIÓN:")
        recommendations = self.results['recommendations']
        
        high_priority = [r for r in recommendations if r['priority'] == 'High']
        medium_priority = [r for r in recommendations if r['priority'] == 'Medium']
        
        if high_priority:
            print("\n   🔴 PRIORIDAD ALTA:")
            for i, rec in enumerate(high_priority, 1):
                print(f"   {i}. [{rec['category']}] {rec['issue']}")
                print(f"      Solución: {rec['solution']}")
                print(f"      Impacto: {rec['impact']}")
                print()
        
        if medium_priority:
            print("   🟡 PRIORIDAD MEDIA:")
            for i, rec in enumerate(medium_priority, 1):
                print(f"   {i}. [{rec['category']}] {rec['issue']}")
                print(f"      Solución: {rec['solution']}")
                print(f"      Impacto: {rec['impact']}")
                print()
        
        # Score general
        total_issues = len([r for r in recommendations if r['priority'] == 'High']) * 2 + \
                      len([r for r in recommendations if r['priority'] == 'Medium'])
        
        if total_issues <= 3:
            score = "EXCELENTE"
            color = "🟢"
        elif total_issues <= 6:
            score = "BUENO"
            color = "🟡"
        elif total_issues <= 10:
            score = "REGULAR"
            color = "🟠"
        else:
            score = "NECESITA MEJORAS"
            color = "🔴"
        
        print(f"\n🎯 EVALUACIÓN GENERAL: {color} {score}")
        print(f"   - Issues de alta prioridad: {len(high_priority)}")
        print(f"   - Issues de media prioridad: {len(medium_priority)}")
        print(f"   - Score total: {max(0, 100 - total_issues * 5)}/100")
        
        return self.results

def main():
    """Función principal"""
    print("🚀 INICIANDO ANÁLISIS DE PERFORMANCE")
    print("="*70)
    
    analyzer = PerformanceAnalyzer()
    
    # Ejecutar análisis
    analyzer.analyze_frontend_bundle()
    analyzer.analyze_backend_performance()
    analyzer.analyze_database_queries()
    analyzer.analyze_system_resources()
    analyzer.generate_recommendations()
    
    # Generar reporte
    results = analyzer.generate_report()
    
    # Guardar resultados
    output_file = "/home/ubuntu/performance_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    print("\n🏁 Análisis completado")

if __name__ == "__main__":
    main()

