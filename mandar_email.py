import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header  # <--- Esto es clave para las ñ en el asunto

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib

def enviar_lista_email(destinatario, productos, usuario_email, password):
    mensaje = MIMEMultipart("alternative") # "alternative" permite enviar texto y HTML
    mensaje["From"] = usuario_email
    mensaje["To"] = destinatario
    mensaje["Subject"] = Header("🛒 Tu Lista de la Compra", "utf-8")

    # 1. Generamos las filas de la tabla dinámicamente
    filas_html = ""
    for p in productos:
        filas_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #eee;">{p}</td>
        </tr>
        """

    # 2. Creamos un diseño HTML con CSS integrado
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


    # Añadimos la versión HTML al mensaje
    parte_html = MIMEText(html, "html", "utf-8")
    mensaje.attach(parte_html)

    server = None
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(usuario_email, password)
        server.sendmail(usuario_email, destinatario, mensaje.as_string())
        return True
    except Exception as e:
        print(f"Error al enviar: {e}")
        return False
    finally:
        if server:
            try:
                server.quit()
            except:
                pass