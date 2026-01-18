import streamlit as st
import requests
from datetime import datetime
import random

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="DIAMOND v56 - TOTAL ACCESS", layout="wide")

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

# --- MOTOR DE INTELIGENCIA Y DATOS ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d" #
URL_BASE = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

LIGAS_ID = {
    "La Liga 🇪🇸": 140, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "Serie A 🇮🇹": 135,
    "Bundesliga 🇩🇪": 78, "Ligue 1 🇫🇷": 61, "Liga 1 🇵🇪": 281
}

ARBITROS_STRICT = ["Michael Oliver", "Anthony Taylor", "Kevin Ortega", "Alberola Rojas", "H. Hernández", "S. Marciniak", "F. Tello"] #

def fetch_all_fixtures(l_id):
    hoy = datetime.now().strftime('%Y-%m-%d')
    all_data = []
    
    # LLAMADA 1: Partidos de HOY (Barcelona si juega hoy)
    try:
        r1 = requests.get(URL_BASE, headers=HEADERS, params={"league": l_id, "date": hoy, "season": 2025}, timeout=10)
        all_data.extend(r1.json().get('response', []))
    except: pass
    
    # LLAMADA 2: Próximos 15 partidos (Calendario general)
    try:
        r2 = requests.get(URL_BASE, headers=HEADERS, params={"league": l_id, "next": 15}, timeout=10)
        all_data.extend(r2.json().get('response', []))
    except: pass

    # Eliminar duplicados
    seen = set()
    final = []
    for m in all_data:
        if m['fixture']['id'] not in seen:
            final.append(m)
            seen.add(m['fixture']['id'])
    return final

def calcular_diamond_v56(m, f, l):
    # Lógica de Marcador y Stats
    ref = m['fixture']['referee'] or "Sin asignar"
    p_h = 2.3 if "Barcelona" in m['teams']['home']['name'] or "Madrid" in m['teams']['home']['name'] else 1.4
    p_a = 1.1
    if f: p_h *= 0.82
    if l: p_h *= 0.70
    
    g_h = max(0, round(p_h + random.uniform(-0.1, 0.4)))
    g_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    
    strict = any(name in ref for name in ARBITROS_STRICT)
    return {
        "score": f"{g_h} - {g_a}", "total_g": g_h + g_a,
        "corners": random.randint(9, 13) if p_h > 1.9 else random.randint(7, 11),
        "cards": random.randint(5, 9) if strict else random.randint(3, 6),
        "ref": ref
    }

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v56")
sel = st.sidebar.selectbox("LIGAS MASTER", list(LIGAS_ID.keys()))
l_id = LIGAS_ID[sel]

if st.sidebar.button("🚀 SINCRONIZAR CALENDARIO"):
    with st.spinner("Forzando acceso total a la API..."):
        st.session_state['v56_data'] = fetch_all_fixtures(l_id)

if 'v56_data' in st.session_state:
    matches = st.session_state['v56_data']
    if not matches:
        st.error("No se detectaron partidos. Intenta con 'Premier League' para verificar.")
    else:
        st.success(f"✅ {len(matches)} partidos sincronizados con éxito.")
        for i, p in enumerate(matches):
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <h2 style='text-align:center;'>{p['teams']['home']['name']} vs {p['teams']['away']['name']}</h2>
                    <p style='text-align:center; color:#888;'>📅 {p['fixture']['date'][:10]} | ⚖️ Árbitro: {p['fixture']['referee'] or 'TBD'}</p>
                </div>""", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1: f = st.toggle("Fatiga", key=f"f_{i}")
                with c2: l = st.toggle("Lesión", key=f"l_{i}")
                
                if st.button("💎 ANALIZAR", key=f"b_{i}"):
                    res = calcular_diamond_v56(p, f, l)
                    st.divider()
                    r1, r2 = st.columns(2)
                    with r1:
                        st.write(f"🎯 Marcador: <span class='stat-result'>{res['score']}</span>", unsafe_allow_html=True)
                        st.write(f"🚩 Esquinas: <span class='stat-result'>{res['corners']}+</span>", unsafe_allow_html=True)
                    with r2:
                        st.write(f"🟨 Tarjetas: <span class='stat-result'>{res['cards']}</span>", unsafe_allow_html=True)
                        st.write(f"⚖️ Árbitro: {res['ref']}")