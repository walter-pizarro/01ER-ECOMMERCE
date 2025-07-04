"""
APIs de autenticación para eCommerce Modular
Endpoints para login, registro, refresh tokens y gestión de usuarios
"""
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError, validate
import jwt

from services.auth_service import AuthService, token_required, rate_limit

# Crear blueprint para autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Esquemas de validación con Marshmallow
class LoginSchema(Schema):
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    password = fields.Str(required=True, validate=validate.Length(min=6), 
                          error_messages={'required': 'Password is required'})

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)

class RefreshTokenSchema(Schema):
    refresh_token = fields.Str(required=True)

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))

class ResetPasswordRequestSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    reset_token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))

# Instanciar esquemas
login_schema = LoginSchema()
register_schema = RegisterSchema()
refresh_token_schema = RefreshTokenSchema()
change_password_schema = ChangePasswordSchema()
reset_password_request_schema = ResetPasswordRequestSchema()
reset_password_schema = ResetPasswordSchema()

@auth_bp.route('/login', methods=['POST'])
@rate_limit(limit=5, window=300)  # 5 intentos por 5 minutos
def login():
    """
    Autenticar usuario
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login exitoso
        schema:
          type: object
          properties:
            success:
              type: boolean
            user:
              type: object
            tokens:
              type: object
      400:
        description: Datos inválidos
      401:
        description: Credenciales inválidas
      429:
        description: Demasiados intentos
    """
    try:
        # Validar datos de entrada
        data = login_schema.load(request.json)
        
        # Autenticar usuario
        auth_service = AuthService()
        result = auth_service.authenticate_user(data['email'], data['password'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': result['user'],
            'tokens': result['tokens']
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/register', methods=['POST'])
@rate_limit(limit=3, window=3600)  # 3 registros por hora
def register():
    """
    Registrar nuevo usuario
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: user_data
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              format: email
            password:
              type: string
              minLength: 8
            first_name:
              type: string
            last_name:
              type: string
            phone:
              type: string
    responses:
      201:
        description: Usuario registrado exitosamente
      400:
        description: Datos inválidos
      409:
        description: Email ya registrado
    """
    try:
        # Validar datos de entrada
        data = register_schema.load(request.json)
        
        # Registrar usuario
        auth_service = AuthService()
        result = auth_service.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone')
        )
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'user': result['user']
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 409
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@rate_limit(limit=10, window=300)  # 10 refresh por 5 minutos
def refresh_token():
    """
    Renovar access token
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: refresh_data
        required: true
        schema:
          type: object
          properties:
            refresh_token:
              type: string
    responses:
      200:
        description: Token renovado exitosamente
      400:
        description: Refresh token inválido
    """
    try:
        # Validar datos de entrada
        data = refresh_token_schema.load(request.json)
        
        # Renovar token
        auth_service = AuthService()
        tokens = auth_service.refresh_access_token(data['refresh_token'])
        
        return jsonify({
            'success': True,
            'message': 'Token refreshed successfully',
            'tokens': tokens
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Obtener información del usuario actual
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Información del usuario
      401:
        description: Token inválido
    """
    try:
        user = request.current_user
        roles = request.current_user_roles
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'roles': roles,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
@rate_limit(limit=3, window=3600, per='user')  # 3 cambios por hora por usuario
def change_password():
    """
    Cambiar contraseña del usuario actual
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: password_data
        required: true
        schema:
          type: object
          properties:
            current_password:
              type: string
            new_password:
              type: string
              minLength: 8
    responses:
      200:
        description: Contraseña cambiada exitosamente
      400:
        description: Datos inválidos
      401:
        description: Contraseña actual incorrecta
    """
    try:
        # Validar datos de entrada
        data = change_password_schema.load(request.json)
        
        # Cambiar contraseña
        auth_service = AuthService()
        auth_service.change_password(
            user_id=request.current_user.id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/reset-password-request', methods=['POST'])
@rate_limit(limit=3, window=3600)  # 3 solicitudes por hora
def reset_password_request():
    """
    Solicitar reset de contraseña
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: email_data
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              format: email
    responses:
      200:
        description: Solicitud procesada (siempre retorna 200 por seguridad)
    """
    try:
        # Validar datos de entrada
        data = reset_password_request_schema.load(request.json)
        
        # Procesar solicitud
        auth_service = AuthService()
        auth_service.reset_password_request(data['email'])
        
        # Siempre retornar éxito por seguridad (no revelar si el email existe)
        return jsonify({
            'success': True,
            'message': 'If the email exists, a reset link has been sent'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
@rate_limit(limit=5, window=3600)  # 5 intentos por hora
def reset_password():
    """
    Resetear contraseña con token
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: reset_data
        required: true
        schema:
          type: object
          properties:
            reset_token:
              type: string
            new_password:
              type: string
              minLength: 8
    responses:
      200:
        description: Contraseña reseteada exitosamente
      400:
        description: Token inválido o datos incorrectos
    """
    try:
        # Validar datos de entrada
        data = reset_password_schema.load(request.json)
        
        # Resetear contraseña
        auth_service = AuthService()
        auth_service.reset_password(
            reset_token=data['reset_token'],
            new_password=data['new_password']
        )
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/verify-email/<int:user_id>/<token>', methods=['GET'])
def verify_email(user_id, token):
    """
    Verificar email de usuario
    ---
    tags:
      - Authentication
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
      - in: path
        name: token
        type: string
        required: true
    responses:
      200:
        description: Email verificado exitosamente
      400:
        description: Token inválido
    """
    try:
        auth_service = AuthService()
        success = auth_service.verify_user_email(user_id, token)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email verified successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid verification token'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Cerrar sesión (invalidar token)
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Sesión cerrada exitosamente
    """
    # En una implementación completa, aquí se agregaría el token a una blacklist
    # Por simplicidad, solo retornamos éxito
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200

# Manejadores de errores específicos para el blueprint
@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'message': 'The request could not be understood by the server'
    }), 400

@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401

@auth_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 'Forbidden',
        'message': 'Insufficient permissions'
    }), 403

@auth_bp.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429

@auth_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

