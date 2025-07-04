#!/usr/bin/env python3
"""
TIENDAS TRESMAS - Sistema de Tallas Completo
Implementación real basada en especificaciones EncuentratuTallas.zip
"""

import json
from typing import Dict, List, Optional, Tuple

class SistemaTallas:
    """Sistema completo de cálculo de tallas según especificaciones"""
    
    def __init__(self):
        self.tablas_tallas = self._inicializar_tablas_tallas()
        self.tipos_prendas = self._inicializar_tipos_prendas()
    
    def _inicializar_tablas_tallas(self) -> Dict:
        """Inicializar todas las tablas de tallas según especificaciones"""
        return {
            "streetwear": [
                {"min": 79, "max": 82, "eu": 34, "cl": 36, "letter": "XS"},
                {"min": 83, "max": 86, "eu": 36, "cl": 38, "letter": "S"},
                {"min": 87, "max": 90, "eu": 38, "cl": 40, "letter": "M"},
                {"min": 91, "max": 94, "eu": 40, "cl": 42, "letter": "M"},
                {"min": 95, "max": 98, "eu": 42, "cl": 44, "letter": "L"},
                {"min": 99, "max": 102, "eu": 44, "cl": 46, "letter": "XL"},
                {"min": 103, "max": 106, "eu": 46, "cl": 48, "letter": "XL"},
                {"min": 107, "max": 112, "eu": 48, "cl": 50, "letter": "XXL"},
                {"min": 113, "max": 118, "eu": 50, "cl": 52, "letter": "XXL-3XL"},
                {"min": 119, "max": 124, "eu": 52, "cl": 54, "letter": "3XL"},
                {"min": 125, "max": 130, "eu": 54, "cl": 56, "letter": "3-4XL"},
                {"min": 131, "max": 136, "eu": 56, "cl": 58, "letter": "4XL"},
                {"min": 137, "max": 142, "eu": 58, "cl": 60, "letter": "4XL"},
                {"min": 143, "max": 148, "eu": 60, "cl": 62, "letter": "4-5XL"}
            ],
            "mujer_superior": [
                {"min": 79, "max": 82, "eu": 34, "cl": 36, "letter": "XS"},
                {"min": 83, "max": 86, "eu": 36, "cl": 38, "letter": "S"},
                {"min": 87, "max": 90, "eu": 38, "cl": 40, "letter": "M"},
                {"min": 91, "max": 94, "eu": 40, "cl": 42, "letter": "M"},
                {"min": 95, "max": 98, "eu": 42, "cl": 44, "letter": "L"},
                {"min": 99, "max": 102, "eu": 44, "cl": 46, "letter": "XL"},
                {"min": 103, "max": 106, "eu": 46, "cl": 48, "letter": "XL"},
                {"min": 107, "max": 112, "eu": 48, "cl": 50, "letter": "XXL"},
                {"min": 113, "max": 118, "eu": 50, "cl": 52, "letter": "XXL-3XL"},
                {"min": 119, "max": 124, "eu": 52, "cl": 54, "letter": "3XL"},
                {"min": 125, "max": 130, "eu": 54, "cl": 56, "letter": "3-4XL"},
                {"min": 131, "max": 136, "eu": 56, "cl": 58, "letter": "4XL"},
                {"min": 137, "max": 142, "eu": 58, "cl": 60, "letter": "4XL"},
                {"min": 143, "max": 148, "eu": 60, "cl": 62, "letter": "4-5XL"}
            ],
            "hombre_superior": [
                {"min": 86, "max": 89, "eu": 44, "cl": 46, "letter": "XS"},
                {"min": 90, "max": 93, "eu": 46, "cl": 48, "letter": "S"},
                {"min": 94, "max": 97, "eu": 48, "cl": 50, "letter": "M"},
                {"min": 98, "max": 101, "eu": 50, "cl": 52, "letter": "L"},
                {"min": 102, "max": 105, "eu": 52, "cl": 54, "letter": "XL"},
                {"min": 106, "max": 109, "eu": 54, "cl": 56, "letter": "XXL"},
                {"min": 110, "max": 113, "eu": 56, "cl": 58, "letter": "3XL"},
                {"min": 114, "max": 117, "eu": 58, "cl": 60, "letter": "4XL"},
                {"min": 118, "max": 121, "eu": 60, "cl": 62, "letter": "5XL"}
            ],
            "zapatos_mujer": [
                {"min": 22.0, "max": 22.5, "eu": 35, "us": "4.5-5", "uk": "2.5-3"},
                {"min": 22.6, "max": 23.0, "eu": 36, "us": "5.5", "uk": "3.5"},
                {"min": 23.1, "max": 23.5, "eu": 37, "us": "6.5", "uk": "4.5"},
                {"min": 23.6, "max": 24.0, "eu": 38, "us": "7.5", "uk": "5.5"},
                {"min": 24.1, "max": 24.5, "eu": 39, "us": "8.5", "uk": "6.5"},
                {"min": 24.6, "max": 25.0, "eu": 40, "us": "9.5", "uk": "7.5"},
                {"min": 25.1, "max": 25.5, "eu": 41, "us": "10.5", "uk": "8.5"},
                {"min": 25.6, "max": 26.0, "eu": 42, "us": "11", "uk": "9"}
            ],
            "zapatos_hombre": [
                {"min": 24.0, "max": 24.5, "eu": 38, "us": "6", "uk": "5"},
                {"min": 24.6, "max": 25.0, "eu": 39, "us": "6.5", "uk": "5.5"},
                {"min": 25.1, "max": 25.5, "eu": 40, "us": "7", "uk": "6"},
                {"min": 25.6, "max": 26.0, "eu": 41, "us": "8", "uk": "7"},
                {"min": 26.1, "max": 26.5, "eu": 42, "us": "8.5", "uk": "7.5"},
                {"min": 26.6, "max": 27.0, "eu": 43, "us": "9.5", "uk": "8.5"},
                {"min": 27.1, "max": 27.5, "eu": 44, "us": "10", "uk": "9"},
                {"min": 27.6, "max": 28.0, "eu": 45, "us": "11", "uk": "10"},
                {"min": 28.1, "max": 28.5, "eu": 46, "us": "12", "uk": "11"}
            ],
            "infantil": [
                {"min": 50, "max": 55, "edad": "0-3 meses", "talla": "50-56", "letter": "RN"},
                {"min": 56, "max": 61, "edad": "3-6 meses", "talla": "56-62", "letter": "3M"},
                {"min": 62, "max": 67, "edad": "6-9 meses", "talla": "62-68", "letter": "6M"},
                {"min": 68, "max": 73, "edad": "9-12 meses", "talla": "68-74", "letter": "9M"},
                {"min": 74, "max": 79, "edad": "12-18 meses", "talla": "74-80", "letter": "12M"},
                {"min": 80, "max": 85, "edad": "18-24 meses", "talla": "80-86", "letter": "18M"},
                {"min": 86, "max": 91, "edad": "2-3 años", "talla": "86-92", "letter": "2T"},
                {"min": 92, "max": 97, "edad": "3-4 años", "talla": "92-98", "letter": "3T"},
                {"min": 98, "max": 103, "edad": "4-5 años", "talla": "98-104", "letter": "4T"},
                {"min": 104, "max": 109, "edad": "5-6 años", "talla": "104-110", "letter": "5T"},
                {"min": 110, "max": 115, "edad": "6-7 años", "talla": "110-116", "letter": "6"},
                {"min": 116, "max": 121, "edad": "7-8 años", "talla": "116-122", "letter": "7"},
                {"min": 122, "max": 127, "edad": "8-9 años", "talla": "122-128", "letter": "8"},
                {"min": 128, "max": 133, "edad": "9-10 años", "talla": "128-134", "letter": "9"},
                {"min": 134, "max": 139, "edad": "10-11 años", "talla": "134-140", "letter": "10"},
                {"min": 140, "max": 145, "edad": "11-12 años", "talla": "140-146", "letter": "11"},
                {"min": 146, "max": 151, "edad": "12-13 años", "talla": "146-152", "letter": "12"},
                {"min": 152, "max": 157, "edad": "13-14 años", "talla": "152-158", "letter": "13"},
                {"min": 158, "max": 163, "edad": "14-15 años", "talla": "158-164", "letter": "14"}
            ],
            "plus_size_mujer": [
                {"min": 119, "max": 124, "eu": 52, "cl": 54, "letter": "3XL"},
                {"min": 125, "max": 130, "eu": 54, "cl": 56, "letter": "3-4XL"},
                {"min": 131, "max": 136, "eu": 56, "cl": 58, "letter": "4XL"},
                {"min": 137, "max": 142, "eu": 58, "cl": 60, "letter": "4XL"},
                {"min": 143, "max": 148, "eu": 60, "cl": 62, "letter": "4-5XL"},
                {"min": 149, "max": 154, "eu": 62, "cl": 64, "letter": "5XL"},
                {"min": 155, "max": 160, "eu": 64, "cl": 66, "letter": "5-6XL"},
                {"min": 161, "max": 166, "eu": 66, "cl": 68, "letter": "6XL"},
                {"min": 167, "max": 172, "eu": 68, "cl": 70, "letter": "6-7XL"},
                {"min": 173, "max": 178, "eu": 70, "cl": 72, "letter": "7XL"}
            ],
            "sujetadores": [
                {"contorno": 63, "copa_a": "70A", "copa_b": "70B", "copa_c": "70C", "copa_d": "70D"},
                {"contorno": 68, "copa_a": "75A", "copa_b": "75B", "copa_c": "75C", "copa_d": "75D"},
                {"contorno": 73, "copa_a": "80A", "copa_b": "80B", "copa_c": "80C", "copa_d": "80D"},
                {"contorno": 78, "copa_a": "85A", "copa_b": "85B", "copa_c": "85C", "copa_d": "85D"},
                {"contorno": 83, "copa_a": "90A", "copa_b": "90B", "copa_c": "90C", "copa_d": "90D"},
                {"contorno": 88, "copa_a": "95A", "copa_b": "95B", "copa_c": "95C", "copa_d": "95D"},
                {"contorno": 93, "copa_a": "100A", "copa_b": "100B", "copa_c": "100C", "copa_d": "100D"},
                {"contorno": 98, "copa_a": "105A", "copa_b": "105B", "copa_c": "105C", "copa_d": "105D"}
            ],
            "cinturones": [
                {"min": 71, "max": 76, "talla": "75", "letter": "XS"},
                {"min": 77, "max": 82, "talla": "80", "letter": "S"},
                {"min": 83, "max": 88, "talla": "85", "letter": "M"},
                {"min": 89, "max": 94, "talla": "90", "letter": "L"},
                {"min": 95, "max": 100, "talla": "95", "letter": "XL"},
                {"min": 101, "max": 106, "talla": "100", "letter": "XXL"},
                {"min": 107, "max": 112, "talla": "105", "letter": "3XL"},
                {"min": 113, "max": 118, "talla": "110", "letter": "4XL"}
            ],
            "sombreros": [
                {"min": 53, "max": 54, "talla": "XS", "cm": "53-54"},
                {"min": 55, "max": 56, "talla": "S", "cm": "55-56"},
                {"min": 57, "max": 58, "talla": "M", "cm": "57-58"},
                {"min": 59, "max": 60, "talla": "L", "cm": "59-60"},
                {"min": 61, "max": 62, "talla": "XL", "cm": "61-62"},
                {"min": 63, "max": 64, "talla": "XXL", "cm": "63-64"}
            ],
            "guantes": [
                {"min": 15, "max": 16, "talla": "XS", "cm": "15-16"},
                {"min": 17, "max": 18, "talla": "S", "cm": "17-18"},
                {"min": 19, "max": 20, "talla": "M", "cm": "19-20"},
                {"min": 21, "max": 22, "talla": "L", "cm": "21-22"},
                {"min": 23, "max": 24, "talla": "XL", "cm": "23-24"},
                {"min": 25, "max": 26, "talla": "XXL", "cm": "25-26"}
            ]
        }
    
    def _inicializar_tipos_prendas(self) -> List[Dict]:
        """Inicializar tipos de prendas disponibles"""
        return [
            {
                "id": 1,
                "nombre": "Streetwear",
                "genero": "Unisex",
                "tabla": "streetwear",
                "medida": "Contorno de pecho",
                "unidad": "cm",
                "descripcion": "Ropa urbana y casual",
                "min_medida": 79,
                "max_medida": 148
            },
            {
                "id": 2,
                "nombre": "Chaquetas/Blusas/Vestidos Mujer",
                "genero": "Mujer",
                "tabla": "mujer_superior",
                "medida": "Contorno de pecho",
                "unidad": "cm",
                "descripcion": "Prendas superiores femeninas",
                "min_medida": 79,
                "max_medida": 148
            },
            {
                "id": 3,
                "nombre": "Chaquetas/Blazers/Abrigos Hombre",
                "genero": "Hombre",
                "tabla": "hombre_superior",
                "medida": "Contorno de pecho",
                "unidad": "cm",
                "descripcion": "Prendas superiores masculinas",
                "min_medida": 86,
                "max_medida": 121
            },
            {
                "id": 4,
                "nombre": "Zapatos Mujer",
                "genero": "Mujer",
                "tabla": "zapatos_mujer",
                "medida": "Longitud del pie",
                "unidad": "cm",
                "descripcion": "Calzado femenino",
                "min_medida": 22.0,
                "max_medida": 26.0
            },
            {
                "id": 5,
                "nombre": "Zapatos Hombre",
                "genero": "Hombre",
                "tabla": "zapatos_hombre",
                "medida": "Longitud del pie",
                "unidad": "cm",
                "descripcion": "Calzado masculino",
                "min_medida": 24.0,
                "max_medida": 28.5
            },
            {
                "id": 6,
                "nombre": "Ropa Infantil/Juvenil",
                "genero": "Infantil",
                "tabla": "infantil",
                "medida": "Altura",
                "unidad": "cm",
                "descripcion": "Ropa para niños 0-14 años",
                "min_medida": 50,
                "max_medida": 163
            },
            {
                "id": 7,
                "nombre": "Plus Size Mujer",
                "genero": "Mujer",
                "tabla": "plus_size_mujer",
                "medida": "Contorno de pecho",
                "unidad": "cm",
                "descripcion": "Tallas grandes femeninas",
                "min_medida": 119,
                "max_medida": 178
            },
            {
                "id": 8,
                "nombre": "Sujetadores",
                "genero": "Mujer",
                "tabla": "sujetadores",
                "medida": "Contorno bajo pecho",
                "unidad": "cm",
                "descripcion": "Ropa interior femenina",
                "min_medida": 63,
                "max_medida": 98
            },
            {
                "id": 9,
                "nombre": "Cinturones",
                "genero": "Unisex",
                "tabla": "cinturones",
                "medida": "Contorno de cintura",
                "unidad": "cm",
                "descripcion": "Accesorios de cintura",
                "min_medida": 71,
                "max_medida": 118
            },
            {
                "id": 10,
                "nombre": "Sombreros",
                "genero": "Unisex",
                "tabla": "sombreros",
                "medida": "Contorno de cabeza",
                "unidad": "cm",
                "descripcion": "Accesorios de cabeza",
                "min_medida": 53,
                "max_medida": 64
            },
            {
                "id": 11,
                "nombre": "Guantes",
                "genero": "Unisex",
                "tabla": "guantes",
                "medida": "Ancho de mano",
                "unidad": "cm",
                "descripcion": "Accesorios de manos",
                "min_medida": 15,
                "max_medida": 26
            }
        ]
    
    def obtener_tipos_prendas(self) -> List[Dict]:
        """Obtener lista de tipos de prendas disponibles"""
        return self.tipos_prendas
    
    def calcular_talla(self, tipo_id: int, medida: float) -> Dict:
        """Calcular talla basada en tipo de prenda y medida"""
        try:
            # Buscar tipo de prenda
            tipo_prenda = next((t for t in self.tipos_prendas if t["id"] == tipo_id), None)
            if not tipo_prenda:
                return {
                    "success": False,
                    "error": "Tipo de prenda no encontrado"
                }
            
            # Validar rango de medida
            if medida < tipo_prenda["min_medida"] or medida > tipo_prenda["max_medida"]:
                return {
                    "success": False,
                    "error": f"Medida fuera de rango. Rango válido: {tipo_prenda['min_medida']}-{tipo_prenda['max_medida']} {tipo_prenda['unidad']}"
                }
            
            # Obtener tabla correspondiente
            tabla = self.tablas_tallas.get(tipo_prenda["tabla"])
            if not tabla:
                return {
                    "success": False,
                    "error": "Tabla de tallas no encontrada"
                }
            
            # Buscar talla en la tabla
            talla_encontrada = None
            for entrada in tabla:
                if medida >= entrada["min"] and medida <= entrada["max"]:
                    talla_encontrada = entrada
                    break
            
            if not talla_encontrada:
                return {
                    "success": False,
                    "error": "No se encontró talla para la medida especificada"
                }
            
            # Formatear resultado según tipo de tabla
            resultado = {
                "success": True,
                "tipo_prenda": tipo_prenda["nombre"],
                "medida_ingresada": medida,
                "unidad": tipo_prenda["unidad"],
                "talla": self._formatear_talla(talla_encontrada, tipo_prenda["tabla"])
            }
            
            return resultado
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al calcular talla: {str(e)}"
            }
    
    def _formatear_talla(self, entrada: Dict, tipo_tabla: str) -> Dict:
        """Formatear resultado de talla según tipo de tabla"""
        if tipo_tabla in ["streetwear", "mujer_superior", "hombre_superior", "plus_size_mujer"]:
            return {
                "talla": entrada.get("letter", "N/A"),
                "eu": entrada.get("eu", "N/A"),
                "cl": entrada.get("cl", "N/A"),
                "rango": f"{entrada['min']}-{entrada['max']} cm"
            }
        elif tipo_tabla in ["zapatos_mujer", "zapatos_hombre"]:
            return {
                "talla": f"EU {entrada.get('eu', 'N/A')}",
                "eu": entrada.get("eu", "N/A"),
                "us": entrada.get("us", "N/A"),
                "uk": entrada.get("uk", "N/A"),
                "rango": f"{entrada['min']}-{entrada['max']} cm"
            }
        elif tipo_tabla == "infantil":
            return {
                "talla": entrada.get("letter", "N/A"),
                "edad": entrada.get("edad", "N/A"),
                "talla_numerica": entrada.get("talla", "N/A"),
                "rango": f"{entrada['min']}-{entrada['max']} cm"
            }
        elif tipo_tabla == "sujetadores":
            return {
                "contorno": f"{entrada.get('contorno', 'N/A')} cm",
                "copa_a": entrada.get("copa_a", "N/A"),
                "copa_b": entrada.get("copa_b", "N/A"),
                "copa_c": entrada.get("copa_c", "N/A"),
                "copa_d": entrada.get("copa_d", "N/A")
            }
        elif tipo_tabla in ["cinturones", "sombreros", "guantes"]:
            return {
                "talla": entrada.get("talla", "N/A"),
                "cm": entrada.get("cm", f"{entrada['min']}-{entrada['max']} cm"),
                "rango": f"{entrada['min']}-{entrada['max']} cm"
            }
        else:
            return entrada
    
    def obtener_tabla_referencia(self, tipo_id: int) -> Dict:
        """Obtener tabla de referencia completa para un tipo de prenda"""
        try:
            tipo_prenda = next((t for t in self.tipos_prendas if t["id"] == tipo_id), None)
            if not tipo_prenda:
                return {
                    "success": False,
                    "error": "Tipo de prenda no encontrado"
                }
            
            tabla = self.tablas_tallas.get(tipo_prenda["tabla"])
            if not tabla:
                return {
                    "success": False,
                    "error": "Tabla de tallas no encontrada"
                }
            
            # Formatear tabla para mostrar
            tabla_formateada = []
            for entrada in tabla:
                fila = {
                    "rango": f"{entrada['min']}-{entrada['max']} {tipo_prenda['unidad']}",
                    **self._formatear_talla(entrada, tipo_prenda["tabla"])
                }
                tabla_formateada.append(fila)
            
            return {
                "success": True,
                "tipo_prenda": tipo_prenda["nombre"],
                "medida": tipo_prenda["medida"],
                "unidad": tipo_prenda["unidad"],
                "tabla": tabla_formateada
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al obtener tabla: {str(e)}"
            }
    
    def buscar_tallas_por_medida(self, medida: float, genero: str = None) -> List[Dict]:
        """Buscar todas las tallas posibles para una medida dada"""
        resultados = []
        
        for tipo in self.tipos_prendas:
            if genero and tipo["genero"] != genero and tipo["genero"] != "Unisex":
                continue
            
            if medida >= tipo["min_medida"] and medida <= tipo["max_medida"]:
                resultado = self.calcular_talla(tipo["id"], medida)
                if resultado["success"]:
                    resultados.append({
                        "tipo": tipo["nombre"],
                        "genero": tipo["genero"],
                        "talla": resultado["talla"]
                    })
        
        return resultados
    
    def validar_medida(self, tipo_id: int, medida: float) -> Dict:
        """Validar si una medida es válida para un tipo de prenda"""
        tipo_prenda = next((t for t in self.tipos_prendas if t["id"] == tipo_id), None)
        if not tipo_prenda:
            return {
                "valida": False,
                "error": "Tipo de prenda no encontrado"
            }
        
        if medida < tipo_prenda["min_medida"] or medida > tipo_prenda["max_medida"]:
            return {
                "valida": False,
                "error": f"Medida fuera de rango",
                "rango_valido": f"{tipo_prenda['min_medida']}-{tipo_prenda['max_medida']} {tipo_prenda['unidad']}"
            }
        
        return {
            "valida": True,
            "mensaje": "Medida válida"
        }

# Instancia global del sistema de tallas
sistema_tallas = SistemaTallas()

if __name__ == "__main__":
    # Test del sistema
    print("📏 Sistema de Tallas TIENDAS TRESMAS")
    print("✅ Sistema inicializado correctamente")
    print(f"📊 Tipos de prendas disponibles: {len(sistema_tallas.tipos_prendas)}")
    print(f"📋 Tablas de tallas: {len(sistema_tallas.tablas_tallas)}")
    
    # Test de cálculo
    resultado = sistema_tallas.calcular_talla(1, 85)  # Streetwear, 85cm
    print(f"🧪 Test: {resultado}")

