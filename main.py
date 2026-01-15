import streamlit as st
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Analizador Fútbol Pro 2026", layout="wide", page_icon="⚽")

# --- BASE DE DATOS (CARRITO PERMANENTE) ---
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

# --- DATOS DE LA JORNADA (SIMULACIÓN 2026) ---
def obtener_jornada_completa():
    return [
        {"home": "Arsenal", "away": "Man City", "hora": "12:30", "pred": "1-1", "corners": "10.5", "amarillas": "5.5+"},
        {"home": "Liverpool", "away": "Chelsea", "hora": "15:00", "pred": "2-1", "corners": "9.5", "amarillas": "4.5+"},
        {"home": "Man United", "away": "Tottenham", "hora": "17:30", "pred": "2-2", "corners": "11.5", "amarillas": "6.5+"},
        {"home": "Newcastle", "away": "Aston Villa", "hora": "15:00", "pred": "3-2", "corners": "10.0", "amarillas": "4.0+"},
        {"home": "Brighton", "away": "West Ham", "hora": "15:00", "pred": "2-0", "corners": "8.5", "amarillas": "3.5+"}
    ]

# --- INTERFAZ ---
st.title("🏆 Dashboard de Inteligencia Deportiva 2026")
st.sidebar.header("Panel de Control")

liga = st.sidebar.selectbox("Liga", ["Premier League"])
fecha = st.sidebar.date_input("Fecha de Análisis", datetime(2026, 1, 17))

col_p, col_c = st.columns([2, 1])

with col_p:
    st.header(f"Partidos: {liga}")
    for p in obtener_jornada_completa():
        with st.container(border=True):
            st.subheader(f"{p['home']} vs {p['away']} 🕒 {p['hora']}")
            
            # LOS 6 PUNTOS CLAVE (DISEÑO SOLICITADO)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success(f"🎯 Marcador: {p['pred']}")
                st.warning(f"🟨 Amarillas: {p['amarillas']}")
            with c2:
                st.info("⚽ Goles: +2.5")
                st.error("🟥 Rojas: Riesgo Bajo")
            with c3:
                st.write("⏱️ Goles 1T: 70%")
                st.write(f"🚩 Corners: {p['corners']}")
            
            # Input para nota personalizada
            nota_usuario = st.text_input("Añadir observación", key=f"note_{p['home']}")
            
            if st.button(f"Guardar Referencia: {p['home']}", key=f"btn_{p['home']}"):
                resumen = f"📌 {p['home']} vs {p['away']} | Pred: {p['pred']} | Nota: {nota_usuario}"
                fecha_reg = datetime.now().strftime("%d/%m %H:%M")
                
                cursor = db_conn.cursor()
                cursor.execute('INSERT INTO carrito (info, fecha_registro) VALUES (?, ?)', (resumen, fecha_reg))
                db_conn.commit()
                st.rerun()

with col_c:
    st.header("🛒 Carrito Permanente")
    st.caption("Los datos se guardan aunque reinicies la app.")
    
    cursor = db_conn.cursor()
    cursor.execute('SELECT info, fecha_registro FROM carrito ORDER BY id DESC')
    registros = cursor.fetchall()
    
    if not registros:
        st.write("El carrito está vacío.")
    else:
        for info, fecha_reg in registros:
            with st.chat_message("assistant"):
                st.caption(f"Guardado el: {fecha_reg}")
                st.write(info)
        
        st.divider()
        if st.sidebar.button("🗑️ Vaciar Todo el Carrito"):
            db_conn.execute('DELETE FROM carrito')
            db_conn.commit()
            st.rerun()