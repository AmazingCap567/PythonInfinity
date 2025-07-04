from flask import Blueprint, render_template, session, redirect, url_for

gerente_bp = Blueprint('gerente', __name__, url_prefix='/gerente')

@gerente_bp.route('/reportes')
def reportes():
    if "usuario" not in session or session.get("cargo") != "Gerente":
        return redirect(url_for("auth.login"))
    return render_template("gerente/reportes.html")

@gerente_bp.route('/agregar_cliente', methods=["GET", "POST"])
def agregar_cliente():
    if request.method == "POST":
        # registrar nuevo cliente en la base de datos
        pass
    return render_template("gerente/agregar_cliente.html")
