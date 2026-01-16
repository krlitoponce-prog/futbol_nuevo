import streamlit as st
import sqlite3
import os
from datetime import datetime
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v35 - Full Coherencia", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v35.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn
db_conn = init_db()

# --- MOTOR DE CÁLCULO (AJUSTADO PARA SUPERIORIDAD TÉCNICA) ---
def calcular_elite(h, a, estado_h, estado_a, arbitro):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    
    GIGANTES = ["Atalanta BC", "PSG", "Man. City", "Real Madrid", "Barcelona", "Inter", "Bayern", "Arsenal", "Liverpool", "Juventus", "Milan"]
    g_h, g_a = 0, 0

    # LÓGICA DE SUPERIORIDAD (Caso Pisa vs Atalanta)
    if a in GIGANTES and estado_h == "Baja Crítica (Estrella)":
        g_a = random.randint(2, 4) # El gigante golea si el local tiene bajas críticas
        g_h = 0 if estado_a == "Completo" else random.randint(0, 1)
    elif h in GIGANTES and estado_a == "Baja Crítica (Estrella)":
        g_h = random.randint(2, 4)
        g_a = 0 if estado_h == "Completo" else random.randint(0, 1)
    else:
        # Lógica estándar equilibrada
        if a in GIGANTES:
            g_a, g_h = random.randint(1, 2), random.randint(0, 1)
        elif h in GIGANTES:
            g_h, g_a = random.randint(1, 3), 0
        else:
            g_h, g_a = random.randint(0, 2), random.randint(0, 2)

    # COHERENCIA OBLIGATORIA (Si el marcador suma +2, la prob. debe ser ALTA)
    total = g_h + g_a
    if total >= 2:
        p15, p1t = random.randint(88, 98), random.randint(75, 92)
    elif total == 1:
        p15, p1t = random.randint(35, 55), random.randint(25, 45)
    else:
        p15, p1t = random.randint(5, 12), random.randint(2, 8)

    # ÁRBITROS
    estrictos = ["Matteo Marchetti", "Clément Turpin", "Anthony Taylor", "Michael Oliver", "Hernández Hernández"]
    t_rango = "5-8" if arbitro in estrictos else "2-5"
    roja = "ALTA" if arbitro in estrictos else "MODERADA"
    
    return {"p15": p15, "p1t": p1t, "g_h": g_h, "g_a": g_a, "corners": random.choice(["8.5+", "9.5+", "10.5+"]), "t_rango": t_rango, "roja": roja}

# --- TODAS LAS LIGAS COMPLETAS (SIN BORRAR NADA) ---
DATOS_REALES = {
    "Serie A (Italia)": [
        {"h": "AC Pisa 1909", "a": "Atalanta BC", "f": "Vie 16/01", "arb": "Matteo Marchetti"},
        {"h": "Lazio", "a": "Como", "f": "Sáb 17/01", "arb": "Marco Guida"},
        {"h": "Monza", "a": "Fiorentina", "f": "Sáb 17/01", "arb": "Daniele Doveri"},
        {"h": "Bologna", "a": "Roma", "f": "Dom 18/01", "arb": "Fabio Maresca"},
        {"h": "Inter", "a": "Empoli", "f": "Dom 18/01", "arb": "Davide Massa"},
        {"h": "Juventus", "a": "Milan", "f": "Lun 19/01", "arb": "Andrea Colombo"}
    ],
    "Ligue 1 (Francia)": [
        {"h": "PSG", "a": "Lille", "f": "Vie 16/01", "arb": "Clément Turpin"},
        {"h": "Mónaco", "a": "Lorient", "f": "Vie 16/01", "arb": "Benoît Bastien"},
        {"h": "Lens", "a": "Auxerre", "f": "Sáb 17/01", "arb": "W. Dechepy"},
        {"h": "Toulouse", "a": "Niza", "f": "Sáb 17/01", "arb": "K. Angoula"},
        {"h": "Lyon", "a": "Brest", "f": "Dom 18/01", "arb": "F. Letexier"},
        {"h": "Marsella", "a": "Nantes", "f": "Dom 18/01", "arb": "S. Frappart"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "Sáb 17/01", "arb": "Michael Oliver"},
        {"h": "Chelsea", "a": "Brentford", "f": "Sáb 17/01", "arb": "Anthony Taylor"},
        {"h": "Liverpool", "a": "Burnley", "f": "Sáb 17/01", "arb": "Paul Tierney"},
        {"h": "Tottenham", "a": "West Ham", "f": "Sáb 17/01", "arb": "Simon Hooper"},
        {"h": "Arsenal", "a": "Everton", "f": "Dom 18/01", "arb": "John Brooks"}
    ],
    "La Liga (España)": [
        {"h": "Real Madrid", "a": "Levante", "f": "Sáb 17/01", "arb": "Alberola Rojas"},
        {"h": "Barcelona", "a": "Real Sociedad", "f": "Dom 18/01", "arb": "Hernández Hernández"},
        {"h": "Girona", "a": "Sevilla", "f": "Sáb 17/01", "arb": "Busquets Ferrer"},
        {"h": "Atletico Madrid", "a": "Villarreal", "f": "Dom 18/01", "arb": "Soto Grado"}
    ],
    "Primeira Liga (Portugal)": [
        {"h": "Sporting CP", "a": "Casa Pia", "f": "16/01", "arb": "Claudio Pereira"},
        {"h": "Benfica", "a": "Rio Ave", "f": "17/01", "arb": "João Pinheiro"},
        {"h": "Oporto", "a": "Guimarães", "f": "18/01", "arb": "Nuno Almeida"}
    ],
    "Bundesliga (Alemania)": [
        {"h": "Werder Bremen", "a": "Frankfurt", "f": "16/01", "arb": "Felix Zwayer"},
        {"h": "RB Leipzig", "a": "Bayern", "f": "17/01", "arb": "Deniz Aytekin"}
    ],
    "UEFA Champions League": [
        {"h": "Inter", "a": "Arsenal", "f": "20/01", "arb": "Szymon Marciniak"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "20/01", "arb": "Slavko Vincic"}
    ],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Kevin Ortega"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01", "arb": "Wilton Sampaio"}],
    "Liga Argentina": [{"h": "Boca", "a": "River", "f": "01/02", "arb": "Facundo Tello"}],
    "Eredivisie (Holanda)": [{"h": "Ajax", "a": "PSV", "f": "18/01", "arb": "S. Gözübüyük"}],
    "UEFA Europa League": [{"h": "Man. United", "a": "Roma", "f": "22/01", "arb": "Gil Manzano"}]
}

# --- INTERFAZ ---
st.sidebar.title("⚽ PRO ANALYZER v35")
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
    st.header(f"🏟️ Partidos: {liga_sel}")
    for p in DATOS_REALES[liga_sel]:
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            st.caption(f"🗓️ {p['f']} | ⚖️ Árb: **{p['arb']}**")
            
            c1, c2 = st.columns(2)
            with c1: est_h = st.selectbox(f"Estado {p['h']}", ["Completo", "Rotación", "Baja Crítica (Estrella)"], key=f"h_{p['h']}_{p['f']}")
            with c2: est_a = st.selectbox(f"Estado {p['a']}", ["Completo", "Rotación", "Baja Crítica (Estrella)"], key=f"a_{p['h']}_{p['f']}")

            res = calcular_elite(p['h'], p['a'], est_h, est_a, p['arb'])
            
            r1, r2, r3 = st.columns(3)
            with r1: 
                st.success(f"🎯 Score: {res['g_h']} - {res['g_a']}")
                st.info(f"🚩 Corners: {res['corners']}")
            with r2: 
                st.metric("🟢 Prob. +1.5", f"{res['p15']}%")
                st.write(f"⏱️ Gol 1T: **{res['p1t']}%**")
            with r3: 
                st.warning(f"🟨 Tarjetas: {res['t_rango']}")
                st.markdown(f"🟥 Roja: **{res['roja']}**")

            if st.button(f"💾 Guardar Pick", key=f"btn_{p['h']}_{p['f']}"):
                txt = f"⚽ {p['h']}-{p['a']} | Score: {res['g_h']}-{res['g_a']} | Árb: {p['arb']}"
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                db_conn.commit(); st.rerun()

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"): st.caption(f); st.write(d)