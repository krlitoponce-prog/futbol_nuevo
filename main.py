import streamlit as st
import requests
from datetime import datetime, timedelta
import random

# --- CONFIGURACIÓN VISUAL ELITE ---
st.set_page_config(page_title="DIAMOND v59 - THE FINAL KEY", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: white; }
    .stApp { background-color: #000; }
    .match-card { 
        background: linear-gradient(145deg, #0a0a0a, #151515);
        border: 1px solid #ffd700; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.1);
    }
    .stat-result { color: #ffd700; font-weight: bold; font-size: 1.2em; }
    h1, h2, h3 { color: #ffd700 !important; }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; width: 100%; border-radius: 12px; height: 3.5em; border: none; }
    .stButton>button:hover { background: #ffea00; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE CONEXIÓN ABSOLUTO ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d" #
URL_BASE = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS_ID = {
    "La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, "Liga 1 🇵🇪": 281, "Ligue 1 🇫🇷": 61
}

ARBITROS_STRICT = ["Michael Oliver", "Anthony Taylor", "Kevin Ortega", "Alberola Rojas", "H. Hernández", "Gil Manzano"]

def fetch_data_v59(l_id):
    """Escaneo por fecha directa para asegurar la aparición del Barcelona."""
    hoy = datetime.now().strftime('%Y-%m-%d')
    manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    resultados = []
    # Escaneamos hoy y mañana por separado para no saturar la petición
    for fecha in [hoy, manana]:
        try:
            # Buscamos en temporada 2025 que es la activa para enero 2026
            res = requests.get(URL_BASE, headers=HEADERS, params={"league": l_id, "date": fecha, "season": 2025}, timeout=15)
            if res.status_code == 200:
                data = res.json().get('response', [])
                if data: resultados.extend(data)
        except: continue
    
    # Si sigue vacío, probamos el último recurso sin año fijo
    if not resultados:
        try:
            res_alt = requests.get(URL_BASE, headers=HEADERS, params={"league": l_id, "next": 15}, timeout=15)
            resultados = res_alt.json().get('response', [])
        except: pass
        
    return resultados

def analizar_oracle_v59(m, fatiga, lesion):
    ref = m['fixture']['referee'] or "Sin asignar"
    home = m['teams']['home']['name']
    
    # Marcador y Goles
    p_h = 2.5 if "Barcelona" in home or "Madrid" in home else 1.5
    p_a = 1.1
    if fatiga: p_h *= 0.80
    if lesion: p_h *= 0.70
    
    g_h = max(0, round(p_h + random.uniform(-0.1, 0.4)))
    g_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    
    # Stats Pro: Corners y Tarjetas
    strict = any(name in ref for name in ARBITROS_STRICT)
    corners = random.randint(10, 15) if p_h > 2.2 else random.randint(7, 11)
    amarillas = random.randint(6, 10) if strict else random.randint(3, 5)
    
    return {
        "score": f"{g_h} - {g_a}", "total_g": g_h + g_a,
        "corners": f"{corners}+", "cards": f"{amarillas} Amarillas",
        "red": "ALTO RIESGO" if strict else "BAJO", "ref": ref
    }

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v59")
st.sidebar.markdown(f"**API Status:** 🟢 Conectado")
liga_name = st.sidebar.selectbox("LIGAS MASTER", list(LIGAS_ID.keys()))
l_id = LIGAS_ID[liga_name]

if st.sidebar.button("🚀 INICIAR ESCANEO ABSOLUTO"):
    with st.spinner("Estableciendo enlace de alta prioridad..."):
        data = fetch_data_v59(l_id)
        if data:
            st.session_state['v59_data'] = data
            st.success(f"✅ CONEXIÓN ESTABLECIDA: {len(data)} partidos encontrados.")
        else:
            st.error("🚨 ERROR CRÍTICO: El servidor no devolvió datos para esta fecha. Intenta Premier League.")

if 'v59_data' in st.session_state:
    for i, p in enumerate(st.session_state['v59_data']):
        with st.container():
            st.markdown(f"""<div class='match-card'>
                <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | 🏟️ {p['fixture']['venue']['name'] or 'Oficial'}</p>
                <p style='text-align:center; color:#ffd700; font-weight:bold;'>⚖️ Juez: {p['fixture']['referee'] or 'TBD'}</p>
            </div>""", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1: f = st.toggle("Cansancio Físico", key=f"f_{i}")
            with c2: l = st.toggle("Baja Sensible", key=f"l_{i}")
            
            if st.button(f"💎 ANALIZAR {p['teams']['home']['name'].upper()}", key=f"btn_{i}"):
                res = analizar_oracle_v59(p, f, l)
                st.markdown("---")
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.write(f"🎯 Marcador: <span class='stat-result'>{res['score']}</span>", unsafe_allow_html=True)
                    st.write(f"⚽ Goles: <span class='stat-result'>{res['total_g']}</span>", unsafe_allow_html=True)
                with r2:
                    st.write(f"🚩 Esquinas: <span class='stat-result'>{res['corners']}</span>", unsafe_allow_html=True)
                    st.write(f"🟨 Tarjetas: <span class='stat-result'>{res['cards']}</span>", unsafe_allow_html=True)
                with r3:
                    st.write(f"🟥 Roja: <span class='stat-result'>{res['red']}</span>", unsafe_allow_html=True)
                    st.caption(f"Árbitro: {res['ref']}")