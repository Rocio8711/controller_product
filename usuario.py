import sqlite3
from InicializacionBaseDatos.acceso_base_datos import conexion


def login(email, contrasena):
    conn = conexion()
    cursor = conn.cursor()

    # buscamos usuario que coincida con email y contrasena
    cursor.execute(
        "SELECT id, nombre FROM usuarios WHERE email = ? AND contrasena = ?",
        (email, contrasena)
    )

    usuario = cursor.fetchone()
    conn.close()

    return usuario
def agregar_usuario(nombre, email, contrasena):
    conn = conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    if cursor.fetchone():
        print("El usuario ya existe")
        conn.close()
        return
    # insertamos nuevo usuario en la base de datos
    cursor.execute(
        "INSERT INTO usuarios (nombre, email, contrasena) VALUES (?, ?, ?)",
        (nombre, email, contrasena)
    )
    conn.commit()




