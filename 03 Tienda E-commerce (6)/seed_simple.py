#!/usr/bin/env python3
"""
Script simplificado para poblar datos de demostración
"""

import mysql.connector
import hashlib

def connect_db():
    return mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='root_pass_2024',
        database='ecommerce_dev'
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def populate_data():
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Categorías
        categories = [
            (1, 'Electrónicos', 'Dispositivos electrónicos y tecnología', 'electronics.jpg', True, None),
            (2, 'Smartphones', 'Teléfonos inteligentes', 'smartphones.jpg', True, 1),
            (3, 'Laptops', 'Computadoras portátiles', 'laptops.jpg', True, 1),
            (4, 'Ropa', 'Vestimenta y accesorios', 'fashion.jpg', True, None),
        ]
        
        for cat in categories:
            cursor.execute("""
                INSERT INTO categories (id, name, description, image_url, is_active, parent_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name)
            """, cat)
        
        # Marcas
        brands = [
            (1, 'Apple', 'Tecnología innovadora', 'apple-logo.png', True),
            (2, 'Samsung', 'Electrónicos de calidad', 'samsung-logo.png', True),
            (3, 'Nike', 'Ropa deportiva', 'nike-logo.png', True),
        ]
        
        for brand in brands:
            cursor.execute("""
                INSERT INTO brands (id, name, description, logo_url, is_active)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name)
            """, brand)
        
        # Productos
        products = [
            (1, 'iPhone 15 Pro', 'El iPhone más avanzado', 1299990, 1199990, 2, 1, 'iphone-15-pro.jpg', True, 4.8, 150),
            (2, 'Samsung Galaxy S24', 'Smartphone premium', 1099990, 999990, 2, 2, 'galaxy-s24.jpg', True, 4.7, 120),
            (3, 'MacBook Pro 16"', 'Laptop profesional', 2999990, 2799990, 3, 1, 'macbook-pro-16.jpg', True, 4.9, 80),
            (4, 'Camiseta Nike', 'Camiseta deportiva', 29990, 24990, 4, 3, 'nike-tee.jpg', True, 4.3, 500),
        ]
        
        for product in products:
            cursor.execute("""
                INSERT INTO products (id, name, description, price, sale_price, category_id, brand_id, image_url, is_active, rating, stock_quantity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name)
            """, product)
        
        # Usuarios
        users = [
            (1, 'admin@ecommerce.com', hash_password('admin123'), 'Admin', 'Sistema', '+56912345678', 'admin', True, True),
            (2, 'juan.perez@email.com', hash_password('user123'), 'Juan', 'Pérez', '+56987654321', 'customer', True, True),
            (3, 'maria.gonzalez@email.com', hash_password('user123'), 'María', 'González', '+56976543210', 'customer', True, True),
        ]
        
        for user in users:
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, first_name, last_name, phone, role, is_active, email_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE email = VALUES(email)
            """, user)
        
        # Direcciones
        cursor.execute("""
            INSERT INTO user_addresses (user_id, type, first_name, last_name, address_line_1, city, state, postal_code, country, phone, is_default)
            VALUES (2, 'home', 'Juan', 'Pérez', 'Av. Providencia 1234', 'Santiago', 'RM', '7500000', 'Chile', '+56987654321', TRUE)
            ON DUPLICATE KEY UPDATE first_name = VALUES(first_name)
        """)
        
        cursor.execute("""
            INSERT INTO user_addresses (user_id, type, first_name, last_name, address_line_1, city, state, postal_code, country, phone, is_default)
            VALUES (3, 'home', 'María', 'González', 'Calle Las Condes 5678', 'Santiago', 'RM', '7550000', 'Chile', '+56976543210', TRUE)
            ON DUPLICATE KEY UPDATE first_name = VALUES(first_name)
        """)
        
        # Órdenes
        cursor.execute("""
            INSERT INTO orders (id, user_id, subtotal, discount_amount, shipping_cost, total_amount, status, payment_method, shipping_address)
            VALUES (1, 2, 1199990, 0, 5990, 1205980, 'delivered', 'stripe', 'Av. Providencia 1234, Santiago')
            ON DUPLICATE KEY UPDATE status = VALUES(status)
        """)
        
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
            VALUES (1, 1, 1, 1199990, 1199990)
            ON DUPLICATE KEY UPDATE quantity = VALUES(quantity)
        """)
        
        # Reseñas
        cursor.execute("""
            INSERT INTO product_reviews (product_id, user_id, rating, title, comment, is_verified)
            VALUES (1, 2, 5, 'Excelente producto', 'El iPhone 15 Pro es increíble, la cámara es espectacular.', TRUE)
            ON DUPLICATE KEY UPDATE rating = VALUES(rating)
        """)
        
        conn.commit()
        print("✅ Datos de demostración poblados exitosamente")
        
        print("\n👥 Usuarios de prueba:")
        print("- Admin: admin@ecommerce.com / admin123")
        print("- Cliente: juan.perez@email.com / user123")
        print("- Cliente: maria.gonzalez@email.com / user123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    populate_data()

