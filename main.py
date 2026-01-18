import streamlit as st
import requests
from datetime import datetime
import random

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="DIAMOND v55.1 - ULTRA PRECISION", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: #0a0a0a; border: 1px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
    }
    .stat-result { color: #ffd700; font-weight: bold; font-size: 1.1em; }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS E INTELIGENCIA ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d" #
URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS_ID = {
    "La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, "Ligue 1 🇫🇷": 61, "Liga 1 🇵🇪": 281
}

ARBITROS_STRICT = ["Michael Oliver", "Anthony Taylor", "Kevin Ortega", "Alberola Rojas", "H. Hernández", "S. Marciniak", "F. Tello"] #

def calcular_diamond_pro(m, fatiga, lesion):
    referee = m['fixture']['referee'] or "Sin asignar"
    home_name = m['teams']['home']['name']
    
    # 1. Goles y Marcador Exacto
    p_h = (2.2 if "Barcelona" in home_name or "Madrid" in home_name else 1.5)
    p_a = 1.1
    if fatiga: p_h *= 0.85 #
    if lesion: p_h *= 0.75 #
    
    g_h = max(0, round(p_h + random.uniform(-0.1, 0.4)))
    g_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    g_totales = g_h + g_a
    
    # 2. Tiros de Esquina (Corners)
    corners = random.randint(9, 12) if p_h > 1.8 else random.randint(7, 10)
    
    # 3. Lógica de Tarjetas basada en Árbitro
    es_estricto = any(name in referee for name in ARBITROS_STRICT)
    t_amarillas = random.randint(5, 8) if es_estricto else random.randint(3, 5)
    t_roja = "ALTA" if es_estricto else "MEDIA/BAJA"

    return {
        "marcador": f"{g_h} - {g_a}",
        "goles": f"{g_totales} Goles Totales",
        "corners": f"{corners}+ Corners",
        "tarjetas": f"{t_amarillas} Tarjetas Amarillas",
        "roja": t_roja,
        "referee": referee
    }

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v55.1")
liga_sel = st.sidebar.selectbox("LIGAS MASTER", list(LIGAS_ID.keys()))
id_actual = LIGAS_ID[liga_sel]

if st.sidebar.button("🚀 SINCRONIZAR CALENDARIO"):
    # Búsqueda híbrida para capturar partidos de hoy (Barcelona)
    hoy = datetime.now().strftime('%Y-%m-%d')
    res = requests.get(URL, headers=HEADERS, params={"league": id_actual, "season": 2025, "next": 15}, timeout=10)
    st.session_state['v55_data'] = res.json().get('response', [])

if 'v55_data' in st.session_state:
    partidos = st.session_state['v55_data']
    if not partidos:
        st.error("No se encontraron partidos. Intenta recargar.")
    else:
        st.success(f"✅ {len(partidos)} partidos sincronizados.")
        for i, p in enumerate(partidos):
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                    <p style='text-align:center; color:#888;'>⚖️ Árbitro: <b>{p['fixture']['referee'] or 'TBD'}</b></p>
                    <p style='text-align:center; font-size:0.8em;'>📅 {p['fixture']['date'][:10]}</p>
                </div>""", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1: f = st.toggle("Factor Fatiga", key=f"f_{i}")
                with c2: l = st.toggle("Baja Estrella", key=f"l_{i}")
                
                if st.button(f"💎 ANALIZAR PARTIDO", key=f"btn_{i}"):
                    res = calcular_diamond_pro(p, f, l)
                    st.markdown("---")
                    res1, res2 = st.columns(2)
                    with res1:
                        st.write(f"🎯 Marcador: <span class='stat-result'>{res['marcador']}</span>", unsafe_allow_html=True)
                        st.write(f"⚽ Goles: <span class='stat-result'>{res['goles']}</span>", unsafe_allow_html=True)
                        st.write(f"🚩 Esquinas: <span class='stat-result'>{res['corners']}</span>", unsafe_allow_html=True)
                    with res2:
                        st.write(f"🟨 Amarillas: <span class='stat-result'>{res['tarjetas']}</span>", unsafe_allow_html=True)
                        st.write(f"🟥 Riesgo Roja: <span class='stat-result'>{res['roja']}</span>", unsafe_allow_html=True)
                        st.caption(f"Análisis basado en: {res['referee']}")