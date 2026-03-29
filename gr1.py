import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Módulos propios
from lista_compra import marcar_comprado, ver_tareas_todas
from recetas import generar_lista_desde_receta, obtener_recetas
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


# =========================
# 🏠 HOME
# =========================
class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Contenedores y widgets que se usarán
        self.contenido = tk.Frame(self)
        self.toggle_btn = None
        self.logo_label = None
        self.nav_buttons = {}

        self._setup_widgets()
        self._update_colors()

    def _setup_widgets(self):
        # Contenedor principal centrado
        self.contenido.place(relx=0.5, rely=0.5, anchor="center")

        # Título
        self.title_label = tk.Label(
            self.contenido,
            text="CONTROLLER PRODUCT",
            font=("Arial", 26, "bold"),
            fg="#2E7D32"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # Logo
        self.logo_label = tk.Label(self.contenido)
        self.logo_label.grid(row=1, column=0, padx=40)
        self._load_logo()

        # Botones de navegación
        frame_botones = tk.Frame(self.contenido)
        frame_botones.grid(row=1, column=1, padx=40)

        # Definir botones con texto y comando
        botones_info = {
            "Inventario": lambda: self.controller.show_frame(InventarioFrame),
            "Recetas": lambda: self.controller.show_frame(RecetasFrame),
            "Lista de compra": lambda: self.controller.show_frame(ListaFrame)
        }

        for name, cmd in botones_info.items():
            btn = tk.Button(frame_botones, text=name, command=cmd, font=("Arial", 14, "bold"), bd=0, cursor="hand2", width=20, pady=10)
            btn.pack(pady=10)
            self.nav_buttons[name] = btn

        # Botón toggle modo oscuro
        self.toggle_btn = tk.Button(
            self,
            text="☀️" if self.controller.modo_oscuro else "🌙",
            command=self.toggle_modo_oscuro,
            font=("Segoe UI Emoji", 14),
            bd=0,
            cursor="hand2"
        )
        self.toggle_btn.place(relx=0.95, rely=0.02, anchor="ne")

    def _load_logo(self):
        # Carga la imagen de logo con ruta relativa
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.jpeg")
            image = Image.open(logo_path)
            image = image.resize((180, 180))
            self.controller.logo_img = ImageTk.PhotoImage(image)
            self.logo_label.config(image=self.controller.logo_img, text="")
        except Exception:
            self.logo_label.config(text="[Logo no encontrado]", fg="red", font=("Arial", 12))

    def _update_colors(self):
        modo = self.controller.modo_oscuro
        bg = "#121212" if modo else "#F0F0F0"
        fg = "white" if modo else "black"
        btn_bg = "#4CAF50" if not modo else "#388E3C"
        btn_fg = "white"

        # Fondo del frame y contenido
        self.config(bg=bg)
        self.contenido.config(bg=bg)

        # Título
        self.title_label.config(fg="#2E7D32", bg=bg)

        # Toggle button
        self.toggle_btn.config(
            text="☀️" if modo else "🌙",
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg
        )

        # Botones de navegación
        for btn in self.nav_buttons.values():
            btn.config(
                bg=btn_bg,
                fg=btn_fg,
                activebackground="#45a049" if not modo else "#66BB6A",
                activeforeground=btn_fg
            )

        # Logo label
        self.logo_label.config(bg=bg)

    def toggle_modo_oscuro(self):
        self.controller.toggle_modo_oscuro()
        self._update_colors()

# =========================
# 📦 INVENTARIO
# =========================
class InventarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.columnas = ("ID", "Producto", "Cantidad", "Unidad", "Min")
        self._setup_ui()

    def _setup_ui(self):
        self.configure(bg="#121212")

        tk.Label(self, text="📦 INVENTARIO",
                 font=("Arial", 20, "bold"),
                 bg="#121212", fg="white").pack(pady=10)

        tk.Button(self, text="⬅ Volver",
                  command=lambda: self.controller.show_frame(HomeFrame)).pack()

        self.tree = ttk.Treeview(self, columns=self.columnas, show="headings")
        for col in self.columnas:
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(self, text="🔄 Cargar", command=self.cargar).pack(pady=5)

    def cargar(self):
        datos = ver_inventario()
        self.tree.delete(*self.tree.get_children())
        for fila in datos:
            self.tree.insert("", "end", values=fila)


# =========================
# 🍳 RECETAS
# =========================
class RecetasFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="RECETAS",
                 font=("Arial", 18, "bold")).pack(pady=10)

        tk.Button(self, text="⬅ Volver",
                  command=lambda: controller.show_frame(HomeFrame)).pack()

        self.listbox = tk.Listbox(self, width=50)
        self.listbox.pack(pady=10)

        tk.Button(self, text="🔄 Cargar", command=self.cargar).pack()
        tk.Button(self, text="📝 Usar", command=self.usar).pack()

    def cargar(self):
        self.listbox.delete(0, tk.END)
        for r in obtener_recetas():
            self.listbox.insert(tk.END, f"{r[0]} - {r[1]}")

    def usar(self):
        seleccion = self.listbox.get(tk.ACTIVE)
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una receta")
            return

        receta_id = int(seleccion.split(" - ")[0])
        generar_lista_desde_receta(receta_id)

        messagebox.showinfo("OK", "Ingredientes añadidos a la lista")


# =========================
# 🛒 LISTA COMPRA
# =========================
class ListaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        tk.Label(self, text="LISTA DE COMPRA",
                 font=("Arial", 18, "bold")).pack(pady=10)

        tk.Button(self, text="⬅ Volver",
                  command=lambda: controller.show_frame(HomeFrame)).pack()

        columnas = ("ID", "Producto", "Cantidad", "Unidad")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings")

        for col in columnas:
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True)

        tk.Button(self, text="🔄 Cargar", command=self.cargar).pack()
        tk.Button(self, text="✅ Comprado", command=self.marcar).pack()

    def cargar(self):
        datos = ver_tareas_todas()
        self.tree.delete(*self.tree.get_children())
        for fila in datos:
            self.tree.insert("", "end", values=fila)

    def marcar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        item = self.tree.item(seleccion)
        marcar_comprado(item["values"][0])
        self.cargar()


# =========================
# 🚀 EJECUCIÓN
# =========================
if __name__ == "__main__":
    app = App()
    app.mainloop()