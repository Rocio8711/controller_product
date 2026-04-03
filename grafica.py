import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# 1. IMPORTA TUS VENTANAS (Asegúrate de que los nombres de archivo sean correctos)
from HomeFrame import HomeFrame
from InventarioFrame import InventarioFrame
from RecetasFrame import RecetasFrame
from ListaFrame import ListaFrame
from RecetasPendientesFrame import RecetasPendientesFrame

# 2. Imports de tus módulos de lógica
from lista_compras import marcar_comprado, ver_tareas_todas
from recetas import (
    generar_lista_desde_receta, 
    obtener_recetas, 
    preparar_receta
)
from inventario import ver_inventario
from acceso_base_datos import conexion

# =========================
# 🧠 APP PRINCIPAL
# =========================
class App(tk.Tk):
    def __init__(self):
        super().__init__()


        self.title("Controller Product")
        
        # 1. AQUÍ ACTIVAMOS EL CENTRADO (900x700 es tu tamaño)
        self.centrar_ventana(900, 700)

        self.modo_oscuro = False

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self._set_global_colors()
    

        container = tk.Frame(self, bg=self.bg_app)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomeFrame, InventarioFrame, RecetasFrame, ListaFrame, RecetasPendientesFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomeFrame)
        self.after(100, self._configurar_estilos_treeview)

    # 2. ESTA FUNCIÓN DEBE ESTAR ALINEADA CON EL DEF __INIT__
    def centrar_ventana(self, ancho, alto):
        """Calcula el centro de la pantalla y posiciona la ventana ahí"""
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()

        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)

        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _set_global_colors(self):
        self.bg_app = "#121212" if self.modo_oscuro else "#F0F0F0"
        self.fg_app = "white" if self.modo_oscuro else "black"

    def _configurar_estilos_treeview(self):
        """Configura el look de todas las tablas de la app"""
        bg_tree = "#1E1E1E" if self.modo_oscuro else "#ffffff"
        fg_tree = "white" if self.modo_oscuro else "black"
        
        self.style.configure("Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background="#2E7D32",
            foreground="white",
            padding=6,
            relief="flat"
        )
        self.style.map("Treeview.Heading", background=[("active", "#7CA27E")])

        self.style.configure("Treeview",
            background=bg_tree,
            foreground=fg_tree,
            rowheight=28,
            fieldbackground=bg_tree,
            font=("Segoe UI", 10)
        )
        self.style.map("Treeview",
            background=[("selected", "#83C285")],
            foreground=[("selected", "black")]
        )

    def toggle_modo_oscuro(self):
        self.modo_oscuro = not self.modo_oscuro
        self._set_global_colors()
        self._configurar_estilos_treeview()

        # Refrescar todos los frames
        for frame in self.frames.values():
            if hasattr(frame, "setup_ui"):
                for widget in frame.winfo_children():
                    widget.destroy()
                frame.setup_ui()
                
                # --- AQUÍ ESTÁ EL TRUCO ---
                # Si el frame tiene una función 'cargar', la llamamos 
                # inmediatamente después de reconstruir la interfaz
                if hasattr(frame, "cargar"):
                    frame.cargar()
                    
            elif hasattr(frame, "_setup_ui"):
                frame._setup_ui()

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()
        self.after(50, self._refresh_frame, frame)

    def _refresh_frame(self, frame):
        if hasattr(frame, "cargar"):
            frame.cargar()

# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    app = App()
    app.mainloop()