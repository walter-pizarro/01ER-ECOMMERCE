"""
Configuración principal del sistema eCommerce
Maneja todas las configuraciones de manera segura usando variables de entorno
"""
import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Configuración de base de datos"""
    host: str
    port: int
    database: str
    username: str
    password: str
    charset: str = 'utf8mb4'
    
    @property
    def url(self) -> str:
        return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"

@dataclass
class RedisConfig:
    """Configuración de Redis"""
    host: str
    port: int
    password: str
    db: int = 0
    
    @property
    def url(self) -> str:
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"

@dataclass
class JWTConfig:
    """Configuración de JWT"""
    secret_key: str
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

@dataclass
class EmailConfig:
    """Configuración de email"""
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    from_email: str
    use_tls: bool = True

@dataclass
class PaymentConfig:
    """Configuración de métodos de pago"""
    stripe_public_key: str
    stripe_secret_key: str
    paypal_client_id: str
    paypal_client_secret: str
    mercadopago_access_token: str

class Config:
    """Configuración principal del sistema"""
    
    def __init__(self):
        self.app_name = os.getenv('APP_NAME', 'eCommerce Modular')
        self.app_env = os.getenv('APP_ENV', 'development')
        self.app_debug = os.getenv('APP_DEBUG', 'true').lower() == 'true'
        self.app_url = os.getenv('APP_URL', 'http://localhost:8000')
        self.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
        
        # Configuración de base de datos
        self.database = DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '3306')),
            database=os.getenv('DB_DATABASE', 'ecommerce_db'),
            username=os.getenv('DB_USERNAME', 'ecommerce_user'),
            password=os.getenv('DB_PASSWORD', 'ecommerce_password')
        )
        
        # Configuración de Redis
        self.redis = RedisConfig(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            password=os.getenv('REDIS_PASSWORD', 'redis_password')
        )
        
        # Configuración de JWT
        self.jwt = JWTConfig(
            secret_key=os.getenv('JWT_SECRET_KEY', self.secret_key),
            access_token_expire_minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30')),
            refresh_token_expire_days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7'))
        )
        
        # Configuración de email
        self.email = EmailConfig(
            smtp_host=os.getenv('MAIL_HOST', 'localhost'),
            smtp_port=int(os.getenv('MAIL_PORT', '1025')),
            smtp_username=os.getenv('MAIL_USERNAME', ''),
            smtp_password=os.getenv('MAIL_PASSWORD', ''),
            from_email=os.getenv('MAIL_FROM_ADDRESS', 'noreply@ecommerce.local')
        )
        
        # Configuración de pagos
        self.payment = PaymentConfig(
            stripe_public_key=os.getenv('STRIPE_PUBLIC_KEY', ''),
            stripe_secret_key=os.getenv('STRIPE_SECRET_KEY', ''),
            paypal_client_id=os.getenv('PAYPAL_CLIENT_ID', ''),
            paypal_client_secret=os.getenv('PAYPAL_CLIENT_SECRET', ''),
            mercadopago_access_token=os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
        )
        
        # Configuración de archivos
        self.upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        self.max_content_length = int(os.getenv('MAX_CONTENT_LENGTH', '50')) * 1024 * 1024  # 50MB
        
        # Configuración de CORS
        self.cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
        
        # Configuración de rate limiting
        self.rate_limit_per_minute = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
        
        # Configuración de Elasticsearch
        self.elasticsearch_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        
    def is_production(self) -> bool:
        """Verifica si estamos en entorno de producción"""
        return self.app_env == 'production'
    
    def is_development(self) -> bool:
        """Verifica si estamos en entorno de desarrollo"""
        return self.app_env == 'development'
    
    def get_database_url(self) -> str:
        """Obtiene la URL de conexión a la base de datos"""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Obtiene la URL de conexión a Redis"""
        return self.redis.url
    
    def validate_config(self) -> Dict[str, Any]:
        """Valida la configuración y retorna errores si los hay"""
        errors = []
        warnings = []
        
        # Validaciones críticas
        if self.secret_key == 'your-secret-key-change-in-production':
            if self.is_production():
                errors.append("SECRET_KEY debe ser cambiada en producción")
            else:
                warnings.append("SECRET_KEY usando valor por defecto (solo desarrollo)")
        
        if not self.database.password and self.is_production():
            errors.append("DB_PASSWORD es requerida en producción")
        
        if not self.redis.password and self.is_production():
            errors.append("REDIS_PASSWORD es requerida en producción")
        
        # Validaciones de pagos
        if self.is_production():
            if not self.payment.stripe_secret_key:
                warnings.append("STRIPE_SECRET_KEY no configurada")
            if not self.payment.paypal_client_secret:
                warnings.append("PAYPAL_CLIENT_SECRET no configurada")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        }

# Instancia global de configuración
config = Config()

