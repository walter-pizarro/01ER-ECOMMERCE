#!/bin/bash
# Script de Despliegue Automatizado para Producción
# eCommerce Moderno - Configuración de Producción

set -e

echo "🚀 INICIANDO CONFIGURACIÓN DE PRODUCCIÓN"
echo "========================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Variables de configuración
PROJECT_NAME="ecommerce-moderno"
DOMAIN="${DOMAIN:-ecommerce.example.com}"
EMAIL="${EMAIL:-admin@example.com}"
ENVIRONMENT="${ENVIRONMENT:-production}"

log "Configurando entorno de producción para $PROJECT_NAME"
log "Dominio: $DOMAIN"
log "Ambiente: $ENVIRONMENT"

# 1. Verificar dependencias
log "Verificando dependencias del sistema..."

check_dependency() {
    if ! command -v $1 &> /dev/null; then
        error "$1 no está instalado"
        exit 1
    else
        log "✅ $1 encontrado"
    fi
}

check_dependency "docker"
check_dependency "docker-compose"
check_dependency "git"
check_dependency "curl"

# 2. Crear estructura de directorios de producción
log "Creando estructura de directorios..."

mkdir -p /opt/ecommerce-production/{config,logs,backups,ssl,scripts}
mkdir -p /opt/ecommerce-production/data/{mysql,redis,uploads}

log "✅ Estructura de directorios creada"

# 3. Configurar variables de entorno de producción
log "Configurando variables de entorno de producción..."

cat > /opt/ecommerce-production/.env << EOF
# Configuración de Producción - eCommerce Moderno
ENVIRONMENT=production
DEBUG=false

# Base de Datos
DATABASE_URL=mysql://ecommerce_user:$(openssl rand -base64 32)@mysql:3306/ecommerce_prod
DATABASE_HOST=mysql
DATABASE_PORT=3306
DATABASE_NAME=ecommerce_prod
DATABASE_USER=ecommerce_user
DATABASE_PASSWORD=$(openssl rand -base64 32)

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=$(openssl rand -base64 32)

# JWT y Seguridad
JWT_SECRET_KEY=$(openssl rand -base64 64)
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400
SECRET_KEY=$(openssl rand -base64 64)
SECURITY_PASSWORD_SALT=$(openssl rand -base64 32)

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=${EMAIL}
SMTP_PASSWORD=your_app_password_here
SMTP_USE_TLS=true

# Pagos - Configurar con credenciales reales
STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

PAYPAL_CLIENT_ID=your_paypal_live_client_id
PAYPAL_CLIENT_SECRET=your_paypal_live_client_secret
PAYPAL_MODE=live

MERCADOPAGO_ACCESS_TOKEN=your_mercadopago_live_token
MERCADOPAGO_PUBLIC_KEY=your_mercadopago_live_public_key

# Dominio y URLs
DOMAIN=${DOMAIN}
FRONTEND_URL=https://${DOMAIN}
BACKEND_URL=https://api.${DOMAIN}
CDN_URL=https://cdn.${DOMAIN}

# SSL/TLS
SSL_CERT_PATH=/etc/ssl/certs/${DOMAIN}.crt
SSL_KEY_PATH=/etc/ssl/private/${DOMAIN}.key

# Logging
LOG_LEVEL=INFO
LOG_FILE=/opt/ecommerce-production/logs/app.log

# Backup
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET=ecommerce-backups-$(date +%s)

# Monitoreo
SENTRY_DSN=your_sentry_dsn_here
NEW_RELIC_LICENSE_KEY=your_newrelic_key_here

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST=200

# Cache
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=300
CACHE_KEY_PREFIX=ecommerce_prod

# Session
SESSION_TYPE=redis
SESSION_PERMANENT=false
SESSION_USE_SIGNER=true
SESSION_KEY_PREFIX=session:

# File Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/opt/ecommerce-production/data/uploads
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx

# Security Headers
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
EOF

log "✅ Variables de entorno configuradas"

# 4. Crear docker-compose para producción
log "Creando configuración Docker para producción..."

cat > /opt/ecommerce-production/docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: ecommerce_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/sites:/etc/nginx/conf.d:ro
      - ./ssl:/etc/ssl:ro
      - ./data/uploads:/var/www/uploads:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - ecommerce_network

  # Frontend React
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: ecommerce_frontend
    environment:
      - NODE_ENV=production
      - VITE_API_URL=https://api.${DOMAIN}
      - VITE_CDN_URL=https://cdn.${DOMAIN}
    volumes:
      - frontend_build:/app/dist
    restart: unless-stopped
    networks:
      - ecommerce_network

  # Backend Flask API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: ecommerce_backend
    env_file:
      - .env
    volumes:
      - ./data/uploads:/app/uploads
      - ./logs/backend:/app/logs
      - ./backups:/app/backups
    depends_on:
      - mysql
      - redis
      - elasticsearch
    restart: unless-stopped
    networks:
      - ecommerce_network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  # MySQL Database
  mysql:
    image: mysql:8.0
    container_name: ecommerce_mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${DATABASE_PASSWORD}
      MYSQL_DATABASE: ${DATABASE_NAME}
      MYSQL_USER: ${DATABASE_USER}
      MYSQL_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./config/mysql.cnf:/etc/mysql/conf.d/custom.cnf:ro
      - ./backups/mysql:/backups
      - ./logs/mysql:/var/log/mysql
    ports:
      - "127.0.0.1:3306:3306"
    restart: unless-stopped
    networks:
      - ecommerce_network
    command: >
      --innodb-buffer-pool-size=512M
      --innodb-log-file-size=128M
      --max-connections=200
      --query-cache-type=1
      --query-cache-size=64M

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: ecommerce_redis
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    volumes:
      - redis_data:/data
      - ./logs/redis:/var/log/redis
    ports:
      - "127.0.0.1:6379:6379"
    restart: unless-stopped
    networks:
      - ecommerce_network

  # Elasticsearch
  elasticsearch:
    image: elasticsearch:8.11.0
    container_name: ecommerce_elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
      - ./logs/elasticsearch:/usr/share/elasticsearch/logs
    ports:
      - "127.0.0.1:9200:9200"
    restart: unless-stopped
    networks:
      - ecommerce_network

  # Backup Service
  backup:
    build:
      context: ./scripts/backup
      dockerfile: Dockerfile
    container_name: ecommerce_backup
    env_file:
      - .env
    volumes:
      - ./backups:/backups
      - mysql_data:/mysql_data:ro
      - redis_data:/redis_data:ro
      - ./data/uploads:/uploads:ro
    depends_on:
      - mysql
      - redis
    restart: unless-stopped
    networks:
      - ecommerce_network

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: ecommerce_prometheus
    ports:
      - "127.0.0.1:9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    restart: unless-stopped
    networks:
      - ecommerce_network

  grafana:
    image: grafana/grafana:latest
    container_name: ecommerce_grafana
    ports:
      - "127.0.0.1:3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin123}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana:/etc/grafana/provisioning
    restart: unless-stopped
    networks:
      - ecommerce_network

volumes:
  mysql_data:
    driver: local
  redis_data:
    driver: local
  elasticsearch_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
  frontend_build:
    driver: local

networks:
  ecommerce_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF

log "✅ Docker Compose para producción creado"

# 5. Configurar Nginx para producción
log "Configurando Nginx para producción..."

mkdir -p /opt/ecommerce-production/config/sites

cat > /opt/ecommerce-production/config/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 16M;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Include site configurations
    include /etc/nginx/conf.d/*.conf;
}
EOF

cat > /opt/ecommerce-production/config/sites/default.conf << 'EOF'
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/${DOMAIN}.crt;
    ssl_certificate_key /etc/ssl/private/${DOMAIN}.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.stripe.com;" always;

    # Frontend (React)
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Cache for static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Vary Accept-Encoding;
        }
    }

    # API Backend
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://backend:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffers
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # Auth endpoints with stricter rate limiting
    location /api/auth/ {
        limit_req zone=login burst=5 nodelay;
        
        proxy_pass http://backend:5000/auth/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # File uploads
    location /uploads/ {
        alias /var/www/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}

# API subdomain
server {
    listen 443 ssl http2;
    server_name api.${DOMAIN};

    # SSL Configuration (same as main)
    ssl_certificate /etc/ssl/certs/${DOMAIN}.crt;
    ssl_certificate_key /etc/ssl/private/${DOMAIN}.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;

    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://backend:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

log "✅ Configuración Nginx completada"

# 6. Crear scripts de backup
log "Configurando sistema de backup..."

mkdir -p /opt/ecommerce-production/scripts/backup

cat > /opt/ecommerce-production/scripts/backup/backup.sh << 'EOF'
#!/bin/bash
# Script de Backup Automatizado

set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Crear directorio de backup
mkdir -p "$BACKUP_DIR/$DATE"

# Backup MySQL
log "Iniciando backup de MySQL..."
mysqldump -h mysql -u $DATABASE_USER -p$DATABASE_PASSWORD $DATABASE_NAME > "$BACKUP_DIR/$DATE/mysql_backup.sql"
gzip "$BACKUP_DIR/$DATE/mysql_backup.sql"
log "✅ Backup MySQL completado"

# Backup Redis
log "Iniciando backup de Redis..."
redis-cli -h redis -a $REDIS_PASSWORD --rdb "$BACKUP_DIR/$DATE/redis_backup.rdb"
gzip "$BACKUP_DIR/$DATE/redis_backup.rdb"
log "✅ Backup Redis completado"

# Backup archivos subidos
log "Iniciando backup de archivos..."
tar -czf "$BACKUP_DIR/$DATE/uploads_backup.tar.gz" -C /uploads .
log "✅ Backup archivos completado"

# Limpiar backups antiguos
log "Limpiando backups antiguos..."
find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} +
log "✅ Limpieza completada"

# Subir a S3 (opcional)
if [ ! -z "$BACKUP_S3_BUCKET" ]; then
    log "Subiendo backup a S3..."
    aws s3 sync "$BACKUP_DIR/$DATE" "s3://$BACKUP_S3_BUCKET/$DATE/"
    log "✅ Backup subido a S3"
fi

log "🎉 Backup completado: $DATE"
EOF

chmod +x /opt/ecommerce-production/scripts/backup/backup.sh

# 7. Configurar SSL/TLS (Let's Encrypt)
log "Configurando certificados SSL..."

cat > /opt/ecommerce-production/scripts/setup-ssl.sh << 'EOF'
#!/bin/bash
# Script para configurar SSL con Let's Encrypt

set -e

DOMAIN=${1:-$DOMAIN}
EMAIL=${2:-$EMAIL}

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Uso: $0 <domain> <email>"
    exit 1
fi

# Instalar certbot si no existe
if ! command -v certbot &> /dev/null; then
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Obtener certificado
certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN \
    -d api.$DOMAIN

# Copiar certificados
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/ecommerce-production/ssl/$DOMAIN.crt
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/ecommerce-production/ssl/$DOMAIN.key

# Configurar renovación automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -

echo "✅ SSL configurado para $DOMAIN"
EOF

chmod +x /opt/ecommerce-production/scripts/setup-ssl.sh

# 8. Crear script de despliegue
log "Creando script de despliegue..."

cat > /opt/ecommerce-production/deploy.sh << 'EOF'
#!/bin/bash
# Script de Despliegue Principal

set -e

ENVIRONMENT=${1:-production}
BRANCH=${2:-main}

log() {
    echo -e "\033[0;32m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

error() {
    echo -e "\033[0;31m[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1\033[0m"
}

log "🚀 Iniciando despliegue en $ENVIRONMENT"

# Verificar que estamos en el directorio correcto
cd /opt/ecommerce-production

# Actualizar código fuente
if [ -d ".git" ]; then
    log "Actualizando código fuente..."
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    log "Clonando repositorio..."
    git clone https://github.com/tu-usuario/ecommerce-moderno.git .
    git checkout $BRANCH
fi

# Construir imágenes
log "Construyendo imágenes Docker..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Ejecutar migraciones
log "Ejecutando migraciones de base de datos..."
docker-compose -f docker-compose.prod.yml run --rm backend python manage.py migrate

# Ejecutar seeders (solo en primera instalación)
if [ "$3" = "--seed" ]; then
    log "Ejecutando seeders..."
    docker-compose -f docker-compose.prod.yml run --rm backend python manage.py seed
fi

# Detener servicios existentes
log "Deteniendo servicios existentes..."
docker-compose -f docker-compose.prod.yml down

# Iniciar servicios
log "Iniciando servicios..."
docker-compose -f docker-compose.prod.yml up -d

# Verificar salud del sistema
log "Verificando salud del sistema..."
sleep 30

if curl -f http://localhost/health > /dev/null 2>&1; then
    log "✅ Despliegue completado exitosamente"
else
    error "❌ Fallo en verificación de salud"
    exit 1
fi

log "🎉 Sistema desplegado y funcionando"
EOF

chmod +x /opt/ecommerce-production/deploy.sh

log "✅ Script de despliegue creado"

# 9. Configurar monitoreo básico
log "Configurando monitoreo básico..."

mkdir -p /opt/ecommerce-production/config

cat > /opt/ecommerce-production/config/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ecommerce-backend'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    scrape_interval: 30s

  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql:9104']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
    scrape_interval: 30s
EOF

log "✅ Configuración de monitoreo completada"

# 10. Crear documentación de despliegue
log "Creando documentación de despliegue..."

cat > /opt/ecommerce-production/README.md << 'EOF'
# eCommerce Moderno - Despliegue en Producción

## Configuración Inicial

1. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   # Editar .env con valores reales
   ```

2. **Configurar SSL**:
   ```bash
   ./scripts/setup-ssl.sh tu-dominio.com tu-email@ejemplo.com
   ```

3. **Primer despliegue**:
   ```bash
   ./deploy.sh production main --seed
   ```

## Comandos Útiles

- **Desplegar**: `./deploy.sh production main`
- **Ver logs**: `docker-compose -f docker-compose.prod.yml logs -f`
- **Backup manual**: `./scripts/backup/backup.sh`
- **Reiniciar servicios**: `docker-compose -f docker-compose.prod.yml restart`

## Monitoreo

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin123)
- **Logs**: `/opt/ecommerce-production/logs/`

## Backup

Los backups se ejecutan automáticamente cada día a las 2:00 AM.
Ubicación: `/opt/ecommerce-production/backups/`

## Troubleshooting

1. **Verificar estado de servicios**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. **Ver logs de un servicio específico**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend
   ```

3. **Acceder a contenedor**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend bash
   ```
EOF

log "✅ Documentación creada"

# Resumen final
echo ""
echo "🎉 CONFIGURACIÓN DE PRODUCCIÓN COMPLETADA"
echo "========================================"
echo ""
echo "📁 Directorio de producción: /opt/ecommerce-production"
echo "🔧 Configuración: /opt/ecommerce-production/.env"
echo "🚀 Despliegue: /opt/ecommerce-production/deploy.sh"
echo "📚 Documentación: /opt/ecommerce-production/README.md"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Editar /opt/ecommerce-production/.env con valores reales"
echo "2. Configurar SSL: ./scripts/setup-ssl.sh tu-dominio.com tu-email@ejemplo.com"
echo "3. Ejecutar primer despliegue: ./deploy.sh production main --seed"
echo ""
echo "⚠️  IMPORTANTE:"
echo "- Configurar credenciales reales de pagos en .env"
echo "- Configurar SMTP para emails"
echo "- Configurar backup en S3 (opcional)"
echo "- Revisar configuración de dominio y DNS"
echo ""

log "Script de configuración completado exitosamente"

