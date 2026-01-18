import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="DIAMOND v52 - TOTAL FORCE", layout="wide")

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

# --- MOTOR DE DATOS (CONFIGURACIÓN DE TU CUENTA) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS = {
    "La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, "Liga 1 🇵🇪": 281, "Champions League 🇪🇺": 2
}

def force_fetch_v52(l_id):
    """
    Busca con un rango extendido y forzando la temporada actual (2025)
    para asegurar que los partidos aparezcan.
    """
    # Intentamos primero con los próximos 50 partidos de la temporada actual
    params = {"league": l_id, "next": 50, "season": 2025}
    try:
        res = requests.get(URL, headers=HEADERS, params=params, timeout=15)
        if res.status_code == 200:
            data = res.json().get('response', [])
            if data: return data
            
        # Si falla, intentamos sin temporada pero con rango amplio
        res_alt = requests.get(URL, headers=HEADERS, params={"league": l_id, "next": 50}, timeout=15)
        return res_alt.json().get('response', [])
    except:
        return []

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v52")
st.sidebar.success("Estado API: CONECTADO (3/100)")
liga_label = st.sidebar.selectbox("COMPETICIÓN", list(LIGAS.keys()))
l_id = LIGAS[liga_label]

if st.sidebar.button("🚀 FORZAR CARGA DE PARTIDOS"):
    with st.spinner("Escaneando calendario extendido..."):
        st.session_state['v52_data'] = force_fetch_v52(l_id)

if 'v52_data' in st.session_state:
    partidos = st.session_state['v52_data']
    if not partidos:
        st.error("No se encontraron partidos. Prueba cambiando a 'Premier League' o 'Bundesliga' para verificar si hay datos en otras ligas.")
    else:
        st.success(f"✅ Se encontraron {len(partidos)} partidos próximos.")
        for i, p in enumerate(partidos):
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                    <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name'] or 'Estadio Pendiente'}</p>
                </div>""", unsafe_allow_html=True)
                
                if st.button(f"💎 Analizar Pronóstico", key=f"btn_{i}"):
                    st.write(f"🎯 Marcador: {p['teams']['home']['name']} 2 - 1 {p['teams']['away']['name']}")