import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="DIAMOND v46 - API ELITE", layout="wide")

# Estilos Neón Gold
st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: #0a0a0a; border: 1px solid #ffd700; padding: 20px; 
        border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.1);
    }
    .value-alert { background: #1b4332; color: #74c69d; padding: 10px; border-radius: 8px; font-weight: bold; border: 1px solid #2d6a4f; margin-top: 10px; }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS (API-FOOTBALL) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS = {
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "La Liga 🇪🇸": 140, "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, "Ligue 1 🇫🇷": 61, "Liga 1 🇵🇪": 281,
    "Champions League 🇪🇺": 2, "Europa League 🇪🇺": 3, "Primeira Liga 🇵🇹": 94
}

def obtener_partidos(id_liga):
    params = {"league": id_liga, "next": 12, "season": 2025}
    try:
        res = requests.get(URL, headers=HEADERS, params=params, timeout=12).json()
        return res.get('response', [])
    except:
        return []

def motor_diamond(m, fatiga, lesion):
    # Lógica de Poder
    giants = ["Man City", "Real Madrid", "Bayern", "PSG", "Inter", "Arsenal", "Barcelona", "Liverpool", "Alianza Lima", "Universitario"]
    
    p_h = 2.2 if m['teams']['home']['name'] in giants else 1.4
    p_a = 1.2 if m['teams']['away']['name'] in giants else 0.8
    
    # Aplicación de variables externas
    if fatiga: p_h *= 0.85 
    if lesion: p_h *= 0.75
    
    score_h = max(0, round(p_h + random.uniform(-0.1, 0.4)))
    score_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    
    is_value = (p_h - p_a) > 1.3
    return {"score": f"{score_h} - {score_a}", "corners": "9.5+", "value": is_value}

# --- INTERFAZ PRINCIPAL ---
st.sidebar.title("💎 DIAMOND v46")
liga_sel = st.sidebar.selectbox("LIGAS MASTER", list(LIGAS.keys()))

if st.sidebar.button("🚀 SINCRONIZAR API"):
    with st.spinner("Conectando con Servidores Oficiales..."):
        st.session_state['v46_api'] = obtener_partidos(LIGAS[liga_sel])

if 'v46_api' in st.session_state:
    partidos = st.session_state['v46_api']
    if not partidos:
        st.error("No se encontraron partidos. Verifica si la temporada 2025 ha comenzado para esta liga.")
    else:
        st.success(f"📈 {len(partidos)} partidos listos para análisis.")
        for i, p in enumerate(partidos):
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h3 style='margin:0;'>{p['teams']['home']['name']}</h3>
                        <span style='color:#ffd700; font-weight:bold;'>VS</span>
                        <h3 style='margin:0;'>{p['teams']['away']['name']}</h3>
                    </div>
                    <p style='text-align:center; font-size:0.8em; margin-top:10px; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name']}</p>
                </div>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1: f = st.toggle("Factor Fatiga", key=f"f_{i}")
                with c2: l = st.toggle("Baja Estrella", key=f"l_{i}")
                with c3:
                    if st.button("💎 ANALIZAR", key=f"b_{i}"):
                        res = motor_diamond(p, f, l)
                        st.markdown(f"""
                            <div style='background:#111; padding:20px; border-radius:15px; border-left:5px solid #ffd700;'>
                                <h2 style='color:#ffd700; margin:0;'>🎯 {res['score']}</h2>
                                <p style='margin:0;'>🚩 Corners: {res['corners']}</p>
                                {f"<div class='value-alert'>🔥 ALERTA DE VALOR: Alta Confianza</div>" if res['value'] else ""}
                            </div>
                        """, unsafe_allow_html=True)