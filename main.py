import streamlit as st
import sqlite3
import os
from datetime import datetime
import random
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v29", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v29.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn
db_conn = init_db()

# --- MOTOR DE CÁLCULO CON COHERENCIA INVIOLABLE ---
def calcular_elite(h, a, estado_h, estado_a, arbitro):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    
    # 1. GENERAR MARCADOR REALISTA PRIMERO
    GIGANTES = ["Atalanta BC", "PSG", "Man. City", "Real Madrid", "Barcelona", "Inter", "Bayern", "Arsenal", "Liverpool"]
    
    if a in GIGANTES:
        g_h = random.randint(0, 1) if estado_h != "Completo" else random.randint(0, 2)
        g_a = random.randint(1, 2) if estado_a == "Completo" else random.randint(0, 1)
    elif h in GIGANTES:
        g_h = random.randint(1, 3) if estado_h == "Completo" else random.randint(1, 2)
        g_a = random.randint(0, 1)
    else:
        g_h, g_a = random.randint(0, 2), random.randint(0, 2)

    if estado_h == "Baja Crítica (Estrella)": g_h = 0
    if estado_a == "Baja Crítica (Estrella)": g_a = 0

    # 2. FILTRO DE COHERENCIA RADICAL (Corrigiendo los errores de las fotos)
    total_goles = g_h + g_a
    
    if total_goles >= 2:
        p15 = random.randint(85, 98)
        p1t = random.randint(70, 90)
    elif total_goles == 1:
        # Si solo hay 1 gol proyectado, la probabilidad de +1.5 DEBE ser baja
        p15 = random.randint(15, 35) 
        p1t = random.randint(10, 30)
    else:
        # Si es 0-0, la probabilidad de +1.5 DEBE ser mínima
        p15 = random.randint(2, 10)
        p1t = random.randint(1, 5)

    # Tarjetas
    estrictos = ["Daniele Orsato", "Anthony Taylor", "Michael Oliver", "Hernández Hernández", "Kevin Ortega"]
    t_rango = "5-8" if arbitro in estrictos else "2-5"
    
    return {"p15": p15, "p1t": p1t, "g_h": g_h, "g_a": g_a, "corners": random.choice(["8.5+", "9.5+", "10.5+"]), "t_rango": t_rango}

# --- DATOS COMPLETOS (TODAS LAS LIGAS) ---
DATOS_REALES = {
    "Serie A (Italia)": [
        {"h": "AC Pisa 1909", "a": "Atalanta BC", "f": "Vie 16/01", "arb": "Daniele Orsato"},
        {"h": "Lazio", "a": "Como", "f": "Sáb 17/01", "arb": "Marco Guida"},
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
        {"h": "Arsenal", "a": "Everton", "f": "Dom 18/01", "arb": "John Brooks"}
    ],
    "La Liga (España)": [
        {"h": "Real Madrid", "a": "Levante", "f": "Sáb 17/01", "arb": "Alberola Rojas"},
        {"h": "Barcelona", "a": "Real Sociedad", "f": "Dom 18/01", "arb": "Hernández Hernández"}
    ],
    "Primeira Liga (Portugal)": [{"h": "Sporting CP", "a": "Casa Pia", "f": "Vie 16/01", "arb": "Claudio Pereira"}],
    "Bundesliga (Alemania)": [{"h": "Werder Bremen", "a": "Frankfurt", "f": "Vie 16/01", "arb": "Felix Zwayer"}],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Kevin Ortega"}]
}

# --- INTERFAZ ---
st.sidebar.title("⚽ ANALIZADOR v29")
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
                # Ahora la métrica reflejará la realidad del score
                st.metric("🟢 Prob. +1.5", f"{res['p15']}%")
                st.write(f"⏱️ Gol 1T: **{res['p1t']}%**")
            with r3: 
                st.warning(f"🟨 Tarjetas: {res['t_rango']}")

            if st.button(f"💾 Guardar Pick", key=f"btn_{p['h']}_{p['f']}"):
                txt = f"⚽ {p['h']}-{p['a']} | Score: {res['g_h']}-{res['g_a']} | +1.5: {res['p15']}%"
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                db_conn.commit(); st.rerun()

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"): st.caption(f); st.write(d)