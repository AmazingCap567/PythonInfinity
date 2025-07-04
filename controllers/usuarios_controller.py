from db import conectar_bd

def verificar_usuario(usuario, contrasena):
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s"
    cursor.execute(query, (usuario, contrasena))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return {
            "usuario": user["usuario"],
            "cargo": user["cargo"]
        }
    return None
