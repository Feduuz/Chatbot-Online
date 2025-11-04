def procesar_texto(mensaje):
    mensaje = mensaje.lower()

    if any(palabra in mensaje for palabra in ["bitcoin", "btc", "cripto"]):
        return "criptomoneda"
    elif any(palabra in mensaje for palabra in ["acción", "acciones", "cedear", "bolsa"]):
        return "acciones"
    elif "plazo fijo" in mensaje or "plazos fijos" in mensaje:
        return "plazo_fijo"
    elif "hola" in mensaje or "buenas" in mensaje:
        return "saludo"
    elif "cuenta remunerada" in mensaje or "cuentas remuneradas" in mensaje:
        return "cuenta_remunerada"
    else:
        return "desconocido"
