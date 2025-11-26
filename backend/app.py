from flask import Flask, render_template, request, jsonify
from backend.nlp.responder import obtener_datos_financieros
from backend.nlp.processor import procesar_intencion
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=os.path.join(FRONTEND_DIR)
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()
    mensaje = data.get("message", "")

    intencion, entities = procesar_intencion(mensaje)
    respuesta = obtener_datos_financieros(intencion, mensaje, entities=entities)

    return jsonify({"response": respuesta})

if __name__ == "__main__":
    app.run(debug=True)
