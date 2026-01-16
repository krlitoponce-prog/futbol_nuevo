import streamlit as st
import sqlite3
import os
from datetime import datetime
import random
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v21", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v21.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- MOTOR DE CÁLCULO ---
def obtener_analisis_completo(h, a, arb):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    p15, p25, p1t = random.randint(85, 98), random.randint(45, 78), random.randint(60, 92)
    return {"p15": p15, "p25": p25, "p1t": p1t, "corners": random.choice(["8.5+", "9.5+", "10.5+"]),
            "t_rango": random.choice(["3-5", "6-9"]), "roja": random.choice(["ALTO", "BAJO"])}

# --- BASE DE DATOS DE PARTIDOS (12 LIGAS COMPLETAS) ---
DATOS_REALES = {
    "Serie A (Italia)": [
        {"h": "AC Pisa 1909", "a": "Atalanta BC", "f": "Vie 16/01", "arb": "Orsato"},
        {"h": "Lazio", "a": "Como", "f": "Sáb 17/01", "arb": "Guida"},
        {"h": "Monza", "a": "Fiorentina", "f": "Sáb 17/01", "arb": "Doveri"},
        {"h": "Bologna", "a": "Roma", "f": "Dom 18/01", "arb": "Maresca"},
        {"h": "Inter", "a": "Empoli", "f": "Dom 18/01", "arb": "Massa"},
        {"h": "Juventus", "a": "Milan", "f": "Lun 19/01", "arb": "Colombo"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "Sáb 17/01", "arb": "Oliver"},
        {"h": "Chelsea", "a": "Brentford", "f": "Sáb 17/01", "arb": "Taylor"},
        {"h": "Liverpool", "a": "Burnley", "f": "Sáb 17/01", "arb": "Tierney"},
        {"h": "Tottenham", "a": "West Ham", "f": "Sáb 17/01", "arb": "Hooper"},
        {"h": "Arsenal", "a": "Everton", "f": "Dom 18/01", "arb": "Madley"},
        {"h": "Wolves", "a": "Newcastle", "f": "Dom 18/01", "arb": "Robinson"}
    ],
    "La Liga (España)": [
        {"h": "Real Madrid", "a": "Levante", "f": "Sáb 17/01", "arb": "Alberola"},
        {"h": "Espanyol", "a": "Valladolid", "f": "Sáb 17/01", "arb": "Munuera"},
        {"h": "Getafe", "a": "Valencia", "f": "Dom 18/01", "arb": "Soto Grado"},
        {"h": "Barcelona", "a": "Real Sociedad", "f": "Dom 18/01", "arb": "Hernández"}
    ],
    "Ligue 1 (Francia)": [
        {"h": "PSG", "a": "Lille", "f": "Vie 16/01", "arb": "Turpin"},
        {"h": "Mónaco", "a": "Lorient", "f": "Vie 16/01", "arb": "Bastien"},
        {"h": "Lyon", "a": "Brest", "f": "Sáb 17/01", "arb": "Letexier"},
        {"h": "Marsella", "a": "Nantes", "f": "Dom 18/01", "arb": "Frappart"}
    ],
    "Bundesliga (Alemania)": [
        {"h": "Werder Bremen", "a": "Frankfurt", "f": "Vie 16/01", "arb": "Zwayer"},
        {"h": "Dortmund", "a": "St. Pauli", "f": "Sáb 17/01", "arb": "Brych"},
        {"h": "RB Leipzig", "a": "Bayern", "f": "Sáb 17/01", "arb": "Aytekin"},
        {"h": "Union Berlin", "a": "Mainz", "f": "Dom 18/01", "arb": "Stegemann"}
    ],
    "Primeira Liga (Portugal)": [
        {"h": "Sporting CP", "a": "Casa Pia", "f": "Vie 16/01", "arb": "Pereira"},
        {"h": "Benfica", "a": "Rio Ave", "f": "Sáb 17/01", "arb": "Pinheiro"},
        {"h": "Oporto", "a": "Guimarães", "f": "Dom 18/01", "arb": "Soares"}
    ],
    "UEFA Champions League": [
        {"h": "Inter", "a": "Arsenal", "f": "Mar 20/01", "arb": "Makkelie"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "Mar 20/01", "arb": "Vincic"},
        {"h": "Bayern", "a": "U. Saint-Gilloise", "f": "Mié 21/01", "arb": "Oliver"}
    ],
    "UEFA Europa League": [{"h": "Man. United", "a": "Roma", "f": "Jue 22/01", "arb": "Manzano"}],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Ortega"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01", "arb": "Raphael Claus"}],
    "Liga Argentina": [{"h": "Boca", "a": "River", "f": "Feb 01", "arb": "Tello"}],
    "Eredivisie (Holanda)": [{"h": "Ajax", "a": "PSV", "f": "Dom 18/01", "arb": "Gozubuyuk"}]
}

# --- INTERFAZ ---
st.sidebar.title("⚽ ANALIZADOR ELITE")
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
    # FILTRO DE ORO
    if st.button("💎 ANALIZAR Y GUARDAR PICKS DE ORO"):
        partidos = DATOS_REALES[liga_sel]
        for p in partidos:
            res = obtener_analisis_completo(p['h'], p['a'], p['arb'])
            if res['p15'] > 94:
                txt = f"🔥 {p['h']} vs {p['a']} | +1.5: {res['p15']}%"
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
        db_conn.commit()
        st.rerun()

    st.header(f"🏟️ Partidos: {liga_sel}")
    for p in DATOS_REALES[liga_sel]:
        s = obtener_analisis_completo(p['h'], p['a'], p['arb'])
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            st.caption(f"🗓️ {p['f']} | ⚖️ Árbitro: {p['arb']}")
            c1, c2, c3 = st.columns(3)
            with c1: st.success(f"🎯 Score: {random.randint(1,3)}-{random.randint(0,2)}"); st.info(f"🚩 Corners: {s['corners']}")
            with c2: st.warning(f"🟨 Tarjetas: {s['t_rango']}"); st.write(f"🟥 Roja: {s['roja']}")
            with c3: st.write(f"⏱️ 1T: {s['p1t']}%"); st.write(f"🟢 +1.5: {s['p15']}%")
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"💾 Guardar", key=f"s_{p['h']}_{p['f']}"):
                    txt = f"📌 {p['h']} vs {p['a']} | Conf: {s['p15']}%"
                    db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                    db_conn.commit()
                    st.rerun()
            with b2:
                msg = f"*REPORTE ELITE*\n\n🔥 *{p['h']} vs {p['a']}*\n🟢 Prob. +1.5: {s['p15']}%"
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"):
            st.caption(f); st.write(d)
    if st.sidebar.button("🗑️ Vaciar Carrito"):
        db_conn.execute('DELETE FROM carrito'); db_conn.commit(); st.rerun()