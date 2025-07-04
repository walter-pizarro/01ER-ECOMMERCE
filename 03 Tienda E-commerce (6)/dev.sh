#!/bin/bash

# Script de desarrollo para eCommerce Modular
# Automatiza tareas comunes de desarrollo

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}eCommerce Modular - Script de Desarrollo${NC}"
    echo ""
    echo "Uso: ./dev.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  setup     - Configuración inicial del proyecto"
    echo "  start     - Iniciar todos los servicios"
    echo "  stop      - Detener todos los servicios"
    echo "  restart   - Reiniciar todos los servicios"
    echo "  logs      - Mostrar logs de todos los servicios"
    echo "  backend   - Iniciar solo el backend"
    echo "  frontend  - Iniciar solo el frontend"
    echo "  db        - Iniciar solo la base de datos"
    echo "  test      - Ejecutar tests"
    echo "  build     - Construir para producción"
    echo "  clean     - Limpiar contenedores y volúmenes"
    echo "  status    - Mostrar estado de los servicios"
    echo "  help      - Mostrar esta ayuda"
}

# Función para verificar dependencias
check_dependencies() {
    echo -e "${BLUE}Verificando dependencias...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker no está instalado${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose no está instalado${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Dependencias verificadas${NC}"
}

# Función de configuración inicial
setup() {
    echo -e "${BLUE}Configurando proyecto eCommerce Modular...${NC}"
    
    check_dependencies
    
    # Crear archivos de entorno si no existen
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Creando archivo .env...${NC}"
        cp .env.example .env
    fi
    
    # Construir imágenes
    echo -e "${BLUE}Construyendo imágenes Docker...${NC}"
    docker-compose build
    
    # Iniciar servicios de base de datos
    echo -e "${BLUE}Iniciando servicios de base de datos...${NC}"
    docker-compose up -d mysql redis elasticsearch
    
    # Esperar a que la base de datos esté lista
    echo -e "${YELLOW}Esperando a que la base de datos esté lista...${NC}"
    sleep 30
    
    # Ejecutar migraciones
    echo -e "${BLUE}Ejecutando migraciones de base de datos...${NC}"
    docker-compose exec backend python src/database/migrate.py
    
    # Ejecutar seeders
    echo -e "${BLUE}Ejecutando seeders de datos de prueba...${NC}"
    docker-compose exec backend python src/database/seed.py
    
    echo -e "${GREEN}✓ Configuración completada${NC}"
    echo -e "${YELLOW}Ejecuta './dev.sh start' para iniciar todos los servicios${NC}"
}

# Función para iniciar servicios
start() {
    echo -e "${BLUE}Iniciando servicios eCommerce Modular...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}✓ Servicios iniciados${NC}"
    echo -e "${YELLOW}Frontend: http://localhost:3000${NC}"
    echo -e "${YELLOW}Backend API: http://localhost:8000${NC}"
    echo -e "${YELLOW}Nginx: http://localhost${NC}"
    echo -e "${YELLOW}Mailhog: http://localhost:8025${NC}"
    echo -e "${YELLOW}Elasticsearch: http://localhost:9200${NC}"
}

# Función para detener servicios
stop() {
    echo -e "${BLUE}Deteniendo servicios...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Servicios detenidos${NC}"
}

# Función para reiniciar servicios
restart() {
    echo -e "${BLUE}Reiniciando servicios...${NC}"
    docker-compose restart
    echo -e "${GREEN}✓ Servicios reiniciados${NC}"
}

# Función para mostrar logs
logs() {
    if [ -n "$2" ]; then
        docker-compose logs -f "$2"
    else
        docker-compose logs -f
    fi
}

# Función para iniciar solo el backend
backend() {
    echo -e "${BLUE}Iniciando backend y dependencias...${NC}"
    docker-compose up -d mysql redis elasticsearch backend
    echo -e "${GREEN}✓ Backend iniciado en http://localhost:8000${NC}"
}

# Función para iniciar solo el frontend
frontend() {
    echo -e "${BLUE}Iniciando frontend...${NC}"
    docker-compose up -d frontend
    echo -e "${GREEN}✓ Frontend iniciado en http://localhost:3000${NC}"
}

# Función para iniciar solo la base de datos
db() {
    echo -e "${BLUE}Iniciando servicios de base de datos...${NC}"
    docker-compose up -d mysql redis elasticsearch
    echo -e "${GREEN}✓ Base de datos iniciada${NC}"
}

# Función para ejecutar tests
test() {
    echo -e "${BLUE}Ejecutando tests...${NC}"
    
    # Tests del backend
    echo -e "${YELLOW}Ejecutando tests del backend...${NC}"
    docker-compose exec backend python -m pytest tests/ -v
    
    # Tests del frontend
    echo -e "${YELLOW}Ejecutando tests del frontend...${NC}"
    docker-compose exec frontend npm test
    
    echo -e "${GREEN}✓ Tests completados${NC}"
}

# Función para construir para producción
build() {
    echo -e "${BLUE}Construyendo para producción...${NC}"
    
    # Build del frontend
    echo -e "${YELLOW}Construyendo frontend...${NC}"
    docker-compose exec frontend npm run build
    
    # Build del backend (si es necesario)
    echo -e "${YELLOW}Preparando backend...${NC}"
    docker-compose exec backend pip freeze > requirements.txt
    
    echo -e "${GREEN}✓ Build completado${NC}"
}

# Función para limpiar
clean() {
    echo -e "${YELLOW}¿Estás seguro de que quieres limpiar todos los contenedores y volúmenes? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${BLUE}Limpiando contenedores y volúmenes...${NC}"
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo -e "${GREEN}✓ Limpieza completada${NC}"
    else
        echo -e "${YELLOW}Operación cancelada${NC}"
    fi
}

# Función para mostrar estado
status() {
    echo -e "${BLUE}Estado de los servicios:${NC}"
    docker-compose ps
    
    echo -e "\n${BLUE}Uso de recursos:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Función principal
main() {
    case "${1:-help}" in
        setup)
            setup
            ;;
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs "$@"
            ;;
        backend)
            backend
            ;;
        frontend)
            frontend
            ;;
        db)
            db
            ;;
        test)
            test
            ;;
        build)
            build
            ;;
        clean)
            clean
            ;;
        status)
            status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Comando desconocido: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"

