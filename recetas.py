from InicializacionBaseDatos.acceso_base_datos import conexion
from inventario import verificar_stock_minimo
from lista_compras import marcar_comprado


def agregar_receta(nombre):
    conexion_bd = conexion()
    if not conexion_bd:
        return
    cursor = conexion_bd.cursor()

    # insertamos la nueva receta en la base de datos
    cursor.execute("INSERT INTO recetas (nombre) VALUES (?)", (nombre,))

    conexion_bd.commit()
    conexion_bd.close()
    print(f"Receta '{nombre}' agregada.")


def agregar_ingrediente_a_receta(receta_id, producto_id, cantidad, unidad):
    conexion_bd = conexion()
    if not conexion_bd: return
    cursor = conexion_bd.cursor()

    # insertamos el ingrediente en la receta
    cursor.execute("""
        INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad)
        VALUES (?, ?, ?, ?)
    """, (receta_id, producto_id, cantidad, unidad))

    conexion_bd.commit()
    conexion_bd.close()
    
    # recalculamos la necesidad de compra del producto afectado
    recalcular_necesidad_producto(producto_id)
    
    print(f"Ingrediente añadido y stock sincronizado.")


def modificar_cantidad_ingrediente(receta_id, producto_id, nueva_cantidad):
    conexion_bd = conexion()
    if not conexion_bd:
        return
    cursor = conexion_bd.cursor()

    # actualizamos la cantidad de un ingrediente
    cursor.execute("""
        UPDATE receta_ingredientes 
        SET cantidad = ? 
        WHERE receta_id = ? AND producto_id = ?
    """, (nueva_cantidad, receta_id, producto_id))
    
    conexion_bd.commit()
    conexion_bd.close()

    # recalculamos la lista de compras
    recalcular_necesidad_producto(producto_id)

def preparar_receta(receta_id):
    conexion_bd = conexion()
    if not conexion_bd: return False
    cursor = conexion_bd.cursor()

    # consultamos ingredientes necesarios vs stock actual
    cursor.execute("""
        SELECT ri.producto_id, ri.cantidad, p.cantidad, p.nombre, ri.unidad
        FROM receta_ingredientes ri
        JOIN productos p ON ri.producto_id = p.id
        WHERE ri.receta_id = ?
    """, (receta_id,))
    ingredientes = cursor.fetchall()

    # comprobamos si hay stock suficiente
    faltantes = []
    for pid, cant_nec, stock_act, nombre, unidad in ingredientes:
        if stock_act < cant_nec:
            faltantes.append(f"{nombre} (Necesitas {cant_nec}{unidad}, tienes {stock_act})")

    if faltantes:
        mensaje = "No hay stock suficiente:\n" + "\n".join(faltantes)
        # Retornamos False y el mensaje de error
        conexion_bd.close()
        return False, mensaje

    # si todo está correcto, descontamos stock
    try:
        for pid, cant_nec, stock_act, nombre, unidad in ingredientes:
            cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?", (cant_nec, pid))
        
        conexion_bd.commit()
        return True, "¡Receta preparada con éxito!"
    except Exception as e:
        conexion_bd.rollback()
        return False, f"Error en la base de datos: {e}"
    finally:
        conexion_bd.close()


def generar_lista_desde_receta(receta_id, usuario_id=None):
    conexion_bd = conexion()
    if not conexion_bd:
        return

    cursor = conexion_bd.cursor()

    # obtenemos ingredientes de la receta
    cursor.execute("""
        SELECT ri.producto_id, ri.cantidad, ri.unidad, p.cantidad
        FROM receta_ingredientes ri
        JOIN productos p ON ri.producto_id = p.id
        WHERE ri.receta_id = ?
    """, (receta_id,))

    ingredientes = cursor.fetchall()

    # generamos lista de compra si falta stock
    for producto_id, cantidad_receta, unidad, stock_actual in ingredientes:

        if stock_actual < cantidad_receta:
            cantidad_faltante = cantidad_receta - stock_actual

            # comprobamos si ya existe en la lista
            cursor.execute("""
                SELECT id, cantidad
                FROM lista_compras
                WHERE producto_id = ? AND comprado = 0
            """, (producto_id,))
            existe = cursor.fetchone()

            if existe:
                # actualizamos cantidad existente
                cursor.execute("""
                    UPDATE lista_compras
                    SET cantidad = cantidad + ?
                    WHERE id = ?
                """, (cantidad_faltante, existe[0]))
            else:
                # insertamos nuevo registro
                cursor.execute("""
                    INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado, usuario_id_asignado)
                    VALUES (?, ?, ?, 0, ?)
                """, (producto_id, cantidad_faltante, unidad, usuario_id))

    conexion_bd.commit()
    conexion_bd.close()

    print("Lista de compras generada correctamente.")


def obtener_recetas():
    conn = conexion()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM recetas")

    recetas = cursor.fetchall()
    conn.close()
    return recetas


def recalcular_necesidad_producto(producto_id):
    """
    Calcula cuánto hay que comprar de un producto sumando todas las 
    recetas del planificador + stock mínimo - stock actual.
    """
    conexion_bd = conexion()
    cursor = conexion_bd.cursor()
    
   # sumamos lo que piden las recetas pendientes
    cursor.execute("""
        SELECT SUM(ri.cantidad) 
        FROM receta_ingredientes ri
        JOIN recetas_pendientes rp ON ri.receta_id = rp.receta_id
        WHERE ri.producto_id = ? AND rp.completada = 0
    """, (producto_id,))
    total_planificador = cursor.fetchone()[0] or 0

    # obtenemos stock y mínimo
    cursor.execute("SELECT cantidad, stock_minimo, unidad FROM productos WHERE id = ?", (producto_id,))
    prod_data = cursor.fetchone()
    if not prod_data: 
        conexion_bd.close()
        return
    
    stock_actual, stock_min, unidad = prod_data

    # cálculo final de compra necesaria
    necesidad_total = total_planificador + stock_min
    cantidad_a_comprar = round(max(0, necesidad_total - stock_actual), 2)

    # actualizamos la tabla lista_compras (Solo lo que no se ha comprado aún)
    cursor.execute("DELETE FROM lista_compras WHERE producto_id = ? AND comprado = 0", (producto_id,))
    
    if cantidad_a_comprar > 0:
        cursor.execute("""
            INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado)
            VALUES (?, ?, ?, 0)
        """, (producto_id, cantidad_a_comprar, unidad))

    conexion_bd.commit()
    conexion_bd.close()


