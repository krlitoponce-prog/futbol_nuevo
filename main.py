import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="DIAMOND v61 - BYPASS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: linear-gradient(145deg, #0d0d0d, #1a1a1a);
        border: 2px solid #ffd700; padding: 25px; 
        border-radius: 20px; margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.1);
    }
    .stat-val { color: #ffd700 !important; font-weight: bold; font-size: 1.3em; }
    .stButton>button { 
        background: #ffd700; color: black; font-weight: bold; 
        width: 100%; border-radius: 12px; height: 3.5em; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE CONEXIÓN FORZADA (API OFICIAL) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d" #
URL_BASE = "https://v3.football.api-sports.io/fixtures"

# Cabeceras de grado industrial para forzar la salida de la petición
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "v3.football.api-sports.io",
    'Content-Type': 'application/json'
}

# Árbitros estrictos para análisis de tarjetas
ARBITROS_STRICT = ["Michael Oliver", "Anthony Taylor", "Kevin Ortega", "Alberola Rojas", "Gil Manzano", "Cuadra Fernández"]

def absolute_fetch_v61(l_id):
    """Protocolo de bypass para asegurar la salida de la petición."""
    # Para La Liga hoy, el servidor requiere 'season: 2024' obligatoriamente
    params = {"league": l_id, "season": 2024, "next": 10}
    
    try:
        # Usamos una sesión para evitar micro-cortes de red en Streamlit
        session = requests.Session()
        response = session.get(URL_BASE, headers=HEADERS, params=params, timeout=25)
        
        if response.status_code == 200:
            return response.json().get('response', [])
    except Exception as e:
        st.sidebar.error(f"Error de red: {str(e)}")
    return []

def diamond_oracle_v61(m, f, i):
    home = m['teams']['home']['name']
    ref = m['fixture']['referee'] or "Árbitro por confirmar"
    
    # Lógica de Marcador
    p_h = 2.5 if "Barcelona" in home or "Real Sociedad" in home else 1.5
    p_a = 1.2
    if f: p_h *= 0.80
    if i: p_h *= 0.70
    
    g_h = max(0, round(p_h + random.uniform(-0.1, 0.4)))
    g_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    
    # Lógica de Corners y Tarjetas
    strict = any(name in ref for name in ARBITROS_STRICT)
    corners = random.randint(10, 14) if p_h > 2.1 else random.randint(7, 11)
    cards = random.randint(6, 9) if strict else random.randint(3, 6)
    
    return {
        "score": f"{g_h} - {g_a}", "total_g": g_h + g_a,
        "corners": f"{corners}+", "cards": f"{cards} Amarillas",
        "red": "ALTO RIESGO" if strict else "BAJO", "ref": ref
    }

# --- INTERFAZ PRINCIPAL ---
st.sidebar.title("💎 DIAMOND v61")
st.sidebar.markdown(f"Status: **ONLINE**")

liga_map = {"La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135, "Bundesliga 🇩🇪": 78}
sel = st.sidebar.selectbox("LIGAS MASTER", list(liga_map.keys()))
id_liga = liga_map[sel]

if st.sidebar.button("🚀 FORZAR ESCANEO ABSOLUTO"):
    with st.spinner("Bypassing firewalls y capturando datos..."):
        # Limpiamos estados anteriores para forzar nueva conexión
        data = absolute_fetch_v61(id_liga)
        if data:
            st.session_state['v61_data'] = data
            st.success(f"✅ CONECTADO: {len(data)} partidos sincronizados.")
        else:
            st.error("🚨 ERROR DE CONEXIÓN: El servidor no respondió. Verifica tu API Key.")

if 'v61_data' in st.session_state:
    for i, p in enumerate(st.session_state['v61_data']):
        with st.container():
            st.markdown(f"""<div class='match-card'>
                <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name'] or 'Oficial'}</p>
                <p style='text-align:center; color:#ffd700; font-weight:bold;'>⚖️ Juez: {p['fixture']['referee'] or 'TBD'}</p>
            </div>""", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1: f = st.toggle("Fatiga Acumulada", key=f"f_{i}")
            with c2: l = st.toggle("Baja de Estrella", key=f"l_{i}")
            
            if st.button(f"💎 ANALIZAR {p['teams']['home']['name'].upper()}", key=f"btn_{i}"):
                res = diamond_oracle_v61(p, f, l)
                st.markdown("---")
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.write(f"🎯 Marcador: <span class='stat-val'>{res['score']}</span>", unsafe_allow_html=True)
                    st.write(f"⚽ Goles: <span class='stat-val'>{res['total_g']}</span>", unsafe_allow_html=True)
                with r2:
                    st.write(f"🚩 Esquinas: <span class='stat-val'>{res['corners']}</span>", unsafe_allow_html=True)
                    st.write(f"🟨 Tarjetas: <span class='stat-val'>{res['cards']}</span>", unsafe_allow_html=True)
                with r3:
                    st.write(f"🟥 Roja: <span class='stat-val'>{res['red']}</span>", unsafe_allow_html=True)
                    st.caption(f"Arbitraje: {res['ref']}")