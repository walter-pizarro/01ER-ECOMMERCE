-- Solo crear las tablas nuevas y configuraciones que faltan
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

-- Agregar campos faltantes a products (solo si no existen)
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS original_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS status ENUM('active', 'inactive', 'draft') DEFAULT 'active',
ADD COLUMN IF NOT EXISTS meta_title VARCHAR(255),
ADD COLUMN IF NOT EXISTS meta_description TEXT,
ADD COLUMN IF NOT EXISTS featured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS sort_order INT DEFAULT 0;

-- Renombrar columnas existentes para consistencia
ALTER TABLE products 
CHANGE COLUMN stock_quantity stock INT DEFAULT 0,
CHANGE COLUMN sale_price original_price DECIMAL(10,2);

-- Agregar campos faltantes a orders
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS shipping_address TEXT,
ADD COLUMN IF NOT EXISTS billing_address TEXT,
ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50),
ADD COLUMN IF NOT EXISTS payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS tracking_number VARCHAR(100),
ADD COLUMN IF NOT EXISTS notes TEXT;

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

