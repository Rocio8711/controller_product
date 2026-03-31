import tkinter as tk
from tkinter import ttk, messagebox

# Importamos las funciones de tu lógica (asegúrate de que los nombres coincidan)
from lista_compras import ver_tareas_todas, marcar_comprado

# =========================
# 🛒 LISTA COMPRA
# =========================
class ListaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Título
        tk.Label(self, text="LISTA DE COMPRA PENDIENTE", font=("Arial", 18, "bold"), pady=10).pack()

        # ⬅ BOTÓN VOLVER (Configurado para enlazar con HomeFrame.py)
        tk.Button(
            self, 
            text="⬅ Volver al Inicio", 
            command=self.ir_a_home,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(pady=5)

        # Configuración de la Tabla (Treeview)
        columnas = ("ID", "Producto", "Cantidad", "Unidad")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings")

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Botones de acción
        btn_frame = tk.Frame(self)
        btn_frame.pack()

        tk.Button(
            btn_frame, 
            text="🔄 Cargar Lista", 
            command=self.cargar, 
            width=15
        ).grid(row=0, column=0, padx=5, pady=10)

        tk.Button(
            btn_frame, 
            text="✅ Marcar Comprado", 
            bg="#4CAF50", 
            fg="white", 
            font=("Arial", 10, "bold"),
            command=self.marcar, 
            width=15,
            cursor="hand2"
        ).grid(row=0, column=1, padx=5, pady=10)

    # --- FUNCIONES DE ENLACE Y LÓGICA ---

    def ir_a_home(self):
        """Puente para volver al menú principal sin errores de importación"""
        from HomeFrame import HomeFrame
        self.controller.show_frame(HomeFrame)

    def cargar(self):
        """Carga los datos desde el módulo lista_compras.py"""
        try:
            datos = ver_tareas_todas()
            for i in self.tree.get_children():
                self.tree.delete(i)
            for fila in datos:
                self.tree.insert("", "end", values=fila)
        except Exception as e:
            print(f"Error al cargar la lista: {e}")

    def marcar(self):
        """Marca un producto como comprado y refresca la tabla"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto de la lista.")
            return

        item = self.tree.item(seleccion)
        valores = item["values"]

        try:
            marcar_comprado(valores[0]) # Usa el ID del producto
            messagebox.showinfo("Actualizado", f"{valores[1]} marcado como comprado.")
            
            # Refresco automático después de marcar
            self.after(100, self.cargar)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo marcar como comprado: {e}")