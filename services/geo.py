import requests
from typing import Dict, Any  #  Correcto

# Sesión reutilizable para mejorar la eficiencia de las conexiones
session = requests.Session()

def obtener_coordenadas(destino: str) -> dict[str, any] | None:
    url = f"https://nominatim.openstreetmap.org/search?q={destino}&format=json&limit=1"
    headers = {"User-Agent": "TravelAI_App/3.0"}
    
    try:
        # Tupla de timeout: 3 segundos para conectar, 10 para recibir respuesta
        response = session.get(url, headers=headers, timeout=(3, 10))
        response.raise_for_status()
        
        data = response.json()
        if data:
            first_result = data[0]
            partes = first_result["display_name"].split(",")
            pais = partes[-1].strip()
            return {
                "lat": float(first_result["lat"]),
                "lon": float(first_result["lon"]),
                "nombre": first_result["display_name"],
                "pais": pais
            }
    except requests.RequestException:
        return None
    return None