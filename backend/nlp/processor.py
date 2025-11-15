import spacy
from difflib import get_close_matches

nlp = spacy.load("es_core_news_md")

# Diccionario simple
INTENT_KEYWORDS = {
    "saludo": ["hola", "buenas", "buenos", "hey"],
    "criptomoneda": ["bitcoin", "btc", "cripto", "criptomonedas", "ethereum"],
    "acciones": ["acción", "acciones", "bolsa", "cedear", "mercado"],
    "plazo_fijo": ["plazo fijo", "plazofijo", "plazo"],
    "cuenta_remunerada": ["cuenta remunerada", "cuentas remuneradas", "cuentas"],
    "dolar": ["dolar", "dólar", "usd"],
    "riesgo_pais": ["riesgo país", "riesgo pais", "riesgo"],
    "riesgo_pais_historico": ["riesgo país histórico", "riesgo pais historico", "riesgo histórico", "historico", "histórico"],
    "inflacion": ["inflacion", "inflación", "ipc", "inflación mensual"],
    "inflacion_interanual": ["interanual", "inflación interanual", "inflacion interanual"],
    "uva": ["uva", "valor uva", "índice uva", "indice uva"],
    "inicio": ["inicio", "menu", "menú", "volver"]
}

def _keyword_intent(mensaje):
    texto = mensaje.lower()
    for intent, keys in INTENT_KEYWORDS.items():
        for k in keys:
            if k in texto:
                return intent

    tokens = [t.lemma_.lower() for t in nlp(texto) if not t.is_stop and t.is_alpha]
    flat_keys = [k for keys in INTENT_KEYWORDS.values() for k in keys]
    for tok in tokens:
        close = get_close_matches(tok, flat_keys, n=1, cutoff=0.8)
        if close:
            for intent, keys in INTENT_KEYWORDS.items():
                if close[0] in keys:
                    return intent
    return None

def procesar_texto(mensaje, context=None):
    """
    Retorna (intent, entities)
    entities: dict por ejemplo {"FECHA": "2025-09-30", "PERIODO": "interanual"}
    """
    if not mensaje:
        return "desconocido", {}

    doc = nlp(mensaje)
    entities = {}

    for ent in doc.ents:
        if ent.label_ in ("DATE", "FECHA"):
            entities.setdefault("FECHA", []).append(ent.text)
        elif ent.label_ in ("PERCENT", "PORCENTAJE"):
            entities.setdefault("PORCENTAJE", []).append(ent.text)
        else:
            entities.setdefault(ent.label_, []).append(ent.text)

    # Intent por reconocimiento semántico simple
    best_intent = None
    best_score = 0.0
    for intent, keys in INTENT_KEYWORDS.items():
        for k in keys:
            score = nlp(k).similarity(doc)
            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score < 0.65:
        kw_intent = _keyword_intent(mensaje)
        if kw_intent:
            best_intent = kw_intent

    if not best_intent:
        if context and context.get("last_intent"):
            best_intent = context.get("last_intent")
        else:
            best_intent = "desconocido"

    return best_intent, entities