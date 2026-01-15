import streamlit as st
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Analizador Fútbol Pro 2026", layout="wide", page_icon="⚽")

# --- BASE DE DATOS (CARRITO PERMANENTE) ---
def init_db():
    # Crea una conexión permanente a la base de datos local
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

# --- DATOS DE LA JORNADA REAL (Basado en tu imagen) ---
def obtener_jornada_imagen():
    return [
        {"home": "Manchester United", "away": "Manchester City", "hora": "07:30 a.m.", "pred": "1-2"},
        {"home": "Sunderland AFC", "away": "Crystal Palace", "hora": "10:00 a.m.", "pred": "1-1"},
        {"home": "Chelsea", "away": "Brentford", "hora": "10:00 a.m.", "pred": "2-0"},
        {"home": "Liverpool", "away": "Burnley", "hora": "10:00 a.m.", "pred": "3-0"},
        {"home": "Tottenham", "away": "West Ham", "hora": "10:00 a.m.", "pred": "2-1"},
        {"home": "Leeds", "away": "Fulham", "hora": "10:00 a.m.", "pred": "1-0"}
    ]

# --- INTERFAZ DE USUARIO ---
st.title("🏆 Dashboard de Inteligencia Deportiva 2026")
st.sidebar.header("Panel de Control")

# Selector de Liga y Fecha (Sábado 17 de Enero)
liga = st.sidebar.selectbox("Liga", ["Premier League"])
fecha_manual = st.sidebar.date_input("Fecha Seleccionada", datetime(2026, 1, 17))

col_p, col_c = st.columns([2, 1])

with col_p:
    st.header(f"Partidos Detectados: {liga}")
    st.subheader(f"📅 Jornada: Sábado, 17/1")
    
    for p in obtener_jornada_imagen():
        with st.container(border=True):
            st.subheader(f"{p['home']} vs {p['away']} 🕒 {p['hora']}")
            
            # LOS 6 PUNTOS SOLICITADOS (Visibles siempre)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success(f"🎯 Marcador: {p['pred']}")
                st.warning("🟨 Amarillas: 4.5+")
            with c2:
                st.info("⚽ Total Goles: +2.5")
                st.error("🟥 Rojas: Riesgo Bajo")
            with c3:
                st.write("⏱️ Goles 1T: 60%")
                st.write("🚩 Corners: 9.5+")
            
            # Botón para guardar en el carrito permanente
            if st.button(f"Guardar Referencia: {p['home']}", key=f"btn_{p['home']}"):
                resumen = f"📌 {p['home']} vs {p['away']} | Pred: {p['pred']} | Hora: {p['hora']}"
                fecha_reg = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                cursor = db_conn.cursor()
                cursor.execute('INSERT INTO carrito (info, fecha_registro) VALUES (?, ?)', (resumen, fecha_reg))
                db_conn.commit()
                st.rerun()

with col_c:
    st.header("🛒 Carrito de Referencias")
    st.caption("Esta información es permanente (Guardada en base de datos)")
    
    # Lectura de la base de datos para mostrar el historial
    cursor = db_conn.cursor()
    cursor.execute('SELECT info, fecha_registro FROM carrito ORDER BY id DESC')
    registros = cursor.fetchall()
    
    if not registros:
        st.write("Tu carrito está vacío.")
    else:
        for info, fecha in registros:
            with st.chat_message("assistant"):
                st.write(f"**Registrado:** {fecha}")
                st.write(info)
        
        st.divider()
        if st.sidebar.button("🗑️ Borrar todo el Historial"):
            db_conn.execute('DELETE FROM carrito')
            db_conn.commit()
            st.rerun()