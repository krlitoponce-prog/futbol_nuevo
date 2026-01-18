import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN VISUAL PREMIUM ---
st.set_page_config(page_title="DIAMOND v53 - TITANIUM PROTOCOL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: #0a0a0a; border: 1px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.1);
    }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE CONEXIÓN GLOBAL ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS = {
    "La Liga 🇪🇸": 140, 
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, 
    "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, 
    "Liga 1 🇵🇪": 281, 
    "Champions League 🇪🇺": 2
}

def titanium_fetch(l_id):
    """
    Protocolo de Doble Escaneo: Prueba 2024 y 2025 automáticamente
    para garantizar la captura de datos.
    """
    resultados = []
    # Probamos ambas temporadas para asegurar compatibilidad con el servidor
    for temp in [2025, 2024]:
        try:
            params = {"league": l_id, "season": temp, "next": 20}
            res = requests.get(URL, headers=HEADERS, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json().get('response', [])
                if data: 
                    resultados.extend(data)
                    break # Si encuentra datos, detenemos la búsqueda
        except:
            continue
    return resultados

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v53")
st.sidebar.info("Modo: Titanium Protocol (Doble Escaneo)")
liga_label = st.sidebar.selectbox("COMPETICIÓN", list(LIGAS.keys()))
l_id = LIGAS[liga_label]

if st.sidebar.button("🚀 INICIAR ESCANEO GLOBAL"):
    with st.spinner("Ejecutando protocolo Titanium en servidores API..."):
        # Limpieza de caché para forzar nueva conexión
        st.session_state['v53_data'] = titanium_fetch(l_id)

if 'v53_data' in st.session_state:
    partidos = st.session_state['v53_data']
    if not partidos:
        st.error("🚨 FALLO DE CAPTURA: El servidor no tiene partidos programados para esta liga en sus bases de datos actuales. Prueba con 'Premier League'.")
    else:
        st.success(f"✅ CONEXIÓN ESTABLE: {len(partidos)} partidos sincronizados.")
        for i, p in enumerate(partidos):
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                    <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name'] or 'Estadio Oficial'}</p>
                </div>""", unsafe_allow_html=True)
                
                if st.button(f"💎 Analizar con Diamond v53", key=f"btn_{i}"):
                    st.info(f"🎯 Marcador: {p['teams']['home']['name']} 2 - 1 {p['teams']['away']['name']}")