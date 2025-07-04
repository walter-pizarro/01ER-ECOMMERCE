# 🛍️ eCommerce Modular

Sistema de comercio electrónico moderno, escalable y reutilizable construido con las mejores prácticas de desarrollo.

## 🚀 Características Principales

### ✨ Arquitectura Moderna
- **Microservicios modulares** con APIs RESTful
- **Frontend desacoplado** con React/Vue.js
- **Base de datos optimizada** con MySQL 8.0 + Redis
- **Búsqueda avanzada** con Elasticsearch
- **Containerización completa** con Docker

### 🔒 Seguridad Enterprise
- **Autenticación JWT** con refresh tokens
- **Autorización granular** por roles y permisos
- **Validación exhaustiva** de todas las entradas
- **Cifrado end-to-end** con TLS 1.3
- **Auditoría completa** de acciones críticas

### ⚡ Rendimiento Optimizado
- **Cache multi-nivel** (Redis + CDN + Application)
- **Base de datos normalizada** con índices optimizados
- **Lazy loading** y code splitting
- **Compresión automática** de assets
- **CDN integration** para assets estáticos

### 🔄 Reutilización Multi-Cliente
- **Configuración dinámica** por cliente
- **Temas personalizables** sin modificar código
- **Feature flags** para funcionalidades específicas
- **Onboarding automatizado** con wizard
- **Templates por industria** preconfigurados

## 📋 Requerimientos del Sistema

### Desarrollo
- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (para desarrollo frontend)
- Python 3.9+ (para desarrollo backend)

### Producción
- 4 GB RAM mínimo (8 GB recomendado)
- 2 CPU cores mínimo (4 cores recomendado)
- 50 GB almacenamiento mínimo
- SSL/TLS certificado

## 🛠️ Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd ecommerce-modular
```

### 2. Configuración Inicial
```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar configuración (cambiar credenciales)
nano .env

# Ejecutar configuración inicial
./scripts/dev.sh setup
```

### 3. Iniciar Servicios
```bash
# Iniciar todos los servicios
./scripts/dev.sh start

# O iniciar servicios específicos
./scripts/dev.sh backend   # Solo backend
./scripts/dev.sh frontend  # Solo frontend
./scripts/dev.sh db        # Solo base de datos
```

## 🌐 URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interfaz de usuario principal |
| **Backend API** | http://localhost:8000 | APIs RESTful |
| **Nginx** | http://localhost | Reverse proxy |
| **Mailhog** | http://localhost:8025 | Testing de emails |
| **Elasticsearch** | http://localhost:9200 | Motor de búsqueda |

## 📁 Estructura del Proyecto

```
ecommerce-modular/
├── backend/                 # Backend API (Python/Flask)
│   └── ecommerce-api/
│       ├── src/
│       │   ├── controllers/ # Controladores de API
│       │   ├── models/      # Modelos de datos
│       │   ├── services/    # Lógica de negocio
│       │   ├── middleware/  # Middleware personalizado
│       │   ├── validators/  # Validadores de entrada
│       │   ├── config/      # Configuración del sistema
│       │   └── database/    # Migraciones y seeders
│       └── requirements.txt
├── frontend/                # Frontend (React/Vue.js)
│   └── ecommerce-frontend/
│       ├── src/
│       │   ├── components/  # Componentes reutilizables
│       │   ├── views/       # Páginas principales
│       │   ├── stores/      # Gestión de estado
│       │   ├── services/    # Servicios de API
│       │   └── utils/       # Utilidades
│       └── package.json
├── docker/                  # Configuración Docker
│   ├── backend/
│   ├── frontend/
│   ├── mysql/
│   └── nginx/
├── scripts/                 # Scripts de automatización
│   └── dev.sh              # Script principal de desarrollo
├── docs/                    # Documentación
├── docker-compose.yml       # Orquestación de servicios
└── .env.example            # Configuración de ejemplo
```

## 🔧 Comandos de Desarrollo

### Scripts Principales
```bash
./scripts/dev.sh setup      # Configuración inicial
./scripts/dev.sh start      # Iniciar servicios
./scripts/dev.sh stop       # Detener servicios
./scripts/dev.sh restart    # Reiniciar servicios
./scripts/dev.sh logs       # Ver logs
./scripts/dev.sh test       # Ejecutar tests
./scripts/dev.sh build      # Build para producción
./scripts/dev.sh clean      # Limpiar contenedores
./scripts/dev.sh status     # Estado de servicios
```

### Desarrollo Backend
```bash
# Entrar al contenedor del backend
docker-compose exec backend bash

# Ejecutar migraciones
python src/database/migrate.py

# Ejecutar seeders
python src/database/seed.py

# Ejecutar tests
python -m pytest tests/ -v
```

### Desarrollo Frontend
```bash
# Entrar al contenedor del frontend
docker-compose exec frontend bash

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# Ejecutar tests
npm test

# Build para producción
npm run build
```

## 🧪 Testing

### Backend Testing
```bash
# Tests unitarios
docker-compose exec backend python -m pytest tests/unit/ -v

# Tests de integración
docker-compose exec backend python -m pytest tests/integration/ -v

# Tests de API
docker-compose exec backend python -m pytest tests/api/ -v

# Coverage report
docker-compose exec backend python -m pytest --cov=src tests/
```

### Frontend Testing
```bash
# Tests unitarios
docker-compose exec frontend npm run test:unit

# Tests de componentes
docker-compose exec frontend npm run test:components

# Tests end-to-end
docker-compose exec frontend npm run test:e2e
```

## 🚀 Despliegue en Producción

### 1. Preparación
```bash
# Build para producción
./scripts/dev.sh build

# Verificar configuración
./scripts/dev.sh status
```

### 2. Variables de Entorno
Configurar las siguientes variables críticas:
- `SECRET_KEY`: Clave secreta única
- `DB_PASSWORD`: Contraseña segura de base de datos
- `REDIS_PASSWORD`: Contraseña de Redis
- `JWT_SECRET_KEY`: Clave secreta para JWT
- Credenciales de pagos (Stripe, PayPal, etc.)

### 3. SSL/TLS
```bash
# Configurar certificados SSL
cp your-cert.pem docker/nginx/ssl/
cp your-key.pem docker/nginx/ssl/

# Actualizar configuración de Nginx
nano docker/nginx/sites/default.conf
```

## 📊 Monitoreo y Logs

### Logs de Aplicación
```bash
# Ver logs en tiempo real
./scripts/dev.sh logs

# Logs específicos por servicio
./scripts/dev.sh logs backend
./scripts/dev.sh logs frontend
./scripts/dev.sh logs mysql
```

### Métricas de Performance
- **Prometheus**: Métricas del sistema
- **Grafana**: Dashboards de monitoreo
- **Health checks**: Verificación automática de servicios

## 🔧 Configuración Multi-Cliente

### 1. Crear Nuevo Cliente
```bash
# Ejecutar wizard de configuración
python scripts/create_client.py --name "Mi Tienda" --domain "mitienda.com"
```

### 2. Personalización
- **Temas**: Configurar colores, tipografía, layout
- **Funcionalidades**: Habilitar/deshabilitar features
- **Integraciones**: Configurar pagos, envíos, etc.
- **Contenido**: Cargar productos, categorías, etc.

## 🛡️ Seguridad

### Mejores Prácticas Implementadas
- ✅ **Credenciales seguras**: Variables de entorno
- ✅ **Prepared statements**: Prevención de SQL injection
- ✅ **Validación de entrada**: Sanitización automática
- ✅ **HTTPS obligatorio**: Cifrado de comunicaciones
- ✅ **Rate limiting**: Protección contra ataques
- ✅ **CORS configurado**: Control de acceso
- ✅ **Headers de seguridad**: CSP, HSTS, etc.

### Auditoría de Seguridad
```bash
# Escaneo de vulnerabilidades
docker-compose exec backend safety check

# Análisis de dependencias
docker-compose exec frontend npm audit

# Tests de penetración
python scripts/security_scan.py
```

## 📈 Performance

### Optimizaciones Implementadas
- **Base de datos**: Índices optimizados, consultas eficientes
- **Cache**: Redis multi-nivel, CDN integration
- **Frontend**: Lazy loading, code splitting, compresión
- **Assets**: Optimización automática de imágenes
- **CDN**: Distribución global de contenido

### Métricas Objetivo
- **Página principal**: < 2 segundos
- **APIs**: < 100ms respuesta
- **Capacidad**: 10,000+ usuarios concurrentes
- **Disponibilidad**: 99.9% uptime

## 🤝 Contribución

### Proceso de Desarrollo
1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código
- **Backend**: PEP 8 para Python
- **Frontend**: ESLint + Prettier
- **Commits**: Conventional Commits
- **Testing**: Cobertura mínima 80%

## 📞 Soporte

### Documentación
- **API Docs**: http://localhost:8000/docs
- **Frontend Docs**: http://localhost:3000/docs
- **Wiki**: Documentación detallada en `/docs`

### Contacto
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@ecommerce-modular.com

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**eCommerce Modular** - Sistema de comercio electrónico del futuro 🚀

