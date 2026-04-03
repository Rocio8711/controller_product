import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Importamos tus módulos de lógica
from acceso_base_datos import conexion
from inventario import ver_inventario

# ==========================================
# 📦 INVENTARIO (COLORES DE SELECCIÓN SUAVES)
# ==========================================
class InventarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.menu = None
        self._setup_ui()

    def _setup_ui(self):
        """Dibuja la interfaz completa y limpia restos visuales."""
        for widget in self.winfo_children():
            widget.destroy()

        modo = self.controller.modo_oscuro
        
        # --- Configuración de Colores ---
        bg_main = "#121212" if modo else "#F8F9FA"
        fg_text = "#FFFFFF" if modo else "#333333"
        accent_green = "#2E7D32" if modo else "#1B5E20"
        card_bg = "#1E1E1E" if modo else "#FFFFFF"
        
        # COLORES DE SELECCIÓN SUAVES (Aquí está el cambio)
        # Modo Oscuro: Un verde grisáceo / Modo Claro: Un verde pastel
        select_bg = "#38493A" if modo else "#C8E6C9" 
        select_fg = "#FFFFFF" if modo else "#000000"

        self.configure(bg=bg_main)

        # 2. Botón de Modo Oscuro
        self.toggle_btn = tk.Button(
            self, text="☀️" if modo else "🌙",
            command=self.alternar_modo,
            font=("Segoe UI Emoji", 14), bd=0, cursor="hand2",
            bg=bg_main, fg=fg_text, activebackground=bg_main,
            highlightthickness=0
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # 3. Título
        tk.Label(
            self, text="📦 INVENTARIO DE PRODUCTOS",
            font=("Segoe UI", 24, "bold"),
            bg=bg_main, fg=accent_green
        ).pack(pady=(30, 5))

        # 4. Botón Volver
        tk.Button(
            self, text="⬅ Volver",
            bg="#444444" if modo else "#E0E0E0",
            fg="white" if modo else "black",
            command=self.ir_a_home
        ).pack(pady=5)

        # 5. Estilo de la Tabla (Treeview)
        style = ttk.Style()
        style.theme_use("default") 
        
        style.configure("Treeview", 
                        background=card_bg, 
                        foreground=fg_text,
                        fieldbackground=card_bg,
                        rowheight=30,
                        font=("Segoe UI", 10),
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        background=accent_green, 
                        foreground="white", 
                        font=("Segoe UI", 11, "bold"),
                        relief="flat")
        
        # APLICAR EL VERDE CLARITO AQUÍ 👇
        style.map("Treeview", 
                  background=[('selected', select_bg)],
                  foreground=[('selected', select_fg)])

        # 6. Contenedor de la Tabla
        self.frame_tabla = tk.Frame(self, bg=bg_main)
        self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=5)

        columnas = ("ID", "Producto", "Cantidad", "Unidad", "Min")
        self.tree = ttk.Treeview(self.frame_tabla, columns=columnas, show="headings", style="Treeview")

        for col in columnas:
            self.tree.heading(col, text=col)
            ancho = 250 if col == "Producto" else 80
            self.tree.column(col, width=ancho, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # 7. Menú Contextual
        self.menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 10), bg=card_bg, fg=fg_text)
        self.menu.add_command(label="➕ Añadir producto", command=self.abrir_agregar)
        self.menu.add_command(label="✏️ Modificar producto", command=self.modificar_producto)
        self.menu.add_separator()
        self.menu.add_command(label="🗑️ Borrar producto", command=self.borrar_producto)
        self.tree.bind("<Button-3>", self.mostrar_menu)

        # 8. Frame de Acciones
        self.frame_acciones = tk.Frame(self, bg=bg_main)
        self.frame_acciones.pack(pady=20)

        btn_configs = [
            ("➕ Añadir", "#4CAF50", self.abrir_agregar),
            ("✏️ Modificar", "#FF9800", self.modificar_producto),
            ("❌ Borrar", "#F44336", self.borrar_producto),
            ("🔄 Cargar Datos", "#2196F3", self.cargar)
        ]

        for i, (texto, color, comando) in enumerate(btn_configs):
            tk.Button(
                self.frame_acciones,
                text=texto,
                command=comando,
                bg=color,
                fg="white",
                bd=0
            ).grid(row=0, column=i, padx=5)

        self.cargar()

    def alternar_modo(self):
        self.controller.toggle_modo_oscuro()
        self._setup_ui()

    def ir_a_home(self):
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def mostrar_menu(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            self.tree.selection_set(row)
            self.menu.post(event.x_root, event.y_root)

    def cargar(self):
        datos = ver_inventario()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for fila in datos:
            f_lista = list(fila)
            if isinstance(f_lista[2], (float, int)):
                f_lista[2] = round(float(f_lista[2]), 2)
            self.tree.insert("", "end", values=f_lista)

    def abrir_agregar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Nuevo producto")
        modo = self.controller.modo_oscuro
        ventana.configure(bg="#1E1E1E" if modo else "#F0F0F0")

        def crear_entry(label_text):
            tk.Label(ventana, text=label_text, bg=ventana["bg"], fg="white" if modo else "black").pack(pady=(5,0))
            e = tk.Entry(ventana)
            e.pack(pady=5, padx=20)
            return e

        nombre = crear_entry("Nombre")
        cantidad = crear_entry("Cantidad")
        unidad = crear_entry("Unidad")
        minimo = crear_entry("Stock mínimo")

        def guardar():
            try:
                n, c, u, m = nombre.get(), cantidad.get(), unidad.get(), minimo.get()
                if not n or not c: raise ValueError("Nombre y Cantidad obligatorios")
                conn = conexion(); cur = conn.cursor()
                cur.execute("INSERT INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?,?,?,?)",
                            (n, float(c), u, float(m) if m else 0))
                conn.commit(); conn.close()
                ventana.destroy()
                self.cargar()
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al guardar: {e}")

        tk.Button(ventana, text="Guardar", bg="#4CAF50", fg="white", command=guardar, padx=15).pack(pady=15)

    def borrar_producto(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un producto")
            return
        item = self.tree.item(seleccion); p_id = item["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Borrar '{item['values'][1]}'?"):
            conn = conexion(); cur = conn.cursor()
            cur.execute("DELETE FROM productos WHERE id = ?", (p_id,))
            cur.execute("DELETE FROM lista_compras WHERE producto_id = ?", (p_id,))
            conn.commit(); conn.close()
            self.cargar()

    def modificar_producto(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un producto")
            return
        item = self.tree.item(seleccion)
        p_id, n_act, c_act, u_act, m_act = item["values"]

        ventana = tk.Toplevel(self)
        ventana.title("Modificar producto")
        modo = self.controller.modo_oscuro
        ventana.configure(bg="#1E1E1E" if modo else "#F0F0F0")

        def crear_entry(label_text, valor_inicial):
            tk.Label(ventana, text=label_text, bg=ventana["bg"], fg="white" if modo else "black").pack(pady=(5,0))
            e = tk.Entry(ventana); e.insert(0, valor_inicial); e.pack(pady=5, padx=20)
            return e

        enombre = crear_entry("Nombre", n_act)
        ecantidad = crear_entry("Cantidad", c_act)
        eunidad = crear_entry("Unidad", u_act)
        eminimo = crear_entry("Stock mínimo", m_act)

        def guardar():
            try:
                n_new, c_new = enombre.get(), float(ecantidad.get())
                u_new, m_new = eunidad.get(), float(eminimo.get())
                conn = conexion(); cur = conn.cursor()
                cur.execute("UPDATE productos SET nombre=?, cantidad=?, unidad=?, stock_minimo=? WHERE id=?",
                            (n_new, c_new, u_new, m_new, p_id))
                
                if m_new > c_new:
                    cur.execute("SELECT id FROM lista_compras WHERE producto_id=? AND comprado=0", (p_id,))
                    res = cur.fetchone(); dif = m_new - c_new
                    if res: cur.execute("UPDATE lista_compras SET cantidad=? WHERE id=?", (dif, res[0]))
                    else: cur.execute("INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado) VALUES (?, ?, ?, 0)", (p_id, dif, u_new))
                else:
                    cur.execute("DELETE FROM lista_compras WHERE producto_id=? AND comprado=0", (p_id,))

                conn.commit(); conn.close()
                ventana.destroy(); self.cargar()
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al actualizar: {e}")

        tk.Button(ventana, text="Guardar cambios", bg="#FF9800", fg="white", command=guardar, padx=15).pack(pady=15)