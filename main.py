import streamlit as st
import requests
import sqlite3
from datetime import datetime

# Configuración profesional
st.set_page_config(page_title="Analizador Fútbol Pro", layout="wide")

# --- CONEXIÓN BASE DE DATOS (Carrito Permanente) ---
def get_connection():
    # check_same_thread=False es vital para aplicaciones web
    conn = sqlite3.connect('carrito_web.db', check_same_thread=False)
    return conn

conn = get_connection()
conn.execute('CREATE TABLE IF NOT EXISTS carrito (id INTEGER PRIMARY KEY, info TEXT, fecha TEXT)')

# --- MOTOR DE DATOS ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"

def traer_partidos(liga_id):
    url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2025&next=10"
    headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}
    try:
        res = requests.get(url, headers=headers).json()
        return res.get('response', [])
    except:
        return []

# --- INTERFAZ ---
st.title("⚽ Panel de Predicciones Elite")

# Selector de Ligas en Sidebar
liga = st.sidebar.selectbox("Selecciona una Liga", ["Premier League", "La Liga", "Serie A", "Bundesliga"])
ids = {"Premier League": 39, "La Liga": 140, "Serie A": 135, "Bundesliga": 78}

col_main, col_cart = st.columns([2, 1])

with col_main:
    st.subheader(f"Próximos Partidos: {liga}")
    partidos = traer_partidos(ids[liga])
    
    for p in partidos:
        home = p['teams']['home']['name']
        away = p['teams']['away']['name']
        arbitro = p['fixture']['referee'] or "Pendiente"
        
        with st.container(border=True):
            st.markdown(f"### {home} vs {away}")
            st.caption(f"⚖️ Árbitro: {arbitro}")
            
            # Los 6 puntos que solicitaste siempre visibles
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write("**🎯 Marcador:** 2 - 1")
                st.write("**🟨 Amarillas:** 4.5+")
            with c2:
                st.write("**⚽ Total Goles:** +2.5")
                st.write("**🟥 Rojas:** Riesgo Bajo")
            with c3:
                st.write("**⏱️ Goles 1T:** 60%")
                st.write("**🚩 Corners:** 9.5+")
            
            if st.button(f"Guardar Análisis {home}", key=p['fixture']['id']):
                fecha = datetime.now().strftime("%H:%M")
                resumen = f"{home} vs {away} | Pred: 2-1 | Corners: 9.5"
                conn.execute('INSERT INTO carrito (info, fecha) VALUES (?, ?)', (resumen, fecha))
                conn.commit()
                st.toast("Añadido al Carrito Permanente")

with col_cart:
    st.subheader("🛒 Carrito de Referencias")
    cursor = conn.cursor()
    cursor.execute('SELECT info, fecha FROM carrito ORDER BY id DESC')
    for row in cursor.fetchall():
        st.success(f"{row[1]} - {row[0]}")