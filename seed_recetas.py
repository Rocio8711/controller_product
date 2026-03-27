from acceso_base_datos import conexion


def insertar_recetas():
    conexion_bd = conexion()
    if not conexion_bd:
        return

    cursor = conexion_bd.cursor()

    recetas = [
        "Tortilla de patatas",
        "Paella valenciana",
        "Ensalada mixta",
        "Macarrones con tomate",
        "Pollo al horno",
        "Lentejas estofadas",
        "Gazpacho",
        "Arroz tres delicias",
        "Sopa de pollo",
        "Hamburguesa casera",
        "Pizza margarita",
        "Bocadillo de jamón",
        "Croquetas de jamón",
        "Tacos mexicanos",
        "Spaghetti boloñesa",
        "Salmón a la plancha",
        "Crema de calabacín",
        "Fabada asturiana",
        "Cocido madrileño",
        "Pimientos rellenos"
    ]

    for receta in recetas:
        cursor.execute(
            "INSERT INTO recetas (nombre) VALUES (?)",
            (receta,)
        )

    conexion_bd.commit()
    conexion_bd.close()

    print("20 recetas insertadas correctamente")


if __name__ == "__main__":
    insertar_recetas()