import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Fútbol Pro", layout="wide")

# Inicializar Carrito en memoria (evita errores de base de datos en la web)
if 'carrito' not in st.session_state:
    st.session_state['carrito'] = []

# --- MOTOR DE API ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "v3.football.api-sports.io"
}

def obtener_partidos(liga_id, fecha_obj):
    fecha_str = fecha_obj.strftime("%Y-%m-%d")
    # Intentamos obtener los partidos de la fecha seleccionada
    url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2025&date={fecha_str}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        
        # Depuración: Si la API responde algo raro, lo vemos
        if "errors" in data and data["errors"]:
            st.sidebar.error(f"Error API: {data['errors']}")
            
        return data.get('response', [])
    except Exception as e:
        st.sidebar.error(f"Error de conexión: {e}")
        return []

# --- INTERFAZ ---
st.title("🏆 Dashboard de Inteligencia Deportiva")

# Sidebar
st.sidebar.header("Configuración")
liga_nombre = st.sidebar.selectbox("1. Liga", ["Premier League", "La Liga", "Serie A", "Bundesliga"])
# Forzamos que el calendario sea para el sábado si lo deseas
fecha_sel = st.sidebar.date_input("2. Selecciona Fecha", datetime(2026, 1, 17))

ligas_dict = {"Premier League": 39, "La Liga": 140, "Serie A": 135, "Bundesliga": 78}

col_p, col_c = st.columns([2, 1])

with col_p:
    st.header(f"Partidos: {liga_nombre}")
    st.caption(f"📅 Buscando para el día: {fecha_sel}")
    
    with st.spinner('Conectando con la API...'):
        partidos = obtener_partidos(ligas_dict[liga_nombre], fecha_sel)
    
    if not partidos:
        st.info("No se encontraron partidos para esta fecha. Intenta cambiar de liga o de día.")
        # Botón de auxilio: ver últimos 5 resultados si no hay próximos
        if st.button("Ver últimos resultados de esta liga"):
            url_last = f"https://v3.football.api-sports.io/fixtures?league={ligas_dict[liga_nombre]}&season=2025&last=5"
            partidos = requests.get(url_last, headers=HEADERS).json().get('response', [])
            st.rerun()
    else:
        for p in partidos:
            home = p['teams']['home']['name']
            away = p['teams']['away']['name']
            hora = p['fixture']['date'][11:16]
            
            with st.container(border=True):
                st.subheader(f"{home} vs {away} 🕒 {hora}")
                
                # Los 6 puntos clave
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
                
                if st.button(f"Guardar Referencia {home}", key=p['fixture']['id']):
                    nota = f"{home} vs {away} | Sábado 17 | Pred: 2-1"
                    st.session_state['carrito'].append(nota)
                    st.toast("Añadido al carrito")

with col_c:
    st.header("🛒 Carrito")
    if not st.session_state['carrito']:
        st.write("Tu carrito temporal está vacío.")
    else:
        for item in st.session_state['carrito'][::-1]:
            st.info(item)
        if st.button("Limpiar Carrito"):
            st.session_state['carrito'] = []
            st.rerun()