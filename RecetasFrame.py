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
        tk.Button(self.frame_recetas, text="✏️ Modificar", command=self.modificar_receta, bg="#FF9800", fg="white").grid(row=0, column=2, padx=5)
        tk.Button(self.frame_recetas, text="🗑️ Borrar", command=self.borrar_receta, bg="#F44336", fg="white").grid(row=0, column=3, padx=5)
        tk.Button(self.frame_recetas, text="📝 Añadir a Lista de Pendientes", command=self.usar_receta, bg="#2196F3", fg="white").grid(row=0, column=4, padx=5)

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

        tk.Button(self.frame_ing, text="🗑️ Borrar", command=self.borrar_ingrediente,
                bg="#F44336", fg="white").grid(row=0, column=2, padx=5)


        # =========================
        # MENÚ RECETAS
        # =========================
        self.menu_recetas = tk.Menu(self, tearoff=0)
        self.menu_recetas.add_command(label="➕ Nueva receta", command=self.crear_receta)
        self.menu_recetas.add_command(label="✏️ Modificar receta", command=self.modificar_receta)
        self.menu_recetas.add_command(label="🗑️ Borrar receta", command=self.borrar_receta)
        self.menu_recetas.add_separator()
        self.menu_recetas.add_command(label="📝 Usar receta", command=self.usar_receta)

        # =========================
        # MENÚ INGREDIENTES
        # =========================
        self.menu_ing = tk.Menu(self, tearoff=0)
        self.menu_ing.add_command(label="➕ Añadir", command=self.anadir_ingrediente)
        self.menu_ing.add_command(label="✏️ Modificar", command=self.modificar_ingrediente)
        self.menu_ing.add_command(label="🗑️ Borrar", command=self.borrar_ingrediente)

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
        if self.tree.get_children():
            first = self.tree.get_children()[0]
            self.tree.selection_set(first)
            self.tree.focus(first)
            self.after(50, lambda: self.on_select_receta(None))#para que no se descuadre visualemnte

    def on_select_receta(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return

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
            # Redondeamos la cantidad a 2 decimales antes de mostrarla
            try:
                cantidad_limpia = round(float(f[1]), 2)
            except:
                cantidad_limpia = f[1] # Si no es número, lo dejamos como está
            
            # Insertamos los valores con la cantidad ya redondeada
            self.tree_ing.insert("", "end", values=(f[0], cantidad_limpia, f[2]), tags=(f[3],))

        conn.close()

    # =====================================================
    # CRUD RECETAS
    # =====================================================
    def crear_receta(self):
        win = tk.Toplevel(self)
        win.title("Nueva Receta")
        win.geometry("300x180")

        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"
        entry_bg = "#2E2E2E" if modo else "white"

        win.configure(bg=bg)

        tk.Label(win, text="Nombre de la receta:", bg=bg, fg=fg, font=("Arial", 10, "bold")).pack(pady=(20, 5))

        e = tk.Entry(win, bg=entry_bg, fg=fg, insertbackground=fg, font=("Arial", 10))
        e.pack(pady=5, padx=20)
        e.focus_set() # Para poder escribir directamente

        def guardar():
            nombre = e.get().strip()
            if not nombre:
                messagebox.showwarning("Atención", "El nombre no puede estar vacío")
                return
                
            conn = conexion()
            cur = conn.cursor()
            cur.execute("INSERT INTO recetas (nombre) VALUES (?)", (nombre,))
            conn.commit()
            conn.close()
            win.destroy()
            self.cargar()

        tk.Button(win, text="Guardar", command=guardar, bg="#4CAF50", fg="white", 
                  bd=0, padx=15, pady=6, cursor="hand2").pack(pady=15)

    def modificar_receta(self):
        sel = self.tree.selection()
        if not sel:
            return

        rid, nombre_antiguo = self.tree.item(sel[0])["values"]

        win = tk.Toplevel(self)
        win.title(f"Editando: {nombre_antiguo}")
        win.geometry("300x180")

        modo = self.controller.modo_oscuro
        bg, fg, entry_bg = ("#121212", "white", "#2E2E2E") if modo else ("#F0F0F0", "black", "white")
        win.configure(bg=bg)

        tk.Label(win, text="Nuevo nombre:", bg=bg, fg=fg, font=("Arial", 10, "bold")).pack(pady=(20, 5))
        e = tk.Entry(win, bg=entry_bg, fg=fg, insertbackground=fg, font=("Arial", 10))
        e.insert(0, nombre_antiguo)
        e.pack(pady=5, padx=20)

        def guardar():
            nuevo_nombre = e.get().strip()
            if nuevo_nombre:
                conn = conexion()
                cur = conn.cursor()
                cur.execute("UPDATE recetas SET nombre=? WHERE id=?", (nuevo_nombre, rid))
                conn.commit()
                conn.close()
                win.destroy()
                self.cargar()

        tk.Button(win, text="Actualizar", command=guardar, bg="#FF9800", fg="white", 
                  bd=0, padx=15, pady=6, cursor="hand2").pack(pady=15)
        

    def borrar_receta(self):
        sel = self.tree.selection()
        if not sel:
            return

        if not messagebox.askyesno("Confirmar", "¿Borrar esta receta?"):
            return

        rid = self.tree.item(sel[0])["values"][0]

        conn = None # Inicializamos para evitar errores en el finally
        try:
            conn = conexion()
            cur = conn.cursor()
            
            # 1. Borrar dependencias primero
            cur.execute("DELETE FROM receta_ingredientes WHERE receta_id=?", (rid,))
            # 2. Borrar la receta
            cur.execute("DELETE FROM recetas WHERE id=?", (rid,))
            
            conn.commit()
            print("Borrado exitoso.")

        except Exception as e:
            print(f"Error al borrar: {e}")
            if conn:
                conn.rollback() # Si falla, deshacemos los cambios
            messagebox.showerror("Error", f"No se pudo borrar: {e}")
        
        finally:
            if conn:
                conn.close() # 🔑 ¡ESTO ES LO MÁS IMPORTANTE!
                print("Conexión cerrada.")

        # Limpiar y recargar
        self.tree_ing.delete(*self.tree_ing.get_children())
        self.cargar()

    def usar_receta(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona una receta.")
            return

        rid = self.tree.item(sel[0])["values"][0]
        nombre_receta = self.tree.item(sel[0])["values"][1]

        try:
            conn = conexion()
            cur = conn.cursor()

            # ✅ CORREGIDO: p.stock_minimo coincide ahora con tu CREATE TABLE
            cur.execute("""
                SELECT ri.producto_id, p.nombre, ri.cantidad, p.cantidad, p.unidad, p.stock_minimo
                FROM receta_ingredientes ri
                JOIN productos p ON ri.producto_id = p.id
                WHERE ri.receta_id = ?
            """, (rid,))
            
            ingredientes = cur.fetchall()
            if not ingredientes:
                messagebox.showwarning("Atención", "Esta receta no tiene ingredientes.")
                conn.close()
                return

            items_anadidos = []

            for p_id, p_nombre, cant_nec, stock_act, unidad, stock_min in ingredientes:
                try:
                    # 🛡️ Limpieza total para evitar errores de 'str' a 'float'
                    # Si el campo está vacío o es None, usamos "0.0"
                    n_necesaria = float(str(cant_nec).strip().replace(',', '.')) if cant_nec else 0.0
                    
                    raw_stock = float(str(stock_act).strip().replace(',', '.')) if stock_act else 0.0
                    n_stock = max(0.0, raw_stock) # Filtro para el aceite -2.0
                    
                    n_minimo = float(str(stock_min).strip().replace(',', '.')) if stock_min else 0.0
                except (ValueError, TypeError):
                    n_necesaria = n_stock = n_minimo = 0.0

                # 💡 Lógica de Stock Mínimo
                stock_proyectado = n_stock - n_necesaria

                if stock_proyectado < n_minimo:
                    # Calculamos cuánto falta para cubrir la receta y quedar en el mínimo
                    faltante = round((n_necesaria + n_minimo) - n_stock, 2)
                    
                    if faltante > 0:
                        cur.execute("SELECT id, cantidad FROM lista_compras WHERE producto_id = ? AND comprado = 0", (p_id,))
                        existe = cur.fetchone()
                        
                        if existe:
                            try:
                                cant_previa = float(str(existe[1]).replace(',', '.'))
                                nueva_cant = round(cant_previa + faltante, 2)
                                cur.execute("UPDATE lista_compras SET cantidad = ? WHERE id = ?", (nueva_cant, existe[0]))
                            except: pass
                        else:
                            cur.execute("""
                                INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado)
                                VALUES (?, ?, ?, 0)
                            """, (p_id, faltante, unidad))
                        
                        items_anadidos.append(f"- {p_nombre}: {faltante} {unidad}")

            # Registrar la receta en pendientes
            cur.execute("""
                INSERT INTO recetas_pendientes (receta_id, fecha_planificada, completada)
                VALUES (?, date('now', 'localtime'), 0)
            """, (rid,))

            conn.commit()
            conn.close()

            mensaje = f"✅ '{nombre_receta}' añadida a pendientes."
            if items_anadidos:
                mensaje += "\n\n⚠️ Stock insuficiente o bajo mínimos. Añadido a la lista de compras:\n" + "\n".join(items_anadidos)
            else:
                mensaje += "\n\n✨ Tienes stock suficiente para esta receta."
                
            messagebox.showinfo("Planificador", mensaje)

        except Exception as e:
            if 'conn' in locals() and conn: conn.close()
            messagebox.showerror("Error", f"Fallo crítico: {e}")

            

    # =====================================================
    # INGREDIENTES
    # =====================================================
    def anadir_ingrediente(self):
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Atención", "Selecciona primero una receta a la que añadir ingredientes.")
                return

            rid = self.tree.item(sel[0])["values"][0]

            win = tk.Toplevel(self)
            win.title("Añadir ingrediente")
            win.geometry("300x350") # Un tamaño fijo queda más ordenado

            modo = self.controller.modo_oscuro
            bg = "#121212" if modo else "#F0F0F0"
            fg = "white" if modo else "black"
            entry_bg = "#2E2E2E" if modo else "white"
            btn_bg = "#4CAF50"

            win.configure(bg=bg)

            # ===== CARGAR PRODUCTOS =====
            conn = conexion()
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, unidad FROM productos ORDER BY nombre ASC")
            productos = cur.fetchall()
            conn.close()

            opciones = {
                f"{nombre} ({unidad})": (pid, unidad)
                for pid, nombre, unidad in productos
            }

            # --- UI ---
            tk.Label(win, text="Seleccionar Producto", bg=bg, fg=fg, font=("Arial", 10, "bold")).pack(pady=(15, 0))
            
            combo = ttk.Combobox(
                win,
                values=list(opciones.keys()),
                state="readonly",
                width=30
            )
            combo.pack(pady=10)

            tk.Label(win, text="Cantidad", bg=bg, fg=fg, font=("Arial", 10, "bold")).pack(pady=(10, 0))
            
            c = tk.Entry(
                win,
                bg=entry_bg,
                fg=fg,
                insertbackground=fg,
                font=("Arial", 10)
            )
            c.pack(pady=5)

            def guardar():
                # 1. Validar producto seleccionado
                seleccion = combo.get()
                if not seleccion:
                    messagebox.showwarning("Faltan datos", "Por favor, selecciona un producto.")
                    return

                # 2. Validar cantidad (que no esté vacía)
                cantidad = c.get().strip()
                if not cantidad:
                    messagebox.showwarning("Faltan datos", "Introduce una cantidad.")
                    return

                producto_id, unidad = opciones[seleccion]

                conn = conexion()
                cur = conn.cursor()

                # 3. Evitar duplicados (¡Esto ya lo tenías y es genial!)
                cur.execute("""
                    SELECT 1 FROM receta_ingredientes
                    WHERE receta_id=? AND producto_id=?
                """, (rid, producto_id))

                if cur.fetchone():
                    messagebox.showerror("Error", "Ese ingrediente ya existe en esta receta.")
                    conn.close()
                    return

                try:
                    cur.execute("""
                        INSERT INTO receta_ingredientes
                        (receta_id, producto_id, cantidad, unidad)
                        VALUES (?,?,?,?)
                    """, (rid, producto_id, cantidad, unidad))

                    conn.commit()
                    conn.close()
                    win.destroy()
                    self.cargar_ingredientes(rid) # Refrescamos la tabla de abajo
                    
                except Exception as e:
                    messagebox.showerror("Error de BD", f"No se pudo guardar: {e}")

            tk.Button(
                win, 
                text="Añadir a la Receta", 
                command=guardar, 
                bg=btn_bg, 
                fg="white",
                font=("Arial", 10, "bold"),
                padx=20,
                pady=8,
                bd=0,
                cursor="hand2"
            ).pack(pady=25)


    def modificar_ingrediente(self):
        sel_r = self.tree.selection()
        sel_i = self.tree_ing.selection()

        if not sel_r or not sel_i:
            messagebox.showwarning("Atención", "Selecciona una receta y un ingrediente")
            return

        rid = self.tree.item(sel_r[0])["values"][0]
        item = self.tree_ing.item(sel_i[0])
        
        # Obtenemos valores actuales
        valores = item["values"]
        nombre_prod = valores[0]
        cant_actual = valores[1]
        unid_actual = valores[2]
        
        # IMPORTANTE: El ID del producto está en el primer tag
        pid = item["tags"][0] 

        win = tk.Toplevel(self)
        win.title(f"Modificando: {nombre_prod}")
        win.geometry("300x250") # Añadido un tamaño base

        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"
        entry_bg = "#2E2E2E" if modo else "white"
        win.configure(bg=bg)

        tk.Label(win, text=f"Producto: {nombre_prod}", bg=bg, fg="#4CAF50", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(win, text="Nueva Cantidad:", bg=bg, fg=fg).pack(pady=(5, 0))
        e1 = tk.Entry(win, bg=entry_bg, fg=fg, insertbackground=fg)
        e1.insert(0, cant_actual)
        e1.pack(pady=5, padx=20)

        tk.Label(win, text="Nueva Unidad:", bg=bg, fg=fg).pack(pady=(5, 0))
        e2 = tk.Entry(win, bg=entry_bg, fg=fg, insertbackground=fg)
        e2.insert(0, unid_actual)
        e2.pack(pady=5, padx=20)

        def guardar():
            try:
                nueva_cant = e1.get().strip()
                nueva_unid = e2.get().strip()
                
                if not nueva_cant:
                    messagebox.showwarning("Error", "La cantidad no puede estar vacía.")
                    return

                conn = conexion()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE receta_ingredientes
                    SET cantidad=?, unidad=?
                    WHERE receta_id=? AND producto_id=?
                """, (nueva_cant, nueva_unid, rid, pid))
                
                conn.commit()
                conn.close()
                
                win.destroy()
                self.cargar_ingredientes(rid) 
            except Exception as error:
                messagebox.showerror("Error", f"No se pudo actualizar: {error}")

        tk.Button(
            win, text="Guardar Cambios", command=guardar,
            bg="#FF9800", fg="white", bd=0, padx=15, pady=7, cursor="hand2"
        ).pack(pady=20)

    def borrar_ingrediente(self):
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

        # SOLO refrescar UI, NO redefinir estilos
        self.aplicar_tema()

    def aplicar_tema(self):
        self.tree.configure(style="Treeview")
        self.tree_ing.configure(style="Treeview")

        self.update()
        self.update_idletasks()

        self.tree.update()
        self.tree_ing.update()


    
