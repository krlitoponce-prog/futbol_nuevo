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
    # Aseguramos que la tabla exista SIEMPRE al iniciar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            info TEXT,
            fecha_registro TEXT
        )
    ''')
    conn.commit()
    return conn

# Inicializar conexión
db_conn = init_db()

# --- FUNCIONES DE LA API (SOLUCIÓN PLAN FREE) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "v3.football.api-sports.io"
}

def obtener_partidos_free(liga_id):
    hoy = datetime.now().strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2025&date={hoy}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10).json()
        partidos = res.get('response', [])
        
        if not partidos:
            manana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            url_manana = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2025&date={manana}"
            res_m = requests.get(url_manana, headers=HEADERS, timeout=10).json()
            partidos = res_m.get('response', [])
            
        return partidos
    except Exception as e:
        return []

# --- INTERFAZ DE USUARIO ---
st.title("🏆 Dashboard de Inteligencia Deportiva")
st.markdown("---")

# Sidebar
st.sidebar.header("Control de Ligas")
liga_seleccionada = st.sidebar.selectbox(
    "Selecciona Competición", 
    ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
)

ids_ligas = {"Premier League": 39, "La Liga": 140, "Serie A": 135, "Bundesliga": 78, "Ligue 1": 61}

col_analisis, col_carrito = st.columns([2, 1])

with col_analisis:
    st.header(f"Partidos: {liga_seleccionada}")
    lista_partidos = obtener_partidos_free(ids_ligas[liga_seleccionada])
    
    if not lista_partidos:
        st.info("No hay partidos para hoy ni mañana. Prueba seleccionando otra liga en el menú izquierdo.")
    else:
        for p in lista_partidos:
            home = p['teams']['home']['name']
            away = p['teams']['away']['name']
            referee = p['fixture']['referee'] or "Por confirmar"
            hora = p['fixture']['date'][11:16]
            p_id = p['fixture']['id']
            
            with st.container(border=True):
                st.subheader(f"{home} vs {away} 🕒 {hora}")
                st.write(f"⚖️ **Juez:** {referee}")
                
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
                
                if st.button(f"Guardar {home}", key=f"btn_{p_id}"):
                    resumen = f"{home} vs {away} | Pred: 2-1 | Goles: +2.5"
                    fecha_reg = datetime.now().strftime("%d/%m %H:%M")
                    cursor = db_conn.cursor()
                    cursor.execute('INSERT INTO carrito (info, fecha_registro) VALUES (?, ?)', (resumen, fecha_reg))
                    db_conn.commit()
                    st.rerun() # Refresca para mostrar en el carrito al instante

with col_carrito:
    st.header("🛒 Carrito")
    try:
        cursor = db_conn.cursor()
        cursor.execute('SELECT info, fecha_registro FROM carrito ORDER BY id DESC')
        registros = cursor.fetchall()
        
        if not registros:
            st.write("Carrito vacío.")
        else:
            for info, fecha in registros:
                with st.chat_message("assistant"):
                    st.write(f"**{fecha}**")
                    st.write(info)
    except:
        st.error("Error al cargar el carrito. Intenta reiniciar la app.")

# Botón para limpiar
if st.sidebar.button("Borrar Todo el Carrito"):
    db_conn.execute('DELETE FROM carrito')
    db_conn.commit()
    st.rerun()