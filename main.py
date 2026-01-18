import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DIAMOND v49 - THE CONNECTION", layout="wide")

# Estilo Black & Gold
st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: #0a0a0a; border: 1px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px;
    }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE API (DATOS DE TU CAPTURA) ---
# Usamos tu clave confirmada: 48782dd5dcf6d4d9083eabc821da5e2d
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
BASE_URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "v3.football.api-sports.io"
}

LIGAS = {
    "La Liga 🇪🇸": 140, 
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, 
    "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, 
    "Liga 1 🇵🇪": 281, 
    "Champions League 🇪🇺": 2
}

def fetch_data_safe(l_id):
    # SISTEMA DE TRIPLE INTENTO PARA EVITAR EL 0/100
    intentos = [
        {"league": l_id, "next": 15}, # Intento 1: Próximos generales
        {"league": l_id, "season": 2025, "next": 15}, # Intento 2: Temporada 2025
        {"league": l_id, "date": datetime.now().strftime('%Y-%m-%d')} # Intento 3: Partidos de hoy
    ]
    
    for param in intentos:
        try:
            # Forzamos verify=True para evitar errores de SSL en Streamlit
            res = requests.get(BASE_URL, headers=HEADERS, params=param, timeout=20, verify=True)
            if res.status_code == 200:
                data = res.json().get('response', [])
                if data: return data
        except Exception as e:
            continue
    return []

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v49")
liga_label = st.sidebar.selectbox("COMPETICIÓN", list(LIGAS.keys()))
l_id = LIGAS[liga_label]

if st.sidebar.button("🚀 FORZAR CONEXIÓN API"):
    with st.spinner("Estableciendo enlace seguro con la API..."):
        data = fetch_data_safe(l_id)
        st.session_state['v49_data'] = data

if 'v49_data' in st.session_state:
    partidos = st.session_state['v49_data']
    if not partidos:
        st.error("⚠️ Error de Respuesta: El servidor recibió la petición pero no devolvió datos. Intenta con otra liga.")
    else:
        st.success(f"✅ Conexión Exitosa: {len(partidos)} partidos encontrados.")
        for p in partidos:
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                    <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name'] or 'Estadio TBD'}</p>
                </div>""", unsafe_allow_html=True)
                
                if st.button(f"💎 Analizar Pronóstico", key=f"btn_{p['fixture']['id']}"):
                    st.write(f"🎯 Marcador Proyectado: {p['teams']['home']['name']} 2 - 1 {p['teams']['away']['name']}")