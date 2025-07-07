from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from db import conectar_bd  # Asegúrate de importar tu función de conexión

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)  # <-- Acceso por nombre de columna
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND activo = TRUE", (usuario,))
        usuario_encontrado = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario_encontrado and check_password_hash(usuario_encontrado['contrasena'], contrasena):
            session["usuario"] = usuario_encontrado['usuario']
            session["id_usuario"] = usuario_encontrado['id_usuario']
            session["cargo"] = usuario_encontrado['cargo']

            if usuario_encontrado['cargo'] == "Gerente":
                return redirect(url_for("gerente.usuarios"))
            else:
                return redirect(url_for("vendedor.ventas"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))
