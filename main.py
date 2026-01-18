import streamlit as st
import requests
from datetime import datetime
import random

# --- ESTILO VISUAL ELITE ---
st.set_page_config(page_title="DIAMOND v57 - ABSOLUTE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: linear-gradient(145deg, #0a0a0a, #111);
        border: 1px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px;
    }
    .stat-box { background: #1a1a1a; padding: 15px; border-radius: 10px; border-left: 4px solid #ffd700; }
    .stat-val { color: #ffd700; font-weight: bold; font-size: 1.2em; }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 10px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE INTELIGENCIA ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d" #
URL_BASE = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS_ID = {
    "La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, "Ligue 1 🇫🇷": 61, "Liga 1 🇵🇪": 281
}

ARBITROS_STRICT = ["Michael Oliver", "Anthony Taylor", "Kevin Ortega", "Alberola Rojas", "H. Hernández", "S. Marciniak"]

def fetch_absolute_v57(l_id):
    """Protocolo de carga única para evitar errores de conexión."""
    # Usamos la temporada 2025 que es la activa para enero 2026
    params = {"league": l_id, "season": 2025, "next": 20}
    try:
        response = requests.get(URL_BASE, headers=HEADERS, params=params, timeout=15)
        if response.status_code == 200:
            return response.json().get('response', [])
    except:
        return []
    return []

def analizar_full_diamond(m, fatiga, lesion):
    ref = m['fixture']['referee'] or "Por confirmar"
    home = m['teams']['home']['name']
    
    # Lógica de Goles y Marcador
    p_h = 2.4 if "Barcelona" in home or "Madrid" in home else 1.5
    p_a = 1.2
    if fatiga: p_h *= 0.80
    if lesion: p_h *= 0.70
    
    g_h = max(0, round(p_h + random.uniform(-0.1, 0.4)))
    g_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    
    # Lógica de Tarjetas y Corners
    es_estricto = any(name in ref for name in ARBITROS_STRICT)
    corners = random.randint(10, 14) if p_h > 2.0 else random.randint(8, 11)
    amarillas = random.randint(6, 9) if es_estricto else random.randint(3, 6)
    
    return {
        "marcador": f"{g_h} - {g_a}",
        "goles_t": g_h + g_a,
        "corners": f"{corners}+",
        "tarjetas": f"{amarillas}",
        "roja": "ALTO RIESGO" if es_estricto else "BAJO",
        "arbitro": ref
    }

# --- INTERFAZ PRINCIPAL ---
st.sidebar.title("💎 DIAMOND v57")
st.sidebar.markdown("---")
sel_liga = st.sidebar.selectbox("LIGAS MASTER", list(LIGAS_ID.keys()))
l_id = LIGAS_ID[sel_liga]

if st.sidebar.button("🚀 SINCRONIZAR ABSOLUTO"):
    with st.spinner("Estableciendo conexión blindada con la API..."):
        # Limpiamos y cargamos
        data = fetch_absolute_v57(l_id)
        if data:
            st.session_state['v57_data'] = data
            st.success(f"✅ CONEXIÓN EXITOSA: {len(data)} partidos encontrados.")
        else:
            st.error("🚨 ERROR DE RESPUESTA: El servidor no devolvió datos. Verifica tu conexión.")

if 'v57_data' in st.session_state:
    for i, p in enumerate(st.session_state['v57_data']):
        with st.container():
            st.markdown(f"""<div class='match-card'>
                <h2 style='text-align:center; margin-bottom:0;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                <p style='text-align:center; color:#888; font-size:0.9em;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name'] or 'Oficial'}</p>
                <p style='text-align:center; font-weight:bold; color:#ffd700;'>⚖️ Juez: {p['fixture']['referee'] or 'TBD'}</p>
            </div>""", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1: f = st.toggle("Factor Fatiga", key=f"f_{i}")
            with col2: l = st.toggle("Baja Estrella", key=f"l_{i}")
            
            if st.button(f"💎 ANALIZAR {p['teams']['home']['name'].upper()}", key=f"btn_{i}"):
                res = analizar_full_diamond(p, f, l)
                st.markdown("<br>", unsafe_allow_html=True)
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.markdown(f"<div class='stat-box'>🎯 MARCADOR<br><span class='stat-val'>{res['marcador']}</span></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='stat-box' style='margin-top:10px;'>⚽ TOTAL GOLES<br><span class='stat-val'>{res['goles_t']}</span></div>", unsafe_allow_html=True)
                with r2:
                    st.markdown(f"<div class='stat-box'>🚩 CORNERS<br><span class='stat-val'>{res['corners']}</span></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='stat-box' style='margin-top:10px;'>🟨 AMARILLAS<br><span class='stat-val'>{res['tarjetas']}</span></div>", unsafe_allow_html=True)
                with r3:
                    st.markdown(f"<div class='stat-box'>🟥 RIESGO ROJA<br><span class='stat-val'>{res['roja']}</span></div>", unsafe_allow_html=True)
                    st.caption(f"Análisis arbitral: {res['arbitro']}")