import streamlit as st
import sqlite3
import os
from datetime import datetime
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v8 - Cuotas", layout="wide", page_icon="💰")

# --- BASE DE DATOS (CARRITO PERMANENTE) ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_master_2026.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- MOTOR DE PROBABILIDAD Y CUOTAS ---
def obtener_analisis_completo(h, a, arb):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    p15 = random.randint(78, 98)
    p25 = random.randint(35, 75)
    
    # Simulación de Cuotas Scrapeadas
    cuota_15 = round(random.uniform(1.20, 1.45), 2)
    cuota_25 = round(random.uniform(1.65, 2.30), 2)
    
    estrictos = ["Szymon Marciniak", "Kevin Ortega", "Michael Oliver", "Facundo Tello"]
    es_duro = arb in estrictos
    
    return {
        "p15": p15, "p25": p25, "c15": cuota_15, "c25": cuota_25,
        "corners": random.choice(["9.5+", "10.5+", "11.5+"]),
        "t_rango": "5-9" if es_duro else "2-5",
        "roja": "ALTO" if es_duro else "BAJO"
    }

# --- CALENDARIO INTEGRAL (12 COMPETENCIAS) ---
DATOS_REALES = {
    "UEFA Champions League": [
        {"h": "Real Madrid", "a": "Man. City", "f": "20/01", "arb": "Szymon Marciniak"},
        {"h": "Bayern Múnich", "a": "Arsenal", "f": "21/01", "arb": "Daniele Orsato"},
        {"h": "PSG", "a": "Barcelona", "f": "20/01", "arb": "Anthony Taylor"},
        {"h": "Atlético Madrid", "a": "Inter Milán", "f": "21/01", "arb": "Michael Oliver"}
    ],
    "UEFA Europa League": [
        {"h": "Man. United", "a": "Roma", "f": "22/01", "arb": "Gil Manzano"},
        {"h": "Ajax", "a": "Sevilla", "f": "22/01", "arb": "Danny Makkelie"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Liverpool", "a": "Chelsea", "f": "17/01", "arb": "Anthony Taylor"},
        {"h": "Man. United", "a": "Man. City", "f": "17/01", "arb": "Michael Oliver"},
        {"h": "Tottenham", "a": "Arsenal", "f": "18/01", "arb": "Chris Kavanagh"}
    ],
    "La Liga (España)": [
        {"h": "Barcelona", "a": "Real Madrid", "f": "25/01", "arb": "Hernández Hernández"},
        {"h": "Villarreal", "a": "Atlético Madrid", "f": "18/01", "arb": "Sánchez Martínez"}
    ],
    "Liga 1 (Perú)": [
        {"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Kevin Ortega"},
        {"h": "Universitario", "a": "ADT", "f": "01/02", "arb": "Diego Haro"},
        {"h": "Melgar", "a": "Cienciano", "f": "31/01", "arb": "Edwin Ordoñez"}
    ],
    "Bundesliga (Alemania)": [{"h": "RB Leipzig", "a": "Bayern", "f": "17/01", "arb": "Deniz Aytekin"}],
    "Serie A (Italia)": [{"h": "Juventus", "a": "Milan", "f": "18/01", "arb": "Davide Massa"}],
    "Ligue 1 (Francia)": [{"h": "Monaco", "a": "PSG", "f": "19/01", "arb": "Clément Turpin"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01", "arb": "Wilton Sampaio"}],
    "Liga Argentina": [{"h": "River Plate", "a": "Boca Juniors", "f": "01/02", "arb": "Facundo Tello"}],
    "Primeira Liga (Portugal)": [{"h": "Sporting CP", "a": "Benfica", "f": "19/01", "arb": "Artur Soares"}],
    "Eredivisie (Países Bajos)": [{"h": "Feyenoord", "a": "Ajax", "f": "20/01", "arb": "Danny Makkelie"}]
}

# --- INTERFAZ ---
st.title("🛡️ Sistema de Inteligencia Deportiva 2026")

liga_sel = st.sidebar.selectbox("Seleccionar Liga/Torneo", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2, 1])

with col_main:
    # BOTÓN DE CONFIANZA
    if st.button("💎 ANALIZAR PICKS CON MEJOR CUOTA (VALUE)"):
        st.subheader(f"🎯 Oportunidades en {liga_sel}")
        partidos = DATOS_REALES[liga_sel]
        mejores = []
        for p in partidos:
            s = obtener_analisis_completo(p['h'], p['a'], p['arb'])
            if s['p15'] > 85 and s['c15'] > 1.30:
                mejores.append((f"🔥 +1.5 Goles: {p['h']}", f"Cuota: {s['c15']}"))
        
        if mejores:
            cols = st.columns(len(mejores[:4]))
            for i, (label, val) in enumerate(mejores[:4]):
                cols[i].metric(label, val, "VALOR DETECTADO")
        st.divider()

    st.header(f"⚽ Partidos: {liga_sel}")
    for p in DATOS_REALES[liga_sel]:
        s = obtener_analisis_completo(p['h'], p['a'], p['arb'])
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            st.caption(f"🗓️ {p['f']} | ⚖️ Árbitro: {p['arb']}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success(f"🎯 Marcador: {random.randint(1,3)}-{random.randint(0,2)}")
                st.info(f"🚩 Corners: {s['corners']}")
                st.write(f"💵 Cuota +1.5: **{s['c15']}**")
            with c2:
                st.warning(f"🟨 Tarjetas: {s['t_rango']}")
                color = "red" if s['roja'] == "ALTO" else "gray"
                st.markdown(f"🟥 Roja: <span style='color:{color};font-weight:bold'>{s['roja']}</span>", unsafe_allow_html=True)
                st.write(f"💵 Cuota +2.5: **{s['c25']}**")
            with c3:
                st.write(f"⏱️ Gol 1T: **{s['p1t']}%**")
                st.write(f"🟢 +1.5 Goles: **{s['p15']}%**")
                st.write(f"🔵 +2.5 Goles: **{s['p25']}%**")

            if st.button(f"Guardar Referencia: {p['h']}", key=f"{p['h']}_{p['f']}"):
                txt = f"📌 {p['h']}-{p['a']} | Pick: +1.5 ({s['p15']}%) | Cuota: {s['c15']}"
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                db_conn.commit()
                st.rerun()

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"):
            st.caption(f)
            st.write(d)
    
    if st.sidebar.button("🗑️ Vaciar Carrito"):
        db_conn.execute('DELETE FROM carrito')
        db_conn.commit()
        st.rerun()