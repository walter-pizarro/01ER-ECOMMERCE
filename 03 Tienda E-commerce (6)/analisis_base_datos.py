#!/usr/bin/env python3
"""
Análisis de Base de Datos MySQL - Sistema Tienda Virtual
Evaluación de estructura relacional, integridad y optimización
"""

def analizar_esquema_base_datos():
    """
    Análisis completo del esquema de base de datos
    """
    print("=== ANÁLISIS DE ESQUEMA DE BASE DE DATOS ===")
    
    # Estructura de tablas identificada
    tablas = {
        "calificaciones": {
            "campos": ["id", "cantidad", "id_producto", "id_cliente"],
            "proposito": "Sistema de calificaciones de productos",
            "relaciones": ["productos", "clientes"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin índices en FK", "Campo 'cantidad' confuso para calificaciones"]
        },
        "categorias": {
            "campos": ["id", "categoria", "imagen", "estado"],
            "proposito": "Categorización de productos",
            "relaciones": ["productos"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin índice en estado"]
        },
        "clientes": {
            "campos": ["id", "nombre", "apellido", "correo", "telefono", "direccion", 
                      "clave", "perfil", "token", "verify", "estado", "accion", "metodo"],
            "proposito": "Gestión de clientes y usuarios",
            "relaciones": ["pedidos", "ventas", "calificaciones"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin índice único en correo", "Muchos campos opcionales"]
        },
        "colores": {
            "campos": ["id", "nombre", "color", "estado"],
            "proposito": "Atributos de color para productos",
            "relaciones": ["tallas_colores"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin validación de formato color"]
        },
        "configuracion": {
            "campos": ["id", "ruc", "nombre", "telefono", "correo", "direccion", 
                      "mensaje", "whatsapp", "facebook", "twitter", "instagram"],
            "proposito": "Configuración general del sistema",
            "relaciones": [],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Tabla singleton mal diseñada"]
        },
        "descargables": {
            "campos": ["id", "ruta", "id_producto"],
            "proposito": "Archivos descargables de productos",
            "relaciones": ["productos"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin FK definida", "Sin índice en id_producto"]
        },
        "detalle_pedidos": {
            "campos": ["id", "producto", "precio", "cantidad", "atributos", "id_pedido", "id_producto"],
            "proposito": "Detalles de items en pedidos",
            "relaciones": ["pedidos", "productos"],
            "indices": ["PRIMARY KEY (id)", "FOREIGN KEY (id_pedido)"],
            "problemas": ["Duplicación de datos (producto, precio)", "Sin FK a productos"]
        },
        "pedidos": {
            "campos": ["id", "id_transaccion", "metodo", "monto", "estado", "fecha", 
                      "email", "nombre", "apellido", "direccion", "ciudad", "id_cliente", "proceso"],
            "proposito": "Gestión de pedidos de clientes",
            "relaciones": ["clientes", "detalle_pedidos"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin FK a clientes", "Duplicación datos cliente", "Sin índices en estado/fecha"]
        },
        "productos": {
            "campos": ["id", "nombre", "descripcion", "precio", "cantidad", "ventas", 
                      "imagen", "descargable", "estado", "id_categoria"],
            "proposito": "Catálogo de productos",
            "relaciones": ["categorias", "tallas_colores", "descargables"],
            "indices": ["PRIMARY KEY (id)", "FOREIGN KEY (id_categoria)"],
            "problemas": ["Sin índices en estado/precio", "Campo ventas desnormalizado"]
        },
        "sliders": {
            "campos": ["id", "nombre", "imagen", "estado"],
            "proposito": "Imágenes del slider principal",
            "relaciones": [],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin índice en estado"]
        },
        "suscripciones": {
            "campos": ["id", "email", "fecha"],
            "proposito": "Newsletter y suscripciones",
            "relaciones": [],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin índice único en email"]
        },
        "tallas": {
            "campos": ["id", "nombre", "estado"],
            "proposito": "Atributos de talla para productos",
            "relaciones": ["tallas_colores"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin índice en estado"]
        },
        "tallas_colores": {
            "campos": ["id", "id_talla", "id_color", "cantidad", "precio", "id_producto"],
            "proposito": "Variantes de productos (talla + color)",
            "relaciones": ["tallas", "colores", "productos"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin FK definidas", "Sin índices compuestos", "Duplicación de precios"]
        },
        "testimonial": {
            "campos": ["id", "mensaje", "id_cliente"],
            "proposito": "Testimonios de clientes",
            "relaciones": ["clientes"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin FK a clientes"]
        },
        "usuarios": {
            "campos": ["id", "nombres", "apellidos", "correo", "telefono", "direccion", "clave", "perfil", "estado"],
            "proposito": "Usuarios administrativos",
            "relaciones": ["ventas"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Sin índice único en correo", "Duplicación con clientes"]
        },
        "ventas": {
            "campos": ["id", "productos", "total", "fecha", "estado", "id_cliente", "id_usuario"],
            "proposito": "Registro de ventas realizadas",
            "relaciones": ["clientes", "usuarios"],
            "indices": ["PRIMARY KEY (id)"],
            "problemas": ["Campo productos como texto", "Sin FK definidas", "Sin índices en fecha/estado"]
        }
    }
    
    print(f"Total de tablas: {len(tablas)}")
    
    # Análisis por categoría
    categorias_tablas = {
        "Gestión de Productos": ["productos", "categorias", "colores", "tallas", "tallas_colores", "descargables"],
        "Gestión de Clientes": ["clientes", "usuarios"],
        "Procesamiento de Ventas": ["pedidos", "detalle_pedidos", "ventas"],
        "Sistema de Calificaciones": ["calificaciones", "testimonial"],
        "Configuración": ["configuracion", "sliders", "suscripciones"]
    }
    
    for categoria, lista_tablas in categorias_tablas.items():
        print(f"\n{categoria}: {len(lista_tablas)} tablas")
        for tabla in lista_tablas:
            problemas = len(tablas[tabla]["problemas"])
            estado = "❌" if problemas > 2 else "⚠️" if problemas > 0 else "✅"
            print(f"  {estado} {tabla} ({problemas} problemas)")
    
    return tablas

def evaluar_integridad_referencial(tablas):
    """
    Evaluación de integridad referencial y relaciones
    """
    print("\n\n=== EVALUACIÓN DE INTEGRIDAD REFERENCIAL ===")
    
    # FK definidas vs FK necesarias
    fk_definidas = [
        ("detalle_pedidos", "id_pedido", "pedidos", "id"),
        ("productos", "id_categoria", "categorias", "id")
    ]
    
    fk_faltantes = [
        ("calificaciones", "id_producto", "productos", "id"),
        ("calificaciones", "id_cliente", "clientes", "id"),
        ("descargables", "id_producto", "productos", "id"),
        ("pedidos", "id_cliente", "clientes", "id"),
        ("detalle_pedidos", "id_producto", "productos", "id"),
        ("tallas_colores", "id_talla", "tallas", "id"),
        ("tallas_colores", "id_color", "colores", "id"),
        ("tallas_colores", "id_producto", "productos", "id"),
        ("testimonial", "id_cliente", "clientes", "id"),
        ("ventas", "id_cliente", "clientes", "id"),
        ("ventas", "id_usuario", "usuarios", "id")
    ]
    
    print(f"FK definidas: {len(fk_definidas)}/13 (15%)")
    print(f"FK faltantes: {len(fk_faltantes)}/13 (85%)")
    
    print(f"\n--- FK CRÍTICAS FALTANTES ---")
    for tabla_origen, campo_origen, tabla_destino, campo_destino in fk_faltantes:
        print(f"❌ {tabla_origen}.{campo_origen} → {tabla_destino}.{campo_destino}")
    
    # Análisis de integridad de datos
    problemas_integridad = {
        "Duplicación de Datos": [
            "detalle_pedidos.producto (duplica productos.nombre)",
            "detalle_pedidos.precio (duplica productos.precio)",
            "pedidos.email/nombre/apellido (duplica clientes.*)",
            "tallas_colores.precio (duplica productos.precio)"
        ],
        "Campos Desnormalizados": [
            "productos.ventas (debería calcularse)",
            "ventas.productos (debería ser tabla relacionada)",
            "clientes.perfil (URL vs archivo local inconsistente)"
        ],
        "Validaciones Faltantes": [
            "colores.color (formato hexadecimal)",
            "clientes.correo (formato email)",
            "usuarios.correo (formato email)",
            "productos.precio (valores positivos)"
        ]
    }
    
    for categoria, problemas in problemas_integridad.items():
        print(f"\n{categoria}:")
        for problema in problemas:
            print(f"  ⚠️ {problema}")
    
    return fk_faltantes

def analizar_indices_optimizacion(tablas):
    """
    Análisis de índices y optimización de consultas
    """
    print("\n\n=== ANÁLISIS DE ÍNDICES Y OPTIMIZACIÓN ===")
    
    # Índices recomendados basados en consultas comunes
    indices_recomendados = {
        "productos": [
            "INDEX idx_estado (estado)",
            "INDEX idx_categoria (id_categoria)",
            "INDEX idx_precio (precio)",
            "INDEX idx_nombre (nombre)",
            "INDEX idx_estado_categoria (estado, id_categoria)"
        ],
        "pedidos": [
            "INDEX idx_cliente (id_cliente)",
            "INDEX idx_estado (estado)",
            "INDEX idx_fecha (fecha)",
            "INDEX idx_transaccion (id_transaccion)",
            "INDEX idx_proceso (proceso)"
        ],
        "detalle_pedidos": [
            "INDEX idx_pedido (id_pedido)",
            "INDEX idx_producto (id_producto)",
            "INDEX idx_pedido_producto (id_pedido, id_producto)"
        ],
        "clientes": [
            "UNIQUE INDEX idx_correo (correo)",
            "INDEX idx_estado (estado)",
            "INDEX idx_verify (verify)"
        ],
        "ventas": [
            "INDEX idx_cliente (id_cliente)",
            "INDEX idx_usuario (id_usuario)",
            "INDEX idx_fecha (fecha)",
            "INDEX idx_estado (estado)"
        ],
        "calificaciones": [
            "INDEX idx_producto (id_producto)",
            "INDEX idx_cliente (id_cliente)",
            "INDEX idx_producto_cliente (id_producto, id_cliente)"
        ],
        "tallas_colores": [
            "INDEX idx_producto (id_producto)",
            "INDEX idx_talla (id_talla)",
            "INDEX idx_color (id_color)",
            "INDEX idx_producto_talla_color (id_producto, id_talla, id_color)"
        ]
    }
    
    total_indices_actuales = len(tablas)  # Solo PK
    total_indices_recomendados = sum(len(indices) for indices in indices_recomendados.values())
    
    print(f"Índices actuales: {total_indices_actuales} (solo PRIMARY KEY)")
    print(f"Índices recomendados: {total_indices_recomendados}")
    print(f"Déficit de índices: {total_indices_recomendados - total_indices_actuales}")
    
    # Consultas problemáticas identificadas
    consultas_problematicas = [
        {
            "consulta": "SELECT * FROM productos WHERE estado = 1",
            "problema": "Sin índice en estado",
            "impacto": "Escaneo completo de tabla",
            "solucion": "INDEX idx_estado (estado)"
        },
        {
            "consulta": "SELECT * FROM productos WHERE nombre LIKE '%valor%'",
            "problema": "LIKE con % al inicio",
            "impacto": "No puede usar índices",
            "solucion": "Full-text search o índice trigram"
        },
        {
            "consulta": "SELECT SUM(cantidad) FROM calificaciones WHERE id_producto = ?",
            "problema": "Sin índice en id_producto",
            "impacto": "Escaneo completo por cada producto",
            "solucion": "INDEX idx_producto (id_producto)"
        },
        {
            "consulta": "SELECT * FROM pedidos WHERE id_cliente = ? ORDER BY fecha DESC",
            "problema": "Sin índices en id_cliente ni fecha",
            "impacto": "Escaneo + ordenamiento costoso",
            "solucion": "INDEX idx_cliente_fecha (id_cliente, fecha)"
        }
    ]
    
    print(f"\n--- CONSULTAS PROBLEMÁTICAS ---")
    for i, consulta in enumerate(consultas_problematicas, 1):
        print(f"\n{i}. {consulta['consulta']}")
        print(f"   Problema: {consulta['problema']}")
        print(f"   Impacto: {consulta['impacto']}")
        print(f"   Solución: {consulta['solucion']}")
    
    return indices_recomendados

def evaluar_normalizacion():
    """
    Evaluación del nivel de normalización de la base de datos
    """
    print("\n\n=== EVALUACIÓN DE NORMALIZACIÓN ===")
    
    # Análisis por forma normal
    formas_normales = {
        "1NF (Primera Forma Normal)": {
            "cumple": False,
            "violaciones": [
                "ventas.productos contiene JSON/texto con múltiples valores",
                "detalle_pedidos.atributos contiene datos estructurados como texto"
            ]
        },
        "2NF (Segunda Forma Normal)": {
            "cumple": False,
            "violaciones": [
                "detalle_pedidos.producto depende de id_producto, no de la PK completa",
                "detalle_pedidos.precio depende de id_producto, no de la PK completa"
            ]
        },
        "3NF (Tercera Forma Normal)": {
            "cumple": False,
            "violaciones": [
                "pedidos contiene datos del cliente (nombre, apellido, email) que dependen de id_cliente",
                "productos.ventas es un campo calculado que depende de otras tablas"
            ]
        }
    }
    
    for forma, info in formas_normales.items():
        estado = "✅" if info["cumple"] else "❌"
        print(f"\n{estado} {forma}: {'Cumple' if info['cumple'] else 'No cumple'}")
        if not info["cumple"]:
            for violacion in info["violaciones"]:
                print(f"   • {violacion}")
    
    # Recomendaciones de normalización
    recomendaciones = [
        "Crear tabla 'detalle_ventas' para reemplazar ventas.productos",
        "Crear tabla 'atributos_pedido' para estructurar detalle_pedidos.atributos",
        "Eliminar duplicación de datos de cliente en tabla pedidos",
        "Calcular productos.ventas dinámicamente o usar triggers",
        "Separar configuración en múltiples tablas especializadas"
    ]
    
    print(f"\n--- RECOMENDACIONES DE NORMALIZACIÓN ---")
    for i, rec in enumerate(recomendaciones, 1):
        print(f"{i}. {rec}")
    
    return formas_normales

def calcular_metricas_rendimiento():
    """
    Cálculo de métricas estimadas de rendimiento
    """
    print("\n\n=== MÉTRICAS DE RENDIMIENTO ESTIMADAS ===")
    
    # Estimaciones basadas en estructura actual
    estimaciones = {
        "Productos": {
            "registros_estimados": 1000,
            "consultas_frecuentes": ["SELECT por categoría", "SELECT por estado", "Búsqueda por nombre"],
            "tiempo_sin_indices": "500ms",
            "tiempo_con_indices": "5ms",
            "mejora": "100x"
        },
        "Pedidos": {
            "registros_estimados": 5000,
            "consultas_frecuentes": ["SELECT por cliente", "SELECT por fecha", "SELECT por estado"],
            "tiempo_sin_indices": "800ms",
            "tiempo_con_indices": "8ms",
            "mejora": "100x"
        },
        "Calificaciones": {
            "registros_estimados": 10000,
            "consultas_frecuentes": ["SUM por producto", "COUNT por producto"],
            "tiempo_sin_indices": "1200ms",
            "tiempo_con_indices": "10ms",
            "mejora": "120x"
        }
    }
    
    for tabla, info in estimaciones.items():
        print(f"\n{tabla}:")
        print(f"  Registros estimados: {info['registros_estimados']:,}")
        print(f"  Tiempo sin índices: {info['tiempo_sin_indices']}")
        print(f"  Tiempo con índices: {info['tiempo_con_indices']}")
        print(f"  Mejora potencial: {info['mejora']}")
    
    # Cálculo de impacto en página principal
    print(f"\n--- IMPACTO EN PÁGINA PRINCIPAL ---")
    productos_homepage = 8
    consultas_por_producto = 2  # SUM y COUNT calificaciones
    tiempo_actual = productos_homepage * consultas_por_producto * 120  # ms sin índices
    tiempo_optimizado = productos_homepage * consultas_por_producto * 1  # ms con índices
    
    print(f"Tiempo actual: {tiempo_actual}ms")
    print(f"Tiempo optimizado: {tiempo_optimizado}ms")
    print(f"Mejora: {tiempo_actual // tiempo_optimizado}x más rápido")

if __name__ == "__main__":
    print("AUDITORÍA TÉCNICA - ANÁLISIS DE BASE DE DATOS MYSQL")
    print("=" * 60)
    
    tablas = analizar_esquema_base_datos()
    fk_faltantes = evaluar_integridad_referencial(tablas)
    indices_recomendados = analizar_indices_optimizacion(tablas)
    formas_normales = evaluar_normalizacion()
    calcular_metricas_rendimiento()
    
    print("\n\n=== RESUMEN DE EVALUACIÓN DE BASE DE DATOS ===")
    print("1. Esquema con 16 tablas, diseño básico funcional")
    print("2. Integridad referencial crítica: 85% FK faltantes")
    print("3. Normalización deficiente: No cumple 1NF, 2NF, 3NF")
    print("4. Índices insuficientes: Solo PRIMARY KEYs")
    print("5. Rendimiento degradado: Consultas sin optimizar")
    print("6. Duplicación de datos: Múltiples violaciones")
    
    print("\n🚨 RECOMENDACIÓN: Reestructuración de BD urgente")

