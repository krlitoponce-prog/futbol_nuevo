import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="DIAMOND v67 - RECONSTRUCTION", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: #0d0d0d; border: 2px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px;
    }
    .stat-box { background: #1a1a1a; padding: 10px; border-radius: 8px; border-left: 4px solid #ffd700; }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 10px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE CONEXIÓN ESTÁNDAR (API-FOOTBALL) ---
# Usamos tu clave confirmada: 48782dd5dcf6d4d9083eabc821da5e2d
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "v3.football.api-sports.io",
    'User-Agent': 'Mozilla/5.0'
}

def conectar_api_limpia(league_id):
    """
    Intenta conectar con los parámetros mínimos necesarios 
    para asegurar que el contador de la API se mueva.
    """
    # Intentamos obtener los próximos 15 partidos de la liga seleccionada
    params = {"league": league_id, "next": 15}
    try:
        response = requests.get(URL, headers=HEADERS, params=params, timeout=20)
        if response.status_code == 200:
            return response.json().get('response', [])
    except Exception as e:
        st.sidebar.error(f"Error de red: {e}")
    return []

# --- INTERFAZ DE USUARIO ---
st.sidebar.title("💎 DIAMOND v67")
st.sidebar.write(f"Contador API actual: **{st.session_state.get('last_count', 6)}/100**")

ligas = {
    "La Liga 🇪🇸": 140,
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39,
    "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78
}

seleccion = st.sidebar.selectbox("SELECCIONAR COMPETICIÓN", list(ligas.keys()))
id_liga = ligas[seleccion]

if st.sidebar.button("🚀 PROBAR CONEXIÓN Y CARGAR"):
    with st.spinner("Estableciendo enlace con el servidor oficial..."):
        # Limpiamos resultados previos
        if 'v67_data' in st.session_state: del st.session_state['v67_data']
        
        data = conectar_api_limpia(id_liga)
        if data:
            st.session_state['v67_data'] = data
            st.session_state['last_count'] = st.session_state.get('last_count', 6) + 1
            st.success(f"✅ CONEXIÓN EXITOSA: {len(data)} partidos encontrados.")
        else:
            st.error("La API no devolvió datos. Verifica si la temporada está activa o prueba con otra liga.")

# --- VISUALIZACIÓN DE RESULTADOS ---
if 'v67_data' in st.session_state:
    for i, p in enumerate(st.session_state['v67_data']):
        with st.container():
            st.markdown(f"""<div class='match-card'>
                <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name'] or 'Oficial'}</p>
                <p style='text-align:center; font-weight:bold; color:#ffd700;'>⚖️ Árbitro: {p['fixture']['referee'] or 'TBD'}</p>
            </div>""", unsafe_allow_html=True)
            
            if st.button(f"💎 ANALIZAR {p['teams']['home']['name'].upper()}", key=f"btn_{i}"):
                # Análisis de ejemplo (Esto se potenciará una vez conecte)
                st.info("Proyectando Marcador, Corners y Tarjetas...")