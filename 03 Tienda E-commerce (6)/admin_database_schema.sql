-- Esquema adicional para funcionalidades administrativas
-- eCommerce Moderno - Panel Administrativo

-- Tabla para métodos de pago
CREATE TABLE IF NOT EXISTS payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('credit_card', 'debit_card', 'paypal', 'bank_transfer', 'webpay', 'mercadopago') NOT NULL,
    config JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla para configuración de tienda
CREATE TABLE IF NOT EXISTS store_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insertar métodos de pago por defecto
INSERT IGNORE INTO payment_methods (name, type, config, is_active) VALUES
('Tarjeta de Crédito', 'credit_card', '{"processor": "stripe", "currencies": ["CLP", "USD"]}', TRUE),
('Tarjeta de Débito', 'debit_card', '{"processor": "stripe", "currencies": ["CLP"]}', TRUE),
('PayPal', 'paypal', '{"client_id": "", "client_secret": ""}', FALSE),
('WebPay', 'webpay', '{"commerce_code": "", "api_key": ""}', FALSE),
('MercadoPago', 'mercadopago', '{"access_token": "", "public_key": ""}', FALSE),
('Transferencia Bancaria', 'bank_transfer', '{"bank_info": "Información bancaria aquí"}', TRUE);

-- Insertar configuración básica de tienda
INSERT IGNORE INTO store_config (`key`, value) VALUES
('store_name', 'eCommerce Moderno'),
('store_description', 'Tu tienda online moderna y profesional'),
('store_email', 'contacto@ecommerce.com'),
('store_phone', '+56 9 1234 5678'),
('store_address', 'Santiago, Chile'),
('currency', 'CLP'),
('tax_rate', '19'),
('shipping_cost', '5000'),
('free_shipping_threshold', '50000'),
('store_logo', ''),
('store_favicon', ''),
('maintenance_mode', 'false'),
('allow_guest_checkout', 'true'),
('require_email_verification', 'false'),
('max_cart_items', '50'),
('session_timeout', '3600'),
('backup_frequency', 'daily'),
('analytics_enabled', 'true'),
('newsletter_enabled', 'true'),
('reviews_enabled', 'true');

-- Actualizar tabla de productos para más campos (MySQL compatible)
ALTER TABLE products 
ADD COLUMN sku VARCHAR(100) UNIQUE,
ADD COLUMN weight DECIMAL(8,2) DEFAULT 0,
ADD COLUMN dimensions VARCHAR(100),
ADD COLUMN meta_title VARCHAR(255),
ADD COLUMN meta_description TEXT,
ADD COLUMN featured BOOLEAN DEFAULT FALSE,
ADD COLUMN sort_order INT DEFAULT 0;

-- Actualizar tabla de órdenes para más información (MySQL compatible)
ALTER TABLE orders 
ADD COLUMN shipping_address TEXT,
ADD COLUMN billing_address TEXT,
ADD COLUMN payment_method VARCHAR(50),
ADD COLUMN payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
ADD COLUMN tracking_number VARCHAR(100),
ADD COLUMN notes TEXT;

-- Tabla para historial de cambios de stock
CREATE TABLE IF NOT EXISTS stock_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    change_type ENUM('increase', 'decrease', 'adjustment') NOT NULL,
    quantity_change INT NOT NULL,
    previous_stock INT NOT NULL,
    new_stock INT NOT NULL,
    reason VARCHAR(255),
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Tabla para cupones de descuento
CREATE TABLE IF NOT EXISTS coupons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    type ENUM('percentage', 'fixed') NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    minimum_amount DECIMAL(10,2) DEFAULT 0,
    usage_limit INT DEFAULT NULL,
    used_count INT DEFAULT 0,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla para reseñas de productos
CREATE TABLE IF NOT EXISTS product_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id)
);

-- Índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_featured ON products(featured);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_stock_history_product ON stock_history(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON product_reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_approved ON product_reviews(is_approved);

