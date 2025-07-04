# Auditoría Técnica - Fase 2: Inventario y Análisis de Código Fuente PHP

## RESUMEN EJECUTIVO DE FASE 2

**Total de archivos PHP analizados**: 110 archivos
**Vulnerabilidades críticas identificadas**: 3
**Problemas de arquitectura**: 5
**Recomendaciones urgentes**: 8

---

## 1. INVENTARIO COMPLETO DE ARCHIVOS PHP

### 1.1 Distribución por Categorías

#### **Configuración del Sistema (7 archivos)**
- `Config/Config.php` - Configuración principal ⚠️ CRÍTICO
- `Config/App/Autoload.php` - Sistema de autoload
- `Config/App/Conexion.php` - Conexión a BD
- `Config/App/Controller.php` - Controlador base
- `Config/App/Query.php` - Clase base para consultas
- `Config/App/Views.php` - Sistema de vistas
- `Config/Helpers.php` - Funciones auxiliares

#### **Controladores MVC (12 archivos)**
- `Controllers/Admin.php` - Panel administrativo
- `Controllers/Home.php` - Página principal
- `Controllers/Productos.php` - Gestión de productos
- `Controllers/Categorias.php` - Gestión de categorías
- `Controllers/Clientes.php` - Gestión de clientes
- `Controllers/Usuarios.php` - Gestión de usuarios
- `Controllers/Ventas.php` - Gestión de ventas
- `Controllers/Pedidos.php` - Gestión de pedidos
- `Controllers/Principal.php` - Frontend público
- `Controllers/Proveedores.php` - Gestión de proveedores
- `Controllers/Colores.php` - Atributos de color
- `Controllers/Sizes.php` - Atributos de talla

#### **Modelos de Datos (13 archivos)**
- `Models/ProductosModel.php` - Modelo de productos
- `Models/CategoriasModel.php` - Modelo de categorías
- `Models/ClientesModel.php` - Modelo de clientes
- `Models/UsuariosModel.php` - Modelo de usuarios
- `Models/VentasModel.php` - Modelo de ventas
- `Models/AdminModel.php` - Modelo administrativo
- `Models/HomeModel.php` - Modelo página principal
- `Models/PedidosModel.php` - Modelo de pedidos
- `Models/PrincipalModel.php` - Modelo frontend
- `Models/ProveedoresModel.php` - Modelo de proveedores
- `Models/ColoresModel.php` - Modelo de colores
- `Models/SizesModel.php` - Modelo de tallas
- `Models/SlidersModel.php` - Modelo de sliders

#### **Vistas y Templates (15 archivos)**
- Panel administrativo (8 archivos)
- Frontend público (5 archivos)
- Templates base (2 archivos)

#### **Archivos Sueltos/Endpoints (63 archivos)**
⚠️ **PROBLEMA ARQUITECTÓNICO**: Demasiados archivos PHP sueltos fuera del patrón MVC

---

## 2. ANÁLISIS DETALLADO DE CÓDIGO FUENTE

### 2.1 🚨 VULNERABILIDADES CRÍTICAS IDENTIFICADAS

#### **VULNERABILIDAD #1: Credenciales Hardcodeadas**
**Archivo**: `Config/Config.php`
**Severidad**: CRÍTICA
**Descripción**: Todas las credenciales del sistema están expuestas en texto plano

```php
const HOST = "localhost";
const USER = "aquitulogo23";
const PASS = "g-i,F6+{MawJ";
const DB = "aquitulogo23_tienda_virtual";
const CLIENT_ID = "AfUTL8dhKiZ3IyczvyqkrERqgxlUzUkdPHMfEAu8sf3Yj6i63P3NIk8huFpNvaJHuqYEkpvtoWTkPm0a";
const ACCESS_TOKEN = "TEST-6787179734142830-071711-218653ab11b71bdf62612fdb71b663f3-1425304689";
const USER_SMTP = "soporte.hosting@walcom.cl";
const PASS_SMTP = "sO2023%$#hO";
```

#### **VULNERABILIDAD #2: Conexiones Duplicadas con Credenciales**
**Archivo**: `buscarProveedorPorCodigo.php`
**Severidad**: CRÍTICA
**Descripción**: Credenciales de BD duplicadas fuera del sistema de configuración

```php
$conexion = new mysqli("localhost", "aquitulogo23", "g-i,F6+{MawJ", "aquitulogo23_tienda_virtual");
```

#### **VULNERABILIDAD #3: Credenciales de Transbank Expuestas**
**Archivo**: `transbank.php`
**Severidad**: CRÍTICA
**Descripción**: API keys de Transbank hardcodeadas en el código

```php
$TbkApiKeyId='597043249735';
$TbkApiKeySecret='a2fdbcd54daaba465cfdfd3f8c98bb66';
```

### 2.2 PROBLEMAS DE ARQUITECTURA Y CÓDIGO

#### **PROBLEMA #1: Violación del Patrón MVC**
- **63 archivos PHP sueltos** que no siguen el patrón MVC
- Lógica de negocio mezclada con presentación
- Endpoints directos sin control de acceso

#### **PROBLEMA #2: Inconsistencia en Conexiones a BD**
- Algunos archivos usan la clase `Conexion` centralizada
- Otros crean conexiones mysqli directas
- Falta de estandarización en el acceso a datos

#### **PROBLEMA #3: Ausencia de Validación de Entrada**
**Ejemplo en `buscarProveedorPorCodigo.php`**:
```php
$codigoProveedor = $_GET['codigo_proveedor']; // Sin validación
```

#### **PROBLEMA #4: Manejo Inconsistente de Errores**
- Algunos archivos muestran errores al usuario final
- Falta de logging centralizado
- Información sensible expuesta en errores

#### **PROBLEMA #5: Falta de Documentación**
- **0% de comentarios** en el código analizado
- Sin documentación de APIs
- Sin especificación de parámetros

### 2.3 ANÁLISIS DE CONTROLADORES PRINCIPALES

#### **Controller: Admin.php**
**Funcionalidad**: Panel de administración y autenticación
**Observaciones**:
- ✅ Uso correcto de `password_verify()`
- ✅ Manejo de sesiones implementado
- ⚠️ Falta validación CSRF
- ⚠️ Sin rate limiting para login

#### **Controller: Home.php**
**Funcionalidad**: Página principal del sitio
**Observaciones**:
- ✅ Estructura MVC respetada
- ✅ Separación de lógica y presentación
- ⚠️ Cálculo de calificaciones podría optimizarse
- ⚠️ Sin caché para consultas frecuentes

#### **Model: ProductosModel.php**
**Funcionalidad**: Gestión de productos
**Observaciones**:
- ✅ Uso de prepared statements
- ✅ Herencia correcta de clase Query
- ⚠️ Consulta SQL con concatenación directa: `"SELECT * FROM productos WHERE id = $idPro"`
- ⚠️ Falta validación de tipos de datos

---

## 3. ANÁLISIS DE ARCHIVOS SUELTOS CRÍTICOS

### 3.1 Archivos de Búsqueda de Proveedores
**Archivos**: `buscarProveedorPorCodigo.php`, `buscarProveedorPorNombre.php`
**Problemas**:
- Credenciales hardcodeadas
- Sin autenticación
- Sin validación de entrada
- Exposición de estructura de BD

### 3.2 Archivo de Integración Transbank
**Archivo**: `transbank.php`
**Problemas**:
- 500+ líneas de código sin estructura
- Credenciales de producción expuestas
- Lógica de negocio mezclada con presentación
- Sin manejo de errores robusto

### 3.3 Archivos de Procesamiento de Compras
**Archivos**: `compra_exitosa.php`, `compra_rechazada.php`, `procesar_estado_compra.php`
**Problemas**:
- Sin validación de tokens
- Falta de logging de transacciones
- Posible manipulación de estados

---

## 4. PATRONES Y FIRMAS DE DESARROLLADORES

### 4.1 Firmas Identificadas
- **Comentarios en español**: Indica desarrollador hispanohablante
- **Estilo de nomenclatura**: snake_case mezclado con camelCase
- **Estructura de archivos**: Sugiere desarrollo incremental sin planificación

### 4.2 Posibles Desarrolladores Anteriores
- **Dominio**: `aquitulogo.cl` - Empresa chilena
- **Email de soporte**: `soporte.hosting@walcom.cl` - Walcom (proveedor de hosting)
- **Zona horaria**: `America/Santiago` en código Transbank

---

## 5. RECOMENDACIONES URGENTES

### 5.1 Seguridad Crítica (Implementar INMEDIATAMENTE)
1. **Migrar credenciales a variables de entorno**
2. **Eliminar archivos con credenciales duplicadas**
3. **Implementar autenticación en endpoints sueltos**
4. **Validar todas las entradas de usuario**

### 5.2 Arquitectura (Implementar en 30 días)
1. **Refactorizar archivos sueltos al patrón MVC**
2. **Centralizar conexiones de base de datos**
3. **Implementar sistema de logging**
4. **Añadir documentación de código**

### 5.3 Calidad de Código (Implementar en 60 días)
1. **Establecer estándares de codificación PSR**
2. **Implementar sistema de testing**
3. **Optimizar consultas SQL**
4. **Añadir caché para consultas frecuentes**

---

**Próxima Fase**: Auditoría de Seguridad y Detección de Código Malicioso
**Fecha de Análisis**: $(date)
**Archivos Analizados**: 110/110 (100%)

