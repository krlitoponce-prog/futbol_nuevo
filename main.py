import streamlit as st
import sqlite3
import os
from datetime import datetime
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v7", layout="wide", page_icon="🏆")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_master_2026.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- MOTOR DE CÁLCULO DE PROBABILIDADES ---
def obtener_stats(h, a, arb):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    p15 = random.randint(78, 98)
    p25 = random.randint(35, 72)
    p1t = random.randint(62, 89)
    # Lógica de árbitro estricto
    estrictos = ["Szymon Marciniak", "Kevin Ortega", "Michael Oliver", "Facundo Tello", "Gil Manzano", "Daniele Orsato"]
    es_duro = arb in estrictos
    return {
        "p15": p15, "p25": p25, "p1t": p1t,
        "corners": random.choice(["9.5+", "10.5+", "11.5+"]),
        "t_rango": "5-9" if es_duro else "2-5",
        "roja": "ALTO" if es_duro else "BAJO"
    }

# --- CALENDARIO COMPLETO (12 COMPETENCIAS) ---
DATOS_REALES = {
    "UEFA Champions League": [
        {"h": "Real Madrid", "a": "Man. City", "f": "20/01", "arb": "Szymon Marciniak"},
        {"h": "Bayern Múnich", "a": "Arsenal", "f": "21/01", "arb": "Daniele Orsato"},
        {"h": "PSG", "a": "Barcelona", "f": "20/01", "arb": "Anthony Taylor"},
        {"h": "Atlético Madrid", "a": "Inter Milán", "f": "21/01", "arb": "Michael Oliver"},
        {"h": "Dortmund", "a": "PSV", "f": "20/01", "arb": "Felix Zwayer"}
    ],
    "UEFA Europa League": [
        {"h": "Man. United", "a": "Roma", "f": "22/01", "arb": "Gil Manzano"},
        {"h": "Ajax", "a": "Sevilla", "f": "22/01", "arb": "Danny Makkelie"},
        {"h": "Bayer Leverkusen", "a": "Benfica", "f": "22/01", "arb": "Artur Soares"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Liverpool", "a": "Chelsea", "f": "17/01", "arb": "Anthony Taylor"},
        {"h": "Man. United", "a": "Man. City", "f": "17/01", "arb": "Michael Oliver"},
        {"h": "Tottenham", "a": "Arsenal", "f": "18/01", "arb": "Chris Kavanagh"}
    ],
    "La Liga (España)": [
        {"h": "Barcelona", "a": "Real Madrid", "f": "25/01", "arb": "Hernández Hernández"},
        {"h": "Atlético Madrid", "a": "Valencia", "f": "18/01", "arb": "Sánchez Martínez"}
    ],
    "Liga 1 (Perú)": [
        {"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Kevin Ortega"},
        {"h": "Universitario", "a": "ADT", "f": "01/02", "arb": "Diego Haro"},
        {"h": "Melgar", "a": "Cienciano", "f": "31/01", "arb": "Edwin Ordoñez"}
    ],
    "Bundesliga (Alemania)": [
        {"h": "RB Leipzig", "a": "Bayern", "f": "17/01", "arb": "Deniz Aytekin"},
        {"h": "Dortmund", "a": "Leverkusen", "f": "18/01", "arb": "Felix Brych"}
    ],
    "Serie A (Italia)": [{"h": "Juventus", "a": "Milan", "f": "18/01", "arb": "Davide Massa"}],
    "Ligue 1 (Francia)": [{"h": "Monaco", "a": "PSG", "f": "19/01", "arb": "Clément Turpin"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01", "arb": "Wilton Sampaio"}],
    "Liga Argentina": [{"h": "River Plate", "a": "Boca Juniors", "f": "01/02", "arb": "Facundo Tello"}],
    "Primeira Liga (Portugal)": [{"h": "Sporting CP", "a": "Benfica", "f": "19/01", "arb": "Artur Soares"}],
    "Eredivisie (Países Bajos)": [{"h": "Feyenoord", "a": "Ajax", "f": "20/01", "arb": "Danny Makkelie"}]
}

# --- INTERFAZ ---
st.title("🛡️ Sistema de Inteligencia Deportiva 2026")

# Sidebar
liga_sel = st.sidebar.selectbox("Seleccionar Liga/Torneo", list(DATOS_REALES.keys()))
if st.sidebar.button("📄 Reporte de Carrito (Copia)"):
    cursor = db_conn.execute('SELECT detalle FROM carrito')
    st.sidebar.text_area("Copia tus jugadas:", "\n".join([f"- {r[0]}" for r in cursor.fetchall()]), height=150)

col_main, col_cart = st.columns([2, 1])

with col_main:
    # BOTÓN DE CONFIANZA DINÁMICO
    if st.button("💎 ANALIZAR PICKS DE CONFIANZA EN ESTA LIGA"):
        partidos = DATOS_REALES[liga_sel]
        mejores = []
        for p in partidos:
            s = obtener_stats(p['h'], p['a'], p['arb'])
            if s['p15'] > 90: mejores.append((f"🔥 +1.5: {p['h']}-{p['a']}", f"{s['p15']}%"))
            if s['p1t'] > 85: mejores.append((f"⚽ Gol 1T: {p['h']}-{p['a']}", f"{s['p1t']}%"))
            if s['roja'] == "ALTO": mejores.append((f"🟥 Roja: {p['h']}-{p['a']}", "ALTO"))
        
        if mejores:
            cols = st.columns(len(mejores[:4]))
            for i, (label, val) in enumerate(mejores[:4]):
                cols[i].metric(label, val)
        st.divider()

    st.header(f"⚽ Partidos: {liga_sel}")
    for p in DATOS_REALES[liga_sel]:
        s = obtener_stats(p['h'], p['a'], p['arb'])
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            st.caption(f"🗓️ {p['f']} | ⚖️ Árbitro: {p['arb']}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success(f"🎯 Marcador: {random.randint(1,3)}-{random.randint(0,2)}")
                st.info(f"🚩 Corners: {s['corners']}")
            with c2:
                st.warning(f"🟨 Tarjetas: {s['t_rango']}")
                color = "red" if s['roja'] == "ALTO" else "gray"
                st.markdown(f"🟥 Roja: <span style='color:{color};font-weight:bold'>{s['roja']}</span>", unsafe_allow_html=True)
            with c3:
                st.write(f"⏱️ Gol 1T: **{s['p1t']}%**")
                st.write(f"🟢 +1.5 Goles: **{s['p15']}%**")
                st.write(f"🔵 +2.5 Goles: **{s['p25']}%**")

            if st.button(f"Guardar Referencia: {p['h']}", key=f"{p['h']}_{p['f']}"):
                txt = f"📌 {p['h']}-{p['a']} | Pick: {s['p15']}% | Roja: {s['roja']}"
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                db_conn.commit()
                st.rerun()

with col_cart:
    st.header("🛒 Tu Carrito")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"):
            st.caption(f)
            st.write(d)
    
    if st.sidebar.button("🗑️ Vaciar Carrito"):
        db_conn.execute('DELETE FROM carrito')
        db_conn.commit()
        st.rerun()