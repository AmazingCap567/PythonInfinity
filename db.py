import mysql.connector

def conectar_bd():
    return mysql.connector.connect(
        host="NewProyect567.mysql.pythonanywhere-services.com",
        user="NewProyect567",
        password="FNAFa_121",  # Reemplaza esto por la contraseña correcta
        database="NewProyect567$RETROLAX567"
    )
