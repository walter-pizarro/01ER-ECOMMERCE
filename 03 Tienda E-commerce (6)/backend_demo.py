#!/usr/bin/env python3
"""
Backend API simplificado para demostración del eCommerce
"""

from flask import Flask, jsonify, request, session
from flask_cors import CORS
import mysql.connector
import hashlib
import jwt
import datetime
import os

app = Flask(__name__)
app.secret_key = 'dev_secret_key_2024'
CORS(app, origins=['*'])

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root_pass_2024',
    'database': 'ecommerce_dev'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id, email):
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, app.secret_key, algorithm='HS256')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'service': 'eCommerce Backend API'
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña requeridos'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, email, password_hash, first_name, last_name, role, is_active
            FROM users WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or not user['is_active']:
            return jsonify({'error': 'Usuario no encontrado o inactivo'}), 401
        
        if user['password_hash'] != hash_password(password):
            return jsonify({'error': 'Contraseña incorrecta'}), 401
        
        token = generate_token(user['id'], user['email'])
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Parámetros de consulta
        category_id = request.args.get('category_id')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        offset = (page - 1) * per_page
        
        # Construir consulta
        where_conditions = ['p.is_active = TRUE']
        params = []
        
        if category_id:
            where_conditions.append('p.category_id = %s')
            params.append(category_id)
        
        if search:
            where_conditions.append('(p.name LIKE %s OR p.description LIKE %s)')
            params.extend([f'%{search}%', f'%{search}%'])
        
        where_clause = ' AND '.join(where_conditions)
        
        # Consulta principal
        query = f"""
            SELECT 
                p.id, p.name, p.description, p.price, p.sale_price,
                p.image_url, p.rating, p.review_count, p.stock_quantity,
                c.name as category_name,
                b.name as brand_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN brands b ON p.brand_id = b.id
            WHERE {where_clause}
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([per_page, offset])
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        # Contar total
        count_query = f"""
            SELECT COUNT(*) as total
            FROM products p
            WHERE {where_clause}
        """
        cursor.execute(count_query, params[:-2])  # Excluir LIMIT y OFFSET
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'products': products,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                p.id, p.name, p.description, p.price, p.sale_price,
                p.image_url, p.rating, p.review_count, p.stock_quantity,
                p.weight, p.dimensions,
                c.name as category_name,
                b.name as brand_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN brands b ON p.brand_id = b.id
            WHERE p.id = %s AND p.is_active = TRUE
        """, (product_id,))
        
        product = cursor.fetchone()
        
        if not product:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Obtener reseñas
        cursor.execute("""
            SELECT 
                r.id, r.rating, r.title, r.comment, r.created_at,
                u.first_name, u.last_name
            FROM product_reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.product_id = %s AND r.is_approved = TRUE
            ORDER BY r.created_at DESC
            LIMIT 10
        """, (product_id,))
        
        reviews = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        product['reviews'] = reviews
        
        return jsonify(product)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, name, description, image_url, parent_id
            FROM categories
            WHERE is_active = TRUE
            ORDER BY parent_id, name
        """)
        
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'categories': categories})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart', methods=['GET'])
def get_cart():
    try:
        # Simulación de carrito (en producción usaríamos sesiones/JWT)
        return jsonify({
            'items': [],
            'total': 0,
            'count': 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Verificar que el producto existe
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, name, price, sale_price, stock_quantity
            FROM products
            WHERE id = %s AND is_active = TRUE
        """, (product_id,))
        
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not product:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        if product['stock_quantity'] < quantity:
            return jsonify({'error': 'Stock insuficiente'}), 400
        
        return jsonify({
            'message': 'Producto agregado al carrito',
            'product': product,
            'quantity': quantity
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        # Simulación de órdenes del usuario
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                o.id, o.order_number, o.status, o.total_amount,
                o.created_at, o.shipped_at, o.delivered_at
            FROM orders o
            ORDER BY o.created_at DESC
            LIMIT 10
        """)
        
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'orders': orders})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_products():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'products': []})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                p.id, p.name, p.price, p.sale_price, p.image_url, p.rating
            FROM products p
            WHERE p.is_active = TRUE 
            AND (p.name LIKE %s OR p.description LIKE %s)
            ORDER BY p.rating DESC, p.name
            LIMIT 10
        """, (f'%{query}%', f'%{query}%'))
        
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'products': products})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Estadísticas básicas
        cursor.execute("SELECT COUNT(*) as total FROM products WHERE is_active = TRUE")
        total_products = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'customer' AND is_active = TRUE")
        total_customers = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM orders")
        total_orders = cursor.fetchone()['total']
        
        cursor.execute("SELECT SUM(total_amount) as total FROM orders WHERE status = 'delivered'")
        total_revenue = cursor.fetchone()['total'] or 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_products': total_products,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando eCommerce Backend API...")
    print("📊 Endpoints disponibles:")
    print("  - GET  /health")
    print("  - POST /api/auth/login")
    print("  - GET  /api/products")
    print("  - GET  /api/products/<id>")
    print("  - GET  /api/categories")
    print("  - GET  /api/search")
    print("  - GET  /api/stats")
    print("  - GET  /api/cart")
    print("  - POST /api/cart/add")
    print("  - GET  /api/orders")
    print("\n✅ API lista en http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

