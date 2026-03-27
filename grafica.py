import tkinter as tk
from tkinter import ttk, messagebox
from lista_compra import marcar_comprado, ver_tareas_todas
from recetas import generar_lista_desde_receta, obtener_recetas   # 👈 IMPORTANTE
from acceso_base_datos import conexion
from recetas import obtener_recetas, preparar_receta
from inventario import ver_inventario

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartKitchen Inventory")
        self.root.geometry("700x500")

        # =========================
        # FRAME BOTONES (ARRIBA)
        # =========================
        frame_botones = tk.Frame(root)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Cargar lista", command=self.cargar_lista).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Marcar comprado", command=self.marcar_seleccionado).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Ver lista compras", command=self.mostrar_compras).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Ver inventario", command=self.mostrar_inventario).pack(side="left", padx=5)

        # =========================
        # TABLA (CENTRO)
        # =========================
        self.tree = ttk.Treeview(
            root,
            columns=("ID", "Producto", "Cantidad", "Unidad"),
            show="headings"
        )

        self.tree.heading("ID", text="ID")
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Unidad", text="Unidad")

        self.tree.pack(fill="both", expand=True)



        #ver inventario
        self.tree_inventario = ttk.Treeview(
            root,
            columns=("ID", "Producto", "Cantidad", "Unidad", "Min"),
            show="headings"
        )

        self.tree_inventario.heading("ID", text="ID")
        self.tree_inventario.heading("Producto", text="Producto")
        self.tree_inventario.heading("Cantidad", text="Cantidad")
        self.tree_inventario.heading("Unidad", text="Unidad")
        self.tree_inventario.heading("Min", text="Stock mínimo")

        # 👇 NO SE MUESTRA AL INICIO
        self.tree_inventario.pack_forget()


        # =========================
        # FRAME RECETAS (ABAJO)
        # =========================
        frame_recetas = tk.Frame(root)
        frame_recetas.pack(pady=10)

        tk.Label(frame_recetas, text="Recetas disponibles").pack()

        self.lista_recetas = tk.Listbox(frame_recetas, height=5)
        self.lista_recetas.pack()

        tk.Button(frame_recetas, text="Usar receta", command=self.usar_receta).pack(pady=5)

        # CARGAMOS RECETAS
        self.cargar_recetas()

        #  ESTO ES CLAVE
        self.mostrar_compras()
    # =========================
    # CARGAR LISTA COMPRAS
    # =========================
    def cargar_lista(self):
        try:
            datos = ver_tareas_todas()

            # Limpiamos tabla
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insertamos datos
            for fila in datos:
                self.tree.insert("", "end", values=fila)

        except Exception as e:
            messagebox.showerror("Error", f"No hemos podido cargar los datos: {e}")

    # =========================
    # CARGAR RECETAS
    # =========================
    def cargar_recetas(self):
        # Cargamos recetas desde la base de datos
        conexion_bd = conexion()
        cursor = conexion_bd.cursor()

        cursor.execute("SELECT id, nombre FROM recetas")
        recetas = cursor.fetchall()

        self.lista_recetas.delete(0, tk.END)

        for receta in recetas:
            self.lista_recetas.insert(tk.END, f"{receta[0]} - {receta[1]}")

        conexion_bd.close()

    # =========================
    # USAR RECETA
    # =========================
    def usar_receta(self):
        seleccion = self.lista_recetas.get(tk.ACTIVE)

        if not seleccion:
            messagebox.showerror("Error", "Selecciona una receta")
            return

        receta_id = int(seleccion.split(" - ")[0])

        generar_lista_desde_receta(receta_id)

        messagebox.showinfo("OK", "Lista de compras actualizada")

        # Recargamos tabla automáticamente
        self.cargar_lista()


    def marcar_seleccionado(self):
        # Obtenemos elemento seleccionado
        seleccion = self.tree.selection()

        if not seleccion:
            messagebox.showerror("Error", "Selecciona un producto")
            return

        # Obtenemos valores de la fila
        item = self.tree.item(seleccion)
        valores = item["values"]

        item_id = valores[0]  # ID de lista_compras

        # Marcamos como comprado
        marcar_comprado(item_id)

        messagebox.showinfo("OK", "Producto marcado como comprado")

        # Refrescamos tabla
        self.cargar_lista()

        # =========================
        # VER RECETAS
        # =========================
    def ver_recetas(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Recetas disponibles")
        ventana.geometry("350x400")

        recetas = obtener_recetas()

        for receta_id, nombre in recetas:

            frame = tk.Frame(ventana)
            frame.pack(fill="x", pady=5)

            # Nombre receta
            tk.Label(frame, text=nombre).pack(side="left", padx=10)

            # Botón preparar
            tk.Button(
                frame,
                text="Preparar",
                command=lambda r_id=receta_id: self.preparar_receta_ui(r_id)
            ).pack(side="right", padx=10)


    def preparar_receta_ui(self, receta_id):
        try:
            preparar_receta(receta_id)
            messagebox.showinfo("OK", "Receta preparada correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo preparar: {e}")

    def cargar_inventario(self):
        datos = ver_inventario()

        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)

        for fila in datos:
            self.tree_inventario.insert("", "end", values=fila)

    def mostrar_compras(self):
        self.tree_inventario.pack_forget()
        self.tree.pack(fill="both", expand=True)
        self.cargar_lista()


    def mostrar_inventario(self):
        self.tree.pack_forget()
        self.tree_inventario.pack(fill="both", expand=True)
        self.cargar_inventario()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()