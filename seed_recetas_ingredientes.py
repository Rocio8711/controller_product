from acceso_base_datos import conexion


def insertar_datos():
    conexion_bd = conexion()
    if not conexion_bd:
        return

    cursor = conexion_bd.cursor()

    # =========================
    # 🧹 LIMPIAR TABLAS (CLAVE)
    # =========================
    cursor.execute("DELETE FROM receta_ingredientes")
    cursor.execute("DELETE FROM recetas")
    cursor.execute("DELETE FROM productos")

    # =========================
    # RECETAS
    # =========================
    recetas = [
        "Tortilla de patatas",
        "Paella",
        "Ensalada mixta",
        "Macarrones",
        "Pollo al horno"
    ]

    for r in recetas:
        cursor.execute("INSERT INTO recetas (nombre) VALUES (?)", (r,))

    # =========================
    # PRODUCTOS
    # =========================
    productos = [
        ("Patata", "kg"),
        ("Huevo", "unidades"),
        ("Aceite", "litros"),
        ("Arroz", "kg"),
        ("Pollo", "kg"),
        ("Lechuga", "unidades"),
        ("Tomate", "kg"),
        ("Pasta", "kg")
    ]

    for p in productos:
        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?, ?, ?, ?)",
            (p[0], 0, p[1], 0)
        )

    # =========================
    # INGREDIENTES RECETAS
    # =========================

    # Tortilla (1)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 1, 1, 0.5, 'kg')")
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 1, 2, 3, 'unidades')")
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 1, 3, 0.1, 'litros')")

    # Paella (2)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 2, 4, 0.5, 'kg')")
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 2, 5, 0.5, 'kg')")
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 2, 7, 0.3, 'kg')")

    # Ensalada (3)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 3, 6, 1, 'unidades')")
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 3, 7, 0.2, 'kg')")

    # Macarrones (4)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 4, 8, 0.5, 'kg')")
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 4, 7, 0.3, 'kg')")

    # Pollo al horno (5)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 5, 5, 1, 'kg')")
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 5, 3, 0.05, 'litros')")

    conexion_bd.commit()
    conexion_bd.close()

    print("✅ Base de datos reiniciada correctamente (sin duplicados)")


if __name__ == "__main__":
    insertar_datos()