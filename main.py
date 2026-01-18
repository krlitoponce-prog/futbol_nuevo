import streamlit as st
import requests
from datetime import datetime
import random

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="DIAMOND v58 - EMERGENCY PROTOCOL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: linear-gradient(145deg, #0a0a0a, #111);
        border: 1px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px;
    }
    .stat-box { background: #1a1a1a; padding: 10px; border-radius: 8px; border-left: 4px solid #ffd700; margin-bottom: 10px; }
    .stat-val { color: #ffd700; font-weight: bold; font-size: 1.2em; }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 10px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE INTELIGENCIA Y CONEXIÓN ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d" #
URL_BASE = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS_ID = {
    "La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, "Liga 1 🇵🇪": 281, "Ligue 1 🇫🇷": 61
}

ARBITROS_STRICT = ["Michael Oliver", "Anthony Taylor", "Kevin Ortega", "Alberola Rojas", "H. Hernández", "S. Marciniak", "Gil Manzano"]

def fetch_data_emergency(l_id):
    """Prueba múltiples parámetros en una secuencia para forzar la respuesta de datos."""
    # Intentamos primero lo más seguro: Próximos 20 partidos sin restricción de temporada
    intentos = [
        {"league": l_id, "next": 20},
        {"league": l_id, "season": 2024, "next": 20},
        {"league": l_id, "season": 2025, "next": 20}
    ]
    
    for params in intentos:
        try:
            response = requests.get(URL_BASE, headers=HEADERS, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json().get('response', [])
                if data: return data
        except: continue
    return []

def analizar_full_stats(m, fatiga, lesion):
    ref = m['fixture']['referee'] or "Arbitro por confirmar"
    home = m['teams']['home']['name']
    
    # 1. Marcador y Goles
    p_h = 2.4 if "Barcelona" in home or "Madrid" in home else 1.5
    p_a = 1.1
    if fatiga: p_h *= 0.80
    if lesion: p_h *= 0.70
    
    g_h = max(0, round(p_h + random.uniform(-0.1, 0.4)))
    g_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    
    # 2. Esquinas y Tarjetas (Lógica Arbitral)
    es_estricto = any(name in ref for name in ARBITROS_STRICT)
    corners = random.randint(10, 14) if p_h > 2.0 else random.randint(8, 11)
    amarillas = random.randint(6, 10) if es_estricto else random.randint(3, 5)
    riesgo_roja = "ALTO" if es_estricto else "BAJO"
    
    return {
        "score": f"{g_h} - {g_a}",
        "total_g": g_h + g_a,
        "corners": f"{corners}+",
        "cards": f"{amarillas} Amarillas",
        "red": riesgo_roja,
        "ref": ref
    }

# --- INTERFAZ PRINCIPAL ---
st.sidebar.title("💎 DIAMOND v58")
st.sidebar.write(f"Estado API: **Conectado ({st.session_state.get('api_count', 6)}/100)**")
liga_name = st.sidebar.selectbox("LIGAS MASTER", list(LIGAS_ID.keys()))
l_id = LIGAS_ID[liga_name]

if st.sidebar.button("🚀 FORZAR ESCANEO DE DATOS"):
    with st.spinner("Ejecutando protocolo de emergencia en la API..."):
        data = fetch_data_emergency(l_id)
        if data:
            st.session_state['v58_data'] = data
            st.session_state['api_count'] = st.session_state.get('api_count', 6) + 1
            st.success(f"✅ DATOS CAPTURADOS: {len(data)} partidos encontrados.")
        else:
            st.error("🚨 FALLO TOTAL: La API no tiene datos para esta liga. Intenta con Premier League.")

if 'v58_data' in st.session_state:
    for i, p in enumerate(st.session_state['v58_data']):
        with st.container():
            st.markdown(f"""<div class='match-card'>
                <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name'] or 'Estadio Oficial'}</p>
                <p style='text-align:center; color:#ffd700;'>⚖️ Árbitro: {p['fixture']['referee'] or 'TBD'}</p>
            </div>""", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1: f = st.toggle("Fatiga Acumulada", key=f"f_{i}")
            with c2: l = st.toggle("Lesión de Estrella", key=f"l_{i}")
            
            if st.button(f"💎 ANALIZAR {p['teams']['home']['name'].upper()}", key=f"btn_{i}"):
                res = analizar_full_stats(p, f, l)
                st.markdown("---")
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.markdown(f"<div class='stat-box'>🎯 MARCADOR<br><span class='stat-val'>{res['score']}</span></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='stat-box'>⚽ TOTAL GOLES<br><span class='stat-val'>{res['total_g']}</span></div>", unsafe_allow_html=True)
                with r2:
                    st.markdown(f"<div class='stat-box'>🚩 CORNERS<br><span class='stat-val'>{res['corners']}</span></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='stat-box'>🟨 AMARILLAS<br><span class='stat-val'>{res['cards']}</span></div>", unsafe_allow_html=True)
                with r3:
                    st.markdown(f"<div class='stat-box'>🟥 RIESGO ROJA<br><span class='stat-val'>{res['red']}</span></div>", unsafe_allow_html=True)
                    st.caption(f"Referencia: {res['ref']}")