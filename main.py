import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="DIAMOND v47 - H2H & ODDS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .match-card { 
        background: #0a0a0a; border: 1px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px;
    }
    .odds-box { background: #111; padding: 10px; border-radius: 8px; border: 1px dashed #ffd700; text-align: center; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS (API-FOOTBALL) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
BASE_URL = "https://v3.football.api-sports.io/"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS = {
    "La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, "Liga 1 🇵🇪": 281, "Champions League 🇪🇺": 2
}

def obtener_datos(endpoint, params):
    try:
        res = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params, timeout=15).json()
        return res.get('response', [])
    except:
        return []

def motor_diamond(m, fatiga, lesion):
    # Lógica de Poder Proyectado
    p_h = 2.2 if "Barcelona" in m['teams']['home']['name'] or "Madrid" in m['teams']['home']['name'] else 1.4
    p_a = 1.1
    
    if fatiga: p_h *= 0.85
    if lesion: p_h *= 0.75
    
    score_h = max(0, round(p_h + random.uniform(-0.1, 0.4)))
    score_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    
    return {"score": f"{score_h} - {score_a}", "value": (p_h - p_a) > 1.2}

# --- UI PRINCIPAL ---
st.sidebar.title("💎 DIAMOND v47")
liga_sel = st.sidebar.selectbox("COMPETICIÓN", list(LIGAS.keys()))

if st.sidebar.button("🚀 SINCRONIZAR CARTELERA"):
    # Buscamos los próximos 20 partidos de la temporada actual (2025)
    st.session_state['v47_api'] = obtener_datos("fixtures", {"league": LIGAS[liga_sel], "next": 20, "season": 2025})

if 'v47_api' in st.session_state:
    partidos = st.session_state['v47_api']
    if not partidos:
        st.error("No se encontraron partidos. Verifica tu límite de API diario o intenta con temporada 2025.")
    else:
        for i, p in enumerate(partidos):
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                    <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name']}</p>
                </div>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1: 
                    fatiga = st.toggle("Fatiga", key=f"f_{i}")
                    lesion = st.toggle("Baja", key=f"l_{i}")
                with c2:
                    if st.button("📊 VER H2H / ODDS", key=f"h2h_{i}"):
                        h2h = obtener_datos("fixtures/headtohead", {"h2h": f"{p['teams']['home']['id']}-{p['teams']['away']['id']}", "last": 5})
                        st.write("**Últimos Enfrentamientos:**")
                        for match in h2h:
                            st.caption(f"📅 {match['fixture']['date'][:10]}: {match['goals']['home']} - {match['goals']['away']}")
                with c3:
                    if st.button("💎 ANALIZAR", key=f"b_{i}"):
                        res = motor_diamond(p, fatiga, lesion)
                        st.subheader(f"🎯 {res['score']}")
                        if res['value']: st.warning("🔥 ALERTA DE VALOR")