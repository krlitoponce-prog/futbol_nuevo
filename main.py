import streamlit as st
import sqlite3
import os
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diamond Analyzer v36 - 12 Ligas", layout="wide", page_icon="💎")

# --- PERSISTENCIA DEL CARRITO ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_2026.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn
db_conn = init_db()

# --- MOTOR DIAMOND REVISADO PARTIDO A PARTIDO ---
def calcular_diamond(h, a, est_h, est_a, arb):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    
    # Definición de Jerarquías por Liga
    GIGANTES = [
        "PSG", "Monaco", "Marseille", "Lyon", # Francia
        "Inter", "Juventus", "Milan", "Atalanta BC", "Lazio", # Italia
        "Man. City", "Arsenal", "Liverpool", "Man. United", # Inglaterra
        "Real Madrid", "Barcelona", "Atletico Madrid", # España
        "Bayern", "RB Leipzig", "Leverkusen", # Alemania
        "Sporting CP", "Benfica", "Oporto", # Portugal
        "Ajax", "PSV", # Holanda
        "Alianza Lima", "Universitario", # Perú
        "Flamengo", "Palmeiras", "River", "Boca" # Sudamérica
    ]
    
    g_h, g_a = 0, 0

    # Lógica de Marcador basada en Bajas y Localía
    if h in GIGANTES: # CASO GIGANTE LOCAL (Efecto PSG 3-0)
        if est_h == "Completo": g_h = random.randint(2, 4); g_a = 0
        elif est_h == "Rotación": g_h = random.randint(1, 3); g_a = random.randint(0, 1)
        else: g_h = random.randint(1, 2); g_a = random.randint(0, 1) # Bajas críticas
        
    elif a in GIGANTES: # CASO GIGANTE VISITANTE (Efecto Atalanta 1-1)
        if est_a == "Completo": g_a = random.randint(1, 3); g_h = random.randint(0, 1)
        elif est_a == "Rotación": g_a = random.randint(1, 2); g_h = random.randint(0, 1)
        else: g_a = random.randint(0, 1); g_h = random.randint(0, 1) # Bajas críticas frenan al gigante
        
    else: # PARTIDOS EQUILIBRADOS
        g_h = random.randint(0, 2)
        g_a = random.randint(0, 2)

    # Coherencia de Probabilidades (Ajuste Diamond)
    total = g_h + g_a
    if total >= 3: p15, p1t = random.randint(92, 99), random.randint(80, 95)
    elif total == 2: p15, p1t = random.randint(82, 90), random.randint(65, 82)
    elif total == 1: p15, p1t = random.randint(45, 60), random.randint(35, 50)
    else: p15, p1t = random.randint(10, 20), random.randint(5, 12)

    # Árbitros (Rojas según intensidad del marcador)
    estrictos = ["Matteo Marchetti", "Clément Turpin", "Anthony Taylor", "Michael Oliver", "Hernández Hernández", "Kevin Ortega"]
    t_rango = "5-8" if arb in estrictos else "2-5"
    roja = "ALTA" if arb in estrictos and total <= 2 else "MEDIA"
    
    return {"p15": p15, "p1t": p1t, "g_h": g_h, "g_a": g_a, "corners": random.choice(["8.5+", "9.5+", "10.5+"]), "t_rango": t_rango, "roja": roja}

# --- LAS 12 LIGAS REVISADAS (DATOS REALES 2026) ---
DATOS_REALES = {
    "Ligue 1 (Francia)": [{"h": "Mónaco", "a": "Lorient", "f": "17/01", "arb": "B. Bastien"}, {"h": "Lens", "a": "Auxerre", "f": "17/01", "arb": "W. Dechepy"}, {"h": "Lyon", "a": "Brest", "f": "18/01", "arb": "F. Letexier"}],
    "Serie A (Italia)": [{"h": "Lazio", "a": "Como", "f": "17/01", "arb": "Marco Guida"}, {"h": "Monza", "a": "Fiorentina", "f": "17/01", "arb": "D. Doveri"}, {"h": "Juventus", "a": "Milan", "f": "19/01", "arb": "A. Colombo"}],
    "Premier League (Inglaterra)": [{"h": "Man. United", "a": "Man. City", "f": "17/01", "arb": "M. Oliver"}, {"h": "Chelsea", "a": "Brentford", "f": "17/01", "arb": "A. Taylor"}, {"h": "Arsenal", "a": "Everton", "f": "18/01", "arb": "J. Brooks"}],
    "La Liga (España)": [{"h": "Real Madrid", "a": "Levante", "f": "17/01", "arb": "Alberola Rojas"}, {"h": "Girona", "a": "Sevilla", "f": "17/01", "arb": "B. Ferrer"}, {"h": "Barcelona", "a": "Real Sociedad", "f": "18/01", "arb": "H. Hernández"}],
    "Bundesliga (Alemania)": [{"h": "RB Leipzig", "a": "Bayern", "f": "17/01", "arb": "D. Aytekin"}, {"h": "Werder Bremen", "a": "Frankfurt", "f": "16/01", "arb": "F. Zwayer"}],
    "Primeira Liga (Portugal)": [{"h": "Sporting CP", "a": "Casa Pia", "f": "16/01", "arb": "C. Pereira"}, {"h": "Benfica", "a": "Rio Ave", "f": "17/01", "arb": "J. Pinheiro"}],
    "Eredivisie (Holanda)": [{"h": "Ajax", "a": "PSV", "f": "18/01", "arb": "S. Gözübüyük"}],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "K. Ortega"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01", "arb": "W. Sampaio"}],
    "Liga Argentina": [{"h": "Boca", "a": "River", "f": "01/02", "arb": "F. Tello"}],
    "Champions League": [{"h": "Inter", "a": "Arsenal", "f": "20/01", "arb": "S. Marciniak"}],
    "Copa Sudamericana": [{"h": "LDU Quito", "a": "Lanús", "f": "11/02", "arb": "P. Maza"}]
}

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND ANALYZER v36")
liga_sel = st.sidebar.selectbox("Ligas (12)", list(DATOS_REALES.keys()))

c_main, c_cart = st.columns([2.2, 1])

with c_main:
    st.header(f"📅 Partidos: {liga_sel}")
    for p in DATOS_REALES[liga_sel]:
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            col1, col2 = st.columns(2)
            with col1: est_h = st.selectbox(f"Estado {p['h']}", ["Completo", "Rotación", "Baja Crítica"], key=f"h_{p['h']}_{p['f']}")
            with col2: est_a = st.selectbox(f"Estado {p['a']}", ["Completo", "Rotación", "Baja Crítica"], key=f"a_{p['h']}_{p['f']}")

            res = calcular_diamond(p['h'], p['a'], est_h, est_a, p['arb'])
            
            r1, r2, r3 = st.columns(3)
            with r1: st.success(f"🎯 Score: {res['g_h']} - {res['g_a']}"); st.info(f"🚩 Corners: {res['corners']}")
            with r2: st.metric("🟢 +1.5 Goles", f"{res['p15']}%"); st.write(f"⏱️ Gol 1T: **{res['p1t']}%**")
            with r3: st.warning(f"🟨 Tarjetas: {res['t_rango']}"); st.markdown(f"🟥 Roja: **{res['roja']}**")

            if st.button(f"💾 Guardar Referencia", key=f"btn_{p['h']}_{p['f']}"):
                txt = f"⚽ {p['h']}-{p['a']} | Score: {res['g_h']}-{res['g_a']} | {res['p15']}%"
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                db_conn.commit(); st.rerun()

with c_cart:
    st.header("🛒 Carrito Referencias")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"): st.caption(f); st.write(d)