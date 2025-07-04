from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import conectar_bd  # Corrección aplicada
from controllers.vendedor_controller import (
    buscar_cliente,
    registrar_cliente,
    ingresar_cliente,
    agregar_producto_carrito,
    registrar_venta,
    limpiar_formulario,
    eliminar_producto_carrito
)


vendedor_bp = Blueprint('vendedor', __name__, url_prefix='/vendedor')

@vendedor_bp.route('/ventas')
def ventas():
    from db import conectar_bd
    conn = conectar_bd()
    cursor = conn.cursor()

    # Obtener productos
    cursor.execute("SELECT id_producto, nombre, precio FROM productos")
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

@vendedor_bp.route('/agregar_producto', methods=['POST'])
def agregar_producto_route():
    return agregar_producto_carrito()

@vendedor_bp.route('/registrar_venta', methods=['POST'])
def registrar_venta_route():
    return registrar_venta()

@vendedor_bp.route('/limpiar_formulario', methods=['POST'])
def limpiar_formulario_route():
    return limpiar_formulario()

@vendedor_bp.route('/eliminar_producto', methods=['POST'])
def eliminar_producto_route():
    return eliminar_producto_carrito()

@vendedor_bp.route("/historial_ventas", methods=["GET", "POST"])
def historial_ventas():
    # Ya no se valida si inició sesión
    conn = conectar_bd()
    cursor = conn.cursor()

    id_usuario = session.get("id_usuario")  # Suponemos que está garantizado por login

    # Filtros desde el formulario
    fecha_inicio = request.form.get("fecha_inicio")
    fecha_fin = request.form.get("fecha_fin")
    min_total = request.form.get("min_total")
    max_total = request.form.get("max_total")

    query = """
        SELECT DATE(v.fecha) AS fecha, SUM(v.total) AS total_diario
        FROM ventas v
        WHERE v.id_usuario = %s
    """
    params = [id_usuario]

    if fecha_inicio and fecha_fin:
        query += " AND v.fecha BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])

    if min_total:
        query += " AND v.total >= %s"
        params.append(min_total)

    if max_total:
        query += " AND v.total <= %s"
        params.append(max_total)

    query += " GROUP BY DATE(v.fecha) ORDER BY fecha DESC"

    cursor.execute(query, params)
    ventas = cursor.fetchall()

    return render_template("vendedor/historial_ventas.html", ventas=ventas)
