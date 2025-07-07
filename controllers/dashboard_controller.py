from db import conectar_bd

def obtener_ventas_por_dia():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT fecha, SUM(total) AS total_ventas
        FROM ventas
        GROUP BY fecha
        ORDER BY fecha DESC
        LIMIT 7
    """)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def obtener_formas_pago_mas_usadas():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT forma_pago, COUNT(*) AS cantidad
        FROM ventas
        GROUP BY forma_pago
        ORDER BY cantidad DESC
    """)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def obtener_productos_mas_vendidos():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.nombre, SUM(dv.cantidad) AS cantidad_vendida
        FROM detalle_venta dv
        JOIN productos p ON dv.id_producto = p.id_producto
        GROUP BY p.nombre
        ORDER BY cantidad_vendida DESC
        LIMIT 5
    """)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def obtener_categorias_mas_vendidas():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.tipo AS categoria, SUM(dv.cantidad) AS total_vendidos
        FROM detalle_venta dv
        JOIN productos p ON dv.id_producto = p.id_producto
        GROUP BY p.tipo
        ORDER BY total_vendidos DESC
    """)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def obtener_vendedores_con_mas_ventas():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.usuario, COUNT(v.id_venta) AS cantidad_ventas
        FROM ventas v
        JOIN usuarios u ON v.id_usuario = u.id_usuario
        GROUP BY u.usuario
        ORDER BY cantidad_ventas DESC
    """)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def obtener_datos_resumen():
    conn = conectar_bd()
    cursor = conn.cursor()

    # Ventas por día (últimos 7 días)
    cursor.execute("""
        SELECT fecha, SUM(total) AS total_dia
        FROM ventas
        GROUP BY fecha
        ORDER BY fecha DESC
        LIMIT 7;
    """)
    ventas_dia = cursor.fetchall()

    # Formas de pago más usadas
    cursor.execute("""
        SELECT forma_pago, COUNT(*) AS cantidad
        FROM ventas
        GROUP BY forma_pago;
    """)
    formas_pago = cursor.fetchall()

    # Productos más vendidos
    cursor.execute("""
        SELECT p.nombre, SUM(dv.cantidad) AS total
        FROM detalle_venta dv
        JOIN productos p ON dv.id_producto = p.id_producto
        GROUP BY p.nombre
        ORDER BY total DESC
        LIMIT 5;
    """)
    productos = cursor.fetchall()

    # Categorías más vendidas
    cursor.execute("""
        SELECT tipo, SUM(dv.cantidad) AS total
        FROM detalle_venta dv
        JOIN productos p ON dv.id_producto = p.id_producto
        GROUP BY tipo
        ORDER BY total DESC
        LIMIT 5;
    """)
    categorias = cursor.fetchall()

    # Vendedores con más ventas
    cursor.execute("""
        SELECT u.usuario, COUNT(v.id_venta) AS total
        FROM ventas v
        JOIN usuarios u ON v.id_usuario = u.id_usuario
        GROUP BY u.usuario
        ORDER BY total DESC
        LIMIT 5;
    """)
    vendedores = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "ventas_dia": ventas_dia,
        "formas_pago": formas_pago,
        "productos": productos,
        "categorias": categorias,
        "vendedores": vendedores
    }

