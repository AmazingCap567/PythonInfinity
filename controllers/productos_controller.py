# --- controllers/gerente_controller.py ---
from flask import request, redirect, url_for, flash, jsonify
from db import conectar_bd

def listar_productos_con_filtros(filtros):
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM productos WHERE 1=1"
    valores = []

    if filtros.get("nombre"):
        query += " AND nombre LIKE %s"
        valores.append(f"%{filtros['nombre']}%")
    if filtros.get("tipo"):
        query += " AND tipo LIKE %s"
        valores.append(f"%{filtros['tipo']}%")
    if filtros.get("color"):
        query += " AND color LIKE %s"
        valores.append(f"%{filtros['color']}%")
    if filtros.get("material"):
        query += " AND material LIKE %s"
        valores.append(f"%{filtros['material']}%")

    query += " ORDER BY nombre"

    cursor.execute(query, valores)
    productos = cursor.fetchall()
    conn.close()
    return productos

def obtener_producto_por_id(id_producto):
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return producto

def agregar_producto():
    data = request.json
    conn = conectar_bd()
    cursor = conn.cursor()
    query = """
        INSERT INTO productos (nombre, descripcion, tipo, precio, stock, color, material)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    valores = (
        data.get("nombre"),
        data.get("descripcion"),
        data.get("tipo"),
        data.get("precio"),
        data.get("stock"),
        data.get("color"),
        data.get("material")
    )
    cursor.execute(query, valores)
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Producto agregado exitosamente"})

def eliminar_producto():
    id_producto = request.args.get("id")
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET stock = 0 WHERE id_producto = %s", (id_producto,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Stock puesto en 0"})


def editar_producto():
    data = request.json
    id_producto = data.get("id_producto")

    conn = conectar_bd()
    cursor = conn.cursor()
    query = """
        UPDATE productos
        SET nombre=%s, descripcion=%s, tipo=%s, precio=%s, stock=%s, color=%s, material=%s
        WHERE id_producto = %s
    """
    valores = (
        data.get("nombre"),
        data.get("descripcion"),
        data.get("tipo"),
        data.get("precio"),
        data.get("stock"),
        data.get("color"),
        data.get("material"),
        id_producto
    )
    cursor.execute(query, valores)
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Producto actualizado"})

