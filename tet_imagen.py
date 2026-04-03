import tkinter as tk
from PIL import Image, ImageTk
import os

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("400x400")
        self.configure(bg="black")

        # Intentar cargar la imagen
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        ruta = os.path.join(dir_actual, "logo.jpeg")
        
        print(f"Buscando en: {ruta}")

        try:
            img = Image.open(ruta).resize((300, 300))
            self.photo = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.photo, bg="black").pack(expand=True)
            print("✅ Imagen cargada")
        except:
            tk.Label(self, text="DEBUG SPLASH", fg="white", bg="black").pack(expand=True)
            print("❌ Imagen no encontrada, usando texto")

        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 200
        self.geometry(f"400x400+{x}+{y}")
        
        self.after(4000, self.destroy)

if __name__ == "__main__":
    print("--- INICIANDO PRUEBA AISLADA ---")
    app = SplashScreen()
    app.mainloop()
    print("--- PRUEBA FINALIZADA ---")