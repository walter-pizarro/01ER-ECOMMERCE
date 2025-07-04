#!/usr/bin/env python3
"""
TIENDAS TRESMAS - Sistema de Señaléticas Completo
Implementación real basada en especificaciones del usuario
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class SistemaSeñaleticas:
    """Sistema completo de cálculo de costos de señaléticas"""
    
    def __init__(self):
        self.materiales_db = self._inicializar_materiales()
        self.parametros_default = self._inicializar_parametros_default()
    
    def _inicializar_materiales(self) -> List[Dict]:
        """Inicializar base de datos de materiales según especificaciones"""
        return [
            # Sustratos
            {
                "id": "alu-30",
                "nombre": "Aluminio Compuesto 3mm",
                "tipo": "Sustrato",
                "precio_unitario": 45000,
                "ancho_unitario": 1.22,
                "alto_unitario": 2.44,
                "espesor": 3.0,
                "precio_m2": None  # Se calculará automáticamente
            },
            {
                "id": "alu-40",
                "nombre": "Aluminio Compuesto 4mm",
                "tipo": "Sustrato",
                "precio_unitario": 60000,
                "ancho_unitario": 1.22,
                "alto_unitario": 2.44,
                "espesor": 4.0,
                "precio_m2": None
            },
            {
                "id": "alu-50",
                "nombre": "Aluminio Compuesto 5mm",
                "tipo": "Sustrato",
                "precio_unitario": 75000,
                "ancho_unitario": 1.22,
                "alto_unitario": 2.44,
                "espesor": 5.0,
                "precio_m2": None
            },
            {
                "id": "tro-30",
                "nombre": "Trovicel Zintra 3mm",
                "tipo": "Sustrato",
                "precio_unitario": 18500,
                "ancho_unitario": 1.22,
                "alto_unitario": 2.44,
                "espesor": 3.0,
                "precio_m2": None
            },
            {
                "id": "tro-50",
                "nombre": "Trovicel Zintra 5mm",
                "tipo": "Sustrato",
                "precio_unitario": 30000,
                "ancho_unitario": 1.22,
                "alto_unitario": 2.44,
                "espesor": 5.0,
                "precio_m2": None
            },
            {
                "id": "tro-70",
                "nombre": "Trovicel Zintra 7mm",
                "tipo": "Sustrato",
                "precio_unitario": 42000,
                "ancho_unitario": 1.22,
                "alto_unitario": 2.44,
                "espesor": 7.0,
                "precio_m2": None
            },
            {
                "id": "foa-30",
                "nombre": "Plástico Foamex 3mm",
                "tipo": "Sustrato",
                "precio_unitario": 15000,
                "ancho_unitario": 1.22,
                "alto_unitario": 2.44,
                "espesor": 3.0,
                "precio_m2": None
            },
            {
                "id": "foa-50",
                "nombre": "Plástico Foamex 5mm",
                "tipo": "Sustrato",
                "precio_unitario": 25000,
                "ancho_unitario": 1.22,
                "alto_unitario": 2.44,
                "espesor": 5.0,
                "precio_m2": None
            },
            {
                "id": "foa-70",
                "nombre": "Plástico Foamex 7mm",
                "tipo": "Sustrato",
                "precio_unitario": 35000,
                "ancho_unitario": 1.22,
                "alto_unitario": 2.44,
                "espesor": 7.0,
                "precio_m2": None
            },
            # Gráficas (Vinilos)
            {
                "id": "vin-gc-imp",
                "nombre": "Vinilo Reflectante Grado Comercial Impreso",
                "tipo": "Grafica",
                "precio_unitario": 125000,
                "ancho_unitario": 0.62,
                "alto_unitario": 45,
                "espesor": 0,
                "precio_m2": None
            },
            {
                "id": "vin-gc",
                "nombre": "Vinilo Reflectante Grado Comercial",
                "tipo": "Grafica",
                "precio_unitario": 70000,
                "ancho_unitario": 0.62,
                "alto_unitario": 45,
                "espesor": 0,
                "precio_m2": None
            },
            {
                "id": "vin-gi",
                "nombre": "Vinilo Adhesivo Grado Ingeniería",
                "tipo": "Grafica",
                "precio_unitario": 360000,
                "ancho_unitario": 0.62,
                "alto_unitario": 45,
                "espesor": 0,
                "precio_m2": None
            },
            {
                "id": "vin-aip",
                "nombre": "Vinilo Reflectante Alta Intensidad Prismático",
                "tipo": "Grafica",
                "precio_unitario": 438000,
                "ancho_unitario": 0.62,
                "alto_unitario": 45,
                "espesor": 0,
                "precio_m2": None
            },
            {
                "id": "vin-aip-f",
                "nombre": "Vinilo Reflectante AIP Fluorescente",
                "tipo": "Grafica",
                "precio_unitario": 494000,
                "ancho_unitario": 0.62,
                "alto_unitario": 45,
                "espesor": 0,
                "precio_m2": None
            }
        ]
    
    def _inicializar_parametros_default(self) -> Dict:
        """Parámetros por defecto para cálculos"""
        return {
            "porcentaje_utilidad": 25.0,  # %
            "tiempo_mod": 0.75,  # horas
            "costo_hora_mod": 8500,  # CLP
            "merma_material": 15.0,  # %
            "porcentaje_cif": 15.0,  # %
            "porcentaje_gav": 20.0,  # %
            "tasa_iva": 19.0  # %
        }
    
    def calcular_precio_m2(self, material: Dict) -> float:
        """Calcular precio por metro cuadrado de un material"""
        area_unitaria = material["ancho_unitario"] * material["alto_unitario"]
        return material["precio_unitario"] / area_unitaria if area_unitaria > 0 else 0
    
    def actualizar_precios_m2(self):
        """Actualizar precios por m² de todos los materiales"""
        for material in self.materiales_db:
            material["precio_m2"] = self.calcular_precio_m2(material)
    
    def obtener_materiales(self) -> Dict:
        """Obtener materiales organizados por tipo"""
        self.actualizar_precios_m2()
        
        sustratos = [m for m in self.materiales_db if m["tipo"] == "Sustrato"]
        graficas = [m for m in self.materiales_db if m["tipo"] == "Grafica"]
        
        return {
            "sustratos": sustratos,
            "graficas": graficas,
            "todos": self.materiales_db
        }
    
    def obtener_material_por_id(self, material_id: str) -> Optional[Dict]:
        """Obtener material específico por ID"""
        return next((m for m in self.materiales_db if m["id"] == material_id), None)
    
    def calcular_costo_senaletica(self, parametros: Dict) -> Dict:
        """
        Calcular costo completo de señalética según especificaciones
        
        Parámetros esperados:
        - ancho_cm: Ancho en centímetros
        - alto_cm: Alto en centímetros
        - cantidad: Cantidad de unidades
        - sustrato_id: ID del material sustrato
        - grafica_id: ID del material gráfica
        - parametros opcionales de costos
        """
        try:
            # Extraer parámetros
            ancho_cm = float(parametros.get("ancho_cm", 60))
            alto_cm = float(parametros.get("alto_cm", 90))
            cantidad = int(parametros.get("cantidad", 1))
            sustrato_id = parametros.get("sustrato_id")
            grafica_id = parametros.get("grafica_id")
            
            # Parámetros de costos (usar defaults si no se proporcionan)
            porc_utilidad = float(parametros.get("porcentaje_utilidad", self.parametros_default["porcentaje_utilidad"])) / 100
            tiempo_mod = float(parametros.get("tiempo_mod", self.parametros_default["tiempo_mod"]))
            costo_hora_mod = float(parametros.get("costo_hora_mod", self.parametros_default["costo_hora_mod"]))
            porc_merma = float(parametros.get("merma_material", self.parametros_default["merma_material"])) / 100
            porc_cif = float(parametros.get("porcentaje_cif", self.parametros_default["porcentaje_cif"])) / 100
            porc_gav = float(parametros.get("porcentaje_gav", self.parametros_default["porcentaje_gav"])) / 100
            porc_iva = float(parametros.get("tasa_iva", self.parametros_default["tasa_iva"])) / 100
            
            # Validar materiales
            sustrato = self.obtener_material_por_id(sustrato_id)
            grafica = self.obtener_material_por_id(grafica_id)
            
            if not sustrato or not grafica:
                return {
                    "success": False,
                    "error": "Materiales no encontrados"
                }
            
            # Actualizar precios m²
            self.actualizar_precios_m2()
            
            # Cálculos básicos
            area_m2 = (ancho_cm * alto_cm) / 10000  # Convertir cm² a m²
            
            # Costos de materiales con merma
            costo_sustrato = area_m2 * sustrato["precio_m2"] * (1 + porc_merma)
            costo_grafica = area_m2 * grafica["precio_m2"] * (1 + porc_merma)
            subtotal_md = costo_sustrato + costo_grafica
            
            # Costo MOD (Mano de Obra Directa)
            costo_mod = tiempo_mod * costo_hora_mod
            
            # Costo directo total
            costo_directo_total = subtotal_md + costo_mod
            
            # CIF (Costos Indirectos de Fabricación)
            costo_cif = costo_directo_total * porc_cif
            
            # Costo de producción
            costo_produccion = costo_directo_total + costo_cif
            
            # GAV (Gastos Administrativos y de Ventas)
            costo_gav = costo_produccion * porc_gav
            
            # Costo total comercial
            costo_total_comercial = costo_produccion + costo_gav
            
            # Cálculo de precios finales
            if porc_utilidad >= 1:
                # Utilidad >= 100% es inválida
                precio_venta_neto = float('inf')
                monto_iva = float('inf')
                precio_final_publico = float('inf')
                margen_contribucion = float('nan')
                margen_bruto = float('nan')
                margen_neto = float('nan')
            else:
                precio_venta_neto = costo_total_comercial / (1 - porc_utilidad)
                monto_iva = precio_venta_neto * porc_iva
                precio_final_publico = precio_venta_neto + monto_iva
                
                # Márgenes
                margen_contribucion = (precio_venta_neto - costo_directo_total) / precio_venta_neto if precio_venta_neto > 0 else 0
                margen_bruto = (precio_venta_neto - costo_produccion) / precio_venta_neto if precio_venta_neto > 0 else 0
                margen_neto = (precio_venta_neto - costo_total_comercial) / precio_venta_neto if precio_venta_neto > 0 else 0
            
            # Cálculos por cantidad
            precio_total = precio_final_publico * cantidad if math.isfinite(precio_final_publico) else float('inf')
            
            # Resultado estructurado
            resultado = {
                "success": True,
                "parametros": {
                    "ancho_cm": ancho_cm,
                    "alto_cm": alto_cm,
                    "area_m2": round(area_m2, 4),
                    "cantidad": cantidad,
                    "sustrato": sustrato["nombre"],
                    "grafica": grafica["nombre"]
                },
                "costos_unitarios": {
                    "costo_sustrato": round(costo_sustrato, 0),
                    "costo_grafica": round(costo_grafica, 0),
                    "subtotal_materiales": round(subtotal_md, 0),
                    "costo_mod": round(costo_mod, 0),
                    "costo_directo_total": round(costo_directo_total, 0),
                    "costo_cif": round(costo_cif, 0),
                    "costo_produccion": round(costo_produccion, 0),
                    "costo_gav": round(costo_gav, 0),
                    "costo_total_comercial": round(costo_total_comercial, 0)
                },
                "precios_unitarios": {
                    "precio_venta_neto": round(precio_venta_neto, 0) if math.isfinite(precio_venta_neto) else "Inválido",
                    "monto_iva": round(monto_iva, 0) if math.isfinite(monto_iva) else "Inválido",
                    "precio_final_publico": round(precio_final_publico, 0) if math.isfinite(precio_final_publico) else "Inválido"
                },
                "precios_totales": {
                    "precio_total": round(precio_total, 0) if math.isfinite(precio_total) else "Inválido"
                },
                "margenes": {
                    "margen_contribucion": round(margen_contribucion * 100, 2) if not math.isnan(margen_contribucion) else "N/A",
                    "margen_bruto": round(margen_bruto * 100, 2) if not math.isnan(margen_bruto) else "N/A",
                    "margen_neto": round(margen_neto * 100, 2) if not math.isnan(margen_neto) else "N/A"
                },
                "parametros_calculo": {
                    "porcentaje_utilidad": round(porc_utilidad * 100, 2),
                    "tiempo_mod_horas": tiempo_mod,
                    "costo_hora_mod": costo_hora_mod,
                    "merma_material": round(porc_merma * 100, 2),
                    "porcentaje_cif": round(porc_cif * 100, 2),
                    "porcentaje_gav": round(porc_gav * 100, 2),
                    "tasa_iva": round(porc_iva * 100, 2)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return resultado
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en cálculo: {str(e)}"
            }
    
    def agregar_material(self, material_data: Dict) -> Dict:
        """Agregar nuevo material a la base de datos"""
        try:
            # Validar datos requeridos
            campos_requeridos = ["nombre", "tipo", "precio_unitario", "ancho_unitario", "alto_unitario"]
            for campo in campos_requeridos:
                if campo not in material_data:
                    return {
                        "success": False,
                        "error": f"Campo requerido: {campo}"
                    }
            
            # Generar ID único
            nuevo_id = f"mat-{int(datetime.now().timestamp())}"
            
            nuevo_material = {
                "id": nuevo_id,
                "nombre": material_data["nombre"],
                "tipo": material_data["tipo"],
                "precio_unitario": float(material_data["precio_unitario"]),
                "ancho_unitario": float(material_data["ancho_unitario"]),
                "alto_unitario": float(material_data["alto_unitario"]),
                "espesor": float(material_data.get("espesor", 0)),
                "precio_m2": None
            }
            
            self.materiales_db.append(nuevo_material)
            
            return {
                "success": True,
                "material": nuevo_material,
                "mensaje": "Material agregado exitosamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al agregar material: {str(e)}"
            }
    
    def actualizar_material(self, material_id: str, material_data: Dict) -> Dict:
        """Actualizar material existente"""
        try:
            material = self.obtener_material_por_id(material_id)
            if not material:
                return {
                    "success": False,
                    "error": "Material no encontrado"
                }
            
            # Actualizar campos proporcionados
            campos_actualizables = ["nombre", "tipo", "precio_unitario", "ancho_unitario", "alto_unitario", "espesor"]
            for campo in campos_actualizables:
                if campo in material_data:
                    if campo in ["precio_unitario", "ancho_unitario", "alto_unitario", "espesor"]:
                        material[campo] = float(material_data[campo])
                    else:
                        material[campo] = material_data[campo]
            
            return {
                "success": True,
                "material": material,
                "mensaje": "Material actualizado exitosamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al actualizar material: {str(e)}"
            }
    
    def eliminar_material(self, material_id: str) -> Dict:
        """Eliminar material de la base de datos"""
        try:
            material = self.obtener_material_por_id(material_id)
            if not material:
                return {
                    "success": False,
                    "error": "Material no encontrado"
                }
            
            self.materiales_db.remove(material)
            
            return {
                "success": True,
                "mensaje": "Material eliminado exitosamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al eliminar material: {str(e)}"
            }
    
    def obtener_cotizacion_completa(self, parametros: Dict) -> Dict:
        """Generar cotización completa con detalles técnicos"""
        resultado_calculo = self.calcular_costo_senaletica(parametros)
        
        if not resultado_calculo["success"]:
            return resultado_calculo
        
        # Agregar información adicional para cotización
        cotizacion = {
            **resultado_calculo,
            "cotizacion": {
                "numero": f"COT-{int(datetime.now().timestamp())}",
                "fecha": datetime.now().strftime("%d/%m/%Y"),
                "validez_dias": 30,
                "condiciones": [
                    "Precios en pesos chilenos (CLP)",
                    "No incluye instalación",
                    "Materiales sujetos a disponibilidad",
                    "Tiempo de entrega: 5-7 días hábiles"
                ],
                "especificaciones_tecnicas": {
                    "sustrato": resultado_calculo["parametros"]["sustrato"],
                    "grafica": resultado_calculo["parametros"]["grafica"],
                    "dimensiones": f"{resultado_calculo['parametros']['ancho_cm']} x {resultado_calculo['parametros']['alto_cm']} cm",
                    "area_total": f"{resultado_calculo['parametros']['area_m2']} m²",
                    "cantidad": resultado_calculo["parametros"]["cantidad"]
                }
            }
        }
        
        return cotizacion

# Instancia global del sistema de señaléticas
sistema_senaleticas = SistemaSeñaleticas()

if __name__ == "__main__":
    # Test del sistema
    print("🏗️ Sistema de Señaléticas TIENDAS TRESMAS")
    print("✅ Sistema inicializado correctamente")
    print(f"📦 Materiales disponibles: {len(sistema_senaleticas.materiales_db)}")
    
    # Test de cálculo
    parametros_test = {
        "ancho_cm": 60,
        "alto_cm": 90,
        "cantidad": 1,
        "sustrato_id": "alu-30",
        "grafica_id": "vin-gc"
    }
    
    resultado = sistema_senaleticas.calcular_costo_senaletica(parametros_test)
    print(f"🧪 Test cálculo: {resultado['success']}")
    if resultado["success"]:
        print(f"💰 Precio final: ${resultado['precios_unitarios']['precio_final_publico']:,.0f}")

