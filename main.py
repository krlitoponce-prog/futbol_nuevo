import streamlit as st
import requests
import sqlite3
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Analizador Fútbol Pro", layout="wide")

# --- CONEXIÓN BASE DE DATOS ---
def get_connection():
    conn = sqlite3.connect('carrito_web.db', check_same_thread=False)
    return conn

conn = get_connection()
conn.execute('CREATE TABLE IF NOT EXISTS carrito (id INTEGER PRIMARY KEY, info TEXT, fecha TEXT)')
conn.commit()

# --- MOTOR DE DATOS (CORREGIDO) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"

def traer_partidos(liga_id):
    # Intentamos traer los próximos 10 partidos sin importar la fecha exacta
    url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&next=10"
    headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # Si la API nos da error de credenciales
        if "errors" in data and data["errors"]:
            st.error(f"Error de API: {data['errors']}")
            return []
            
        return data.get('response', [])
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return []

# --- INTERFAZ WEB ---
st.title("⚽ Panel de Predicciones Elite")

# Sidebar
st.sidebar.header("Configuración")
liga_nombre = st.sidebar.selectbox("Selecciona una Liga", ["Premier League", "La Liga", "Serie A", "Bundesliga"])
ids = {"Premier League": 39, "La Liga": 140, "Serie A": 135, "Bundesliga": 78}

col_main, col_cart = st.columns([2, 1])

with col_main:
    st.subheader(f"Próximos Partidos: {liga_nombre}")
    with st.spinner('Cargando datos de la API...'):
        partidos = traer_partidos(ids[liga_nombre])
    
    if not partidos:
        st.warning("No se encontraron partidos próximos. Verifica tu API Key o la conexión.")
    else:
        for p in partidos:
            home = p['teams']['home']['name']
            away = p['teams']['away']['name']
            referee = p['fixture']['referee'] or "Árbitro no asignado"
            f_id = p['fixture']['id']
            
            with st.container(border=True):
                st.markdown(f"### {home} vs {away}")
                st.caption(f"⚖️ Juez: {referee}")
                
                # Los 6 puntos clave
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
                
                if st.button(f"Guardar {home} vs {away}", key=f_id):
                    fecha_str = datetime.now().strftime("%H:%M")
                    resumen = f"{home} vs {away} | Pred: 2-1 | Corners: 9.5"
                    conn.execute('INSERT INTO carrito (info, fecha) VALUES (?, ?)', (resumen, fecha_str))
                    conn.commit()
                    st.success("Guardado en Carrito")

with col_cart:
    st.subheader("🛒 Carrito de Referencias")
    cursor = conn.cursor()
    cursor.execute('SELECT info, fecha FROM carrito ORDER BY id DESC')
    filas = cursor.fetchall()
    
    if not filas:
        st.write("Tu carrito está vacío.")
    else:
        for row in filas:
            st.info(f"📅 {row[1]}\n{row[0]}")