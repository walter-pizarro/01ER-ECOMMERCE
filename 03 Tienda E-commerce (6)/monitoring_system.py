#!/usr/bin/env python3
"""
Sistema de Monitoreo y Logging para eCommerce en Producción
Incluye logging estructurado, métricas, alertas y observabilidad
"""

import logging
import json
import time
import psutil
import requests
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import os

class StructuredLogger:
    def __init__(self, name, log_file=None, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Formatter para logs estructurados
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler si se especifica
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_event(self, level, event_type, message, **kwargs):
        """Log estructurado con metadatos"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'message': message,
            'metadata': kwargs
        }
        
        log_message = json.dumps(log_data)
        
        if level == 'info':
            self.logger.info(log_message)
        elif level == 'warning':
            self.logger.warning(log_message)
        elif level == 'error':
            self.logger.error(log_message)
        elif level == 'critical':
            self.logger.critical(log_message)

class SystemMonitor:
    def __init__(self):
        self.logger = StructuredLogger('SystemMonitor', '/opt/ecommerce-production/logs/monitor.log')
        self.metrics = {}
        self.alerts = []
        
    def collect_system_metrics(self):
        """Recopilar métricas del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            # Red
            net_io = psutil.net_io_counters()
            
            self.metrics['system'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'percent': memory_percent,
                    'used_gb': round(memory_used, 2),
                    'total_gb': round(memory_total, 2)
                },
                'disk': {
                    'percent': disk_percent,
                    'used_gb': round(disk_used, 2),
                    'total_gb': round(disk_total, 2)
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            }
            
            self.logger.log_event('info', 'system_metrics', 'System metrics collected', **self.metrics['system'])
            
            # Verificar umbrales y generar alertas
            self._check_system_thresholds()
            
        except Exception as e:
            self.logger.log_event('error', 'system_metrics_error', f'Error collecting system metrics: {str(e)}')
    
    def collect_application_metrics(self):
        """Recopilar métricas de la aplicación"""
        try:
            # Health check de servicios
            services = {
                'frontend': 'http://localhost:3000/health',
                'backend': 'http://localhost:5000/health',
                'nginx': 'http://localhost/health'
            }
            
            service_status = {}
            
            for service, url in services.items():
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=5)
                    response_time = time.time() - start_time
                    
                    service_status[service] = {
                        'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                        'response_time': round(response_time, 3),
                        'status_code': response.status_code
                    }
                except Exception as e:
                    service_status[service] = {
                        'status': 'down',
                        'error': str(e),
                        'response_time': None
                    }
            
            self.metrics['application'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'services': service_status
            }
            
            self.logger.log_event('info', 'application_metrics', 'Application metrics collected', **self.metrics['application'])
            
            # Verificar servicios críticos
            self._check_service_health(service_status)
            
        except Exception as e:
            self.logger.log_event('error', 'application_metrics_error', f'Error collecting application metrics: {str(e)}')
    
    def collect_database_metrics(self):
        """Recopilar métricas de base de datos"""
        try:
            # Conectar a MySQL y obtener métricas
            import mysql.connector
            
            config = {
                'host': os.getenv('DATABASE_HOST', 'localhost'),
                'port': int(os.getenv('DATABASE_PORT', 3306)),
                'user': os.getenv('DATABASE_USER', 'root'),
                'password': os.getenv('DATABASE_PASSWORD', ''),
                'database': os.getenv('DATABASE_NAME', 'ecommerce_prod')
            }
            
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor(dictionary=True)
            
            # Obtener estadísticas de conexiones
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            connections = cursor.fetchone()['Value']
            
            cursor.execute("SHOW STATUS LIKE 'Threads_running'")
            running_threads = cursor.fetchone()['Value']
            
            cursor.execute("SHOW STATUS LIKE 'Queries'")
            total_queries = cursor.fetchone()['Value']
            
            # Obtener tamaño de base de datos
            cursor.execute("""
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS db_size_mb
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, (config['database'],))
            db_size = cursor.fetchone()['db_size_mb']
            
            # Obtener queries lentas
            cursor.execute("SHOW STATUS LIKE 'Slow_queries'")
            slow_queries = cursor.fetchone()['Value']
            
            cursor.close()
            conn.close()
            
            self.metrics['database'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'connections': int(connections),
                'running_threads': int(running_threads),
                'total_queries': int(total_queries),
                'db_size_mb': float(db_size) if db_size else 0,
                'slow_queries': int(slow_queries)
            }
            
            self.logger.log_event('info', 'database_metrics', 'Database metrics collected', **self.metrics['database'])
            
            # Verificar umbrales de base de datos
            self._check_database_thresholds()
            
        except Exception as e:
            self.logger.log_event('error', 'database_metrics_error', f'Error collecting database metrics: {str(e)}')
    
    def _check_system_thresholds(self):
        """Verificar umbrales del sistema y generar alertas"""
        system = self.metrics.get('system', {})
        
        # CPU > 80%
        if system.get('cpu', {}).get('percent', 0) > 80:
            self._create_alert('critical', 'high_cpu_usage', 
                             f"CPU usage is {system['cpu']['percent']}%")
        
        # Memoria > 85%
        if system.get('memory', {}).get('percent', 0) > 85:
            self._create_alert('critical', 'high_memory_usage', 
                             f"Memory usage is {system['memory']['percent']}%")
        
        # Disco > 90%
        if system.get('disk', {}).get('percent', 0) > 90:
            self._create_alert('critical', 'high_disk_usage', 
                             f"Disk usage is {system['disk']['percent']}%")
    
    def _check_service_health(self, service_status):
        """Verificar salud de servicios"""
        for service, status in service_status.items():
            if status['status'] != 'healthy':
                self._create_alert('critical', 'service_down', 
                                 f"Service {service} is {status['status']}")
            elif status.get('response_time', 0) > 5:
                self._create_alert('warning', 'slow_response', 
                                 f"Service {service} response time is {status['response_time']}s")
    
    def _check_database_thresholds(self):
        """Verificar umbrales de base de datos"""
        db = self.metrics.get('database', {})
        
        # Conexiones > 150
        if db.get('connections', 0) > 150:
            self._create_alert('warning', 'high_db_connections', 
                             f"Database connections: {db['connections']}")
        
        # Queries lentas > 100
        if db.get('slow_queries', 0) > 100:
            self._create_alert('warning', 'slow_queries', 
                             f"Slow queries detected: {db['slow_queries']}")
    
    def _create_alert(self, severity, alert_type, message):
        """Crear alerta"""
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'severity': severity,
            'type': alert_type,
            'message': message
        }
        
        self.alerts.append(alert)
        self.logger.log_event(severity, 'alert_generated', message, alert_type=alert_type)
        
        # Enviar notificación si es crítica
        if severity == 'critical':
            self._send_alert_notification(alert)
    
    def _send_alert_notification(self, alert):
        """Enviar notificación de alerta crítica"""
        try:
            # Configuración SMTP
            smtp_host = os.getenv('SMTP_HOST')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not all([smtp_host, smtp_user, smtp_password]):
                self.logger.log_event('warning', 'notification_skip', 'SMTP not configured')
                return
            
            # Crear mensaje
            msg = MimeMultipart()
            msg['From'] = smtp_user
            msg['To'] = os.getenv('ALERT_EMAIL', smtp_user)
            msg['Subject'] = f"🚨 ALERTA CRÍTICA - eCommerce Producción"
            
            body = f"""
            ALERTA CRÍTICA DETECTADA
            
            Tipo: {alert['type']}
            Severidad: {alert['severity']}
            Mensaje: {alert['message']}
            Timestamp: {alert['timestamp']}
            
            Por favor, revise el sistema inmediatamente.
            
            Dashboard: http://localhost:3001
            Logs: /opt/ecommerce-production/logs/
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.log_event('info', 'alert_sent', f'Alert notification sent for {alert["type"]}')
            
        except Exception as e:
            self.logger.log_event('error', 'notification_error', f'Failed to send alert: {str(e)}')
    
    def generate_metrics_report(self):
        """Generar reporte de métricas"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': self.metrics.get('system', {}),
            'application': self.metrics.get('application', {}),
            'database': self.metrics.get('database', {}),
            'alerts': self.alerts[-10:]  # Últimas 10 alertas
        }
        
        # Guardar reporte
        report_file = f"/opt/ecommerce-production/logs/metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

class LogAnalyzer:
    def __init__(self):
        self.logger = StructuredLogger('LogAnalyzer')
        self.log_patterns = {
            'error': r'ERROR|CRITICAL|Exception|Traceback',
            'warning': r'WARNING|WARN',
            'performance': r'slow|timeout|performance',
            'security': r'unauthorized|forbidden|attack|injection'
        }
    
    def analyze_logs(self, log_file, hours=1):
        """Analizar logs de las últimas horas"""
        try:
            if not Path(log_file).exists():
                return {}
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            analysis = {
                'total_lines': len(lines),
                'error_count': 0,
                'warning_count': 0,
                'performance_issues': 0,
                'security_events': 0,
                'recent_errors': []
            }
            
            for line in lines:
                # Verificar si la línea es reciente
                try:
                    # Extraer timestamp de la línea de log
                    timestamp_str = line.split(' - ')[0]
                    log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    
                    if log_time < cutoff_time:
                        continue
                except:
                    continue
                
                # Analizar patrones
                line_lower = line.lower()
                
                if 'error' in line_lower or 'critical' in line_lower:
                    analysis['error_count'] += 1
                    if len(analysis['recent_errors']) < 5:
                        analysis['recent_errors'].append(line.strip())
                
                if 'warning' in line_lower:
                    analysis['warning_count'] += 1
                
                if any(word in line_lower for word in ['slow', 'timeout', 'performance']):
                    analysis['performance_issues'] += 1
                
                if any(word in line_lower for word in ['unauthorized', 'forbidden', 'attack']):
                    analysis['security_events'] += 1
            
            return analysis
            
        except Exception as e:
            self.logger.log_event('error', 'log_analysis_error', f'Error analyzing logs: {str(e)}')
            return {}

def main():
    """Función principal de monitoreo"""
    print("🔍 INICIANDO SISTEMA DE MONITOREO")
    print("=" * 50)
    
    monitor = SystemMonitor()
    log_analyzer = LogAnalyzer()
    
    # Crear directorios de logs si no existen
    Path("/opt/ecommerce-production/logs").mkdir(parents=True, exist_ok=True)
    
    try:
        while True:
            print(f"\n📊 Recopilando métricas - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Recopilar métricas
            monitor.collect_system_metrics()
            monitor.collect_application_metrics()
            monitor.collect_database_metrics()
            
            # Analizar logs
            log_files = [
                '/opt/ecommerce-production/logs/app.log',
                '/opt/ecommerce-production/logs/nginx/access.log',
                '/opt/ecommerce-production/logs/nginx/error.log'
            ]
            
            for log_file in log_files:
                if Path(log_file).exists():
                    analysis = log_analyzer.analyze_logs(log_file)
                    if analysis.get('error_count', 0) > 0:
                        monitor.logger.log_event('warning', 'log_errors_detected', 
                                               f'Found {analysis["error_count"]} errors in {log_file}')
            
            # Generar reporte
            report = monitor.generate_metrics_report()
            
            # Mostrar resumen
            print(f"✅ Sistema: CPU {monitor.metrics.get('system', {}).get('cpu', {}).get('percent', 0):.1f}%, "
                  f"RAM {monitor.metrics.get('system', {}).get('memory', {}).get('percent', 0):.1f}%")
            
            services = monitor.metrics.get('application', {}).get('services', {})
            healthy_services = sum(1 for s in services.values() if s.get('status') == 'healthy')
            print(f"🔧 Servicios: {healthy_services}/{len(services)} saludables")
            
            if monitor.alerts:
                print(f"🚨 Alertas activas: {len([a for a in monitor.alerts if a['severity'] == 'critical'])}")
            
            # Esperar 60 segundos antes del próximo ciclo
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en monitoreo: {str(e)}")

if __name__ == "__main__":
    main()

