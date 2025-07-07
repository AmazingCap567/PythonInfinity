from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from db import conectar_bd  # Corrección aplicada

from controllers.vendedor_controller import (
    buscar_cliente,
    registrar_cliente,
    ingresar_cliente,
    agregar_producto_carrito,
    registrar_venta,
    limpiar_formulario,
    eliminar_producto_carrito,
    obtener_historial_ventas
)


vendedor_bp = Blueprint('vendedor', __name__, url_prefix='/vendedor')

@vendedor_bp.route('/ventas')
def ventas():
    from db import conectar_bd
    conn = conectar_bd()
    cursor = conn.cursor()

    # Obtener productos con stock
    cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos")
    productos = cursor.fetchall()
    conn.close()

    # Variables desde la sesión
    cliente = session.get("cliente_actual")
    carrito = session.get("carrito", [])

    # Calcular totales
    subtotal = sum(item["subtotal"] for item in carrito)
    igv = round(subtotal * 0.18, 2)
    total = round(subtotal + igv, 2)

    return render_template(
        'vendedor/ventas.html',
        productos=productos,
        cliente=cliente,
        carrito=carrito,
        subtotal=subtotal,
        igv=igv,
        total=total,
        cliente_confirmado=cliente
    )


@vendedor_bp.route('/buscar_cliente', methods=['POST'])
def buscar_cliente_route():
    return buscar_cliente()

@vendedor_bp.route('/registrar_cliente', methods=['POST'])
def registrar_cliente_route():
    return registrar_cliente()

@vendedor_bp.route('/ingresar_cliente', methods=['POST'])
def ingresar_cliente_route():
    return ingresar_cliente()

@vendedor_bp.route("/api/buscar_clientes", methods=["POST"])
def api_buscar_clientes():
    termino = request.form.get("termino", "").strip()

    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    if termino:
        query = """
            SELECT * FROM clientes
            WHERE activo = TRUE AND (
                nombre LIKE %s OR
                apellidos LIKE %s OR
                ruc LIKE %s
            )
        """
        like_term = f"%{termino}%"
        cursor.execute(query, (like_term, like_term, like_term))
    else:
        cursor.execute("SELECT * FROM clientes WHERE activo = TRUE")

    clientes = cursor.fetchall()
    conn.close()
    return jsonify(clientes)





@vendedor_bp.route('/agregar_producto', methods=['POST'])
def agregar_producto_route():
    return agregar_producto_carrito()

@vendedor_bp.route('/registrar_venta', methods=['POST'])
def registrar_venta_route():
    return registrar_venta()

@vendedor_bp.route('/limpiar_formulario', methods=["POST"])
def limpiar_formulario_route():
    session.pop("cliente", None)
    session.pop("carrito", None)
    return redirect(url_for('vendedor.ventas'))


@vendedor_bp.route('/eliminar_producto', methods=['POST'])
def eliminar_producto_route():
    return eliminar_producto_carrito()

@vendedor_bp.route("/historial_ventas", methods=["GET"])
def historial_ventas():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    id_usuario = session.get("id_usuario")

    # Filtros desde request.args (GET)
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    min_total = request.args.get("min_total")
    max_total = request.args.get("max_total")

    query = """
        SELECT fecha, SUM(total_diario) AS total_dia, SUM(cantidad_ventas) AS cantidad
        FROM vista_ventas_diarias
        WHERE id_usuario = %s
    """
    params = [id_usuario]

    if fecha_inicio and fecha_fin:
        query += " AND fecha BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])

    if min_total:
        query += " AND total_diario >= %s"
        params.append(min_total)

    if max_total:
        query += " AND total_diario <= %s"
        params.append(max_total)

    # Agrupamos también por id_usuario para cumplir con SQL ANSI
    query += " GROUP BY fecha, id_usuario ORDER BY fecha DESC"

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()

    return render_template("vendedor/historial_ventas.html", resultados=resultados)

@vendedor_bp.route("/ventas_por_dia/<fecha>")
def ventas_por_dia(fecha):
    id_usuario = session.get("id_usuario")
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT v.id_venta, CONCAT(c.nombre, ' ', c.apellidos) AS cliente,
               v.forma_pago, v.total
        FROM ventas v
        JOIN clientes c ON v.id_cliente = c.id_cliente
        WHERE DATE(v.fecha) = %s AND v.id_usuario = %s
        ORDER BY v.id_venta DESC
    """
    cursor.execute(query, (fecha, id_usuario))
    ventas = cursor.fetchall()
    conn.close()

    return render_template("vendedor/ventas_por_dia.html", fecha=fecha, ventas=ventas)

@vendedor_bp.route("/productos_por_venta/<int:id_venta>")
def productos_por_venta(id_venta):
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT p.nombre, p.tipo, p.color, p.material,
               dv.cantidad, dv.precio_unitario,
               dv.cantidad * dv.precio_unitario AS subtotal
        FROM detalle_venta dv
        JOIN productos p ON dv.id_producto = p.id_producto
        WHERE dv.id_venta = %s
    """
    cursor.execute(query, (id_venta,))
    productos = cursor.fetchall()
    conn.close()

    return render_template("vendedor/productos_por_venta.html", productos=productos)

@vendedor_bp.route('/consultar_stock', methods=['GET'])
def consultar_stock():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_producto, nombre, descripcion, tipo, precio, stock, color, material
        FROM productos
        ORDER BY nombre
    """)
    productos = cursor.fetchall()

    conn.close()
    return render_template('vendedor/stock_productos.html', productos=productos)

@vendedor_bp.route("/clientes", methods=["GET"])
def clientes():
    termino = request.args.get("buscar", "").strip()

    conn = conectar_bd()
    cursor = conn.cursor()

    if termino:
        query = """
            SELECT * FROM clientes
            WHERE activo = TRUE AND (
                nombre LIKE %s OR
                apellidos LIKE %s OR
                ruc LIKE %s
            )
        """
        like_term = f"%{termino}%"
        cursor.execute(query, (like_term, like_term, like_term))
    else:
        cursor.execute("SELECT * FROM clientes WHERE activo = TRUE")

    clientes = cursor.fetchall()
    conn.close()

    return render_template("vendedor/clientes.html", clientes=clientes, buscar=termino)





