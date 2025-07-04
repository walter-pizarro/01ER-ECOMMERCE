#!/usr/bin/env python3
"""
TIENDAS TRESMAS - Sistema de Carga Masiva de Productos
Implementación real para procesar Excel de productos publicitarios
"""

import pandas as pd
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os

class SistemaCargaMasiva:
    """Sistema completo de carga masiva de productos desde Excel"""
    
    def __init__(self):
        self.productos_cargados = []
        self.errores_carga = []
        self.estadisticas = {
            "total_filas": 0,
            "productos_creados": 0,
            "productos_actualizados": 0,
            "errores": 0
        }
    
    def limpiar_texto(self, texto: str) -> str:
        """Limpiar y normalizar texto"""
        if pd.isna(texto) or texto is None:
            return ""
        
        texto = str(texto).strip()
        # Remover caracteres especiales problemáticos
        texto = re.sub(r'[^\w\s\-\.\,\(\)\[\]\/\&\%\$\#\@\!\?\:\;]', '', texto)
        return texto
    
    def generar_sku(self, codigo_proveedor: str, categoria: str = "") -> str:
        """Generar SKU único basado en código de proveedor"""
        if not codigo_proveedor:
            codigo_proveedor = f"PROD{int(datetime.now().timestamp())}"
        
        # Limpiar código
        codigo_limpio = re.sub(r'[^\w]', '', str(codigo_proveedor).upper())
        
        # Agregar prefijo de categoría si existe
        if categoria:
            cat_prefix = re.sub(r'[^\w]', '', categoria.upper())[:3]
            return f"{cat_prefix}-{codigo_limpio}"
        
        return f"AQTL-{codigo_limpio}"
    
    def calcular_precio_usd(self, precio_clp: float, tasa_cambio: float = 950) -> float:
        """Calcular precio en USD"""
        try:
            return round(precio_clp / tasa_cambio, 2)
        except:
            return 0.0
    
    def calcular_utilidad(self, precio_venta: float, precio_costo: float) -> float:
        """Calcular porcentaje de utilidad"""
        try:
            if precio_costo > 0:
                return round(((precio_venta - precio_costo) / precio_costo) * 100, 2)
            return 0.0
        except:
            return 0.0
    
    def procesar_excel(self, ruta_excel: str, hoja: str = None) -> Dict:
        """Procesar archivo Excel y extraer productos"""
        try:
            # Leer Excel
            if hoja:
                df = pd.read_excel(ruta_excel, sheet_name=hoja)
            else:
                # Leer primera hoja disponible
                excel_file = pd.ExcelFile(ruta_excel)
                hoja = excel_file.sheet_names[0]
                df = pd.read_excel(ruta_excel, sheet_name=hoja)
            
            print(f"📊 Procesando hoja: {hoja}")
            print(f"📋 Filas encontradas: {len(df)}")
            print(f"📋 Columnas: {list(df.columns)}")
            
            self.estadisticas["total_filas"] = len(df)
            
            # Mapear columnas comunes
            mapeo_columnas = self._detectar_columnas(df.columns)
            print(f"🔍 Mapeo de columnas detectado: {mapeo_columnas}")
            
            productos_procesados = []
            
            for index, fila in df.iterrows():
                try:
                    producto = self._procesar_fila(fila, mapeo_columnas, index + 1)
                    if producto:
                        productos_procesados.append(producto)
                        self.estadisticas["productos_creados"] += 1
                    
                except Exception as e:
                    error = {
                        "fila": index + 1,
                        "error": str(e),
                        "datos": dict(fila)
                    }
                    self.errores_carga.append(error)
                    self.estadisticas["errores"] += 1
                    print(f"❌ Error en fila {index + 1}: {str(e)}")
            
            self.productos_cargados = productos_procesados
            
            return {
                "success": True,
                "productos": productos_procesados,
                "estadisticas": self.estadisticas,
                "errores": self.errores_carga,
                "hoja_procesada": hoja
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al procesar Excel: {str(e)}"
            }
    
    def _detectar_columnas(self, columnas: List[str]) -> Dict:
        """Detectar automáticamente qué columnas corresponden a qué campos"""
        mapeo = {}
        
        # Patrones para detectar columnas
        patrones = {
            "nombre": ["nombre", "producto", "descripcion", "title", "name"],
            "categoria": ["categoria", "category", "tipo", "type", "grupo"],
            "subcategoria": ["subcategoria", "subcategory", "subtipo", "subtype"],
            "marca": ["marca", "brand", "fabricante", "manufacturer"],
            "precio_costo": ["costo", "cost", "precio_costo", "precio_compra", "compra"],
            "precio_venta": ["precio", "price", "venta", "sale", "precio_venta", "pvp"],
            "codigo": ["codigo", "code", "sku", "referencia", "ref", "id"],
            "stock": ["stock", "cantidad", "inventory", "existencia"],
            "descripcion": ["descripcion", "description", "detalle", "detail"],
            "imagen": ["imagen", "image", "foto", "photo", "url_imagen"],
            "peso": ["peso", "weight", "kg", "gramos"],
            "dimensiones": ["dimensiones", "dimensions", "medidas", "size", "tamaño"],
            "color": ["color", "colour"],
            "material": ["material", "materials", "composicion"],
            "proveedor": ["proveedor", "supplier", "vendor"]
        }
        
        for campo, palabras_clave in patrones.items():
            for columna in columnas:
                columna_lower = str(columna).lower().strip()
                for palabra in palabras_clave:
                    if palabra in columna_lower:
                        mapeo[campo] = columna
                        break
                if campo in mapeo:
                    break
        
        return mapeo
    
    def _procesar_fila(self, fila: pd.Series, mapeo: Dict, numero_fila: int) -> Optional[Dict]:
        """Procesar una fila individual del Excel"""
        try:
            # Extraer datos básicos
            nombre = self.limpiar_texto(fila.get(mapeo.get("nombre", ""), ""))
            if not nombre:
                # Intentar con la primera columna que tenga texto
                for col in fila.index:
                    valor = self.limpiar_texto(fila[col])
                    if valor and len(valor) > 3:
                        nombre = valor
                        break
            
            if not nombre:
                raise ValueError("No se pudo determinar el nombre del producto")
            
            # Datos básicos
            categoria = self.limpiar_texto(fila.get(mapeo.get("categoria", ""), "Productos Publicitarios"))
            subcategoria = self.limpiar_texto(fila.get(mapeo.get("subcategoria", ""), ""))
            marca = self.limpiar_texto(fila.get(mapeo.get("marca", ""), "AQUI TU LOGO"))
            descripcion = self.limpiar_texto(fila.get(mapeo.get("descripcion", ""), ""))
            
            # Precios
            precio_costo = self._extraer_precio(fila.get(mapeo.get("precio_costo", ""), 0))
            precio_venta = self._extraer_precio(fila.get(mapeo.get("precio_venta", ""), 0))
            
            # Si no hay precio de venta, calcular con margen del 40%
            if precio_venta == 0 and precio_costo > 0:
                precio_venta = precio_costo * 1.4
            
            # Si no hay precio de costo, calcular con margen del 30%
            if precio_costo == 0 and precio_venta > 0:
                precio_costo = precio_venta * 0.7
            
            # Códigos
            codigo_proveedor = self.limpiar_texto(fila.get(mapeo.get("codigo", ""), f"PROD{numero_fila:04d}"))
            sku = self.generar_sku(codigo_proveedor, categoria)
            codigo_tienda = f"AQTL{numero_fila:04d}"
            
            # Stock
            stock = self._extraer_numero(fila.get(mapeo.get("stock", ""), 0))
            
            # Datos adicionales
            imagen_url = self.limpiar_texto(fila.get(mapeo.get("imagen", ""), ""))
            peso = self._extraer_numero(fila.get(mapeo.get("peso", ""), 0))
            dimensiones = self.limpiar_texto(fila.get(mapeo.get("dimensiones", ""), ""))
            color = self.limpiar_texto(fila.get(mapeo.get("color", ""), ""))
            material = self.limpiar_texto(fila.get(mapeo.get("material", ""), ""))
            proveedor = self.limpiar_texto(fila.get(mapeo.get("proveedor", ""), ""))
            
            # Cálculos automáticos
            precio_usd = self.calcular_precio_usd(precio_venta)
            utilidad_porcentaje = self.calcular_utilidad(precio_venta, precio_costo)
            
            # Crear ficha técnica
            ficha_tecnica = {}
            if peso > 0:
                ficha_tecnica["peso"] = f"{peso} kg"
            if dimensiones:
                ficha_tecnica["dimensiones"] = dimensiones
            if color:
                ficha_tecnica["color"] = color
            if material:
                ficha_tecnica["material"] = material
            if proveedor:
                ficha_tecnica["proveedor"] = proveedor
            
            # Agregar todos los datos adicionales de la fila
            for col in fila.index:
                if col not in mapeo.values() and not pd.isna(fila[col]):
                    valor = self.limpiar_texto(fila[col])
                    if valor:
                        ficha_tecnica[str(col).lower().replace(" ", "_")] = valor
            
            producto = {
                "nombre": nombre,
                "categoria": categoria,
                "subcategoria": subcategoria,
                "marca": marca,
                "descripcion": descripcion,
                "precio_costo": precio_costo,
                "precio_venta": precio_venta,
                "precio_usd": precio_usd,
                "utilidad_porcentaje": utilidad_porcentaje,
                "codigo_proveedor": codigo_proveedor,
                "sku": sku,
                "codigo_tienda": codigo_tienda,
                "stock": stock,
                "imagen_url": imagen_url,
                "ficha_tecnica": ficha_tecnica,
                "activo": True,
                "fecha_creacion": datetime.now().isoformat(),
                "origen": "carga_masiva_excel",
                "fila_origen": numero_fila
            }
            
            return producto
            
        except Exception as e:
            raise ValueError(f"Error procesando fila {numero_fila}: {str(e)}")
    
    def _extraer_precio(self, valor) -> float:
        """Extraer precio numérico de un valor"""
        try:
            if pd.isna(valor) or valor is None:
                return 0.0
            
            # Convertir a string y limpiar
            valor_str = str(valor).strip()
            
            # Remover símbolos de moneda y separadores
            valor_limpio = re.sub(r'[^\d\.\,\-]', '', valor_str)
            
            # Manejar separadores decimales
            if ',' in valor_limpio and '.' in valor_limpio:
                # Formato: 1.234,56 o 1,234.56
                if valor_limpio.rfind(',') > valor_limpio.rfind('.'):
                    # Formato europeo: 1.234,56
                    valor_limpio = valor_limpio.replace('.', '').replace(',', '.')
                else:
                    # Formato americano: 1,234.56
                    valor_limpio = valor_limpio.replace(',', '')
            elif ',' in valor_limpio:
                # Solo coma - podría ser decimal o separador de miles
                if len(valor_limpio.split(',')[-1]) <= 2:
                    # Probablemente decimal
                    valor_limpio = valor_limpio.replace(',', '.')
                else:
                    # Probablemente separador de miles
                    valor_limpio = valor_limpio.replace(',', '')
            
            return float(valor_limpio)
            
        except:
            return 0.0
    
    def _extraer_numero(self, valor) -> int:
        """Extraer número entero de un valor"""
        try:
            if pd.isna(valor) or valor is None:
                return 0
            
            valor_str = str(valor).strip()
            numero_limpio = re.sub(r'[^\d\-]', '', valor_str)
            
            return int(numero_limpio) if numero_limpio else 0
            
        except:
            return 0
    
    def exportar_productos_json(self, ruta_salida: str) -> bool:
        """Exportar productos procesados a JSON"""
        try:
            datos_exportacion = {
                "productos": self.productos_cargados,
                "estadisticas": self.estadisticas,
                "errores": self.errores_carga,
                "fecha_exportacion": datetime.now().isoformat()
            }
            
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                json.dump(datos_exportacion, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error al exportar JSON: {str(e)}")
            return False
    
    def obtener_resumen(self) -> Dict:
        """Obtener resumen de la carga masiva"""
        categorias = {}
        marcas = {}
        precio_promedio = 0
        precio_total = 0
        
        for producto in self.productos_cargados:
            # Contar categorías
            cat = producto.get("categoria", "Sin categoría")
            categorias[cat] = categorias.get(cat, 0) + 1
            
            # Contar marcas
            marca = producto.get("marca", "Sin marca")
            marcas[marca] = marcas.get(marca, 0) + 1
            
            # Sumar precios
            precio_total += producto.get("precio_venta", 0)
        
        if self.productos_cargados:
            precio_promedio = precio_total / len(self.productos_cargados)
        
        return {
            "total_productos": len(self.productos_cargados),
            "categorias": categorias,
            "marcas": marcas,
            "precio_promedio": round(precio_promedio, 0),
            "precio_total_inventario": round(precio_total, 0),
            "estadisticas": self.estadisticas,
            "errores_count": len(self.errores_carga)
        }

# Instancia global del sistema de carga masiva
sistema_carga_masiva = SistemaCargaMasiva()

if __name__ == "__main__":
    # Test del sistema
    print("📦 Sistema de Carga Masiva TIENDAS TRESMAS")
    print("✅ Sistema inicializado correctamente")
    
    # Test con archivo de ejemplo
    ruta_excel = "/home/ubuntu/upload/.recovery/TiendaprecargadaPRODUCTOSAQUITULUGOproductospublicitarios2025_V2.xlsx"
    if os.path.exists(ruta_excel):
        print(f"📄 Procesando archivo: {ruta_excel}")
        resultado = sistema_carga_masiva.procesar_excel(ruta_excel)
        if resultado["success"]:
            print(f"✅ Productos procesados: {len(resultado['productos'])}")
            resumen = sistema_carga_masiva.obtener_resumen()
            print(f"📊 Resumen: {resumen}")
        else:
            print(f"❌ Error: {resultado['error']}")
    else:
        print("⚠️ Archivo Excel no encontrado para test")

