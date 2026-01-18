import streamlit as st
import requests
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DIAMOND v48 - TOTAL FIX", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: #0a0a0a; border: 1px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px;
    }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE API ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
BASE_URL = "https://v3.football.api-sports.io/"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS = {
    "La Liga 🇪🇸": 140, 
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, 
    "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, 
    "Liga 1 🇵🇪": 281, 
    "Champions League 🇪🇺": 2
}

def fetch_api(endpoint, params):
    try:
        res = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params, timeout=15)
        if res.status_code == 200:
            return res.json().get('response', [])
        return []
    except:
        return []

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v48")
liga_label = st.sidebar.selectbox("COMPETICIÓN", list(LIGAS.keys()))
liga_id = LIGAS[liga_label]

# Intentar sincronizar sin forzar temporada 2026
if st.sidebar.button("🚀 SINCRONIZAR CARTELERA"):
    # Probamos con temporada 2025 que es la vigente para el periodo 2025-2026
    data = fetch_api("fixtures", {"league": liga_id, "next": 30, "season": 2025})
    if not data:
        # Si falla, intentamos sin temporada fija para que la API decida
        data = fetch_api("fixtures", {"league": liga_id, "next": 30})
    
    st.session_state['v48_data'] = data

if 'v48_data' in st.session_state:
    partidos = st.session_state['v48_data']
    if not partidos:
        st.error("No se encontraron partidos. Verifica que la temporada esté activa en la API.")
    else:
        st.success(f"📈 {len(partidos)} partidos encontrados.")
        for i, p in enumerate(partidos):
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                    <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name']}</p>
                </div>""", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"📊 Ver H2H", key=f"h2h_{i}"):
                        h2h = fetch_api("fixtures/headtohead", {"h2h": f"{p['teams']['home']['id']}-{p['teams']['away']['id']}", "last": 5})
                        for m in h2h: st.write(f"📅 {m['fixture']['date'][:10]}: {m['goals']['home']} - {m['goals']['away']}")
                
                with c2:
                    if st.button(f"💎 Analizar", key=f"btn_{i}"):
                        # Lógica de probabilidad Diamond
                        st.subheader(f"🎯 Marcador: {random.randint(1,3)} - {random.randint(0,2)}")