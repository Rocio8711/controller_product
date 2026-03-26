from acceso_base_datos import conexion

def mostrar_lista_compras():
    conexion_bd = conexion()
    if not conexion_bd:
        return

    cursor = conexion_bd.cursor()
    cursor.execute("""
        SELECT lc.id, p.nombre, lc.cantidad, lc.unidad, u.nombre, lc.comprado
        FROM lista_compras lc
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

def marcar_comprado(item_id):
    conn = conexion()
    if not conn:
        return  
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE lista_compras
            SET comprado = 1
            WHERE id = ?
        """, (item_id,))
        
        conn.commit()
        print("Producto marcado como comprado")
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()


def ver_tareas_usuario(usuario_id):
    conn = conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT lc.id, p.nombre, lc.cantidad, lc.unidad
        FROM lista_compras lc
        JOIN productos p ON lc.producto_id = p.id
        WHERE lc.usuario_id_asignado = ? AND lc.comprado = 0
    """, (usuario_id,))
    resultados = cursor.fetchall()
    conn.close()
    
    return resultados