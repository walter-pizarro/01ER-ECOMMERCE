"""
Sistema de autenticación JWT para eCommerce Modular
Implementa autenticación segura con tokens JWT y refresh tokens
"""
import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Importar modelos
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.catalog import User, Role, UserRole
from config.database import get_database_url

class AuthService:
    """Servicio de autenticación JWT"""
    
    def __init__(self):
        self.database_url = get_database_url()
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Configuración JWT
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-in-production')
        self.jwt_algorithm = 'HS256'
        self.access_token_expires = timedelta(hours=1)
        self.refresh_token_expires = timedelta(days=30)
    
    def hash_password(self, password: str) -> str:
        """Hashea una contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_tokens(self, user_id: int) -> dict:
        """Genera access token y refresh token para un usuario"""
        now = datetime.now(timezone.utc)
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'type': 'access',
            'iat': now,
            'exp': now + self.access_token_expires
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': now + self.refresh_token_expires
        }
        
        # Generar tokens
        access_token = jwt.encode(access_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        refresh_token = jwt.encode(refresh_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(self.access_token_expires.total_seconds())
        }
    
    def verify_token(self, token: str, token_type: str = 'access') -> dict:
        """Verifica y decodifica un JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Verificar tipo de token
            if payload.get('type') != token_type:
                raise jwt.InvalidTokenError(f"Invalid token type. Expected {token_type}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")
    
    def get_user_by_id(self, user_id: int) -> User:
        """Obtiene un usuario por ID"""
        return self.session.query(User).filter_by(id=user_id, is_active=True).first()
    
    def get_user_by_email(self, email: str) -> User:
        """Obtiene un usuario por email"""
        return self.session.query(User).filter_by(email=email, is_active=True).first()
    
    def get_user_roles(self, user_id: int) -> list:
        """Obtiene los roles de un usuario"""
        user_roles = self.session.query(Role).join(UserRole).filter(
            UserRole.user_id == user_id,
            Role.is_active == True
        ).all()
        
        return [role.name for role in user_roles]
    
    def authenticate_user(self, email: str, password: str) -> dict:
        """Autentica un usuario con email y contraseña"""
        user = self.get_user_by_email(email)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        if not user.is_verified:
            raise ValueError("Account not verified. Please check your email.")
        
        if not self.verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        # Actualizar último login
        user.last_login_at = datetime.now(timezone.utc)
        self.session.commit()
        
        # Generar tokens
        tokens = self.generate_tokens(user.id)
        
        # Obtener roles
        roles = self.get_user_roles(user.id)
        
        return {
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': roles,
                'is_verified': user.is_verified
            },
            'tokens': tokens
        }
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Genera un nuevo access token usando un refresh token"""
        try:
            payload = self.verify_token(refresh_token, 'refresh')
            user_id = payload['user_id']
            
            # Verificar que el usuario aún existe y está activo
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found or inactive")
            
            # Generar nuevo access token
            tokens = self.generate_tokens(user_id)
            
            return tokens
            
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    def register_user(self, email: str, password: str, first_name: str, last_name: str, phone: str = None) -> dict:
        """Registra un nuevo usuario"""
        # Verificar que el email no esté en uso
        existing_user = self.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Crear nuevo usuario
        hashed_password = self.hash_password(password)
        
        new_user = User(
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_active=True,
            is_verified=False  # Requiere verificación por email
        )
        
        self.session.add(new_user)
        self.session.flush()
        
        # Asignar rol de customer por defecto
        customer_role = self.session.query(Role).filter_by(name='customer').first()
        if customer_role:
            user_role = UserRole(user_id=new_user.id, role_id=customer_role.id)
            self.session.add(user_role)
        
        self.session.commit()
        
        return {
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'is_verified': new_user.is_verified
            },
            'message': 'User registered successfully. Please check your email for verification.'
        }
    
    def verify_user_email(self, user_id: int, verification_token: str) -> bool:
        """Verifica el email de un usuario (simplificado para demo)"""
        user = self.get_user_by_id(user_id)
        if user and not user.is_verified:
            user.is_verified = True
            user.email_verified_at = datetime.now(timezone.utc)
            self.session.commit()
            return True
        return False
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Cambia la contraseña de un usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not self.verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Actualizar contraseña
        user.password_hash = self.hash_password(new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        self.session.commit()
        
        return True
    
    def reset_password_request(self, email: str) -> bool:
        """Solicita reset de contraseña (simplificado para demo)"""
        user = self.get_user_by_email(email)
        if user:
            # En producción, aquí se enviaría un email con token de reset
            user.password_reset_token = jwt.encode({
                'user_id': user.id,
                'type': 'password_reset',
                'exp': datetime.now(timezone.utc) + timedelta(hours=1)
            }, self.jwt_secret, algorithm=self.jwt_algorithm)
            
            user.password_reset_requested_at = datetime.now(timezone.utc)
            self.session.commit()
            return True
        return False
    
    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """Resetea la contraseña usando un token de reset"""
        try:
            payload = self.verify_token(reset_token, 'password_reset')
            user_id = payload['user_id']
            
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Actualizar contraseña
            user.password_hash = self.hash_password(new_password)
            user.password_changed_at = datetime.now(timezone.utc)
            user.password_reset_token = None
            user.password_reset_requested_at = None
            self.session.commit()
            
            return True
            
        except jwt.InvalidTokenError:
            raise ValueError("Invalid or expired reset token")

# Decoradores para autenticación y autorización
def token_required(f):
    """Decorador que requiere un token JWT válido"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            auth_service = AuthService()
            payload = auth_service.verify_token(token)
            current_user = auth_service.get_user_by_id(payload['user_id'])
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            # Agregar usuario actual al contexto
            request.current_user = current_user
            request.current_user_roles = auth_service.get_user_roles(current_user.id)
            
        except jwt.InvalidTokenError as e:
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            return jsonify({'error': 'Token validation failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(*required_roles):
    """Decorador que requiere roles específicos"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user_roles = getattr(request, 'current_user_roles', [])
            
            if not any(role in user_roles for role in required_roles):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': list(required_roles),
                    'user_roles': user_roles
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

def admin_required(f):
    """Decorador que requiere rol de administrador"""
    return role_required('admin')(f)

def manager_required(f):
    """Decorador que requiere rol de manager o admin"""
    return role_required('admin', 'manager')(f)

# Middleware de rate limiting (simplificado)
class RateLimiter:
    """Rate limiter básico en memoria"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Verifica si una request está permitida"""
        now = datetime.now()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Limpiar requests antiguas
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if (now - req_time).seconds < window
        ]
        
        # Verificar límite
        if len(self.requests[key]) >= limit:
            return False
        
        # Agregar request actual
        self.requests[key].append(now)
        return True

# Instancia global del rate limiter
rate_limiter = RateLimiter()

def rate_limit(limit: int = 100, window: int = 3600, per: str = 'ip'):
    """Decorador de rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if per == 'ip':
                key = request.remote_addr
            elif per == 'user' and hasattr(request, 'current_user'):
                key = f"user_{request.current_user.id}"
            else:
                key = request.remote_addr
            
            if not rate_limiter.is_allowed(key, limit, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': limit,
                    'window': window
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

