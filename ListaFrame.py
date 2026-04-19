import tkinter as tk
from tkinter import ttk, messagebox
from lista_compras import ver_lista_compra, marcar_comprado

from mandar_email import enviar_lista_email

'''VENTANA DE LISTA DE COMPRAS'''

class ListaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        #guardamos una referencia al controlador principal para poder acceder a configuraciones como el modo oscuro
        self.controller = controller

        self.config(height=600)
        #evitamos que el frame cambie de tamaño según sus widgets internos
        self.pack_propagate(False)
        #construimos la interfaz grafica
        self.setup_ui()

    def setup_ui(self):
        #eliminamos todos los widgets actuales para reconstruir la interfaz
        for widget in self.winfo_children():
            widget.destroy()

        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"
        verde_fuerte = "#4CAF50" if modo else "#1B5E20"

        self.configure(bg=bg)

        #colocamos el botón en la esquina superior derecha
        self.toggle_btn = tk.Button(
            self, text="☀️" if modo else "🌙",
            command=self.alternar_modo,
            font=("Segoe UI Emoji", 14), bd=0, cursor="hand2",
            bg=bg, fg=fg, activebackground=bg,
            highlightthickness=0
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

    #BOTÓN CERRAR SESIÓN 
        self.logout_btn = tk.Button(
            self, text="🚪",
            command=self.cerrar_sesion,
            font=("Segoe UI Emoji", 14), bd=0, bg=bg, fg="#f44336", 
            activebackground=bg, cursor="hand2"
        )
        # Usamos rely=0.07 para que quede justo debajo del anterior
        self.logout_btn.place(relx=0.98, rely=0.07, anchor="ne")

        # --- TÍTULO ---
        #creamos un contenedor para alinear correctamente el icono y el texto
        header_lista = tk.Frame(self, bg=bg)
        header_lista.pack(pady=(15, 5))

        #ponemos el icono del carrito
        tk.Label(
            header_lista, 
            text="🛒",
            font=("Segoe UI Emoji", 22), 
            bg=bg, 
            fg="#455A64"  # Un gris azulado para el metal del carrito
        ).pack(side="left", padx=5)

        #mostramos el título principal de la pantalla
        tk.Label(
            header_lista, 
            text="LISTA DE COMPRA",
            font=("Arial", 18, "bold"),
            bg=bg, 
            fg=verde_fuerte
        ).pack(side="left")

        # --- BOTÓN VOLVER (SITUACIÓN IGUALADA) ---
        #creamos un botón que nos permite volver a la pantalla principal
        self.btn_volver = tk.Button(
            self, text="⬅ Volver",
            bg="#444444" if modo else "#E0E0E0",
            fg="white" if modo else "black",
            command=self.ir_a_home
        ).pack(pady=5)

        # --- TABLA de PRODUCTOS ---
        #creamos un contenedor para la tabla y su barra de desplazamiento
        frame_tabla = tk.Frame(self, bg=bg)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        #definimos las columnas que tendra la tabla
        columnas = ("ID", "Producto", "Cantidad", "Unidad")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)

        #configuramos los encabezados y tamaños de cada columna
        for col in columnas:
            self.tree.heading(col, text=col)
            ancho = 60 if col == "ID" else 150
            self.tree.column(col, anchor="center", width=ancho)

        #mostramos la tabla ocupando el espacio disponible
        self.tree.pack(side="left", fill="both", expand=True)

        #añadimos una barra de desplazamiento vertical para la tabla
        scrollbar = tk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # --- BOTONES DE ACCIÓN
        #creamos un contenedor para agrupar los botones inferiores
        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(pady=20)

        # Botón Marcar como Comprado
        tk.Button(
            btn_frame, 
            text="✅ Marcar como Comprado", 
            command=self.marcar, 
            bg="#4CAF50", 
            fg="white",
        ).pack(side="left", padx=10)     # side="left" los pone uno al lado del otro

        # Botón Enviar lista por email
        tk.Button(
            btn_frame,
            text="📧 Enviar lista por email",
            command=self.enviar_email,
            bg="#2196F3",
            fg="white",
        ).pack(side="left", padx=10)     # padx=10 crea la separación entre ellos

    

        # Cargamos los datos al construir la interfaz
        self.cargar()

    def alternar_modo(self):
    #cambiamos el modo (claro/oscuro) usando el controlador principal
        self.controller.toggle_modo_oscuro()
        #reconstruimos la interfaz para aplicar los nuevos colores
        self.setup_ui()

    def ir_a_home(self):
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def cargar(self):
        #limpiamos todos los elementos actuales de la tabla
        self.tree.delete(*self.tree.get_children())
        try:
            #obtenemos todos los datos de la lista de la compra desde la base de datos
            datos = ver_lista_compra()
            #recorremos los datos y los insertamos en la tabla
            for fila in datos:
                self.tree.insert("", "end", values=fila)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la lista: {e}")

    def marcar(self):
        #obtenemos el elemento seleccionado en la tabla
        seleccion = self.tree.selection()
        if not seleccion:
            #avisamos si no hemos seleccionado nada
            messagebox.showwarning("Atención", "Selecciona un producto.")
            return
        #recuperamos los datos del elemento seleccionado
        item = self.tree.item(seleccion[0])
        valores = item["values"]
        item_id = valores[0]
        nombre_prod = valores[1]

        try:
            marcar_comprado(item_id) 
            #mostramos un mensaje de confirmación al usuario
            messagebox.showinfo("Actualizado", f"'{nombre_prod}' se ha marcado como comprado.")
            #recargamos la tabla para reflejar el cambio
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo marcar: {e}")



    def cerrar_sesion(self):
            #preguntamos al usuario si está seguro de cerrar sesión
            if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres salir?"):
                #borramos rastro del usuario en el controlador
                self.controller.usuario_email = None
                
                #cerramos la ventana actual de la App
                self.controller.destroy()
                
                #lanzamos de nuevo el LoginApp
                import tkinter as tk
                from login import LoginApp 
                
                root_login = tk.Tk()
                LoginApp(root_login)
                root_login.mainloop()



    def enviar_email(self):
        # ACTIVAMOS MODO ESPERA
        #cambiamos el cursor a modo carga para indicar que estamos procesando
        self.config(cursor="watch") 
        self.update_idletasks()

        #creamos una lista donde guardaremos los productos a enviar
        productos = []
        for item in self.tree.get_children():
            valores = self.tree.item(item)["values"]

            #comprobamos que el producto no esté ya marcado como comprado
            if len(valores) > 4 and valores[4] == "comprado":
                continue

            #formateamos el texto del producto para el email
            productos.append(f"🛒 {valores[1]} - Cantidad: {valores[2]} {valores[3]}")
        #si no hay productos pendientes mostramos aviso
        if not productos:
            messagebox.showwarning("Vacío", "No hay productos pendientes para enviar.")
            return

        #recuperamos las credenciales desde el controlador
        destinatario = getattr(self.controller, 'usuario_email', None)
        email_user = getattr(self.controller, 'email_user', None)
        email_pass = getattr(self.controller, 'email_pass', None)

        #comprobamos que tenemos todos los datos necesarios
        if not destinatario or not email_user or not email_pass:
            messagebox.showerror("Configuración", "Faltan las credenciales de email en el sistema.")
            return

        try:
            from mandar_email import enviar_lista_email
            
            #llamamos a la función para enviar la lista
            ok = enviar_lista_email(
                destinatario,
                productos,
                email_user,
                email_pass
            )
            #ponemos mensajito al usuario
            if ok:
                messagebox.showinfo("Éxito", f"Lista enviada a:\n{destinatario} ✉️")
            else:
                messagebox.showerror("Error", "El servidor SMTP rechazó la conexión.\nRevisa tu Contraseña de Aplicación.")

        except Exception as e:
            #capturamos cualquier error inesperado
            messagebox.showerror("Error Crítico", f"Ocurrió un error inesperado:\n{e}")

        finally:
            #restblecemos el cursor
            self.config(cursor="")