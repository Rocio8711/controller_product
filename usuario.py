import sqlite3
from acceso_base_datos import conexion


def agregar_usuario(nombre,email,contrasena):
    conexion_bd = conexion()
    if not conexion_bd:
        return
    cursor = conexion_bd.cursor()
    if comprobar_existe_usuario(email):
        print("El usuario ya existe")
        conexion_bd.close()
        return
    cursor.execute("INSERT INTO usuarios (nombre, email, contrasena) VALUES (?, ?, ?)", (nombre, email, contrasena))
    conexion_bd.commit()
    conexion_bd.close()
    print(f"Usuario '{nombre}' creado.")

def comprobar_existe_usuario(email):
    conexion_bd=conexion()
    if not conexion_bd:
        return False
    cursor = conexion_bd.cursor()
    cursor.execute("SELECT * FROM usuarios where email=?",(email,))
    resultado=cursor.fetchone()
    conexion_bd.close()
    return resultado is not None

def comprobar_contrasena(email, contrasena):
    conexion_bd = conexion()
    if not conexion_bd:
        return False
    cursor = conexion_bd.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = ? AND contrasena = ?",(email, contrasena))

    resultado = cursor.fetchone()
    conexion_bd.close()

    return resultado is not None