from flask import Flask, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# CONFIGURACIÓN DE FLASK Y BASE DE DATOS
app = Flask(__name__, template_folder="../frontend", static_folder="../frontend")

# Configuración de conexión a MySQL
# CREATE DATABASE chatbot_finanzas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/chatbot_finanzas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización del ORM
db = SQLAlchemy(app)


# MODELOS DE BASE DE DATOS
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    chat_id = db.Column(db.String(50), unique=True)
    preferencias = db.Column(db.String(200))


# RUTA PRINCIPAL
@app.route("/")
def home():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"))
    with open(path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return render_template_string(html_content)


# RUTA PARA RECIBIR MENSAJES DEL CHAT
@app.route("/send_message", methods=["POST"])
def send_message():
    """
    Recibe el mensaje del usuario (vía fetch/AJAX) y devuelve la respuesta del chatbot.
    """
    user_message = request.json.get("message")
    print(" Mensaje recibido:", user_message)
    bot_response = procesar_mensaje_finanzas(user_message)
    return jsonify({"response": bot_response})


# LÓGICA BÁSICA DEL CHATBOT FINANCIERO
def procesar_mensaje_finanzas(mensaje):
    mensaje = mensaje.lower()

    if "hola" in mensaje:
        return "¡Hola! Soy tu asistente financiero 🤖. ¿Querés saber sobre acciones, criptomonedas o plazos fijos?"
    elif "bitcoin" in mensaje or "btc" in mensaje:
        return "Actualmente el Bitcoin ronda los $67,000 (valor aproximado)."
    elif "acciones" in mensaje:
        return "Podés consultar el estado de acciones, CEDEARs o índices. Pronto te mostraré datos en tiempo real 📈."
    elif "plazo fijo" in mensaje:
        return "La tasa promedio del plazo fijo ronda el 70% TNA. ¿Querés que calcule tus ganancias?"
    else:
        return "No entendí muy bien 🤔. Probá preguntarme por criptomonedas, acciones o tasas de inversión."


# INICIO DEL SERVIDOR
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # crea las tablas si no existen
    print("✅ Base de datos conectada y tablas listas.")
    print("🚀 Servidor ejecutándose en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
