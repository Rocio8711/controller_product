import sqlite3
from datetime import datetime, timedelta
import random
import shutil
import os

DB_NAME = "controllerproduct.db"

# =====================================================
# CONEXIÓN
# =====================================================
def conexion():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# =====================================================
# USUARIOS
# =====================================================
def insertar_usuarios(cursor):
    usuarios = [
        ("Ana", "ana@gmail.com", "1234"),
        ("Luis", "luis@gmail.com", "1234"),
        ("Marta", "marta@gmail.com", "1234"),
        ("Carlos", "carlos@gmail.com", "1234"),
        ("Nala","1","1"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO usuarios (nombre, email, contrasena) VALUES (?, ?, ?)",
        usuarios
    )

# =====================================================
# PRODUCTOS (AMPLIADOS)
# =====================================================
def insertar_productos(cursor):
    productos = [
        ("Harina", 10, "kg", 2),
        ("Leche", 20, "litros", 5),
        ("Huevos", 30, "unidades", 10),
        ("Azúcar", 15, "kg", 3),
        ("Sal", 5, "kg", 1),
        ("Aceite", 10, "litros", 2),
        ("Pollo", 10, "kg", 2),
        ("Arroz", 20, "kg", 5),
        ("Tomate", 15, "kg", 3),
        ("Queso", 8, "kg", 2),
        ("Pan", 20, "unidades", 5),
        ("Chocolate", 10, "kg", 2),
        ("Mantequilla", 5, "kg", 1),
        ("Patatas", 25, "kg", 5),

        # NUEVOS
        ("Agua", 100, "litros", 10),
        ("Lentejas", 10, "kg", 2),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?, ?, ?, ?)",
        productos
    )

# =====================================================
# RECETAS (30)
# =====================================================
def insertar_recetas(cursor):
    recetas = [
        "Tortilla","Paella","Pizza","Bizcocho","Pancakes","Galletas","Ensalada",
        "Sopa","Arroz con pollo","Pasta","Hamburguesa","Sandwich","Croquetas",
        "Tarta","Brownie","Batido","Lentejas","Quiche","Empanada","Crepes",
        "Arroz blanco","Pollo al horno","Patatas fritas","Huevos revueltos",
        "Pan con tomate","Quesadilla","Arroz dulce","Chocolate caliente",
        "Tostadas","Ensalada de arroz"
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO recetas (nombre) VALUES (?)",
        [(r,) for r in recetas]
    )

# =====================================================
# INGREDIENTES REALISTAS
# =====================================================
def insertar_receta_ingredientes(cursor):
    cursor.execute("SELECT id, nombre FROM recetas")
    recetas = {nombre: id for id, nombre in cursor.fetchall()}

    cursor.execute("SELECT id, nombre FROM productos")
    productos = {nombre: id for id, nombre in cursor.fetchall()}

    recetas_ingredientes = {
        "Tortilla": [("Huevos",4,"unidades"),("Patatas",0.5,"kg"),("Aceite",0.1,"litros")],
        "Paella": [("Arroz",0.3,"kg"),("Pollo",0.5,"kg"),("Tomate",0.2,"kg")],
        "Pizza": [("Harina",0.3,"kg"),("Tomate",0.2,"kg"),("Queso",0.2,"kg")],
        "Bizcocho": [("Harina",0.25,"kg"),("Huevos",3,"unidades"),("Azúcar",0.2,"kg")],
        "Pancakes": [("Harina",0.2,"kg"),("Huevos",2,"unidades"),("Leche",0.3,"litros")],
        "Galletas": [("Harina",0.3,"kg"),("Azúcar",0.2,"kg"),("Mantequilla",0.15,"kg")],
        "Ensalada": [("Tomate",0.3,"kg"),("Queso",0.1,"kg")],
        "Sopa": [("Agua",1,"litros"),("Pollo",0.3,"kg")],
        "Arroz con pollo": [("Arroz",0.3,"kg"),("Pollo",0.5,"kg")],
        "Pasta": [("Harina",0.3,"kg"),("Tomate",0.2,"kg")],
        "Hamburguesa": [("Pan",2,"unidades"),("Pollo",0.2,"kg")],
        "Sandwich": [("Pan",2,"unidades"),("Queso",0.1,"kg")],
        "Croquetas": [("Harina",0.2,"kg"),("Leche",0.5,"litros"),("Pollo",0.3,"kg")],
        "Tarta": [("Harina",0.3,"kg"),("Huevos",3,"unidades")],
        "Brownie": [("Chocolate",0.3,"kg"),("Huevos",3,"unidades")],
        "Batido": [("Leche",0.5,"litros"),("Azúcar",0.05,"kg")],
        "Lentejas": [("Lentejas",0.3,"kg")],
        "Quiche": [("Huevos",3,"unidades"),("Queso",0.2,"kg")],
        "Empanada": [("Harina",0.4,"kg"),("Pollo",0.3,"kg")],
        "Crepes": [("Harina",0.2,"kg"),("Leche",0.3,"litros")],
        "Arroz blanco": [("Arroz",0.3,"kg")],
        "Pollo al horno": [("Pollo",1,"kg")],
        "Patatas fritas": [("Patatas",0.5,"kg")],
        "Huevos revueltos": [("Huevos",3,"unidades")],
        "Pan con tomate": [("Pan",2,"unidades"),("Tomate",0.2,"kg")],
        "Quesadilla": [("Queso",0.2,"kg"),("Pan",2,"unidades")],
        "Arroz dulce": [("Arroz",0.2,"kg"),("Leche",0.5,"litros")],
        "Chocolate caliente": [("Leche",0.5,"litros"),("Chocolate",0.2,"kg")],
        "Tostadas": [("Pan",2,"unidades"),("Mantequilla",0.05,"kg")],
        "Ensalada de arroz": [("Arroz",0.3,"kg"),("Tomate",0.2,"kg")]
    }

    datos = []

    for receta, lista in recetas_ingredientes.items():
        if receta in recetas:
            for nombre, cantidad, unidad in lista:
                if nombre in productos:
                    datos.append((recetas[receta], productos[nombre], cantidad, unidad))

    cursor.executemany("""
        INSERT OR IGNORE INTO receta_ingredientes
        (receta_id, producto_id, cantidad, unidad)
        VALUES (?, ?, ?, ?)
    """, datos)

# =====================================================
# LISTA COMPRA
# =====================================================
def insertar_lista_compras(cursor):
    cursor.execute("SELECT id FROM productos")
    productos = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM usuarios")
    usuarios = [row[0] for row in cursor.fetchall()]

    lista = []
    for _ in range(10):
        lista.append((
            random.choice(productos),
            random.randint(1, 5),
            random.choice(["kg", "litros", "unidades"]),
            random.choice([0, 1]),
            random.choice(usuarios)
        ))

    cursor.executemany("""
        INSERT INTO lista_compras 
        (producto_id, cantidad, unidad, comprado, usuario_id_asignado)
        VALUES (?, ?, ?, ?, ?)
    """, lista)

# =====================================================
# RECETAS PENDIENTES
# =====================================================
def insertar_recetas_pendientes(cursor):
    cursor.execute("SELECT id FROM recetas")
    recetas = [row[0] for row in cursor.fetchall()]

    pendientes = []
    for r in recetas:
        fecha = datetime.now() + timedelta(days=random.randint(1, 10))
        pendientes.append((r, fecha.strftime("%d/%m/%Y"), random.choice([0, 1])))

    cursor.executemany("""
        INSERT INTO recetas_pendientes 
        (receta_id, fecha_planificada, completada)
        VALUES (?, ?, ?)
    """, pendientes)


#=================================================
#Copiar base a padre
#=================================================

def copiar_bd_al_padre():
    origen = DB_NAME
    destino = os.path.join("..", DB_NAME)

    try:
        shutil.copy2(origen, destino)
        print("📁 Base de datos copiada al directorio padre")
    except Exception as e:
        print(f"❌ Error al copiar la BD: {e}")


# =====================================================
# EJECUCIÓN
# =====================================================
def generar_datos():
    conn = conexion()
    cursor = conn.cursor()

    try:
        insertar_usuarios(cursor)
        insertar_productos(cursor)
        insertar_recetas(cursor)
        insertar_receta_ingredientes(cursor)
        insertar_lista_compras(cursor)
        insertar_recetas_pendientes(cursor)

        conn.commit()
        print("✅ Datos realistas insertados correctamente")
        
        
        
        # 👇 AQUÍ la copia
        copiar_bd_al_padre()
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    generar_datos()