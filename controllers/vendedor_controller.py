from flask import request, session, jsonify, redirect, url_for, flash
from db import conectar_bd

def buscar_cliente():
    termino = request.form.get("termino", "").strip()
    conn = conectar_bd()
    cursor = conn.cursor()

    query = """
        SELECT id_cliente, nombre, apellidos, ruc, correo, direccion, razon_social
        FROM clientes
        WHERE nombre LIKE %s OR ruc LIKE %s
    """
    valores = (f"%{termino}%", f"%{termino}%")
    cursor.execute(query, valores)

    rows = cursor.fetchall()
    conn.close()

    clientes = [{
        "id_cliente": row[0],
        "nombre": row[1],
        "apellidos": row[2],
        "ruc": row[3],
        "correo": row[4],
        "direccion": row[5],
        "razon_social": row[6]
    } for row in rows]

    return jsonify(clientes)

def registrar_cliente():
    data = request.form
    if not (data.get("nombre") and data.get("apellidos") and data.get("ruc")):
        flash("Nombre, Apellidos y RUC son obligatorios", "danger")
        return redirect(url_for('vendedor.ventas'))

    conn = conectar_bd()
    cursor = conn.cursor()
    query = """
        INSERT INTO clientes (nombre, apellidos, ruc, direccion, razon_social, correo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    valores = (
        data["nombre"], data["apellidos"], data["ruc"],
        data.get("direccion") or None,
        data.get("razon_social") or None,
        data.get("correo") or None
    )
    cursor.execute(query, valores)
    conn.commit()
    conn.close()
    flash("Cliente registrado con éxito", "success")
    return redirect(url_for('vendedor.ventas'))

def ingresar_cliente():
    id_cliente = request.form.get("cod_cliente")
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
    cliente = cursor.fetchone()
    conn.close()

    if cliente:
        session["cliente_actual"] = cliente
        return redirect(url_for("vendedor.ventas"))
    else:
        flash("El cliente no existe en la base de datos.", "danger")
        return redirect(url_for("vendedor.ventas"))

def agregar_producto_carrito():
    id_producto = request.form.get("id_producto")
    cantidad = int(request.form.get("cantidad", 1))

    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
    producto = cursor.fetchone()
    conn.close()

    if producto:
        item = {
            "id_producto": producto["id_producto"],
            "nombre": producto["nombre"],
            "precio_unitario": float(producto["precio"]),
            "cantidad": cantidad,
            "subtotal": cantidad * float(producto["precio"])
        }

        carrito = session.get("carrito", [])
        carrito.append(item)
        session["carrito"] = carrito

    return redirect(url_for("vendedor.ventas"))

def registrar_venta():
    cliente = session.get("cliente_actual")
    carrito = session.get("carrito", [])
    id_usuario = session.get("id_usuario")  # <-- OBTIENE el usuario logueado

    if not cliente or not carrito:
        flash("Debe ingresar un cliente y al menos un producto.", "warning")
        return redirect(url_for("vendedor.ventas"))

    total = sum(item["subtotal"] for item in carrito)
    forma_pago = request.form.get("forma_pago")

    conn = conectar_bd()
    cursor = conn.cursor()

    # INSERT con id_usuario
    cursor.execute("""
        INSERT INTO ventas (id_cliente, fecha, forma_pago, total, id_usuario)
        VALUES (%s, NOW(), %s, %s, %s)
    """, (
        cliente["id_cliente"],
        forma_pago,
        total,
        id_usuario  # <-- Agregado aquí
    ))
    id_venta = cursor.lastrowid

    for item in carrito:
        cursor.execute("""
            INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
        """, (
            id_venta, item["id_producto"], item["cantidad"], item["precio_unitario"]
        ))

    conn.commit()
    conn.close()

    session.pop("cliente_actual", None)
    session.pop("carrito", None)
    flash("Venta registrada correctamente.", "success")
    return redirect(url_for("vendedor.ventas"))

def limpiar_formulario():
    session.pop("cliente_actual", None)
    session.pop("carrito", None)
    flash("Formulario limpiado", "info")
    return redirect(url_for("vendedor.ventas"))

def eliminar_producto_carrito():
    index = int(request.form.get("index", -1))
    carrito = session.get("carrito", [])
    if 0 <= index < len(carrito):
        carrito.pop(index)
        session["carrito"] = carrito
    return redirect(url_for("vendedor.ventas"))
