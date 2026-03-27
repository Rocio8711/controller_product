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

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        usuario = login_bd(email, password)

        if usuario:
            messagebox.showinfo("OK", f"Bienvenido {usuario[1]}")

            self.root.destroy()

            root = tk.Tk()
            App(root)
            root.mainloop()

        else:
            messagebox.showerror("Error", "Credenciales incorrectas")


if __name__ == "__main__":
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()