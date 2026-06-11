import streamlit as st
import requests
from typing import Dict, List, Any  #  Correcto

session = requests.Session()

# El caché ahora expira automáticamente cada hora (3600 segundos)
@st.cache_data(ttl=3600)
def obtener_clima(lat: float, lon: float) -> Dict[str, Any] | None:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"
    try:
        response = session.get(url, timeout=(3, 10))
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

@st.cache_data(ttl=3600)
def obtener_datos_pais(nombre_pais: str) -> Dict[str, Any] | None:
    url = f"https://restcountries.com/v3.1/name/{nombre_pais}?fullText=true"
    try:
        response = session.get(url, timeout=(3, 10))
        response.raise_for_status()
        
        # --- PARCHE DE SEGURIDAD 1 ---
        res_json = response.json()
        if isinstance(res_json, list) and len(res_json) > 0:
            return res_json[0]
        
        # Si llegó aquí, no es una lista válida. Forzamos ir al intento alternativo.
        raise requests.RequestException 

    except requests.RequestException:
        try:
            # Intento alternativo por si el nombre viene con formatos extraños
            url_alt = f"https://restcountries.com/v3.1/name/{nombre_pais}"
            response = session.get(url_alt, timeout=(3, 10))
            response.raise_for_status()
            
            # --- PARCHE DE SEGURIDAD 2 (Ya lo tenías casi listo aquí) ---
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                return res_json[0]
            return None
            
        except requests.RequestException:
            return None

@st.cache_data(ttl=3600)
def obtener_tasa_cambio(moneda_local: str) -> float | None:
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        response = session.get(url, timeout=(3, 10))
        response.raise_for_status()
        rates = response.json().get("rates", {})
        return rates.get(moneda_local, None)
    except requests.RequestException:
        return None

@st.cache_data(ttl=3600)
def obtener_lugares_interes(lat: float, lon: float) -> list[str]:
    url = f"https://es.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord={lat}|{lon}&gsradius=5000&gslimit=7&format=json"
    try:
        response = session.get(url, timeout=(3, 10))
        response.raise_for_status()
        res_json = response.json()
        if "query" in res_json and "geosearch" in res_json["query"]:
            return [lugar["title"] for lugar in res_json["query"]["geosearch"]]
    except requests.RequestException:
        return []
    return []