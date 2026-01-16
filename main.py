import streamlit as st
import sqlite3
import os
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diamond v38.2 - Master Global", layout="wide", page_icon="💎")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_2026.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn
db_conn = init_db()

# --- MOTOR DIAMOND v38.2 (RESTAURADO AL 100%) ---
def calcular_diamond(h, a, est_h, est_a, arb):
    random.seed(len(h) + len(a) + 2026)
    GIGANTES = ["Man. City", "Arsenal", "Liverpool", "Man. United", "Chelsea", "Tottenham", 
                "Real Madrid", "Barcelona", "PSG", "Inter", "Milan", "Bayern", "Dortmund",
                "Alianza Lima", "Universitario", "Boca", "River", "Flamengo", "Sporting CP"]
    
    # 1. Score Probable (Ajuste Derbi 2-2)
    if h in GIGANTES and a in GIGANTES:
        g_h, g_a = (2, 2) if est_h == "Completo" and est_a == "Completo" else (1, 1)
    elif h in GIGANTES and est_h == "Completo":
        g_h, g_a = random.randint(2, 4), 0
    elif a in GIGANTES and est_a == "Completo":
        g_h, g_a = 0, random.randint(2, 3)
    else:
        g_h, g_a = random.randint(1, 2), random.randint(1, 2)

    # 2. Tiros de Esquina (Corners) - Basado en agresividad
    corners_val = "10.5+" if (h in GIGANTES or a in GIGANTES) else "9.5+"
    
    # 3. Perfil de Árbitros y Tarjetas
    estrictos = ["Michael Oliver", "Anthony Taylor", "Kevin Ortega", "Alberola Rojas", "H. Hernández", 
                 "C. Turpin", "S. Marciniak", "F. Tello", "W. Sampaio", "D. Aytekin"]
    
    t_rango = "5-8" if arb in estrictos else "3-5"
    roja = "ALTA" if arb in estrictos else "MEDIA"
    
    p15 = 98 if (g_h + g_a) >= 2 else 48
    return {"g_h": g_h, "g_a": g_a, "p15": p15, "corners": corners_val, "t_rango": t_rango, "roja": roja}

# --- BASE DE DATOS DE LAS 12 LIGAS (RESTAURADA) ---
LIGAS_MASTER = {
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": [
        {"h": "Man. United", "a": "Man. City", "f": "17/01 07:30", "arb": "Michael Oliver"},
        {"h": "Chelsea", "a": "Brentford", "f": "17/01 10:00", "arb": "Anthony Taylor"},
        {"h": "Nottingham Forest", "a": "Arsenal", "f": "17/01 12:30", "arb": "John Brooks"},
        {"h": "Liverpool", "a": "Burnley", "f": "17/01 10:00", "arb": "Paul Tierney"}
    ],
    "La Liga 🇪🇸": [
        {"h": "Real Madrid", "a": "Levante", "f": "17/01 14:00", "arb": "Alberola Rojas"},
        {"h": "Real Sociedad", "a": "Barcelona", "f": "18/01 21:00", "arb": "H. Hernández"},
        {"h": "Atlético Madrid", "a": "Alavés", "f": "18/01 16:15", "arb": "Soto Grado"}
    ],
    "Liga 1 🇵🇪": [
        {"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01 15:30", "arb": "Kevin Ortega"},
        {"h": "Universitario", "a": "ADT", "f": "01/02 18:00", "arb": "Diego Haro"}
    ],
    "Serie A 🇮🇹": [
        {"h": "Inter", "a": "Empoli", "f": "18/01 15:00", "arb": "Matteo Marchetti"},
        {"h": "Juventus", "a": "Milan", "f": "19/01 20:45", "arb": "D. Doveri"}
    ],
    "Bundesliga 🇩🇪": [
        {"h": "RB Leipzig", "a": "Bayern", "f": "17/01 18:30", "arb": "D. Aytekin"},
        {"h": "Dortmund", "a": "St. Pauli", "f": "17/01 15:30", "arb": "F. Zwayer"}
    ],
    "Ligue 1 🇫🇷": [
        {"h": "PSG", "a": "Lille", "f": "16/01 21:00", "arb": "C. Turpin"},
        {"h": "Lyon", "a": "Brest", "f": "18/01 20:45", "arb": "F. Letexier"}
    ],
    "Primeira Liga 🇵🇹": [
        {"h": "Rio Ave", "a": "Benfica", "f": "17/01 21:30", "arb": "J. Pinheiro"},
        {"h": "Sporting CP", "a": "Casa Pia", "f": "16/01 21:15", "arb": "C. Pereira"}
    ],
    "Liga Argentina 🇦🇷": [
        {"h": "Boca", "a": "Newell's", "f": "01/02 19:15", "arb": "F. Tello"},
        {"h": "Rosario Central", "a": "River", "f": "01/02 21:30", "arb": "Y. Falcón"}
    ],
    "Brasileirao 🇧🇷": [
        {"h": "Flamengo", "a": "Palmeiras", "f": "25/01 16:00", "arb": "W. Sampaio"}
    ],
    "Champions League 🇪🇺": [
        {"h": "Inter", "a": "Arsenal", "f": "20/01 21:00", "arb": "S. Marciniak"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "20/01 21:00", "arb": "Slavko Vincic"}
    ],
    "Europa League 🇪🇺": [
        {"h": "Roma", "a": "Stuttgart", "f": "22/01 21:00", "arb": "D. Orsato"},
        {"h": "Fenerbahçe", "a": "Aston Villa", "f": "22/01 18:45", "arb": "B. Bastien"}
    ],
    "Eredivisie 🇳🇱": [
        {"h": "Ajax", "a": "PSV", "f": "18/01 16:45", "arb": "Danny Makkelie"}
    ]
}

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v38.2")
liga_sel = st.sidebar.selectbox("Ligas (12)", list(LIGAS_MASTER.keys()))

c1, c2 = st.columns([2.3, 1])

with c1:
    st.header(f"📅 Cartelera: {liga_sel}")
    for p in LIGAS_MASTER[liga_sel]:
        with st.container(border=True):
            st.write(f"⏰ {p['f']} | 👤 Árbitro: **{p['arb']}**")
            colh, cola = st.columns(2)
            with colh: eh = st.selectbox(f"Est. {p['h']}", ["Completo", "Rotación", "Baja Crítica"], key=f"h_{p['h']}")
            with cola: ea = st.selectbox(f"Est. {p['a']}", ["Completo", "Rotación", "Baja Crítica"], key=f"a_{p['a']}")
            
            res = calcular_diamond(p['h'], p['a'], eh, ea, p['arb'])
            
            r1, r2, r3, r4 = st.columns(4)
            with r1: st.success(f"🎯 {res['g_h']} - {res['g_a']}")
            with r2: st.info(f"🚩 {res['corners']} Corn")
            with r3: st.warning(f"🟨 {res['t_rango']}")
            with r4: st.error(f"🟥 Roja: {res['roja']}")

            if st.button(f"💾 Guardar Pick", key=f"btn_{p['h']}"):
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', 
                               (f"{p['h']}-{p['a']} ({res['g_h']}-{res['g_a']})", liga_sel, p['f']))
                db_conn.commit(); st.rerun()

with c2:
    st.header("🛒 Mi Carrito")
    cursor = db_conn.execute('SELECT detalle, liga FROM carrito ORDER BY id DESC')
    for d, l in cursor.fetchall():
        st.info(f"**{l}**: {d}")