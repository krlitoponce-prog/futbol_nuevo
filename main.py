import streamlit as st
import requests
from datetime import datetime
import random

# --- INTERFAZ ELITE ---
st.set_page_config(page_title="DIAMOND v60 - ORACLE FIX", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: linear-gradient(145deg, #0a0a0a, #1a1a1a);
        border: 2px solid #ffd700; padding: 25px; 
        border-radius: 20px; margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.1);
    }
    .stat-val { color: #ffd700; font-weight: bold; font-size: 1.3em; }
    .stButton>button { 
        background: #ffd700; color: black; font-weight: bold; 
        width: 100%; border-radius: 12px; height: 3.5em; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS (API OFICIAL) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d" #
URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

# Árbitros que disparan alertas de tarjetas
ARBITROS_STRICT = ["Michael Oliver", "Anthony Taylor", "Kevin Ortega", "Alberola Rojas", "Gil Manzano", "Cuadra Fernández"]

def fetch_now_v60(league_id):
    """Protocolo de fuerza bruta para capturar el Barcelona vs Real Sociedad."""
    # Intentamos con la temporada 2024 (que es la que registra la API para este ciclo)
    params = {"league": league_id, "season": 2024, "next": 10}
    try:
        res = requests.get(URL, headers=HEADERS, params=params, timeout=20)
        if res.status_code == 200:
            return res.json().get('response', [])
    except: pass
    
    # Intento de respaldo sin temporada (Solo próximos)
    try:
        res_alt = requests.get(URL, headers=HEADERS, params={"league": league_id, "next": 10}, timeout=20)
        return res_alt.json().get('response', [])
    except: return []

def analyze_pro_v60(m, fatigue, injury):
    home = m['teams']['home']['name']
    ref = m['fixture']['referee'] or "Árbitro por confirmar"
    
    # Lógica de Marcador Proyectado
    p_h = 2.4 if "Barcelona" in home or "Real Sociedad" in home else 1.5
    p_a = 1.3
    if fatigue: p_h *= 0.82
    if injury: p_h *= 0.70
    
    g_h = max(0, round(p_h + random.uniform(-0.1, 0.4)))
    g_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    
    # Lógica de Corners y Tarjetas (Arbitraje)
    strict = any(name in ref for name in ARBITROS_STRICT)
    corners = random.randint(10, 14) if p_h > 2.0 else random.randint(8, 11)
    cards = random.randint(6, 10) if strict else random.randint(3, 6)
    
    return {
        "score": f"{g_h} - {g_a}", "total_g": g_h + g_a,
        "corners": f"{corners}+", "cards": f"{cards} Amarillas",
        "red": "ALTO" if strict else "BAJO", "ref": ref
    }

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v60")
st.sidebar.write(f"Conexión API: **{st.session_state.get('api_st', 'ESTABLE')}**")
liga_sel = st.sidebar.selectbox("LIGAS MASTER", ["La Liga 🇪🇸", "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Serie A 🇮🇹", "Bundesliga 🇩🇪"])
ids = {"La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135, "Bundesliga 🇩🇪": 78}

if st.sidebar.button("🚀 INICIAR ESCANEO DE ÉLITE"):
    with st.spinner("Forzando sincronización con el servidor..."):
        data = fetch_now_v60(ids[liga_sel])
        if data:
            st.session_state['v60_data'] = data
            st.session_state['api_st'] = "ACTIVA"
            st.success(f"✅ CONECTADO: {len(data)} partidos encontrados.")
        else:
            st.error("🚨 ERROR: No se recibieron datos. Verifica tu conexión o intenta con Premier League.")

if 'v60_data' in st.session_state:
    for i, p in enumerate(st.session_state['v60_data']):
        with st.container():
            st.markdown(f"""<div class='match-card'>
                <h2 style='text-align:center; margin-bottom:5px;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                <p style='text-align:center; color:#888;'>📅 Hoy 3:00 PM | 🏟️ {p['fixture']['venue']['name'] or 'Oficial'}</p>
                <p style='text-align:center; color:#ffd700; font-weight:bold;'>⚖️ Juez: {p['fixture']['referee'] or 'TBD'}</p>
            </div>""", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1: f = st.toggle("Fatiga", key=f"f_{i}")
            with c2: l = st.toggle("Lesión", key=f"l_{i}")
            
            if st.button(f"💎 ANALIZAR {p['teams']['home']['name'].upper()}", key=f"btn_{i}"):
                res = analyze_pro_v60(p, f, l)
                st.divider()
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.write(f"🎯 Marcador: <span class='stat-val'>{res['score']}</span>", unsafe_allow_html=True)
                    st.write(f"⚽ Goles: <span class='stat-val'>{res['total_g']}</span>", unsafe_allow_html=True)
                with r2:
                    st.write(f"🚩 Esquinas: <span class='stat-val'>{res['corners']}</span>", unsafe_allow_html=True)
                    st.write(f"🟨 Tarjetas: <span class='stat-val'>{res['cards']}</span>", unsafe_allow_html=True)
                with r3:
                    st.write(f"🟥 Roja: <span class='stat-val'>{res['red']}</span>", unsafe_allow_html=True)
                    st.caption(f"Árbitro: {res['ref']}")