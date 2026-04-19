import tkinter as tk
from tkinter import ttk, messagebox

from InicializacionBaseDatos.acceso_base_datos import conexion
from recetas import obtener_recetas, generar_lista_desde_receta,recalcular_necesidad_producto



'''VENTANA DE RECETAS'''

class RecetasFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(height=600)
        #impedimos que el tamaño dependa de los widgets internos
        self.pack_propagate(False)

        self.setup_ui()

    def setup_ui(self):
        #eliminamos todos los widgets existentes para evitar duplicados
        for widget in self.winfo_children():
            widget.destroy()

        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"

        self.configure(bg=bg)

        #boton modo oscuro
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

        # boton cerrar sesion
        self.logout_btn = tk.Button(
            self, text="🚪",
            command=self.cerrar_sesion,
            font=("Segoe UI Emoji", 14), bd=0, 
            bg=bg, fg="#f44336", # <-- Cambiado bg_main por bg
            activebackground=bg, cursor="hand2"
        )
        self.logout_btn.place(relx=0.98, rely=0.08, anchor="ne")

        #creamos un contenedor para alinear el icono y el texto del titulo
        header_recetario = tk.Frame(self, bg=bg)
        header_recetario.pack(pady=10)

        #El Icono de la Sartén
        tk.Label(
            header_recetario, 
            text="🍳",
            font=("Segoe UI Emoji", 22), 
            bg=bg, 
            fg="#37474F"  # Gris oscuro tipo sartén de hierro
        ).pack(side="left", padx=5)

        # 2. El Texto del Título (Verde)
        tk.Label(
            header_recetario, 
            text="RECETARIO",
            font=("Arial", 18, "bold"),
            bg=bg, 
            fg="#4CAF50" if modo else "#1B5E20"
        ).pack(side="left")

        # volver
        self.btn_volver = tk.Button(
            self, text="⬅ Volver",
            bg="#444444" if modo else "#E0E0E0",
            fg="white" if modo else "black",
            command=self.ir_a_home
        ).pack(pady=5)
        

        #creamos un contenedor para la TABLA DE RECETAS
        frame_recetas_tabla = tk.Frame(self, bg=bg)
        frame_recetas_tabla.pack(fill="x", padx=20, pady=10)

        scroll_recetas = tk.Scrollbar(frame_recetas_tabla)
        scroll_recetas.pack(side="right", fill="y")

        #creamos la tabla donde mostraremos las recetas
        self.tree = ttk.Treeview(
            frame_recetas_tabla,
            columns=("ID", "Nombre"),
            show="headings",
            height=6,
            yscrollcommand=scroll_recetas.set
        )

        #definimos los encabezados de la tabla
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Receta")

        #mostramos la tabla
        self.tree.pack(side="left", fill="both", expand=True)
        #conectamos el scroll con la tabla
        scroll_recetas.config(command=self.tree.yview)

        #detectamos selección de recetas y clic derecho
        self.tree.bind("<<TreeviewSelect>>", self.on_select_receta)
        self.tree.bind("<Button-3>", self.menu_recetas_popup)

        # botones recetas
        self.frame_recetas = tk.Frame(self, bg=bg)
        self.frame_recetas.pack(pady=5)

        tk.Button(self.frame_recetas, text="➕ Nueva", command=self.crear_receta, bg="#4CAF50", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(self.frame_recetas, text="✏️ Modificar", command=self.modificar_receta, bg="#FF9800", fg="white").grid(row=0, column=2, padx=5)
        tk.Button(self.frame_recetas, text="🗑️Borrar", command=self.borrar_receta, bg="#F44336", fg="white").grid(row=0, column=3, padx=5)
        tk.Button(self.frame_recetas, text="📝 Añadir a Lista de Pendientes", command=self.usar_receta, bg="#2196F3", fg="white").grid(row=0, column=4, padx=5)


        # INGREDIENTES
       
        #creamos una etiqueta para indicar la sección de ingredientes
        self.label_ing = tk.Label(
            self,
            text="Ingredientes",
            font=("Arial", 14, "bold"),
            bg=bg,
            fg=fg
        )
        self.label_ing.pack(pady=10)

        # tabla de ingredientes
        #creamos un contenedor para la tabla de ingredientes
        frame_ing_tabla = tk.Frame(self, bg=bg)
        frame_ing_tabla.pack(fill="x", padx=20, pady=5)

        scroll_ing = tk.Scrollbar(frame_ing_tabla)
        scroll_ing.pack(side="right", fill="y")

        #creamos la tabla de ingredientes
        self.tree_ing = ttk.Treeview(
            frame_ing_tabla,
            columns=("Producto", "Cantidad", "Unidad"),
            show="headings",
            height=6,
            yscrollcommand=scroll_ing.set
        )

        #definimos encabezados
        self.tree_ing.heading("Producto", text="Producto")
        self.tree_ing.heading("Cantidad", text="Cantidad")
        self.tree_ing.heading("Unidad", text="Unidad")

        self.tree_ing.pack(side="left", fill="both", expand=True)
        scroll_ing.config(command=self.tree_ing.yview)

        #detectamos clic derecho para menú contextual
        self.tree_ing.bind("<Button-3>", self.menu_ing_popup)

        # ===== FRAME BOTONES =====
        self.frame_ing = tk.Frame(self, bg=bg)
        self.frame_ing.pack(pady=5)

        tk.Button(self.frame_ing, text="➕ Añadir", command=self.anadir_ingrediente, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(self.frame_ing, text="✏️ Modificar", command=self.modificar_ingrediente,bg="#FF9800", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(self.frame_ing, text="🗑️Borrar", command=self.borrar_ingrediente,bg="#F44336", fg="white").grid(row=0, column=2, padx=5)


        # MENÚ CONTEXTUAL RECETAS
        #creamos un menú contextual para acciones rápidas sobre recetas
        self.menu_recetas = tk.Menu(self, tearoff=0)
        self.menu_recetas.add_command(label="➕ Nueva receta", command=self.crear_receta)
        self.menu_recetas.add_command(label="✏️ Modificar receta", command=self.modificar_receta)
        self.menu_recetas.add_command(label="🗑️Borrar receta", command=self.borrar_receta)
        self.menu_recetas.add_separator()
        self.menu_recetas.add_command(label="📝 Usar receta", command=self.usar_receta)

        # MENÚ CONTEXTUAL INGREDIENTES
        self.menu_ing = tk.Menu(self, tearoff=0)
        self.menu_ing.add_command(label="➕ Añadir", command=self.anadir_ingrediente)
        self.menu_ing.add_command(label="✏️ Modificar", command=self.modificar_ingrediente)
        self.menu_ing.add_command(label="🗑️Borrar", command=self.borrar_ingrediente)

    # POPUPS (ventanitas)
    def menu_recetas_popup(self, event):
        try:
            #detectamos sobre qué fila hemos hecho clic derecho
            row = self.tree.identify_row(event.y)
            if row:
                #seleccionamos esa fila
                self.tree.selection_set(row)
                #mostramos el menú contextual en la posición del cursor
                self.menu_recetas.post(event.x_root, event.y_root)
        except:
            #si ocurre algún error lo ignoramos para no romper la interfaz
            pass

    def menu_ing_popup(self, event):
        try:
            #detectamos la fila del ingrediente donde hemos hecho clic
            row = self.tree_ing.identify_row(event.y)
            if row:
                #seleccionamos esa fila
                self.tree_ing.selection_set(row)
                #mostramos el menú contextual
                self.menu_ing.post(event.x_root, event.y_root)
        except:
            pass

    # RECETAS
    def cargar(self):
        #limpiamos ambas tablas (recetas e ingredientes)
        self.tree.delete(*self.tree.get_children())
        self.tree_ing.delete(*self.tree_ing.get_children())

        #cargamos todas las recetas desde la base de datos
        for r in obtener_recetas():
            self.tree.insert("", "end", values=(r[0], r[1]))
        #si hay recetas, seleccionamos automáticamente la primera
        if self.tree.get_children():
            first = self.tree.get_children()[0]
            self.tree.selection_set(first)
            self.tree.focus(first)
            self.after(50, lambda: self.on_select_receta(None))#para que no se descuadre visualemnte

    def on_select_receta(self, event=None):
        #obtenemos la receta seleccionada
        sel = self.tree.selection()
        if not sel:
            return
        #extraemos el id de la receta
        rid = self.tree.item(sel[0])["values"][0]
        #cargamos sus ingredientes asociados
        self.cargar_ingredientes(rid)

    def cargar_ingredientes(self, receta_id):
        #limpiamos la tabla de ingredientes
        self.tree_ing.delete(*self.tree_ing.get_children())

        conn = conexion()
        cur = conn.cursor()

        #obtenemos los ingredientes de la receta junto con sus datos
        cur.execute("""
            SELECT p.nombre, ri.cantidad, ri.unidad, p.id
            FROM receta_ingredientes ri
            JOIN productos p ON ri.producto_id = p.id
            WHERE ri.receta_id=?
        """, (receta_id,))

        for f in cur.fetchall():
            #intentamos redondear la cantidad a 2 decimales
            try:
                cantidad_limpia = round(float(f[1]), 2)
            except:
                cantidad_limpia = f[1] #si no es un número, dejamos el valor original
            
            #insertamos los datos en la tabla
            self.tree_ing.insert("", "end", values=(f[0], cantidad_limpia, f[2]), tags=(f[3],))

        conn.close()


    # CRUD RECETAS
    def crear_receta(self):
        #creamos una ventana emergente para añadir una nueva receta
        win = tk.Toplevel(self)
        win.title("Nueva Receta")
        win.geometry("300x180")

        #configuramos colores según modo
        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"
        entry_bg = "#2E2E2E" if modo else "white"

        win.configure(bg=bg)

        #mostramos etiqueta de entrada
        tk.Label(win, text="Nombre de la receta:", bg=bg, fg=fg, font=("Arial", 10, "bold")).pack(pady=(20, 5))

        #creamos campo de texto
        e = tk.Entry(win, bg=entry_bg, fg=fg, insertbackground=fg, font=("Arial", 10))
        e.pack(pady=5, padx=20)
        e.focus_set() #colocamos el cursor directamente en el campo

        def guardar():
            #obtenemos el nombre introducido
            nombre = e.get().strip()
            if not nombre:
                messagebox.showwarning("Atención", "El nombre no puede estar vacío")
                return
            
            #insertamos la receta en la base de datos
            conn = conexion()
            cur = conn.cursor()
            cur.execute("INSERT INTO recetas (nombre) VALUES (?)", (nombre,))
            conn.commit()
            conn.close()
            win.destroy()
            self.cargar()
        
        #botón para guardar la receta
        tk.Button(win, text="Guardar", command=guardar, bg="#4CAF50", fg="white", bd=0, padx=15, pady=6, cursor="hand2").pack(pady=15)

    def modificar_receta(self):
        #obtenemos la receta seleccionada
        sel = self.tree.selection()
        if not sel:
            return

        rid, nombre_antiguo = self.tree.item(sel[0])["values"]

        #creamos ventana emergente
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
            #obtenemos el nuevo nombre
            nuevo_nombre = e.get().strip()
            if nuevo_nombre:
                #actualizamos en la base de datos
                conn = conexion()
                cur = conn.cursor()
                cur.execute("UPDATE recetas SET nombre=? WHERE id=?", (nuevo_nombre, rid))
                conn.commit()
                conn.close()
                #recalculamos necesidades por si afecta a productos
                recalcular_necesidad_producto(rid)
                win.destroy()
                self.cargar()

        #boton de actualizar
        tk.Button(win, text="Actualizar", command=guardar, bg="#FF9800", fg="white", bd=0, padx=15, pady=6, cursor="hand2").pack(pady=15)
        

    def borrar_receta(self):
        #obtenemos la receta seleccionada
        sel = self.tree.selection()
        if not sel:
            return
        #pedimos confirmación al usuario
        if not messagebox.askyesno("Confirmar", "¿Borrar esta receta?"):
            return

        rid = self.tree.item(sel[0])["values"][0]

        conn = None # Inicializamos para evitar errores en el finally
        try:
            conn = conexion()
            cur = conn.cursor()
            
            #borramos primero los ingredientes asociados
            cur.execute("DELETE FROM receta_ingredientes WHERE receta_id=?", (rid,))
            #borramos la receta
            cur.execute("DELETE FROM recetas WHERE id=?", (rid,))
            
            conn.commit()
            print("Borrado exitoso.")

        except Exception as e:
            print(f"Error al borrar: {e}")
            if conn:
                conn.rollback() #si hay error, deshacemos los cambios
            messagebox.showerror("Error", f"No se pudo borrar: {e}")
        
        finally:
            if conn:
                conn.close()
                print("Conexión cerrada.")

        #limpiamos y recargamos datos
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

            #añadimos la receta al planificador
            cur.execute("""
                INSERT INTO recetas_pendientes (receta_id, fecha_planificada, completada)
                VALUES (?, date('now', 'localtime'), 0)
            """, (rid,))

            #obtenemos los productos que usa esta receta para recalcularlos
            cur.execute("SELECT producto_id FROM receta_ingredientes WHERE receta_id = ?", (rid,))
            productos_afectados = [p[0] for p in cur.fetchall()]

            if not productos_afectados:
                conn.commit()
                messagebox.showinfo("Planificador", f"✅ '{nombre_receta}' añadida (no tiene ingredientes).")
                conn.close()
                return

            items_necesarios_lista = []

            #recalculamos necesidades para cada producto
            for p_id in productos_afectados:
                #sumamos lo necesario de todas las recetas pendientes
                cur.execute("""
                    SELECT SUM(ri.cantidad) 
                    FROM receta_ingredientes ri
                    JOIN recetas_pendientes rp ON ri.receta_id = rp.receta_id
                    WHERE ri.producto_id = ? AND rp.completada = 0
                """, (p_id,))
                total_necesario_recetas = cur.fetchone()[0] or 0

                #obtenemos stock actual y mínimo
                cur.execute("SELECT nombre, cantidad, stock_minimo, unidad FROM productos WHERE id = ?", (p_id,))
                p_nombre, stock_act, stock_min, unidad = cur.fetchone()

                #calculamos cuánto necesitamos comprar realmente(Total Recetas + Mínimo) - Stock Actual
                cantidad_final_compra = round(max(0, (total_necesario_recetas + stock_min) - stock_act), 2)

                #actualizamos la lista de la compra
                cur.execute("DELETE FROM lista_compras WHERE producto_id = ? AND comprado = 0", (p_id,))
                
                if cantidad_final_compra > 0:
                    cur.execute("""
                        INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado)
                        VALUES (?, ?, ?, 0)
                    """, (p_id, cantidad_final_compra, unidad))
                    items_necesarios_lista.append(f"- {p_nombre}: {cantidad_final_compra} {unidad}")

            conn.commit()
            conn.close()

            mensaje = f"✅ '{nombre_receta}' añadida a pendientes."
            if items_necesarios_lista:
                mensaje += "\n\n📋 Lista de compras actualizada (Total acumulado):\n" + "\n".join(items_necesarios_lista)
            else:
                mensaje += "\n\n✨ Tienes stock suficiente para todo el plan actual."
                
            messagebox.showinfo("Planificador", mensaje)

        except Exception as e:
            #si hay error, deshacemos cambios y avisamos
            if 'conn' in locals() and conn:
                conn.rollback()
                conn.close()
            messagebox.showerror("Error", f"Fallo crítico al añadir: {e}")


    # INGREDIENTES

    def anadir_ingrediente(self):
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Atención", "Selecciona primero una receta a la que añadir ingredientes.")
                return

            rid = self.tree.item(sel[0])["values"][0]

            #creamos una ventana emergente para añadir el ingrediente
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
            #obtenemos todos los productos disponibles desde la base de datos
            conn = conexion()
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, unidad FROM productos ORDER BY nombre ASC")
            productos = cur.fetchall()
            conn.close()

            #creamos un diccionario para mapear texto visible con id y unidad
            opciones = {
                f"{nombre} ({unidad})": (pid, unidad)
                for pid, nombre, unidad in productos
            }

            # interfaz
            tk.Label(win, text="Seleccionar Producto", bg=bg, fg=fg, font=("Arial", 10, "bold")).pack(pady=(15, 0))
            
            #creamos un desplegable con los productos
            combo = ttk.Combobox(
                win,
                values=list(opciones.keys()),
                state="readonly",
                width=30
            )
            combo.pack(pady=10)

            tk.Label(win, text="Cantidad", bg=bg, fg=fg, font=("Arial", 10, "bold")).pack(pady=(10, 0))
            
            #campo para introducir la cantidad
            c = tk.Entry(
                win,
                bg=entry_bg,
                fg=fg,
                insertbackground=fg,
                font=("Arial", 10)
            )
            c.pack(pady=5)

            def guardar():
                #validamos que se ha seleccionado un producto
                seleccion = combo.get()
                if not seleccion:
                    messagebox.showwarning("Faltan datos", "Por favor, selecciona un producto.")
                    return

                #validamos que se ha introducido cantidad
                cantidad = c.get().strip()
                if not cantidad:
                    messagebox.showwarning("Faltan datos", "Introduce una cantidad.")
                    return

                producto_id, unidad = opciones[seleccion]

                conn = conexion()
                cur = conn.cursor()

                #evitamos duplicar ingredientes dentro de la misma receta
                cur.execute("""
                    SELECT 1 FROM receta_ingredientes
                    WHERE receta_id=? AND producto_id=?
                """, (rid, producto_id))

                if cur.fetchone():
                    messagebox.showerror("Error", "Ese ingrediente ya existe en esta receta.")
                    conn.close()
                    return

                try:
                    #insertamos el nuevo ingrediente en la base de datos
                    cur.execute("""
                        INSERT INTO receta_ingredientes
                        (receta_id, producto_id, cantidad, unidad)
                        VALUES (?,?,?,?)
                    """, (rid, producto_id, cantidad, unidad))

                    conn.commit()
                    conn.close()

                    #recalculamos necesidades por si afecta a la lista de la compra
                    recalcular_necesidad_producto(producto_id)
                    win.destroy()
                    self.cargar_ingredientes(rid) # Refrescamos la tabla de abajo
                    
                except Exception as e:
                    messagebox.showerror("Error de BD", f"No se pudo guardar: {e}")

            #botón para confirmar la acción
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
        #comprobamos que hay una receta y un ingrediente seleccionados
        sel_r = self.tree.selection()
        sel_i = self.tree_ing.selection()

        if not sel_r or not sel_i:
            messagebox.showwarning("Atención", "Selecciona una receta y un ingrediente")
            return

        #obtenemos datos actuales
        rid = self.tree.item(sel_r[0])["values"][0]
        item = self.tree_ing.item(sel_i[0])
        
        valores = item["values"]
        nombre_prod = valores[0]
        cant_actual = valores[1]
        unid_actual = valores[2]
        
        # IMPORTANTE recuperamos el id del producto desde los tags
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

        #campo para modificar cantidad
        tk.Label(win, text="Nueva Cantidad:", bg=bg, fg=fg).pack(pady=(5, 0))
        e1 = tk.Entry(win, bg=entry_bg, fg=fg, insertbackground=fg)
        e1.insert(0, cant_actual)
        e1.pack(pady=5, padx=20)

        #campo de unidad (solo lectura)
        tk.Label(win, text="Nueva Unidad:", bg=bg, fg=fg).pack(pady=(5, 0))
        e2 = tk.Entry(win, bg=entry_bg, fg=fg, insertbackground=fg)
        e2.insert(0, unid_actual)
        e2.config(state='readonly')
        e2.pack(pady=5, padx=20)

        def guardar():
            try:
                nueva_cant = e1.get().strip()
                nueva_unid = e2.get().strip()
                
                if not nueva_cant:
                    messagebox.showwarning("Error", "La cantidad no puede estar vacía.")
                    return

                #actualizamos en la base de datos
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

        # Obtenemos el nombre del ingrediente para el mensaje (está en la columna 0 de la tabla de ingredientes)
        nombre_ing = self.tree_ing.item(sel_i[0])["values"][0]

        #pedimos confirmación al usuario
        from tkinter import messagebox
        if not messagebox.askyesno("Confirmar borrado", f"¿Estás seguro de que deseas eliminar '{nombre_ing}' de esta receta?"):
            return 

        rid = self.tree.item(sel_r[0])["values"][0]
        pid = self.tree_ing.item(sel_i[0])["tags"][0]

        #borramos el ingrediente de la base de datos
        conn = conexion()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM receta_ingredientes
            WHERE receta_id=? AND producto_id=?
        """, (rid, pid))
        conn.commit()
        conn.close()
        recalcular_necesidad_producto(pid)
        #actualizamos tabla
        self.cargar_ingredientes(rid)


    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Seguro que quieres salir?"):
            #limpiamos datos del usuario
            self.controller.usuario_email = None
            
            #cerramos la app
            self.controller.destroy()
            
            #relanzamos el login
            import tkinter as tk
            from login import LoginApp
            
            root_login = tk.Tk()
            LoginApp(root_login)
            root_login.mainloop()



    # NAV

    def ir_a_home(self):
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def alternar_modo(self):
        #avisamos al controlador para cambiar el modo
        self.controller.toggle_modo_oscuro()
        
        #reconstruimos la interfaz con el nuevo tema
        self.setup_ui()
        
        #recargamos los datos para evitar que la tabla quede vacía
        self.cargar()

    def aplicar_tema(self):
        self.tree.configure(style="Treeview")
        self.tree_ing.configure(style="Treeview")

        #forzamos actualización visual
        self.update()
        self.update_idletasks()

        self.tree.update()
        self.tree_ing.update()


    
