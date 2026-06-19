import requests
import certifi
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
import yfinance as yf

load_dotenv()
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": COINGECKO_API_KEY
}

def obtener_tasas_plazofijo():
    url = "https://api.argentinadatos.com/v1/finanzas/tasas/plazoFijo"

    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        print(f"📄 Contenido recibido: {response.text}")
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            print("⚠️ La respuesta no es una lista. Estructura inesperada.")
            return [], []

        # Filtrar y ordenar tasas de clientes
        clientes = [item for item in data if isinstance(item.get("tnaClientes"), (int, float))]
        clientes = sorted(clientes, key=lambda x: x["tnaClientes"], reverse=True)

        no_clientes = [item for item in data if isinstance(item.get("tnaNoClientes"), (int, float))]
        no_clientes = sorted(no_clientes, key=lambda x: x["tnaNoClientes"], reverse=True)

        top_clientes = [
            {"banco": item["entidad"], "tasa": item["tnaClientes"]}
            for item in clientes[:5]
            if item.get("tnaClientes") is not None
        ]
        top_no_clientes = [
            {"banco": item["entidad"], "tasa": item["tnaNoClientes"]}
            for item in no_clientes[:5]
            if item.get("tnaNoClientes") is not None
        ]

        return top_clientes, top_no_clientes

    except Exception as e:
        print(f"⚠️ Error al obtener tasas de ArgentinaDatos: {e}")
        return [], []

def obtener_top5_acciones():
    tickers = {
        "ALUA.BA": "Aluar",
        "BBAR.BA": "BBVA Argentina",
        "BMA.BA": "Banco Macro",
        "BYMA.BA": "BYMA",
        "CEPU.BA": "Central Puerto",
        "COME.BA": "Comercial del Plata",
        "CRES.BA": "Cresud",
        "CVH.BA": "Cablevisión",
        "EDN.BA": "Edenor",
        "GGAL.BA": "Grupo Galicia",
        "HARG.BA": "Holcim Argentina",
        "LOMA.BA": "Loma Negra",
        "METR.BA": "Metrogas",
        "MIRG.BA": "Mirgor",
        "MOLI.BA": "Molinos",
        "PAMP.BA": "Pampa Energía",
        "SUPV.BA": "Supervielle",
        "TECO2.BA": "Telecom",
        "TGNO4.BA": "TGN",
        "TGSU2.BA": "TGS",
        "TRAN.BA": "Transener",
        "TXAR.BA": "Ternium",
        "YPFD.BA": "YPF"
    }

    acciones = []

    for ticker, nombre in tickers.items():

        try:

            data = yf.Ticker(ticker).history(period="5d")

            if len(data) < 2:
                continue

            precio_actual = float(data["Close"].iloc[-1])
            precio_anterior = float(data["Close"].iloc[-2])

            variacion = (
                (precio_actual - precio_anterior)
                / precio_anterior
            ) * 100

            acciones.append({
                "nombre": nombre,
                "ticker": ticker.replace(".BA", ""),
                "precio": precio_actual,
                "variacion": variacion
            })

        except Exception as e:
            print(f"⚠️ Error en {ticker}: {e}")

    try:

        merval = yf.Ticker("^MERV")
        hist = merval.history(period="5d")

        merval_actual = float(hist["Close"].iloc[-1])
        merval_anterior = float(hist["Close"].iloc[-2])

        variacion_merval = (
            (merval_actual - merval_anterior)
            / merval_anterior
        ) * 100

    except Exception as e:

        print(f"⚠️ Error obteniendo MERVAL: {e}")

        merval_actual = 0
        variacion_merval = 0

    top_subas = sorted(
        acciones,
        key=lambda x: x["variacion"],
        reverse=True
    )[:5]

    top_bajas = sorted(
        acciones,
        key=lambda x: x["variacion"]
    )[:5]

    return {
        "fecha": datetime.now(),
        "merval": merval_actual,
        "variacion_merval": variacion_merval,
        "subas": top_subas,
        "bajas": top_bajas
    }


def obtener_top5_criptos():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": "false"
    }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        criptos = []

        stablecoins_excluidas = [
            "usdt",
            "usdc",
            "usds",
            "dai",
        ]

        for coin in data:
            if coin["symbol"].lower() in stablecoins_excluidas:
                continue

            criptos.append({
                "nombre": coin["name"],
                "simbolo": coin["symbol"].upper(),
                "precio": coin["current_price"],
                "variacion": coin.get("price_change_percentage_24h", 0) or 0
            })

            if len(criptos) == 5:
                break

        return criptos
    except Exception as e:
        return [f"Error al obtener datos de criptomonedas: {e}"]

def obtener_listado_criptos():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": "false"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Ordenar alfabéticamente
        data_sorted = sorted(data, key=lambda x: x['name'].lower())

        stablecoins_excluidas = [
            "usdt",
            "usdc",
            "usds",
            "dai",
        ]

        data_filtrada = [
            coin for coin in data
            if coin["symbol"].lower() not in stablecoins_excluidas
        ]

        data_sorted = sorted(
            data_filtrada,
            key=lambda x: x["name"].lower()
        )

        criptos = []

        for coin in data_sorted:
            criptos.append({
                "nombre": coin["name"],
                "simbolo": coin["symbol"].upper(),
                "precio": coin["current_price"],
                "variacion": coin.get("price_change_percentage_24h", 0) or 0
            })

        return criptos
    except Exception as e:
        return [f"Error al obtener listado de criptomonedas: {e}"]
    
def obtener_cuentas_remuneradas():
    url = "https://api.argentinadatos.com/v1/finanzas/fci/otros/ultimo"

    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or len(data) == 0:
            return []

        cuentas = []
        for item in data:
            tna = item.get("tna")

            if tna is None:
                continue

            cuentas.append({
                "entidad": item.get("fondo", "Entidad desconocida"),
                "tna": float(tna),
                "tope": item.get("tope")
            })

        cuentas_ordenadas = sorted(
            cuentas,
            key=lambda x: x["tna"],
            reverse=True
        )

        return cuentas_ordenadas[:5]

    except Exception as e:
        print(f"⚠️ Error al obtener cuentas remuneradas: {e}")
        return []

def obtener_cotizaciones_dolar():
    url = "https://dolarapi.com/v1/ambito/dolares"
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        cotizaciones = []
        for d in data:
            nombre = d.get("nombre", "Desconocido")
            compra = d.get("compra")
            venta = d.get("venta")
            fecha = d.get("fechaActualizacion", "")

            # Formateo de fecha
            try:
                fecha_dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
                fecha_formateada = fecha_dt.strftime("%Y-%m-%d, %H:%M:%S")
            except Exception:
                fecha_formateada = fecha

            # Si es Dólar Tarjeta, no mostrar valor compra
            if "tarjeta" in nombre.lower():
                compra = " ---"

            cotizaciones.append({
                "nombre": nombre,
                "compra": compra,
                "venta": venta,
                "fechaActualizacion": fecha_formateada
            })

        return cotizaciones

    except Exception as e:
        print(f"⚠️ Error al obtener cotizaciones del dólar: {e}")
        return []
    
def obtener_historico_dolares_todos():
    tipos = ["oficial", "blue", "bolsa", "ccl", "solidario", "tarjeta", "cripto"]
    resultado = {}
    
    print("🔄 Descargando históricos de todos los dólares...")
    
    for t in tipos:
        # Reutilizamos tu función existente
        fechas, valores, _ = obtener_historico_dolar(t)
        
        if fechas and valores:
            resultado[t] = {
                "fechas": fechas,
                "valores": valores
            }
        else:
            # Si falla alguno, mandamos listas vacías para que no rompa el JS
            resultado[t] = {"fechas": [], "valores": []}
            
    return resultado

def obtener_historico_dolar(tipo="blue"):
    url = f"https://api.argentinadatos.com/v1/cotizaciones/dolares/{tipo}"

    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or len(data) == 0:
            return [], [], {}

        fechas = []
        valores = []

        for d in data:
            fecha = d.get("fecha")
            venta = d.get("venta")
            if fecha and isinstance(venta, (int, float)):
                fechas.append(fecha)
                valores.append(venta)

        ultimo_registro = data[-1]
        ultimo = {
            "fecha": ultimo_registro.get("fecha"),
            "compra": ultimo_registro.get("compra"),
            "venta": ultimo_registro.get("venta")
        }

        return fechas, valores, ultimo

    except Exception as e:
        print(f"⚠️ Error al obtener histórico del dólar ({tipo}): {e}")
        return [], [], {}


def obtener_riesgo_pais():
    url = "https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo"
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        fecha = data.get("fecha", "")
        valor = data.get("valor", "N/D")

        # Formateo de fecha
        try:
            fecha_dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
            fecha_formateada = fecha_dt.strftime("%Y-%m-%d, %H:%M:%S")
        except Exception:
                fecha_formateada = fecha

        return {
            "valor": valor,
            "fecha": fecha_formateada
        }

    except Exception as e:
        print(f"⚠️ Error al obtener Riesgo País: {e}")
        return None

def obtener_riesgo_pais_historico():
    url = "https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais"
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        fechas = [item.get("fecha") for item in data if "fecha" in item]
        valores = [item.get("valor") for item in data if "valor" in item]

        fechas_legibles = []
        for f in fechas:
            try:
                fecha_dt = datetime.fromisoformat(f.replace("Z", "+00:00"))
                fechas_legibles.append(fecha_dt.strftime("%Y-%m-%d"))
            except Exception:
                fechas_legibles.append(f)

        return fechas_legibles, valores

    except Exception as e:
        print(f"⚠️ Error al obtener Riesgo País histórico: {e}")
        return None, None


def obtener_indice_inflacion():
    url = "https://api.argentinadatos.com/v1/finanzas/indices/inflacion"
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        # Filtrar solo los registros válidos
        registros = [d for d in data if "fecha" in d and "valor" in d]
        registros_ordenados = sorted(registros, key=lambda x: x["fecha"])

        if not registros_ordenados:
            return None, None, None

        fechas = [r["fecha"] for r in registros_ordenados]
        valores = [r["valor"] for r in registros_ordenados]

        # Último dato
        ultimo = registros_ordenados[-1]
        fecha_ultima = ultimo["fecha"]
        valor_ultimo = ultimo["valor"]

        return fechas, valores, {"fecha": fecha_ultima, "valor": valor_ultimo}

    except Exception as e:
        print(f"⚠️ Error al obtener índice de inflación: {e}")
        return None, None, None

def obtener_indice_inflacion_interanual():
    url = "https://api.argentinadatos.com/v1/finanzas/indices/inflacionInteranual"
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        registros = [d for d in data if "fecha" in d and "valor" in d]
        registros_ordenados = sorted(registros, key=lambda x: x["fecha"])

        if not registros_ordenados:
            return None, None, None

        fechas = [r["fecha"] for r in registros_ordenados]
        valores = [r["valor"] for r in registros_ordenados]

        ultimo = registros_ordenados[-1]
        fecha_ultima = ultimo["fecha"]
        valor_ultimo = ultimo["valor"]

        return fechas, valores, {"fecha": fecha_ultima, "valor": valor_ultimo}

    except Exception as e:
        print(f"⚠️ Error al obtener índice de inflación interanual: {e}")
        return None, None, None

def obtener_indice_uva():
    url = "https://api.argentinadatos.com/v1/finanzas/indices/uva"
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        registros = [d for d in data if "fecha" in d and "valor" in d]
        registros_ordenados = sorted(registros, key=lambda x: x["fecha"])

        if not registros_ordenados:
            return None, None, None

        fechas = [r["fecha"] for r in registros_ordenados]
        valores = [r["valor"] for r in registros_ordenados]

        # Último dato
        ultimo = registros_ordenados[-1]
        fecha_ultima = ultimo["fecha"]
        valor_ultimo = ultimo["valor"]

        return fechas, valores, {"fecha": fecha_ultima, "valor": valor_ultimo}

    except Exception as e:
        print(f"⚠️ Error al obtener índice UVA: {e}")
        return None, None, None