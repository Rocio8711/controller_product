from InicializacionBaseDatos.acceso_base_datos import conexion


# VERIFICAR STOCK MÍNIMO
def verificar_stock_minimo():
    conn = conexion()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        #buscamos todos los productos que están por debajo del stock mínimo
        cursor.execute("""
            SELECT id, nombre, cantidad, stock_minimo, unidad
            FROM productos
            WHERE cantidad < stock_minimo
        """)

        productos_bajo_stock = cursor.fetchall()

        #recorremos cada producto con stock insuficiente
        for producto_id, nombre, cantidad, stock_minimo, unidad in productos_bajo_stock:
            #calculamos cuánto necesitamos reponer para llegar al mínimo
            cantidad_a_comprar = stock_minimo - cantidad

            #comprobamos si el producto ya existe en la lista de compras (sin comprar)
            cursor.execute("""
                SELECT id, cantidad 
                FROM lista_compras 
                WHERE producto_id = ? AND comprado = 0
            """, (producto_id,))

            resultado = cursor.fetchone()

            if resultado:
                lista_id, cantidad_existente = resultado

                #si ya existe, sumamos la nueva necesidad para no perder información previa
                cursor.execute("""
                    UPDATE lista_compras
                    SET cantidad = cantidad + ?
                    WHERE id = ?
                """, (cantidad_a_comprar, lista_id))

            else:
                #si no existe, lo añadimos a la lista de compras
                cursor.execute("""
                    INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado)
                    VALUES (?, ?, ?, 0)
                """, (producto_id, cantidad_a_comprar, unidad))

            print(f"Producto '{nombre}' añadido a la lista: {cantidad_a_comprar} {unidad}")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Error verificando stock mínimo:", e)

    finally:
        conn.close()



# VER INVENTARIO
def ver_inventario():
    conn = conexion()
    if not conn:
        return []

    cursor = conn.cursor()
    #obtenemos todos los productos del inventario
    cursor.execute("""
        SELECT id, nombre, cantidad, unidad, stock_minimo
        FROM productos
    """)

    datos = cursor.fetchall()
    conn.close()
    #devolvemos la lista de productos
    return datos