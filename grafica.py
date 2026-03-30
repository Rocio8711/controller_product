import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Imports de tus módulos personalizados
from lista_compra import marcar_comprado, ver_tareas_todas
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
# 🏠 HOME
# =========================
class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Guardaremos una referencia al logo para que el Garbage Collector no la borre
        self.logo_img = None
        
        # Dibujamos la interfaz por primera vez
        self._setup_ui()

    def _setup_ui(self):
        """Configura y dibuja todos los widgets de la interfaz"""
        modo = self.controller.modo_oscuro
        
        # Definición de colores según el modo
        bg_color = "#121212" if modo else "#F0F0F0"
        fg_color = "white" if modo else "black"
        btn_bg = "#388E3C" if modo else "#4CAF50"
        btn_active = "#66BB6A" if modo else "#45a049"

        # 1. Limpiar el frame antes de redibujar (para el toggle)
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(bg=bg_color)

        # 2. Botón de Toggle (Modo Oscuro/Claro)
        # Usamos un color de fondo que contraste o el mismo del sistema
        self.toggle_btn = tk.Button(
            self,
            text="☀️" if modo else "🌙",
            command=self.toggle_modo_oscuro,
            bg=bg_color,
            fg=fg_color,
            activebackground=bg_color,
            activeforeground=fg_color,
            font=("Segoe UI Emoji", 14),
            bd=0,
            cursor="hand2"
        )
        self.toggle_btn.place(relx=0.95, rely=0.02, anchor="ne")

        # 3. Contenedor principal centrado
        contenido = tk.Frame(self, bg=bg_color)
        contenido.place(relx=0.5, rely=0.5, anchor="center")

        # 4. Título
        tk.Label(
            contenido,
            text="CONTROLLER PRODUCT",
            font=("Arial", 26, "bold"),
            fg="#2E7D32", # Mantenemos el verde corporativo
            bg=bg_color
        ) .grid(row=0, column=0, columnspan=2, pady=(0, 30))

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

        # Creamos los botones con sus comandos
        tk.Button(
            frame_botones, 
            text="📦 Inventario", 
            command=lambda: self.controller.show_frame(InventarioFrame), 
            **boton_estilo
        ).pack(pady=10)

        tk.Button(
            frame_botones, 
            text="🍳 Recetas", 
            command=lambda: self.controller.show_frame(RecetasFrame), 
            **boton_estilo
        ).pack(pady=10)

        tk.Button(
            frame_botones, 
            text="🛒 Lista de compra", 
            command=lambda: self.controller.show_frame(ListaFrame), 
            **boton_estilo
        ).pack(pady=10)

    def _load_logo(self):
        """Carga la imagen del logo"""
        try:
            # Ruta absoluta que proporcionaste
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


# =========================
# 📦 INVENTARIO
# =========================
# =========================
# 📦 INVENTARIO
# =========================
class InventarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Creamos la interfaz
        self.setup_ui()
        # Aplicamos colores
        self.actualizar_colores()

    def setup_ui(self):

        modo = self.controller.modo_oscuro

        # 🌙 --- BOTÓN MODO OSCURO (CORREGIDO) ---
        # Definimos primero el color para que nazca bien
        bg_init = "#121212" if modo else "#E8F5E9"
        fg_init = "white" if modo else "black"

        # Lo guardamos como self.toggle_btn para poder configuarlo luego
        self.toggle_btn = tk.Button(
            self,
            text="☀️" if modo else "🌙",
            command=self.alternar_modo, # Necesitamos esta función (ver abajo)
            font=("Segoe UI Emoji", 14),
            bd=0, # Sin borde de relieve
            highlightthickness=0, # <--- ¡ESTA ES LA LÍNEA CLAVE! (Quita el recuadro blanco)
            cursor="hand2",
            bg=bg_init,
            fg=fg_init,
            activebackground=bg_init, # Color al hacer clic
            activeforeground=fg_init
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # 🔹 Título
        self.label_titulo = tk.Label(
            self,
            text="📦 INVENTARIO DE PRODUCTOS",
            font=("Arial", 20, "bold")
        )

        # 🔹 Botón volver
        self.btn_volver = tk.Button(
            self,
            text="⬅ Volver al Inicio",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda: self.controller.show_frame(HomeFrame)
        )
        self.btn_volver.pack(pady=5)

        # ---------------------------------------------------------
        # 📂 CONTENEDOR DE TABLA + SCROLLBAR
        # ---------------------------------------------------------
        self.frame_tabla = tk.Frame(self, bg=bg_init)
        self.frame_tabla.pack(fill="both", expand=True, padx=20, pady=15)

        # Crear Scrollbar
        self.scrollbar = ttk.Scrollbar(self.frame_tabla, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        # Crear Tabla (Treeview) conectada al scroll
        columnas = ("ID", "Producto", "Cantidad", "Unidad", "Min")
        self.tree = ttk.Treeview(
            self.frame_tabla, 
            columns=columnas, 
            show="headings",
            yscrollcommand=self.scrollbar.set # Conecta la tabla al scroll
        )
        
        # Configurar el scroll para que mueva la tabla
        self.scrollbar.config(command=self.tree.yview)

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        self.tree.pack(side="left", fill="both", expand=True)
        

        # 🔹 Menú contextual
        self.menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 10, "bold"), bd=0)
        self.menu.add_command(label="➕   Añadir producto", command=self.abrir_agregar)
        self.menu.add_command(label="✏️   Editar producto", command=self.modificar_producto)
        self.menu.add_separator()
        self.menu.add_command(label="🗑️   Eliminar producto", command=self.eliminar_producto)

        self.tree.bind("<Button-3>", self.mostrar_menu)

        # 🔹 Frame de botones de acción
        self.frame_acciones = tk.Frame(self)
        self.frame_acciones.pack(pady=10)

        # Botones inferiores con sus comandos
        tk.Button(self.frame_acciones, text="➕ Añadir", command=self.abrir_agregar, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), bd=0, padx=10, pady=6, cursor="hand2").pack(side="left", padx=5)
        tk.Button(self.frame_acciones, text="✏️ Modificar", command=self.modificar_producto, bg="#FF9800", fg="white", font=("Arial", 10, "bold"), bd=0, padx=10, pady=6, cursor="hand2").pack(side="left", padx=5)
        tk.Button(self.frame_acciones, text="❌ Eliminar", command=self.eliminar_producto, bg="#F44336", fg="white", font=("Arial", 10, "bold"), bd=0, padx=10, pady=6, cursor="hand2").pack(side="left", padx=5)

        # 🔹 Botón cargar datos
        self.btn_cargar = tk.Button(
            self,
            text="🔄 Cargar Datos",
            fg="white",
            font=("Arial", 11, "bold"),
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.cargar
        )
        self.btn_cargar.pack(pady=10)


    def actualizar_colores(self):
        """Aplica los colores dependiendo de si el modo oscuro está activo"""
        modo = self.controller.modo_oscuro
        bg_main = "#121212" if modo else "#E8F5E9"
        fg_text = "white" if modo else "black"
        bg_card = "#1E1E1E" if modo else "#F1F8E9"



        self.configure(bg=bg_main)
        self.label_titulo.config(bg=bg_main, fg="#4CAF50" if modo else "#1B5E20")
        self.btn_volver.config(bg="#333333" if modo else "#A5D6A7", fg="white" if modo else "black")
        self.frame_acciones.config(bg=bg_main)
        self.btn_cargar.config(bg="#1976D2" if modo else "#2196F3")
        self.menu.config(bg=bg_card, fg=fg_text, activebackground="#4CAF50")
        self.tree.tag_configure("filTab", background="#C0BABA" if modo else "#ffffff")
        
        self.toggle_btn.config(bg=bg_main, fg=fg_text, activebackground=bg_main)



    def alternar_modo(self):
            """Cambia el modo en el controlador y actualiza este botón inmediatamente"""
            self.controller.toggle_modo_oscuro()
            modo = self.controller.modo_oscuro
            
            # Colores inmediatos para el botón
            bg_actual = "#121212" if modo else "#E8F5E9"
            fg_actual = "white" if modo else "black"

            # Actualizamos el botón aquí mismo
            self.toggle_btn.config(
                text="☀️" if modo else "🌙",
                bg=bg_actual,
                fg=fg_actual,
                activebackground=bg_actual,
                activeforeground=fg_actual
            )
            
            # Luego mandamos a actualizar el resto de la pantalla
            self.actualizar_colores()

    # --- LÓGICA DE DATOS ---
    def cargar(self):
        datos = ver_inventario()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for fila in datos:
            self.tree.insert("", "end", values=fila,tags=("filTab",))

    def mostrar_menu(self, event):
        try:
            row = self.tree.identify_row(event.y)
            if row:
                self.tree.selection_set(row)
                self.menu.post(event.x_root, event.y_root)
        except:
            pass

    def abrir_agregar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Nuevo producto")
        modo = self.controller.modo_oscuro
        ventana.configure(bg="#1E1E1E" if modo else "#F0F0F0")

        def crear_entry(label_text):
            tk.Label(ventana, text=label_text, bg=ventana["bg"], fg="white" if modo else "black").pack(pady=(5,0))
            e = tk.Entry(ventana)
            e.pack(pady=5, padx=20)
            return e

        nombre = crear_entry("Nombre")
        cantidad = crear_entry("Cantidad")
        unidad = crear_entry("Unidad")
        minimo = crear_entry("Stock mínimo")

        def guardar():
            conn = conexion()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?,?,?,?)",
                           (nombre.get(), cantidad.get(), unidad.get(), minimo.get()))
            conn.commit()
            conn.close()
            ventana.destroy()
            self.cargar()

        tk.Button(ventana, text="Guardar", bg="#4CAF50", fg="white", command=guardar).pack(pady=15)

    def eliminar_producto(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un producto")
            return
        
        producto_id = self.tree.item(seleccion)["values"][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            conn = conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            conn.commit()
            conn.close()
            self.cargar()

    def modificar_producto(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un producto")
            return

        item = self.tree.item(seleccion)
        p_id, n_act, c_act, u_act, m_act = item["values"]

        ventana = tk.Toplevel(self)
        ventana.title("Modificar producto")
        modo = self.controller.modo_oscuro
        ventana.configure(bg="#1E1E1E" if modo else "#F0F0F0")

        def crear_entry(label_text, valor_inicial):
            tk.Label(ventana, text=label_text, bg=ventana["bg"], fg="white" if modo else "black").pack(pady=(5,0))
            e = tk.Entry(ventana)
            e.insert(0, valor_inicial)
            e.pack(pady=5, padx=20)
            return e

        enombre = crear_entry("Nombre", n_act)
        ecantidad = crear_entry("Cantidad", c_act)
        eunidad = crear_entry("Unidad", u_act)
        eminimo = crear_entry("Stock mínimo", m_act)

        def guardar():
            conn = conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET nombre=?, cantidad=?, unidad=?, stock_minimo=? WHERE id=?",
                           (enombre.get(), ecantidad.get(), eunidad.get(), eminimo.get(), p_id))
            
            if eminimo.get()<ecantidad.get():
                cursor.execute("select * from lista_compras where producto_id=? and comprado=0",(p_id,))
                resultado=cursor.fetchall()
                if resultado:
                    cursor.execute("UPDATE lista_compras SET cantidad=? WHERE id=?",
                           (float(eminimo.get())-float(ecantidad.get()),resultado[0][0]))
                else:
                    cursor.execute("INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado) VALUES (?, ?, ?, ?)", (p_id, float(eminimo.get()) - float(ecantidad.get()), eunidad.get(), 0))           
            conn.commit()
            conn.close()
            ventana.destroy()
            self.cargar()

        tk.Button(ventana, text="Guardar cambios", bg="#FF9800", fg="white", command=guardar).pack(pady=15)

# =========================
# 🍳 RECETAS
# =========================
class RecetasFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="RECETARIO DISPONIBLE", font=("Arial", 18, "bold"), pady=10).pack()

        tk.Button(self, text="⬅ Volver al Inicio", command=lambda: controller.show_frame(HomeFrame)).pack(pady=5)

        self.listbox = tk.Listbox(self, font=("Arial", 12), width=50, height=10)
        self.listbox.pack(pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack()

        tk.Button(btn_frame, text="🔄 Cargar Recetas", command=self.cargar, width=15).grid(row=0, column=0, padx=5, pady=10)
        tk.Button(btn_frame, text="📝 Usar Receta", bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                  command=self.usar, width=15).grid(row=0, column=1, padx=5, pady=10)

    def cargar(self):
        self.listbox.delete(0, tk.END)
        recetas = obtener_recetas()
        for r in recetas:
            self.listbox.insert(tk.END, f"{r[0]} - {r[1]}")

    '''    def usar(self):
            seleccion = self.listbox.get(tk.ACTIVE)
            if not seleccion:
                messagebox.showwarning("Atención", "Por favor, selecciona una receta.")
                return

            try:
                receta_id = int(seleccion.split(" - ")[0])
                generar_lista_desde_receta(receta_id)
                messagebox.showinfo("Éxito", f"Se han añadido los ingredientes faltantes a la lista de compra.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo procesar la receta: {e}")

    '''


    def usar(self):
        seleccion = self.listbox.get(tk.ACTIVE)
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona una receta.")
            return

        try:
            receta_id = int(seleccion.split(" - ")[0])
            # Esta es la función que definimos arriba
            generar_lista_desde_receta(receta_id)
            
            messagebox.showinfo("Proceso Completado", 
                "Se ha analizado el inventario.\n"
                "Los ingredientes faltantes han sido añadidos a tu lista de compra.")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la receta: {e}")


# =========================
# 🛒 LISTA COMPRA
# =========================
class ListaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="LISTA DE COMPRA PENDIENTE", font=("Arial", 18, "bold"), pady=10).pack()

        tk.Button(self, text="⬅ Volver al Inicio", command=lambda: controller.show_frame(HomeFrame)).pack(pady=5)

        columnas = ("ID", "Producto", "Cantidad", "Unidad")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings")

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack()

        tk.Button(btn_frame, text="🔄 Cargar Lista", command=self.cargar, width=15).grid(row=0, column=0, padx=5, pady=10)
        tk.Button(btn_frame, text="✅ Marcar Comprado", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                  command=self.marcar, width=15).grid(row=0, column=1, padx=5, pady=10)

    def cargar(self):
        datos = ver_tareas_todas()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for fila in datos:
            self.tree.insert("", "end", values=fila)

    def marcar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto de la lista.")
            return

        item = self.tree.item(seleccion)
        valores = item["values"]

        marcar_comprado(valores[0])

        messagebox.showinfo("Actualizado", f"{valores[1]} marcado como comprado.")

        # 🔥 refresco automático inmediato
        self.after(100, self.cargar)

# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    app = App()
    app.mainloop()