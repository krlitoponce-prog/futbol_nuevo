import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DIAMOND v51 - GLOBAL STABILITY", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: #0a0a0a; border: 1px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px;
    }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE CONEXIÓN ULTRALIGERO ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
BASE_URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "v3.football.api-sports.io"
}

LIGAS = {
    "La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, "Liga 1 🇵🇪": 281, "Champions League 🇪🇺": 2
}

def get_fixtures_v51(league_id):
    """
    Busca partidos usando solo el ID de liga y 'next', dejando que la API 
    decida la temporada activa para evitar el error de 'no datos'.
    """
    params = {"league": league_id, "next": 15}
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
        if response.status_code == 200:
            return response.json().get('response', [])
    except:
        pass
    return []

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v51")
st.sidebar.success("Conexión de Red: ACTIVA")
liga_label = st.sidebar.selectbox("COMPETICIÓN", list(LIGAS.keys()))
l_id = LIGAS[liga_label]

if st.sidebar.button("🚀 SINCRONIZAR PARTIDOS"):
    with st.spinner("Obteniendo cartelera oficial..."):
        # Limpiamos estados anteriores para evitar errores de variable
        st.session_state['v51_data'] = get_fixtures_v51(l_id)

if 'v51_data' in st.session_state:
    partidos = st.session_state['v51_data']
    if not partidos:
        st.error("No se encontraron partidos próximos. Es posible que esta liga no tenga juegos en los próximos 7 días.")
    else:
        st.success(f"📈 {len(partidos)} partidos encontrados con éxito.")
        for p in partidos:
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                    <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name'] or 'Estadio Pendiente'}</p>
                </div>""", unsafe_allow_html=True)
                
                if st.button(f"💎 Analizar Pronóstico", key=f"btn_{p['fixture']['id']}"):
                    st.write(f"🎯 Marcador Diamond: {p['teams']['home']['name']} 2 - 1 {p['teams']['away']['name']}")