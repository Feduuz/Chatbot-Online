import json
from data.financial_api import (
    obtener_top5_criptos,
    obtener_listado_criptos,
    obtener_tasas_plazofijo,
    obtener_top5_acciones,
    obtener_listado_acciones,
    obtener_cuentas_remuneradas,
    obtener_cotizaciones_dolar,
    obtener_historico_dolar,
    obtener_riesgo_pais,
    obtener_riesgo_pais_historico,
    obtener_indice_inflacion,
    obtener_indice_inflacion_interanual,
    obtener_indice_uva
)

def _agregar_boton_inicio(respuesta_actual):
    return respuesta_actual + """
        <div class='button-options'>
            <button class='option-btn' data-intent='Inicio'>Inicio 🏠</button>
        </div>
    """

def obtener_datos_financieros(intencion, mensaje, context=None, entities=None):
    mensaje = mensaje.lower()
    entities = entities or {}
    respuesta = ""

    if intencion == "saludo":
        return "Un gusto. ¿Sobre qué tema te gustaría saber más?"

    elif intencion == "criptomoneda":
        top5 = obtener_top5_criptos()
        respuesta = "<b>💰 Las 5 criptomonedas con mayor capitalización son:</b><br><br>"
        for i, cripto in enumerate(top5, start=1):
            respuesta += f"{i}° {cripto}<br>"


    elif intencion == "acciones":
        top5 = obtener_top5_acciones()
        respuesta = "<b>📈 Las 5 acciones con mayor capitalización son:</b><br><br>"
        for i, accion in enumerate(top5, start=1):
            respuesta += f"{i}° {accion}<br>"


    elif intencion == "plazo_fijo":
        top_clientes, top_no_clientes = obtener_tasas_plazofijo()
        if not top_clientes and not top_no_clientes:
            return "⚠️ No pude obtener las tasas de plazo fijo en este momento. Probá más tarde."

        respuesta = "<b>🏦 Top 5 Tasas de Plazo Fijo más altas (según el BCRA):</b><br><br>"
        if top_clientes:
            respuesta += "<b>👤 **Para Clientes:**</b><br>"
            for i, t in enumerate(top_clientes, start=1):
                respuesta += f"{i}° {t['banco']}: TNA {t['tasa']:.2f}%<br>"

        respuesta += "<br><hr><br>"

        if top_no_clientes:
            respuesta += "<b>🚫 **Para No Clientes:**</b><br>"
            for i, t in enumerate(top_no_clientes, start=1):
                respuesta += f"{i}° {t['banco']}: TNA {t['tasa']:.2f}%<br>"


    elif intencion == "cuenta_remunerada":
        cuentas = obtener_cuentas_remuneradas()
        if not cuentas:
            return "⚠️ No pude obtener los datos de cuentas remuneradas en este momento."

        respuesta = "<b>💵 Top 5 Cuentas Remuneradas (según ArgentinaDatos):</b><br><br>"
        for i, c in enumerate(cuentas, start=1):
            respuesta += f"{i}° <b>{c['entidad']}</b><br>"
            respuesta += f"🏦 TNA: {c['tna']}%<br>"
            tope = c['tope'] if c['tope'] not in [None, "None", "", 0] else " --- "
            respuesta += f"💰 Tope: ${tope}<br><br>"


    elif intencion == "dolar":
        cotizaciones = obtener_cotizaciones_dolar()
        if not cotizaciones:
            return "⚠️ No pude obtener las cotizaciones del dólar en este momento."

        respuesta = "<b>💵 Cotizaciones del Dólar (Fuente Ámbito Financiero):</b><br><br>"

        for c in cotizaciones:
            respuesta += f"<b>Dólar {c['nombre']}</b><br>"
            respuesta += f"🟢 Compra: ${c['compra']}<br>"
            respuesta += f"🔴 Venta: ${c['venta']}<br>"
            respuesta += f"🕒 Última actualización: {c['fechaActualizacion']}<br><br>"
        """
                <div class='button-options'>
            <button class='option-btn' data-intent='Dolar historico'>Dólar Histórico 💰</button>
        </div>          
        """

    elif intencion == "dolar_historico":
        from data.financial_api import obtener_historico_dolares_todos

        historicos = obtener_historico_dolares_todos()

        if not historicos:
            return "⚠️ No pude obtener los datos históricos del dólar."

        # Por defecto mostrar “oficial”
        tipo = "oficial"
        datos = historicos[tipo]

        respuesta = f"""
        <b>📈 Histórico del Dólar</b><br><br>

        <label><b>Elige tipo de dólar:</b></label><br>
        <select id='tipoDolarSelect' class='option-btn' style='margin-top:10px;'>
            <option value='oficial'>Oficial</option>
            <option value='blue'>Blue</option>
            <option value='bolsa'>Bolsa</option>
            <option value='ccl'>CCL</option>
            <option value='solidario'>Solidario</option>
            <option value='tarjeta'>Tarjeta</option>
            <option value='cripto'>Cripto</option>
            <option value='mayorista'>Mayorista</option>
        </select>

        <br><br>

        <canvas id='dolarChart' width='900' height='350'></canvas>

        <script>
            const historicosDolar = {json.dumps(historicos)};

            function renderChartDolar(tipo) {{
                const datos = historicosDolar[tipo];

                if (!datos) return;

                const fechas = datos.fechas;
                const valores = datos.valores;

                const ctx = document.getElementById('dolarChart').getContext('2d');

                if (window.dolarChart) {{
                    try {{ window.dolarChart.destroy(); }} catch (e) {{}}
                }}

                Chart.register(window['chartjs-plugin-zoom']);

                window.dolarChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: fechas,
                        datasets: [{{
                            label: 'Dólar ' + tipo.toUpperCase(),
                            data: valores,
                            borderColor: '#00ff99',
                            backgroundColor: 'rgba(0,255,153,0.2)',
                            fill: true,
                            tension: 0.3
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            zoom: {{
                                zoom: {{
                                    wheel: {{ enabled: true }},
                                    pinch: {{ enabled: true }},
                                    mode: 'x'
                                }},
                                pan: {{
                                    enabled: true,
                                    mode: 'x'
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            renderChartDolar('oficial');

            // Cambiar el gráfico SIN enviar mensajes
            document.getElementById('tipoDolarSelect').addEventListener('change', (e) => {{
                const tipo = e.target.value;
                renderChartDolar(tipo);
            }});
        </script>
        """

        return _agregar_boton_inicio(respuesta)


    elif intencion == "riesgo_pais":
        datos = obtener_riesgo_pais()
        if not datos:
            return "⚠️ No pude obtener el valor del Riesgo País en este momento."

        respuesta = "<b>📊 Índice de Riesgo País (Argentina)</b><br><br>"
        respuesta += f"🇦🇷 Valor actual: <b>{datos['valor']}</b> puntos<br>"
        respuesta += f"🕒 Última actualización: {datos['fecha']}<br>"

        respuesta += """
        <div class='button-options'>
            <button class='option-btn' data-intent='Historico'>Histórico 📈</button>
        </div>
        """


    elif intencion == "riesgo_pais_historico":
        datos = obtener_riesgo_pais()
        fechas, valores = obtener_riesgo_pais_historico()

        if not datos or not fechas:
            return "⚠️ No pude obtener los datos del Riesgo País en este momento."

        respuesta = "<b>📊 Índice de Riesgo País (Argentina)</b><br><br>"
        respuesta += f"🇦🇷 Valor actual: <b>{datos['valor']}</b> puntos<br>"
        respuesta += f"🕒 Última actualización: {datos['fecha']}<br><br>"
        respuesta += "📈 Evolución histórica:<br>"
        respuesta += "<canvas id='riesgoPaisChart' width='900' height='350'></canvas>"

        respuesta += f"""

        <script>
            if (!Chart.registry.plugins.get('zoom')) {{
                Chart.register(window['chartjs-plugin-zoom']);
            }}

            const ctx3 = document.getElementById('riesgoPaisChart').getContext('2d');
            window.riesgoPaisChart = new Chart(ctx3, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(fechas)},
                    datasets: [{{
                        label: 'Riesgo País (puntos)',
                        data: {json.dumps(valores)},
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.2)',
                        tension: 0.3,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        x: {{
                            ticks: {{ color: '#ccc' }},
                            grid: {{ display: false }}
                        }},
                        y: {{
                            ticks: {{ color: '#ccc' }},
                            grid: {{ color: 'rgba(255,255,255,0.1)' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#ccc' }}
                        }},
                        zoom: {{
                            pan: {{
                                enabled: true,
                                mode: 'x'
                            }},
                            zoom: {{
                                wheel: {{ enabled: true }},
                                pinch: {{ enabled: true }},
                                mode: 'x'
                            }},
                            limits: {{
                                x: {{ minRange: 6 }}
                            }}
                        }}
                    }}
                }}
            }});
        </script>
        """


    elif intencion == "inflacion":
        fechas, valores, ultimo = obtener_indice_inflacion()
        if not fechas:
            return "⚠️ No pude obtener los datos de inflación mensual."

        respuesta = "<b>📉 Índice de Inflación Mensual (Argentina)</b><br><br>"
        respuesta += f"📆 Último dato: <b>{ultimo['fecha']}</b><br>"
        respuesta += f"💸 Inflación: <b>{ultimo['valor']}%</b><br><br>"
        respuesta += "📊 Evolución histórica:<br>"
        respuesta += "<canvas id='inflacionChart' width='900' height='350'></canvas>"

        respuesta += f"""

        <script>
            if (!Chart.registry.plugins.get('zoom')) {{
                Chart.register(window['chartjs-plugin-zoom']);
            }}

            const ctx = document.getElementById('inflacionChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(fechas)},
                    datasets: [{{
                        label: 'Inflación mensual (%)',
                        data: {json.dumps(valores)},
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.2)',
                        tension: 0.3,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        x: {{
                            ticks: {{ color: '#ccc' }},
                            grid: {{ display: false }}
                        }},
                        y: {{
                            ticks: {{ color: '#ccc' }},
                            grid: {{ color: 'rgba(255,255,255,0.1)' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#ccc' }}
                        }},
                        zoom: {{
                            pan: {{
                                enabled: true,
                                mode: 'x'
                            }},
                            zoom: {{
                                wheel: {{ enabled: true }},
                                pinch: {{ enabled: true }},
                                mode: 'x'
                            }},
                            limits: {{
                                x: {{ minRange: 6 }}
                            }}
                        }}
                    }}
                }}
            }});        
        </script>
        <div class='button-options'>
            <button class='option-btn' data-intent='Interanual'>Inflación Interanual 📅</button>
        </div>          
        """


    elif intencion == "inflacion interanual" or "interanual" in mensaje.lower():
        fechas, valores, ultimo = obtener_indice_inflacion_interanual()
        if not fechas:
            return "⚠️ No pude obtener los datos de inflación interanual."

        respuesta = "<b>📆 Índice de Inflación Interanual (Argentina)</b><br><br>"
        respuesta += f"📅 Último dato: <b>{ultimo['fecha']}</b><br>"
        respuesta += f"💸 Inflación Interanual: <b>{ultimo['valor']}%</b><br><br>"
        respuesta += "📊 Evolución histórica:<br>"
        respuesta += "<canvas id='inflacionInteranualChart' width='900' height='350'></canvas>"

        respuesta += f"""

        <script>
            if (!Chart.registry.plugins.get('zoom')) {{
                Chart.register(window['chartjs-plugin-zoom']);
            }}

            const ctx2 = document.getElementById('inflacionInteranualChart').getContext('2d');
            new Chart(ctx2, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(fechas)},
                    datasets: [{{
                        label: 'Inflación interanual (%)',
                        data: {json.dumps(valores)},
                        borderColor: '#ff7f50',
                        backgroundColor: 'rgba(255, 127, 80, 0.2)',
                        tension: 0.3,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        x: {{
                            ticks: {{ color: '#ccc' }},
                            grid: {{ display: false }}
                        }},
                        y: {{
                            ticks: {{ color: '#ccc' }},
                            grid: {{ color: 'rgba(255,255,255,0.1)' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#ccc' }}
                        }},
                        zoom: {{
                            pan: {{
                                enabled: true,
                                mode: 'x'
                            }},
                            zoom: {{
                                wheel: {{ enabled: true }},
                                pinch: {{ enabled: true }},
                                mode: 'x'
                            }},
                            limits: {{
                                x: {{ minRange: 6 }}
                            }}
                        }}
                    }}
                }}
            }});
        </script>
        """


    elif intencion == "uva":
        fechas, valores, ultimo = obtener_indice_uva()
        if not fechas:
            return "⚠️ No pude obtener los datos del índice UVA en este momento."

        respuesta = "<b>🏠 Valor de la Unidad de Valor Adquisitivo (UVA)</b><br><br>"
        respuesta += f"📆 Último valor: <b>${ultimo['valor']:.2f}</b><br>"
        respuesta += f"📅 Fecha: <b>{ultimo['fecha']}</b><br><br>"
        respuesta += "📊 Evolución histórica:<br>"
        respuesta += "<canvas id='uvaChart' width='900' height='350'></canvas>"

        respuesta += f"""

        <script>
            if (!Chart.registry.plugins.get('zoom')) {{
                Chart.register(window['chartjs-plugin-zoom']);
            }}

            const ctxUVA = document.getElementById('uvaChart').getContext('2d');
            new Chart(ctxUVA, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(fechas)},
                    datasets: [{{
                        label: 'Valor UVA ($)',
                        data: {json.dumps(valores)},
                        borderColor: '#ffc107', // Color Amarillo/Ámbar
                        backgroundColor: 'rgba(255, 193, 7, 0.2)',
                        tension: 0.3,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        x: {{
                            ticks: {{ color: '#ccc' }},
                            grid: {{ display: false }}
                        }},
                        y: {{
                            ticks: {{ color: '#ccc' }},
                            grid: {{ color: 'rgba(255,255,255,0.1)' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#ccc' }}
                        }},
                        zoom: {{
                            pan: {{
                                enabled: true,
                                mode: 'x'
                            }},
                            zoom: {{
                                wheel: {{ enabled: true }},
                                pinch: {{ enabled: true }},
                                mode: 'x'
                            }},
                            limits: {{
                                x: {{ minRange: 6 }}
                            }}
                        }}
                    }}
                }}
            }});
        </script>
        """


    elif intencion == "inicio" or "inicios" in mensaje:
        respuesta = f"""
        <b>🏠 Menú principal</b><br><br>
        Seleccioná una categoría para explorar:<br><br>
        <div class='button-options'>
            <button class='option-btn' data-intent='Criptomoneda'>Criptomonedas 🪙</button>
            <button class='option-btn' data-intent='Acciones'>Acciones 📈</button>
            <button class='option-btn' data-intent='Plazo fijo'>Plazo Fijo 🏦</button>
            <button class='option-btn' data-intent='Cuenta remunerada'>Cuentas Remuneradas 💵</button>
            <button class='option-btn' data-intent='Dolar'>Dólar 💲</button>
            <button class='option-btn' data-intent='Dolar historico'>Dólar Histórico 💰</button>
            <button class='option-btn' data-intent='Riesgo pais'>Riesgo País 📊</button>
            <button class='option-btn' data-intent='Inflacion'>Inflación 📉</button>
            <button class='option-btn' data-intent='Uva'>Índice UVA 📅</button>
        </div>
        """
        return respuesta

    elif intencion == "desconocido":
        from nlp.ollama_client import consultar_ollama
        respuesta_llm = consultar_ollama(mensaje)
        return _agregar_boton_inicio(respuesta_llm)
    
    else:
        return _agregar_boton_inicio("Todavía no tengo información para esa consulta, pero pronto la agregaré 📊.")
    
    if respuesta and intencion != "saludo":
        respuesta = _agregar_boton_inicio(respuesta)
        
    return respuesta