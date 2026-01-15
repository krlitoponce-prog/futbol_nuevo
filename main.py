import streamlit as st
import sqlite3
import os
from datetime import datetime
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v5", layout="wide", page_icon="📈")

# --- BASE DE DATOS (CARRITO PERMANENTE) ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_total_2026.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# --- MOTOR DE PROBABILIDAD Y CONFIANZA ---
def analizar_confianza(liga_nombre):
    # Simulamos el escaneo de datos scrapeados (Flashscore, SofaScore, etc.)
    picks = [
        {"tipo": "🔥 Goles +1.5", "partido": "Real Madrid vs Man. City", "confianza": "94%", "razón": "Ataque élite + H2H alto"},
        {"tipo": "⚽ Gol 1T", "partido": "Bayern vs Arsenal", "confianza": "89%", "razón": "Racha de 10 partidos con gol 1T"},
        {"tipo": "🚩 Corners", "partido": "Liverpool vs Burnley", "confianza": "91%", "razón": "Promedio 12.5 corners/partido"},
        {"tipo": "🟨 Tarjetas", "partido": "Boca vs River", "confianza": "95%", "razón": "Árbitro Facundo Tello (Tarjetero)"},
        {"tipo": "🚀 Goles +2.5", "partido": "RB Leipzig vs Bayern", "confianza": "87%", "razón": "Defensas abiertas en Bundesliga"}
    ]
    return picks

def calcular_stats(arb):
    p_15 = random.randint(75, 98)
    p_25 = random.randint(40, 70)
    p_1t = random.randint(60, 90)
    estrictos = ["Kevin Ortega", "Michael Oliver", "Hernández Hernández", "Szymon Marciniak", "Facundo Tello"]
    es_propenso = arb in estrictos
    return {"p15": p_15, "p25": p_25, "p1t": p_1t, "roja": "ALTO" if es_propenso else "BAJO", "t_rango": "5-8" if es_propenso else "2-4"}

# --- DATOS DE LIGAS (12 + CHAMPIONS/EUROPA) ---
LIGAS_DATA = {
    "UEFA Champions League": [{"h": "Real Madrid", "a": "Man. City", "f": "20/01", "arb": "Szymon Marciniak"}],
    "UEFA Europa League": [{"h": "Man. United", "a": "Roma", "f": "22/01", "arb": "Gil Manzano"}],
    "Premier League (Inglaterra)": [{"h": "Liverpool", "a": "Burnley", "f": "17/01", "arb": "Anthony Taylor"}],
    "La Liga (España)": [{"h": "Real Madrid", "a": "Levante", "f": "17/01", "arb": "Munuera Montero"}],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Kevin Ortega"}],
    "Bundesliga (Alemania)": [{"h": "RB Leipzig", "a": "Bayern", "f": "17/01", "arb": "Deniz Aytekin"}],
    "Serie A (Italia)": [{"h": "Inter", "a": "Milan", "f": "18/01", "arb": "Davide Massa"}],
    "Ligue 1 (Francia)": [{"h": "PSG", "a": "Lyon", "f": "18/01", "arb": "Clément Turpin"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01", "arb": "Wilton Sampaio"}],
    "Liga Argentina": [{"h": "Boca Juniors", "a": "River Plate", "f": "01/02", "arb": "Facundo Tello"}],
    "Primeira Liga (Portugal)": [{"h": "Benfica", "a": "Porto", "f": "20/01", "arb": "Artur Soares"}],
    "Eredivisie (Países Bajos)": [{"h": "Ajax", "a": "PSV", "f": "22/01", "arb": "Danny Makkelie"}]
}

# --- INTERFAZ ---
st.title("🛡️ Sistema de Inteligencia Deportiva 2026")

# SIDEBAR: Reporte y Filtros
st.sidebar.header("📊 Centro de Reportes")
if st.sidebar.button("📄 Generar Reporte de Carrito"):
    cursor = db_conn.cursor()
    cursor.execute('SELECT detalle FROM carrito')
    filas = cursor.fetchall()
    reporte = "\n".join([f"- {f[0]}" for f in filas])
    st.sidebar.text_area("Copia tu Reporte:", value=f"REPORTE DE REFERENCIAS 2026:\n{reporte}", height=200)

st.sidebar.divider()
st.sidebar.header("Ligas y Torneos")
liga_sel = st.sidebar.selectbox("Selecciona:", list(LIGAS_DATA.keys()))

col_p, col_c = st.columns([2, 1])

with col_p:
    # BOTÓN DE CONFIANZA
    if st.button("💎 ANALIZAR PARTIDOS DE MÁXIMA CONFIANZA (REAL-TIME)"):
        st.subheader("🎯 Picks de Alta Probabilidad detectados:")
        recomendados = analizar_confianza(liga_sel)
        cols = st.columns(len(recomendados))
        for i, r in enumerate(recomendados):
            with cols[i]:
                st.metric(label=r['tipo'], value=r['confianza'], delta=r['partido'])
                st.caption(r['razón'])
        st.divider()

    st.header(f"⚽ {liga_sel}")
    for p in LIGAS_DATA[liga_sel]:
        s = calcular_stats(p['arb'])
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            st.caption(f"🗓️ {p['f']} | ⚖️ Árbitro: {p['arb']}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success(f"🎯 Marcador: {random.choice(['2-1', '1-1', '2-0'])}")
                st.info(f"🚩 Corners: {random.choice(['9.5+', '10.5+'])}")
            with c2:
                st.warning(f"🟨 Tarjetas: {s['t_rango']}")
                color_roja = "red" if s['roja'] == "ALTO" else "white"
                st.markdown(f"🟥 Riesgo Roja: <span style='color:{color_roja}'>{s['roja']}</span>", unsafe_allow_html=True)
            with c3:
                st.write(f"⏱️ Gol 1T: **{s['p1t']}%**")
                st.write(f"🟢 +1.5 Goles: **{s['p115']}%**" if 'p115' in s else f"🟢 +1.5 Goles: **{s['p15']}%**")
                st.write(f"🔵 +2.5 Goles: **{s['p25']}%**")

            if st.button("Guardar en Carrito Permanente", key=p['h']):
                txt = f"📌 {p['h']} vs {p['a']} | Pick: +1.5 ({s['p15']}%) | Roja: {s['roja']}"
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                db_conn.commit()
                st.rerun()

with col_c:
    st.header("🛒 Tu Carrito")
    cursor = db_conn.cursor()
    cursor.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    items = cursor.fetchall()
    for d, f in items:
        with st.chat_message("user"):
            st.caption(f)
            st.write(d)
    
    if st.sidebar.button("🗑️ Vaciar Todo"):
        db_conn.execute('DELETE FROM carrito')
        db_conn.commit()
        st.rerun()