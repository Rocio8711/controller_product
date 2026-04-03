import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os # Añadido para manejar rutas de archivos

# =========================
# 🏠 HOME
# =========================
class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.modo=None
        # Guardaremos una referencia al logo para que el Garbage Collector no la borre
        self.logo_img = None
        
        # Dibujamos la interfaz por primera vez
        self._setup_ui()

    def _setup_ui(self):
        """Configura y dibuja todos los widgets de la interfaz"""
        self.modo = self.controller.modo_oscuro
        
        
        # Definición de colores según el modo
        bg_color = "#000000" if self.modo else "#ffffff"
        fg_color = "white" if self.modo else "black"
        btn_bg = "#388E3C" if self.modo else "#4CAF50"
        btn_active = "#66BB6A" if self.modo else "#45a049"

        # 1. Limpiar el frame antes de redibujar (importante para el toggle)
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(bg=bg_color)

        # 2. Botón de Toggle (Modo Oscuro/Claro)
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

        # 3. Contenedor principal centrado
        contenido = tk.Frame(self, bg=bg_color)
        contenido.place(relx=0.5, rely=0.5, anchor="center")

        # 4. Título
        tk.Label(
            contenido,
            text="CONTROLLER PRODUCT",
            font=("Segoe UI", 26, "bold"),
            fg="#2E7D32", 
            bg=bg_color
        ).grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # 5. Imagen de Logo
        self.logo_label = tk.Label(contenido, bg=bg_color)
        self.logo_label.grid(row=1, column=0, padx=40)
        self._load_logo()

        # 6. Botones de navegación
        frame_botones = tk.Frame(contenido, bg=bg_color)
        frame_botones.grid(row=1, column=1, padx=40)

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

        # Importaciones locales para evitar errores
        from InventarioFrame import InventarioFrame
        from RecetasFrame import RecetasFrame
        from ListaFrame import ListaFrame
        from RecetasPendientesFrame import RecetasPendientesFrame # 👈 ¡Añade esta línea!

        # --- LISTA DE BOTONES ---
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

        # 📅 ESTE ES EL BOTÓN DEL PLANIFICADOR
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
        
    def _load_logo(self):
        """Carga la imagen del logo usando ruta robusta"""
        try:
            # Intentamos usar ruta relativa primero por si mueves la carpeta
            img_name = "logo_oscuro.jpeg" if self.modo else "logo.jpeg"
            path = os.path.join(os.path.dirname(__file__), img_name)
            
            # Si no existe en la carpeta relativa, usamos la absoluta que tenías
            if not os.path.exists(path):
                path = r"C:\Users\sienr\Documents\Proyecto_ControllerProduct\logo.jpeg"

            image = Image.open(path)
            image = image.resize((180, 180))
            self.logo_img = ImageTk.PhotoImage(image)
            self.logo_label.config(image=self.logo_img)
        except Exception as e:
            print(f"Error cargando logo: {e}")
            self.logo_label.config(
                text="[Logo no encontrado]", 
                fg="red", 
                font=("Arial", 12)
            )

    def toggle_modo_oscuro(self):
        """Cambia el estado en el controlador y refresca la UI del Frame"""
        self.controller.toggle_modo_oscuro()
        self._setup_ui()