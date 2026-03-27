from acceso_base_datos import crear_tablas
import tkinter as tk
from login import LoginApp


if __name__ == "__main__":
    crear_tablas()

    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()