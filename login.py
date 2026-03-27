import tkinter as tk
from tkinter import messagebox
from usuario import login as login_bd
from grafica import App


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x200")

        tk.Label(root, text="Email").pack()
        self.email_entry = tk.Entry(root)
        self.email_entry.pack()

        tk.Label(root, text="Contraseña").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Iniciar sesión", command=self.login).pack(pady=10)
        tk.Button(root, text="Registrarse", command=self.abrir_registro).pack()
   
   
   
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        usuario = login_bd(email, password)

        if usuario:
            messagebox.showinfo("OK", f"Bienvenido {usuario[1]}")

            self.root.destroy()  # Cerramos la ventana de login

            app = App()          # Creamos la ventana principal
            app.mainloop()

        else:
            messagebox.showerror("Error", "Credenciales incorrectas")
    
    def abrir_registro(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Registro")
        ventana.geometry("300x250")

        tk.Label(ventana, text="Nombre").pack()
        nombre_entry = tk.Entry(ventana)
        nombre_entry.pack()

        tk.Label(ventana, text="Email").pack()
        email_entry = tk.Entry(ventana)
        email_entry.pack()

        tk.Label(ventana, text="Contraseña").pack()
        password_entry = tk.Entry(ventana, show="*")
        password_entry.pack()

        def registrar():
            nombre = nombre_entry.get()
            email = email_entry.get()
            password = password_entry.get()

            from usuario import agregar_usuario
            agregar_usuario(nombre, email, password)

            messagebox.showinfo("OK", "Usuario registrado")
            ventana.destroy()

        tk.Button(ventana, text="Crear cuenta", command=registrar).pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()