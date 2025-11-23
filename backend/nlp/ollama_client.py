import json
import requests
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/chat"

def normalizar_fecha(f):
    if not f:
        return None
    try:
        return datetime.strptime(f.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        return None

def consultar_ollama(mensaje, historial=None):
    historial = historial or []

    payload = {
        "model": "llama3.2:3b",
        "messages": historial + [
            {"role": "user", "content": mensaje}
        ],
        "stream": False,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "buscar_dato_financiero",
                    "description": "Devuelve datos financieros actuales o históricos.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "consulta": {"type": "string"},
                            "fecha": {"type": "string"}
                        },
                        "required": ["consulta"]
                    }
                }
            }
        ]
    }

    response = requests.post(OLLAMA_URL, json=payload)
    data = response.json()

    # Respuesta normal (sin Tools)
    message = data.get("message")
    if not message:
        return "No pude generar una respuesta en este momento."

    if "tool_calls" not in message:
        return message.get("content", "No pude interpretar la respuesta del modelo.")

    # Aplica Tools
    tool = message["tool_calls"][0]
    args_raw = tool["function"].get("arguments", {})

    try:
        args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
    except:
        args = {}

    consulta = args.get("consulta", "").lower()
    fecha = normalizar_fecha(args.get("fecha"))

    # Import APIs existentes
    from data.financial_api import (
        obtener_top5_criptos,
        obtener_top5_acciones,
        obtener_cotizaciones_dolar,
        obtener_historico_dolar,
        obtener_riesgo_pais,
        obtener_riesgo_pais_historico,
        obtener_indice_inflacion,
        obtener_indice_inflacion_interanual,
        obtener_indice_uva
    )

    if "cripto" in consulta:
        resultado = obtener_top5_criptos()

    elif "acción" in consulta or "acciones" in consulta:
        resultado = obtener_top5_acciones()

    elif "dólar" in consulta or "dolar" in consulta:
        if fecha:
            resultado = [f"No tengo datos históricos del dólar para la fecha {fecha}."]
        else:
            resultado = obtener_cotizaciones_dolar()

    elif "riesgo" in consulta:
        if fecha:
            fechas, valores = obtener_riesgo_pais_historico()
            if fechas and fecha in fechas:
                idx = fechas.index(fecha)
                resultado = [f"Riesgo País del {fecha}: {valores[idx]} puntos"]
            else:
                resultado = [f"No hay datos históricos del Riesgo País para {fecha}."]
        else:
            dato = obtener_riesgo_pais()
            if dato:
                resultado = [f"Riesgo País actual: {dato['valor']} puntos (Actualizado: {dato['fecha']})"]
            else:
                resultado = ["No pude obtener el valor actual del Riesgo País."]

    elif "inflación" in consulta and "inter" not in consulta:
        fechas, valores, ultimo = obtener_indice_inflacion()
        if fecha:
            if fecha in fechas:
                idx = fechas.index(fecha)
                resultado = [f"Inflación mensual en {fecha}: {valores[idx]}%"]
            else:
                resultado = [f"No hay datos de inflación mensual para {fecha}."]
        else:
            resultado = [f"Última inflación mensual ({ultimo['fecha']}): {ultimo['valor']}%"]

    elif "interanual" in consulta:
        fechas, valores, ultimo = obtener_indice_inflacion_interanual()
        if fecha:
            if fecha in fechas:
                idx = fechas.index(fecha)
                resultado = [f"Inflación interanual en {fecha}: {valores[idx]}%"]
            else:
                resultado = [f"No hay datos de inflación interanual para {fecha}."]
        else:
            resultado = [f"Última inflación interanual ({ultimo['fecha']}): {ultimo['valor']}%"]

    elif "uva" in consulta:
        fechas, valores, ultimo = obtener_indice_uva()
        if fecha:
            if fecha in fechas:
                idx = fechas.index(fecha)
                resultado = [f"Valor de UVA en {fecha}: ${valores[idx]:.2f}"]
            else:
                resultado = [f"No hay datos del índice UVA para {fecha}."]
        else:
            resultado = [f"Último valor UVA ({ultimo['fecha']}): ${ultimo['valor']:.2f}"]

    else:
        resultado = ["No entendí qué dato financiero querés consultar."]

    # Enviar datos al modelo
    final_payload = {
        "model": "llama3.2:3b",
        "messages": [
            *payload["messages"],
            {
                "role": "tool",
                "content": json.dumps(resultado, ensure_ascii=False),
                "tool_call_id": tool["id"]
            }
        ],
        "stream": False
    }

    final = requests.post(OLLAMA_URL, json=final_payload).json()
    return final.get("message", {}).get("content", "No pude generar una respuesta final.")