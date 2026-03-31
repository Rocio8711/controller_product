from acceso_base_datos import conexion


def insertar_datos_prueba():
    conexion_bd = conexion()
    if not conexion_bd:
        return

    cursor = conexion_bd.cursor()

    # =========================
    # USUARIOS (SIN DUPLICADOS)
    # =========================
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", ("juan@test.com",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, contrasena) VALUES (?, ?, ?)",
            ("Juan", "juan@test.com", "1234")
        )

    cursor.execute("SELECT id FROM usuarios WHERE email = ?", ("ana@test.com",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, contrasena) VALUES (?, ?, ?)",
            ("Ana", "ana@test.com", "1234")
        )

    # =========================
    # PRODUCTOS (SIN DUPLICADOS)
    # =========================
    cursor.execute("SELECT id FROM productos WHERE nombre = ?", ("Leche",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?, ?, ?, ?)",
            ("Leche", 10, "litros", 2)
        )

    cursor.execute("SELECT id FROM productos WHERE nombre = ?", ("Pan",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?, ?, ?, ?)",
            ("Pan", 20, "unidades", 5)
        )

    cursor.execute("SELECT id FROM productos WHERE nombre = ?", ("Huevos",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?, ?, ?, ?)",
            ("Huevos", 30, "unidades", 6)
        )

    # =========================
    # LISTA DE COMPRAS (SIN DUPLICADOS SIMPLES)
    # =========================
    cursor.execute("SELECT id FROM lista_comprass WHERE producto_id = 1 AND usuario_id_asignado = 1")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO lista_comprass (producto_id, cantidad, unidad, comprado, usuario_id_asignado) VALUES (?, ?, ?, ?, ?)",
            (1, 2, "litros", 0, 1)
        )

    cursor.execute("SELECT id FROM lista_comprass WHERE producto_id = 2 AND usuario_id_asignado = 2")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO lista_comprass (producto_id, cantidad, unidad, comprado, usuario_id_asignado) VALUES (?, ?, ?, ?, ?)",
            (2, 5, "unidades", 0, 2)
        )

    cursor.execute("SELECT id FROM lista_comprass WHERE producto_id = 3 AND usuario_id_asignado = 1")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO lista_comprass (producto_id, cantidad, unidad, comprado, usuario_id_asignado) VALUES (?, ?, ?, ?, ?)",
            (3, 12, "unidades", 1, 1)
        )

    conexion_bd.commit()
    conexion_bd.close()

    print("Datos de prueba insertados correctamente")


if __name__ == "__main__":
    insertar_datos_prueba()