#!/usr/bin/env python3
import pandas as pd
import sys

def analizar_excel():
    try:
        # Leer el archivo Excel
        excel_path = '/home/ubuntu/upload/.recovery/TiendaprecargadaPRODUCTOSAQUITULUGOproductospublicitarios2025_V2.xlsx'
        
        # Obtener todas las hojas
        excel_file = pd.ExcelFile(excel_path)
        print(f"📊 ANÁLISIS DEL EXCEL DE PRODUCTOS PUBLICITARIOS")
        print(f"📁 Archivo: {excel_path}")
        print(f"📋 Hojas disponibles: {excel_file.sheet_names}")
        print("=" * 80)
        
        # Analizar cada hoja
        for sheet_name in excel_file.sheet_names:
            print(f"\n🔍 HOJA: {sheet_name}")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
            
            if not df.empty:
                print(f"📝 Columnas disponibles:")
                for i, col in enumerate(df.columns, 1):
                    print(f"  {i:2d}. {col}")
                
                print(f"\n📋 Primeras 3 filas de datos:")
                print(df.head(3).to_string())
                
                # Buscar columnas importantes
                important_cols = ['nombre', 'precio', 'categoria', 'sku', 'codigo', 'descripcion', 'marca']
                found_cols = []
                for col in df.columns:
                    for imp in important_cols:
                        if imp.lower() in col.lower():
                            found_cols.append(col)
                            break
                
                if found_cols:
                    print(f"\n🎯 Columnas importantes encontradas:")
                    for col in found_cols:
                        print(f"  ✅ {col}")
            
            print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error al analizar el Excel: {str(e)}")
        return False

if __name__ == "__main__":
    analizar_excel()

