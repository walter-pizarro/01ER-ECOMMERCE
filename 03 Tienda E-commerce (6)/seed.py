#!/usr/bin/env python3
"""
Sistema de seeders para eCommerce Modular
Puebla la base de datos con datos de prueba realistas
"""
import os
import sys
import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.database import get_database_url
from models import *
from models.orders import OrderStatus, PaymentStatus, PaymentMethod, ShippingStatus
from models.additional import CouponType, DiscountTarget

# Configurar Faker
fake = Faker(['es_ES', 'en_US'])
Faker.seed(42)  # Para resultados reproducibles

class DatabaseSeeder:
    """Generador de datos de prueba"""
    
    def __init__(self):
        self.database_url = get_database_url()
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def seed_all(self):
        """Ejecuta todos los seeders"""
        try:
            print("🌱 Iniciando seeders de datos de prueba...")
            
            # Verificar que las tablas existan
            self._verify_tables()
            
            # Ejecutar seeders en orden de dependencias
            self.seed_users_and_roles()
            self.seed_geographic_data()
            self.seed_catalog_data()
            self.seed_products()
            self.seed_orders_and_transactions()
            self.seed_reviews_and_ratings()
            self.seed_coupons()
            self.seed_analytics_data()
            
            self.session.commit()
            print("\n✅ Todos los seeders completados exitosamente!")
            
        except Exception as e:
            print(f"\n❌ Error en seeders: {e}")
            self.session.rollback()
            raise
        finally:
            self.session.close()
    
    def _verify_tables(self):
        """Verifica que las tablas necesarias existan"""
        required_tables = ['users', 'products', 'categories', 'orders']
        
        for table in required_tables:
            result = self.session.execute(text(
                f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES "
                f"WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table}'"
            ))
            if result.scalar() == 0:
                raise Exception(f"Tabla requerida '{table}' no existe. Ejecuta las migraciones primero.")
    
    def seed_users_and_roles(self):
        """Crea usuarios y asigna roles"""
        print("\n👥 Creando usuarios y roles...")
        
        # Obtener roles existentes
        admin_role = self.session.query(Role).filter_by(name='admin').first()
        customer_role = self.session.query(Role).filter_by(name='customer').first()
        
        if not admin_role or not customer_role:
            print("⚠️  Roles no encontrados. Asegúrate de que las migraciones se ejecutaron correctamente.")
            return
        
        # Crear usuario administrador
        admin_user = User(
            email='admin@ecommerce.local',
            password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PJ/...',  # password: admin123
            first_name='Admin',
            last_name='Sistema',
            phone='+1234567890',
            is_active=True,
            is_verified=True
        )
        self.session.add(admin_user)
        self.session.flush()
        
        # Asignar rol de admin
        admin_user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        self.session.add(admin_user_role)
        
        # Crear usuarios clientes
        customers = []
        for i in range(50):
            customer = User(
                email=fake.email(),
                password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PJ/...',  # password: customer123
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=fake.phone_number()[:20],
                is_active=True,
                is_verified=random.choice([True, False])
            )
            customers.append(customer)
            self.session.add(customer)
        
        self.session.flush()
        
        # Asignar rol de customer
        for customer in customers:
            customer_user_role = UserRole(user_id=customer.id, role_id=customer_role.id)
            self.session.add(customer_user_role)
        
        print(f"✓ Creados: 1 admin + {len(customers)} clientes")
    
    def seed_geographic_data(self):
        """Crea datos geográficos adicionales"""
        print("\n🌍 Creando datos geográficos...")
        
        # Obtener países existentes
        chile = self.session.query(Country).filter_by(code='CL').first()
        usa = self.session.query(Country).filter_by(code='US').first()
        
        if not chile or not usa:
            print("⚠️  Países no encontrados")
            return
        
        # Ciudades para Chile
        rm_state = self.session.query(State).filter_by(code='RM').first()
        if rm_state:
            chile_cities = [
                City(state_id=rm_state.id, name='Santiago', postal_code='8320000'),
                City(state_id=rm_state.id, name='Las Condes', postal_code='7550000'),
                City(state_id=rm_state.id, name='Providencia', postal_code='7500000'),
                City(state_id=rm_state.id, name='Ñuñoa', postal_code='7750000'),
            ]
            
            for city in chile_cities:
                self.session.add(city)
        
        # Estados para USA
        us_states = [
            State(country_id=usa.id, code='CA', name='California'),
            State(country_id=usa.id, code='NY', name='New York'),
            State(country_id=usa.id, code='TX', name='Texas'),
        ]
        
        for state in us_states:
            self.session.add(state)
        
        self.session.flush()
        
        # Ciudades para USA
        ca_state = self.session.query(State).filter_by(code='CA').first()
        if ca_state:
            us_cities = [
                City(state_id=ca_state.id, name='Los Angeles', postal_code='90210'),
                City(state_id=ca_state.id, name='San Francisco', postal_code='94102'),
            ]
            
            for city in us_cities:
                self.session.add(city)
        
        print("✓ Datos geográficos creados")
    
    def seed_catalog_data(self):
        """Crea categorías, marcas y atributos"""
        print("\n📦 Creando catálogo base...")
        
        # Categorías principales
        categories = [
            Category(name='Electrónicos', slug='electronicos', description='Dispositivos electrónicos y gadgets'),
            Category(name='Ropa', slug='ropa', description='Vestimenta para hombre y mujer'),
            Category(name='Hogar', slug='hogar', description='Artículos para el hogar'),
            Category(name='Deportes', slug='deportes', description='Equipamiento deportivo'),
            Category(name='Libros', slug='libros', description='Libros y material de lectura'),
        ]
        
        for category in categories:
            self.session.add(category)
        
        self.session.flush()
        
        # Subcategorías
        electronics = self.session.query(Category).filter_by(slug='electronicos').first()
        clothing = self.session.query(Category).filter_by(slug='ropa').first()
        
        subcategories = [
            Category(name='Smartphones', slug='smartphones', parent_id=electronics.id),
            Category(name='Laptops', slug='laptops', parent_id=electronics.id),
            Category(name='Camisetas', slug='camisetas', parent_id=clothing.id),
            Category(name='Pantalones', slug='pantalones', parent_id=clothing.id),
        ]
        
        for subcategory in subcategories:
            self.session.add(subcategory)
        
        # Marcas
        brands = [
            Brand(name='Apple', slug='apple', description='Tecnología innovadora'),
            Brand(name='Samsung', slug='samsung', description='Electrónicos de calidad'),
            Brand(name='Nike', slug='nike', description='Ropa deportiva'),
            Brand(name='Adidas', slug='adidas', description='Equipamiento deportivo'),
            Brand(name='Zara', slug='zara', description='Moda contemporánea'),
        ]
        
        for brand in brands:
            self.session.add(brand)
        
        self.session.flush()
        
        # Atributos
        color_group = self.session.query(AttributeGroup).filter_by(name='color').first()
        size_group = self.session.query(AttributeGroup).filter_by(name='size').first()
        
        if color_group:
            colors = [
                Attribute(group_id=color_group.id, name='Rojo', value='red', color_code='#FF0000'),
                Attribute(group_id=color_group.id, name='Azul', value='blue', color_code='#0000FF'),
                Attribute(group_id=color_group.id, name='Negro', value='black', color_code='#000000'),
                Attribute(group_id=color_group.id, name='Blanco', value='white', color_code='#FFFFFF'),
            ]
            
            for color in colors:
                self.session.add(color)
        
        if size_group:
            sizes = [
                Attribute(group_id=size_group.id, name='XS', value='xs'),
                Attribute(group_id=size_group.id, name='S', value='s'),
                Attribute(group_id=size_group.id, name='M', value='m'),
                Attribute(group_id=size_group.id, name='L', value='l'),
                Attribute(group_id=size_group.id, name='XL', value='xl'),
            ]
            
            for size in sizes:
                self.session.add(size)
        
        print("✓ Catálogo base creado")
    
    def seed_products(self):
        """Crea productos con variantes"""
        print("\n🛍️  Creando productos...")
        
        categories = self.session.query(Category).filter(Category.parent_id.isnot(None)).all()
        brands = self.session.query(Brand).all()
        
        if not categories or not brands:
            print("⚠️  Categorías o marcas no encontradas")
            return
        
        products_data = [
            {
                'name': 'iPhone 15 Pro',
                'description': 'El smartphone más avanzado de Apple con chip A17 Pro',
                'price': Decimal('999.99'),
                'category_type': 'smartphones',
                'brand_name': 'Apple'
            },
            {
                'name': 'Samsung Galaxy S24',
                'description': 'Smartphone Android con cámara de 200MP',
                'price': Decimal('899.99'),
                'category_type': 'smartphones',
                'brand_name': 'Samsung'
            },
            {
                'name': 'MacBook Pro 16"',
                'description': 'Laptop profesional con chip M3 Pro',
                'price': Decimal('2499.99'),
                'category_type': 'laptops',
                'brand_name': 'Apple'
            },
            {
                'name': 'Camiseta Nike Dri-FIT',
                'description': 'Camiseta deportiva con tecnología Dri-FIT',
                'price': Decimal('29.99'),
                'category_type': 'camisetas',
                'brand_name': 'Nike'
            },
            {
                'name': 'Jeans Zara Slim Fit',
                'description': 'Pantalones vaqueros de corte slim',
                'price': Decimal('49.99'),
                'category_type': 'pantalones',
                'brand_name': 'Zara'
            },
        ]
        
        created_products = []
        
        for product_data in products_data:
            # Encontrar categoría y marca
            category = next((c for c in categories if product_data['category_type'] in c.slug), categories[0])
            brand = next((b for b in brands if product_data['brand_name'] in b.name), brands[0])
            
            product = Product(
                sku=f"SKU-{fake.random_number(digits=8)}",
                name=product_data['name'],
                slug=fake.slug(),
                short_description=product_data['description'][:100],
                description=product_data['description'],
                price=product_data['price'],
                compare_price=product_data['price'] * Decimal('1.2'),
                cost_price=product_data['price'] * Decimal('0.6'),
                inventory_quantity=random.randint(10, 100),
                category_id=category.id,
                brand_id=brand.id,
                is_active=True,
                is_featured=random.choice([True, False]),
                weight=Decimal(str(random.uniform(0.1, 5.0))),
                meta_title=product_data['name'],
                meta_description=product_data['description'][:160]
            )
            
            self.session.add(product)
            created_products.append(product)
        
        self.session.flush()
        
        # Crear imágenes para productos
        for product in created_products:
            for i in range(random.randint(1, 4)):
                image = ProductImage(
                    product_id=product.id,
                    image_url=f"https://picsum.photos/800/600?random={product.id}{i}",
                    alt_text=f"{product.name} - Imagen {i+1}",
                    sort_order=i,
                    is_primary=(i == 0)
                )
                self.session.add(image)
        
        # Crear variantes para productos de ropa
        colors = self.session.query(Attribute).join(AttributeGroup).filter(AttributeGroup.name == 'color').all()
        sizes = self.session.query(Attribute).join(AttributeGroup).filter(AttributeGroup.name == 'size').all()
        
        for product in created_products:
            if 'camiseta' in product.name.lower() or 'jeans' in product.name.lower():
                # Crear variantes con combinaciones de color y talla
                for color in colors[:2]:  # Solo 2 colores por producto
                    for size in sizes[:3]:  # Solo 3 tallas por producto
                        variant = ProductVariant(
                            product_id=product.id,
                            sku=f"{product.sku}-{color.value}-{size.value}",
                            price=product.price + Decimal(str(random.uniform(-5, 10))),
                            inventory_quantity=random.randint(5, 20)
                        )
                        self.session.add(variant)
                        self.session.flush()
                        
                        # Asignar atributos a la variante
                        variant_color = VariantAttribute(variant_id=variant.id, attribute_id=color.id)
                        variant_size = VariantAttribute(variant_id=variant.id, attribute_id=size.id)
                        self.session.add(variant_color)
                        self.session.add(variant_size)
        
        print(f"✓ Creados {len(created_products)} productos con variantes")
    
    def seed_orders_and_transactions(self):
        """Crea pedidos y transacciones"""
        print("\n🛒 Creando pedidos y transacciones...")
        
        users = self.session.query(User).filter(User.email != 'admin@ecommerce.local').all()
        products = self.session.query(Product).all()
        cities = self.session.query(City).all()
        
        if not users or not products or not cities:
            print("⚠️  Datos requeridos no encontrados")
            return
        
        # Crear direcciones para usuarios
        for user in users[:20]:  # Solo para los primeros 20 usuarios
            city = random.choice(cities)
            address = Address(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                address_line_1=fake.street_address(),
                city_id=city.id,
                state_id=city.state_id,
                country_id=city.state.country_id,
                postal_code=fake.postcode(),
                phone=fake.phone_number()[:20],
                is_default=True
            )
            self.session.add(address)
        
        self.session.flush()
        
        # Crear pedidos
        addresses = self.session.query(Address).all()
        
        for i in range(30):  # 30 pedidos
            user = random.choice(users)
            user_address = next((a for a in addresses if a.user_id == user.id), addresses[0])
            
            order = Order(
                order_number=f"ORD-{fake.random_number(digits=8)}",
                user_id=user.id,
                status=random.choice(list(OrderStatus)),
                email=user.email,
                phone=user.phone,
                billing_address_id=user_address.id,
                shipping_address_id=user_address.id,
                subtotal=Decimal('0'),
                tax_amount=Decimal('0'),
                shipping_amount=Decimal('10.00'),
                total_amount=Decimal('0'),
                currency='USD',
                created_at=fake.date_time_between(start_date='-6M', end_date='now', tzinfo=timezone.utc)
            )
            
            self.session.add(order)
            self.session.flush()
            
            # Crear items del pedido
            subtotal = Decimal('0')
            num_items = random.randint(1, 5)
            
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                unit_price = product.price
                total_price = unit_price * quantity
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    product_sku=product.sku,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                
                self.session.add(order_item)
                subtotal += total_price
            
            # Actualizar totales del pedido
            order.subtotal = subtotal
            order.tax_amount = subtotal * Decimal('0.19')  # 19% tax
            order.total_amount = order.subtotal + order.tax_amount + order.shipping_amount
            
            # Crear pago
            payment = Payment(
                order_id=order.id,
                payment_number=f"PAY-{fake.random_number(digits=8)}",
                method=random.choice(list(PaymentMethod)),
                status=random.choice(list(PaymentStatus)),
                amount=order.total_amount,
                gateway='stripe',
                gateway_transaction_id=fake.uuid4(),
                processed_at=order.created_at + timedelta(minutes=random.randint(1, 30))
            )
            
            self.session.add(payment)
        
        print("✓ Pedidos y transacciones creados")
    
    def seed_reviews_and_ratings(self):
        """Crea reseñas y calificaciones"""
        print("\n⭐ Creando reseñas y calificaciones...")
        
        users = self.session.query(User).filter(User.email != 'admin@ecommerce.local').all()
        products = self.session.query(Product).all()
        orders = self.session.query(Order).all()
        
        if not users or not products:
            print("⚠️  Usuarios o productos no encontrados")
            return
        
        # Crear reseñas
        for _ in range(100):  # 100 reseñas
            user = random.choice(users)
            product = random.choice(products)
            order = random.choice(orders) if orders else None
            
            # Verificar que no exista ya una reseña del mismo usuario para el mismo producto
            existing_review = self.session.query(Review).filter_by(
                user_id=user.id, 
                product_id=product.id
            ).first()
            
            if existing_review:
                continue
            
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 35, 35])[0]  # Más reseñas positivas
            
            review = Review(
                product_id=product.id,
                user_id=user.id,
                order_id=order.id if order and order.user_id == user.id else None,
                rating=rating,
                title=fake.sentence(nb_words=4),
                comment=fake.text(max_nb_chars=500),
                is_approved=random.choice([True, True, True, False]),  # 75% aprobadas
                is_verified_purchase=order is not None and order.user_id == user.id,
                helpful_count=random.randint(0, 20),
                not_helpful_count=random.randint(0, 5),
                created_at=fake.date_time_between(start_date='-3M', end_date='now', tzinfo=timezone.utc)
            )
            
            self.session.add(review)
        
        print("✓ Reseñas y calificaciones creadas")
    
    def seed_coupons(self):
        """Crea cupones de descuento"""
        print("\n🎫 Creando cupones de descuento...")
        
        coupons_data = [
            {
                'code': 'WELCOME10',
                'name': 'Bienvenida 10%',
                'description': 'Descuento de bienvenida para nuevos clientes',
                'type': CouponType.PERCENTAGE,
                'value': Decimal('10.00'),
                'minimum_amount': Decimal('50.00')
            },
            {
                'code': 'SAVE20',
                'name': 'Ahorra $20',
                'description': 'Descuento fijo de $20 en tu compra',
                'type': CouponType.FIXED_AMOUNT,
                'value': Decimal('20.00'),
                'minimum_amount': Decimal('100.00')
            },
            {
                'code': 'FREESHIP',
                'name': 'Envío Gratis',
                'description': 'Envío gratuito en tu pedido',
                'type': CouponType.FREE_SHIPPING,
                'value': Decimal('0.00'),
                'minimum_amount': Decimal('75.00')
            },
            {
                'code': 'BLACKFRIDAY',
                'name': 'Black Friday 25%',
                'description': 'Descuento especial Black Friday',
                'type': CouponType.PERCENTAGE,
                'value': Decimal('25.00'),
                'minimum_amount': Decimal('200.00')
            }
        ]
        
        for coupon_data in coupons_data:
            coupon = Coupon(
                code=coupon_data['code'],
                name=coupon_data['name'],
                description=coupon_data['description'],
                type=coupon_data['type'],
                value=coupon_data['value'],
                target=DiscountTarget.ORDER,
                minimum_amount=coupon_data['minimum_amount'],
                usage_limit=random.randint(50, 500),
                usage_limit_per_user=random.randint(1, 3),
                starts_at=datetime.now(timezone.utc) - timedelta(days=30),
                expires_at=datetime.now(timezone.utc) + timedelta(days=60),
                is_active=True
            )
            
            self.session.add(coupon)
        
        print(f"✓ Creados {len(coupons_data)} cupones")
    
    def seed_analytics_data(self):
        """Crea datos de analytics"""
        print("\n📊 Creando datos de analytics...")
        
        users = self.session.query(User).all()
        products = self.session.query(Product).all()
        
        if not products:
            print("⚠️  Productos no encontrados")
            return
        
        # Crear visualizaciones de productos
        for _ in range(1000):  # 1000 visualizaciones
            product = random.choice(products)
            user = random.choice(users) if random.choice([True, False]) else None
            
            view = ProductView(
                product_id=product.id,
                user_id=user.id if user else None,
                session_id=fake.uuid4(),
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                referrer=fake.url() if random.choice([True, False]) else None,
                created_at=fake.date_time_between(start_date='-1M', end_date='now', tzinfo=timezone.utc)
            )
            
            self.session.add(view)
        
        # Crear consultas de búsqueda
        search_terms = [
            'iphone', 'samsung', 'laptop', 'camiseta', 'nike', 'adidas',
            'smartphone', 'ropa deportiva', 'electrónicos', 'ofertas'
        ]
        
        for _ in range(200):  # 200 búsquedas
            query = random.choice(search_terms)
            user = random.choice(users) if random.choice([True, False]) else None
            
            search = SearchQuery(
                query=query,
                user_id=user.id if user else None,
                session_id=fake.uuid4(),
                results_count=random.randint(0, 50),
                clicked_product_id=random.choice(products).id if random.choice([True, False]) else None,
                created_at=fake.date_time_between(start_date='-1M', end_date='now', tzinfo=timezone.utc)
            )
            
            self.session.add(search)
        
        print("✓ Datos de analytics creados")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de seeders eCommerce')
    parser.add_argument('--clear', action='store_true', help='Limpiar datos existentes antes de crear nuevos')
    
    args = parser.parse_args()
    
    seeder = DatabaseSeeder()
    
    if args.clear:
        print("🧹 Limpiando datos existentes...")
        # Aquí podrías agregar lógica para limpiar datos específicos
        # Por ahora, solo mostramos el mensaje
    
    seeder.seed_all()

if __name__ == "__main__":
    main()

