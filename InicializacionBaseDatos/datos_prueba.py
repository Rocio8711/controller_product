import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "controllerproduct.db"

# CONEXIÓN
def conexion():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# USUARIOS
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

# PRODUCTOS
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
        ("Levadura", 2, "kg", 0.5),
        ("Patatas", 25, "kg", 5),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?, ?, ?, ?)",
        productos
    )


# RECETAS 
def insertar_recetas(cursor):
    recetas = [
        "Tortilla", "Bizcocho", "Pancakes", "Galletas", "Pizza",
        "Ensalada", "Sopa", "Arroz con pollo", "Pasta", "Hamburguesa",
        "Sandwich", "Croquetas", "Tarta", "Brownie", "Batido",
        "Lentejas", "Paella", "Quiche", "Empanada", "Crepes"
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO recetas (nombre) VALUES (?)",
        [(r,) for r in recetas]
    )


# INGREDIENTES AUTOMÁTICOS
def insertar_receta_ingredientes(cursor):
    cursor.execute("SELECT id FROM recetas")
    recetas = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT id FROM productos")
    productos = [p[0] for p in cursor.fetchall()]

    ingredientes = []

    for receta_id in recetas:
        num_ingredientes = random.randint(2, 5)
        productos_seleccionados = random.sample(productos, num_ingredientes)

        for producto_id in productos_seleccionados:
            cantidad = round(random.uniform(0.1, 2), 2)
            unidad = random.choice(["kg", "litros", "unidades"])

            ingredientes.append((receta_id, producto_id, cantidad, unidad))

    cursor.executemany("""
        INSERT OR IGNORE INTO receta_ingredientes
        (receta_id, producto_id, cantidad, unidad)
        VALUES (?, ?, ?, ?)
    """, ingredientes)


# LISTA DE COMPRAS
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


# RECETAS PENDIENTES
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

# EJECUCIÓN
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
        print("✅ Datos de prueba insertados correctamente")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    generar_datos()