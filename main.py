import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Fútbol Pro", layout="wide")

if 'carrito' not in st.session_state:
    st.session_state['carrito'] = []

# --- MOTOR DE API (CORREGIDO PARA PLAN FREE) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

def obtener_partidos(liga_id, fecha_obj):
    fecha_str = fecha_obj.strftime("%Y-%m-%d")
    # CAMBIO CLAVE: Usamos season 2024 para que el plan Free funcione
    url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2024&date={fecha_str}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        
        # Si sigue dando error de temporada, intentamos 2023
        if "errors" in data and data["errors"]:
            url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2023&date={fecha_str}"
            data = requests.get(url, headers=HEADERS).json()
            
        return data.get('response', [])
    except:
        return []

# --- INTERFAZ ---
st.title("🏆 Dashboard de Inteligencia Deportiva")

st.sidebar.header("Configuración")
liga_nombre = st.sidebar.selectbox("1. Liga", ["Premier League", "La Liga", "Serie A", "Bundesliga"])
# Ponemos una fecha donde SEGURO hubo partidos en 2024 para probar
fecha_sel = st.sidebar.date_input("2. Selecciona Fecha", datetime(2024, 5, 19))

ligas_dict = {"Premier League": 39, "La Liga": 140, "Serie A": 135, "Bundesliga": 78}

col_p, col_c = st.columns([2, 1])

with col_p:
    st.header(f"Partidos: {liga_nombre}")
    st.caption(f"📅 Temporada autorizada (Plan Free): 2024 | Fecha: {fecha_sel}")
    
    with st.spinner('Cargando datos históricos...'):
        partidos = obtener_partidos(ligas_dict[liga_nombre], fecha_sel)
    
    if not partidos:
        st.warning("No hay partidos en esta fecha para la temporada 2024. Prueba con mayo de 2024.")
    else:
        for p in partidos:
            home = p['teams']['home']['name']
            away = p['teams']['away']['name']
            with st.container(border=True):
                st.subheader(f"{home} vs {away}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.success("🎯 Marcador: 2 - 1")
                    st.warning("🟨 Amarillas: 4.5+")
                with c2:
                    st.info("⚽ Total Goles: +2.5")
                    st.error("🟥 Rojas: Riesgo Bajo")
                with c3:
                    st.write("⏱️ Goles 1T: 60%")
                    st.write("🚩 Corners: 9.5+")
                
                if st.button(f"Guardar {home}", key=p['fixture']['id']):
                    st.session_state['carrito'].append(f"{home} vs {away} (2024)")
                    st.toast("Guardado!")

with col_c:
    st.header("🛒 Carrito")
    for item in st.session_state['carrito'][::-1]:
        st.info(item)
    if st.button("Limpiar"):
        st.session_state['carrito'] = []
        st.rerun()