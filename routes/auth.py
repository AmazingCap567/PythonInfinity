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
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
        usuario_encontrado = cursor.fetchone()

        if usuario_encontrado and check_password_hash(usuario_encontrado[4], contrasena):
            session["usuario"] = usuario_encontrado[1]  # usuario
            session["id_usuario"] = usuario_encontrado[0]  # id_usuario
            session["cargo"] = usuario_encontrado[3]  # cargo

            if usuario_encontrado[3] == "Gerente":
                return redirect(url_for("gerente.dashboard"))
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
