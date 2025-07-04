"""
TIENDAS TRESMAS - Sistema Completo y Profesional
Versión de Despliegue Simplificada
"""

import os
import json
import jwt
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración
SECRET_KEY = "tresmas_secret_key_2025_real"
JWT_EXPIRATION_HOURS = 24

class TresmasDatabase:
    """Base de datos simplificada del sistema TIENDAS TRESMAS"""
    
    def __init__(self):
        self.init_planes_reales()
        self.init_clientes()
        self.init_productos()
        self.init_usuarios()
        
    def init_planes_reales(self):
        """Planes reales según especificaciones exactas del usuario JUNIO 2025"""
        self.planes = [
            {
                "id": 1,
                "nombre": "PLAN TIENDA MENSUAL | WEB E-Commerce ONE",
                "tipo": "mensual",
                "precio_mensual": 20000,
                "precio_anual": 270000,
                "pago_inicial": 70000,
                "caracteristicas": [
                    "Sitio Web Tienda on Line (E-commerce)",
                    "Tienda Auto Administrable",
                    "Buscador de Productos",
                    "Gestionar Estado de Pedidos",
                    "Administrador de Clientes",
                    "Implementacion Formas de Pagos",
                    "Diseño Personalizado",
                    "1 Dominio profesional",
                    "10 Correos Corporativos",
                    "Catalogo de Productos (200 Prd.)",
                    "Productos Destacados",
                    "Ficha Técnica",
                    "Posicionamiento SEO",
                    "Modificaciones Anuales (8)",
                    "Diseño Responsive (Adaptativo)",
                    "Incluye Hosting de alto rendimiento por Un Año",
                    "Incluye Certificado SSL",
                    "Formulario de Contacto",
                    "Chat Whatsapp en linea",
                    "Link a Redes Sociales",
                    "Mapa de Google",
                    "Perfil Google My Business",
                    "Página de Facebook para empresas",
                    "Página de Instagram para empresas",
                    "Transferencia mensual 20GB",
                    "Espacio en disco 4GB",
                    "Mas de 1000 Modelos Originales Elegant Themes Divi"
                ],
                "limite_productos": 200,
                "transferencia_gb": 20,
                "espacio_disco_gb": 4,
                "correos_corporativos": 10,
                "modificaciones_anuales": 8,
                "activo": True,
                "popular": False
            },
            {
                "id": 2,
                "nombre": "PLAN TIENDA ANUAL | WEB E-Commerce ONE",
                "tipo": "anual",
                "precio_mensual": 11250,
                "precio_anual": 180500,
                "pago_inicial": 100000,
                "ahorro": 135000,
                "caracteristicas": [
                    "Sitio Web Tienda on Line (E-commerce)",
                    "Tienda Auto Administrable",
                    "Buscador de Productos",
                    "Gestionar Estado de Pedidos",
                    "Administrador de Clientes",
                    "Implementacion Formas de Pagos",
                    "Diseño Personalizado",
                    "1 Dominio profesional",
                    "10 Correos Corporativos",
                    "Catalogo de Productos (200 Prd.)",
                    "Productos Destacados",
                    "Ficha Técnica",
                    "Posicionamiento SEO",
                    "Modificaciones Anuales (8)",
                    "Diseño Responsive (Adaptativo)",
                    "Incluye Hosting de alto rendimiento por Un Año",
                    "Incluye Certificado SSL",
                    "Formulario de Contacto",
                    "Chat Whatsapp en linea",
                    "Link a Redes Sociales",
                    "Mapa de Google",
                    "Perfil Google My Business",
                    "Página de Facebook para empresas",
                    "Página de Instagram para empresas",
                    "Transferencia mensual 20GB",
                    "Espacio en disco 4GB",
                    "Mas de 1000 Modelo Originales Elegant Themes Divi",
                    "AHORRO -50%: $135.000"
                ],
                "limite_productos": 200,
                "transferencia_gb": 20,
                "espacio_disco_gb": 4,
                "correos_corporativos": 10,
                "modificaciones_anuales": 8,
                "activo": True,
                "popular": True
            }
        ]
    
    def init_clientes(self):
        """Clientes del sistema"""
        self.clientes = [
            {
                "id": 1,
                "nombre": "Cliente Demo",
                "email": "cliente@demo.com",
                "telefono": "+56912345678",
                "plan_id": 1,
                "fecha_registro": "2025-01-01",
                "activo": True
            }
        ]
    
    def init_productos(self):
        """Productos del sistema"""
        self.productos = []
    
    def init_usuarios(self):
        """Usuarios administradores"""
        self.usuarios = [
            {
                "id": 1,
                "email": "admin@tresmas.cl",
                "password": self.hash_password("admin123"),
                "nombre": "Administrador",
                "rol": "admin",
                "activo": True,
                "fecha_creacion": "2025-01-01"
            }
        ]
    
    def hash_password(self, password):
        """Hash de contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()

# Inicializar base de datos
db = TresmasDatabase()

def generate_jwt_token(user_data):
    """Generar token JWT"""
    payload = {
        'user_id': user_data['id'],
        'email': user_data['email'],
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Rutas principales
@app.route('/')
def home():
    """Página principal - servir frontend"""
    return send_from_directory('static', 'index.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Login de administrador"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email y contraseña requeridos"}), 400
        
        # Buscar usuario
        usuario = None
        for user in db.usuarios:
            if user['email'] == email and user['password'] == db.hash_password(password):
                usuario = user
                break
        
        if not usuario:
            return jsonify({"error": "Credenciales inválidas"}), 401
        
        # Generar token
        token = generate_jwt_token(usuario)
        
        return jsonify({
            "success": True,
            "token": token,
            "usuario": {
                "id": usuario['id'],
                "email": usuario['email'],
                "nombre": usuario['nombre'],
                "rol": usuario['rol']
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Error en login: {str(e)}"}), 500

@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Dashboard administrativo"""
    try:
        return jsonify({
            "success": True,
            "data": {
                "total_planes": len(db.planes),
                "total_clientes": len(db.clientes),
                "total_productos": len(db.productos),
                "planes_activos": len([p for p in db.planes if p.get('activo', True)]),
                "clientes_activos": len([c for c in db.clientes if c.get('activo', True)])
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Error en dashboard: {str(e)}"}), 500

@app.route('/admin/planes', methods=['GET'])
def get_planes():
    """Obtener todos los planes"""
    try:
        return jsonify({
            "success": True,
            "data": db.planes
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al obtener planes: {str(e)}"}), 500

@app.route('/admin/productos', methods=['GET'])
def get_productos():
    """Obtener todos los productos"""
    try:
        return jsonify({
            "success": True,
            "data": db.productos
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al obtener productos: {str(e)}"}), 500

@app.route('/admin/clientes', methods=['GET'])
def get_clientes():
    """Obtener todos los clientes"""
    try:
        return jsonify({
            "success": True,
            "data": db.clientes
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al obtener clientes: {str(e)}"}), 500

# Servir archivos estáticos
@app.route('/<path:filename>')
def serve_static(filename):
    """Servir archivos estáticos"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("🚀 Iniciando TIENDAS TRESMAS - Sistema Completo")
    print("📊 Planes cargados:", len(db.planes))
    print("👥 Clientes cargados:", len(db.clientes))
    print("📦 Productos cargados:", len(db.productos))
    print("✅ Sistema listo")
    
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)

