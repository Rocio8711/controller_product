import tkinter as tk
from tkinter import ttk, messagebox

from acceso_base_datos import conexion
from recetas import obtener_recetas, generar_lista_desde_receta


class RecetasFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 🔒 evita ventana gigante
        self.config(height=600)
        self.pack_propagate(False)

        self.setup_ui()

    # =====================================================
    # UI
    # =====================================================
    def setup_ui(self):
        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"

        self.configure(bg=bg)

        # 🌙 toggle
        self.toggle_btn = tk.Button(
            self,
            text="☀️" if modo else "🌙",
            command=self.alternar_modo,
            font=("Segoe UI Emoji", 14),
            bd=0,
            bg=bg,
            fg=fg
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # título
        self.label_titulo = tk.Label(
            self,
            text="🍳 RECETARIO",
            font=("Arial", 18, "bold"),
            bg=bg,
            fg="#4CAF50" if modo else "#1B5E20"
        )
        self.label_titulo.pack(pady=10)

        # volver
        self.btn_volver = tk.Button(
            self,
            text="⬅ Volver",
            command=self.ir_a_home,
            bg="#333333" if modo else "#A5D6A7",
            fg="white" if modo else "black"
        )
        self.btn_volver.pack(pady=5)

        # =========================
        # RECETAS
        # =========================

        frame_recetas_tabla = tk.Frame(self, bg=bg)
        frame_recetas_tabla.pack(fill="x", padx=20, pady=10)

        scroll_recetas = tk.Scrollbar(frame_recetas_tabla)
        scroll_recetas.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            frame_recetas_tabla,
            columns=("ID", "Nombre"),
            show="headings",
            height=6,
            yscrollcommand=scroll_recetas.set
        )

        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Receta")

        self.tree.pack(side="left", fill="both", expand=True)

        scroll_recetas.config(command=self.tree.yview)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_receta)
        self.tree.bind("<Button-3>", self.menu_recetas_popup)

        # botones recetas
        self.frame_recetas = tk.Frame(self, bg=bg)
        self.frame_recetas.pack(pady=5)

        tk.Button(self.frame_recetas, text="➕ Nueva", command=self.crear_receta, bg="#4CAF50", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(self.frame_recetas, text="✏️ Editar", command=self.editar_receta, bg="#FF9800", fg="white").grid(row=0, column=2, padx=5)
        tk.Button(self.frame_recetas, text="🗑️ Borrar", command=self.borrar_receta, bg="#F44336", fg="white").grid(row=0, column=3, padx=5)
        tk.Button(self.frame_recetas, text="📝 Usar", command=self.usar_receta, bg="#2196F3", fg="white").grid(row=0, column=4, padx=5)

        # =========================
        # INGREDIENTES
        # =========================

        self.label_ing = tk.Label(
            self,
            text="Ingredientes",
            font=("Arial", 14, "bold"),
            bg=bg,
            fg=fg
        )
        self.label_ing.pack(pady=10)

        # ===== FRAME TABLA =====
        frame_ing_tabla = tk.Frame(self, bg=bg)
        frame_ing_tabla.pack(fill="x", padx=20, pady=5)

        scroll_ing = tk.Scrollbar(frame_ing_tabla)
        scroll_ing.pack(side="right", fill="y")

        self.tree_ing = ttk.Treeview(
            frame_ing_tabla,
            columns=("Producto", "Cantidad", "Unidad"),
            show="headings",
            height=6,
            yscrollcommand=scroll_ing.set
        )

        self.tree_ing.heading("Producto", text="Producto")
        self.tree_ing.heading("Cantidad", text="Cantidad")
        self.tree_ing.heading("Unidad", text="Unidad")

        self.tree_ing.pack(side="left", fill="both", expand=True)
        scroll_ing.config(command=self.tree_ing.yview)

        self.tree_ing.bind("<Button-3>", self.menu_ing_popup)

        # ===== FRAME BOTONES =====
        self.frame_ing = tk.Frame(self, bg=bg)
        self.frame_ing.pack(pady=5)

        tk.Button(self.frame_ing, text="➕ Añadir", command=self.anadir_ingrediente,
                bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5)

        tk.Button(self.frame_ing, text="✏️ Modificar", command=self.modificar_ingrediente,
                bg="#FF9800", fg="white").grid(row=0, column=1, padx=5)

        tk.Button(self.frame_ing, text="🗑️ Eliminar", command=self.eliminar_ingrediente,
                bg="#F44336", fg="white").grid(row=0, column=2, padx=5)


        # =========================
        # MENÚ RECETAS
        # =========================
        self.menu_recetas = tk.Menu(self, tearoff=0)
        self.menu_recetas.add_command(label="➕ Nueva receta", command=self.crear_receta)
        self.menu_recetas.add_command(label="✏️ Editar receta", command=self.editar_receta)
        self.menu_recetas.add_command(label="🗑️ Eliminar receta", command=self.borrar_receta)
        self.menu_recetas.add_separator()
        self.menu_recetas.add_command(label="📝 Usar receta", command=self.usar_receta)

        # =========================
        # MENÚ INGREDIENTES
        # =========================
        self.menu_ing = tk.Menu(self, tearoff=0)
        self.menu_ing.add_command(label="➕ Añadir", command=self.anadir_ingrediente)
        self.menu_ing.add_command(label="✏️ Modificar", command=self.modificar_ingrediente)
        self.menu_ing.add_command(label="🗑️ Eliminar", command=self.eliminar_ingrediente)

    # =====================================================
    # POPUPS
    # =====================================================
    def menu_recetas_popup(self, event):
        try:
            row = self.tree.identify_row(event.y)
            if row:
                self.tree.selection_set(row)
                self.menu_recetas.post(event.x_root, event.y_root)
        except:
            pass

    def menu_ing_popup(self, event):
        try:
            row = self.tree_ing.identify_row(event.y)
            if row:
                self.tree_ing.selection_set(row)
                self.menu_ing.post(event.x_root, event.y_root)
        except:
            pass

    # =====================================================
    # RECETAS
    # =====================================================
    def cargar(self):
        self.tree.delete(*self.tree.get_children())
        self.tree_ing.delete(*self.tree_ing.get_children())

        for r in obtener_recetas():
            self.tree.insert("", "end", values=(r[0], r[1]))

    def on_select_receta(self, event):
        sel = self.tree.selection()
        if sel:
            rid = self.tree.item(sel[0])["values"][0]
            self.cargar_ingredientes(rid)

    def cargar_ingredientes(self, receta_id):
        self.tree_ing.delete(*self.tree_ing.get_children())

        conn = conexion()
        cur = conn.cursor()

        cur.execute("""
            SELECT p.nombre, ri.cantidad, ri.unidad, p.id
            FROM receta_ingredientes ri
            JOIN productos p ON ri.producto_id = p.id
            WHERE ri.receta_id=?
        """, (receta_id,))

        for f in cur.fetchall():
            self.tree_ing.insert("", "end", values=f[:3], tags=(f[3],))

        conn.close()

    # =====================================================
    # CRUD RECETAS
    # =====================================================
    def crear_receta(self):
        win = tk.Toplevel(self)
        tk.Label(win, text="Nombre").pack()
        e = tk.Entry(win); e.pack()

        def guardar():
            conn = conexion()
            cur = conn.cursor()
            cur.execute("INSERT INTO recetas (nombre) VALUES (?)", (e.get(),))
            conn.commit()
            conn.close()
            win.destroy()
            self.cargar()

        tk.Button(win, text="Guardar", command=guardar).pack()

    def editar_receta(self):
        sel = self.tree.selection()
        if not sel:
            return

        rid, nombre = self.tree.item(sel[0])["values"]

        win = tk.Toplevel(self)
        e = tk.Entry(win)
        e.insert(0, nombre)
        e.pack()

        def guardar():
            conn = conexion()
            cur = conn.cursor()
            cur.execute("UPDATE recetas SET nombre=? WHERE id=?", (e.get(), rid))
            conn.commit()
            conn.close()
            win.destroy()
            self.cargar()

        tk.Button(win, text="Guardar", command=guardar).pack()

    def borrar_receta(self):
        sel = self.tree.selection()
        if not sel:
            return

        rid = self.tree.item(sel[0])["values"][0]

        conn = conexion()
        cur = conn.cursor()
        cur.execute("DELETE FROM recetas WHERE id=?", (rid,))
        cur.execute("DELETE FROM receta_ingredientes WHERE receta_id=?", (rid,))
        conn.commit()
        conn.close()

        self.cargar()

    def usar_receta(self):
        sel = self.tree.selection()
        if not sel:
            return

        rid = self.tree.item(sel[0])["values"][0]
        generar_lista_desde_receta(rid)

    # =====================================================
    # INGREDIENTES
    # =====================================================
    def anadir_ingrediente(self):
        sel = self.tree.selection()
        if not sel:
            return

        rid = self.tree.item(sel[0])["values"][0]

        win = tk.Toplevel(self)
        win.title("Añadir ingrediente")

        tk.Label(win, text="Producto").pack()

        conn = conexion()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, unidad FROM productos")
        productos = cur.fetchall()
        conn.close()

        opciones = {f"{p[1]} ({p[2]})": (p[0], p[2]) for p in productos}

        combo = ttk.Combobox(win, values=list(opciones.keys()), state="readonly")
        combo.pack(pady=5)

        tk.Label(win, text="Cantidad").pack()
        c = tk.Entry(win)
        c.pack()

        def guardar():
            if not combo.get():
                return

            producto_id, unidad = opciones[combo.get()]

            conn = conexion()
            cur = conn.cursor()

            cur.execute("""
                SELECT 1 FROM receta_ingredientes
                WHERE receta_id=? AND producto_id=?
            """, (rid, producto_id))

            if cur.fetchone():
                messagebox.showerror("Error", "Ese ingrediente ya existe en esta receta")
                conn.close()
                return

            cur.execute("""
                INSERT INTO receta_ingredientes
                (receta_id, producto_id, cantidad, unidad)
                VALUES (?,?,?,?)
            """, (rid, producto_id, c.get(), unidad))

            conn.commit()
            conn.close()
            win.destroy()
            self.cargar_ingredientes(rid)

        tk.Button(win, text="Guardar", command=guardar).pack(pady=10)

    def modificar_ingrediente(self):
        sel_r = self.tree.selection()
        sel_i = self.tree_ing.selection()

        if not sel_r or not sel_i:
            return

        rid = self.tree.item(sel_r[0])["values"][0]
        item = self.tree_ing.item(sel_i[0])

        cant, unidad = item["values"][1], item["values"][2]
        pid = item["tags"][0]

        win = tk.Toplevel(self)
        e1 = tk.Entry(win); e1.insert(0, cant); e1.pack()
        e2 = tk.Entry(win); e2.insert(0, unidad); e2.pack()

        def guardar():
            conn = conexion()
            cur = conn.cursor()
            cur.execute("""
                UPDATE receta_ingredientes
                SET cantidad=?, unidad=?
                WHERE receta_id=? AND producto_id=?
            """, (e1.get(), e2.get(), rid, pid))
            conn.commit()
            conn.close()
            win.destroy()
            self.cargar_ingredientes(rid)

        tk.Button(win, text="Guardar", command=guardar).pack()

    def eliminar_ingrediente(self):
        sel_r = self.tree.selection()
        sel_i = self.tree_ing.selection()

        if not sel_r or not sel_i:
            return

        rid = self.tree.item(sel_r[0])["values"][0]
        pid = self.tree_ing.item(sel_i[0])["tags"][0]

        conn = conexion()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM receta_ingredientes
            WHERE receta_id=? AND producto_id=?
        """, (rid, pid))
        conn.commit()
        conn.close()

        self.cargar_ingredientes(rid)

    # =====================================================
    # NAV
    # =====================================================
    def ir_a_home(self):
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def alternar_modo(self):
        self.controller.toggle_modo_oscuro()
        self.setup_ui()