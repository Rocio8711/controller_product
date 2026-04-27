import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header  # Esto es clave para las ñ en el asunto

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib

def enviar_lista_email(destinatario, productos, usuario_email, password):
    #preparamos el contenedor del mensaje indicando que vamos a enviar una versión visual en html
    mensaje = MIMEMultipart("alternative") # "alternative" permite enviar texto y HTML
    mensaje["From"] = usuario_email
    mensaje["To"] = destinatario
    #usamos header para que los caracteres especiales como la ñ o los emojis se vean bien en el asunto
    mensaje["Subject"] = Header("🛒 Tu Lista de la Compra", "utf-8")

    #recorremos la lista de productos y vamos montando las filas de la tabla una por una en formato html
    filas_html = ""
    for p in productos:
        filas_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #eee;">{p}</td>
        </tr>
        """

    #escribimos toda la estructura del correo con estilos css para que se vea modernillo
    html = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 10px; overflow: hidden; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <div style="background-color: #4CAF50; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">Lista de la Compra</h1>
            </div>
            <div style="padding: 20px;">
                <p>Hola, aquí tienes los productos pendientes de tu inventario:</p>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f2f2f2;">
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #4CAF50;">Producto y Cantidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_html}
                    </tbody>
                </table>
                <p style="margin-top: 25px; font-size: 12px; color: #888; text-align: center;">
                    Enviado automáticamente por <strong>Controller Product</strong>
                </p>
            </div>
        </div>
    </body>
    </html>
    """


    #convertimos el texto html que hemos fabricado en una pieza del mensaje con codificación utf-8
    parte_html = MIMEText(html, "html", "utf-8")
    mensaje.attach(parte_html)

    server = None
    try:
        #nos conectamos al servidor de gmail usando el puerto de seguridad y activamos el cifrado tls
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        #entramos con nuestra cuenta, enviamos el correo convertido a cadena de texto y avisamos de que todo ha ido bien
        server.login(usuario_email, password)
        server.sendmail(usuario_email, destinatario, mensaje.as_string())
        return True
    except Exception as e:
        #si algo falla durante la conexion o el envio mostramos el error por pantalla y devolvemos falso
        print(f"Error al enviar: {e}")
        return False
    finally:
        #cerramos la conexion con el servidor siempre, tanto si el envio ha funcionado como si no
        if server:
            try:
                server.quit()
            except:
                pass