import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import sqlite3

# Configuración de la página
st.set_page_config(page_title="Analyzer Pro Web", layout="wide")

# --- BASE DE DATOS (Carrito Permanente) ---
def init_db():
    conn = sqlite3.connect('carrito_web.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS carrito (id INTEGER PRIMARY KEY, info TEXT, fecha TEXT)')
    conn.commit()
    return conn

conn = init_db()

# --- LÓGICA DE LA API ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}

def obtener_partidos(liga_id):
    url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2025&next=10"
    response = requests.get(url, headers=HEADERS)
    return response.json().get('response', [])

# --- INTERFAZ STREAMLIT ---
st.title("⚽ Football Analyzer Pro - Dashboard Web")

# Sidebar para Ligas
st.sidebar.header("Ligas Principales")
liga_nombre = st.sidebar.selectbox("Selecciona Liga", 
    ["Premier League", "La Liga", "Serie A", "Ligue 1", "Bundesliga"])

ligas_ids = {"Premier League": 39, "La Liga": 140, "Serie A": 135, "Ligue 1": 61, "Bundesliga": 78}

# Cuerpo Principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header(f"Partidos de {liga_nombre}")
    partidos = obtener_partidos(ligas_ids[liga_nombre])
    
    for p in partidos:
        home = p['teams']['home']['name']
        away = p['teams']['away']['name']
        referee = p['fixture']['referee'] or "Sin asignar"
        
        with st.expander(f"🏟️ {home} vs {away} - Ver Análisis"):
            st.write(f"**⚖️ Árbitro:** {referee}")
            
            # Los 6 puntos clave
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("🎯 Marcador Exacto", "2 - 1")
                st.metric("🟨 Amarillas", "4 - 5")
            with c2:
                st.metric("⚽ Goles Totales", "Over 2.5")
                st.metric("🟥 Rojas", "Riesgo Bajo")
            with c3:
                st.metric("⏱️ Goles 1T", "65% Prob.")
                st.metric("🚩 Corners", "10.5 Prom.")
            
            if st.button(f"Guardar {home} vs {away}", key=p['fixture']['id']):
                fecha = datetime.now().strftime("%d/%m %H:%M")
                info = f"{home} vs {away} | Marcador: 2-1 | Corners: 10.5"
                conn.execute('INSERT INTO carrito (info, fecha) VALUES (?, ?)', (info, fecha))
                conn.commit()
                st.success("Guardado en el Carrito")

with col2:
    st.header("🛒 Carrito Permanente")
    cursor = conn.cursor()
    cursor.execute('SELECT info, fecha FROM carrito ORDER BY id DESC')
    for row in cursor.fetchall():
        st.info(f"📅 {row[1]}\n{row[0]}")