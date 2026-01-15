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

# --- FUNCIONES DE LA API (SOLUCIÓN PLAN FREE) ---
API_KEY = "48782dd5dcf6d4d9083eabc821da5e2d"
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "v3.football.api-sports.io"
}

def obtener_partidos_free(liga_id):
    """Consulta partidos por fecha para evitar el error del plan gratuito."""
    hoy = datetime.now().strftime("%Y-%m-%d")
    # Consultamos hoy
    url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2025&date={hoy}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10).json()
        partidos = res.get('response', [])
        
        # Si no hay partidos hoy, intentamos con mañana automáticamente
        if not partidos:
            manana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            url_manana = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2025&date={manana}"
            res_m = requests.get(url_manana, headers=HEADERS, timeout=10).json()
            partidos = res_m.get('response', [])
            
        return partidos
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return []

# --- INTERFAZ DE USUARIO ---
st.title("🏆 Dashboard de Inteligencia Deportiva")
st.markdown("---")

# Sidebar: Ligas y Filtros
st.sidebar.header("Control de Ligas")
liga_seleccionada = st.sidebar.selectbox(
    "Selecciona Competición", 
    ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
)

ids_ligas = {
    "Premier League": 39, 
    "La Liga": 140, 
    "Serie A": 135, 
    "Bundesliga": 78, 
    "Ligue 1": 61
}

col_analisis, col_carrito = st.columns([2, 1])

with col_analisis: