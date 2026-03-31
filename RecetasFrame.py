import tkinter as tk
from tkinter import ttk, messagebox

# Importamos la lógica necesaria
from acceso_base_datos import conexion
from recetas import obtener_recetas, generar_lista_desde_receta

class RecetasFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        # 1. CONFIGURACIÓN DE COLORES Y FONDO
        modo = self.controller.modo_oscuro
        bg_color = "#121212" if modo else "#F0F0F0"
        fg_color = "white" if modo else "black"
        self.configure(bg=bg_color)

        # ☀️/🌙 BOTÓN MODO OSCURO
        self.toggle_btn = tk.Button(
            self, text="☀️" if modo else "🌙", command=self.alternar_modo,
            font=("Segoe UI Emoji", 14), bd=0, cursor="hand2",
            bg=bg_color, fg=fg_color, activebackground=bg_color
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # 🔹 TÍTULO
        self.label_titulo = tk.Label(self, text="🍳 RECETARIO", font=("Arial", 18, "bold"), 
                                     bg=bg_color, fg="#4CAF50" if modo else "#1B5E20")
        self.label_titulo.pack(pady=10)

        # ⬅ BOTÓN VOLVER
        self.btn_volver = tk.Button(self, text="⬅ Volver", command=self.ir_a_home, 
                                    font=("Arial", 10, "bold"), bd=0, padx=10,
                                    bg="#333333" if modo else "#A5D6A7", 
                                    fg="white" if modo else "black")
        self.btn_volver.pack(pady=5)

        # 📋 TABLA RECETAS (ARRIBA)
        self.tree = ttk.Treeview(self, columns=("ID", "Nombre"), show="headings", height=6)
        self.tree.heading("ID", text="ID"); self.tree.heading("Nombre", text="Receta")
        self.tree.column("ID", width=50, anchor="center"); self.tree.column("Nombre", width=300)
        self.tree.pack(pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_receta)

        # 🔹 BOTONES RECETAS
        self.frame_btn_recetas = tk.Frame(self, bg=bg_color)
        self.frame_btn_recetas.pack(pady=5)
        tk.Button(self.frame_btn_recetas, text="🔄 Cargar", command=self.cargar).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_btn_recetas, text="➕ Nueva", command=self.crear_receta, bg="#4CAF50", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(self.frame_btn_recetas, text="✏️ Editar", command=self.editar_receta, bg="#FF9800", fg="white").grid(row=0, column=2, padx=5)
        tk.Button(self.frame_btn_recetas, text="🗑️ Borrar", command=self.borrar_receta, bg="#F44336", fg="white").grid(row=0, column=3, padx=5)
        tk.Button(self.frame_btn_recetas, text="📝 Usar", command=self.usar_receta, bg="#FF9800", fg="white").grid(row=0, column=4, padx=5)

        # 🧾 SECCIÓN INGREDIENTES (ABAJO)
        self.label_ing = tk.Label(self, text="Ingredientes", font=("Arial", 14, "bold"), 
                                  bg=bg_color, fg=fg_color)
        self.label_ing.pack(pady=10)

        self.tree_ing = ttk.Treeview(self, columns=("Producto", "Cantidad", "Unidad"), show="headings")
        self.tree_ing.heading("Producto", text="Producto"); self.tree_ing.heading("Cantidad", text="Cant"); self.tree_ing.heading("Unidad", text="Unid")
        self.tree_ing.pack(fill="both", expand=True, padx=20, pady=10)

        # 🔹 BOTONES INGREDIENTES
        self.frame_btn_ing = tk.Frame(self, bg=bg_color)
        self.frame_btn_ing.pack(pady=5)
        tk.Button(self.frame_btn_ing, text="➕ Añadir", command=self.anadir_ingrediente, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(self.frame_btn_ing, text="❌ Eliminar", command=self.eliminar_ingrediente, bg="#F44336", fg="white").grid(row=0, column=1, padx=5)

    # --- NAVEGACIÓN Y MODO ---
    def ir_a_home(self):
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def alternar_modo(self):
        sel = self.tree.selection()
        id_sel = self.tree.item(sel[0])['values'][0] if sel else None
        self.controller.toggle_modo_oscuro()
        if id_sel:
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == id_sel:
                    self.tree.selection_set(item)
                    self.cargar_ingredientes(id_sel)
                    break

    # --- LÓGICA DE CARGA Y SELECCIÓN ---
    def cargar(self):
        self.tree.delete(*self.tree.get_children())
        self.tree_ing.delete(*self.tree_ing.get_children())

        self._receta_actual = None  # 🔥 RESET REAL

        recetas = obtener_recetas()
        for r in recetas:
            self.tree.insert("", "end", values=(r[0], r[1]))
            
    def on_select_receta(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        receta_id = self.tree.item(sel[0])["values"][0]

        # 🔥 SOLUCIÓN REAL: comprobar lo que ya está mostrado
        if self.tree_ing.get_children():
            # ya hay ingredientes cargados → evitar recarga innecesaria
            actual = getattr(self, "_receta_actual", None)
            if actual == receta_id:
                return

        self._receta_actual = receta_id
        self.cargar_ingredientes(receta_id)

    def cargar_ingredientes(self, receta_id):
        """Limpia la tabla de ingredientes antes de cargar los nuevos"""
        self.tree_ing.delete(*self.tree_ing.get_children())
        conn = conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.nombre, ri.cantidad, ri.unidad, p.id
            FROM receta_ingredientes ri
            JOIN productos p ON ri.producto_id = p.id
            WHERE ri.receta_id = ?
        """, (receta_id,))
        for fila in cursor.fetchall():
            self.tree_ing.insert("", "end", values=fila[:3], tags=(fila[3],))
        conn.close()

    # --- GESTIÓN DE RECETAS ---
    def crear_receta(self):
        ventana = tk.Toplevel(self)
        ventana.title("Nueva receta")
        tk.Label(ventana, text="Nombre").pack()
        nombre = tk.Entry(ventana); nombre.pack()
        def guardar():
            conn = conexion(); cursor = conn.cursor()
            cursor.execute("INSERT INTO recetas (nombre) VALUES (?)", (nombre.get(),))
            conn.commit(); conn.close(); ventana.destroy(); self.cargar()
        tk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)

    def editar_receta(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Error", "Selecciona una receta"); return
        receta_id, nombre_actual = self.tree.item(sel[0])["values"]
        ventana = tk.Toplevel(self)
        nombre = tk.Entry(ventana); nombre.insert(0, nombre_actual); nombre.pack()
        def guardar():
            conn = conexion(); cursor = conn.cursor()
            cursor.execute("UPDATE recetas SET nombre=? WHERE id=?", (nombre.get(), receta_id))
            conn.commit(); conn.close(); ventana.destroy(); self.cargar()
        tk.Button(ventana, text="Guardar cambios", command=guardar).pack(pady=10)

    def borrar_receta(self):
        sel = self.tree.selection()
        if not sel: return
        receta_id = self.tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirmar", "¿Eliminar receta?"): return
        conn = conexion(); cursor = conn.cursor()
        cursor.execute("DELETE FROM recetas WHERE id=?", (receta_id,))
        cursor.execute("DELETE FROM receta_ingredientes WHERE receta_id=?", (receta_id,))
        conn.commit(); conn.close(); self.cargar()

    def usar_receta(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona una receta."); return
        try:
            receta_id = self.tree.item(sel[0])["values"][0]
            generar_lista_desde_receta(receta_id)
            messagebox.showinfo("Éxito", "Ingredientes añadidos a la lista de compra.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- GESTIÓN DE INGREDIENTES ---
    def anadir_ingrediente(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Error", "Selecciona una receta"); return
        receta_id = self.tree.item(sel[0])["values"][0]
        ventana = tk.Toplevel(self)
        tk.Label(ventana, text="ID Producto").pack(); prod_id = tk.Entry(ventana); prod_id.pack()
        tk.Label(ventana, text="Cantidad").pack(); cant = tk.Entry(ventana); cant.pack()
        tk.Label(ventana, text="Unidad").pack(); unid = tk.Entry(ventana); unid.pack()
        def guardar():
            conn = conexion(); cursor = conn.cursor()
            cursor.execute("INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad) VALUES (?,?,?,?)",
                           (receta_id, prod_id.get(), cant.get(), unid.get()))
            conn.commit(); conn.close(); ventana.destroy(); self.cargar_ingredientes(receta_id)
        tk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)

    def eliminar_ingrediente(self):
        sel_receta = self.tree.selection()
        sel_ing = self.tree_ing.selection()
        if not sel_receta or not sel_ing:
            messagebox.showwarning("Error", "Selecciona ingrediente"); return
        receta_id = self.tree.item(sel_receta[0])["values"][0]
        producto_id = self.tree_ing.item(sel_ing[0])["tags"][0]
        conn = conexion(); cursor = conn.cursor()
        cursor.execute("DELETE FROM receta_ingredientes WHERE receta_id=? AND producto_id=?", (receta_id, producto_id))
        conn.commit(); conn.close(); self.cargar_ingredientes(receta_id)