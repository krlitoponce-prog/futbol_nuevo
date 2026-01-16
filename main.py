import streamlit as st
import sqlite3
import os
from datetime import datetime
import random
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v20", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v20.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- MOTOR DE CÁLCULO ESTABLE ---
def obtener_analisis_completo(h, a, arb):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    p15, p25, p1t = random.randint(85, 98), random.randint(45, 78), random.randint(60, 92)
    c15, c25 = round(random.uniform(1.22, 1.38), 2), round(random.uniform(1.70, 2.15), 2)
    return {"p15": p15, "p25": p25, "p1t": p1t, "c15": c15, "c25": c25,
            "corners": random.choice(["8.5+", "9.5+", "10.5+"]),
            "t_rango": random.choice(["2-4", "5-8"]), "roja": random.choice(["ALTO", "BAJO"])}

# --- JORNADAS 100% COMPLETAS (NO SE ELIMINA NADA) ---
DATOS_REALES = {
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "17/01 7:30 a.m.", "arb": "Michael Oliver"},
        {"h": "Sunderland", "a": "Crystal Palace", "f": "17/01 10:00 a.m.", "arb": "Robert Jones"},
        {"h": "Chelsea", "a": "Brentford", "f": "17/01 10:00 a.m.", "arb": "Anthony Taylor"},
        {"h": "Liverpool", "a": "Burnley", "f": "17/01 10:00 a.m.", "arb": "Paul Tierney"},
        {"h": "Tottenham", "a": "West Ham", "f": "17/01 10:00 a.m.", "arb": "Simon Hooper"},
        {"h": "Leeds", "a": "Fulham", "f": "17/01 10:00 a.m.", "arb": "Chris Kavanagh"},
        {"h": "Nottingham Forest", "a": "Arsenal", "f": "17/01 12:30 p.m.", "arb": "Jarred Gillett"},
        {"h": "Wolves", "a": "Newcastle", "f": "18/01 9:00 a.m.", "arb": "Tim Robinson"},
        {"h": "Aston Villa", "a": "Everton", "f": "18/01 11:30 a.m.", "arb": "John Brooks"},
        {"h": "Brighton", "a": "Bournemouth", "f": "19/01 3:00 p.m.", "arb": "Andrew Madley"}
    ],
    "Ligue 1 (Francia)": [
        {"h": "Mónaco", "a": "Lorient", "f": "16/01 1:00 p.m.", "arb": "Benoît Bastien"},
        {"h": "PSG", "a": "Lille", "f": "16/01 3:00 p.m.", "arb": "Clément Turpin"},
        {"h": "Lens", "a": "Auxerre", "f": "17/01 11:00 a.m.", "arb": "Dechepy"},
        {"h": "Toulouse", "a": "Niza", "f": "17/01 1:00 p.m.", "arb": "Angoula"},
        {"h": "Angers", "a": "Marsella", "f": "17/01 3:05 p.m.", "arb": "Buquet"},
        {"h": "Estrasburgo", "a": "Metz", "f": "18/01 9:00 a.m.", "arb": "Pignard"},
        {"h": "Rennes", "a": "Le Havre", "f": "18/01 11:15 a.m.", "arb": "Frappart"},
        {"h": "Nantes", "a": "Paris FC", "f": "18/01 11:15 a.m.", "arb": "Millot"},
        {"h": "Lyon", "a": "Brest", "f": "18/01 2:45 p.m.", "arb": "Lissorgue"}
    ],
    "Primeira Liga (Portugal)": [
        {"h": "Sporting CP", "a": "Casa Pia", "f": "16/01", "arb": "Pereira"},
        {"h": "Gil Vicente", "a": "Nacional", "f": "17/01", "arb": "Nogueira"},
        {"h": "AVS", "a": "Arouca", "f": "17/01", "arb": "Pinheiro"},
        {"h": "Alverca", "a": "Moreirense", "f": "17/01", "arb": "Godinho"},
        {"h": "Rio Ave", "a": "Benfica", "f": "17/01", "arb": "Pereira"},
        {"h": "Santa Clara", "a": "Famalicão", "f": "18/01", "arb": "Torres"},
        {"h": "Tondela", "a": "Braga", "f": "18/01", "arb": "Correia"},
        {"h": "Guimarães", "a": "Oporto", "f": "18/01", "arb": "Gonçalves"},
        {"h": "Estrela", "a": "Estoril", "f": "19/01", "arb": "Ramalho"}
    ],
    "UEFA Champions League": [
        {"h": "Kairat", "a": "Club Brujas", "f": "20/01", "arb": "Zwayer"},
        {"h": "Bodø/Glimt", "a": "Man. City", "f": "20/01", "arb": "Oliver"},
        {"h": "Villarreal", "a": "Ajax", "f": "20/01", "arb": "Taylor"},
        {"h": "Tottenham", "a": "Dortmund", "f": "20/01", "arb": "Marciniak"},
        {"h": "Inter", "a": "Arsenal", "f": "20/01", "arb": "Makkelie"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "20/01", "arb": "Vincic"},
        {"h": "København", "a": "Napoli", "f": "20/01", "arb": "Turpin"},
        {"h": "Galatasaray", "a": "Atlético Madrid", "f": "21/01", "arb": "Schärer"},
        {"h": "Slavia Praga", "a": "Barcelona", "f": "21/01", "arb": "Massa"}
    ],
    "Serie A (Italia)": [
        {"h": "Inter", "a": "Empoli", "f": "18/01", "arb": "Massa"},
        {"h": "Juventus", "a": "Milan", "f": "19/01", "arb": "Orsato"},
        {"h": "Lazio", "a": "Napoli", "f": "19/01", "arb": "Guida"},
        {"h": "Roma", "a": "Atalanta", "f": "19/01", "arb": "Maresca"}
    ],
    "La Liga (España)": [
        {"h": "Real Madrid", "a": "Levante", "f": "17/01", "arb": "Alberola"},
        {"h": "Barcelona", "a": "Real Sociedad", "f": "18/01", "arb": "Hernández"},
        {"h": "Girona", "a": "Sevilla", "f": "17/01", "arb": "Busquets"}
    ],
    "Bundesliga (Alemania)": [
        {"h": "RB Leipzig", "a": "Bayern", "f": "17/01", "arb": "Aytekin"},
        {"h": "Dortmund", "a": "St. Pauli", "f": "17/01", "arb": "Brych"},
        {"h": "Werder Bremen", "a": "Frankfurt", "f": "16/01", "arb": "Zwayer"}
    ],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Ortega"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01", "arb": "Sampaio"}],
    "UEFA Europa League": [{"h": "Man. United", "a": "Roma", "f": "22/01", "arb": "Manzano"}]
}

# --- INTERFAZ ---
st.sidebar.title("⚽ PANEL DE CONTROL")
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
    # FILTRO DE ORO
    if st.button("💎 ANALIZAR Y AUTO-GUARDAR PICKS DE ORO"):
        partidos = DATOS_REALES[liga_sel]
        for p in partidos:
            res = obtener_analisis_completo(p['h'], p['a'], p['arb'])
            if res['p15'] > 94:
                txt = f"🔥 {p['h']} vs {p['a']} | Confianza: {res['p15']}%"
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
                    txt = f"📌 {p['h']} vs {p['a']} | Confianza: {s['p15']}%"
                    db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                    db_conn.commit()
                    st.rerun()
            with b2:
                msg = f"*REPORTE ELITE*\n\n🔥 *{p['h']} vs {p['a']}*\n🟢 Prob. +1.5 Goles: {s['p15']}%"
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"):
            st.caption(f); st.write(d)
    if st.sidebar.button("🗑️ Vaciar Carrito"):
        db_conn.execute('DELETE FROM carrito'); db_conn.commit(); st.rerun()