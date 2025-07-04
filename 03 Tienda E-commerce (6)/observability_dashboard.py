#!/usr/bin/env python3
"""
Dashboard de Observabilidad en Tiempo Real
Genera dashboard web para monitoreo del sistema eCommerce
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

app = Flask(__name__)

class ObservabilityDashboard:
    def __init__(self):
        self.db_path = "/opt/ecommerce-production/logs/metrics.db"
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos SQLite para métricas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                severity TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_metric(self, metric_type, metric_name, value, metadata=None):
        """Almacenar métrica en base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (metric_type, metric_name, value, metadata)
            VALUES (?, ?, ?, ?)
        ''', (metric_type, metric_name, value, json.dumps(metadata) if metadata else None))
        
        conn.commit()
        conn.close()
    
    def get_metrics(self, metric_type=None, hours=24):
        """Obtener métricas de las últimas horas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if metric_type:
            cursor.execute('''
                SELECT timestamp, metric_name, value, metadata
                FROM metrics
                WHERE metric_type = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (metric_type, cutoff_time))
        else:
            cursor.execute('''
                SELECT timestamp, metric_type, metric_name, value, metadata
                FROM metrics
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (cutoff_time,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_current_status(self):
        """Obtener estado actual del sistema"""
        # Leer último reporte de métricas
        log_dir = Path("/opt/ecommerce-production/logs")
        
        # Buscar el archivo de reporte más reciente
        report_files = list(log_dir.glob("metrics_report_*.json"))
        if not report_files:
            return {"status": "no_data"}
        
        latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_report, 'r') as f:
                data = json.load(f)
            return data
        except:
            return {"status": "error"}

dashboard = ObservabilityDashboard()

@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API para obtener estado actual"""
    status = dashboard.get_current_status()
    return jsonify(status)

@app.route('/api/metrics/<metric_type>')
def api_metrics(metric_type):
    """API para obtener métricas específicas"""
    hours = request.args.get('hours', 24, type=int)
    metrics = dashboard.get_metrics(metric_type, hours)
    
    # Formatear datos para gráficos
    formatted_data = []
    for metric in metrics:
        formatted_data.append({
            'timestamp': metric[0],
            'name': metric[1],
            'value': metric[2],
            'metadata': json.loads(metric[3]) if metric[3] else None
        })
    
    return jsonify(formatted_data)

@app.route('/api/alerts')
def api_alerts():
    """API para obtener alertas activas"""
    conn = sqlite3.connect(dashboard.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, severity, alert_type, message
        FROM alerts
        WHERE resolved = FALSE
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    
    alerts = []
    for row in cursor.fetchall():
        alerts.append({
            'timestamp': row[0],
            'severity': row[1],
            'type': row[2],
            'message': row[3]
        })
    
    conn.close()
    return jsonify(alerts)

# Template HTML para el dashboard
dashboard_html = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eCommerce - Dashboard de Observabilidad</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        
        .header {
            background: #2563eb;
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .card h3 {
            margin-bottom: 1rem;
            color: #374151;
            font-size: 1.1rem;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-value {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .status-healthy { color: #10b981; }
        .status-warning { color: #f59e0b; }
        .status-critical { color: #ef4444; }
        
        .alert {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 4px;
            border-left: 4px solid;
        }
        
        .alert-critical {
            background: #fef2f2;
            border-color: #ef4444;
            color: #991b1b;
        }
        
        .alert-warning {
            background: #fffbeb;
            border-color: #f59e0b;
            color: #92400e;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 1rem;
        }
        
        .refresh-btn {
            background: #2563eb;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .refresh-btn:hover {
            background: #1d4ed8;
        }
        
        .timestamp {
            font-size: 0.8rem;
            color: #6b7280;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 eCommerce - Dashboard de Observabilidad</h1>
    </div>
    
    <div class="container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <h2>Estado del Sistema en Tiempo Real</h2>
            <button class="refresh-btn" onclick="refreshData()">🔄 Actualizar</button>
        </div>
        
        <div class="grid">
            <!-- Estado del Sistema -->
            <div class="card">
                <h3>💻 Sistema</h3>
                <div id="system-metrics">
                    <div class="metric">
                        <span>CPU</span>
                        <span class="metric-value" id="cpu-usage">--</span>
                    </div>
                    <div class="metric">
                        <span>Memoria</span>
                        <span class="metric-value" id="memory-usage">--</span>
                    </div>
                    <div class="metric">
                        <span>Disco</span>
                        <span class="metric-value" id="disk-usage">--</span>
                    </div>
                </div>
            </div>
            
            <!-- Estado de Servicios -->
            <div class="card">
                <h3>🔧 Servicios</h3>
                <div id="service-status">
                    <div class="metric">
                        <span>Frontend</span>
                        <span class="metric-value" id="frontend-status">--</span>
                    </div>
                    <div class="metric">
                        <span>Backend</span>
                        <span class="metric-value" id="backend-status">--</span>
                    </div>
                    <div class="metric">
                        <span>Nginx</span>
                        <span class="metric-value" id="nginx-status">--</span>
                    </div>
                </div>
            </div>
            
            <!-- Base de Datos -->
            <div class="card">
                <h3>🗄️ Base de Datos</h3>
                <div id="database-metrics">
                    <div class="metric">
                        <span>Conexiones</span>
                        <span class="metric-value" id="db-connections">--</span>
                    </div>
                    <div class="metric">
                        <span>Queries Lentas</span>
                        <span class="metric-value" id="slow-queries">--</span>
                    </div>
                    <div class="metric">
                        <span>Tamaño DB</span>
                        <span class="metric-value" id="db-size">--</span>
                    </div>
                </div>
            </div>
            
            <!-- Alertas -->
            <div class="card">
                <h3>🚨 Alertas Activas</h3>
                <div id="alerts-container">
                    <p style="color: #6b7280;">Cargando alertas...</p>
                </div>
            </div>
        </div>
        
        <!-- Gráficos -->
        <div class="grid">
            <div class="card">
                <h3>📊 CPU y Memoria (24h)</h3>
                <div class="chart-container">
                    <canvas id="systemChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h3>⚡ Tiempo de Respuesta</h3>
                <div class="chart-container">
                    <canvas id="responseChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="timestamp" id="last-update">
            Última actualización: --
        </div>
    </div>
    
    <script>
        let systemChart, responseChart;
        
        function initCharts() {
            // Gráfico de sistema
            const systemCtx = document.getElementById('systemChart').getContext('2d');
            systemChart = new Chart(systemCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Memoria %',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
            
            // Gráfico de tiempo de respuesta
            const responseCtx = document.getElementById('responseChart').getContext('2d');
            responseChart = new Chart(responseCtx, {
                type: 'bar',
                data: {
                    labels: ['Frontend', 'Backend', 'Nginx'],
                    datasets: [{
                        label: 'Tiempo de Respuesta (ms)',
                        data: [0, 0, 0],
                        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        async function refreshData() {
            try {
                // Obtener estado actual
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateSystemMetrics(data.system || {});
                updateServiceStatus(data.application?.services || {});
                updateDatabaseMetrics(data.database || {});
                
                // Obtener alertas
                const alertsResponse = await fetch('/api/alerts');
                const alerts = await alertsResponse.json();
                updateAlerts(alerts);
                
                // Actualizar timestamp
                document.getElementById('last-update').textContent = 
                    `Última actualización: ${new Date().toLocaleString()}`;
                
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }
        
        function updateSystemMetrics(system) {
            const cpu = system.cpu?.percent || 0;
            const memory = system.memory?.percent || 0;
            const disk = system.disk?.percent || 0;
            
            document.getElementById('cpu-usage').textContent = `${cpu.toFixed(1)}%`;
            document.getElementById('memory-usage').textContent = `${memory.toFixed(1)}%`;
            document.getElementById('disk-usage').textContent = `${disk.toFixed(1)}%`;
            
            // Actualizar colores según umbrales
            updateMetricColor('cpu-usage', cpu, 80, 90);
            updateMetricColor('memory-usage', memory, 85, 95);
            updateMetricColor('disk-usage', disk, 80, 90);
        }
        
        function updateServiceStatus(services) {
            const serviceElements = {
                'frontend': 'frontend-status',
                'backend': 'backend-status',
                'nginx': 'nginx-status'
            };
            
            Object.entries(serviceElements).forEach(([service, elementId]) => {
                const element = document.getElementById(elementId);
                const status = services[service]?.status || 'unknown';
                const responseTime = services[service]?.response_time || 0;
                
                element.textContent = status === 'healthy' ? 
                    `✅ ${(responseTime * 1000).toFixed(0)}ms` : 
                    `❌ ${status}`;
                
                element.className = `metric-value status-${status === 'healthy' ? 'healthy' : 'critical'}`;
            });
            
            // Actualizar gráfico de tiempo de respuesta
            if (responseChart) {
                responseChart.data.datasets[0].data = [
                    (services.frontend?.response_time || 0) * 1000,
                    (services.backend?.response_time || 0) * 1000,
                    (services.nginx?.response_time || 0) * 1000
                ];
                responseChart.update();
            }
        }
        
        function updateDatabaseMetrics(database) {
            document.getElementById('db-connections').textContent = database.connections || '--';
            document.getElementById('slow-queries').textContent = database.slow_queries || '--';
            document.getElementById('db-size').textContent = 
                database.db_size_mb ? `${database.db_size_mb} MB` : '--';
        }
        
        function updateAlerts(alerts) {
            const container = document.getElementById('alerts-container');
            
            if (alerts.length === 0) {
                container.innerHTML = '<p style="color: #10b981;">✅ No hay alertas activas</p>';
                return;
            }
            
            container.innerHTML = alerts.slice(0, 5).map(alert => `
                <div class="alert alert-${alert.severity}">
                    <strong>${alert.type}</strong><br>
                    ${alert.message}<br>
                    <small>${new Date(alert.timestamp).toLocaleString()}</small>
                </div>
            `).join('');
        }
        
        function updateMetricColor(elementId, value, warningThreshold, criticalThreshold) {
            const element = document.getElementById(elementId);
            element.className = 'metric-value';
            
            if (value >= criticalThreshold) {
                element.classList.add('status-critical');
            } else if (value >= warningThreshold) {
                element.classList.add('status-warning');
            } else {
                element.classList.add('status-healthy');
            }
        }
        
        // Inicializar
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            refreshData();
            
            // Actualizar cada 30 segundos
            setInterval(refreshData, 30000);
        });
    </script>
</body>
</html>
'''

# Crear directorio de templates
templates_dir = Path("/home/ubuntu/ecommerce-modular/templates")
templates_dir.mkdir(exist_ok=True)

with open(templates_dir / "dashboard.html", "w") as f:
    f.write(dashboard_html)

if __name__ == "__main__":
    # Crear directorio de logs si no existe
    Path("/opt/ecommerce-production/logs").mkdir(parents=True, exist_ok=True)
    
    print("🚀 Iniciando Dashboard de Observabilidad")
    print("📊 Acceso: http://localhost:8080")
    
    app.run(host='0.0.0.0', port=8080, debug=False)

