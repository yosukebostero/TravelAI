import streamlit as st
import pandas as pd
import random
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai

# Importaciones de nuestros nuevos módulos limpios
from services.geo import obtener_coordenadas
from services.apis import (
    obtener_clima, 
    obtener_datos_pais, 
    obtener_tasa_cambio, 
    obtener_lugares_interes
)

# Configuración inicial de la página
st.set_page_config(
    page_title="TravelAI - Enterprise Edition",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales
st.markdown("""
    <style>
    .big-title { font-size:40px !important; font-weight: bold; color: #1E3A8A; }
    .subtitle { font-size:18px !important; color: #4B5563; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">✈️ TravelAI: Planificador de Viajes Inteligente</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Arquitectura paralela de alto rendimiento con copiloto adaptativo.</p>', unsafe_allow_html=True)

def emoji_clima(code: int) -> str:
    mapeo = {0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 51: "🌧️", 61: "🌧️", 71: "❄️", 95: "⛈️"}
    return mapeo.get(code, "🌤️")

# Generador de humor inteligente contextual basado en el estado del clima real
def obtener_comentario_climatico(code: int, temp_max: float) -> str:
    if code in [95]:
        return "Excelente elección. Nada dice vacaciones como sentir que Zeus te odia personalmente. ⛈️"
    elif temp_max > 35:
        return f"Con {temp_max}°C máximos... un escenario perfecto para descubrir nuevas formas de sudar. 🥵"
    elif code in [71] or temp_max < 5:
        return "Recuerda que el hielo es solo agua con malas intenciones. Abrígate. 🥶"
    elif code in [51, 61]:
        return "Espero que te guste el agua, porque tu destino va a parecer una piscina sin costo adicional. 🌧️"
    else:
        return "El clima se ve sospechosamente decente. Seguro tu aerolínea lo compensará perdiendo tus maletas. ✈️"

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración del Sistema")
    destino_input = st.text_input("Escribe tu destino:", placeholder="Ej: Roma, Berlín, Tokio...")
    st.write("---")
    st.subheader("🎭 Personalidad de la App")
    modo_sarcastico = st.checkbox("Activar Copiloto Sarcástico ✈️", value=True)
    st.write("---")
    st.caption("Estructura modular multiproceso 🐍.")

if destino_input:
    with st.spinner("🔄 Despertando a los servidores... dales un momento, no tomaron café hoy."):
        datos_destino = obtener_coordenadas(destino_input)
        
    if datos_destino:
        lat, lon = datos_destino["lat"], datos_destino["lon"]
        
        # 🔥 RETO DEL PROFE: Carga masiva paralela usando hilos concurrentes
        with st.spinner("⚡ Ejecutando peticiones HTTP concurrentes en paralelo..."):
            with ThreadPoolExecutor() as executor:
                futuro_clima = executor.submit(obtener_clima, lat, lon)
                futuro_pais = executor.submit(obtener_datos_pais, datos_destino["pais"])
                futuro_lugares = executor.submit(obtener_lugares_interes, lat, lon)
                
                # Extracción inmediata de los hilos resueltos
                clima = futuro_clima.result()
                info_pais = futuro_pais.result()
                lugares = futuro_lugares.result()
        
        # Configuración de variables del clima para el humor
        clima_ok = clima and "daily" in clima
        primer_codigo = clima["daily"]["weathercode"][0] if clima_ok else 0
        primera_temp = clima["daily"]["temperature_2m_max"][0] if clima_ok else 20.0
        
        # Renderizado de pestañas
        tab_resumen, tab_clima, tab_finanzas, tab_ia = st.tabs([
            "🗺️ Tablero de Ubicación", 
            "🌦️ Clima de la Semana", 
            "💱 Datos del País y Moneda", 
            "🤖 Itinerario Experto IA"
        ])
        
        # --- PESTAÑA 1: MAPA Y PUNTOS DE INTERÉS ---
        with tab_resumen:
            col_mapa, col_puntos = st.columns([2, 1])
            with col_mapa:
                st.subheader("📍 Ubicación Geográfica")
                df_mapa = pd.DataFrame({"lat": [lat], "lon": [lon]})
                st.map(df_mapa, zoom=12, use_container_width=True)
            
            with col_puntos:
                st.subheader("🏛️ Lugares Cercanos")
                st.caption("Puntos destacados según Wikipedia en un radio de 5km:")
                if lugares:
                    for l in lugares:
                        st.markdown(f"- 📍 **{l}**")
                else:
                    st.write("No encontramos nada indexado cerca. Un desierto cultural absoluto.")

        # --- PESTAÑA 2: PRONÓSTICO AVANZADO ---
        with tab_clima:
            st.subheader("📅 Pronóstico Meteorológico para 5 Días")
            if clima_ok:
                dias = clima["daily"]["time"][:5]
                maxs = clima["daily"]["temperature_2m_max"][:5]
                mins = clima["daily"]["temperature_2m_min"][:5]
                codes = clima["daily"]["weathercode"][:5]
                
                cols = st.columns(5)
                for i in range(5):
                    with cols[i]:
                        st.container(border=True).metric(
                            label=f"📆 {dias[i]}",
                            value=f"{emoji_clima(codes[i])} {maxs[i]}°C",
                            delta=f"Mín: {mins[i]}°C",
                            delta_color="inverse"
                        )
            else:
                st.error("Error al conectar con el satélite meteorológico. Probablemente chocó con un ave.")

        # --- PESTAÑA 3: DATOS DEL PAÍS Y CONVERSOR ---
        with tab_finanzas:
            if info_pais:
                col_pais, col_money = st.columns(2)
                with col_pais:
                    st.subheader(f"ℹ️ Información de {datos_destino['pais']}")
                    st.image(info_pais["flags"]["png"], width=180)
                    st.write(f"🏛️ **Capital:** {info_pais.get('capital', ['No aplica'])[0]}")
                    st.write(f"👥 **Población:** {info_pais.get('population', 0):,}")
                    st.write(f"🌍 **Región:** {info_pais.get('region', 'N/A')} ({info_pais.get('subregion', 'N/A')})")
                
                with col_money:
                    st.subheader("💱 Conversor de Divisas en Vivo")
                    curr_code = list(info_pais["currencies"].keys())[0]
                    curr_info = info_pais["currencies"][curr_code]
                    st.info(f"Moneda oficial: **{curr_info['name']}** (`{curr_code}` - {curr_info.get('symbol', '')})")
                    
                    tasa = obtener_tasa_cambio(curr_code)
                    if tasa:
                        st.metric(label=f"1 USD equivale a:", value=f"{tasa:,.2f} {curr_code}")
                        dolares = st.number_input("Monto en Dólares (USD):", min_value=1.0, value=100.0, step=10.0)
                        conversion = dolares * tasa
                        st.success(f"💰 {dolares:,} USD = **{conversion:,.2f} {curr_code}**")
                    else:
                        st.warning("No se pudo obtener el tipo de cambio. Asume que todo está carísimo.")
            else:
                st.error("No se pudieron emparejar los datos internacionales de este lugar.")

        # --- PESTAÑA 4: ITINERARIO CON IA ---
        with tab_ia:
            st.subheader("🤖 Planificación de Itinerario Inteligente")
            
            # 💀 Puntuación de Supervivencia Turística
            indice_supervivencia = random.randint(40, 100)
            
            # 1. Configurar textos y prompts según el modo (Sin meter lógica de API aquí adentro)
            if modo_sarcastico:
                comentario_clima = obtener_comentario_climatico(primer_codigo, primera_temp)
                st.warning(f"💥 **Copiloto dice:** {comentario_clima}")
                
                st.metric(
                    label="💀 Puntuación de Supervivencia Turística™",
                    value=f"{indice_supervivencia}%",
                    delta="Riesgo de pérdida de equipaje: Alto" if indice_supervivencia < 75 else "Milagrosamente seguro"
                )
                
                texto_boton = "Generar Itinerario (Sin llorar si hay retrasos)"
                prompt_final = (
                    f"Actúa como un guía turístico experto pero profundamente cansado de lidiar con turistas. "
                    f"Crea un itinerario de 3 días para {destino_input}. Integra de forma ácida ironías sobre "
                    f"retrasos en aeropuertos, escalas interminables, el clima actual que es de {primera_temp}°C y maletas perdidas. "
                    f"Usa emojis, negritas y organízalo por Mañana, Tarde y Noche."
                )
            else:
                st.info("Copiloto corporativo listo para aburrirte.")
                st.metric(label="📊 Índice de Seguridad Estándar", value=f"{indice_supervivencia}%")
                texto_boton = "Generar Itinerario Profesional"
                prompt_final = f"Crea un itinerario de viaje detallado y profesional de 3 días para {destino_input}. Organízalo por Mañana, Tarde y Noche."

            st.write("---") # Una línea divisoria estética

            # 2. CONTROL DE API KEY UNIFICADO (Solo se escribe una vez aquí abajo)
            import os
            api_key_lista = False
            api_key_actual = ""

            # Bypass silencioso de archivos para Streamlit
            dir_secrets = ".streamlit"
            archivo_secrets = os.path.join(dir_secrets, "secrets.toml")
            if not os.path.exists(dir_secrets):
                os.makedirs(dir_secrets)
            if not os.path.exists(archivo_secrets):
                with open(archivo_secrets, "w", encoding="utf-8") as f:
                    f.write("# Calmando berrinches de Streamlit\n")

            try:
                if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                    if st.secrets["GEMINI_API_KEY"].strip() != "":
                        api_key_actual = st.secrets["GEMINI_API_KEY"]
                        api_key_lista = True
            except Exception:
                pass

            # Si no hay clave en secretos, se muestra la interfaz interactiva una sola vez
            if not api_key_lista:
                st.error("🚨 **Si quieres que esta chatarra funcione pon tu API Key aquí, humano mortal:**")
                api_key_input = st.text_input(
                    "Introduce tu GEMINI_API_KEY:", 
                    type="password", 
                    placeholder="AIzaSy...",
                    label_visibility="collapsed",
                    key="input_api_key_usuario_unico"
                )
                
                if api_key_input:
                    api_key_actual = api_key_input
                    api_key_lista = True
                
                with st.expander("❓ ¿Qué? ¿No sabes cómo conseguirla, pequeño mono? Sólo sigue estos pasos:"):
                    st.markdown("""
    1. Entra arrastrando los pies a la [Groq Console](https://console.groq.com/).
    2. Inicia sesión rápido con tu cuenta de Google.
    3. En el menú de la izquierda, haz clic en **"API Keys"**.
    4. Presiona el botón **"Create API Key"**, dale cualquier nombre ridículo y copiala.
    5. Pégala aquí arriba. Empieza por `gsk_` y, a diferencia de otras IA corporativas orientadas al fracaso (Cof, Cof, Google), esta sí funciona al toque.
    """)
# 3. BOTÓN DE EJECUCIÓN (Único para toda la pestaña)
if st.button("✈️ ¡Despegar Itinerario Cínico!"): 
                if api_key_lista:
                    with st.spinner("🤖 Invocando al motor de IA ultra-veloz..."):
                        try:
                            import requests
                            import json

                            # Cambiamos al endpoint oficial de Groq (¡Adiós Google y tus berrinches!)
                            url_groq = "https://api.groq.com/openai/v1/chat/completions"
                            
                            headers = {
                                "Authorization": f"Bearer {api_key_actual}",
                                "Content-Type": "application/json"
                            }
                            
                            # Usamos un modelo potente, rápido y totalmente libre de bloqueos
                            payload = {
                                "model": "llama-3.3-70b-versatile",
                                "messages": [
                                    {"role": "user", "content": prompt_final}
                                ],
                                "temperature": 0.8
                            }

                            # Disparamos directo
                            response_api = requests.post(url_groq, headers=headers, json=payload, timeout=30)
                            
                            if response_api.status_code == 200:
                                datos_ia = response_api.json()
                                # Extraemos la respuesta en formato estándar
                                texto_generado = datos_ia["choices"][0]["message"]["content"]
                                st.markdown(texto_generado)
                            else:
                                st.error(f"Error del servidor alternativo (Código {response_api.status_code}): {response_api.text}")
                                
                        except Exception as e:
                            st.error(f"El puente de conexión colapsó, humano mortal. Error: {e}")
                else:
                    st.error("¡Bloqueo de seguridad! No puedo invocar a la IA sin combustible energético (la API Key).")