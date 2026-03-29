from acceso_base_datos import conexion
from inventario import verificar_stock_minimo
from lista_compra import marcar_comprado

def agregar_receta(nombre):
    conexion_bd = conexion()
    if not conexion_bd:
        return
    cursor = conexion_bd.cursor()
    cursor.execute("INSERT INTO recetas (nombre) VALUES (?)", (nombre,))
    conexion_bd.commit()
    conexion_bd.close()
    print(f"Receta '{nombre}' agregada.")

def agregar_ingrediente_a_receta(receta_id, producto_id, cantidad, unidad):
    conexion_bd = conexion()
    if not conexion_bd:
        return
    cursor = conexion_bd.cursor()
    cursor.execute(
        "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad) VALUES (?, ?, ?, ?)",
        (receta_id, producto_id, cantidad, unidad)
    )
    conexion_bd.commit()
    conexion_bd.close()
    print(f"Ingrediente añadido a receta {receta_id}.")

def preparar_receta(receta_id):
    conexion_bd = conexion()
    if not conexion_bd:
        return
    cursor = conexion_bd.cursor()

    # obtenemos los ingredientes de la receta
    cursor.execute("""
        SELECT ri.producto_id, ri.cantidad, ri.unidad, p.cantidad, p.nombre
        FROM receta_ingredientes ri
        JOIN productos p ON ri.producto_id = p.id
        WHERE ri.receta_id = ?
    """, (receta_id,))
    
    ingredientes = cursor.fetchall()

    # comprobamos si hay suficiente stock
    faltantes = []
    for producto_id, cant_receta, unidad, cant_actual, nombre in ingredientes:
        if cant_actual < cant_receta:
            faltantes.append((nombre, cant_actual, cant_receta, unidad))

    if faltantes:
        print("No se puede preparar la receta. Faltan ingredientes:")
        for nombre, actual, necesario, unidad in faltantes:
            print(f"- {nombre}: hay {actual} {unidad}, se necesitan {necesario} {unidad}")
        conexion_bd.close()
        return

    # descontamos del stock de manera segura
    for producto_id, cant_receta, unidad, cant_actual, nombre in ingredientes:
        cursor.execute("""
            UPDATE productos
            SET cantidad = cantidad - ?
            WHERE id = ?
        """, (cant_receta, producto_id))

    conexion_bd.commit()
    conexion_bd.close()

    # actualizamos la lista de compras por si algún producto quedó bajo stock
    verificar_stock_minimo()

    print(f"Receta {receta_id} preparada correctamente y stock actualizado.")

def generar_lista_desde_receta(receta_id, usuario_id=None):
    conexion_bd = conexion()
    if not conexion_bd:
        return

    cursor = conexion_bd.cursor()

    # obtenemos ingredientes + stock actual
    cursor.execute("""
        SELECT ri.producto_id, ri.cantidad, ri.unidad, p.cantidad
        FROM receta_ingredientes ri
        JOIN productos p ON ri.producto_id = p.id
        WHERE ri.receta_id = ?
    """, (receta_id,))

    ingredientes = cursor.fetchall()

    for producto_id, cantidad_receta, unidad, stock_actual in ingredientes:

        # solo añadimos si falta stock
        if stock_actual < cantidad_receta:
            cantidad_faltante = cantidad_receta - stock_actual

            # comprobamos si ya está en lista
            cursor.execute("""
                SELECT id, cantidad FROM lista_compra
                WHERE producto_id = ? AND comprado = 0
            """, (producto_id,))
            existe = cursor.fetchone()

            if existe:
                # si ya existe, sumamos la cantidad faltante
                cursor.execute("""
                    UPDATE lista_compras
                    SET cantidad = cantidad + ?
                    WHERE id = ?
                """, (cantidad_faltante, existe[0]))
            else:
                # insertamos nuevo
                cursor.execute("""
                    INSERT INTO lista_compra (producto_id, cantidad, unidad, comprado, usuario_id_asignado)
                    VALUES (?, ?, ?, 0, ?)
                """, (producto_id, cantidad_faltante, unidad, usuario_id))

    conexion_bd.commit()
    conexion_bd.close()
    print("Lista de compras generada inteligentemente")

def obtener_recetas():
    conn = conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM recetas")
    recetas = cursor.fetchall()
    conn.close()
    return recetas