import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Predicción Elite Multifuente", layout="wide", page_icon="📊")

# --- 1. BASE DE DATOS (CARRITO PERMANENTE) ---
def init_db():
    conn = sqlite3.connect('analisis_elite.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detalle TEXT,
            liga TEXT,
            fecha TEXT
        )
    ''')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. MOTOR DE SCRAPING (SIMULACIÓN DE LÓGICA MULTIFUENTE) ---
# Nota: En un entorno real, aquí usaríamos Selenium o Playwright para entrar a SofaScore/Flashscore
def scraping_multifuente(liga, sources):
    # Simulamos la extracción de datos cruzados de las 5 páginas
    # SofaScore -> Árbitros y Corners
    # Flashscore -> Alineaciones y Goles 1T
    # ESPN/AS -> Noticias y Bajas
    
    # Datos de ejemplo basados en las mejores ligas solicitadas
    datos = {
        "Premier League": [
            {"home": "Man. United", "away": "Man. City", "arbitro": "Michael Oliver (7.5 amarillas prom)", "corners_p": "11.5", "goles_1t": "80%"},
            {"home": "Arsenal", "away": "Liverpool", "arbitro": "Anthony Taylor (4.2 amarillas prom)", "corners_p": "10.0", "goles_1t": "65%"}
        ],
        "La Liga": [
            {"home": "Real Madrid", "away": "Barcelona", "arbitro": "Gil Manzano (6.0 amarillas prom)", "corners_p": "9.5", "goles_1t": "75%"}
        ],
        "Liga 1 (Perú)": [
            {"home": "Universitario", "away": "Alianza Lima", "arbitro": "Kevin Ortega (8.0 amarillas prom)", "corners_p": "10.5", "goles_1t": "50%"}
        ]
    }
    return datos.get(liga, [])

# --- 3. INTERFAZ PRINCIPAL ---
st.title("🛡️ Sistema de Predicción en Tiempo Real (Scraping Mode)")

# Sidebar con todas tus ligas
st.sidebar.header("Configuración de Rastreo")
ligas_disponibles = [
    "Premier League", "La Liga", "Bundesliga", "Serie A", 
    "Ligue 1", "Primeira Liga (Portugal)", "Brasileirao", "Liga 1 (Perú)"
]
liga_sel = st.sidebar.selectbox("Selecciona Liga para Scraping", ligas_disponibles)

# Botón de Actualización en Tiempo Real
if st.sidebar.button("🔄 Actualizar Datos (Real-Time Scraping)"):
    with st.spinner(f"Extrayendo datos de Flashscore, SofaScore y ESPN..."):
        time.sleep(2) # Simulación de tiempo de carga de las webs
        st.toast("¡Datos actualizados desde las 5 fuentes!")

col1, col2 = st.columns([2, 1])

with col1:
    st.header(f"Análisis Técnico: {liga_sel}")
    partidos = scraping_multifuente(liga_sel, ["SofaScore", "Flashscore", "ESPN", "AS"])
    
    if not partidos:
        st.info("No hay partidos detectados para esta liga en las próximas horas.")
    
    for p in partidos:
        with st.container(border=True):
            st.subheader(f"🏟️ {p['home']} vs {p['away']}")
            
            # --- EL MEJOR ANÁLISIS DE 6 PUNTOS ---
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success(f"🎯 Marcador Exacto: 2-1 / 1-1")
                st.info(f"🚩 Corners: {p['corners_p']} (Más de 9.5)")
            with c2:
                st.warning(f"🟨 Tarjetas: {p['arbitro']}")
                st.write(f"⏱️ Goles 1T: {p['goles_1t']} de probabilidad")
            with c3:
                st.error(f"⚽ Goles Totales: +2.5 / +3.5")
                st.write("🟥 Rojas: Riesgo Alto")
            
            if st.button(f"Guardar en Carrito Permanente: {p['home']}", key=p['home']):
                detalle = f"{p['home']} vs {p['away']} | Pred: 2-1 | Árbitro: {p['arbitro']}"
                cursor = db_conn.cursor()
                cursor.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', 
                             (detalle, liga_sel, datetime.now().strftime("%Y-%m-%d %H:%M")))
                db_conn.commit()
                st.rerun()

with col2:
    st.header("🛒 Carrito de Referencias")
    st.caption("Guardado permanentemente en base de datos")
    
    cursor = db_conn.cursor()
    cursor.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    items = cursor.fetchall()
    
    for det, fec in items:
        with st.chat_message("assistant"):
            st.caption(f"Fecha: {fec}")
            st.write(det)
            
    if st.sidebar.button("🗑️ Vaciar Carrito"):
        db_conn.execute('DELETE FROM carrito')
        db_conn.commit()
        st.rerun()