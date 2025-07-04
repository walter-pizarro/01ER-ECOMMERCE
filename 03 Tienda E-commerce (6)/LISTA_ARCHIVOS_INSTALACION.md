# 📦 PAQUETE DE ARCHIVOS PARA INSTALACIÓN
## eCommerce Moderno - Servidor cPanel

### 🎯 **ARCHIVOS NECESARIOS PARA LA INSTALACIÓN**

Este documento lista todos los archivos que necesitas subir a tu servidor cPanel para completar la instalación del eCommerce Moderno.

---

## 📁 **ESTRUCTURA DE ARCHIVOS A SUBIR**

### **1. FRONTEND (Directorio: `/public_html/tienda/`)**

#### **Archivo Principal:**
- `index.html` - Frontend demo completo
- `frontend_demo.html` - Versión alternativa

#### **Directorio Assets:**
```
/assets/
├── css/
│   └── tailwind.min.css
├── js/
│   ├── app.js
│   └── api.js
└── images/
    ├── logo.png
    └── productos/
```

### **2. BACKEND API (Directorio: `/public_html/tienda/api/`)**

#### **Archivos PHP Principales:**
- `config.php` - Configuración de base de datos
- `database.php` - Conexión y funciones DB
- `products.php` - API de productos
- `auth.php` - Autenticación de usuarios
- `search.php` - Búsqueda de productos
- `cart.php` - Gestión de carrito
- `orders.php` - Gestión de pedidos
- `health.php` - Health check del sistema

#### **Archivos de Configuración:**
- `.htaccess` - Configuración Apache
- `cors.php` - Configuración CORS

### **3. BASE DE DATOS**

#### **Scripts SQL:**
- `database_schema.sql` - Estructura de tablas
- `seed_data.sql` - Datos de demostración
- `indexes.sql` - Índices para optimización

### **4. CONFIGURACIÓN**

#### **Archivos de Configuración:**
- `config.example.php` - Plantilla de configuración
- `.env.example` - Variables de entorno
- `backup_script.sh` - Script de backup

---

## 🔧 **ARCHIVOS DE CONFIGURACIÓN ESPECÍFICOS**

### **config.php (Personalizado para tu servidor)**
```php
<?php
// Configuración específica para aquitumarca.com
define('DB_HOST', 'localhost');
define('DB_NAME', 'marcdogo_ecommerce');
define('DB_USER', 'marcdogo_ecom');
define('DB_PASS', '[TU_PASSWORD_AQUI]');

// URLs específicas
define('SITE_URL', 'https://aquitumarca.com/tienda');
define('API_URL', 'https://aquitumarca.com/tienda/api');

// Configuración de correo para aquitumarca.com
define('SMTP_HOST', 'mail.aquitumarca.com');
define('SMTP_USER', 'noreply@aquitumarca.com');
define('SMTP_PASS', '[PASSWORD_EMAIL]');

// Claves de seguridad (GENERAR NUEVAS)
define('JWT_SECRET', 'tu_clave_jwt_secreta_aqui');
define('ENCRYPTION_KEY', 'tu_clave_encriptacion_aqui');
?>
```

### **.htaccess (Optimizado para cPanel)**
```apache
# Configuración específica para cPanel/Apache
Options -Indexes
ServerSignature Off

# Protección de archivos sensibles
<Files "config.php">
    Order Allow,Deny
    Deny from all
</Files>

<Files "*.sql">
    Order Allow,Deny
    Deny from all
</Files>

# Redirección HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Headers de seguridad
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
</IfModule>

# Cache para performance
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
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/json
</IfModule>
```

---

## 📋 **CHECKLIST DE ARCHIVOS A SUBIR**

### **Paso 1: Preparar Archivos Localmente**
- [ ] Descargar todos los archivos del proyecto
- [ ] Personalizar `config.php` con datos de tu servidor
- [ ] Generar claves de seguridad únicas
- [ ] Verificar que todos los archivos estén presentes

### **Paso 2: Subir Frontend**
- [ ] Subir `index.html` a `/public_html/tienda/`
- [ ] Subir carpeta `assets/` completa
- [ ] Verificar permisos (755 para directorios, 644 para archivos)

### **Paso 3: Subir Backend**
- [ ] Crear directorio `/public_html/tienda/api/`
- [ ] Subir todos los archivos PHP
- [ ] Subir `.htaccess` configurado
- [ ] Establecer permisos 600 para `config.php`

### **Paso 4: Configurar Base de Datos**
- [ ] Crear base de datos en cPanel
- [ ] Importar `database_schema.sql`
- [ ] Importar `seed_data.sql`
- [ ] Ejecutar `indexes.sql`

---

## 🚀 **PROCESO DE SUBIDA RECOMENDADO**

### **Método 1: Administrador de Archivos cPanel**
1. **Acceder a cPanel** → **Administrador de archivos**
2. **Navegar a** `/public_html/`
3. **Crear directorio** `tienda`
4. **Subir archivos** uno por uno o en ZIP
5. **Extraer ZIP** si es necesario
6. **Configurar permisos** correctos

### **Método 2: FTP/SFTP**
1. **Usar cliente FTP** (FileZilla, WinSCP)
2. **Conectar con credenciales** de cPanel
3. **Subir estructura completa** de directorios
4. **Verificar integridad** de archivos

### **Método 3: Git (Si disponible)**
1. **Clonar repositorio** en servidor
2. **Configurar archivos** específicos
3. **Establecer permisos** correctos

---

## ⚙️ **CONFIGURACIONES POST-SUBIDA**

### **Verificar Funcionamiento**
1. **Acceder a:** `https://aquitumarca.com/tienda/`
2. **Probar API:** `https://aquitumarca.com/tienda/api/health.php`
3. **Verificar base de datos:** Login con credenciales de prueba

### **Optimizar Performance**
1. **Verificar cache** funcionando
2. **Comprobar compresión** GZIP
3. **Testear velocidad** de carga

### **Configurar Seguridad**
1. **Verificar SSL** activo
2. **Comprobar headers** de seguridad
3. **Testear protección** de archivos

---

## 📞 **SOPORTE DURANTE INSTALACIÓN**

### **Problemas Comunes y Soluciones**

#### **Error: "No se puede conectar a la base de datos"**
- Verificar credenciales en `config.php`
- Confirmar que la base de datos existe
- Revisar permisos del usuario de BD

#### **Error 500: Internal Server Error**
- Revisar logs de errores en cPanel
- Verificar permisos de archivos
- Comprobar sintaxis PHP

#### **Archivos no se muestran**
- Verificar estructura de directorios
- Comprobar permisos (755/644)
- Revisar configuración de .htaccess

### **Herramientas de Diagnóstico**
- **Error Logs**: cPanel → Métricas → Errores
- **File Manager**: Para verificar archivos
- **phpMyAdmin**: Para verificar base de datos

---

## 🎯 **RESULTADO FINAL ESPERADO**

Una vez completada la instalación tendrás:

### **URLs Operativas:**
- **Landing Page**: `https://aquitumarca.com`
- **Tienda Online**: `https://aquitumarca.com/tienda`
- **API Backend**: `https://aquitumarca.com/tienda/api`

### **Funcionalidades Activas:**
- ✅ Catálogo de productos completo
- ✅ Sistema de búsqueda y filtros
- ✅ Carrito de compras funcional
- ✅ Autenticación de usuarios
- ✅ Panel administrativo básico
- ✅ API REST completamente operativa

### **Credenciales de Acceso:**
- **Admin**: admin@ecommerce.com / admin123
- **Cliente**: juan.perez@email.com / user123

**¡Tu eCommerce Moderno estará listo para recibir los primeros clientes!**

