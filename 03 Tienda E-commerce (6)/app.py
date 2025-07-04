"""
Aplicación principal Flask para eCommerce Modular
Configuración de la aplicación, blueprints, middleware y documentación
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
import os
import sys
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar controladores
from controllers.auth_controller import auth_bp
from controllers.products_controller import products_bp
from controllers.orders_controller import orders_bp

# Importar configuración
from config.settings import get_config

def create_app(config_name='development'):
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Cargar configuración
    config = get_config(config_name)
    app.config.update(config)
    
    # Configurar CORS para permitir requests desde el frontend
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5173', '*'])
    
    # Configurar Swagger para documentación de APIs
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "eCommerce Modular API",
            "description": "API RESTful para sistema de eCommerce modular y escalable",
            "version": "1.0.0",
            "contact": {
                "name": "eCommerce Modular Team",
                "email": "api@ecommerce-modular.com"
            }
        },
        "host": "localhost:5000",
        "basePath": "/",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        },
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "tags": [
            {
                "name": "Authentication",
                "description": "Endpoints para autenticación y gestión de usuarios"
            },
            {
                "name": "Products",
                "description": "Endpoints para gestión del catálogo de productos"
            },
            {
                "name": "Orders",
                "description": "Endpoints para gestión de pedidos y transacciones"
            },
            {
                "name": "System",
                "description": "Endpoints del sistema y utilidades"
            }
        ]
    }
    
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    
    # Middleware para logging de requests
    @app.before_request
    def log_request_info():
        """Log información de cada request"""
        if app.config.get('DEBUG'):
            print(f"[{datetime.now()}] {request.method} {request.url}")
            if request.json:
                print(f"Body: {request.json}")
    
    # Middleware para headers de seguridad
    @app.after_request
    def add_security_headers(response):
        """Agregar headers de seguridad a todas las respuestas"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    # Rutas principales
    @app.route('/')
    def index():
        """
        Endpoint raíz de la API
        ---
        tags:
          - System
        responses:
          200:
            description: Información básica de la API
            schema:
              type: object
              properties:
                message:
                  type: string
                version:
                  type: string
                docs:
                  type: string
        """
        return jsonify({
            'message': 'eCommerce Modular API',
            'version': '1.0.0',
            'docs': '/docs/',
            'status': 'running',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/health')
    def health_check():
        """
        Health check endpoint
        ---
        tags:
          - System
        responses:
          200:
            description: Estado de salud de la API
            schema:
              type: object
              properties:
                status:
                  type: string
                timestamp:
                  type: string
                database:
                  type: string
        """
        # Verificar conexión a base de datos
        try:
            from config.database import get_database_url
            from sqlalchemy import create_engine, text
            
            engine = create_engine(get_database_url())
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': db_status,
            'version': '1.0.0'
        })
    
    @app.route('/api/v1/stats')
    def api_stats():
        """
        Estadísticas básicas de la API
        ---
        tags:
          - System
        responses:
          200:
            description: Estadísticas de la API
        """
        try:
            from config.database import get_database_url
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            
            engine = create_engine(get_database_url())
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Obtener estadísticas básicas
            stats = {}
            
            try:
                # Contar productos activos
                result = session.execute(text("SELECT COUNT(*) FROM products WHERE is_active = true"))
                stats['active_products'] = result.scalar()
            except:
                stats['active_products'] = 0
            
            try:
                # Contar usuarios
                result = session.execute(text("SELECT COUNT(*) FROM users WHERE is_active = true"))
                stats['active_users'] = result.scalar()
            except:
                stats['active_users'] = 0
            
            try:
                # Contar pedidos del último mes
                result = session.execute(text("""
                    SELECT COUNT(*) FROM orders 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """))
                stats['orders_last_30_days'] = result.scalar()
            except:
                stats['orders_last_30_days'] = 0
            
            session.close()
            
            return jsonify({
                'success': True,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Could not retrieve stats',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    # Manejadores de errores globales
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested endpoint was not found',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL',
            'timestamp': datetime.now().isoformat()
        }), 405
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server',
            'timestamp': datetime.now().isoformat()
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication is required',
            'timestamp': datetime.now().isoformat()
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'timestamp': datetime.now().isoformat()
        }), 403
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'success': False,
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.',
            'timestamp': datetime.now().isoformat()
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Manejador global de excepciones"""
        if app.config.get('DEBUG'):
            # En modo debug, mostrar el error completo
            import traceback
            return jsonify({
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }), 500
        else:
            # En producción, no mostrar detalles del error
            return jsonify({
                'success': False,
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    return app

# Crear instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Configuración para desarrollo
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting eCommerce Modular API on port {port}")
    print(f"Debug mode: {debug}")
    print(f"API Documentation: http://localhost:{port}/docs/")
    
    app.run(
        host='0.0.0.0',  # Permitir conexiones externas
        port=port,
        debug=debug,
        threaded=True
    )

