#!/usr/bin/env python3
"""
Analizador del archivo Excel de productos AQUI TU LOGO
Extrae toda la información de productos, categorías y especificaciones
"""

import pandas as pd
import json
from datetime import datetime
import numpy as np

def analizar_productos_excel(archivo_path):
    """Analiza el archivo Excel y extrae toda la información de productos"""
    
    print("🔍 ANALIZANDO ARCHIVO DE PRODUCTOS AQUI TU LOGO")
    print("=" * 60)
    
    try:
        # Leer el archivo Excel
        print(f"📁 Archivo: {archivo_path}")
        
        # Obtener todas las hojas del archivo
        excel_file = pd.ExcelFile(archivo_path)
        print(f"📊 Hojas encontradas: {excel_file.sheet_names}")
        
        resultados = {
            "archivo": archivo_path,
            "fecha_analisis": datetime.now().isoformat(),
            "hojas": {},
            "resumen": {
                "total_productos": 0,
                "categorias": set(),
                "subcategorias": set(),
                "marcas": set(),
                "proveedores": set(),
                "productos_muestra": []
            }
        }
        
        # Analizar cada hoja
        for hoja_nombre in excel_file.sheet_names:
            print(f"\n📋 Analizando hoja: {hoja_nombre}")
            
            try:
                # Leer con dtype=str para evitar problemas de tipos
                df = pd.read_excel(archivo_path, sheet_name=hoja_nombre, dtype=str)
                print(f"   📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
                print(f"   📝 Columnas: {list(df.columns)}")
                
                # Guardar información de la hoja
                hoja_info = {
                    "nombre": hoja_nombre,
                    "filas": df.shape[0],
                    "columnas": df.shape[1],
                    "nombres_columnas": list(df.columns),
                    "muestra_datos": []
                }
                
                # Mostrar primeras 10 filas como muestra
                if not df.empty:
                    muestra = df.head(10).fillna("").to_dict('records')
                    hoja_info["muestra_datos"] = muestra
                    
                    # Extraer información para el resumen
                    for col in df.columns:
                        col_lower = str(col).lower()
                        try:
                            if 'categoria' in col_lower:
                                categorias = df[col].dropna().unique()
                                categorias = [str(c).strip() for c in categorias if str(c).strip() and str(c) != 'nan']
                                resultados["resumen"]["categorias"].update(categorias)
                            elif 'marca' in col_lower:
                                marcas = df[col].dropna().unique()
                                marcas = [str(m).strip() for m in marcas if str(m).strip() and str(m) != 'nan']
                                resultados["resumen"]["marcas"].update(marcas)
                        except Exception as e:
                            print(f"   ⚠️  Error procesando columna {col}: {e}")
                    
                    # Extraer productos de muestra para análisis detallado
                    productos_muestra = []
                    for i, row in df.head(20).iterrows():
                        try:
                            producto = {}
                            for col in df.columns:
                                valor = row[col]
                                if pd.notna(valor) and str(valor).strip() and str(valor) != 'nan':
                                    producto[col] = str(valor).strip()
                            if producto:
                                productos_muestra.append(producto)
                        except Exception as e:
                            print(f"   ⚠️  Error procesando fila {i}: {e}")
                    
                    resultados["resumen"]["productos_muestra"] = productos_muestra[:10]
                    
                    # Contar productos válidos
                    productos_validos = 0
                    for col in ['nombre', 'Nombre', 'NOMBRE', 'producto', 'Producto']:
                        if col in df.columns:
                            productos_validos = df[col].dropna().shape[0]
                            break
                    
                    if productos_validos == 0:
                        productos_validos = df.shape[0]  # Usar total de filas si no hay columna específica
                    
                    resultados["resumen"]["total_productos"] = productos_validos
                
                resultados["hojas"][hoja_nombre] = hoja_info
                
            except Exception as e:
                print(f"   ❌ Error al leer hoja {hoja_nombre}: {e}")
                resultados["hojas"][hoja_nombre] = {"error": str(e)}
        
        # Convertir sets a listas para JSON
        for key in ["categorias", "subcategorias", "marcas", "proveedores"]:
            if key in resultados["resumen"]:
                resultados["resumen"][key] = sorted(list(resultados["resumen"][key]))
        
        # Mostrar resumen
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"   🛍️  Total productos: {resultados['resumen']['total_productos']}")
        print(f"   📂 Categorías: {len(resultados['resumen']['categorias'])}")
        print(f"   🏷️  Marcas: {len(resultados['resumen']['marcas'])}")
        
        if resultados['resumen']['categorias']:
            print(f"   📂 Lista de categorías: {resultados['resumen']['categorias'][:10]}...")
        
        if resultados['resumen']['marcas']:
            print(f"   🏷️  Lista de marcas: {resultados['resumen']['marcas'][:10]}...")
        
        return resultados
        
    except Exception as e:
        print(f"❌ Error al analizar archivo: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    archivo = "/home/ubuntu/upload/.recovery/TiendaprecargadaPRODUCTOSAQUITULUGOproductospublicitarios2025_V2.xlsx"
    
    resultado = analizar_productos_excel(archivo)
    
    if resultado:
        # Guardar resultado en JSON
        with open("/home/ubuntu/analisis_productos_aqui_tu_logo.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Análisis completado. Resultado guardado en: /home/ubuntu/analisis_productos_aqui_tu_logo.json")
    else:
        print("❌ No se pudo completar el análisis")

