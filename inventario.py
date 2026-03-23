from acceso_base_datos import conexion


def verificar_stock_minimo():
    conexion_db = conexion()
    if not conexion_db:
        return

    cursor = conexion_db.cursor()
    
    # seleccionamos los productos bajo stock minimo
    cursor.execute("SELECT id, nombre, cantidad, stock_minimo, unidad FROM productos WHERE cantidad < stock_minimo")
    productos_bajo_stock = cursor.fetchall()
    
    for producto in productos_bajo_stock:
        producto_id, nombre, cantidad, stock_minimo, unidad = producto
        cantidad_a_comprar = stock_minimo - cantidad
        
        # comprobamos si el producto ya lo tenemos en la lista
        cursor.execute("SELECT id FROM lista_compras WHERE producto_id = ?", (producto_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            # actualizamos las cantidades
            cursor.execute("UPDATE lista_compras SET cantidad = ? WHERE producto_id = ?", (cantidad_a_comprar, producto_id))
        else:
            # insertamos el ingrediente
            cursor.execute("INSERT INTO lista_compras (producto_id, cantidad, unidad) VALUES (?, ?, ?)", (producto_id, cantidad_a_comprar, unidad))
        
        print(f"Producto '{nombre}' añadido a la lista de compras: {cantidad_a_comprar} {unidad}")

    conexion_db.commit()
    conexion_db.close()