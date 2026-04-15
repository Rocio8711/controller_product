import tkinter as tk
from PIL import Image, ImageTk
import os

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuraciones de ventana
        #quitamos los bordes de la ventana y los botones de cerrar o minimizar para que parezca una pantalla de carga real
        self.overrideredirect(True)
        #hacemos que esta ventana se quede siempre por encima de todas las demás mientras carga
        self.attributes("-topmost", True)
        
        #elegimos un tono de verde para el fondo que represente nuestra marca
        verde_corporativo = "#2E7D32" 
        self.configure(bg=verde_corporativo)
        
        # Dimensiones y centrado
        #calculamos el centro de la pantalla del usuario para que el logo aparezca justo en el medio
        w, h = 450, 450
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Carga de imagen
        #buscamos la imagen del logo en nuestra carpeta de imagenes usando una ruta que funcione en cualquier ordenador
        ruta = os.path.join(os.path.dirname(__file__), ".\\imagenes\\logo.jpeg")
        try:
            # #abrimos el logo, lo pasamos a un formato y lo ajustamos al tamaño de nuestra ventana
            img = Image.open(ruta).convert("RGBA")
            img = img.resize((400, 400), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            
            #colocamos la imagen en una etiqueta sin bordes y con el mismo fondo verde para que quede bien integrada
            self.label = tk.Label(self, image=self.photo, bg=verde_corporativo, bd=0)
            self.label.pack(expand=True)

        except Exception as e:
            #si por algun motivo no encontramos la imagen o falla al cargar ponemos un texto de repuesto para no dejar la pantalla vacia
            print(f"No se pudo cargar la imagen: {e}")
            tk.Label(
                self, 
                text="Controller Product \nCargando...", 
                fg="white", 
                bg=verde_corporativo, 
                font=("Arial", 20, "bold")
            ).pack(expand=True)
        #forzamos la actualizacion visual y programamos que la ventana se destruya sola despues de dos segundos
        self.update()
        self.after(2000, self.destroy)

        
if __name__ == "__main__":
    #empezamos el programa lanzando primero la pantalla de presentacion
    splash = SplashScreen()
    splash.mainloop()

    #una vez que se quita el logo intentamos conectar con la base de datos y crear las tablas si no existen todavia
    try:
        from InicializacionBaseDatos.acceso_base_datos import crear_tablas
        crear_tablas()
    except Exception as e:
        print(f"Error BD: {e}")

    #cuando ya tenemos la base de datos lista abrimos la ventana de acceso para que el usuario pueda entrar
    from login import LoginApp
    root = tk.Tk()
    app = LoginApp(root) 
    root.mainloop()