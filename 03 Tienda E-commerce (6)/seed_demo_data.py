#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de demostración
eCommerce Moderno - Vista Previa
"""

import mysql.connector
import json
import hashlib
import random
from datetime import datetime, timedelta
import os

class DatabaseSeeder:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='ecommerce_user',
                password='ecommerce_pass_2024',
                database='ecommerce_dev'
            )
            self.cursor = self.connection.cursor()
            print("✅ Conectado a la base de datos")
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            return False
        return True
    
    def hash_password(self, password):
        """Hash de contraseña simple para demo"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def seed_categories(self):
        """Poblar categorías"""
        categories = [
            (1, 'Electrónicos', 'Dispositivos electrónicos y tecnología', 'electronics.jpg', True, None),
            (2, 'Smartphones', 'Teléfonos inteligentes y accesorios', 'smartphones.jpg', True, 1),
            (3, 'Laptops', 'Computadoras portátiles y accesorios', 'laptops.jpg', True, 1),
            (4, 'Tablets', 'Tabletas y accesorios', 'tablets.jpg', True, 1),
            (5, 'Ropa y Moda', 'Vestimenta y accesorios de moda', 'fashion.jpg', True, None),
            (6, 'Hombre', 'Ropa para hombre', 'men-fashion.jpg', True, 5),
            (7, 'Mujer', 'Ropa para mujer', 'women-fashion.jpg', True, 5),
            (8, 'Hogar y Jardín', 'Artículos para el hogar y jardín', 'home-garden.jpg', True, None),
            (9, 'Muebles', 'Muebles para el hogar', 'furniture.jpg', True, 8),
            (10, 'Decoración', 'Artículos decorativos', 'decoration.jpg', True, 8),
        ]
        
        query = """
        INSERT INTO categories (id, name, description, image_url, is_active, parent_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        description = VALUES(description),
        image_url = VALUES(image_url),
        is_active = VALUES(is_active),
        parent_id = VALUES(parent_id)
        """
        
        self.cursor.executemany(query, categories)
        print("✅ Categorías pobladas")
    
    def seed_brands(self):
        """Poblar marcas"""
        brands = [
            (1, 'Apple', 'Tecnología innovadora', 'apple-logo.png', True),
            (2, 'Samsung', 'Electrónicos de calidad', 'samsung-logo.png', True),
            (3, 'Sony', 'Entretenimiento y tecnología', 'sony-logo.png', True),
            (4, 'Nike', 'Ropa deportiva', 'nike-logo.png', True),
            (5, 'Adidas', 'Ropa y calzado deportivo', 'adidas-logo.png', True),
            (6, 'Zara', 'Moda contemporánea', 'zara-logo.png', True),
            (7, 'IKEA', 'Muebles y decoración', 'ikea-logo.png', True),
            (8, 'Dell', 'Computadoras y tecnología', 'dell-logo.png', True),
            (9, 'HP', 'Tecnología e impresión', 'hp-logo.png', True),
            (10, 'Xiaomi', 'Tecnología accesible', 'xiaomi-logo.png', True),
        ]
        
        query = """
        INSERT INTO brands (id, name, description, logo_url, is_active)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        description = VALUES(description),
        logo_url = VALUES(logo_url),
        is_active = VALUES(is_active)
        """
        
        self.cursor.executemany(query, brands)
        print("✅ Marcas pobladas")
    
    def seed_products(self):
        """Poblar productos"""
        products = [
            # Smartphones
            (1, 'iPhone 15 Pro', 'El iPhone más avanzado con chip A17 Pro', 1299990, 1199990, 2, 1, 'iphone-15-pro.jpg', True, 4.8, 150),
            (2, 'Samsung Galaxy S24 Ultra', 'Smartphone premium con S Pen integrado', 1499990, 1399990, 2, 2, 'galaxy-s24-ultra.jpg', True, 4.7, 120),
            (3, 'Xiaomi 14 Pro', 'Flagship con cámara Leica', 899990, 799990, 2, 10, 'xiaomi-14-pro.jpg', True, 4.6, 200),
            
            # Laptops
            (4, 'MacBook Pro 16"', 'Laptop profesional con chip M3 Pro', 2999990, 2799990, 3, 1, 'macbook-pro-16.jpg', True, 4.9, 80),
            (5, 'Dell XPS 15', 'Laptop premium para creativos', 2199990, 1999990, 3, 8, 'dell-xps-15.jpg', True, 4.5, 60),
            (6, 'HP Spectre x360', 'Laptop convertible premium', 1899990, 1699990, 3, 9, 'hp-spectre-x360.jpg', True, 4.4, 90),
            
            # Tablets
            (7, 'iPad Pro 12.9"', 'Tablet profesional con chip M2', 1399990, 1299990, 4, 1, 'ipad-pro-12.jpg', True, 4.8, 100),
            (8, 'Samsung Galaxy Tab S9+', 'Tablet Android premium', 899990, 799990, 4, 2, 'galaxy-tab-s9.jpg', True, 4.6, 75),
            
            # Ropa Hombre
            (9, 'Camiseta Nike Dri-FIT', 'Camiseta deportiva transpirable', 29990, 24990, 6, 4, 'nike-dri-fit-tee.jpg', True, 4.3, 500),
            (10, 'Jeans Levi\'s 501', 'Jeans clásicos de mezclilla', 79990, 69990, 6, None, 'levis-501-jeans.jpg', True, 4.5, 300),
            
            # Ropa Mujer
            (11, 'Vestido Zara Floral', 'Vestido elegante con estampado floral', 59990, 49990, 7, 6, 'zara-floral-dress.jpg', True, 4.2, 150),
            (12, 'Blusa Adidas Originals', 'Blusa casual deportiva', 39990, 34990, 7, 5, 'adidas-originals-top.jpg', True, 4.4, 200),
            
            # Muebles
            (13, 'Sofá IKEA KIVIK', 'Sofá de 3 plazas cómodo y moderno', 399990, 349990, 9, 7, 'ikea-kivik-sofa.jpg', True, 4.6, 25),
            (14, 'Mesa de Centro IKEA LACK', 'Mesa de centro minimalista', 29990, 24990, 9, 7, 'ikea-lack-table.jpg', True, 4.1, 80),
            
            # Decoración
            (15, 'Lámpara de Mesa Moderna', 'Lámpara LED con diseño contemporáneo', 89990, 79990, 10, None, 'modern-table-lamp.jpg', True, 4.3, 120),
        ]
        
        query = """
        INSERT INTO products (id, name, description, price, sale_price, category_id, brand_id, image_url, is_active, rating, stock_quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        description = VALUES(description),
        price = VALUES(price),
        sale_price = VALUES(sale_price),
        category_id = VALUES(category_id),
        brand_id = VALUES(brand_id),
        image_url = VALUES(image_url),
        is_active = VALUES(is_active),
        rating = VALUES(rating),
        stock_quantity = VALUES(stock_quantity)
        """
        
        self.cursor.executemany(query, products)
        print("✅ Productos poblados")
    
    def seed_users(self):
        """Poblar usuarios de demostración"""
        users = [
            (1, 'admin@ecommerce.com', self.hash_password('admin123'), 'Administrador', 'Sistema', '+56912345678', 'admin', True, True),
            (2, 'juan.perez@email.com', self.hash_password('user123'), 'Juan', 'Pérez', '+56987654321', 'customer', True, True),
            (3, 'maria.gonzalez@email.com', self.hash_password('user123'), 'María', 'González', '+56976543210', 'customer', True, True),
            (4, 'carlos.rodriguez@email.com', self.hash_password('user123'), 'Carlos', 'Rodríguez', '+56965432109', 'customer', True, True),
            (5, 'ana.martinez@email.com', self.hash_password('user123'), 'Ana', 'Martínez', '+56954321098', 'customer', True, True),
        ]
        
        query = """
        INSERT INTO users (id, email, password_hash, first_name, last_name, phone, role, is_active, email_verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        email = VALUES(email),
        password_hash = VALUES(password_hash),
        first_name = VALUES(first_name),
        last_name = VALUES(last_name),
        phone = VALUES(phone),
        role = VALUES(role),
        is_active = VALUES(is_active),
        email_verified = VALUES(email_verified)
        """
        
        self.cursor.executemany(query, users)
        print("✅ Usuarios poblados")
    
    def seed_addresses(self):
        """Poblar direcciones de usuarios"""
        addresses = [
            (1, 2, 'home', 'Juan', 'Pérez', 'Av. Providencia 1234', '', 'Providencia', 'Santiago', 'RM', '7500000', 'Chile', '+56987654321', True),
            (2, 3, 'home', 'María', 'González', 'Calle Las Condes 5678', 'Depto 15', 'Las Condes', 'Santiago', 'RM', '7550000', 'Chile', '+56976543210', True),
            (3, 4, 'work', 'Carlos', 'Rodríguez', 'Av. Apoquindo 9012', 'Piso 8', 'Las Condes', 'Santiago', 'RM', '7560000', 'Chile', '+56965432109', False),
            (4, 5, 'home', 'Ana', 'Martínez', 'Calle Ñuñoa 3456', '', 'Ñuñoa', 'Santiago', 'RM', '7750000', 'Chile', '+56954321098', True),
        ]
        
        for address in addresses:
            query = """
            INSERT INTO user_addresses (id, user_id, type, first_name, last_name, address_line_1, address_line_2, city, state, postal_code, country, phone, is_default)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            type = VALUES(type),
            first_name = VALUES(first_name),
            last_name = VALUES(last_name)
            """
            self.cursor.execute(query, address)
        print("✅ Direcciones pobladas")
    
    def seed_orders(self):
        """Poblar órdenes de demostración"""
        # Crear algunas órdenes de ejemplo
        orders = [
            (1, 2, 1299990, 0, 5990, 1305980, 'pending', 'stripe', 'Av. Providencia 1234, Providencia, Santiago'),
            (2, 3, 899990, 0, 5990, 905980, 'shipped', 'paypal', 'Calle Las Condes 5678, Las Condes, Santiago'),
            (3, 4, 2999990, 0, 0, 2999990, 'delivered', 'stripe', 'Av. Apoquindo 9012, Las Condes, Santiago'),
            (4, 5, 89990, 10000, 5990, 85980, 'processing', 'mercadopago', 'Calle Ñuñoa 3456, Ñuñoa, Santiago'),
        ]
        
        query = """
        INSERT INTO orders (id, user_id, subtotal, discount_amount, shipping_cost, total_amount, status, payment_method, shipping_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        subtotal = VALUES(subtotal),
        discount_amount = VALUES(discount_amount),
        shipping_cost = VALUES(shipping_cost),
        total_amount = VALUES(total_amount),
        status = VALUES(status),
        payment_method = VALUES(payment_method),
        shipping_address = VALUES(shipping_address)
        """
        
        self.cursor.executemany(query, orders)
        print("✅ Órdenes pobladas")
    
    def seed_order_items(self):
        """Poblar items de órdenes"""
        order_items = [
            (1, 1, 1, 1, 1199990, 1199990),  # iPhone 15 Pro
            (2, 2, 3, 1, 799990, 799990),    # Xiaomi 14 Pro
            (3, 3, 4, 1, 2799990, 2799990),  # MacBook Pro
            (4, 4, 15, 1, 79990, 79990),     # Lámpara
        ]
        
        query = """
        INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, total_price)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        quantity = VALUES(quantity),
        unit_price = VALUES(unit_price),
        total_price = VALUES(total_price)
        """
        
        self.cursor.executemany(query, order_items)
        print("✅ Items de órdenes poblados")
    
    def seed_reviews(self):
        """Poblar reseñas de productos"""
        reviews = [
            (1, 1, 2, 5, 'Excelente producto', 'El iPhone 15 Pro es increíble, la cámara es espectacular y el rendimiento es excepcional.', True),
            (2, 2, 3, 4, 'Muy bueno', 'El Galaxy S24 Ultra tiene una pantalla hermosa y el S Pen es muy útil.', True),
            (3, 3, 4, 5, 'Perfecto para trabajo', 'El Xiaomi 14 Pro tiene una excelente relación calidad-precio.', True),
            (4, 4, 2, 5, 'Increíble laptop', 'El MacBook Pro es perfecto para edición de video y diseño.', True),
            (5, 7, 3, 4, 'Muy buena tablet', 'El iPad Pro es excelente para dibujar y trabajar.', True),
        ]
        
        query = """
        INSERT INTO product_reviews (id, product_id, user_id, rating, title, comment, is_verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        rating = VALUES(rating),
        title = VALUES(title),
        comment = VALUES(comment),
        is_verified = VALUES(is_verified)
        """
        
        self.cursor.executemany(query, reviews)
        print("✅ Reseñas pobladas")
    
    def run_seeding(self):
        """Ejecutar todo el proceso de poblado"""
        if not self.connect():
            return False
        
        try:
            print("🌱 Iniciando poblado de datos de demostración...")
            
            self.seed_categories()
            self.seed_brands()
            self.seed_products()
            self.seed_users()
            self.seed_addresses()
            self.seed_orders()
            self.seed_order_items()
            self.seed_reviews()
            
            self.connection.commit()
            print("✅ Todos los datos de demostración han sido poblados exitosamente")
            
        except Exception as e:
            print(f"❌ Error durante el poblado: {e}")
            self.connection.rollback()
            return False
        
        finally:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        
        return True

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    success = seeder.run_seeding()
    
    if success:
        print("\n🎉 Base de datos lista para demostración!")
        print("\n👥 Usuarios de prueba:")
        print("- Admin: admin@ecommerce.com / admin123")
        print("- Cliente: juan.perez@email.com / user123")
        print("- Cliente: maria.gonzalez@email.com / user123")
        print("\n🛍️ Productos disponibles: 15")
        print("📦 Órdenes de ejemplo: 4")
        print("⭐ Reseñas de ejemplo: 5")
    else:
        print("\n❌ Error poblando la base de datos")
        exit(1)

