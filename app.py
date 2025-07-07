from flask import Flask, session, redirect, url_for, render_template
from routes.auth import auth_bp
from routes.gerente import gerente_bp
from routes.vendedor import vendedor_bp

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Registrar blueprints con prefijos únicos
app.register_blueprint(auth_bp, url_prefix="/auth")         # /auth/login, /auth/logout
app.register_blueprint(gerente_bp, url_prefix="/gerente")   # /gerente/dashboard
app.register_blueprint(vendedor_bp, url_prefix="/vendedor") # /vendedor/ventas

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
        return redirect(url_for("gerente.usuarios"))  # esto debe coincidir con el nombre de la función en gerente_bp
    elif cargo == "Vendedor":
        return redirect(url_for("vendedor.ventas"))
    else:
        return "Rol desconocido", 403

if __name__ == "__main__":
    app.run(debug=True)
