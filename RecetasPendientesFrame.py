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
        # Limpiar widgets previos (necesario para el cambio de modo oscuro)
        for widget in self.winfo_children():
            widget.destroy()

        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"
        verde_fuerte = "#4CAF50" if modo else "#1B5E20"
        verde_claro = "#333333" if modo else "#A5D6A7"

        self.configure(bg=bg)

        # 🌙 Botón Modo Oscuro
        self.toggle_btn = tk.Button(
            self, text="☀️" if modo else "🌙",
            command=self.alternar_modo,
            font=("Segoe UI Emoji", 14), bd=0, bg=bg, fg=fg, cursor="hand2"
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # --- TÍTULO ---
        tk.Label(
            self, text="📅 RECETAS PLANIFICADAS", 
            font=("Arial", 18, "bold"), bg=bg, fg=verde_fuerte, pady=15
        ).pack()

        # --- BOTÓN VOLVER ---
        tk.Button(
            self, text="⬅ Volver al Inicio", 
            command=self.ir_a_home,
            font=("Arial", 10, "bold"), bg=verde_claro, fg="white" if modo else "black",
            bd=0, padx=15, pady=6, cursor="hand2"
        ).pack(pady=5)

        # --- TABLA DE PENDIENTES ---
        frame_tabla = tk.Frame(self, bg=bg)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        # Añadimos una columna oculta "RID" para guardar el ID de la receta original
        columnas = ("ID", "Receta", "Fecha", "Estado", "RID")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)

        for col in columnas:
            self.tree.heading(col, text=col)
            if col == "Receta": ancho = 150
            elif col == "RID": ancho = 0 # Ocultamos la columna técnica
            else: ancho = 80
            self.tree.column(col, anchor="center", width=ancho)
        
        # Si la columna es RID, la ocultamos de la vista
        self.tree.column("RID", width=0, stretch=tk.NO)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # --- BOTONES DE ACCIÓN ---
        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="✅ Marcar Cocinada", command=self.marcar_completada, 
                  bg="#4CAF50", fg="white", width=18, bd=0, pady=8, cursor="hand2").grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="🗑️ Quitar del Plan", command=self.eliminar_pendiente, 
                  bg="#F44336", fg="white", width=18, bd=0, pady=8, cursor="hand2").grid(row=0, column=1, padx=10)

        self.cargar()

    def alternar_modo(self):
        self.controller.toggle_modo_oscuro()
        self.setup_ui()

    def ir_a_home(self):
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def cargar(self):
        self.tree.delete(*self.tree.get_children())
        conn = conexion()
        cur = conn.cursor()
        # Traemos también rp.receta_id para saber qué ingredientes descontar luego
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

    def marcar_completada(self):
        seleccion = self.tree.selection()
        if not seleccion: 
            messagebox.showwarning("Atención", "Selecciona una receta para marcar como cocinada.")
            return
        
        valores = self.tree.item(seleccion[0])["values"]
        item_id = valores[0]    # ID del plan (recetas_pendientes)
        nombre_receta = valores[1]
        receta_id = valores[4]  # ID real de la receta (en la tabla recetas)
        
        if messagebox.askyesno("Confirmar", f"¿Has cocinado '{nombre_receta}'?\nSe descontarán los ingredientes del stock."):
            conn = conexion()
            cur = conn.cursor()
            try:
                # 1. Buscar ingredientes y cantidades de esa receta
                cur.execute("SELECT producto_id, cantidad FROM receta_ingredientes WHERE receta_id = ?", (receta_id,))
                ingredientes = cur.fetchall()

                # 2. Restar del stock en la tabla 'productos'
                for p_id, cant in ingredientes:
                    cur.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?", (cant, p_id))

                # 3. Marcar como completada en el planificador
                cur.execute("UPDATE recetas_pendientes SET completada = 1 WHERE id = ?", (item_id,))
                
                conn.commit()
                messagebox.showinfo("¡Hecho!", f"Stock actualizado. '{nombre_receta}' marcada como cocinada.")
                self.cargar()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"No se pudo actualizar el stock: {e}")
            finally:
                conn.close()

    def eliminar_pendiente(self):
        seleccion = self.tree.selection()
        if not seleccion: return
        item_id = self.tree.item(seleccion[0])["values"][0]
        
        if messagebox.askyesno("Confirmar", "¿Quitar esta receta del planificador?"):
            conn = conexion()
            cur = conn.cursor()
            cur.execute("DELETE FROM recetas_pendientes WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            self.cargar()