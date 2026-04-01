import tkinter as tk
from PIL import Image, ImageTk
import os

# ==========================================
# 🖼️ 1. CLASE SPLASH SCREEN (Aislada)
# ==========================================
class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="black")
        
        # Centrar
        w, h = 450, 450
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Imagen
        ruta = os.path.join(os.path.dirname(__file__), "logo.png")
        try:
            img = Image.open(ruta).resize((400, 400), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.photo, bg="black", bd=0).pack(expand=True)
        except:
            tk.Label(self, text="SmartKitchen\nCargando...", fg="white", bg="black", font=("Arial", 20)).pack(expand=True)

        self.update()
        # Se cierra solo en 3 segundos
        self.after(2000, self.destroy)

# ==========================================
# 🚀 2. FLUJO PRINCIPAL DE EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    # PASO A: El Splash es lo primero
    print("Lanzando Splash...")
    splash = SplashScreen()
    splash.mainloop()

    # PASO B: Ahora sí, cargamos la base de datos
    print("Verificando base de datos...")
    from acceso_base_datos import crear_tablas
    crear_tablas()

    # PASO C: Cargamos el Login
    print("Iniciando Login...")
    from login import LoginApp
    
    root = tk.Tk()
    # Importante: Asegúrate de que LoginApp acepte 'root' como argumento
    app = LoginApp(root) 
    root.mainloop()