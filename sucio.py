import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from HomeFrame import HomeFrame
from InventarioFrame import InventarioFrame
from RecetasFrame import RecetasFrame
from ListaFrame import ListaFrame


# Imports de módulos personalizados
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

        self.title("SmartKitchen Inventory")
        self.geometry("800x600")

        self.modo_oscuro = True

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self._set_global_colors()

        container = tk.Frame(self, bg=self.bg_app)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomeFrame, InventarioFrame, RecetasFrame, ListaFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomeFrame)

    def _set_global_colors(self):
        self.bg_app = "#121212" if self.modo_oscuro else "#F0F0F0"
        self.fg_app = "white" if self.modo_oscuro else "black"

    def toggle_modo_oscuro(self):
        self.modo_oscuro = not self.modo_oscuro
        self._set_global_colors()

        for frame in self.frames.values():
            if hasattr(frame, "_setup_ui"):
                frame._setup_ui()

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()
        self.after(50, self._refresh_frame, frame)

    def _refresh_frame(self, frame):
        if hasattr(frame, "cargar"):
            frame.cargar()


        # 🔹 Cabeceras
        self.style.configure("Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background="#2E7D32",
            foreground="white",
            padding=6,
            relief="flat"
        )

        # Hover en cabecera
        self.style.map("Treeview.Heading",
            background=[("active", "#388E3C")]
        )

        # 🔹 Tabla
        self.style.configure("Treeview",
            background="#ffffff",
            foreground="black",
            rowheight=28,
            fieldbackground="#ffffff",
            font=("Segoe UI", 10)
        )

        # Selección
        self.style.map("Treeview",
            background=[("selected", "#A5D6A7")],
            foreground=[("selected", "black")]
        )
# =========================
# 🏠 HOME
# =========================


# =========================
# 📦 INVENTARIO
# =========================

# =========================
# 🍳 RECETAS
# =========================


# =========================
# 🛒 LISTA COMPRA
# =========================

# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    app = App()
    app.mainloop()