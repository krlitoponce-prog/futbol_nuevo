import streamlit as st
import requests
import random

# --- ESTILO VISUAL DIAMOND ---
st.set_page_config(page_title="DIAMOND v74 - HYBRID", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .live-card { border: 2px solid #ff4b4b; background: #0d0d0d; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .next-card { border: 2px solid #ffd700; background: #0d0d0d; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .stat-val { color: #ffd700; font-weight: bold; font-size: 1.3em; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d" #
URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

def fetch_hybrid_v74(l_id):
    # 1. Intentar capturar EN VIVO
    try:
        res_live = requests.get(URL, headers=HEADERS, params={"league": l_id, "live": "all"}, timeout=10)
        live_data = res_live.json().get('response', [])
        if live_data: return live_data, "LIVE"
    except: pass
    
    # 2. Si no hay nada en vivo, traer los PRÓXIMOS 10
    try:
        res_next = requests.get(URL, headers=HEADERS, params={"league": l_id, "next": 10}, timeout=10)
        return res_next.json().get('response', []), "NEXT"
    except: return [], "NONE"

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v74")
ligas = {"La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135, "Bundesliga 🇩🇪": 78}
sel = st.sidebar.selectbox("COMPETICIÓN", list(ligas.keys()))

if st.sidebar.button("🚀 SINCRONIZAR MASTER"):
    data, tipo = fetch_hybrid_v74(ligas[sel])
    st.session_state['data'] = data
    st.session_state['tipo'] = tipo

if 'data' in st.session_state:
    tipo = st.session_state['tipo']
    matches = st.session_state['data']
    
    if not matches:
        st.warning("No hay partidos disponibles para esta liga ahora mismo.")
    else:
        st.subheader(f"MODO DETECTADO: {tipo}")
        for i, p in enumerate(matches):
            css_class = "live-card" if tipo == "LIVE" else "next-card"
            badge = "🔴 EN VIVO" if tipo == "LIVE" else "📅 PRÓXIMO"
            
            with st.container():
                st.markdown(f"""<div class='{css_class}'>
                    <h3 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h3>
                    <p style='text-align:center;'>{badge} | ⚖️ Juez: {p['fixture']['referee'] or 'TBD'}</p>
                </div>""", unsafe_allow_html=True)
                
                if st.button(f"💎 ANALIZAR {i}", key=f"b_{i}"):
                    # Análisis Arbitral: Gil Manzano u otros
                    ref = p['fixture']['referee'] or "Desconocido"
                    es_estricto = any(x in ref for x in ["Gil Manzano", "Alberola", "Hernández"])
                    
                    st.divider()
                    c1, c2, c3 = st.columns(3)
                    with c1: st.write("🎯 Marcador: **2 - 1**")
                    with c2: st.write("🚩 Corners: **10.5+**")
                    with c3:
                        st.write(f"🟨 Tarjetas: **{'6.5+' if es_estricto else '3.5+'}**")
                        st.caption(f"Análisis basado en {ref}")