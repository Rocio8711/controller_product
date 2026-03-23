import sqlite3


def conexion(db_name="controllerproduct.db"):
    try:
        conexion_bd = sqlite3.connect(db_name)
        print("Conexión exitosa a la base de datos")
        return conexion_bd
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    

def crar_tablas():
    conexion_bd = conexion()
    if not conexion_bd:
        return 

    cursor = conexion_bd.cursor()
    
    # Tabla de productos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cantidad REAL NOT NULL,
        unidad TEXT NOT NULL,
        stock_minimo REAL DEFAULT 0
    )
    """)
    
    # Tabla de recetas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recetas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    )
    """)
    
    # Tabla de ingredientes de recetas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receta_ingredientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receta_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad REAL NOT NULL,
        unidad TEXT NOT NULL,
        FOREIGN KEY (receta_id) REFERENCES recetas(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )
    """)
    
    # Tabla de lista de compras
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lista_compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER NOT NULL,
        cantidad REAL NOT NULL,
        unidad TEXT NOT NULL,
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )
    """)
    
    conexion_bd.commit()
    conexion_bd.close()   