import streamlit as st
import requests

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DIAMOND v75 - ESTABLE", layout="wide")

# --- MOTOR DE DATOS ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d" #
URL = "https://v3.football.api-sports.io/fixtures"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

def analizar_logico(m):
    # Extraemos datos reales de la API
    g_h = m['goals']['home'] or 0
    g_a = m['goals']['away'] or 0
    ref = m['fixture']['referee'] or "Desconocido"
    
    # Lógica de ganador basada en marcador actual
    if g_a > g_h:
        proy_final = f"{g_h} - {g_a + 1} (Gana Visitante)"
    elif g_h > g_a:
        proy_final = f"{g_h + 1} - {g_a} (Gana Local)"
    else:
        proy_final = f"{g_h + 1} - {g_a + 1} (Empate)"
        
    # Lógica de árbitro fija (Gil Manzano)
    es_estricto = "Gil Manzano" in ref
    return {
        "score": proy_final,
        "cards": "6.5+ (ALTO)" if es_estricto else "3.5+ (MEDIO)",
        "corners": "9.5+ (PROMEDIO)"
    }

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v75")
if st.sidebar.button("🚀 ACTUALIZAR LIVE"):
    res = requests.get(URL, headers=HEADERS, params={"league": 140, "live": "all"})
    st.session_state['live'] = res.json().get('response', [])

if 'live' in st.session_state and st.session_state['live']:
    for p in st.session_state['live']:
        st.write(f"### {p['teams']['home']['name']} {p['goals']['home']} - {p['goals']['away']} {p['teams']['away']['name']}")
        if st.button("💎 ANALIZAR FINAL"):
            res = analizar_logico(p)
            st.success(f"🎯 Marcador Final Proyectado: {res['score']}")
            st.warning(f"🟨 Tarjetas: {res['cards']} | 🚩 Corners: {res['corners']}")