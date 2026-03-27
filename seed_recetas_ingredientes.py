from acceso_base_datos import conexion


def insertar_datos():
    conexion_bd = conexion()
    if not conexion_bd:
        return

    cursor = conexion_bd.cursor()

    # =========================
    # RECETAS (asumimos IDs 1-5)
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
    # PRODUCTOS (IMPORTANTE: IDs fijos)
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

    # Tortilla (receta_id = 1)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 1, 1, 0.5, 'kg')")  # patata
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 1, 2, 3, 'unidades')")  # huevo
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 1, 3, 0.1, 'litros')")  # aceite

    # Paella (receta_id = 2)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 2, 4, 0.5, 'kg')")  # arroz
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 2, 5, 0.5, 'kg')")  # pollo
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 2, 7, 0.3, 'kg')")  # tomate

    # Ensalada (receta_id = 3)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 3, 6, 1, 'unidades')")  # lechuga
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 3, 7, 0.2, 'kg')")  # tomate

    # Macarrones (receta_id = 4)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 4, 8, 0.5, 'kg')")  # pasta
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 4, 7, 0.3, 'kg')")  # tomate

    # Pollo al horno (receta_id = 5)
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 5, 5, 1, 'kg')")  # pollo
    cursor.execute("INSERT INTO receta_ingredientes VALUES (NULL, 5, 3, 0.05, 'litros')")  # aceite

    conexion_bd.commit()
    conexion_bd.close()

    print("Recetas + ingredientes insertados correctamente")


if __name__ == "__main__":
    insertar_datos()