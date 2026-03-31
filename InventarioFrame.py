import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Importamos tus módulos de lógica
from acceso_base_datos import conexion
from inventario import ver_inventario

# =========================
# 📦 INVENTARIO
# =========================
class InventarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Creamos la interfaz
        self.setup_ui()
        # Aplicamos colores iniciales
        self.actualizar_colores()

    def setup_ui(self):
        modo = self.controller.modo_oscuro

        # 🌙 --- BOTÓN MODO OSCURO ---
        bg_init = "#121212" if modo else "#E8F5E9"
        fg_init = "white" if modo else "black"

        self.toggle_btn = tk.Button(
            self,
            text="☀️" if modo else "🌙",
            command=self.alternar_modo,
            font=("Segoe UI Emoji", 14),
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            bg=bg_init,
            fg=fg_init,
            activebackground=bg_init,
            activeforeground=fg_init
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # 🔹 Título
        self.label_titulo = tk.Label(
            self,
            text="📦 INVENTARIO DE PRODUCTOS",
            font=("Arial", 20, "bold")
        )
        self.label_titulo.pack(pady=(20, 10))

        # 🔹 Boton volver (Usando la función de enlace ir_a_home)
        self.btn_volver = tk.Button(
            self,
            text="⬅ Volver al Inicio",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.ir_a_home
        )
        self.btn_volver.pack(pady=5)

        # ---------------------------------------------------------
        # 📂 CONTENEDOR MODERNO DE TABLA + SCROLLBAR
        # ---------------------------------------------------------
        self.frame_tabla = tk.Frame(self)
        self.frame_tabla.pack(fill="both", expand=True, padx=20, pady=15)

        scrollbar = tk.Scrollbar(self.frame_tabla)
        scrollbar.pack(side="right", fill="y")

        columnas = ("ID", "Producto", "Cantidad", "Unidad", "Min")

        self.tree = ttk.Treeview(
            self.frame_tabla,
            columns=columnas,
            show="headings",
            yscrollcommand=scrollbar.set
        )

        scrollbar.config(command=self.tree.yview)

        # 👇 columnas más limpias y modernas
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50, anchor="center")

        self.tree.heading("Producto", text="Producto")
        self.tree.column("Producto", width=220, anchor="center")

        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.column("Cantidad", width=100, anchor="center")

        self.tree.heading("Unidad", text="Unidad")
        self.tree.column("Unidad", width=100, anchor="center")

        self.tree.heading("Min", text="Min")
        self.tree.column("Min", width=80, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        # 🔹 Menú contextual (igual que lo tienes)
        self.menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 10, "bold"), bd=0)
        self.menu.add_command(label="➕   Añadir producto", command=self.abrir_agregar)
        self.menu.add_command(label="✏️   Modificar producto", command=self.modificar_producto)
        self.menu.add_separator()
        self.menu.add_command(label="🗑️   Borrar producto", command=self.borrar_producto)

        self.tree.bind("<Button-3>", self.mostrar_menu)

        # 🔹 Frame de botones de acción
        self.frame_acciones = tk.Frame(self)
        self.frame_acciones.pack(pady=10)

        tk.Button(self.frame_acciones, text="➕ Añadir", command=self.abrir_agregar, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), bd=0, padx=10, pady=6, cursor="hand2").pack(side="left", padx=5)
        tk.Button(self.frame_acciones, text="✏️ Modificar", command=self.modificar_producto, bg="#FF9800", fg="white", font=("Arial", 10, "bold"), bd=0, padx=10, pady=6, cursor="hand2").pack(side="left", padx=5)
        tk.Button(self.frame_acciones, text="❌ Borrar", command=self.borrar_producto, bg="#F44336", fg="white", font=("Arial", 10, "bold"), bd=0, padx=10, pady=6, cursor="hand2").pack(side="left", padx=5)

        # 🔹 Botón cargar datos
        self.btn_cargar = tk.Button(
            self,
            text="🔄 Cargar Datos",
            fg="white",
            font=("Arial", 11, "bold"),
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.cargar
        )
        self.btn_cargar.pack(pady=10)

    def actualizar_colores(self):
        modo = self.controller.modo_oscuro
        bg_main = "#121212" if modo else "#E8F5E9"
        fg_text = "white" if modo else "black"
        bg_card = "#1E1E1E" if modo else "#F1F8E9"

        self.configure(bg=bg_main)
        self.label_titulo.config(bg=bg_main, fg="#4CAF50" if modo else "#1B5E20")
        self.btn_volver.config(bg="#333333" if modo else "#A5D6A7", fg="white" if modo else "black")
        self.frame_acciones.config(bg=bg_main)
        self.frame_tabla.config(bg=bg_main)
        self.btn_cargar.config(bg="#1976D2" if modo else "#2196F3")
        self.menu.config(bg=bg_card, fg=fg_text, activebackground="#4CAF50")
        
        self.toggle_btn.config(bg=bg_main, fg=fg_text, activebackground=bg_main)

    def alternar_modo(self):
        self.controller.toggle_modo_oscuro()
        self.actualizar_colores()
        # Actualizamos el icono del botón
        modo = self.controller.modo_oscuro
        self.toggle_btn.config(text="☀️" if modo else "🌙")

    def cargar(self):
        datos = ver_inventario()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for fila in datos:
            self.tree.insert("", "end", values=fila)

    def mostrar_menu(self, event):
        try:
            row = self.tree.identify_row(event.y)
            if row:
                self.tree.selection_set(row)
                self.menu.post(event.x_root, event.y_root)
        except:
            pass

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
            conn = conexion()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?,?,?,?)",
                           (nombre.get(), cantidad.get(), unidad.get(), minimo.get()))
            conn.commit()
            conn.close()
            ventana.destroy()
            self.cargar()

        tk.Button(ventana, text="Guardar", bg="#4CAF50", fg="white", command=guardar).pack(pady=15)

    def borrar_producto(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un producto")
            return
        
        producto_id = self.tree.item(seleccion)["values"][0]
        if messagebox.askyesno("Confirmar", "¿Borrar este producto?"):
            conn = conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            conn.commit()
            conn.close()
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
            e = tk.Entry(ventana)
            e.insert(0, valor_inicial)
            e.pack(pady=5, padx=20)
            return e

        enombre = crear_entry("Nombre", n_act)
        ecantidad = crear_entry("Cantidad", c_act)
        eunidad = crear_entry("Unidad", u_act)
        eminimo = crear_entry("Stock mínimo", m_act)

        def guardar():
            conn = conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET nombre=?, cantidad=?, unidad=?, stock_minimo=? WHERE id=?",
                           (enombre.get(), ecantidad.get(), eunidad.get(), eminimo.get(), p_id))
            
            # Lógica inteligente para lista de compras
            cant_actual = float(ecantidad.get())
            cant_minima = float(eminimo.get())

            if cant_minima > cant_actual:
                cursor.execute("SELECT * FROM lista_compras WHERE producto_id=? AND comprado=0", (p_id,))
                resultado = cursor.fetchall()
                diferencia = cant_minima - cant_actual
                if resultado:
                    cursor.execute("UPDATE lista_compras SET cantidad=? WHERE id=?", (diferencia, resultado[0][0]))
                else:
                    cursor.execute("INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado) VALUES (?, ?, ?, 0)", 
                                   (p_id, diferencia, eunidad.get()))
            
            conn.commit()
            conn.close()
            ventana.destroy()
            self.cargar()

        tk.Button(ventana, text="Guardar cambios", bg="#FF9800", fg="white", command=guardar).pack(pady=15)

    def ir_a_home(self):
        """Función de enlace para evitar importación circular"""
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)