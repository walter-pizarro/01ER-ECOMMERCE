#!/usr/bin/env python3
"""
TIENDAS TRESMAS - Validador de Imágenes Avanzado
Implementación real según especificaciones del usuario
"""

import os
import sys
import json
import hashlib
import uuid
from datetime import datetime
from PIL import Image, ImageStat
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from io import BytesIO
import base64

class ValidadorImagenes:
    """Validador avanzado de imágenes para productos"""
    
    def __init__(self):
        self.formatos_permitidos = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
        self.tamaño_maximo_mb = 5
        self.dimensiones_minimas = (300, 300)
        self.dimensiones_recomendadas = (800, 800)
        self.calidad_minima = 70
        
        # Crear directorios necesarios
        self.dir_por_validar = "imagenes_por_validar"
        self.dir_productos = "imagenes_productos"
        self.dir_temp = "temp_images"
        
        for directorio in [self.dir_por_validar, self.dir_productos, self.dir_temp]:
            os.makedirs(directorio, exist_ok=True)
    
    def validar_imagen_completa(self, archivo_imagen):
        """Validación completa de imagen según especificaciones"""
        try:
            # Leer imagen
            if hasattr(archivo_imagen, 'read'):
                imagen_data = archivo_imagen.read()
                archivo_imagen.seek(0)  # Reset para uso posterior
            else:
                with open(archivo_imagen, 'rb') as f:
                    imagen_data = f.read()
            
            # Abrir imagen con PIL
            imagen = Image.open(BytesIO(imagen_data))
            
            # Información básica
            info_basica = {
                "formato": imagen.format,
                "modo": imagen.mode,
                "dimensiones": imagen.size,
                "tamaño_bytes": len(imagen_data),
                "tamaño_mb": round(len(imagen_data) / (1024 * 1024), 2)
            }
            
            # Validaciones técnicas
            validaciones = self._realizar_validaciones_tecnicas(imagen, imagen_data)
            
            # Análisis de calidad
            analisis_calidad = self._analizar_calidad_imagen(imagen)
            
            # Sugerencias de optimización
            sugerencias = self._generar_sugerencias(imagen, imagen_data, validaciones)
            
            # Generar SKU sugerido
            sku_sugerido = self._generar_sku_desde_imagen(archivo_imagen)
            
            # Resultado final
            resultado = {
                "valida": all(validaciones.values()),
                "info_basica": info_basica,
                "validaciones": validaciones,
                "analisis_calidad": analisis_calidad,
                "sugerencias": sugerencias,
                "sku_sugerido": sku_sugerido,
                "timestamp": datetime.now().isoformat()
            }
            
            return resultado
            
        except Exception as e:
            return {
                "error": f"Error al procesar imagen: {str(e)}",
                "valida": False
            }
    
    def _realizar_validaciones_tecnicas(self, imagen, imagen_data):
        """Validaciones técnicas específicas"""
        validaciones = {}
        
        # Formato válido
        validaciones["formato_valido"] = imagen.format.lower() in [f.upper() for f in self.formatos_permitidos]
        
        # Tamaño de archivo
        validaciones["tamaño_adecuado"] = len(imagen_data) <= (self.tamaño_maximo_mb * 1024 * 1024)
        
        # Dimensiones mínimas
        ancho, alto = imagen.size
        validaciones["dimensiones_minimas"] = ancho >= self.dimensiones_minimas[0] and alto >= self.dimensiones_minimas[1]
        
        # Relación de aspecto (preferiblemente cuadrada o rectangular estándar)
        relacion_aspecto = ancho / alto
        validaciones["relacion_aspecto_adecuada"] = 0.5 <= relacion_aspecto <= 2.0
        
        # Modo de color adecuado
        validaciones["modo_color_adecuado"] = imagen.mode in ['RGB', 'RGBA', 'L']
        
        # No corrupta
        try:
            imagen.verify()
            validaciones["imagen_integra"] = True
        except:
            validaciones["imagen_integra"] = False
        
        # Reabrir imagen después de verify()
        imagen = Image.open(BytesIO(imagen_data))
        
        # Densidad de píxeles adecuada
        total_pixeles = ancho * alto
        validaciones["densidad_adecuada"] = total_pixeles >= 90000  # Mínimo 300x300
        
        return validaciones
    
    def _analizar_calidad_imagen(self, imagen):
        """Análisis avanzado de calidad de imagen"""
        try:
            # Convertir a RGB si es necesario
            if imagen.mode != 'RGB':
                imagen_rgb = imagen.convert('RGB')
            else:
                imagen_rgb = imagen
            
            # Estadísticas de la imagen
            stats = ImageStat.Stat(imagen_rgb)
            
            # Brillo promedio
            brillo_promedio = sum(stats.mean) / len(stats.mean)
            
            # Contraste (desviación estándar)
            contraste = sum(stats.stddev) / len(stats.stddev)
            
            # Análisis de histograma
            histograma = imagen_rgb.histogram()
            
            # Detectar si la imagen está muy oscura o muy clara
            pixeles_oscuros = sum(histograma[0:85])  # Píxeles muy oscuros
            pixeles_claros = sum(histograma[170:256])  # Píxeles muy claros
            total_pixeles = imagen.size[0] * imagen.size[1]
            
            porcentaje_oscuros = (pixeles_oscuros / total_pixeles) * 100
            porcentaje_claros = (pixeles_claros / total_pixeles) * 100
            
            # Evaluación de calidad
            calidad_score = 100
            
            if brillo_promedio < 50:
                calidad_score -= 20  # Muy oscura
            elif brillo_promedio > 200:
                calidad_score -= 15  # Muy clara
            
            if contraste < 30:
                calidad_score -= 25  # Poco contraste
            
            if porcentaje_oscuros > 60:
                calidad_score -= 20  # Demasiado oscura
            
            if porcentaje_claros > 60:
                calidad_score -= 20  # Demasiado clara
            
            return {
                "calidad_score": max(0, calidad_score),
                "brillo_promedio": round(brillo_promedio, 2),
                "contraste": round(contraste, 2),
                "porcentaje_oscuros": round(porcentaje_oscuros, 2),
                "porcentaje_claros": round(porcentaje_claros, 2),
                "evaluacion": self._evaluar_calidad(calidad_score)
            }
            
        except Exception as e:
            return {
                "error": f"Error en análisis de calidad: {str(e)}",
                "calidad_score": 0,
                "evaluacion": "No se pudo analizar"
            }
    
    def _evaluar_calidad(self, score):
        """Evaluar calidad basada en score"""
        if score >= 90:
            return "Excelente"
        elif score >= 75:
            return "Buena"
        elif score >= 60:
            return "Aceptable"
        elif score >= 40:
            return "Regular"
        else:
            return "Deficiente"
    
    def _generar_sugerencias(self, imagen, imagen_data, validaciones):
        """Generar sugerencias de optimización"""
        sugerencias = []
        
        if not validaciones.get("formato_valido"):
            sugerencias.append("Convertir a formato JPG o PNG")
        
        if not validaciones.get("tamaño_adecuado"):
            tamaño_mb = len(imagen_data) / (1024 * 1024)
            sugerencias.append(f"Reducir tamaño de archivo (actual: {tamaño_mb:.2f}MB, máximo: {self.tamaño_maximo_mb}MB)")
        
        if not validaciones.get("dimensiones_minimas"):
            ancho, alto = imagen.size
            sugerencias.append(f"Aumentar dimensiones (actual: {ancho}x{alto}, mínimo: {self.dimensiones_minimas[0]}x{self.dimensiones_minimas[1]})")
        
        if not validaciones.get("relacion_aspecto_adecuada"):
            sugerencias.append("Ajustar relación de aspecto para que sea más cuadrada o rectangular estándar")
        
        if not validaciones.get("modo_color_adecuado"):
            sugerencias.append(f"Convertir modo de color (actual: {imagen.mode}, recomendado: RGB)")
        
        if not validaciones.get("imagen_integra"):
            sugerencias.append("La imagen parece estar corrupta, verificar integridad del archivo")
        
        # Sugerencias de optimización adicionales
        ancho, alto = imagen.size
        if ancho < self.dimensiones_recomendadas[0] or alto < self.dimensiones_recomendadas[1]:
            sugerencias.append(f"Para mejor calidad, usar dimensiones de {self.dimensiones_recomendadas[0]}x{self.dimensiones_recomendadas[1]} o superiores")
        
        if imagen.format == 'PNG' and imagen.mode == 'RGB':
            sugerencias.append("Considerar convertir a JPG para reducir tamaño de archivo")
        
        return sugerencias
    
    def _generar_sku_desde_imagen(self, archivo_imagen):
        """Generar SKU sugerido basado en el nombre del archivo"""
        try:
            if hasattr(archivo_imagen, 'filename'):
                nombre = archivo_imagen.filename
            else:
                nombre = os.path.basename(archivo_imagen)
            
            # Limpiar nombre
            nombre_limpio = os.path.splitext(nombre)[0]
            nombre_limpio = ''.join(c for c in nombre_limpio if c.isalnum())[:10].upper()
            
            # Generar SKU
            año = datetime.now().year
            return f"AQTL-{nombre_limpio}-{año}"
            
        except:
            # SKU por defecto
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            return f"AQTL-IMG{timestamp[-6:]}-{datetime.now().year}"
    
    def procesar_imagen_para_producto(self, archivo_imagen, sku_producto=None):
        """Procesar imagen y asociarla a un producto"""
        try:
            # Validar imagen
            resultado_validacion = self.validar_imagen_completa(archivo_imagen)
            
            if not resultado_validacion.get("valida"):
                return {
                    "success": False,
                    "error": "Imagen no válida",
                    "validacion": resultado_validacion
                }
            
            # Generar nombre único
            if sku_producto:
                nombre_archivo = f"{sku_producto}_{uuid.uuid4().hex[:8]}"
            else:
                nombre_archivo = f"producto_{uuid.uuid4().hex[:8]}"
            
            # Leer datos de imagen
            if hasattr(archivo_imagen, 'read'):
                imagen_data = archivo_imagen.read()
                archivo_imagen.seek(0)
            else:
                with open(archivo_imagen, 'rb') as f:
                    imagen_data = f.read()
            
            # Abrir y procesar imagen
            imagen = Image.open(BytesIO(imagen_data))
            
            # Optimizar imagen
            imagen_optimizada = self._optimizar_imagen(imagen)
            
            # Guardar imagen optimizada
            ruta_final = os.path.join(self.dir_productos, f"{nombre_archivo}.jpg")
            imagen_optimizada.save(ruta_final, "JPEG", quality=85, optimize=True)
            
            # Generar thumbnail
            thumbnail = imagen_optimizada.copy()
            thumbnail.thumbnail((300, 300), Image.Resampling.LANCZOS)
            ruta_thumbnail = os.path.join(self.dir_productos, f"{nombre_archivo}_thumb.jpg")
            thumbnail.save(ruta_thumbnail, "JPEG", quality=80, optimize=True)
            
            return {
                "success": True,
                "imagen_principal": ruta_final,
                "thumbnail": ruta_thumbnail,
                "validacion": resultado_validacion,
                "nombre_archivo": nombre_archivo
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al procesar imagen: {str(e)}"
            }
    
    def _optimizar_imagen(self, imagen):
        """Optimizar imagen para web"""
        # Convertir a RGB si es necesario
        if imagen.mode in ('RGBA', 'LA', 'P'):
            # Crear fondo blanco para transparencias
            fondo = Image.new('RGB', imagen.size, (255, 255, 255))
            if imagen.mode == 'P':
                imagen = imagen.convert('RGBA')
            fondo.paste(imagen, mask=imagen.split()[-1] if imagen.mode == 'RGBA' else None)
            imagen = fondo
        elif imagen.mode != 'RGB':
            imagen = imagen.convert('RGB')
        
        # Redimensionar si es muy grande
        ancho, alto = imagen.size
        max_dimension = 1200
        
        if ancho > max_dimension or alto > max_dimension:
            if ancho > alto:
                nuevo_ancho = max_dimension
                nuevo_alto = int((alto * max_dimension) / ancho)
            else:
                nuevo_alto = max_dimension
                nuevo_ancho = int((ancho * max_dimension) / alto)
            
            imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
        
        return imagen
    
    def obtener_imagenes_por_validar(self):
        """Obtener lista de imágenes pendientes de validación"""
        try:
            imagenes = []
            for archivo in os.listdir(self.dir_por_validar):
                if archivo.lower().endswith(tuple(self.formatos_permitidos)):
                    ruta_completa = os.path.join(self.dir_por_validar, archivo)
                    stat = os.stat(ruta_completa)
                    
                    imagenes.append({
                        "nombre": archivo,
                        "ruta": ruta_completa,
                        "tamaño_bytes": stat.st_size,
                        "fecha_modificacion": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return imagenes
            
        except Exception as e:
            return []
    
    def asociar_imagen_con_sku(self, nombre_imagen, sku_producto):
        """Asociar imagen validada con SKU de producto"""
        try:
            ruta_origen = os.path.join(self.dir_por_validar, nombre_imagen)
            
            if not os.path.exists(ruta_origen):
                return {
                    "success": False,
                    "error": "Imagen no encontrada"
                }
            
            # Procesar imagen
            resultado = self.procesar_imagen_para_producto(ruta_origen, sku_producto)
            
            if resultado["success"]:
                # Mover imagen original a procesadas
                os.remove(ruta_origen)
                
                return {
                    "success": True,
                    "mensaje": f"Imagen asociada exitosamente al producto {sku_producto}",
                    "rutas": {
                        "imagen_principal": resultado["imagen_principal"],
                        "thumbnail": resultado["thumbnail"]
                    }
                }
            else:
                return resultado
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al asociar imagen: {str(e)}"
            }

# Instancia global del validador
validador = ValidadorImagenes()

if __name__ == "__main__":
    # Test del validador
    print("🔍 Validador de Imágenes TIENDAS TRESMAS")
    print("✅ Sistema inicializado correctamente")
    print(f"📁 Directorios creados:")
    print(f"   - Por validar: {validador.dir_por_validar}")
    print(f"   - Productos: {validador.dir_productos}")
    print(f"   - Temporal: {validador.dir_temp}")

