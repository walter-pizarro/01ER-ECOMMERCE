#!/usr/bin/env python3
"""
Cargador de productos completos AQUI TU LOGO al backend de TIENDAS TRESMAS
Incorpora toda la estructura detallada del archivo Excel
"""

import pandas as pd
import requests
import json
from datetime import datetime
import time

# Configuración del backend
BACKEND_URL = "https://5001-itaxf259u4v3bpr2jse0c-a616a0fd.manusvm.computer"
LOGIN_URL = f"{BACKEND_URL}/admin/login"
PRODUCTOS_URL = f"{BACKEND_URL}/admin/productos"

# Credenciales
CREDENTIALS = {
    "email": "admin@tresmas.cl",
    "password": "tresmas2025"
}

def login_backend():
    """Hacer login al backend y obtener token"""
    print("🔐 Iniciando sesión en el backend...")
    
    try:
        response = requests.post(LOGIN_URL, json=CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data.get('token')
                print("✅ Login exitoso")
                return token
            else:
                print(f"❌ Error en login: {data.get('message')}")
                return None
        else:
            print(f"❌ Error HTTP en login: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión en login: {e}")
        return None

def limpiar_valor(valor):
    """Limpiar y normalizar valores del Excel"""
    if pd.isna(valor) or valor == "" or str(valor).strip() == "":
        return None
    
    valor_str = str(valor).strip()
    if valor_str.lower() in ['nan', 'none', 'null']:
        return None
    
    return valor_str

def convertir_precio(precio_str):
    """Convertir string de precio a número"""
    if not precio_str:
        return 0
    
    try:
        # Remover caracteres no numéricos excepto punto y coma
        precio_limpio = str(precio_str).replace(',', '').replace('$', '').strip()
        return float(precio_limpio) if precio_limpio else 0
    except:
        return 0

def procesar_producto(row):
    """Procesar una fila del Excel y convertirla a formato del backend"""
    
    # Campos básicos obligatorios
    nombre = limpiar_valor(row.get('nombre', ''))
    if not nombre:
        return None
    
    categoria = limpiar_valor(row.get('CATEGORIAS', ''))
    if categoria:
        categoria = categoria.replace('\n', '').replace('\t', '').strip()
    
    # Precios
    costo_str = limpiar_valor(row.get('Costo neto proveedor ', ''))
    precio_venta_str = limpiar_valor(row.get('PRECIO VENTA CLP', ''))
    
    costo = convertir_precio(costo_str)
    precio_venta = convertir_precio(precio_venta_str)
    
    # Si no hay precios válidos, usar valores por defecto
    if costo <= 0:
        costo = 1000  # Precio por defecto
    if precio_venta <= 0:
        precio_venta = costo * 2  # 100% de utilidad por defecto
    
    # Construir producto completo
    producto = {
        # Campos básicos
        "nombre": nombre,
        "categoria": categoria or "PRODUCTOS PUBLICITARIOS",
        "subcategoria": limpiar_valor(row.get('Tipo', '')),
        "marca": "AQUI TU LOGO",
        "precio_costo": costo,
        "precio_venta": precio_venta,
        "stock": 0,  # Stock inicial en 0
        
        # Códigos y referencias
        "codigo_proveedor": limpiar_valor(row.get('Código proveedor', '')),
        "sku_original": limpiar_valor(row.get('sku', '')),
        "slug": limpiar_valor(row.get('slug', '')),
        
        # Descripciones
        "descripcion": limpiar_valor(row.get('Descripción / descripción larga\t', '')),
        "descripcion_corta": limpiar_valor(row.get('Características / descripción corta\t', '')),
        "ficha_tecnica": limpiar_valor(row.get('FICHA TÉCNICA\t', '')),
        
        # Especificaciones técnicas
        "tamaño": limpiar_valor(row.get('Tamaño', '')),
        "largo": limpiar_valor(row.get('Largo ', '')),
        "ancho": limpiar_valor(row.get('Ancho ', '')),
        "alto": limpiar_valor(row.get('Alto', '')),
        "diametro": limpiar_valor(row.get('Diámetro', '')),
        "peso": limpiar_valor(row.get('Peso', '')),
        "material": limpiar_valor(row.get('Material', '')),
        "colores": limpiar_valor(row.get('Colores', '')),
        "capacidad": limpiar_valor(row.get('Capacidad', '')),
        "talla": limpiar_valor(row.get('Talla', '')),
        
        # Información de impresión
        "sugerencia_impresion": limpiar_valor(row.get('Sugerencia De Impresión', '')),
        "area_imprimible": limpiar_valor(row.get('Área Imprimible', '')),
        
        # Presentación y accesorios
        "presentacion": limpiar_valor(row.get('Presentación', '')),
        "accesorios": limpiar_valor(row.get('Accesorios', '')),
        "unidad_venta": limpiar_valor(row.get('Unidad De Venta', '')),
        
        # Información adicional
        "pais_origen": limpiar_valor(row.get('País De Origen', '')),
        "garantia": limpiar_valor(row.get('Detalle De La Garantía', '')),
        "otros": limpiar_valor(row.get('Otros', '')),
        
        # URLs de imágenes
        "imagen_url": limpiar_valor(row.get('Url imagen proveedor', '')),
        "imagen_producto_url": limpiar_valor(row.get('Url imagen Producto\t', '')),
        "imagen_referencia_url": limpiar_valor(row.get('Url imagen pequeña de referencia ', ''))
    }
    
    return producto

def cargar_productos_al_backend(archivo_excel, token, limite=None):
    """Cargar productos del Excel al backend"""
    
    print(f"📊 Cargando productos desde: {archivo_excel}")
    
    try:
        # Leer Excel
        df = pd.read_excel(archivo_excel, sheet_name='Plantilla Datos Recolectados', dtype=str)
        print(f"📏 Total de filas en Excel: {len(df)}")
        
        # Aplicar límite si se especifica
        if limite:
            df = df.head(limite)
            print(f"🔢 Limitando a {limite} productos para prueba")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        productos_exitosos = 0
        productos_fallidos = 0
        errores = []
        
        print(f"\n🚀 Iniciando carga de {len(df)} productos...")
        
        for index, row in df.iterrows():
            try:
                producto = procesar_producto(row)
                
                if not producto:
                    print(f"⚠️  Fila {index + 1}: Producto sin nombre válido, omitiendo")
                    productos_fallidos += 1
                    continue
                
                # Enviar al backend
                response = requests.post(PRODUCTOS_URL, json=producto, headers=headers)
                
                if response.status_code in [200, 201]:  # Aceptar tanto 200 como 201
                    productos_exitosos += 1
                    if productos_exitosos % 50 == 0:  # Mostrar progreso cada 50 productos
                        print(f"✅ Progreso: {productos_exitosos} productos cargados...")
                else:
                    productos_fallidos += 1
                    error_msg = f"Fila {index + 1} ({producto['nombre']}): HTTP {response.status_code}"
                    errores.append(error_msg)
                    
                    if productos_fallidos <= 10:  # Mostrar solo los primeros 10 errores
                        print(f"❌ {error_msg}")
                
                # Pausa pequeña para no sobrecargar el servidor
                time.sleep(0.1)
                
            except Exception as e:
                productos_fallidos += 1
                error_msg = f"Fila {index + 1}: Error de procesamiento - {str(e)}"
                errores.append(error_msg)
                
                if productos_fallidos <= 10:
                    print(f"❌ {error_msg}")
        
        # Resumen final
        print(f"\n📊 RESUMEN DE CARGA:")
        print(f"✅ Productos exitosos: {productos_exitosos}")
        print(f"❌ Productos fallidos: {productos_fallidos}")
        print(f"📈 Tasa de éxito: {(productos_exitosos/(productos_exitosos+productos_fallidos)*100):.1f}%")
        
        if errores and len(errores) > 10:
            print(f"⚠️  Se omitieron {len(errores) - 10} errores adicionales")
        
        return productos_exitosos, productos_fallidos, errores
        
    except Exception as e:
        print(f"❌ Error al procesar archivo Excel: {e}")
        return 0, 0, [str(e)]

def main():
    """Función principal"""
    print("🛍️  CARGADOR DE PRODUCTOS AQUI TU LOGO")
    print("=" * 60)
    
    # Archivo Excel
    archivo_excel = "/home/ubuntu/upload/.recovery/TiendaprecargadaPRODUCTOSAQUITULUGOproductospublicitarios2025_V2.xlsx"
    
    # Login
    token = login_backend()
    if not token:
        print("❌ No se pudo obtener token de autenticación")
        return
    
    # Cargar productos (limitamos a 100 para prueba inicial)
    exitosos, fallidos, errores = cargar_productos_al_backend(archivo_excel, token, limite=100)
    
    # Guardar log de errores si hay
    if errores:
        with open("/home/ubuntu/errores_carga_productos.log", "w", encoding="utf-8") as f:
            f.write(f"Log de errores - {datetime.now()}\n")
            f.write("=" * 50 + "\n")
            for error in errores:
                f.write(f"{error}\n")
        
        print(f"\n📝 Log de errores guardado en: /home/ubuntu/errores_carga_productos.log")
    
    print(f"\n✅ Proceso completado. {exitosos} productos cargados exitosamente.")

if __name__ == "__main__":
    main()

