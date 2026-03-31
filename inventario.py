from acceso_base_datos import conexion


# =========================
# ⚠️ VERIFICAR STOCK MÍNIMO
# =========================
def verificar_stock_minimo():
    conn = conexion()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        # Productos por debajo del mínimo
        cursor.execute("""
            SELECT id, nombre, cantidad, stock_minimo, unidad
            FROM productos
            WHERE cantidad < stock_minimo
        """)

        productos_bajo_stock = cursor.fetchall()

        for producto_id, nombre, cantidad, stock_minimo, unidad in productos_bajo_stock:
            cantidad_a_comprar = stock_minimo - cantidad

            # 🔥 IMPORTANTE: solo mirar pendientes (comprado = 0)
            cursor.execute("""
                SELECT id, cantidad 
                FROM lista_comprass 
                WHERE producto_id = ? AND comprado = 0
            """, (producto_id,))

            resultado = cursor.fetchone()

            if resultado:
                lista_id, cantidad_existente = resultado

                # 🔥 SUMAR en vez de sobrescribir (evita perder datos)
                cursor.execute("""
                    UPDATE lista_comprass
                    SET cantidad = cantidad + ?
                    WHERE id = ?
                """, (cantidad_a_comprar, lista_id))

            else:
                # Insertar nuevo en lista
                cursor.execute("""
                    INSERT INTO lista_comprass (producto_id, cantidad, unidad, comprado)
                    VALUES (?, ?, ?, 0)
                """, (producto_id, cantidad_a_comprar, unidad))

            print(f"Producto '{nombre}' añadido a la lista: {cantidad_a_comprar} {unidad}")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Error verificando stock mínimo:", e)

    finally:
        conn.close()


# =========================
# 📦 VER INVENTARIO
# =========================
def ver_inventario():
    conn = conexion()
    if not conn:
        return []

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, cantidad, unidad, stock_minimo
        FROM productos
    """)

    datos = cursor.fetchall()
    conn.close()

    return datos