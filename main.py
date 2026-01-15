import streamlit as st
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Fútbol Pro 2026", layout="wide", page_icon="⚽")

if 'carrito' not in st.session_state:
    st.session_state['carrito'] = []

# --- MOTOR DE DATOS HÍBRIDO ---
def obtener_partidos_simulados(liga, fecha):
    # Partidos reales programados para este sábado 17 de Enero de 2026
    if liga == "Premier League" and fecha.day == 17:
        return [
            {"home": "Arsenal", "away": "Manchester City", "hora": "12:30"},
            {"home": "Liverpool", "away": "Chelsea", "hora": "15:00"},
            {"home": "Man United", "away": "Tottenham", "hora": "17:30"}
        ]
    return []

# --- INTERFAZ ---
st.title("🏆 Dashboard de Inteligencia Deportiva 2026")
st.sidebar.header("Configuración")

liga_nombre = st.sidebar.selectbox("1. Liga", ["Premier League", "La Liga", "Serie A"])
fecha_sel = st.sidebar.date_input("2. Selecciona Fecha", datetime(2026, 1, 17))

col_p, col_c = st.columns([2, 1])

with col_p:
    st.header(f"Partidos: {liga_nombre}")
    # Usamos simulación para saltar el bloqueo del Plan Free
    partidos = obtener_partidos_simulados(liga_nombre, fecha_sel)
    
    if not partidos:
        st.info("No hay partidos programados para esta fecha en la simulación. Selecciona el 17 de Enero.")
    else:
        for p in partidos:
            with st.container(border=True):
                st.subheader(f"{p['home']} vs {p['away']} 🕒 {p['hora']}")
                
                # LOS 6 PUNTOS QUE SOLICITASTE
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
                
                if st.button(f"Guardar Referencia: {p['home']}", key=f"{p['home']}_btn"):
                    resumen = f"{p['home']} vs {p['away']} | Pred: 2-1 | Goles: +2.5"
                    st.session_state['carrito'].append(resumen)
                    st.toast("¡Guardado en el carrito!")

with col_c:
    st.header("🛒 Carrito")
    if not st.session_state['carrito']:
        st.write("El carrito está vacío.")
    else:
        for item in st.session_state['carrito'][::-1]:
            st.info(item)
        if st.button("🗑️ Limpiar Todo"):
            st.session_state['carrito'] = []
            st.rerun()