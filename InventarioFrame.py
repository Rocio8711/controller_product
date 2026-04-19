import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Importamos los módulos de lógica
from InicializacionBaseDatos.acceso_base_datos import conexion
from inventario import ver_inventario

'''VENTANA DE INVENTARIO'''

class InventarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.menu = None
        self._setup_ui()

    def _setup_ui(self):
        # Limpiar la interfaz, eliminamos widgets previos para evitar duplicados al recargar
        for widget in self.winfo_children():
            widget.destroy()

        modo = self.controller.modo_oscuro
        
        # Configuración de Colores para el modo oscuro
        bg_main = "#121212" if modo else "#F8F9FA"
        fg_text = "#FFFFFF" if modo else "#333333"
        accent_green = "#2E7D32" if modo else "#1B5E20"
        card_bg = "#1E1E1E" if modo else "#FFFFFF"
        
        # Modo Oscuro: Un verde grisáceo / Modo Claro: Un verde pastel
        select_bg = "#38493A" if modo else "#C8E6C9" 
        select_fg = "#FFFFFF" if modo else "#000000"

        self.configure(bg=bg_main)


        #Botones de control

        # Botón de Modo Oscuro
        self.toggle_btn = tk.Button(
            self, text="☀️" if modo else "🌙",
            command=self.alternar_modo,
            font=("Segoe UI Emoji", 14), bd=0, cursor="hand2",
            bg=bg_main, fg=fg_text, activebackground=bg_main,
            highlightthickness=0
        )
        self.toggle_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # Botón para cerrar sesion
        self.logout_btn = tk.Button(
            self, text="🚪",
            command=self.cerrar_sesion,
            font=("Segoe UI Emoji", 14), bd=0, 
            bg=bg_main, fg="#f44336", # <-- Ahora usa bg_main
            activebackground=bg_main, cursor="hand2"
        )
        self.logout_btn.place(relx=0.98, rely=0.08, anchor="ne")

        # Título y logo
        header_frame = tk.Frame(self, bg=bg_main)
        header_frame.pack(pady=(30, 5))

        # El ícono de la cajita en marron
        tk.Label(
            header_frame, text="📋",
            font=("Calibri", 24),
            bg=bg_main, 
            fg="#8B4513"  # Marrón para la caja queda mass realista
        ).pack(side="left", padx=5)

        # titulo princiap de la seccion
        tk.Label(
            header_frame, text="Inventario de Productos",
            font=("Calibri", 22, "bold"),
            bg=bg_main, 
            fg=accent_green
        ).pack(side="left")

        # Botón Volver que nos lleva el menu principal
        tk.Button(
            self, text="⬅ Volver",
            bg="#444444" if modo else "#E0E0E0",
            fg="white" if modo else "black",
            command=self.ir_a_home
        ).pack(pady=5)

        # Estilo de la Tabla (Treeview)
        style = ttk.Style()
        style.theme_use("default") 
        
        #estilo de las filas
        style.configure("Treeview", 
                        background=card_bg, 
                        foreground=fg_text,
                        fieldbackground=card_bg,
                        rowheight=30,
                        font=("Segoe UI", 10),
                        borderwidth=0)
        
        #estilo de las cabeceras de la tabla
        style.configure("Treeview.Heading", 
                        background=accent_green, 
                        foreground="white", 
                        font=("Segoe UI", 11, "bold"),
                        relief="flat")
        
        # aqui es donde se pone el verde clarito cuando pasa el usuario 
        style.map("Treeview", 
                  background=[('selected', select_bg)],
                  foreground=[('selected', select_fg)])

        # Configuracion de la tabla
        #frame contenedor para la tabla y la barra de desplazamiento
        self.frame_tabla = tk.Frame(self, bg=bg_main)
        self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=5)

        #definimos las columnas del inventario
        columnas = ("ID", "Producto", "Cantidad", "Unidad", "Min")
        self.tree = ttk.Treeview(self.frame_tabla, columns=columnas, show="headings", style="Treeview")


        #configuracion de encabezados y anchos de las columas
        for col in columnas:
            self.tree.heading(col, text=col)
            ancho = 250 if col == "Producto" else 80
            self.tree.column(col, width=ancho, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        #la barra de desplazamiento vertical vinculada al treeview
        scroll = tk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # Menú Contextual
        #creamos el menu dessplegable
        self.menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 10), bg=card_bg, fg=fg_text)
        self.menu.add_command(label="➕ Añadir producto", command=self.abrir_agregar)
        self.menu.add_command(label="✏️ Modificar producto", command=self.modificar_producto)
        self.menu.add_separator()
        self.menu.add_command(label="🗑️ Borrar producto", command=self.borrar_producto)

        #aqui vinculamos el evento del click derecho para que se nos muestre el menu
        self.tree.bind("<Button-3>", self.mostrar_menu)

        # Frame de Acciones de los botones inferiores
        self.frame_acciones = tk.Frame(self, bg=bg_main)
        self.frame_acciones.pack(pady=20)

        #configuracion de botones
        btn_configs = [
            ("➕ Añadir", "#4CAF50", self.abrir_agregar),
            ("✏️ Modificar", "#FF9800", self.modificar_producto),
            ("❌ Borrar", "#F44336", self.borrar_producto)
        ]

        # Creación dinámica de botones mediante un bucle (texto, color, accion)
        for i, (texto, color, comando) in enumerate(btn_configs):
            tk.Button(
                self.frame_acciones,
                text=texto,
                command=comando,
                bg=color,
                fg="white",
                bd=0
            ).grid(row=0, column=i, padx=5)
        
        #Carga inicial de datos desde la base de datos al Treeview
        self.cargar()

    def alternar_modo(self):
        # 1. Llama a la función del controlador principal para cambiar el estado global.
        # Esto cambia una variable (ej. de True a False) en el archivo principal.
        self.controller.toggle_modo_oscuro()

        # 2. Vuelve a ejecutar la configuración de la interfaz (colores, botones, etc.)
        # Al ejecutarse de nuevo, leerá el nuevo estado y aplicará los colores correctos.
        self._setup_ui()

    def ir_a_home(self):
        #importamos la pantalla de inicio y le decimos al controlador que la muestre
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def mostrar_menu(self, event):
        #buscamos que fila se ha tocado con el raton y desplegamos nuestro menu en ese sitio
        row = self.tree.identify_row(event.y)
        if row:
            self.tree.selection_set(row)
            self.menu.post(event.x_root, event.y_root)

    def cargar(self):
        #limpiamos la tabla para que no se repitan los datos y traemos todo lo nuevo de la base de datos
        datos = ver_inventario()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for fila in datos:
            f_lista = list(fila)
            #si el numero tiene muchos decimales lo redondeamos a dos para que no quede feo
            if isinstance(f_lista[2], (float, int)):
                f_lista[2] = round(float(f_lista[2]), 2)
            self.tree.insert("", "end", values=f_lista)


    def cerrar_sesion(self):
            #preguntamos al usuario si de verdad quiere salir, borramos su rastro y reiniciamos el login
            if messagebox.askyesno("Cerrar Sesión", "¿Seguro que quieres salir?"):
                #Limpieza de seguridad
                self.controller.usuario_email = None
                
                #Cerramos la ventana de la App
                self.controller.destroy()
                
                #Reiniciamos el Login (Usando la clase LoginApp)
                import tkinter as tk
                from login import LoginApp
                
                root_login = tk.Tk()
                LoginApp(root_login)
                root_login.mainloop()


    def abrir_agregar(self):
        #creamos una ventanita nueva y adaptamos su color segun tengamos el modo oscuro o claro
        ventana = tk.Toplevel(self)
        ventana.title("Nuevo producto")
        modo = self.controller.modo_oscuro
        ventana.configure(bg="#1E1E1E" if modo else "#F0F0F0")

        def crear_entry(label_text):
            #metemos una etiqueta y un cuadro de texto para que podamos escribir los datos
            tk.Label(ventana, text=label_text, bg=ventana["bg"], fg="white" if modo else "black").pack(pady=(5,0))
            e = tk.Entry(ventana)
            e.pack(pady=5, padx=20)
            return e

        nombre = crear_entry("Nombre")
        cantidad = crear_entry("Cantidad")
        unidad = crear_entry("Unidad")
        minimo = crear_entry("Stock mínimo")

        def guardar():
            #recogemos lo que hemos escrito y lo guardamos en la base de datos controlando que no falte nada
            try:
                n, c, u, m = nombre.get(), cantidad.get(), unidad.get(), minimo.get()
                if not n or not c: raise ValueError("Nombre y Cantidad obligatorios")

                conn = conexion(); cur = conn.cursor()
                cur.execute("INSERT INTO productos (nombre, cantidad, unidad, stock_minimo) VALUES (?,?,?,?)",(n, float(c), u, float(m) if m else 0))
                nuevo_id = cur.lastrowid # obtenemos el ID del último registro insertado (vamos el producto recien creado)
                #si vemos que el stock no llega al minimo, añadimos el producto automaticamente a nuestra lista de la compra
                if float(c) < float(m) :
                    cantidad_comprar=float(m) - float(c) 
                    cur.execute("INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado)VALUES (?, ?, ?, 0)", (nuevo_id, cantidad_comprar, u))

                conn.commit(); conn.close()
                ventana.destroy()
                self.cargar()
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al guardar: {e}")

        tk.Button(ventana, text="Guardar", bg="#4CAF50", fg="white", command=guardar, padx=15).pack(pady=15)



    def borrar_producto(self):
        #comprobamos si hemos seleccionado algo en la tabla para saber qué borrar
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un producto")
            return
        #sacamos el id del producto y le pedimos confirmación al usuario para no borrar por error
        item = self.tree.item(seleccion); p_id = item["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Borrar '{item['values'][1]}'?"):
            conn = conexion(); cur = conn.cursor()

            #borramos el producto de la tabla principal y también de la lista de la compra para que no quede suelto
            cur.execute("DELETE FROM productos WHERE id = ?", (p_id,))
            cur.execute("DELETE FROM lista_compras WHERE producto_id = ?", (p_id,))
            conn.commit(); conn.close()
            self.cargar()

    def modificar_producto(self):
        #miramos qué producto queremos cambiar y cargamos sus datos actuales para editarlos
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un producto")
            return
        item = self.tree.item(seleccion)
        p_id, n_act, c_act, u_act, m_act = item["values"]
        c_act = float(c_act)
        m_act = float(m_act)

        #abrimos una ventana con el color que toque y preparamos los campos con la información que ya tenemos
        ventana = tk.Toplevel(self)
        ventana.title("Modificar producto")
        modo = self.controller.modo_oscuro
        ventana.configure(bg="#1E1E1E" if modo else "#F0F0F0")

        def crear_entry(label_text, valor_inicial):
            #ponemos una etiqueta y rellenamos el cuadro de texto con el valor que ya tenía el producto
            tk.Label(ventana, text=label_text, bg=ventana["bg"], fg="white" if modo else "black").pack(pady=(5,0))
            e = tk.Entry(ventana); e.insert(0, valor_inicial); e.pack(pady=5, padx=20)
            return e

        enombre = crear_entry("Nombre", n_act)
        ecantidad = crear_entry("Cantidad", c_act)
        eunidad = crear_entry("Unidad", u_act)
        eminimo = crear_entry("Stock mínimo", m_act)

        def guardar():
            #actualizamos los datos en la base de datos y recalculamos si nos hace falta comprar más
            try:
                n_new, c_new = enombre.get(), float(ecantidad.get())
                u_new, m_new = eunidad.get(), float(eminimo.get())
                conn = conexion(); cur = conn.cursor()
                
                cur.execute("UPDATE productos SET nombre=?, cantidad=?, unidad=?, stock_minimo=? WHERE id=?",
                            (n_new, c_new, u_new, m_new, p_id))
            
                
                #IMPORTANTE si hemos cambiado las cantidades revisamos cuántos ingredientes nos piden las recetas que tenemos pendientes
                if c_act != c_new or m_act != m_new:
                    cur.execute("SELECT receta_ingredientes.cantidad FROM recetas_pendientes inner join receta_ingredientes on recetas_pendientes.receta_id=receta_ingredientes.receta_id where receta_ingredientes.producto_id=? and recetas_pendientes.completada=0",(p_id,))
                    resultado=cur.fetchall()
                    cantidad=0
                    for res in resultado:
                        num=float(res[0])
                        cantidad+=num

                    #si ya estaba en la lista de compras actualizamos la cantidad y si no estaba lo insertamos nuevo
                    if c_new - cantidad < m_new:
                        cantidad_teorica=c_new-cantidad
                        comprar=m_new-cantidad_teorica
                        cur.execute("SELECT id FROM lista_compras WHERE producto_id=? AND comprado=0", (p_id,))
                        res=cur.fetchone()
                        if res: cur.execute("UPDATE lista_compras SET cantidad=? WHERE id=?", (comprar, res[0]))
                        else: cur.execute("INSERT INTO lista_compras (producto_id, cantidad, unidad, comprado) VALUES (?, ?, ?, 0)", (p_id, comprar, u_new))
                    
                    else:
                        #si tras la modificación ya tenemos suficiente stock borramos el producto de la lista de compras pendiente
                        cur.execute("SELECT id FROM lista_compras WHERE producto_id=? AND comprado=0", (p_id,))
                        res=cur.fetchone()
                        if res: 
                            cur.execute("DELETE FROM lista_compras WHERE producto_id=? AND comprado=0", (p_id,))

                conn.commit(); conn.close()
                ventana.destroy(); self.cargar()
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al actualizar: {e}")

        tk.Button(ventana, text="Guardar cambios", bg="#FF9800", fg="white", command=guardar, padx=15).pack(pady=15)