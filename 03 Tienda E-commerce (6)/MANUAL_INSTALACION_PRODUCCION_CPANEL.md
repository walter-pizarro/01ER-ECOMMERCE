# 📋 MANUAL DE INSTALACIÓN EN PRODUCCIÓN
## eCommerce Moderno - Servidor cPanel/WHM

### 🎯 **INFORMACIÓN DEL SERVIDOR ANALIZADO**

**Servidor**: cPanel 118.0.46 con WHM (Hosting Compartido Profesional)  
**Dominio**: aquitumarca.com  
**Proveedor**: WALCOM  
**Panel**: cPanel con herramientas avanzadas  
**IP Compartida**: 199.250.192.72  
**Directorio Principal**: /home/marcdogo  

---

## 📊 **CARACTERÍSTICAS MÍNIMAS DEL SERVIDOR**

### ✅ **REQUISITOS VERIFICADOS EN TU SERVIDOR**

**Hardware Mínimo:**
- ✅ **CPU**: 0/100 (0%) - Suficiente para eCommerce
- ✅ **RAM**: 1 GB disponible - Adecuado
- ✅ **Disco**: 1.95 GB disponibles - Suficiente para inicio
- ✅ **Ancho de Banda**: 11.27 MB / 9.77 GB - Excelente

**Software Disponible:**
- ✅ **PHP**: Múltiples versiones (7.4, 8.0, 8.1, 8.2)
- ✅ **MySQL**: Bases de datos disponibles
- ✅ **Node.js**: Disponible para aplicaciones
- ✅ **Python**: Disponible para backend
- ✅ **SSL/TLS**: Certificados disponibles
- ✅ **WordPress**: Para landing page

**Herramientas cPanel:**
- ✅ **Administrador de archivos** completo
- ✅ **Bases de datos MySQL** y PostgreSQL
- ✅ **Gestión de dominios** y subdominios
- ✅ **Correo electrónico** configurado
- ✅ **Backup automático** disponible

---

## 🏗️ **ARQUITECTURA DE INSTALACIÓN RECOMENDADA**

### 📁 **ESTRUCTURA DE DIRECTORIOS**

```
/home/marcdogo/
├── public_html/                    # Landing page (WordPress)
│   ├── index.php                   # Página principal
│   └── wp-content/                 # Contenido WordPress
├── ecommerce/                      # Aplicación eCommerce
│   ├── frontend/                   # Frontend React/HTML
│   ├── backend/                    # Backend Python/PHP
│   └── assets/                     # Recursos estáticos
├── subdomains/
│   ├── tienda.aquitumarca.com/     # Subdominio para tienda
│   └── admin.aquitumarca.com/      # Panel administrativo
└── databases/                      # Configuraciones DB
```

---

## 🚀 **INSTALACIÓN PASO A PASO**

### **FASE 1: PREPARACIÓN DEL SERVIDOR**

#### **Paso 1.1: Configurar PHP**
1. **Acceder a cPanel** → **Software** → **Administrador MultiPHP**
2. **Seleccionar PHP 8.1** para mejor rendimiento
3. **Habilitar extensiones necesarias:**
   - `mysqli` (para MySQL)
   - `curl` (para APIs)
   - `json` (para datos)
   - `mbstring` (para caracteres especiales)
   - `zip` (para archivos)

#### **Paso 1.2: Crear Base de Datos**
1. **cPanel** → **Bases de datos** → **Bases de datos MySQL**
2. **Crear nueva base de datos:**
   - Nombre: `marcdogo_ecommerce`
3. **Crear usuario:**
   - Usuario: `marcdogo_ecom`
   - Contraseña: `[GENERAR_SEGURA]`
4. **Asignar privilegios completos** al usuario

#### **Paso 1.3: Configurar SSL**
1. **cPanel** → **Seguridad** → **SSL/TLS Status**
2. **Activar SSL** para:
   - `aquitumarca.com`
   - `www.aquitumarca.com`
   - `tienda.aquitumarca.com` (si se usa)

---

### **FASE 2: INSTALACIÓN DEL LANDING PAGE**

#### **Paso 2.1: Instalar WordPress**
1. **cPanel** → **Scripts** → **WordPress**
2. **Configurar instalación:**
   - Directorio: `public_html/`
   - Dominio: `aquitumarca.com`
   - Título: "AQUITUMARCA - Tu Tienda Online"
   - Admin: `admin`
   - Email: `admin@aquitumarca.com`

#### **Paso 2.2: Configurar Landing Page**
1. **Instalar tema eCommerce** (Astra, Storefront, etc.)
2. **Crear páginas principales:**
   - Inicio (Landing page atractivo)
   - Sobre Nosotros
   - Contacto
   - Acceso a Tienda (botón prominente)
3. **Configurar menú** con enlace a tienda

---

### **FASE 3: INSTALACIÓN DEL ECOMMERCE**

#### **Paso 3.1: Subir Archivos del eCommerce**

**Opción A: Subdominio (Recomendado)**
1. **cPanel** → **Dominios** → **Subdominios**
2. **Crear subdominio:** `tienda.aquitumarca.com`
3. **Directorio:** `/home/marcdogo/public_html/tienda/`

**Opción B: Directorio**
1. **Usar directorio:** `/home/marcdogo/public_html/tienda/`
2. **URL de acceso:** `aquitumarca.com/tienda`

#### **Paso 3.2: Subir Archivos Frontend**
1. **Acceder a Administrador de archivos**
2. **Navegar a directorio de tienda**
3. **Subir archivos del frontend:**
   ```
   /tienda/
   ├── index.html              # Frontend demo
   ├── assets/
   │   ├── css/
   │   ├── js/
   │   └── images/
   └── api/                     # Backend PHP
       ├── config.php
       ├── products.php
       ├── auth.php
       └── database.php
   ```

#### **Paso 3.3: Configurar Backend**

**Crear archivo `config.php`:**
```php
<?php
// Configuración de base de datos
define('DB_HOST', 'localhost');
define('DB_NAME', 'marcdogo_ecommerce');
define('DB_USER', 'marcdogo_ecom');
define('DB_PASS', '[TU_PASSWORD]');

// Configuración del sitio
define('SITE_URL', 'https://aquitumarca.com/tienda');
define('API_URL', 'https://aquitumarca.com/tienda/api');

// Configuración de seguridad
define('JWT_SECRET', '[GENERAR_CLAVE_SECRETA]');
define('ENCRYPTION_KEY', '[GENERAR_CLAVE_ENCRIPTACION]');

// Configuración de correo
define('SMTP_HOST', 'mail.aquitumarca.com');
define('SMTP_USER', 'noreply@aquitumarca.com');
define('SMTP_PASS', '[PASSWORD_EMAIL]');
?>
```

---

### **FASE 4: CONFIGURACIÓN DE BASE DE DATOS**

#### **Paso 4.1: Importar Esquema**
1. **cPanel** → **Bases de datos** → **phpMyAdmin**
2. **Seleccionar base de datos** `marcdogo_ecommerce`
3. **Importar archivo SQL** con estructura de tablas
4. **Ejecutar script de datos de prueba**

#### **Paso 4.2: Verificar Conexión**
1. **Crear archivo de prueba** `test_db.php`:
```php
<?php
include 'config.php';
try {
    $pdo = new PDO("mysql:host=".DB_HOST.";dbname=".DB_NAME, DB_USER, DB_PASS);
    echo "✅ Conexión exitosa a la base de datos";
} catch(PDOException $e) {
    echo "❌ Error: " . $e->getMessage();
}
?>
```

---

### **FASE 5: CONFIGURACIÓN DE SEGURIDAD**

#### **Paso 5.1: Proteger Archivos Sensibles**
**Crear archivo `.htaccess` en `/tienda/`:**
```apache
# Protección general
Options -Indexes
ServerSignature Off

# Proteger archivos de configuración
<Files "config.php">
    Order Allow,Deny
    Deny from all
</Files>

# Habilitar HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Protección contra ataques
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
</IfModule>
```

#### **Paso 5.2: Configurar Permisos**
1. **Directorios**: 755
2. **Archivos PHP**: 644
3. **Archivos de configuración**: 600
4. **Directorio de uploads**: 755

---

### **FASE 6: TESTING Y VERIFICACIÓN**

#### **Paso 6.1: Verificar Frontend**
1. **Acceder a:** `https://aquitumarca.com/tienda/`
2. **Verificar:**
   - ✅ Página carga correctamente
   - ✅ CSS y JS funcionan
   - ✅ Productos se muestran
   - ✅ Búsqueda funciona

#### **Paso 6.2: Verificar Backend**
1. **Probar endpoints:**
   - `GET /api/products.php` - Lista productos
   - `POST /api/auth.php` - Login
   - `GET /api/health.php` - Estado del sistema

#### **Paso 6.3: Verificar Integración**
1. **Login de usuario**
2. **Agregar productos al carrito**
3. **Proceso de checkout**
4. **Panel administrativo**

---

## 🔧 **CONFIGURACIONES ADICIONALES**

### **Optimización de Performance**

#### **Paso 7.1: Configurar Cache**
**En `.htaccess` agregar:**
```apache
# Cache de archivos estáticos
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
</IfModule>

# Compresión GZIP
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>
```

#### **Paso 7.2: Optimizar Base de Datos**
1. **Crear índices** en tablas principales
2. **Configurar cache de consultas**
3. **Optimizar consultas frecuentes**

---

### **Configuración de Correo Electrónico**

#### **Paso 8.1: Crear Cuentas de Correo**
1. **cPanel** → **Correo electrónico** → **Cuentas de correo**
2. **Crear cuentas:**
   - `noreply@aquitumarca.com` (notificaciones)
   - `admin@aquitumarca.com` (administración)
   - `ventas@aquitumarca.com` (pedidos)

#### **Paso 8.2: Configurar SMTP**
```php
// En config.php
define('MAIL_CONFIG', [
    'host' => 'mail.aquitumarca.com',
    'port' => 587,
    'encryption' => 'tls',
    'username' => 'noreply@aquitumarca.com',
    'password' => '[PASSWORD]',
    'from_email' => 'noreply@aquitumarca.com',
    'from_name' => 'AQUITUMARCA Tienda'
]);
```

---

## 🚨 **BACKUP Y MANTENIMIENTO**

### **Configurar Backups Automáticos**

#### **Paso 9.1: Backup de Archivos**
1. **cPanel** → **Archivos** → **Backup**
2. **Configurar backup automático:**
   - Frecuencia: Diario
   - Retención: 7 días
   - Incluir: Archivos y bases de datos

#### **Paso 9.2: Backup de Base de Datos**
**Crear script de backup automático:**
```bash
#!/bin/bash
# backup_db.sh
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u marcdogo_ecom -p[PASSWORD] marcdogo_ecommerce > backup_$DATE.sql
```

---

## 📊 **MONITOREO Y LOGS**

### **Configurar Monitoreo**

#### **Paso 10.1: Logs de Errores**
1. **Habilitar logs de PHP** en `.htaccess`:
```apache
php_flag log_errors on
php_value error_log /home/marcdogo/logs/php_errors.log
```

#### **Paso 10.2: Monitoreo de Performance**
1. **Instalar herramientas de monitoreo**
2. **Configurar alertas** para:
   - Uso de CPU > 80%
   - Uso de memoria > 90%
   - Errores de base de datos
   - Tiempo de respuesta > 3s

---

## 🎯 **CONFIGURACIÓN FINAL**

### **Paso 11: Configurar Landing Page**

#### **Integración WordPress → eCommerce**
1. **Editar página de inicio** en WordPress
2. **Agregar botón prominente:**
   ```html
   <a href="https://aquitumarca.com/tienda/" 
      class="btn-tienda">
      🛍️ ACCEDER A LA TIENDA
   </a>
   ```
3. **Configurar menú** con enlace directo
4. **Agregar widgets** de productos destacados

---

## ✅ **CHECKLIST DE VERIFICACIÓN FINAL**

### **Funcionalidades Básicas**
- [ ] Landing page carga correctamente
- [ ] Enlace a tienda funciona
- [ ] Frontend de tienda se muestra
- [ ] Productos se cargan desde BD
- [ ] Búsqueda funciona
- [ ] Login/logout operativo
- [ ] Carrito de compras funciona
- [ ] Panel admin accesible

### **Seguridad**
- [ ] SSL configurado y funcionando
- [ ] Archivos sensibles protegidos
- [ ] Permisos correctos asignados
- [ ] Backup automático configurado
- [ ] Logs de errores habilitados

### **Performance**
- [ ] Cache configurado
- [ ] Compresión GZIP activa
- [ ] Imágenes optimizadas
- [ ] Base de datos optimizada
- [ ] Tiempo de carga < 3 segundos

---

## 🆘 **SOLUCIÓN DE PROBLEMAS COMUNES**

### **Error de Conexión a BD**
```
Error: SQLSTATE[HY000] [2002] Connection refused
```
**Solución:**
1. Verificar credenciales en `config.php`
2. Confirmar que la BD existe
3. Verificar permisos del usuario

### **Error 500 Internal Server**
**Solución:**
1. Revisar logs de errores PHP
2. Verificar permisos de archivos
3. Comprobar sintaxis PHP

### **Problemas de SSL**
**Solución:**
1. Verificar certificado en cPanel
2. Forzar HTTPS en `.htaccess`
3. Actualizar URLs en configuración

---

## 📞 **SOPORTE POST-INSTALACIÓN**

### **Recursos de Ayuda**
- **Documentación cPanel**: Disponible en panel
- **Logs del sistema**: `/home/marcdogo/logs/`
- **Backup automático**: Configurado en cPanel
- **Monitoreo**: Métricas disponibles en panel

### **Mantenimiento Recomendado**
- **Semanal**: Revisar logs de errores
- **Mensual**: Actualizar plugins y sistema
- **Trimestral**: Optimizar base de datos
- **Anual**: Renovar certificados SSL

---

**🎉 ¡INSTALACIÓN COMPLETADA!**

Tu eCommerce Moderno estará operativo en:
- **Landing Page**: `https://aquitumarca.com`
- **Tienda Online**: `https://aquitumarca.com/tienda`
- **Panel Admin**: `https://aquitumarca.com/tienda/admin`

**El sistema está listo para recibir tus primeros clientes y generar ventas desde el día 1.**

