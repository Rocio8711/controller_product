# Controller Product

Una app para llevar el control de lo que tienes en la cocina.

He creado esta aplicación porque llevar el inventario de un bar o incluso el de casa a veces es complicado.  
Con Controller Product puedes saber qué tienes, qué te falta y organizar tus recetas.

---

## ¿Qué puedes hacer con ella?

- **Controlar tus productos:** añade lo que compras, edita cantidades o elimina lo que no uses.  
- **Organizar recetas:** crea platos combinando los ingredientes que ya tienes en el sistema.  
- **Lista de la compra automática:** la app te dice qué productos están bajo mínimos.  
- **Enviar la lista al móvil:** puedes enviarte la lista de la compra por correo electrónico para tenerla en el móvil cuando vayas a la tienda.  
- **Modo oscuro:** para que no te canse la vista si la usas durante mucho tiempo.

---

## ¿Cómo está hecha? (por dentro)

El proyecto está dividido en partes para facilitar su mantenimiento:

- `main.py`: archivo principal que ejecuta la aplicación.  
- `grafica.py`: colores y estilos de la interfaz.  
- `mandar_email.py`: lógica para el envío de correos.  
- `config.py`: configuración del correo y credenciales.  
- `controllerproduct.db`: base de datos con los productos.

---

## Instalación

1. Descarga el código del repositorio.  
2. Crea la base de datos:
  -python init_db.py
(Opcional) Prueba con datos:
  -python datos_prueba.py
Ejecuta la app:
  -python main.py

Hecho por RMR con mucho café y paciencia.
