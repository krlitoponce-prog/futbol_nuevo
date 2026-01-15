import streamlit as st
import requests
import sqlite3
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Analizador Fútbol Pro Elite", layout="wide", page_icon="⚽")

# --- BASE DE DATOS LOCAL (CARRITO PERMANENTE) ---
def init_db():
    conn = sqlite3.connect('carrito_web.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            info TEXT,
            fecha_registro TEXT
        )
    ''')
    conn.commit()
    return conn

db_conn = init_db()

# --- MOTOR DE DATOS (OPTIMIZADO PARA PLAN FREE + CALENDARIO) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "v3.football.api-sports.io"
}

def obtener_partidos_por_fecha(liga_id, fecha_obj):
    fecha_str = fecha_obj.strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2025&date={fecha_str}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10).json()
        return res.get('response', [])
    except Exception as e:
        return []

# --- INTERFAZ DE USUARIO ---
st.title("🏆 Dashboard de Inteligencia Deportiva")
st.markdown("---")

# Sidebar: Ligas y CALENDARIO
st.sidebar.header("Filtros de Búsqueda")
liga_seleccionada = st.sidebar.selectbox(
    "1. Selecciona Liga", 
    ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
)

# Integración del Calendario
fecha_consulta = st.sidebar.date_input(
    "2. Selecciona Fecha",
    datetime.now()
)

ids_ligas = {"Premier League": 39, "La Liga": 140, "Serie A": 135, "Bundesliga": 78, "Ligue 1": 61}

col_analisis, col_carrito = st.columns([2, 1])

with col_analisis:
    st.header(f"Partidos: {liga_seleccionada}")
    st.subheader(f"📅 Fecha: {fecha_consulta.strftime('%d de %B, %Y')}")
    
    lista_partidos = obtener_partidos_por_fecha(ids_ligas[liga_seleccionada], fecha_consulta)
    
    if not lista_partidos:
        st.info(f"No hay partidos programados en {liga_seleccionada} para la fecha elegida.")
    else:
        for p in lista_partidos:
            home = p['teams']['home']['name']
            away = p['teams']['away']['name']
            referee = p['fixture']['referee'] or "TBD (Por asignar)"
            hora = p['fixture']['date'][11:16]
            p_id = p['fixture']['id']
            
            with st.container(border=True):
                st.subheader(f"{home} vs {away} 🕒 {hora}")
                st.write(f"⚖️ **Árbitro:** {referee}")
                
                # BLOQUE DE LOS 6 PUNTOS CLAVE
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.success("🎯 **Marcador:** 2 - 1")
                    st.warning("🟨 **Amarillas:** 4.5+")
                with c2:
                    st.info("⚽ **Total Goles:** +2.5")
                    st.error("🟥 **Rojas:** Riesgo Bajo")
                with c3:
                    st.write("⏱️ **Goles 1T:** 60% Prob.")
                    st.write("🚩 **Corners:** 9.5+")
                
                if st.button(f"Guardar Referencia {home}", key=f"btn_{p_id}"):
                    resumen = f"{home} vs {away} | Fecha: {fecha_consulta} | Pred: 2-1"
                    fecha_reg = datetime.now().strftime("%d/%m %H:%M")
                    cursor = db_conn.cursor()
                    cursor.execute('INSERT INTO carrito (info, fecha_registro) VALUES (?, ?)', (resumen, fecha_reg))
                    db_conn.commit()
                    st.rerun()

with col_carrito:
    st.header("🛒 Carrito")
    try:
        cursor = db_conn.cursor()
        cursor.execute('SELECT info, fecha_registro FROM carrito ORDER BY id DESC')
        registros = cursor.fetchall()
        
        if not registros:
            st.write("Tu carrito está vacío.")
        else:
            for info, fecha in registros:
                with st.chat_message("assistant"):
                    st.caption(f"Guardado el: {fecha}")
                    st.write(info)
                    st.divider()
    except:
        st.error("Error al cargar el historial.")

# Botón para borrar carrito en la parte inferior del sidebar
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Borrar Todo el Carrito"):
    db_conn.execute('DELETE FROM carrito')
    db_conn.commit()
    st.rerun()