from acceso_base_datos import conexion
from inventario import verificar_stock_minimo

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
    cursor.execute("INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad) VALUES (?, ?, ?, ?)", (receta_id, producto_id, cantidad, unidad))
    conexion_bd.commit()
    conexion_bd.close()
    print(f"Ingrediente añadido a receta {receta_id}.")

#lo metemos aqui ete metodo ya que toca productos pero est relacioado con las recetas.
def preparar_receta(receta_id):
    conexion_bd = conexion()
    if not conexion_bd:
        return
    cursor = conexion_bd.cursor()

    # obtenemos los ingredientes de la receta
    cursor.execute("SELECT ri.producto_id, ri.cantidad, ri.unidad, p.cantidad, p.nombre FROM receta_ingredientes ri JOIN productos p ON ri.producto_id = p.id WHERE ri.receta_id = ?", (receta_id,))
    
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

    # si todo está OK, descontamos
    for producto_id, cant_receta, unidad, cant_actual, nombre in ingredientes:
        nueva_cantidad = cant_actual - cant_receta
        cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_id))

    conexion_bd.commit()
    conexion_bd.close()

    # actualizamos la  lista de compras
    verificar_stock_minimo()

    print(f"Receta {receta_id} preparada correctamente y stock actualizado.")


    #para futuro , quizas hacer algo para saber cuantas recetas podria hacer con lso ingredientes que hay...
