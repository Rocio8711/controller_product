from acceso_base_datos import conexion

def mostrar_lista_compras():
    conexion_bd = conexion()
    if not conexion_bd:
        return
    cursor = conexion_bd.cursor()
    cursor.execute("SELECT p.nombre, lc.cantidad, lc.unidad FROM lista_compras lc JOIN productos p ON lc.producto_id = p.id")
    lista = cursor.fetchall()
    print("Lista de Compras:")
    for nombre, cantidad, unidad in lista:
        print(f"- {nombre}: {cantidad} {unidad}")
    conexion_bd.close()