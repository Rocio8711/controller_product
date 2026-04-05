import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header  # <--- Esto es clave para las ñ en el asunto

def enviar_lista_email(destinatario, productos, usuario_email, password):
    mensaje = MIMEMultipart()
    mensaje["From"] = usuario_email
    mensaje["To"] = destinatario
    
    # Usamos Header para que el Asunto soporte caracteres especiales
    mensaje["Subject"] = Header("Mi Lista de la Compra - Controller Product", "utf-8")

    cuerpo = "Aquí tienes tu lista de la compra actualizada:\n\n"
    for p in productos:
        cuerpo += f"• {p}\n"

    # Cuerpo en utf-8
    texto = MIMEText(cuerpo, "plain", "utf-8")
    mensaje.attach(texto)

    server = None
    try:
        # Configuración para Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(usuario_email, password)
        # Usamos as_string() para asegurar la codificación final
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