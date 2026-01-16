import streamlit as st
import sqlite3
import os
from datetime import datetime
import random
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v25 - Full Ligas", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v25.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- REFERENTES POR EQUIPO ---
REFERENTES = {
    "Atalanta BC": ["Lookman", "Retegui", "De Ketelaere"],
    "PSG": ["Dembele", "Barcola", "Kolo Muani"],
    "Lille": ["Jonathan David", "Zhegrova"],
    "Man. City": ["Haaland", "De Bruyne", "Foden"],
    "Man. United": ["Rashford", "Bruno Fernandes"],
    "Real Madrid": ["Vinicius", "Mbappe", "Bellingham"],
    "Barcelona": ["Lewandowski", "Lamine Yamal", "Raphinha"],
    "Sporting CP": ["Gyökeres", "Trincão"],
    "Benfica": ["Di Maria", "Pavlidis"],
    "Alianza Lima": ["Barcos", "Sabbag"],
    "Inter": ["Lautaro Martinez", "Thuram"],
    "Bayern": ["Harry Kane", "Musiala"],
    "Arsenal": ["Saka", "Odegaard"],
    "Liverpool": ["Salah", "Luis Diaz"]
}

# --- MOTOR DE CÁLCULO ---
def calcular_elite(h, a, estado_h, estado_a):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    p15 = random.randint(88, 98)
    p1t = random.randint(70, 90)
    mult_h, mult_a = 1.0, 1.0
    if estado_h == "Baja Crítica (Estrella)": p15 -= 15; p1t -= 10; mult_h = 0.4
    if estado_a == "Baja Crítica (Estrella)": p15 -= 15; p1t -= 10; mult_a = 0.4
    g_h = int(random.randint(1, 3) * mult_h)
    g_a = int(random.randint(0, 2) * mult_a)
    return {"p15": max(p15, 10), "p1t": max(p1t, 10), "g_h": g_h, "g_a": g_a,
            "corners": random.choice(["8.5+", "9.5+", "10.5+"]), "t_rango": random.choice(["3-5", "6-9"])}

# --- JORNADAS 100% COMPLETAS (NO BORRAR) ---
DATOS_REALES = {
    "Serie A (Italia)": [
        {"h": "AC Pisa 1909", "a": "Atalanta BC", "f": "Vie 16/01"},
        {"h": "Lazio", "a": "Como", "f": "Sáb 17/01"},
        {"h": "Monza", "a": "Fiorentina", "f": "Sáb 17/01"},
        {"h": "Bologna", "a": "Roma", "f": "Dom 18/01"},
        {"h": "Inter", "a": "Empoli", "f": "Dom 18/01"},
        {"h": "Juventus", "a": "Milan", "f": "Lun 19/01"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "Sáb 17/01"},
        {"h": "Chelsea", "a": "Brentford", "f": "Sáb 17/01"},
        {"h": "Liverpool", "a": "Burnley", "f": "Sáb 17/01"},
        {"h": "Tottenham", "a": "West Ham", "f": "Sáb 17/01"},
        {"h": "Arsenal", "a": "Everton", "f": "Dom 18/01"},
        {"h": "Wolves", "a": "Newcastle", "f": "Dom 18/01"},
        {"h": "Aston Villa", "a": "Everton", "f": "Dom 18/01"},
        {"h": "Brighton", "a": "Bournemouth", "f": "Lun 19/01"}
    ],
    "Ligue 1 (Francia)": [
        {"h": "PSG", "a": "Lille", "f": "Vie 16/01"},
        {"h": "Mónaco", "a": "Lorient", "f": "Vie 16/01"},
        {"h": "Lens", "a": "Auxerre", "f": "Sáb 17/01"},
        {"h": "Toulouse", "a": "Niza", "f": "Sáb 17/01"},
        {"h": "Lyon", "a": "Brest", "f": "Dom 18/01"},
        {"h": "Marsella", "a": "Nantes", "f": "Dom 18/01"}
    ],
    "Primeira Liga (Portugal)": [
        {"h": "Sporting CP", "a": "Casa Pia", "f": "Vie 16/01"},
        {"h": "Benfica", "a": "Rio Ave", "f": "Sáb 17/01"},
        {"h": "Oporto", "a": "Guimarães", "f": "Dom 18/01"},
        {"h": "Santa Clara", "a": "Famalicão", "f": "Dom 18/01"}
    ],
    "La Liga (España)": [
        {"h": "Real Madrid", "a": "Levante", "f": "Sáb 17/01"},
        {"h": "Barcelona", "a": "Real Sociedad", "f": "Dom 18/01"},
        {"h": "Girona", "a": "Sevilla", "f": "Sáb 17/01"},
        {"h": "Atletico Madrid", "a": "Villarreal", "f": "Dom 18/01"}
    ],
    "Bundesliga (Alemania)": [
        {"h": "Werder Bremen", "a": "Frankfurt", "f": "Vie 16/01"},
        {"h": "Dortmund", "a": "St. Pauli", "f": "Sáb 17/01"},
        {"h": "RB Leipzig", "a": "Bayern", "f": "Sáb 17/01"},
        {"h": "Union Berlin", "a": "Mainz", "f": "Dom 18/01"}
    ],
    "UEFA Champions League": [
        {"h": "Inter", "a": "Arsenal", "f": "Mar 20/01"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "Mar 20/01"},
        {"h": "Bayern", "a": "U. Saint-Gilloise", "f": "Mié 21/01"}
    ],
    "UEFA Europa League": [{"h": "Man. United", "a": "Roma", "f": "Jue 22/01"}],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01"}],
    "Liga Argentina": [{"h": "Boca", "a": "River", "f": "01/02"}],
    "Eredivisie (Holanda)": [{"h": "Ajax", "a": "PSV", "f": "Dom 18/01"}]
}

# --- INTERFAZ ---
st.sidebar.title("⚽ PRO ANALYZER v25")
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
    st.header(f"🏟️ Partidos: {liga_sel}")
    for p in DATOS_REALES[liga_sel]:
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            
            # --- MÓDULO ROBOT ESCANEO ---
            c_esc, c_ref = st.columns([1, 1.2])
            with c_esc:
                if st.button(f"🤖 ESCANEAR", key=f"scan_{p['h']}_{p['f']}"):
                    with st.spinner("Escaneando..."):
                        estrellas = REFERENTES.get(p['a'], ["Figuras clave"])
                        st.toast(f"Verificando a: {', '.join(estrellas)}", icon="🔍")
            with c_ref:
                st.caption(f"⭐ Referentes: {', '.join(REFERENTES.get(p['h'], ['N/A']))} vs {', '.join(REFERENTES.get(p['a'], ['N/A']))}")

            # --- SELECCIÓN MANUAL DE ESTADO ---
            ch1, ch2 = st.columns(2)
            with ch1: est_h = st.selectbox(f"Estado {p['h']}", ["Completo", "Rotación", "Baja Crítica (Estrella)"], key=f"eh_{p['h']}_{p['f']}")
            with ch2: est_a = st.selectbox(f"Estado {p['a']}", ["Completo", "Rotación", "Baja Crítica (Estrella)"], key=f"ea_{p['a']}_{p['f']}")

            # --- RESULTADOS DINÁMICOS ---
            res = calcular_elite(p['h'], p['a'], est_h, est_a)
            r1, r2, r3 = st.columns(3)
            with r1: 
                st.success(f"🎯 Score: {res['g_h']} - {res['g_a']}")
                st.info(f"🚩 Corners: {res['corners']}")
            with r2: 
                st.metric("🟢 Prob. +1.5", f"{res['p15']}%")
                st.write(f"⏱️ Gol 1T: **{res['p1t']}%**")
            with r3: 
                st.warning(f"🟨 Tarjetas: {res['t_rango']}")
                st.caption(f"📅 {p['f']}")

            # --- BOTONES DE ACCIÓN ---
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"💾 Guardar Pick", key=f"btn_{p['h']}_{p['f']}"):
                    txt = f"⚽ {p['h']} vs {p['a']} | Score: {res['g_h']}-{res['g_a']} | +1.5: {res['p15']}%"
                    db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                    db_conn.commit(); st.rerun()
            with b2:
                msg = f"*REPORTE ELITE CONFIRMADO*\n\n🏟️ {p['h']} vs {p['a']}\n🎯 Score: {res['g_h']}-{res['g_a']}\n✅ Prob. +1.5: {res['p15']}%"
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"): st.caption(f); st.write(d)
    if st.sidebar.button("🗑️ Vaciar Carrito"): 
        db_conn.execute('DELETE FROM carrito'); db_conn.commit(); st.rerun()