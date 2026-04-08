from InicializacionBaseDatos.acceso_base_datos import conexion
from inventario import verificar_stock_minimo
from lista_compras import marcar_comprado


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
    if not conexion_bd: return
    cursor = conexion_bd.cursor()

    cursor.execute("""
        INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad)
        VALUES (?, ?, ?, ?)
    """, (receta_id, producto_id, cantidad, unidad))

    conexion_bd.commit()
    conexion_bd.close()
    
    # 🔥 NUEVO: Recalcular la lista de compras por si esta receta está en el planificador
    recalcular_necesidad_producto(producto_id)
    
    print(f"Ingrediente añadido y stock sincronizado.")


def modificar_cantidad_ingrediente(receta_id, producto_id, nueva_cantidad):
    """Actualiza la cantidad de un ingrediente y sincroniza la compra"""
    conexion_bd = conexion()
    if not conexion_bd: return
    cursor = conexion_bd.cursor()
    
    cursor.execute("""
        UPDATE receta_ingredientes 
        SET cantidad = ? 
        WHERE receta_id = ? AND producto_id = ?
    """, (nueva_cantidad, receta_id, producto_id))
    
    conexion_bd.commit()
    conexion_bd.close()

    # 🔥 La "Reacción en cadena"
    recalcular_necesidad_producto(producto_id)

def preparar_receta(receta_id):
    conexion_bd = conexion()
    if not conexion_bd: return False
    cursor = conexion_bd.cursor()

    # 1. Consultar ingredientes necesarios vs stock actual
    cursor.execute("""
        SELECT ri.producto_id, ri.cantidad, p.cantidad, p.nombre, ri.unidad
        FROM receta_ingredientes ri
        JOIN productos p ON ri.producto_id = p.id
        WHERE ri.receta_id = ?
    """, (receta_id,))
    ingredientes = cursor.fetchall()

    # 2. Validar faltantes
    faltantes = []
    for pid, cant_nec, stock_act, nombre, unidad in ingredientes:
        if stock_act < cant_nec:
            faltantes.append(f"{nombre} (Necesitas {cant_nec}{unidad}, tienes {stock_act})")

    if faltantes:
        mensaje = "No hay stock suficiente:\n" + "\n".join(faltantes)
        # Retornamos False y el mensaje de error
        conexion_bd.close()
        return False, mensaje

    # 3. Si todo está OK, descontar stock
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

    cursor.execute("""
        SELECT ri.producto_id, ri.cantidad, ri.unidad, p.cantidad
        FROM receta_ingredientes ri
        JOIN productos p ON ri.producto_id = p.id
        WHERE ri.receta_id = ?
    """, (receta_id,))

    ingredientes = cursor.fetchall()

    for producto_id, cantidad_receta, unidad, stock_actual in ingredientes:

        if stock_actual < cantidad_receta:
            cantidad_faltante = cantidad_receta - stock_actual

            # 🔥 BUSCAR SI YA EXISTE EN LISTA
            cursor.execute("""
                SELECT id, cantidad
                FROM lista_compras
                WHERE producto_id = ? AND comprado = 0
            """, (producto_id,))
            existe = cursor.fetchone()

            if existe:
                # 🔥 ACTUALIZAR EXISTENTE (CORRECTO)
                cursor.execute("""
                    UPDATE lista_compras
                    SET cantidad = cantidad + ?
                    WHERE id = ?
                """, (cantidad_faltante, existe[0]))
            else:
                # 🔥 INSERTAR NUEVO
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
    
    # A. Sumar lo que piden todas las recetas PENDIENTES en el planificador
    cursor.execute("""
        SELECT SUM(ri.cantidad) 
        FROM receta_ingredientes ri
        JOIN recetas_pendientes rp ON ri.receta_id = rp.receta_id
        WHERE ri.producto_id = ? AND rp.completada = 0
    """, (producto_id,))
    total_planificador = cursor.fetchone()[0] or 0

    # B. Obtener stock actual y mínimo
    cursor.execute("SELECT cantidad, stock_minimo, unidad FROM productos WHERE id = ?", (producto_id,))
    prod_data = cursor.fetchone()
    if not prod_data: 
        conexion_bd.close()
        return
    
    stock_actual, stock_min, unidad = prod_data

    # C. Cálculo Maestro
    necesidad_total = total_planificador + stock_min
    cantidad_a_comprar = round(max(0, necesidad_total - stock_actual), 2)

    # D. Actualizar la tabla lista_compras (Solo lo que no se ha comprado aún)
    cursor.execute("DELETE FROM lista_compras WHERE producto_id = ? AND comprado = 0", (producto_id,))
    
    if cantidad_a_comprar > 0:
        cursor.execute("""
            INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado)
            VALUES (?, ?, ?, 0)
        """, (producto_id, cantidad_a_comprar, unidad))

    conexion_bd.commit()
    conexion_bd.close()


