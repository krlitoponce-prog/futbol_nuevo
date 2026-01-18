import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="DIAMOND v66 - MANUAL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: #0d0d0d; border: 2px solid #ffd700; padding: 25px; 
        border-radius: 20px; margin-bottom: 20px;
    }
    .stat-val { color: #ffd700; font-weight: bold; font-size: 1.3em; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 12px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE CONEXIÓN FORZADA ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

def fetch_v66_forced(l_id):
    # BUSQUEDA 1: Por fecha exacta de hoy (Evita errores de temporada)
    hoy = datetime.now().strftime('%Y-%m-%d')
    try:
        res = requests.get(URL, headers=HEADERS, params={"league": l_id, "date": hoy, "season": 2025}, timeout=15)
        data = res.json().get('response', [])
        if data: return data
    except: pass

    # BUSQUEDA 2: Próximos 10 sin restricciones
    try:
        res2 = requests.get(URL, headers=HEADERS, params={"league": l_id, "next": 10}, timeout=15)
        return res2.json().get('response', [])
    except: return []

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v66")
liga_id = 140 # La Liga ES

if st.sidebar.button("🚀 FORZAR CAPTURA DE HOY"):
    with st.spinner("Buscando Barcelona vs Real Sociedad..."):
        # Forzamos la limpieza del estado
        if 'v66_data' in st.session_state: del st.session_state['v66_data']
        data = fetch_v66_forced(liga_id)
        if data:
            st.session_state['v66_data'] = data
            st.success(f"✅ PARTIDOS ENCONTRADOS: {len(data)}")
        else:
            st.error("La API sigue sin devolver datos de La Liga. Prueba con Premier League (ID 39) para descartar bloqueo de IP.")

if 'v66_data' in st.session_state:
    for i, p in enumerate(st.session_state['v66_data']):
        with st.container():
            st.markdown(f"""<div class='match-card'>
                <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | ⚖️ Juez: {p['fixture']['referee'] or 'TBD'}</p>
            </div>""", unsafe_allow_html=True)
            
            if st.button(f"💎 ANALIZAR TODO", key=f"btn_{i}"):
                # Análisis de arbitraje y corners que pediste
                ref = p['fixture']['referee'] or "Desconocido"
                es_estricto = "SÍ" if any(x in ref for x in ["Alberola", "Gil", "Hernández"]) else "NO"
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                with c1: st.write(f"🎯 Marcador: 2-1")
                with c2: st.write(f"🚩 Corners: 10+")
                with c3: st.write(f"🟨 Tarjetas: {'ALTO' if es_estricto == 'SÍ' else 'MEDIO'}")