import tkinter as tk
import re
from tkinter import simpledialog
from usuario import login as login_bd
from grafica import App


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Controller Product")
        self.root.geometry("400x400")
        self.root.configure(bg="#F8F9FA")
        #self.root.eval('tk::PlaceWindow . center')


        self.root.update_idletasks()

        ancho = 400
        alto = 400

        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)

        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")




        self.container = tk.Frame(root, bg="#F8F9FA", pady=20)
        self.container.pack(expand=True)

        tk.Label(
            self.container,
            text="BIENVENIDO",
            font=("Segoe UI", 20, "bold"),
            bg="#F8F9FA",
            fg="#2E7D32"
        ).pack(pady=(0, 25))

        # EMAIL
        tk.Label(self.container, text="Email", bg="#F8F9FA").pack(anchor="w")
        self.email_entry = tk.Entry(self.container, font=("Segoe UI", 12), width=30, fg="#2E7D32")
        self.email_entry.pack(pady=(5, 15), ipady=5)

        # PASSWORD
        tk.Label(self.container, text="Contraseña", bg="#F8F9FA").pack(anchor="w")
        self.password_entry = tk.Entry(self.container, font=("Segoe UI", 12), width=30, show="*", fg="#2E7D32")
        self.password_entry.pack(pady=(5, 10), ipady=5)

        self.show_pass = tk.BooleanVar()
        tk.Checkbutton(
            self.container,
            text="Mostrar contraseña",
            variable=self.show_pass,
            command=self.toggle_password,
            bg="#F8F9FA"
        ).pack(anchor="w")

        # LOGIN
        self.btn_login = tk.Button(
            self.container,
            text="Iniciar Sesión",
            command=self.login,
            bg="#2E7D32",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            width=25,
            bd=0,
            pady=10,
            cursor="hand2"
        )
        self.btn_login.pack(pady=10)

        # REGISTRO
        tk.Button(
            self.container,
            text="¿No tienes cuenta? Regístrate",
            command=self.abrir_seguridad,
            bg="#F8F9FA",
            fg="#2E7D32",
            bd=0,
            font=("Segoe UI", 10, "underline"),
            cursor="hand2"
        ).pack(pady=10)

    # =====================================================
    # ALERTA MODERNA
    # =====================================================
    def mostrar_alerta(self, titulo, mensaje, tipo="info"):
        alerta = tk.Toplevel(self.root)
        alerta.title(titulo)
        alerta.geometry("320x200")
        alerta.configure(bg="white")
        alerta.resizable(False, False)
        alerta.grab_set()

        color = "#2E7D32" if tipo == "info" else "#D32F2F"
        icono = "✅" if tipo == "info" else "❌"

        tk.Label(alerta, text=icono, font=("Segoe UI", 25), bg="white", fg=color).pack(pady=10)
        tk.Label(alerta, text=mensaje, bg="white", wraplength=280, font=("Segoe UI", 11)).pack(pady=10)

        tk.Button(
            alerta,
            text="OK",
            command=alerta.destroy,
            bg=color,
            fg="white",
            bd=0,
            padx=20,
            pady=8
        ).pack(pady=10)



    def mostrar_notificacion(self, mensaje, color_bg="#2E7D32"):
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)

        # fondo invisible
        toast.configure(bg=self.root["bg"])

        #centramos el mensaje de bienvenida al centro
        self.root.update_idletasks()

        toast.update_idletasks()

        w = toast.winfo_reqwidth()
        h = toast.winfo_reqheight()

        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (h // 2)

        toast.geometry(f"+{int(x)}+{int(y)}")

        toast.geometry(f"+{int(x)}+{int(y)}")

        # caja “moderna”
        frame = tk.Frame(toast, bg=color_bg, padx=30, pady=18)
        frame.pack()

        tk.Label(
            frame,
            text=mensaje,
            fg="white",
            bg=color_bg,
            font=("Segoe UI", 16, "bold")
        ).pack()

        toast.after(2500, toast.destroy)


    # =====================================================
    def toggle_password(self):
        self.password_entry.config(
            show="" if self.show_pass.get() else "*"
        )

    # =====================================================
    # LOGIN
    # =====================================================
    def login(self):
        email = self.email_entry.get().strip().lower()
        password = self.password_entry.get()

        if not email or not password:
            self.mostrar_alerta("Error", "Rellena todos los campos", "error")
            return

        usuario = login_bd(email, password)

        if usuario:
            nombre = usuario[1].capitalize()

            self.mostrar_bienvenida(nombre)

            self.root.after(2000, self.finalizar_login)


        else:
            self.mostrar_alerta("Error", "Credenciales incorrectas", "error")

    def finalizar_login(self):
        self.root.destroy()
        app = App()
        app.mainloop()

    # =====================================================
    # VENTANA DE GESTOR (MEJORADA)
    # =====================================================
    def abrir_seguridad(self):
        v = tk.Toplevel(self.root)
        v.title("Acceso de Administrador")
        v.geometry("350x250")
        v.configure(bg="#F8F9FA")
        v.grab_set()

        tk.Label(
            v,
            text="🔐 ACCESO DE GESTOR",
            font=("Segoe UI", 14, "bold"),
            bg="#F8F9FA",
            fg="#2E7D32"
        ).pack(pady=20)

        tk.Label(v, text="Introduce la clave", bg="#F8F9FA").pack()

        entrada = tk.Entry(v, show="*", font=("Segoe UI", 12), justify="center")
        entrada.pack(pady=10, ipady=5)

        def validar():
            if entrada.get() == "12345":
                v.destroy()
                self.abrir_registro()
            else:
                self.mostrar_alerta("Error", "Clave incorrecta", "error")

        tk.Button(
            v,
            text="Verificar",
            command=validar,
            bg="#2E7D32",
            fg="white",
            bd=0,
            pady=10,
            width=20
        ).pack(pady=20)

    # =====================================================
    # REGISTRO CON VALIDACIONES COMPLETAS
    # =====================================================
    def abrir_registro(self):
        reg = tk.Toplevel(self.root)
        reg.title("Registro de Usuario")
        reg.geometry("400x520")
        reg.configure(bg="#F8F9FA")
        reg.grab_set()

        tk.Label(
            reg,
            text="NUEVO REGISTRO",
            font=("Segoe UI", 14, "bold"),
            bg="#F8F9FA",
            fg="#2E7D32"
        ).pack(pady=15)

        # =====================================================
        # ❓ AYUDA CONTRASEÑA
        # =====================================================
        def ayuda():
            self.mostrar_alerta(
                "Requisitos contraseña",
                "• Mínimo 6 caracteres\n"
                "• Al menos 1 mayúscula\n"
                "• Al menos 1 número\n"
                "• Al menos 1 símbolo (!@#$...)",
                "info"
            )

        tk.Button(
            reg,
            text="❓ Requisitos contraseña",
            bg="#F8F9FA",
            fg="#2E7D32",
            bd=0,
            cursor="hand2",
            command=ayuda
        ).pack(pady=5)

        # =====================================================
        # CAMPOS
        # =====================================================
        def campo(texto, show=None):
            tk.Label(reg, text=texto, bg="#F8F9FA").pack(anchor="w", padx=40)
            e = tk.Entry(reg, width=30, show=show)
            e.pack(pady=5, ipady=5, padx=40)
            return e

        nom = campo("Nombre completo")
        ema = campo("Email")
        pas = campo("Contraseña", show="*")
        pas2 = campo("Repite la contraseña", show="*")

        # =====================================================
        # 👁️ MOSTRAR CONTRASEÑA
        # =====================================================
        ver_pass = tk.BooleanVar()

        def toggle_pass():
            estado = "" if ver_pass.get() else "*"
            pas.config(show=estado)
            pas2.config(show=estado)

        tk.Checkbutton(reg, text="Mostrar contraseñas",
                    variable=ver_pass,
                    command=toggle_pass,
                    bg="#F8F9FA").pack(anchor="w", padx=40)

        # =====================================================
        # GUARDAR USUARIO
        # =====================================================
        def guardar():
            n = nom.get()
            e = ema.get().strip().lower()
            p = pas.get()

            # VALIDACIONES CON ALERTAS MODERNAS
            if not n.strip():
                self.mostrar_alerta("Error", "El nombre no puede estar vacío", "error")
                return

            if not e.strip():
                self.mostrar_alerta("Error", "El email no puede estar vacío", "error")
                return

            if not re.match(r"[^@]+@[^@]+\.[^@]+", e):
                self.mostrar_alerta("Error", "Email inválido", "error")
                return

            if len(p) < 6:
                self.mostrar_alerta("Error", "La contraseña debe tener al menos 6 caracteres", "error")
                return

            if not any(c.isupper() for c in p):
                self.mostrar_alerta("Error", "Debe tener al menos una mayúscula", "error")
                return

            if not any(c.isdigit() for c in p):
                self.mostrar_alerta("Error", "Debe tener al menos un número", "error")
                return


            #como las app reales regex
            if not re.search(r"[!@#$%^&*()\-_=+\[\]{};:'\",.<>?/]", p):
                self.mostrar_alerta("Error", "Debe tener al menos un símbolo", "error")
                return
            
            if p != pas2.get():
                self.mostrar_alerta("Error", "Las contraseñas no coinciden", "error")
                return
            try:
                from usuario import agregar_usuario
                agregar_usuario(n, e, p)

                self.mostrar_alerta("Éxito", "Usuario creado correctamente", "info")
                reg.after(1200, reg.destroy)

            except Exception:
                self.mostrar_alerta("Error", "No se pudo crear el usuario", "error")

        # =====================================================
        # BOTÓN FINAL
        # =====================================================
        tk.Button(
            reg,
            text="Crear Cuenta",
            command=guardar,
            bg="#2E7D32",
            fg="white",
            bd=0,
            pady=12,
            width=22,
            cursor="hand2"
        ).pack(pady=20)


    #mensaje chulo!
    def mostrar_bienvenida(self, nombre):
        self.mostrar_notificacion(f"👋 Hola, {nombre}", "#2E7D32")
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()