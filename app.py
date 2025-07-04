from flask import Flask, session, redirect, url_for, render_template
from routes.auth import auth_bp
from routes.gerente import gerente_bp
from routes.vendedor import vendedor_bp

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(gerente_bp)
app.register_blueprint(vendedor_bp)

# Ruta del menú principal (solo si está autenticado)

@app.route('/menu')
def menu():
    return render_template('menu.html')

# Ruta raíz: redirige según el cargo
@app.route("/")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    cargo = session.get("cargo")
    if cargo == "Gerente":
        return render_template("gerente/reportes.html")
    elif cargo == "Vendedor":
        return redirect(url_for("vendedor.ventas"))
    else:
        return "Rol desconocido", 403




if __name__ == "__main__":
    app.run(debug=True)
