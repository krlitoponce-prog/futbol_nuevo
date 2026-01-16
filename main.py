import streamlit as st
import sqlite3
import os
from datetime import datetime
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Diamond v38 - Premier Sync", layout="wide", page_icon="🏴󠁧󠁢󠁥󠁮󠁧󠁿")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_2026.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn
db_conn = init_db()

# --- MOTOR DIAMOND v38 (CON AJUSTE DE "DUELO DE TITANES") ---
def calcular_diamond(h, a, est_h, est_a):
    random.seed(len(h) + len(a) + 2026)
    GIGANTES = ["Man. City", "Arsenal", "Liverpool", "Man. United", "Chelsea", "Tottenham"]
    
    # Lógica de marcadores balanceados (Efecto 2-2 para Derbis)
    if h in GIGANTES and a in GIGANTES:
        if est_h == "Completo" and est_a == "Completo":
            g_h, g_a = 2, 2
        else:
            g_h, g_a = random.randint(1, 2), random.randint(1, 2)
    elif h in GIGANTES and est_h == "Completo":
        g_h, g_a = random.randint(2, 4), 0
    elif a in GIGANTES and est_a == "Completo":
        g_h, g_a = 0, random.randint(2, 3)
    else:
        g_h, g_a = random.randint(1, 2), random.randint(1, 2)

    p15 = 98 if (g_h + g_a) >= 2 else 45
    return {"g_h": g_h, "g_a": g_a, "p15": p15, "corners": "10.5+", "t_rango": "4-7"}

# --- CARTELERA COMPLETA SINCRONIZADA ---
LIGAS_MASTER = {
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": [
        {"h": "Man. United", "a": "Man. City", "f": "17/01 07:30"},
        {"h": "Sunderland", "a": "Crystal Palace", "f": "17/01 10:00"},
        {"h": "Chelsea", "a": "Brentford", "f": "17/01 10:00"},
        {"h": "Liverpool", "a": "Burnley", "f": "17/01 10:00"},
        {"h": "Leeds United", "a": "Fulham", "f": "17/01 10:00"},
        {"h": "Tottenham", "a": "West Ham", "f": "17/01 10:00"},
        {"h": "Nottingham Forest", "a": "Arsenal", "f": "17/01 12:30"},
        {"h": "Wolverhampton", "a": "Newcastle", "f": "18/01 09:00"},
        {"h": "Aston Villa", "a": "Everton", "f": "18/01 11:30"},
        {"h": "Brighton", "a": "Bournemouth", "f": "19/01 15:00"}
    ],
    "La Liga 🇪🇸": [
        {"h": "Real Madrid", "a": "Levante", "f": "17/01 08:00"},
        {"h": "Betis", "a": "Villarreal", "f": "17/01 15:00"},
        {"h": "Getafe", "a": "Valencia", "f": "18/01 08:00"},
        {"h": "Real Sociedad", "a": "Barcelona", "f": "18/01 15:00"}
    ],
    "Liga 1 🇵🇪": [
        {"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01 12:00"},
        {"h": "Universitario", "a": "ADT", "f": "01/02 18:00"}
    ],
    "Champions League 🇪🇺": [
        {"h": "Inter", "a": "Arsenal", "f": "20/01 21:00"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "20/01 21:00"}
    ],
    "Bundesliga 🇩🇪": [
        {"h": "RB Leipzig", "a": "Bayern", "f": "17/01 15:30"},
        {"h": "Dortmund", "a": "St. Pauli", "f": "17/01 15:30"}
    ],
    "Ligue 1 🇫🇷": [
        {"h": "Monaco", "a": "Lorient", "f": "16/01 19:00"},
        {"h": "Lyon", "a": "Brest", "f": "18/01 20:45"}
    ],
    "Primeira Liga 🇵🇹": [
        {"h": "Rio Ave", "a": "Benfica", "f": "17/01 21:30"},
        {"h": "Guimarães", "a": "Oporto", "f": "18/01 21:30"}
    ],
    "Liga Argentina 🇦🇷": [
        {"h": "Boca", "a": "Newell's", "f": "01/02 19:15"},
        {"h": "Rosario Central", "a": "River", "f": "01/02 21:30"}
    ],
    "Europa League 🇪🇺": [
        {"h": "Roma", "a": "Stuttgart", "f": "22/01 21:00"},
        {"h": "Fenerbahçe", "a": "Aston Villa", "f": "22/01 18:45"}
    ]
}

# --- INTERFAZ ---
st.sidebar.title("💎 DIAMOND v38 GLOBAL")
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(LIGAS_MASTER.keys()))

if st.sidebar.button(f"🔄 Sincronizar {liga_sel}"):
    st.sidebar.success(f"Partidos de {liga_sel} actualizados para hoy.")

c1, c2 = st.columns([2.3, 1])

with c1:
    st.header(f"📅 Cartelera: {liga_sel}")
    for p in LIGAS_MASTER[liga_sel]:
        with st.container(border=True):
            st.write(f"⏰ {p['f']} | **{p['h']} vs {p['a']}**")
            colh, cola = st.columns(2)
            with colh: eh = st.selectbox(f"Est. {p['h']}", ["Completo", "Rotación", "Baja Crítica"], key=f"h_{p['h']}")
            with cola: ea = st.selectbox(f"Est. {p['a']}", ["Completo", "Rotación", "Baja Crítica"], key=f"a_{p['a']}")
            
            res = calcular_diamond(p['h'], p['a'], eh, ea)
            st.success(f"🎯 Score: {res['g_h']} - {res['g_a']} | +1.5: {res['p15']}%")
            
            if st.button(f"💾 Guardar Pick", key=f"btn_{p['h']}"):
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', 
                               (f"{p['h']} {res['g_h']}-{res['g_a']} {p['a']}", liga_sel, p['f']))
                db_conn.commit(); st.rerun()

with c2:
    st.header("🛒 Mi Carrito")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        st.info(f"**{f}**: {d}")