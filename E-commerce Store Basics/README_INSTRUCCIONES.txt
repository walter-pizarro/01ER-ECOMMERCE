
🔧 PASO A PASO DE INSTALACIÓN DEL MÓDULO DE CARGA MASIVA DE IMÁGENES

1. Subir la carpeta completa al directorio raíz de tu tienda (ejemplo: /public_html/tienda/)
2. Asegúrate de tener las carpetas:
   - /imagenes_por_validar/
   - /imagenes_productos/
   Estas se usan para cargar y mover imágenes.

3. Base de datos:
   - Asegúrate de tener una tabla `productos` con al menos campos:
     `sku VARCHAR`, `nombre VARCHAR`, `imagen VARCHAR`
   - (Opcional) Para múltiples imágenes por producto, crear tabla:
     CREATE TABLE producto_imagenes (
         id INT AUTO_INCREMENT PRIMARY KEY,
         sku VARCHAR(50),
         ruta_imagen VARCHAR(255),
         orden INT DEFAULT 1
     );

4. Abre el archivo `validador_imagenes_producto.php` en el navegador
   Ejemplo: https://tudominio.cl/tienda/validador_imagenes_producto.php

5. Sube imágenes arrastrando al recuadro o colócalas manualmente en /imagenes_por_validar/

6. El sistema detecta automáticamente coincidencias con SKU y permite asociarlas visualmente.

7. Al hacer clic en "Subir imágenes seleccionadas", se moverán y asociarán en la BD.

🧠 Recomendación: proteger estos archivos con login de administrador.
