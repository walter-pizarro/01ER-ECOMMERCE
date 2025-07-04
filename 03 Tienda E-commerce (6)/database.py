"""
Configuración y manejo de base de datos
Implementa conexiones seguras con pooling y manejo de errores
"""
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
import pymysql
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from src.config.settings import config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base para modelos SQLAlchemy
Base = declarative_base()

class DatabaseManager:
    """Gestor de conexiones de base de datos"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.redis_client = None
        self._initialize_mysql()
        self._initialize_redis()
    
    def _initialize_mysql(self):
        """Inicializa la conexión a MySQL"""
        try:
            # Configurar engine con pooling
            self.engine = create_engine(
                config.get_database_url(),
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=config.is_development()
            )
            
            # Crear factory de sesiones
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            
            # Probar conexión
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Conexión a MySQL establecida exitosamente")
            
        except Exception as e:
            logger.error(f"Error conectando a MySQL: {e}")
            raise
    
    def _initialize_redis(self):
        """Inicializa la conexión a Redis"""
        try:
            self.redis_client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                db=config.redis.db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Probar conexión
            self.redis_client.ping()
            logger.info("Conexión a Redis establecida exitosamente")
            
        except Exception as e:
            logger.error(f"Error conectando a Redis: {e}")
            # Redis es opcional en desarrollo
            if config.is_production():
                raise
            else:
                logger.warning("Redis no disponible, continuando sin cache")
                self.redis_client = None
    
    @contextmanager
    def get_session(self):
        """Context manager para sesiones de base de datos"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error en sesión de base de datos: {e}")
            raise
        finally:
            session.close()
    
    def get_redis(self) -> Optional[redis.Redis]:
        """Obtiene cliente de Redis"""
        return self.redis_client
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica el estado de las conexiones"""
        status = {
            'mysql': False,
            'redis': False,
            'errors': []
        }
        
        # Verificar MySQL
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            status['mysql'] = True
        except Exception as e:
            status['errors'].append(f"MySQL: {str(e)}")
        
        # Verificar Redis
        try:
            if self.redis_client:
                self.redis_client.ping()
                status['redis'] = True
            else:
                status['errors'].append("Redis: No configurado")
        except Exception as e:
            status['errors'].append(f"Redis: {str(e)}")
        
        return status

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

# Funciones de conveniencia
def get_db_session():
    """Obtiene una sesión de base de datos"""
    return db_manager.get_session()

def get_redis():
    """Obtiene cliente de Redis"""
    return db_manager.get_redis()

def create_tables():
    """Crea todas las tablas definidas en los modelos"""
    try:
        Base.metadata.create_all(bind=db_manager.engine)
        logger.info("Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"Error creando tablas: {e}")
        raise

def drop_tables():
    """Elimina todas las tablas (solo para desarrollo)"""
    if config.is_production():
        raise Exception("No se pueden eliminar tablas en producción")
    
    try:
        Base.metadata.drop_all(bind=db_manager.engine)
        logger.info("Tablas eliminadas exitosamente")
    except Exception as e:
        logger.error(f"Error eliminando tablas: {e}")
        raise

