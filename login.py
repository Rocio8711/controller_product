import tkinter as tk
from tkinter import messagebox, simpledialog
from usuario import login as login_bd
from grafica import App  # Importamos tu clase principal moderna

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Controller Product")
        self.root.geometry("400x400")
        self.root.configure(bg="#F8F9FA") # Fondo claro y limpio

        # Centrar la ventana de login en la pantalla al iniciar
        self.root.eval('tk::PlaceWindow . center')

        # --- Contenedor Principal ---
        self.container = tk.Frame(root, bg="#F8F9FA", pady=20)
        self.container.pack(expand=True)

        # Título
        tk.Label(self.container, text="BIENVENIDO", font=("Segoe UI", 20, "bold"), 
                 bg="#F8F9FA", fg="#2E7D32").pack(pady=(0, 25))

        # Campo Email
        tk.Label(self.container, text="Email", bg="#F8F9FA", font=("Segoe UI", 10, "bold"), fg="#555555").pack(anchor="w")
        self.email_entry = tk.Entry(self.container, font=("Segoe UI", 12), width=30, bd=1, relief="solid")
        self.email_entry.pack(pady=(5, 20), ipady=5)

        # Campo Contraseña
        tk.Label(self.container, text="Contraseña", bg="#F8F9FA", font=("Segoe UI", 10, "bold"), fg="#555555").pack(anchor="w")
        self.password_entry = tk.Entry(self.container, show="*", font=("Segoe UI", 12), width=30, bd=1, relief="solid")
        self.password_entry.pack(pady=(5, 30), ipady=5)

        # Botón Iniciar Sesión (Estilo moderno)
        self.btn_login = tk.Button(
            self.container, text="Iniciar Sesión", command=self.login,
            bg="#2E7D32", fg="white", font=("Segoe UI", 12, "bold"),
            width=25, bd=0, cursor="hand2", pady=10, activebackground="#388E3C", activeforeground="white"
        )
        self.btn_login.pack(pady=5)

        # Botón Registrar
        tk.Button(
            self.container, text="¿No tienes cuenta? Regístrate", 
            command=self.abrir_registro, bg="#F8F9FA", fg="#2E7D32", 
            bd=0, cursor="hand2", font=("Segoe UI", 10, "underline")
        ).pack(pady=10)

    def mostrar_notificacion(self, mensaje, color_bg="#2E7D32"):
        """Crea un mensaje flotante que desaparece solo tras 3 segundos"""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True) # Quita bordes de ventana
        toast.configure(bg=color_bg)
        
        # Posicionamiento centrado respecto al Login
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 120
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 30
        toast.geometry(f"+{int(x)}+{int(y)}")

        tk.Label(toast, text=mensaje, fg="white", bg=color_bg, 
                 padx=30, pady=15, font=("Segoe UI", 12, "bold")).pack()

        # Se destruye a los 3 segundos automáticamente
        toast.after(3000, toast.destroy)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        usuario = login_bd(email, password)

        if usuario:
            nombre = usuario[1].capitalize()
            # 1. Mostrar notificación visual
            self.mostrar_notificacion(f"✅ ¡Bienvenid@ {nombre}!")
            
            # 2. Desactivar botones para evitar dobles clics
            self.btn_login.config(state="disabled")

            # 3. Esperar 1.5 seg para que se vea el mensaje y saltar a la App
            self.root.after(1500, self.finalizar_login) 
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def finalizar_login(self):
        """Cierra el login y lanza la aplicación principal"""
        self.root.destroy()
        app_principal = App()
        app_principal.mainloop()

    def abrir_registro(self):
        clave = simpledialog.askstring("Acceso Restringido", "Introduce la clave de gestor:", show="*")
        if clave != "12345":
            messagebox.showerror("Error", "Clave incorrecta")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Registro de Usuario")
        ventana.geometry("350x450")
        ventana.configure(bg="#F8F9FA")

        # Formulario de registro (simplificado para el ejemplo)
        tk.Label(ventana, text="NUEVO REGISTRO", font=("Segoe UI", 14, "bold"), bg="#F8F9FA", fg="#2E7D32").pack(pady=20)
        
        tk.Label(ventana, text="Nombre completo", bg="#F8F9FA").pack()
        nom_e = tk.Entry(ventana, width=30); nom_e.pack(pady=5)

        tk.Label(ventana, text="Email", bg="#F8F9FA").pack()
        ema_e = tk.Entry(ventana, width=30); ema_e.pack(pady=5)

        tk.Label(ventana, text="Contraseña", bg="#F8F9FA").pack()
        pas_e = tk.Entry(ventana, show="*", width=30); pas_e.pack(pady=5)

        def ejecutar_registro():
            from usuario import agregar_usuario
            if nom_e.get() and ema_e.get() and pas_e.get():
                agregar_usuario(nom_e.get(), ema_e.get(), pas_e.get())
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                ventana.destroy()
            else:
                messagebox.showwarning("Atención", "Rellena todos los campos")

        tk.Button(ventana, text="Crear Cuenta", command=ejecutar_registro, 
                  bg="#2E7D32", fg="white", width=20, pady=10, bd=0).pack(pady=30)

# --- INICIO DE LA APLICACIÓN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()