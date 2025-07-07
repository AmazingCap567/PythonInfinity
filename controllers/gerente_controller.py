from db import conectar_bd
from werkzeug.security import generate_password_hash

def obtener_usuarios():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, usuario, dni, cargo FROM usuarios WHERE activo = TRUE")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios


def registrar_o_actualizar_usuario(usuario, dni, cargo, contrasena):
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario, contrasena FROM usuarios WHERE dni = %s", (dni,))
        existente = cursor.fetchone()

        if existente:
            id_usuario, contrasena_guardada = existente
            # Evitamos rehashear si ya parece un hash válido
            if not contrasena.startswith("pbkdf2:") and not contrasena.startswith("scrypt:"):
                contrasena = generate_password_hash(contrasena, method='scrypt')

            cursor.execute("""
                UPDATE usuarios
                SET usuario = %s, cargo = %s, contrasena = %s, activo = TRUE
                WHERE dni = %s
            """, (usuario, cargo, contrasena, dni))
        else:
            contrasena = generate_password_hash(contrasena, method='scrypt')
            cursor.execute("""
                INSERT INTO usuarios (usuario, dni, cargo, contrasena, activo)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (usuario, dni, cargo, contrasena))

        conn.commit()
        return True
    except Exception as e:
        print("Error al registrar o actualizar usuario:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def obtener_usuario_por_id(id_usuario):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    user = cursor.fetchone()
    conn.close()
    return user

def actualizar_usuario(id_usuario, dni, cargo, contrasena):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET dni = %s, cargo = %s, contrasena = %s
        WHERE id_usuario = %s
    """, (dni, cargo, contrasena, id_usuario))
    conn.commit()
    conn.close()

def eliminar_usuario(id_usuario):
    print(f"⚠️ Eliminando usuario con ID: {id_usuario}")  # log
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET activo = FALSE WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
    except Exception as e:
        print("Error al eliminar usuario:", e)
    finally:
        conn.close()



def eliminar_cliente(id):
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        print(f"Intentando eliminar cliente con id {id}")
        cursor.execute("UPDATE clientes SET activo = FALSE WHERE id_cliente = %s", (id,))
        conn.commit()
        return True
    except Exception as e:
        print("Error al eliminar cliente:", e)
        return False
    finally:
        cursor.close()
        conn.close()



def actualizar_cliente(id, razon_social, ruc, direccion, telefono, nombre, apellidos, correo):
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE clientes
            SET razon_social = %s,
                ruc = %s,
                direccion = %s,
                telefono = %s,
                nombre = %s,
                apellidos = %s,
                correo = %s
            WHERE id_cliente = %s
        """, (razon_social, ruc, direccion, telefono, nombre, apellidos, correo, id))
        conn.commit()
        return True
    except Exception as e:
        print("Error al actualizar cliente:", e)  # Útil para debug
        return False
    finally:
        cursor.close()
        conn.close()

def obtener_cliente_por_id(id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s AND activo = TRUE", (id,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()
    return cliente

def registrar_o_actualizar_cliente(razon_social, ruc, direccion, telefono, nombre, apellidos, correo):
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        # Verificar si ya existe cliente con ese RUC
        cursor.execute("SELECT id_cliente FROM clientes WHERE ruc = %s", (ruc,))
        cliente = cursor.fetchone()

        if cliente:
            # Actualizar datos y reactivar
            cursor.execute("""
                UPDATE clientes
                SET razon_social = %s, direccion = %s, telefono = %s,
                    nombre = %s, apellidos = %s, correo = %s, activo = TRUE
                WHERE ruc = %s
            """, (razon_social, direccion, telefono, nombre, apellidos, correo, ruc))
        else:
            # Insertar nuevo cliente
            cursor.execute("""
                INSERT INTO clientes (razon_social, ruc, direccion, telefono, nombre, apellidos, correo, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
            """, (razon_social, ruc, direccion, telefono, nombre, apellidos, correo))

        conn.commit()
        return True
    except Exception as e:
        print("Error al registrar o actualizar cliente:", e)
        return False
    finally:
        cursor.close()
        conn.close()

# ----------- VENTAS POR FECHA--------------

def obtener_ventas_por_fecha(fecha=None):
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT v.id_venta, v.fecha, v.forma_pago, v.total,
               c.nombre, c.apellidos
        FROM ventas v
        JOIN clientes c ON v.id_cliente = c.id_cliente
        WHERE 1=1
    """
    valores = []

    if fecha:
        query += " AND v.fecha = %s"
        valores.append(fecha)

    query += " ORDER BY v.fecha DESC"
    cursor.execute(query, valores)
    ventas = cursor.fetchall()
    conn.close()
    return ventas

#------------- DETALLE VENTA------------------

def obtener_detalle_venta(id_venta):
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT p.nombre, dv.cantidad, dv.precio_unitario,
               (dv.cantidad * dv.precio_unitario) AS subtotal
        FROM detalle_venta dv
        JOIN productos p ON dv.id_producto = p.id_producto
        WHERE dv.id_venta = %s
    """
    cursor.execute(query, (id_venta,))
    detalles = cursor.fetchall()
    conn.close()
    return detalles


def obtener_productos_mas_vendidos():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vista_productos_mas_vendidos")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos

def obtener_productos_con_stock_bajo(limite=10):
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_producto, nombre, tipo, stock, precio
        FROM productos
        WHERE stock <= %s
        ORDER BY stock ASC
    """, (limite,))
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

