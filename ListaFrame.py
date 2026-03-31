import tkinter as tk
from tkinter import ttk, messagebox

# Importamos las funciones de tu lógica
from lista_compras import ver_tareas_todas, marcar_comprado

class ListaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.config(height=600)
        self.pack_propagate(False)

        self.setup_ui()

    def setup_ui(self):
        # 🧹 Limpiamos el frame para que al alternar modo no se dupliquen widgets
        for widget in self.winfo_children():
            widget.destroy()

        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"
        
        # Color verde para coherencia
        verde_fuerte = "#4CAF50" if modo else "#1B5E20"
        verde_claro = "#333333" if modo else "#A5D6A7"

        self.configure(bg=bg)

        # 🌙 BOTÓN TOGGLE (Igual que en RecetasFrame)
        self.toggle_btn = tk.Button(
            self,
            text="☀️" if modo else "🌙",
            command=self.alternar_modo,
            font=("Segoe UI Emoji", 14),
            bd=0,
            bg=bg,
            fg=fg,
            activebackground=bg,
            cursor="hand2"
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # --- TÍTULO ---
        self.label_titulo = tk.Label(
            self, 
            text="🛒 LISTA DE COMPRA", 
            font=("Arial", 18, "bold"), 
            bg=bg, 
            fg=verde_fuerte, 
            pady=15
        )
        self.label_titulo.pack()

        # --- BOTÓN VOLVER ---
        self.btn_volver = tk.Button(
            self, 
            text="⬅ Volver al Inicio", 
            command=self.ir_a_home,
            font=("Arial", 10, "bold"),
            bg=verde_claro,
            fg="white" if modo else "black",
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2"
        )
        self.btn_volver.pack(pady=5)

        # --- TABLA ---
        frame_tabla = tk.Frame(self, bg=bg)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("ID", "Producto", "Cantidad", "Unidad")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)

        for col in columnas:
            self.tree.heading(col, text=col)
            ancho = 60 if col == "ID" else 150
            self.tree.column(col, anchor="center", width=ancho)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # --- BOTONES DE ACCIÓN ---
        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(pady=20)

        # Cargar
        tk.Button(
            btn_frame, 
            text="🔄 Actualizar", 
            command=self.cargar, 
            bg="#757575", 
            fg="white", 
            width=15, 
            bd=0, 
            pady=8, 
            cursor="hand2"
        ).grid(row=0, column=0, padx=10)

        # Comprado
        tk.Button(
            btn_frame, 
            text="✅ Comprado", 
            command=self.marcar, 
            bg="#4CAF50", 
            fg="white", 
            font=("Arial", 10, "bold"),
            width=15, 
            bd=0, 
            pady=8, 
            cursor="hand2"
        ).grid(row=0, column=1, padx=10)

        # Cargamos los datos al construir la interfaz
        self.cargar()

    def alternar_modo(self):
        """Cambia el modo en el controlador y refresca esta pantalla"""
        self.controller.toggle_modo_oscuro()
        self.setup_ui()

    def ir_a_home(self):
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def cargar(self):
        self.tree.delete(*self.tree.get_children())
        try:
            datos = ver_tareas_todas() 
            for fila in datos:
                self.tree.insert("", "end", values=fila)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la lista: {e}")

    def marcar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto.")
            return

        item = self.tree.item(seleccion[0])
        valores = item["values"]
        item_id = valores[0]
        nombre_prod = valores[1]

        try:
            marcar_comprado(item_id) 
            # ✅ Mantenemos el mensaje de confirmación que querías
            messagebox.showinfo("Actualizado", f"'{nombre_prod}' se ha marcado como comprado.")
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo marcar: {e}")