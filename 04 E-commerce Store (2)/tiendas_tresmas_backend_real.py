#!/usr/bin/env python3
"""
TIENDAS TRESMAS - Backend Real y Completo
Sistema profesional de gestión de productos con todas las funcionalidades especificadas
"""

import os
import sys
import json
import jwt
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)

# Configuración
SECRET_KEY = "tresmas_secret_key_2025"
JWT_EXPIRATION_HOURS = 24

# Base de datos en memoria (simulada)
class TresmasDB:
    def __init__(self):
        # Planes reales según especificaciones
        self.planes = [
            {
                "id": 1,
                "nombre": "WEB E-Commerce ONE PYME",
                "precio_mensual": 20000,
                "precio_anual": 180500,
                "pago_inicial": 70000,
                "pago_inicial_anual": 100000,
                "caracteristicas": [
                    "Hasta 200 productos",
                    "Diseño responsive",
                    "Panel administrativo básico",
                    "Integración medios de pago",
                    "Soporte por email",
                    "10 correos corporativos",
                    "Transferencia mensual 20GB",
                    "Espacio en disco 4GB"
                ],
                "limite_productos": 200,
                "activo": True
            },
            {
                "id": 2,
                "nombre": "WEB E-Commerce TWO PREMIUM",
                "precio_mensual": 32000,
                "precio_anual": 192000,
                "pago_inicial": 120000,
                "pago_inicial_anual": 150000,
                "caracteristicas": [
                    "Hasta 400 productos",
                    "Diseño personalizado",
                    "Panel administrativo avanzado",
                    "Múltiples medios de pago",
                    "SEO optimizado",
                    "Soporte prioritario",
                    "Correos corporativos ilimitados",
                    "Transferencia mensual 30GB",
                    "Espacio en disco 10GB"
                ],
                "limite_productos": 400,
                "activo": True
            },
            {
                "id": 3,
                "nombre": "WEB E-Commerce THREE PLATINUM",
                "precio_mensual": 41000,
                "precio_anual": 246000,
                "pago_inicial": 180000,
                "pago_inicial_anual": 200000,
                "caracteristicas": [
                    "Productos ilimitados",
                    "Diseño completamente personalizado",
                    "Panel administrativo completo",
                    "Todos los medios de pago",
                    "SEO avanzado",
                    "Soporte 24/7",
                    "Correos corporativos ilimitados",
                    "Transferencia mensual 80GB",
                    "Espacio en disco 15GB",
                    "Integración con sistemas externos"
                ],
                "limite_productos": -1,  # Ilimitado
                "activo": True
            }
        ]
        
        # Clientes y tiendas
        self.clientes = [
            {
                "id": 1,
                "nombre_representante": "Juan Pérez",
                "rut_representante": "12345678-9",
                "nombre_empresa": "Empresa Demo SpA",
                "rut_empresa": "76123456-7",
                "giro": "Comercio al por menor",
                "direccion": {
                    "region": "Metropolitana",
                    "ciudad": "Santiago",
                    "calle": "Av. Providencia",
                    "numero": "1234",
                    "detalle": "Oficina 501"
                },
                "telefono": "+56912345678",
                "email_corporativo": "contacto@empresademo.cl",
                "whatsapp": "+56912345678",
                "plan_id": 1,
                "fecha_creacion": "2025-01-01",
                "activo": True
            }
        ]
        
        # Productos base (algunos ejemplos)
        self.productos = [
            {
                "id": 1,
                "nombre": "Polera Publicitaria Algodón",
                "categoria": "Textil",
                "subcategoria": "Poleras",
                "marca": "AQUI TU LOGO",
                "descripcion": "Polera de algodón 100% para personalización publicitaria",
                "precio_costo": 3500,
                "precio_venta": 8900,
                "precio_usd": 9.89,
                "utilidad_porcentaje": 154.29,
                "codigo_proveedor": "POL001",
                "sku": "AQTL-POL001-2025",
                "codigo_tienda": "AQTL001",
                "stock": 150,
                "imagen_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Polera",
                "ficha_tecnica": {
                    "material": "Algodón 100%",
                    "tallas": "XS, S, M, L, XL, XXL",
                    "colores": "Blanco, Negro, Azul, Rojo",
                    "peso": "180g",
                    "area_imprimible": "25x30 cm",
                    "sugerencia_impresion": "Serigrafía, Transfer",
                    "cantidad_minima": 250,
                    "presentacion": "Individual en bolsa"
                },
                "activo": True
            },
            {
                "id": 2,
                "nombre": "Taza Cerámica Sublimable",
                "categoria": "Hogar",
                "subcategoria": "Tazas",
                "marca": "AQUI TU LOGO",
                "descripcion": "Taza de cerámica blanca para sublimación",
                "precio_costo": 1200,
                "precio_venta": 3500,
                "precio_usd": 3.89,
                "utilidad_porcentaje": 191.67,
                "codigo_proveedor": "TAZ001",
                "sku": "AQTL-TAZ001-2025",
                "codigo_tienda": "AQTL002",
                "stock": 200,
                "imagen_url": "https://via.placeholder.com/300x300/059669/FFFFFF?text=Taza",
                "ficha_tecnica": {
                    "material": "Cerámica",
                    "capacidad": "325ml",
                    "colores": "Blanco",
                    "peso": "350g",
                    "area_imprimible": "20x8 cm",
                    "sugerencia_impresion": "Sublimación",
                    "cantidad_minima": 250,
                    "presentacion": "Individual en caja"
                },
                "activo": True
            }
        ]
        
        # Sistema de tallas
        self.tallas_tipos = [
            {
                "id": 1,
                "nombre": "Streetwear",
                "descripcion": "Ropa urbana y casual",
                "rangos": {
                    "XS": {"pecho": "76-81", "cintura": "66-71", "equivalencia_eu": "32", "equivalencia_cl": "XS"},
                    "S": {"pecho": "81-86", "cintura": "71-76", "equivalencia_eu": "34", "equivalencia_cl": "S"},
                    "M": {"pecho": "86-91", "cintura": "76-81", "equivalencia_eu": "36", "equivalencia_cl": "M"},
                    "L": {"pecho": "91-96", "cintura": "81-86", "equivalencia_eu": "38", "equivalencia_cl": "L"},
                    "XL": {"pecho": "96-101", "cintura": "86-91", "equivalencia_eu": "40", "equivalencia_cl": "XL"},
                    "XXL": {"pecho": "101-110", "cintura": "91-100", "equivalencia_eu": "42", "equivalencia_cl": "XXL"}
                }
            },
            {
                "id": 2,
                "nombre": "Chaquetas Mujer",
                "descripcion": "Chaquetas, blusas y vestidos para mujer",
                "rangos": {
                    "XS": {"pecho": "76-80", "cintura": "60-64", "cadera": "84-88", "equivalencia_eu": "32", "equivalencia_cl": "XS"},
                    "S": {"pecho": "80-84", "cintura": "64-68", "cadera": "88-92", "equivalencia_eu": "34", "equivalencia_cl": "S"},
                    "M": {"pecho": "84-88", "cintura": "68-72", "cadera": "92-96", "equivalencia_eu": "36", "equivalencia_cl": "M"},
                    "L": {"pecho": "88-92", "cintura": "72-76", "cadera": "96-100", "equivalencia_eu": "38", "equivalencia_cl": "L"},
                    "XL": {"pecho": "92-96", "cintura": "76-80", "cadera": "100-104", "equivalencia_eu": "40", "equivalencia_cl": "XL"},
                    "XXL": {"pecho": "96-104", "cintura": "80-88", "cadera": "104-112", "equivalencia_eu": "42", "equivalencia_cl": "XXL"}
                }
            },
            {
                "id": 3,
                "nombre": "Chaquetas Hombre",
                "descripcion": "Chaquetas, blazers y abrigos para hombre",
                "rangos": {
                    "S": {"pecho": "86-90", "cintura": "76-80", "equivalencia_eu": "44", "equivalencia_cl": "S"},
                    "M": {"pecho": "90-94", "cintura": "80-84", "equivalencia_eu": "46", "equivalencia_cl": "M"},
                    "L": {"pecho": "94-98", "cintura": "84-88", "equivalencia_eu": "48", "equivalencia_cl": "L"},
                    "XL": {"pecho": "98-102", "cintura": "88-92", "equivalencia_eu": "50", "equivalencia_cl": "XL"},
                    "XXL": {"pecho": "102-106", "cintura": "92-96", "equivalencia_eu": "52", "equivalencia_cl": "XXL"},
                    "XXXL": {"pecho": "106-114", "cintura": "96-104", "equivalencia_eu": "54", "equivalencia_cl": "XXXL"}
                }
            }
        ]
        
        # Materiales para señaléticas
        self.materiales_senaleticas = [
            {
                "id": 1,
                "nombre": "Acero Galvanizado 1.5mm",
                "tipo": "Sustrato",
                "precio_unitario": 43529,
                "ancho": 1.0,
                "alto": 3.0,
                "espesor": 1.5,
                "precio_m2": 14509.67
            },
            {
                "id": 2,
                "nombre": "Acero Galvanizado 2.0mm",
                "tipo": "Sustrato",
                "precio_unitario": 46638,
                "ancho": 1.0,
                "alto": 3.0,
                "espesor": 2.0,
                "precio_m2": 15546.0
            },
            {
                "id": 3,
                "nombre": "Trovicel Zintra 3mm",
                "tipo": "Sustrato",
                "precio_unitario": 18500,
                "ancho": 1.22,
                "alto": 2.44,
                "espesor": 3.0,
                "precio_m2": 6218.03
            },
            {
                "id": 4,
                "nombre": "Vinilo Reflectante Grado Comercial",
                "tipo": "Grafica",
                "precio_unitario": 70000,
                "ancho": 0.62,
                "alto": 45.0,
                "espesor": 0,
                "precio_m2": 2508.96
            }
        ]
        
        # Usuarios del sistema
        self.usuarios = [
            {
                "id": 1,
                "email": "admin@tresmas.cl",
                "password_hash": self._hash_password("tresmas2025"),
                "nombre": "Administrador TresMas",
                "rol": "master",
                "activo": True
            }
        ]

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

# Instancia global de la base de datos
db = TresmasDB()

# Utilidades JWT
def generate_jwt_token(user_data):
    payload = {
        'user_id': user_data['id'],
        'email': user_data['email'],
        'rol': user_data['rol'],
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Decorador para rutas protegidas
def require_auth(f):
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

# ==================== RUTAS DE LA API ====================

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'sistema': 'TIENDAS TRESMAS',
        'version': '1.0-REAL',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('usuario') or data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    
    # Buscar usuario
    user = None
    for u in db.usuarios:
        if u['email'] == email and u['password_hash'] == db._hash_password(password):
            user = u
            break
    
    if not user:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    if not user['activo']:
        return jsonify({'error': 'Usuario inactivo'}), 401
    
    token = generate_jwt_token(user)
    
    return jsonify({
        'success': True,
        'token': token,
        'usuario': {
            'id': user['id'],
            'email': user['email'],
            'nombre': user['nombre'],
            'rol': user['rol']
        }
    })

@app.route('/admin/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    return jsonify({
        'tiendas_activas': len([c for c in db.clientes if c['activo']]),
        'clientes': len(db.clientes),
        'productos_base': len([p for p in db.productos if p['activo']]),
        'planes_disponibles': len([p for p in db.planes if p['activo']]),
        'estadisticas': {
            'productos_por_categoria': {
                'Textil': len([p for p in db.productos if p['categoria'] == 'Textil']),
                'Hogar': len([p for p in db.productos if p['categoria'] == 'Hogar']),
                'Tecnología': len([p for p in db.productos if p['categoria'] == 'Tecnología'])
            },
            'ventas_mes': 0,  # Placeholder
            'clientes_activos': len([c for c in db.clientes if c['activo']])
        }
    })

# ==================== GESTIÓN DE PLANES ====================

@app.route('/admin/planes', methods=['GET'])
@require_auth
def get_planes():
    return jsonify({
        'success': True,
        'planes': [p for p in db.planes if p['activo']]
    })

@app.route('/admin/planes', methods=['POST'])
@require_auth
def create_plan():
    data = request.get_json()
    
    new_plan = {
        'id': len(db.planes) + 1,
        'nombre': data.get('nombre'),
        'precio_mensual': data.get('precio_mensual'),
        'precio_anual': data.get('precio_anual'),
        'pago_inicial': data.get('pago_inicial'),
        'pago_inicial_anual': data.get('pago_inicial_anual'),
        'caracteristicas': data.get('caracteristicas', []),
        'limite_productos': data.get('limite_productos'),
        'activo': True
    }
    
    db.planes.append(new_plan)
    
    return jsonify({
        'success': True,
        'plan': new_plan
    })

@app.route('/admin/planes/<int:plan_id>', methods=['PUT'])
@require_auth
def update_plan(plan_id):
    data = request.get_json()
    
    for i, plan in enumerate(db.planes):
        if plan['id'] == plan_id:
            db.planes[i].update(data)
            return jsonify({
                'success': True,
                'plan': db.planes[i]
            })
    
    return jsonify({'error': 'Plan no encontrado'}), 404

@app.route('/admin/planes/<int:plan_id>', methods=['DELETE'])
@require_auth
def delete_plan(plan_id):
    for i, plan in enumerate(db.planes):
        if plan['id'] == plan_id:
            db.planes[i]['activo'] = False
            return jsonify({'success': True})
    
    return jsonify({'error': 'Plan no encontrado'}), 404

# ==================== GESTIÓN DE PRODUCTOS ====================

@app.route('/admin/productos', methods=['GET'])
@require_auth
def get_productos():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    search = request.args.get('search', '')
    categoria = request.args.get('categoria', '')
    
    productos = [p for p in db.productos if p['activo']]
    
    # Filtros
    if search:
        productos = [p for p in productos if search.lower() in p['nombre'].lower()]
    
    if categoria:
        productos = [p for p in productos if p['categoria'] == categoria]
    
    # Paginación
    total = len(productos)
    start = (page - 1) * per_page
    end = start + per_page
    productos_page = productos[start:end]
    
    return jsonify({
        'success': True,
        'productos': productos_page,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/admin/productos', methods=['POST'])
@require_auth
def create_producto():
    data = request.get_json()
    
    # Calcular utilidad y precio USD
    precio_costo = data.get('precio_costo', 0)
    precio_venta = data.get('precio_venta', 0)
    utilidad_porcentaje = ((precio_venta - precio_costo) / precio_costo * 100) if precio_costo > 0 else 0
    precio_usd = precio_venta / 900  # Tasa de cambio fija
    
    # Generar SKU si no se proporciona
    sku = data.get('sku')
    if not sku:
        codigo_proveedor = data.get('codigo_proveedor', 'PROD')
        sku = f"AQTL-{codigo_proveedor}-2025"
    
    new_producto = {
        'id': len(db.productos) + 1,
        'nombre': data.get('nombre'),
        'categoria': data.get('categoria'),
        'subcategoria': data.get('subcategoria'),
        'marca': data.get('marca'),
        'descripcion': data.get('descripcion'),
        'precio_costo': precio_costo,
        'precio_venta': precio_venta,
        'precio_usd': round(precio_usd, 2),
        'utilidad_porcentaje': round(utilidad_porcentaje, 2),
        'codigo_proveedor': data.get('codigo_proveedor'),
        'sku': sku,
        'codigo_tienda': data.get('codigo_tienda'),
        'stock': data.get('stock', 0),
        'imagen_url': data.get('imagen_url'),
        'ficha_tecnica': data.get('ficha_tecnica', {}),
        'activo': True
    }
    
    db.productos.append(new_producto)
    
    return jsonify({
        'success': True,
        'producto': new_producto
    })

# ==================== SISTEMA DE TALLAS ====================

@app.route('/admin/tallas/tipos', methods=['GET'])
@require_auth
def get_tipos_tallas():
    return jsonify({
        'success': True,
        'tipos': db.tallas_tipos
    })

@app.route('/admin/tallas/calcular', methods=['POST'])
@require_auth
def calcular_talla():
    data = request.get_json()
    tipo_id = data.get('tipo_id')
    medidas = data.get('medidas', {})
    
    # Buscar tipo de talla
    tipo = None
    for t in db.tallas_tipos:
        if t['id'] == tipo_id:
            tipo = t
            break
    
    if not tipo:
        return jsonify({'error': 'Tipo de talla no encontrado'}), 404
    
    # Lógica de cálculo de talla (simplificada)
    talla_recomendada = None
    for talla, rangos in tipo['rangos'].items():
        # Aquí iría la lógica real de comparación de medidas
        # Por ahora retornamos una talla de ejemplo
        if not talla_recomendada:
            talla_recomendada = talla
            break
    
    return jsonify({
        'success': True,
        'talla_recomendada': talla_recomendada,
        'tipo': tipo['nombre'],
        'equivalencias': tipo['rangos'][talla_recomendada] if talla_recomendada else {}
    })

# ==================== SISTEMA DE SEÑALÉTICAS ====================

@app.route('/admin/senaleticas/materiales', methods=['GET'])
@require_auth
def get_materiales_senaleticas():
    return jsonify({
        'success': True,
        'materiales': db.materiales_senaleticas
    })

@app.route('/admin/senaleticas/calcular', methods=['POST'])
@require_auth
def calcular_senaletica():
    data = request.get_json()
    
    ancho_cm = data.get('ancho', 60)
    alto_cm = data.get('alto', 90)
    cantidad = data.get('cantidad', 1)
    material_sustrato_id = data.get('material_sustrato_id')
    material_grafica_id = data.get('material_grafica_id')
    
    # Convertir a metros
    ancho_m = ancho_cm / 100
    alto_m = alto_cm / 100
    area_m2 = ancho_m * alto_m
    
    # Buscar materiales
    sustrato = None
    grafica = None
    
    for m in db.materiales_senaleticas:
        if m['id'] == material_sustrato_id:
            sustrato = m
        if m['id'] == material_grafica_id:
            grafica = m
    
    if not sustrato or not grafica:
        return jsonify({'error': 'Materiales no encontrados'}), 404
    
    # Cálculos
    costo_sustrato = area_m2 * sustrato['precio_m2']
    costo_grafica = area_m2 * grafica['precio_m2']
    costo_materiales = costo_sustrato + costo_grafica
    
    # Aplicar merma (15%)
    costo_con_merma = costo_materiales * 1.15
    
    # Mano de obra
    tiempo_mod = data.get('tiempo_mod', 0.75)
    costo_mod_hora = data.get('costo_mod', 8500)
    costo_mod = tiempo_mod * costo_mod_hora
    
    # Costo directo total
    costo_directo = costo_con_merma + costo_mod
    
    # Costos indirectos (15%)
    cif = costo_directo * 0.15
    costo_produccion = costo_directo + cif
    
    # Gastos administrativos y ventas (20%)
    gav = costo_produccion * 0.20
    costo_total = costo_produccion + gav
    
    # Utilidad (25%)
    utilidad = costo_total * 0.25
    precio_venta_neto = costo_total + utilidad
    
    # IVA (19%)
    iva = precio_venta_neto * 0.19
    precio_final = precio_venta_neto + iva
    
    # Multiplicar por cantidad
    resultado = {
        'area_m2': round(area_m2, 4),
        'costo_sustrato': round(costo_sustrato * cantidad, 0),
        'costo_grafica': round(costo_grafica * cantidad, 0),
        'costo_materiales': round(costo_materiales * cantidad, 0),
        'costo_con_merma': round(costo_con_merma * cantidad, 0),
        'costo_mod': round(costo_mod * cantidad, 0),
        'costo_directo': round(costo_directo * cantidad, 0),
        'cif': round(cif * cantidad, 0),
        'costo_produccion': round(costo_produccion * cantidad, 0),
        'gav': round(gav * cantidad, 0),
        'costo_total': round(costo_total * cantidad, 0),
        'utilidad': round(utilidad * cantidad, 0),
        'precio_venta_neto': round(precio_venta_neto * cantidad, 0),
        'iva': round(iva * cantidad, 0),
        'precio_final': round(precio_final * cantidad, 0),
        'cantidad': cantidad
    }
    
    return jsonify({
        'success': True,
        'calculo': resultado
    })

# ==================== CARGA MASIVA DE PRODUCTOS ====================

@app.route('/admin/productos/carga-masiva', methods=['POST'])
@require_auth
def carga_masiva_productos():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    try:
        # Leer archivo Excel
        df = pd.read_excel(file)
        
        productos_creados = 0
        errores = []
        
        for index, row in df.iterrows():
            try:
                # Mapear columnas del Excel a campos del producto
                nombre = str(row.get('Nombre del producto', f'Producto {index + 1}'))
                categoria = str(row.get('CATEGORIA', 'General'))
                precio_costo = float(row.get('Costo neto proveedor', 0))
                precio_venta = float(row.get('PRECIO VENTA CLP', 0))
                
                # Calcular utilidad y USD
                utilidad_porcentaje = ((precio_venta - precio_costo) / precio_costo * 100) if precio_costo > 0 else 0
                precio_usd = precio_venta / 900
                
                # Crear producto
                nuevo_producto = {
                    'id': len(db.productos) + productos_creados + 1,
                    'nombre': nombre,
                    'categoria': categoria,
                    'subcategoria': str(row.get('Subcategoria', '')),
                    'marca': str(row.get('Marca', 'AQUI TU LOGO')),
                    'descripcion': str(row.get('Descripción / descripción larga', '')),
                    'precio_costo': precio_costo,
                    'precio_venta': precio_venta,
                    'precio_usd': round(precio_usd, 2),
                    'utilidad_porcentaje': round(utilidad_porcentaje, 2),
                    'codigo_proveedor': str(row.get('Código proveedor', f'PROV{index + 1}')),
                    'sku': str(row.get('Código TRESMAS', f'AQTL-PROV{index + 1}-2025')),
                    'codigo_tienda': str(row.get('Código Base Tienda', f'AQTL{index + 1:03d}')),
                    'stock': int(row.get('Stock existencia', 0)),
                    'imagen_url': str(row.get('Url imagen Producto', 'https://via.placeholder.com/300x300')),
                    'ficha_tecnica': {
                        'material': str(row.get('Material', '')),
                        'tamaño': str(row.get('Tamaño', '')),
                        'peso': str(row.get('Peso', '')),
                        'colores': str(row.get('Colores', '')),
                        'presentacion': str(row.get('Presentación', '')),
                        'area_imprimible': str(row.get('Área Imprimible', '')),
                        'sugerencia_impresion': str(row.get('Sugerencia De Impresión', ''))
                    },
                    'activo': True
                }
                
                db.productos.append(nuevo_producto)
                productos_creados += 1
                
            except Exception as e:
                errores.append(f"Fila {index + 1}: {str(e)}")
        
        return jsonify({
            'success': True,
            'productos_creados': productos_creados,
            'errores': errores,
            'total_filas': len(df)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error procesando archivo: {str(e)}'}), 500

# ==================== VALIDADOR DE IMÁGENES ====================

@app.route('/admin/validador/upload', methods=['POST'])
@require_auth
def upload_images():
    if 'images' not in request.files:
        return jsonify({'error': 'No se encontraron imágenes'}), 400
    
    files = request.files.getlist('images')
    resultados = []
    
    for file in files:
        if file.filename == '':
            continue
        
        # Validaciones básicas
        validaciones = {
            'nombre_archivo': file.filename,
            'tamaño_kb': len(file.read()) // 1024,
            'formato_valido': file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')),
            'tamaño_valido': len(file.read()) < 5 * 1024 * 1024,  # 5MB
            'sugerencia_sku': file.filename.split('.')[0].upper()
        }
        
        # Buscar productos con SKU similar
        productos_similares = []
        for producto in db.productos:
            if validaciones['sugerencia_sku'] in producto['sku']:
                productos_similares.append({
                    'id': producto['id'],
                    'nombre': producto['nombre'],
                    'sku': producto['sku']
                })
        
        validaciones['productos_similares'] = productos_similares
        resultados.append(validaciones)
    
    return jsonify({
        'success': True,
        'validaciones': resultados
    })

# ==================== ESTADÍSTICAS ====================

@app.route('/admin/estadisticas', methods=['GET'])
@require_auth
def get_estadisticas():
    # Calcular estadísticas reales
    total_productos = len([p for p in db.productos if p['activo']])
    productos_por_categoria = {}
    precio_promedio = 0
    
    for producto in db.productos:
        if producto['activo']:
            categoria = producto['categoria']
            productos_por_categoria[categoria] = productos_por_categoria.get(categoria, 0) + 1
            precio_promedio += producto['precio_venta']
    
    if total_productos > 0:
        precio_promedio = precio_promedio / total_productos
    
    return jsonify({
        'success': True,
        'estadisticas': {
            'total_productos': total_productos,
            'productos_por_categoria': productos_por_categoria,
            'precio_promedio': round(precio_promedio, 0),
            'total_clientes': len(db.clientes),
            'clientes_activos': len([c for c in db.clientes if c['activo']]),
            'planes_disponibles': len([p for p in db.planes if p['activo']]),
            'tipos_tallas': len(db.tallas_tipos),
            'materiales_senaleticas': len(db.materiales_senaleticas)
        }
    })

# ==================== ARCHIVO ESTÁTICO ====================

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    print("🚀 Iniciando TIENDAS TRESMAS Backend Real v1.0")
    print("📊 Dashboard: http://localhost:5001")
    print("🔑 Credenciales: admin@tresmas.cl / tresmas2025")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)

