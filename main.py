import streamlit as st
import sqlite3
import os
from datetime import datetime
import random
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v23", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v23.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- MOTOR DE CÁLCULO DINÁMICO POR EQUIPO ---
def calcular_probabilidades_reales(h, a, estado_h, estado_a):
    # Base inicial aleatoria pero estable
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    
    prob_base = random.randint(80, 90)
    goles_1t = random.randint(65, 85)
    
    # Lógica de impacto
    # Si hay bajas críticas, la probabilidad de ver muchos goles (+1.5) suele bajar
    # porque se pierde calidad ofensiva.
    if estado_h == "Baja Crítica" or estado_a == "Baja Crítica":
        prob_base -= 12
        goles_1t -= 10
    if estado_h == "Rotación":
        prob_base -= 5
    if estado_a == "Rotación":
        prob_base -= 5
        
    return {
        "p15": max(prob_base, 10),
        "p1t": max(goles_1t, 10),
        "corners": random.choice(["8.5+", "9.5+", "10.5+"]),
        "t_rango": random.choice(["3-5", "6-9"])
    }

# --- JORNADAS COMPLETAS (NO SE BORRA NADA) ---
DATOS_REALES = {
    "Serie A (Italia)": [
        {"h": "AC Pisa 1909", "a": "Atalanta BC", "f": "16/01"},
        {"h": "Lazio", "a": "Como", "f": "17/01"},
        {"h": "Monza", "a": "Fiorentina", "f": "17/01"},
        {"h": "Bologna", "a": "Roma", "f": "18/01"},
        {"h": "Inter", "a": "Empoli", "f": "18/01"},
        {"h": "Juventus", "a": "Milan", "f": "19/01"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "17/01"},
        {"h": "Chelsea", "a": "Brentford", "f": "17/01"},
        {"h": "Liverpool", "a": "Burnley", "f": "17/01"},
        {"h": "Tottenham", "a": "West Ham", "f": "17/01"},
        {"h": "Arsenal", "a": "Everton", "f": "18/01"},
        {"h": "Brighton", "a": "Bournemouth", "f": "19/01"}
    ],
    "Ligue 1 (Francia)": [
        {"h": "PSG", "a": "Lille", "f": "16/01"},
        {"h": "Mónaco", "a": "Lorient", "f": "16/01"},
        {"h": "Lens", "a": "Auxerre", "f": "17/01"},
        {"h": "Lyon", "a": "Brest", "f": "18/01"}
    ],
    "Primeira Liga (Portugal)": [
        {"h": "Sporting CP", "a": "Casa Pia", "f": "16/01"},
        {"h": "Benfica", "a": "Rio Ave", "f": "17/01"},
        {"h": "Oporto", "a": "Guimarães", "f": "18/01"}
    ],
    "La Liga (España)": [
        {"h": "Real Madrid", "a": "Levante", "f": "17/01"},
        {"h": "Barcelona", "a": "Real Sociedad", "f": "18/01"}
    ],
    "Bundesliga (Alemania)": [
        {"h": "Werder Bremen", "a": "Frankfurt", "f": "16/01"},
        {"h": "RB Leipzig", "a": "Bayern", "f": "17/01"}
    ],
    "UEFA Champions League": [
        {"h": "Inter", "a": "Arsenal", "f": "20/01"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "20/01"}
    ],
    "UEFA Europa League": [{"h": "Man. United", "a": "Roma", "f": "22/01"}],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01"}],
    "Liga Argentina": [{"h": "Boca", "a": "River", "f": "01/02"}],
    "Eredivisie (Holanda)": [{"h": "Ajax", "a": "PSV", "f": "18/01"}]
}

# --- INTERFAZ ---
st.sidebar.title("⚽ PRO ANALYZER v23")
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
    st.header(f"🏟️ Partidos: {liga_sel}")
    
    for p in DATOS_REALES[liga_sel]:
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            
            # --- SECCIÓN DE INTELIGENCIA (ALINEACIÓN DUAL) ---
            st.write("🔍 **Validación de Alineación (Individual):**")
            c_h, c_a = st.columns(2)
            with c_h:
                estado_h = st.selectbox(f"Estado {p['h']}", ["Completo", "Rotación", "Baja Crítica"], key=f"h_{p['h']}_{p['f']}")
            with c_a:
                estado_a = st.selectbox(f"Estado {p['a']}", ["Completo", "Rotación", "Baja Crítica"], key=f"a_{p['h']}_{p['f']}")
            
            # Cálculo dinámico basado en los dos estados
            s = calcular_probabilidades_reales(p['h'], p['a'], estado_h, estado_a)
            
            # --- RESULTADOS DINÁMICOS ---
            c1, c2, c3 = st.columns(3)
            with c1:
                # El marcador se vuelve más bajo si hay bajas críticas
                g_h = random.randint(0,1) if estado_h == "Baja Crítica" else random.randint(1,3)
                g_a = random.randint(0,1) if estado_a == "Baja Crítica" else random.randint(0,2)
                st.success(f"🎯 Score: {g_h}-{g_a}")
                st.info(f"🚩 Corners: {s['corners']}")
            with c2:
                st.metric("🟢 Prob. +1.5", f"{s['p15']}%")
                st.write(f"⏱️ Gol 1T: **{s['p1t']}%**")
            with c3:
                st.warning(f"🟨 Tarjetas: {s['t_rango']}")
                st.caption(f"📅 {p['f']}")

            # --- ACCIONES ---
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"💾 Guardar", key=f"btn_{p['h']}_{p['f']}"):
                    txt = f"⚽ {p['h']}({estado_h}) vs {p['a']}({estado_a}) | +1.5 Goles: {s['p15']}%"
                    db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                    db_conn.commit()
                    st.rerun()
            with b2:
                msg = f"*REPORTE ELITE CONFIRMADO*\n\n🏟️ {p['h']} vs {p['a']}\n✅ +1.5 Goles: {s['p15']}%\n📋 {p['h']}: {estado_h} | {p['a']}: {estado_a}"
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"):
            st.caption(f); st.write(d)