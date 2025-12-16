import re

def procesar_intencion(mensaje):
    msg = mensaje.lower().strip()

    reglas = {
        "criptomoneda": ["cripto", "bitcoin", "ethereum", "criptomonedas" ,"btc"],
        "acciones": ["acción", "acciones", "stocks", "mercado" ,"bolsa"],
        "cuenta_remunerada": ["cuenta remunerada", "cuentas remuneradas", "remunerada"],
        "plazo_fijo": ["plazo fijo", "plazofijo", "plazo", "plazos fijos"],
        "dolar": ["dólar hoy", "dólar", "dolar", "usd"],
        "dolar_historico": ["histórico dólar", "dolar histórico", "gráfico dólar", "usd histórico"],
        "inflacion": ["inflacion", "inflación", "ipc", "inflación mensual"],
        "interanual": ["interanual", "inflación interanual", "inflacion interanual"],
        "uva": ["uva", "valor uva", "índice uva", "indice uva"],
        "riesgo_pais": ["riesgo país", "riesgo pais", "riesgo"],
        "riesgo_pais_historico": ["riesgo país histórico", "riesgo pais historico", "riesgo histórico"],
        "inicio": ["inicio", "menu"],
    }

    for intent, keywords in reglas.items():
        if any(k in msg for k in keywords):
            return intent, {}

    return "desconocido", {}
