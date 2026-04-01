import tkinter as tk
from PIL import Image, ImageTk
import os

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuraciones de ventana
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        # Definimos el color verde (puedes usar "green" o un Hexadecimal más elegante)
        verde_corporativo = "#2E7D32" 
        self.configure(bg=verde_corporativo)
        
        # Opcional: Si quieres que el fondo sea transparente y NO verde, 
        # descomenta la siguiente línea:
        # self.attributes("-transparentcolor", verde_corporativo)

        # Dimensiones y centrado
        w, h = 450, 450
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Carga de imagen
        ruta = os.path.join(os.path.dirname(__file__), "logo.png")
        try:
            # Abrimos y redimensionamos
            img = Image.open(ruta).convert("RGBA")
            img = img.resize((400, 400), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            
            # El Label DEBE tener el mismo fondo que la ventana para que no se vea el borde
            self.label = tk.Label(self, image=self.photo, bg=verde_corporativo, bd=0)
            self.label.pack(expand=True)
        except Exception as e:
            print(f"No se pudo cargar la imagen: {e}")
            tk.Label(
                self, 
                text="SmartKitchen\nCargando...", 
                fg="white", 
                bg=verde_corporativo, 
                font=("Arial", 20, "bold")
            ).pack(expand=True)

        self.update()
        # Usamos destroy directamente para cerrar la ventana tras 2 segundos
        self.after(2000, self.destroy)

        
if __name__ == "__main__":
    # PASO A: Splash
    splash = SplashScreen()
    splash.mainloop()

    # PASO B: Base de Datos
    try:
        from acceso_base_datos import crear_tablas
        crear_tablas()
    except Exception as e:
        print(f"Error BD: {e}")

    # PASO C: Login
    from login import LoginApp
    root = tk.Tk()
    app = LoginApp(root) 
    root.mainloop()