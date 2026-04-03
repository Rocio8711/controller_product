import tkinter as tk
from tkinter import ttk, messagebox
from acceso_base_datos import conexion

class RecetasPendientesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(height=600)
        self.pack_propagate(False)
        self.setup_ui()

    def setup_ui(self):
        # 1. Limpiar la pantalla para el refresco (Modo Oscuro/Claro)
        for widget in self.winfo_children():
            widget.destroy()

        # 2. Configuración de colores según el modo
        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"
        verde_fuerte = "#4CAF50" if modo else "#1B5E20"
        
        # Colores específicos para los estados de la tabla de ingredientes
        color_ok = "#90EE90" if modo else "#2E7D32"  # Verde pastel / Verde bosque
        color_error = "#FF6B6B" if modo else "red"    # Rojo suave / Rojo estándar
        
        self.configure(bg=bg)

        # ☀️/🌙 Botón de alternar modo (arriba a la derecha)
        self.toggle_btn = tk.Button(
            self, text="☀️" if modo else "🌙", 
            command=self.alternar_modo,
            font=("Segoe UI Emoji", 14), bd=0, bg=bg, fg=fg, cursor="hand2"
        )
        self.toggle_btn.place(relx=0.98, rely=0.01, anchor="ne")

        # --- TÍTULO PRINCIPAL ---
        tk.Label(
            self, text="📅 PLANIFICADOR DE COCINA", 
            font=("Arial", 18, "bold"), bg=bg, fg=verde_fuerte
        ).pack(pady=(10, 5)) # Reducimos un poco el pady inferior

        # --- BOTÓN VOLVER (SITUACIÓN SUPERIOR) ---

        self.btn_volver = tk.Button(
            self, text="⬅ Volver",
            bg="#444444" if modo else "#E0E0E0",
            fg="white" if modo else "black",
            command=self.ir_a_home
        ).pack(pady=5)

        # =====================================================
        # PANEL SUPERIOR: TABLA DE RECETAS PLANIFICADAS
        # =====================================================
        frame_superior = tk.LabelFrame(
            self, text=" Recetas Planificadas ", 
            bg=bg, fg=fg, font=("Arial", 10, "bold")
        )
        frame_superior.pack(fill="both", expand=True, padx=20, pady=5)

        columnas = ("ID", "Receta", "Fecha", "Estado", "RID")
        self.tree = ttk.Treeview(frame_superior, columns=columnas, show="headings", height=5)
        
        for col in columnas:
            self.tree.heading(col, text=col)
            # Ajustamos anchos: Receta más ancho, RID oculto
            ancho = 150 if col == "Receta" else 100
            self.tree.column(col, anchor="center", width=ancho)
        
        self.tree.column("RID", width=0, stretch=tk.NO) # Columna técnica oculta

        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar para la tabla superior
        scroll_sup = tk.Scrollbar(frame_superior, orient="vertical", command=self.tree.yview)
        scroll_sup.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll_sup.set)

        # Evento de selección: Carga los ingredientes abajo al hacer clic
        self.tree.bind("<<TreeviewSelect>>", self.on_receta_select)

        # =====================================================
        # PANEL INFERIOR: DETALLE DE INGREDIENTES Y STOCK
        # =====================================================
        frame_inferior = tk.LabelFrame(
            self, text=" Verificación de Ingredientes ", 
            bg=bg, fg=fg, font=("Arial", 10, "bold")
        )
        frame_inferior.pack(fill="both", expand=True, padx=20, pady=5)

        cols_ing = ("Producto", "Necesario", "En Stock", "Estado")
        self.tree_ing = ttk.Treeview(frame_inferior, columns=cols_ing, show="headings", height=6)
        
        for col in cols_ing:
            self.tree_ing.heading(col, text=col)
            self.tree_ing.column(col, anchor="center", width=110)

        # Configuración de colores de las filas (Tags)
        self.tree_ing.tag_configure("faltante", foreground=color_error)
        self.tree_ing.tag_configure("ok", foreground=color_ok)

        self.tree_ing.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar para la tabla inferior
        scroll_inf = tk.Scrollbar(frame_inferior, orient="vertical", command=self.tree_ing.yview)
        scroll_inf.pack(side="right", fill="y")
        self.tree_ing.configure(yscrollcommand=scroll_inf.set)

        # =====================================================
        # BOTONERA FINAL
        # =====================================================

        # =====================================================
        # BOTONERA FINAL (USANDO PACK PARA IGUALAR TAMAÑOS)
        # =====================================================
        # Creamos un frame para contener los dos botones alineados
        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(pady=10)

        # Botón Cocinar
        self.btn_cocinar = tk.Button(
            btn_frame, 
            text="Cocinar Ahora", # Quitamos el emoji para que no estire la altura
            command=self.ejecutar_cocinado, 
            bg="#333333", 
            fg="white", 
            state="disabled",
            width=15
        )
        self.btn_cocinar.pack(side="left", padx=10)
        # Usamos side="left" para que se pongan uno al lado del otro


        # Botón Eliminar
        tk.Button(
            btn_frame, 
            text="🗑️Quitar del Plan", 
            command=self.eliminar_pendiente, 
            bg="#F44336", 
            fg="white",
            width=15
        ).pack(side="left", padx=5)

        
        # Cargar los datos iniciales de la base de datos
        self.cargar()

    # --- LÓGICA ---

    def on_receta_select(self, event):
        """Se activa al hacer clic en una receta de la tabla superior"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        # Obtener el RID (ID de la receta) de la columna oculta
        receta_id = self.tree.item(seleccion[0])["values"][4]
        self.actualizar_detalle_ingredientes(receta_id)

    def actualizar_detalle_ingredientes(self, receta_id):
        self.tree_ing.delete(*self.tree_ing.get_children())
        
        conn = conexion()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.nombre, ri.cantidad, p.cantidad, p.unidad
            FROM receta_ingredientes ri
            JOIN productos p ON ri.producto_id = p.id
            WHERE ri.receta_id = ?
        """, (receta_id,))
        
        ingredientes = cur.fetchall()
        puedo_cocinar = True if ingredientes else False

        for nombre, nec, stock, uni in ingredientes:
            estado = "LISTO"
            tag = "ok"
            
            if stock < nec:
                estado = "FALTA"
                tag = "faltante"
                puedo_cocinar = False
            
            self.tree_ing.insert("", "end", values=(nombre, f"{nec} {uni}", f"{stock} {uni}", estado), tags=(tag,))
        
        conn.close()
        
        # Habilitar el botón solo si hay stock de TODO
        if puedo_cocinar:
            self.btn_cocinar.config(state="normal", bg="#4CAF50")
        else:
            self.btn_cocinar.config(state="disabled", bg="#333333")

    def ejecutar_cocinado(self):
        seleccion = self.tree.selection()
        if not seleccion: return

        valores = self.tree.item(seleccion[0])["values"]
        item_plan_id = valores[0]
        receta_id = valores[4]

        if messagebox.askyesno("Confirmar", "¿Confirmas que has cocinado esta receta?\nEl stock se descontará automáticamente."):
            conn = conexion()
            cur = conn.cursor()
            try:
                # 1. Obtener ingredientes
                cur.execute("SELECT producto_id, cantidad FROM receta_ingredientes WHERE receta_id=?", (receta_id,))
                ingredientes = cur.fetchall()

                # 2. Descontar stock
                for p_id, cant in ingredientes:
                    cur.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?", (cant, p_id))

                # 3. Marcar como completada
                cur.execute("UPDATE recetas_pendientes SET completada = 1 WHERE id = ?", (item_plan_id,))
                
                conn.commit()
                messagebox.showinfo("Éxito", "¡Buen provecho! Stock actualizado.")
                self.cargar() # Recargar todo
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Fallo al actualizar stock: {e}")
            finally:
                conn.close()

    def cargar(self):
        self.tree.delete(*self.tree.get_children())
        self.tree_ing.delete(*self.tree_ing.get_children())
        self.btn_cocinar.config(state="disabled")
        
        conn = conexion()
        cur = conn.cursor()
        cur.execute("""
            SELECT rp.id, r.nombre, rp.fecha_planificada, 
            CASE WHEN rp.completada = 1 THEN 'Cocinada' ELSE 'Pendiente' END,
            r.id
            FROM recetas_pendientes rp
            JOIN recetas r ON rp.receta_id = r.id
            WHERE rp.completada = 0
            ORDER BY rp.fecha_planificada ASC
        """)
        for fila in cur.fetchall():
            self.tree.insert("", "end", values=fila)
        conn.close()

    def alternar_modo(self):
        # 1. Intentar obtener la receta seleccionada antes de destruir los widgets
        seleccion = self.tree.selection()
        id_receta_previa = None
        if seleccion:
            id_receta_previa = self.tree.item(seleccion[0])["values"][4] # El RID

        # 2. Cambiar modo y reconstruir UI
        self.controller.toggle_modo_oscuro()
        self.setup_ui()

        # 3. Si había algo seleccionado, intentar restaurar la selección y los ingredientes
        if id_receta_previa:
            for item in self.tree.get_children():
                if self.tree.item(item)["values"][4] == id_receta_previa:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    self.actualizar_detalle_ingredientes(id_receta_previa)
                    break

    def ir_a_home(self):
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def eliminar_pendiente(self):
        seleccion = self.tree.selection()
        if not seleccion: return
        
        # 1. Obtener IDs
        item_plan_id = self.tree.item(seleccion[0])["values"][0]
        receta_id_a_borrar = self.tree.item(seleccion[0])["values"][4]

        if messagebox.askyesno("Confirmar", "¿Quitar del plan?\nSe recalculará la lista de compras."):
            conn = None
            try:
                conn = conexion()
                cur = conn.cursor()

                # A. Obtener productos que usa la receta que vamos a quitar
                cur.execute("SELECT producto_id FROM receta_ingredientes WHERE receta_id = ?", (receta_id_a_borrar,))
                productos_afectados = [p[0] for p in cur.fetchall()]

                # B. BORRAR LA RECETA PRIMERO
                cur.execute("DELETE FROM recetas_pendientes WHERE id = ?", (item_plan_id,))
                print(f"DEBUG: Receta {receta_id_a_borrar} eliminada del plan.")

                # C. RECALCULAR CADA PRODUCTO AFECTADO
                for p_id in productos_afectados:
                    # Sumar lo que piden las recetas que QUEDAN en el planificador
                    cur.execute("""
                        SELECT SUM(ri.cantidad) 
                        FROM receta_ingredientes ri
                        JOIN recetas_pendientes rp ON ri.receta_id = rp.receta_id
                        WHERE ri.producto_id = ? AND rp.completada = 0
                    """, (p_id,))
                    res_sum = cur.fetchone()[0]
                    total_recetas_restantes = res_sum if res_sum is not None else 0

                    # Obtener stock actual y mínimo
                    cur.execute("SELECT nombre, cantidad, stock_minimo, unidad FROM productos WHERE id = ?", (p_id,))
                    nombre_p, stock_actual, stock_min, unidad_p = cur.fetchone()

                    # CÁLCULO: (Lo que piden las recetas + El mínimo) - Lo que ya tengo
                    # Ejemplo Pollo: (5 de Receta B + 5 Mínimo) - 2 en Stock = 8 a comprar.
                    necesidad_total = total_recetas_restantes + stock_min
                    cantidad_comprar = round(max(0, necesidad_total - stock_actual), 2)
                    
                    print(f"DEBUG: Producto: {nombre_p} | Necesidad Total: {necesidad_total} | Stock: {stock_actual} | Comprar: {cantidad_comprar}")

                    # D. ACTUALIZAR LISTA DE COMPRAS
                    # Primero borramos cualquier rastro previo de este producto "no comprado"
                    cur.execute("DELETE FROM lista_compras WHERE producto_id = ? AND comprado = 0", (p_id,))
                    
                    # Si todavía falta algo por comprar, lo insertamos de nuevo
                    if cantidad_comprar > 0:
                        cur.execute("""
                            INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado)
                            VALUES (?, ?, ?, 0)
                        """, (p_id, cantidad_comprar, unidad_p))
                        print(f"DEBUG: Insertado en lista_compras: {nombre_p} x {cantidad_comprar}")

                conn.commit() # ¡FUNDAMENTAL!
                messagebox.showinfo("Éxito", "Lista de compras sincronizada.")
                self.cargar()

            except Exception as e:
                if conn: conn.rollback()
                print(f"ERROR CRÍTICO: {e}")
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
            finally:
                if conn: conn.close()