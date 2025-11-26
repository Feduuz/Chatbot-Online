import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
Sos un asistente financiero argentino.
Respondé de forma concisa, clara, sin inventar datos y basándote solo
en lo que el usuario pregunta. No inventes números, remítete siempre
a la información provista por las funciones del backend.
"""

def consultar_groq(mensaje):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mensaje}
            ],
            temperature=0.2,
            max_tokens=500
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error al consultar Groq API: {e}"
