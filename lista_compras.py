from acceso_base_datos import conexion


def mostrar_lista_comprass():
    conexion_bd = conexion()
    if not conexion_bd:
        return

    cursor = conexion_bd.cursor()
    cursor.execute("""
        SELECT lc.id, p.nombre, lc.cantidad, lc.unidad, u.nombre, lc.comprado
        FROM lista_comprass lc
        JOIN productos p ON lc.producto_id = p.id
        LEFT JOIN usuarios u ON lc.usuario_id_asignado = u.id
    """)

    lista = cursor.fetchall()

    print("\n=== LISTA DE COMPRAS ===")

    for item_id, nombre, cantidad, unidad, usuario, comprado in lista:
        estado = "✔ Comprado" if comprado else "❌ Pendiente"
        asignado = usuario if usuario else "Sin asignar"

        print(f"[{item_id}] - {nombre}: {cantidad} {unidad} | {estado} | Responsable: {asignado}")

    conexion_bd.close()


# =========================
# ✅ MARCAR COMO COMPRADO + ACTUALIZAR INVENTARIO
# =========================
def marcar_comprado(item_id):
    conn = conexion()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        # 1. Obtener datos de la lista
        cursor.execute("""
            SELECT producto_id, cantidad 
            FROM lista_comprass 
            WHERE id = ? AND comprado = 0
        """, (item_id,))

        resultado = cursor.fetchone()

        if not resultado:
            print("No existe o ya está comprado")
            return

        producto_id, cantidad = resultado

        # 2. Marcar como comprado
        cursor.execute("""
            UPDATE lista_comprass
            SET comprado = 1
            WHERE id = ?
        """, (item_id,))

        # 3. Sumar al inventario
        cursor.execute("""
            UPDATE productos
            SET cantidad = cantidad + ?
            WHERE id = ?
        """, (cantidad, producto_id))

        conn.commit()
        print(f"✔ Añadido al inventario: +{cantidad}")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        conn.close()


# =========================
# 📋 VER TAREAS
# =========================
def ver_tareas_usuario(usuario_id):
    conexion_bd = conexion()
    if not conexion_bd:
        return []

    cursor = conexion_bd.cursor()
    cursor.execute("""
        SELECT lc.id, p.nombre, lc.cantidad, lc.unidad
        FROM lista_comprass lc
        JOIN productos p ON lc.producto_id = p.id
        WHERE lc.usuario_id_asignado = ? AND lc.comprado = 0
    """, (usuario_id,))

    resultados = cursor.fetchall()
    conexion_bd.close()

    return resultados


def ver_tareas_todas():
    conexion_bd = conexion()
    if not conexion_bd:
        return []

    cursor = conexion_bd.cursor()
    cursor.execute("""
        SELECT lc.id, p.nombre, lc.cantidad, lc.unidad
        FROM lista_comprass lc
        JOIN productos p ON lc.producto_id = p.id
        WHERE lc.comprado = 0
    """)

    resultados = cursor.fetchall()
    conexion_bd.close()

    return resultados


# =========================
# 🧾 GENERAR LISTA DESDE RECETA
# =========================
def generar_lista_desde_receta(receta_id):
    conn = conexion()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT ri.producto_id, ri.cantidad_necesaria, p.stock, p.nombre, p.unidad
            FROM receta_ingredientes ri
            JOIN productos p ON ri.producto_id = p.id
            WHERE ri.receta_id = ?
        """, (receta_id,))

        ingredientes = cursor.fetchall()

        for prod_id, cant_necesaria, stock_actual, nombre, unidad in ingredientes:
            if stock_actual < cant_necesaria:
                faltante = cant_necesaria - stock_actual

                # Verificar si ya existe en lista
                cursor.execute("""
                    SELECT id FROM lista_comprass 
                    WHERE producto_id = ? AND comprado = 0
                """, (prod_id,))

                existe = cursor.fetchone()

                if existe:
                    cursor.execute("""
                        UPDATE lista_comprass 
                        SET cantidad = cantidad + ? 
                        WHERE id = ?
                    """, (faltante, existe[0]))
                else:
                    cursor.execute("""
                        INSERT INTO lista_comprass (producto_id, cantidad, unidad, comprado)
                        VALUES (?, ?, ?, 0)
                    """, (prod_id, faltante, unidad))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()


# =========================
# 🍳 PREPARAR RECETA (RESTAR STOCK)
# =========================
def preparar_receta(receta_id):
    conn = conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE productos 
            SET stock = stock - (
                SELECT cantidad_necesaria 
                FROM receta_ingredientes 
                WHERE receta_id = ? AND producto_id = productos.id
            )
            WHERE id IN (
                SELECT producto_id 
                FROM receta_ingredientes 
                WHERE receta_id = ?
            )
        """, (receta_id, receta_id))

        conn.commit()
        print("¡Receta preparada! Stock actualizado.")

    except Exception as e:
        conn.rollback()
        print("Error al preparar receta:", e)

    finally:
        conn.close()