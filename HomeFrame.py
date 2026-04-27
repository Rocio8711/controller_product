import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os 
from tkinter import ttk, messagebox

# Ventana Homeframe
class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.modo=None

        #guardamos una referencia al logo para que el sistema no lo borre de la memoria
        self.logo_img = None
        
        #dibujamos la interfaz por primera vez al iniciar la pantalla
        self._setup_ui()

    def _setup_ui(self):
        #configuramos y dibujamos todos los elementos visuales de la interfaz
        self.modo = self.controller.modo_oscuro
        
        
        #definimos los colores segun si tenemos activado el modo oscuro o el claro
        bg_color = "#000000" if self.modo else "#ffffff"
        fg_color = "white" if self.modo else "black"
        btn_bg = "#388E3C" if self.modo else "#4CAF50"
        btn_active = "#66BB6A" if self.modo else "#45a049"

        #limpiamos el panel antes de redibujar para que no se amontonen los elementos
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(bg=bg_color)

        #creamos el boton para cambiar entre el sol y la luna
        self.toggle_btn = tk.Button(
            self,
            text="☀️" if self.modo else "🌙",
            command=self.toggle_modo_oscuro,
            bg=bg_color,
            fg=fg_color,
            activebackground=bg_color,
            activeforeground=fg_color,
            font=("Segoe UI Emoji", 14),
            bd=0,
            cursor="hand2",
            highlightthickness=0
        )
        self.toggle_btn.place(relx=0.95, rely=0.02, anchor="ne")


        #añadimos el boton de cerrar sesion con el icono de la puerta
        self.logout_btn = tk.Button(
            self, text="🚪",
            command=self.cerrar_sesion,
            font=("Segoe UI Emoji", 14), bd=0, 
            bg=bg_color, fg="#f44336", # 👈 Cambiado bg por bg_color
            activebackground=bg_color, cursor="hand2"
        )
        self.logout_btn.place(relx=0.95, rely=0.08, anchor="ne") # 0.95 para que alinee con el toggle

        #creamos un contenedor principal para que todo quede centrado en pantalla
        contenido = tk.Frame(self, bg=bg_color)
        contenido.place(relx=0.5, rely=0.5, anchor="center")

        #montamos el encabezado con el icono y el nombre de la aplicacion
        header_home = tk.Frame(contenido, bg=bg_color)
        header_home.grid(row=0, column=0, columnspan=2, pady=(0, 30))

        #colocamos el icono de la caja marron al lado del titulo
        tk.Label(
            header_home, 
            text="📦",
            font=("Segoe UI Emoji", 30), # Un poco más grande para que destaque
            bg=bg_color, 
            fg="#8B4513"  # Marrón madera/cartón
        ).pack(side="left", padx=10)

        #ponemos el texto del titulo con nuestro color verde corporativo
        tk.Label(
            header_home, 
            text="CONTROLLER PRODUCT",
            font=("Segoe UI", 26, "bold"),
            bg=bg_color, 
            fg="#2E7D32"  #el verede que teniamos
        ).pack(side="left")

        #reservamos el espacio para mostrar el logo de nuestra aplicacion (se nos "machaca")
        self.logo_label = tk.Label(contenido, bg=bg_color)
        self.logo_label.grid(row=1, column=0, padx=40)
        self._load_logo()

        #creamos el panel donde meteremos todos los botones de navegacion
        frame_botones = tk.Frame(contenido, bg=bg_color)
        frame_botones.grid(row=1, column=1, padx=40)

        #definimos un estilo comun para que todos los botones se vean iguales
        boton_estilo = {
            "font": ("Arial", 14, "bold"),
            "bg": btn_bg,
            "fg": "white",
            "activebackground": btn_active,
            "activeforeground": "white",
            "width": 20,
            "bd": 0,
            "cursor": "hand2",
            "pady": 10
        }

        #importamos las otras pantallas aqui mismo para evitar que el programa se lie
        from InventarioFrame import InventarioFrame
        from RecetasFrame import RecetasFrame
        from ListaFrame import ListaFrame
        from RecetasPendientesFrame import RecetasPendientesFrame # 👈 ¡Añade esta línea!

        # LISTA DE BOTONES 
        #añadimos los botones para ir al inventario, recetas, planificador y lista
        tk.Button(
            frame_botones, text="📦 Inventario", 
            command=lambda: self.controller.show_frame(InventarioFrame), 
            **boton_estilo
        ).pack(pady=10)

        tk.Button(
            frame_botones, text="🍳 Recetas", 
            command=lambda: self.controller.show_frame(RecetasFrame), 
            **boton_estilo
        ).pack(pady=10)

        tk.Button(
            frame_botones, text="📅 Planificador", 
            command=lambda: self.controller.show_frame(RecetasPendientesFrame), 
            **boton_estilo
        ).pack(pady=10)

        tk.Button(
            frame_botones, text="🛒 Lista de compra", 
            command=lambda: self.controller.show_frame(ListaFrame), 
            **boton_estilo
        ).pack(pady=10)


    def cerrar_sesion(self):
            #mostramos un aviso para confirmar si de verdad queremos salir del programa
            if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres salir?"):
                #borramos los datos del usuario que estaban guardados en el controlador
                self.controller.usuario_email = None
                
                #destruimos la ventana principal de la aplicacion para cerrarla del todo
                self.controller.destroy()
                
                #traemos las librerias y la pantalla de acceso para volver a empezar
                import tkinter as tk
                from login import LoginApp
                
                #creamos una ventana nueva para el login y lanzamos su bucle principal
                root_login = tk.Tk()
                LoginApp(root_login)
                root_login.mainloop()


    def _load_logo(self):
        #intentamos cargar la imagen del logo buscando el archivo en el ordenador
        try:
            #elegimos el nombre del archivo dependiendo de si estamos en modo oscuro o claro
            img_name = ".\imagenes\logo_oscuro.jpeg" if self.modo else ".\imagenes\logo.jpeg"
            #montamos la ruta del archivo combinando la carpeta actual con el nombre de la imagen
            path = os.path.join(os.path.dirname(__file__), img_name)
            
           #si no encontramos la imagen en la carpeta del proyecto usamos una ruta fija
            if not os.path.exists(path):
                path = r"C:\Users\sienr\Documents\Proyecto_ControllerProduct\logo.jpeg"

            #abrimos la imagen y le cambiamos el tamaño para que encaje bien en el diseño
            image = Image.open(path)
            image = image.resize((180, 180))
            self.logo_img = ImageTk.PhotoImage(image)
            self.logo_label.config(image=self.logo_img)
        except Exception as e:
            #si hay algun fallo cargando la foto avisamos por consola y ponemos un texto de error
            print(f"Error cargando logo: {e}")
            self.logo_label.config(
                text="[Logo no encontrado]", 
                fg="red", 
                font=("Arial", 12)
            )

    def toggle_modo_oscuro(self):
        #le pedimos al controlador que cambie el tema y redibujamos toda la pantalla
        self.controller.toggle_modo_oscuro()
        self._setup_ui()