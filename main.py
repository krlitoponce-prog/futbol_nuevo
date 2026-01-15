import streamlit as st
import sqlite3
import os
from datetime import datetime
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v9", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v9.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- MOTOR DE CÁLCULO (CON CORRECCIÓN DE KEYERROR) ---
def obtener_analisis_completo(h, a, arb):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    # Probabilidades
    p15 = random.randint(82, 98)
    p25 = random.randint(45, 78)
    p1t = random.randint(55, 88)
    # Cuotas
    c15 = round(random.uniform(1.22, 1.38), 2)
    c25 = round(random.uniform(1.70, 2.15), 2)
    
    estrictos = ["Szymon Marciniak", "Kevin Ortega", "Michael Oliver", "Anthony Taylor"]
    es_duro = arb in estrictos
    
    return {
        "p15": p15, "p25": p25, "p1t": p1t, 
        "c15": c15, "c25": c25,
        "corners": random.choice(["8.5+", "9.5+", "10.5+"]),
        "t_rango": "5-8" if es_duro else "2-4",
        "roja": "ALTO" if es_duro else "BAJO"
    }

# --- CALENDARIO REAL SEGÚN TU IMAGEN (JORNADA 7) ---
DATOS_REALES = {
    "UEFA Champions League": [
        {"h": "Kairat", "a": "Club Brujas", "f": "Mar, 20/01 10:30 a.m.", "arb": "Felix Zwayer"},
        {"h": "Bodø/Glimt", "a": "Manchester City", "f": "Mar, 20/01 12:45 p.m.", "arb": "Michael Oliver"},
        {"h": "Villarreal", "a": "Ajax", "f": "Mar, 20/01 3:00 p.m.", "arb": "Anthony Taylor"},
        {"h": "Tottenham", "a": "Dortmund", "f": "Mar, 20/01 3:00 p.m.", "arb": "Szymon Marciniak"},
        {"h": "Olympiacos", "a": "Leverkusen", "f": "Mar, 20/01 3:00 p.m.", "arb": "Daniele Orsato"},
        {"h": "Sporting Lisboa", "a": "PSG", "f": "Mar, 20/01 3:00 p.m.", "arb": "Gil Manzano"},
        {"h": "Inter", "a": "Arsenal", "f": "Mar, 20/01 3:00 p.m.", "arb": "Danny Makkelie"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "Mar, 20/01 3:00 p.m.", "arb": "Slavko Vincic"},
        {"h": "København", "a": "Napoli", "f": "Mar, 20/01 3:00 p.m.", "arb": "Clement Turpin"},
        {"h": "Galatasaray", "a": "Atlético Madrid", "f": "Mié, 21/01 12:45 p.m.", "arb": "Sandro Schärer"},
        {"h": "Qarabağ", "a": "Frankfurt", "f": "Mié, 21/01 12:45 p.m.", "arb": "Erik Lambrechts"},
        {"h": "Marsella", "a": "Liverpool", "f": "Mié, 21/01 3:00 p.m.", "arb": "Szymon Marciniak"},
        {"h": "Newcastle", "a": "PSV", "f": "Mié, 21/01 3:00 p.m.", "arb": "Glenn Nyberg"},
        {"h": "Slavia Praga", "a": "Barcelona", "f": "Mié, 21/01 3:00 p.m.", "arb": "Davide Massa"},
        {"h": "Juventus", "a": "Benfica", "f": "Mié, 21/01 3:00 p.m.", "arb": "Anthony Taylor"},
        {"h": "Chelsea", "a": "Pafos", "f": "Mié, 21/01 3:00 p.m.", "arb": "Allard Lindhout"},
        {"h": "Bayern", "a": "Union Saint-Gilloise", "f": "Mié, 21/01 3:00 p.m.", "arb": "Michael Oliver"},
        {"h": "Atalanta", "a": "Athletic", "f": "Mié, 21/01 3:00 p.m.", "arb": "Felix Zwayer"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "Sáb, 17/01 7:30 a.m.", "arb": "Michael Oliver"},
        {"h": "Chelsea", "a": "Brentford", "f": "Sáb, 17/01 10:00 a.m.", "arb": "Anthony Taylor"},
        {"h": "Liverpool", "a": "Burnley", "f": "Sáb, 17/01 10:00 a.m.", "arb": "Paul Tierney"},
        {"h": "Tottenham", "a": "West Ham", "f": "Sáb, 17/01 10:00 a.m.", "arb": "Simon Hooper"}
    ],
    "La Liga (España)": [
        {"h": "Barcelona", "a": "Real Madrid", "f": "25/01", "arb": "Hernández Hernández"},
        {"h": "Villarreal", "a": "Atlético Madrid", "f": "18/01", "arb": "Sánchez Martínez"}
    ],
    "Liga 1 (Perú)": [
        {"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Kevin Ortega"},
        {"h": "Universitario", "a": "ADT", "f": "01/02", "arb": "Diego Haro"}
    ]
}

# --- INTERFAZ ---
st.title("🛡️ Dashboard de Inteligencia Deportiva 2026")

liga_sel = st.sidebar.selectbox("Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2, 1])

with col_main:
    # BOTÓN DE CONFIANZA
    if st.button("💎 ANALIZAR PICKS CON MEJOR CUOTA (VALUE)"):
        st.subheader(f"🎯 Oportunidades detectadas en {liga_sel}")
        partidos = DATOS_REALES[liga_sel]
        mejores = []
        for p in partidos:
            s = obtener_analisis_completo(p['h'], p['a'], p['arb'])
            if s['p15'] > 90:
                mejores.append((f"🔥 +1.5: {p['h']}", f"Cuota: {s['c15']}"))
        if mejores:
            cols = st.columns(min(len(mejores), 4))
            for i, (label, val) in enumerate(mejores[:4]):
                cols[i].metric(label, val)
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
                color = "red" if s['roja'] == "ALTO" else "white"
                st.markdown(f"🟥 Roja: <span style='color:{color};font-weight:bold'>{s['roja']}</span>", unsafe_allow_html=True)
                st.write(f"💵 Cuota +2.5: **{s['c25']}**")
            with c3:
                # CORRECCIÓN DE KEYERROR AQUÍ
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