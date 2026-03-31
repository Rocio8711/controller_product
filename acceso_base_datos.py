import sqlite3


# =====================================================
# CONEXIÓN
# =====================================================
def conexion(db_name="controllerproduct.db"):
    try:
        conn = sqlite3.connect(db_name, timeout=10)
        conn.execute("PRAGMA foreign_keys = ON")  # 🔥 IMPORTANTE
        print("Conexión exitosa a la base de datos")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


# =====================================================
# CREACIÓN DE TABLAS (ORDEN CORRECTO)
# =====================================================
def crear_tablas():
    conn = conexion()
    if not conn:
        return

    cursor = conn.cursor()

    # =========================
    # 1. USUARIOS (PRIMERO)
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        contrasena TEXT NOT NULL
    )
    """)

    # =========================
    # 2. PRODUCTOS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cantidad REAL NOT NULL,
        unidad TEXT NOT NULL,
        stock_minimo REAL DEFAULT 0
    )
    """)

    # =========================
    # 3. RECETAS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recetas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    )
    """)

    # =========================
    # 4. INGREDIENTES RECETAS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receta_ingredientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receta_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad REAL NOT NULL,
        unidad TEXT NOT NULL,
        FOREIGN KEY (receta_id) REFERENCES recetas(id) ON DELETE CASCADE,
        FOREIGN KEY (producto_id) REFERENCES productos(id),
        UNIQUE(receta_id, producto_id)
    )
    """)

    # =========================
    # 5. LISTA COMPRAS (AL FINAL)
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lista_compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER NOT NULL,
        cantidad REAL NOT NULL,
        unidad TEXT NOT NULL,
        comprado INTEGER DEFAULT 0,
        usuario_id_asignado INTEGER,
        FOREIGN KEY (producto_id) REFERENCES productos(id),
        FOREIGN KEY (usuario_id_asignado) REFERENCES usuarios(id)
    )
    """)

    conn.commit()
    conn.close()