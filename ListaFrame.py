import tkinter as tk
from tkinter import ttk, messagebox

# Importamos las funciones de tu lógica
from lista_compras import ver_tareas_todas, marcar_comprado


from mandar_email import enviar_lista_email

class ListaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.config(height=600)
        self.pack_propagate(False)

        self.setup_ui()

    def setup_ui(self):
        # 🧹 Limpiamos el frame
        for widget in self.winfo_children():
            widget.destroy()

        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"
        verde_fuerte = "#4CAF50" if modo else "#1B5E20"

        self.configure(bg=bg)

        # 2. Botón de Modo Oscuro
        self.toggle_btn = tk.Button(
            self, text="☀️" if modo else "🌙",
            command=self.alternar_modo,
            font=("Segoe UI Emoji", 14), bd=0, cursor="hand2",
            bg=bg, fg=fg, activebackground=bg,
            highlightthickness=0
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

    # 🚪 BOTÓN CERRAR SESIÓN (Justo debajo del modo oscuro)
        self.logout_btn = tk.Button(
            self, text="🚪",
            command=self.cerrar_sesion,
            font=("Segoe UI Emoji", 14), bd=0, bg=bg, fg="#f44336", 
            activebackground=bg, cursor="hand2"
        )
        # Usamos rely=0.07 para que quede justo debajo del anterior
        self.logout_btn.place(relx=0.98, rely=0.07, anchor="ne")

        # --- TÍTULO ---
        # --- CONTENEDOR DEL TÍTULO (Frame para alinear icono y texto) ---
        header_lista = tk.Frame(self, bg=bg)
        header_lista.pack(pady=(15, 5))

        # 1. El Icono del Carrito (Color Gris Metálico / Azulado)
        tk.Label(
            header_lista, 
            text="🛒",
            font=("Segoe UI Emoji", 22), 
            bg=bg, 
            fg="#455A64"  # Un gris azulado para el metal del carrito
        ).pack(side="left", padx=5)

        # 2. El Texto del Título (Verde Fuerte)
        tk.Label(
            header_lista, 
            text="LISTA DE COMPRA",
            font=("Arial", 18, "bold"),
            bg=bg, 
            fg=verde_fuerte
        ).pack(side="left")
        # --- BOTÓN VOLVER (SITUACIÓN IGUALADA) ---
        # volver
        self.btn_volver = tk.Button(
            self, text="⬅ Volver",
            bg="#444444" if modo else "#E0E0E0",
            fg="white" if modo else "black",
            command=self.ir_a_home
        ).pack(pady=5)

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

        # --- BOTONES DE ACCIÓN (Solo "Comprado") ---
        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame, 
            text="✅ Marcar como Comprado", 
            command=self.marcar, 
            bg="#4CAF50", 
            fg="white",
            bd=0
        ).pack() # Usamos pack para centrarlo al estar solo

        tk.Button(
            btn_frame,
            text="📧 Enviar lista por email",
            command=self.enviar_email,
            bg="#2196F3",
            fg="white",
            bd=0
        ).pack(pady=5)

    

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



    def cerrar_sesion(self):
            if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres salir?"):
                # 1. Borramos rastro del usuario en el controlador
                self.controller.usuario_email = None
                
                # 2. Cerramos la ventana actual de la App
                self.controller.destroy()
                
                # 3. Lanzamos de nuevo el LoginApp
                import tkinter as tk
                from login import LoginApp # Importamos la clase de tu archivo login.py
                
                root_login = tk.Tk()
                LoginApp(root_login)
                root_login.mainloop()



    def enviar_email(self):
        # 1. 🛡️ ACTIVAMOS MODO ESPERA
        self.config(cursor="watch") 
        self.update_idletasks()

        
        productos = []
        for item in self.tree.get_children():
            valores = self.tree.item(item)["values"]

            # Comprobación de seguridad para el índice
            if len(valores) > 4 and valores[4] == "comprado":
                continue

            # Formateamos bonito el string para el email
            productos.append(f"🛒 {valores[1]} - Cantidad: {valores[2]} {valores[3]}")

        if not productos:
            messagebox.showwarning("Vacío", "No hay productos pendientes para enviar.")
            return

        # Recuperar credenciales del controlador
        destinatario = getattr(self.controller, 'usuario_email', None)
        email_user = getattr(self.controller, 'email_user', None)
        email_pass = getattr(self.controller, 'email_pass', None)

        if not destinatario or not email_user or not email_pass:
            messagebox.showerror("Configuración", "Faltan las credenciales de email en el sistema.")
            return

        try:
            # Llamada a la función externa que creamos antes
            from mandar_email import enviar_lista_email # Asegúrate de importar la función
            
            ok = enviar_lista_email(
                destinatario,
                productos,
                email_user,
                email_pass
            )

            if ok:
                messagebox.showinfo("Éxito", f"Lista enviada a:\n{destinatario} ✉️")
            else:
                messagebox.showerror("Error", "El servidor SMTP rechazó la conexión.\nRevisa tu Contraseña de Aplicación.")

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Ocurrió un error inesperado:\n{e}")