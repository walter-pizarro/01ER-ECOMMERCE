#!/usr/bin/env python3
"""
Backend Completo para Panel Administrativo
eCommerce Moderno - Sistema de Gestión Completo
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import json
import jwt
import hashlib
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app, origins="*")

# Configuración
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root_pass_2024',
    'database': 'ecommerce_dev'
}

JWT_SECRET = 'ecommerce_admin_secret_key_2024'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Crear directorio de uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None

def verify_admin_token(token):
    """Verificar token de administrador"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload.get('user_id') if payload.get('role') == 'admin' else None
    except:
        return None

def allowed_file(filename):
    """Verificar si el archivo es permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== AUTENTICACIÓN ====================

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Login de administrador"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Verificar credenciales de admin
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("""
            SELECT id, email, role FROM users 
            WHERE email = %s AND password_hash = %s AND role = 'admin'
        """, (email, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # Generar token JWT
            token = jwt.encode({
                'user_id': user['id'],
                'email': user['email'],
                'role': user['role'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, JWT_SECRET, algorithm='HS256')
            
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'role': user['role']
                }
            })
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Error en login: {str(e)}'}), 500
    finally:
        conn.close()

# ==================== GESTIÓN DE CATEGORÍAS ====================

@app.route('/admin/categories', methods=['GET'])
def get_categories():
    """Obtener todas las categorías"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, COUNT(p.id) as product_count
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            GROUP BY c.id
            ORDER BY c.name
        """)
        categories = cursor.fetchall()
        
        return jsonify({'success': True, 'categories': categories})
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo categorías: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/categories', methods=['POST'])
def create_category():
    """Crear nueva categoría"""
    # Verificar token de admin
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'error': 'Nombre de categoría requerido'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO categories (name, description, created_at)
            VALUES (%s, %s, %s)
        """, (name, description, datetime.now()))
        
        conn.commit()
        category_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Categoría creada exitosamente',
            'category_id': category_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Error creando categoría: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Actualizar categoría"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'error': 'Nombre de categoría requerido'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE categories 
            SET name = %s, description = %s, updated_at = %s
            WHERE id = %s
        """, (name, description, datetime.now(), category_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Categoría actualizada'})
        else:
            return jsonify({'error': 'Categoría no encontrada'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error actualizando categoría: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Eliminar categoría"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verificar si hay productos en esta categoría
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE category_id = %s", (category_id,))
        result = cursor.fetchone()
        
        if result[0] > 0:
            return jsonify({'error': 'No se puede eliminar categoría con productos'}), 400
        
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Categoría eliminada'})
        else:
            return jsonify({'error': 'Categoría no encontrada'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error eliminando categoría: {str(e)}'}), 500
    finally:
        conn.close()

# ==================== GESTIÓN DE PRODUCTOS ====================

@app.route('/admin/products', methods=['GET'])
def get_admin_products():
    """Obtener productos para administración"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
        """)
        products = cursor.fetchall()
        
        return jsonify({'success': True, 'products': products})
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo productos: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/products', methods=['POST'])
def create_product():
    """Crear nuevo producto"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['name', 'price', 'category_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} requerido'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (
                name, description, price, original_price, category_id, 
                stock, image_url, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['name'],
            data.get('description', ''),
            data['price'],
            data.get('original_price', data['price']),
            data['category_id'],
            data.get('stock', 0),
            data.get('image_url', ''),
            data.get('status', 'active'),
            datetime.now()
        ))
        
        conn.commit()
        product_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Producto creado exitosamente',
            'product_id': product_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Error creando producto: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Actualizar producto"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        update_fields = []
        values = []
        
        allowed_fields = ['name', 'description', 'price', 'original_price', 'category_id', 'stock', 'image_url', 'status']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No hay campos para actualizar'}), 400
        
        update_fields.append("updated_at = %s")
        values.append(datetime.now())
        values.append(product_id)
        
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, values)
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Producto actualizado'})
        else:
            return jsonify({'error': 'Producto no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error actualizando producto: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Eliminar producto"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Producto eliminado'})
        else:
            return jsonify({'error': 'Producto no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error eliminando producto: {str(e)}'}), 500
    finally:
        conn.close()

# ==================== GESTIÓN DE ÓRDENES ====================

@app.route('/admin/orders', methods=['GET'])
def get_admin_orders():
    """Obtener órdenes para administración"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.*, u.email as customer_email, u.name as customer_name
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
        """)
        orders = cursor.fetchall()
        
        # Obtener items de cada orden
        for order in orders:
            cursor.execute("""
                SELECT oi.*, p.name as product_name
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """, (order['id'],))
            order['items'] = cursor.fetchall()
        
        return jsonify({'success': True, 'orders': orders})
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo órdenes: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Actualizar estado de orden"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({'error': 'Estado requerido'}), 400
    
    valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if status not in valid_statuses:
        return jsonify({'error': 'Estado inválido'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders 
            SET status = %s, updated_at = %s
            WHERE id = %s
        """, (status, datetime.now(), order_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Estado actualizado'})
        else:
            return jsonify({'error': 'Orden no encontrada'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error actualizando estado: {str(e)}'}), 500
    finally:
        conn.close()

# ==================== CONFIGURACIÓN DE MEDIOS DE PAGO ====================

@app.route('/admin/payment-methods', methods=['GET'])
def get_payment_methods():
    """Obtener métodos de pago configurados"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM payment_methods ORDER BY name")
        methods = cursor.fetchall()
        
        return jsonify({'success': True, 'payment_methods': methods})
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo métodos de pago: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/payment-methods', methods=['POST'])
def create_payment_method():
    """Crear método de pago"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    data = request.get_json()
    
    required_fields = ['name', 'type']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} requerido'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payment_methods (
                name, type, config, is_active, created_at
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            data['name'],
            data['type'],
            json.dumps(data.get('config', {})),
            data.get('is_active', True),
            datetime.now()
        ))
        
        conn.commit()
        method_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Método de pago creado',
            'method_id': method_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Error creando método de pago: {str(e)}'}), 500
    finally:
        conn.close()

# ==================== CONFIGURACIÓN DE TIENDA ====================

@app.route('/admin/store-config', methods=['GET'])
def get_store_config():
    """Obtener configuración de tienda"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM store_config")
        config = cursor.fetchall()
        
        # Convertir a diccionario
        config_dict = {}
        for item in config:
            config_dict[item['key']] = item['value']
        
        return jsonify({'success': True, 'config': config_dict})
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo configuración: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/store-config', methods=['PUT'])
def update_store_config():
    """Actualizar configuración de tienda"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor()
        
        for key, value in data.items():
            cursor.execute("""
                INSERT INTO store_config (key, value, updated_at)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE value = %s, updated_at = %s
            """, (key, value, datetime.now(), value, datetime.now()))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Configuración actualizada'})
        
    except Exception as e:
        return jsonify({'error': f'Error actualizando configuración: {str(e)}'}), 500
    finally:
        conn.close()

# ==================== DASHBOARD Y ESTADÍSTICAS ====================

@app.route('/admin/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Obtener estadísticas del dashboard"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión a BD'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Estadísticas generales
        stats = {}
        
        # Total de productos
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE status = 'active'")
        stats['total_products'] = cursor.fetchone()['count']
        
        # Total de órdenes
        cursor.execute("SELECT COUNT(*) as count FROM orders")
        stats['total_orders'] = cursor.fetchone()['count']
        
        # Total de clientes
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'customer'")
        stats['total_customers'] = cursor.fetchone()['count']
        
        # Ventas totales
        cursor.execute("SELECT COALESCE(SUM(total), 0) as total FROM orders WHERE status != 'cancelled'")
        stats['total_sales'] = cursor.fetchone()['total']
        
        # Productos más vendidos
        cursor.execute("""
            SELECT p.name, SUM(oi.quantity) as sold
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status != 'cancelled'
            GROUP BY p.id, p.name
            ORDER BY sold DESC
            LIMIT 5
        """)
        stats['top_products'] = cursor.fetchall()
        
        # Órdenes recientes
        cursor.execute("""
            SELECT o.*, u.email as customer_email
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
            LIMIT 10
        """)
        stats['recent_orders'] = cursor.fetchall()
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo estadísticas: {str(e)}'}), 500
    finally:
        conn.close()

# ==================== UPLOAD DE ARCHIVOS ====================

@app.route('/admin/upload', methods=['POST'])
def upload_file():
    """Subir archivo (imágenes de productos)"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_admin_token(token):
        return jsonify({'error': 'Token de admin inválido'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    if file and allowed_file(file.filename):
        # Generar nombre único
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/uploads/{filename}'
        })
    
    return jsonify({'error': 'Tipo de archivo no permitido'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir archivos subidos"""
    return send_from_directory(UPLOAD_FOLDER, filename)

# ==================== HEALTH CHECK ====================

@app.route('/admin/health', methods=['GET'])
def admin_health():
    """Health check del sistema administrativo"""
    return jsonify({
        'status': 'ok',
        'service': 'eCommerce Admin API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando Backend Administrativo Completo...")
    print("📊 Funcionalidades disponibles:")
    print("   - Gestión de Categorías")
    print("   - Gestión de Productos (CRUD completo)")
    print("   - Gestión de Órdenes")
    print("   - Configuración de Medios de Pago")
    print("   - Configuración de Tienda")
    print("   - Dashboard con Estadísticas")
    print("   - Upload de Imágenes")
    print("🌐 Servidor corriendo en: http://0.0.0.0:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True)

