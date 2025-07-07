from flask import Blueprint, render_template, request, redirect, url_for, flash,session,jsonify
from werkzeug.security import generate_password_hash
from db import conectar_bd
from controllers.gerente_controller import (
    obtener_usuarios,
    registrar_o_actualizar_usuario,
    obtener_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario,
    eliminar_cliente as eliminar_cliente_controller,
    actualizar_cliente,
    obtener_cliente_por_id,
    registrar_o_actualizar_cliente,
    obtener_ventas_por_fecha,
    obtener_detalle_venta,
    obtener_productos_con_stock_bajo
)

from controllers.dashboard_controller import (
    obtener_productos_mas_vendidos,
    obtener_datos_resumen
)


from controllers.productos_controller import (
    listar_productos_con_filtros,
    agregar_producto,
    obtener_producto_por_id,
    eliminar_producto,
    editar_producto
)




gerente_bp = Blueprint('gerente', __name__, url_prefix="/gerente")

# ---------- USUARIOS ----------
@gerente_bp.route('/usuarios')
def usuarios():
    lista = obtener_usuarios()
    return render_template('gerente/usuarios.html', usuarios=lista)

@gerente_bp.route('/usuarios/agregar', methods=['GET', 'POST'])
def agregar_usuario():
    if request.method == 'POST':
        usuario = request.form['usuario']
        dni = request.form['dni']
        cargo = request.form['cargo']
        contrasena = generate_password_hash(request.form['contrasena'])

        if registrar_o_actualizar_usuario(usuario, dni, cargo, contrasena):
            flash('Usuario registrado o actualizado correctamente', 'success')
        else:
            flash('Error al registrar o actualizar el usuario', 'danger')

        return redirect(url_for('gerente.usuarios'))

    return render_template('gerente/agregar_usuario.html')



@gerente_bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = obtener_usuario_por_id(id)

    if request.method == 'POST':
        nuevo_dni = request.form['dni']
        nuevo_cargo = request.form['cargo']
        nueva_contrasena = request.form['contrasena']

        contrasena_hash = generate_password_hash(nueva_contrasena) if nueva_contrasena else usuario[4]

        actualizar_usuario(id, nuevo_dni, nuevo_cargo, contrasena_hash)
        flash("Usuario actualizado correctamente", "success")
        return redirect(url_for('gerente.usuarios'))

    return render_template('gerente/editar_usuario.html', usuario=usuario)

@gerente_bp.route('/usuarios/eliminar/<int:id>')
def eliminar_usuario_route(id):
    if session.get("id_usuario") == id:
        flash("No puedes eliminar tu propia cuenta activa", "danger")
        return redirect(url_for('gerente.usuarios'))

    eliminar_usuario(id)
    flash("Usuario eliminado", "warning")
    return redirect(url_for('gerente.usuarios'))


# ---------- CLIENTES ----------
@gerente_bp.route('/clientes')
def clientes():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE activo = TRUE")
    lista = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('gerente/clientes.html', clientes=lista)


@gerente_bp.route("/clientes/agregar", methods=['GET', 'POST'])
def agregar_cliente():
    if request.method == 'POST':
        razon_social = request.form['razon_social']
        ruc = request.form['ruc']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo = request.form['correo']

        if registrar_o_actualizar_cliente(razon_social, ruc, direccion, telefono, nombre, apellidos, correo):
            flash("Cliente registrado o actualizado correctamente", "success")
        else:
            flash("Ocurrió un error al registrar el cliente", "danger")

        return redirect(url_for('gerente.clientes'))

    return render_template('gerente/agregar_cliente.html')


@gerente_bp.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    if request.method == "POST":
        razon_social = request.form['razon_social']
        ruc = request.form['ruc']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo = request.form['correo']

        if actualizar_cliente(id, razon_social, ruc, direccion, telefono, nombre, apellidos, correo):
            flash("Cliente actualizado correctamente", "success")
        else:
            flash("Error al actualizar cliente", "danger")

        return redirect(url_for('gerente.clientes'))
    else:
        cliente = obtener_cliente_por_id(id)
        if not cliente:
            flash("Cliente no encontrado", "warning")
            return redirect(url_for('gerente.clientes'))

        return render_template("gerente/editar_cliente.html", cliente=cliente)



@gerente_bp.route("/clientes/eliminar/<int:id>")
def eliminar_cliente(id):
    if eliminar_cliente_controller(id):
        flash("Cliente eliminado correctamente", "warning")
    else:
        flash("Error al eliminar cliente", "danger")
    return redirect(url_for('gerente.clientes'))

#--------PRODUCTOS-----------

@gerente_bp.route('/productos', methods=['GET'])
def ver_productos():
    filtros = {
        "nombre": request.args.get("nombre", "").strip(),
        "tipo": request.args.get("tipo", "").strip(),
        "color": request.args.get("color", "").strip(),
        "material": request.args.get("material", "").strip()
    }
    productos = listar_productos_con_filtros(filtros)  # aquí se pasa un argumento
    return render_template('gerente/productos.html', productos=productos, filtros=filtros)




@gerente_bp.route("/productos/agregar", methods=["POST"])
def agregar_producto_route():
    return agregar_producto()

@gerente_bp.route("/productos/eliminar/<int:id_producto>", methods=["POST"])
def eliminar_producto_route(id_producto):
    return eliminar_producto(id_producto)

@gerente_bp.route("/editar_producto", methods=["POST"])
def editar_producto_route():
    return editar_producto()


@gerente_bp.route("/productos/detalle/<int:id_producto>")
def detalle_producto(id_producto):
    producto = obtener_producto_por_id(id_producto)
    return jsonify(producto)


@gerente_bp.route("/reportes/ventas_por_dia", methods=["GET"])
def reporte_ventas_por_dia():
    fecha = request.args.get("fecha")
    ventas = obtener_ventas_por_fecha(fecha)
    total_dia = sum(v['total'] for v in ventas) if ventas else 0.00
    return render_template("gerente/reportes/ventas_por_dia.html", ventas=ventas, fecha=fecha, total_dia=total_dia)


@gerente_bp.route("/reportes/detalle_venta/<int:id_venta>")
def detalle_venta(id_venta):
    detalles = obtener_detalle_venta(id_venta)
    return render_template("gerente/reportes/detalle_venta.html", detalles=detalles, id_venta=id_venta)

@gerente_bp.route("/reportes/productos_mas_vendidos", methods=["GET"])
def productos_mas_vendidos():
    productos = obtener_productos_mas_vendidos()
    return render_template("gerente/reportes/productos_mas_vendidos.html", productos=productos)

@gerente_bp.route("/reportes/inventario_bajo", methods=["GET"])
def inventario_bajo():
    productos = obtener_productos_con_stock_bajo()
    return render_template("gerente/reportes/inventario_bajo.html", productos=productos)


@gerente_bp.route("/reportes/resumen_general", methods=["GET"])
def resumen_general():
    resumen = obtener_datos_resumen()  # función que devolverá todos los datos
    return render_template("gerente/reportes/resumen_general.html", resumen=resumen)


