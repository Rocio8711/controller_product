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

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SmartKitchen Inventory")
        self.geometry("800x600")


        # 🎨 ESTILOS GENERALES (Treeview + cabeceras)
        style = ttk.Style(self)

        # Tema necesario para que funcionen los colores
        style.theme_use("clam")

        # 🔹 Cabeceras
        style.configure("Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background="#2E7D32",
            foreground="white",
            padding=6,
            relief="flat"
        )

        # Hover en cabecera
        style.map("Treeview.Heading",
            background=[("active", "#388E3C")]
        )

        # 🔹 Tabla
        style.configure("Treeview",
            background="#ffffff",
            foreground="black",
            rowheight=28,
            fieldbackground="#ffffff",
            font=("Segoe UI", 10)
        )

        # Selección
        style.map("Treeview",
            background=[("selected", "#A5D6A7")],
            foreground=[("selected", "black")]
        )



        # Contenedor principal para los frames
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Configuración de pesos para que los frames hijos se expandan
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Inicialización de todos los frames
        for F in (HomeFrame, InventarioFrame, RecetasFrame, ListaFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomeFrame)

    '''def show_frame(self, frame_class):
        """Muestra el frame solicitado elevándolo al frente"""
        frame = self.frames[frame_class]
        frame.tkraise()'''


    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

        # 🔥 ejecutar después de que Tkinter renderice la pantalla
        self.after(50, self._refresh_frame, frame)

    def _refresh_frame(self, frame):
        if hasattr(frame, "cargar"):
            # evitar doble ejecución accidental
            if not getattr(frame, "_cargando", False):
                frame._cargando = True
                frame.cargar()
                frame._cargando = False

# =========================
# 🏠 HOME
# =========================
class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Centrar contenido
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        contenido = tk.Frame(self)
        contenido.grid(row=0, column=0)

        # Título
        tk.Label(
            contenido,
            text="CONTROLLER PRODUCT",
            font=("Arial", 26, "bold"),
            fg="#2E7D32"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # Imagen de Logo
        try:
            # Asegúrate de que esta ruta sea correcta en tu PC
            image = Image.open(r"C:\Users\sienr\Documents\Proyecto_ControllerProduct\logo.jpeg")
            image = image.resize((180, 180))
            controller.logo_img = ImageTk.PhotoImage(image)
            tk.Label(contenido, image=controller.logo_img).grid(row=1, column=0, padx=40)
        except Exception:
            tk.Label(contenido, text="[Logo no encontrado]", fg="red", font=("Arial", 12)).grid(row=1, column=0, padx=40)

        # Botones de navegación
        boton_estilo = {
            "font": ("Arial", 14, "bold"),
            "bg": "#4CAF50",
            "fg": "white",
            "activebackground": "#45a049",
            "activeforeground": "white",
            "width": 20,
            "bd": 0,
            "cursor": "hand2",
            "pady": 10
        }

        frame_botones = tk.Frame(contenido)
        frame_botones.grid(row=1, column=1, padx=40)

        tk.Button(frame_botones, text="📦 Inventario", command=lambda: controller.show_frame(InventarioFrame), **boton_estilo).pack(pady=10)
        tk.Button(frame_botones, text="🍳 Recetas", command=lambda: controller.show_frame(RecetasFrame), **boton_estilo).pack(pady=10)
        tk.Button(frame_botones, text="🛒 Lista de compra", command=lambda: controller.show_frame(ListaFrame), **boton_estilo).pack(pady=10)


# =========================
# 📦 INVENTARIO
# =========================
class InventarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # 🎨 Fondo general
        self.configure(bg="#E8F5E9")

        # 🔹 Título
        tk.Label(
            self,
            text="📦 INVENTARIO DE PRODUCTOS",
            font=("Arial", 20, "bold"),
            bg="#E8F5E9",
            fg="#1B5E20"
        ).pack(pady=15)

        # 🔹 Botón volver
        tk.Button(
            self,
            text="⬅ Volver al Inicio",
            bg="#A5D6A7",
            fg="black",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda: controller.show_frame(HomeFrame)
        ).pack(pady=5)

        # 🔹 Tabla
        columnas = ("ID", "Producto", "Cantidad", "Unidad", "Min")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings")

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        self.tree.pack(fill="both", expand=True, padx=20, pady=15)


        # 🔹 Menú contextual (clic derecho) con estilo
        self.menu = tk.Menu(
            self,
            tearoff=0,
            bg="#F1F8E9",
            fg="#1B5E20",
            activebackground="#81C784",
            activeforeground="black",
            font=("Segoe UI", 10, "bold"),
            bd=0
        )

        self.menu.add_command(label="➕  Añadir producto", command=self.abrir_agregar)
        self.menu.add_command(label="✏️  Editar producto", command=self.modificar_producto)
        self.menu.add_separator()
        self.menu.add_command(label="🗑️  Eliminar producto", command=self.eliminar_producto)

        self.tree.bind("<Button-3>", self.mostrar_menu)

        # 🔹 Frame de botones
        frame_acciones = tk.Frame(self, bg="#E8F5E9")
        frame_acciones.pack(pady=10)

        def crear_boton(texto, comando, color):
            return tk.Button(
                frame_acciones,
                text=texto,
                command=comando,
                bg=color,
                fg="white",
                font=("Arial", 10, "bold"),
                bd=0,
                padx=10,
                pady=6,
                cursor="hand2"
            )

        crear_boton("➕ Añadir", self.abrir_agregar, "#4CAF50").pack(side="left", padx=5)
        crear_boton("✏️ Modificar", self.modificar_producto, "#FF9800").pack(side="left", padx=5)
        crear_boton("❌ Eliminar", self.eliminar_producto, "#F44336").pack(side="left", padx=5)

        # 🔹 Botón cargar datos
        tk.Button(
            self,
            text="🔄 Cargar Datos",
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.cargar
        ).pack(pady=10)


    def cargar(self):
        datos = ver_inventario()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for fila in datos:
            self.tree.insert("", "end", values=fila)

    def mostrar_menu(self, event):
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.menu.post(event.x_root, event.y_root)
        except:
            pass

    def abrir_agregar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Nuevo producto")

        tk.Label(ventana, text="Nombre").pack()
        nombre = tk.Entry(ventana)
        nombre.pack()

        tk.Label(ventana, text="Cantidad").pack()
        cantidad = tk.Entry(ventana)
        cantidad.pack()

        tk.Label(ventana, text="Unidad").pack()
        unidad = tk.Entry(ventana)
        unidad.pack()

        tk.Label(ventana, text="Stock mínimo").pack()
        minimo = tk.Entry(ventana)
        minimo.pack()

        def guardar():
            conn = conexion()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO productos (nombre, cantidad, unidad, stock_minimo)
                VALUES (?, ?, ?, ?)
            """, (nombre.get(), cantidad.get(), unidad.get(), minimo.get()))

            conn.commit()
            conn.close()

            ventana.destroy()
            self.cargar()

        tk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
    
    
    def eliminar_producto(self):
        seleccion = self.tree.selection()

        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un producto")
            return

        item = self.tree.item(seleccion)
        producto_id = item["values"][0]

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
        producto_id, nombre_actual, cantidad_actual, unidad_actual, minimo_actual = item["values"]

        ventana = tk.Toplevel(self)
        ventana.title("Modificar producto")

        nombre = tk.Entry(ventana)
        nombre.insert(0, nombre_actual)
        nombre.pack()

        cantidad = tk.Entry(ventana)
        cantidad.insert(0, cantidad_actual)
        cantidad.pack()

        unidad = tk.Entry(ventana)
        unidad.insert(0, unidad_actual)
        unidad.pack()

        minimo = tk.Entry(ventana)
        minimo.insert(0, minimo_actual)
        minimo.pack()

        def guardar():
            conn = conexion()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE productos
                SET nombre=?, cantidad=?, unidad=?, stock_minimo=?
                WHERE id=?
            """, (nombre.get(), cantidad.get(), unidad.get(), minimo.get(), producto_id))

            conn.commit()
            conn.close()

            ventana.destroy()
            self.cargar()

        tk.Button(ventana, text="Guardar cambios", command=guardar).pack(pady=10)


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