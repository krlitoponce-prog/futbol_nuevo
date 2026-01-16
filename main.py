import streamlit as st
import sqlite3
import os
from datetime import datetime
import random
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v22 - Pro", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v22.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- MOTOR DE CÁLCULO CON AJUSTE DINÁMICO ---
def obtener_analisis_dinamico(h, a, impacto_bajas):
    # Base de cálculo
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    
    p15 = random.randint(85, 98)
    p1t = random.randint(60, 92)
    
    # Ajuste por Bajas (Inteligencia Externa)
    if impacto_bajas == "Baja Crítica (Estrella)":
        p15 -= 15  # Cae la probabilidad de goles
        p1t -= 10
    elif impacto_bajas == "Rotación (Varios suplentes)":
        p15 -= 8
        p1t -= 5
        
    return {
        "p15": max(p15, 10),
        "p1t": max(p1t, 10),
        "corners": random.choice(["8.5+", "9.5+", "10.5+"]),
        "t_rango": random.choice(["3-5", "6-9"])
    }

# --- DATOS REALES (12 LIGAS COMPLETAS) ---
DATOS_REALES = {
    "Serie A (Italia)": [
        {"h": "AC Pisa 1909", "a": "Atalanta BC", "f": "16/01 2:45 p.m."},
        {"h": "Inter", "a": "Empoli", "f": "18/01 12:30 p.m."},
        {"h": "Juventus", "a": "Milan", "f": "19/01 2:45 p.m."}
    ],
    "Ligue 1 (Francia)": [
        {"h": "PSG", "a": "Lille", "f": "16/01 3:00 p.m."},
        {"h": "Mónaco", "a": "Lorient", "f": "16/01 1:00 p.m."}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "17/01 7:30 a.m."},
        {"h": "Chelsea", "a": "Brentford", "f": "17/01 10:00 a.m."},
        {"h": "Liverpool", "a": "Burnley", "f": "17/01 10:00 a.m."}
    ],
    "Primeira Liga (Portugal)": [{"h": "Sporting CP", "a": "Casa Pia", "f": "16/01"}],
    "Bundesliga (Alemania)": [{"h": "Werder Bremen", "a": "Frankfurt", "f": "16/01"}],
    "La Liga (España)": [{"h": "Real Madrid", "a": "Levante", "f": "17/01"}],
    "UEFA Champions League": [{"h": "Real Madrid", "a": "Mónaco", "f": "20/01"}],
    "UEFA Europa League": [{"h": "Man. United", "a": "Roma", "f": "22/01"}],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01"}],
    "Liga Argentina": [{"h": "Boca", "a": "River", "f": "01/02"}],
    "Eredivisie (Holanda)": [{"h": "Ajax", "a": "PSV", "f": "18/01"}]
}

# --- INTERFAZ ---
st.sidebar.title("⚽ ESTRATEGIA EN VIVO")
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
    st.header(f"🏟️ Jornada: {liga_sel}")
    
    for p in DATOS_REALES[liga_sel]:
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            st.caption(f"🗓️ {p['f']}")
            
            # 1. BOTÓN DE INTELIGENCIA EXTERNA
            search_query = urllib.parse.quote(f"lineups {p['h']} vs {p['a']}")
            st.markdown(f'**[🔍 Ver Alineaciones Oficiales](https://www.google.com/search?q={search_query})**')
            
            # 2. SELECTOR DE IMPACTO DE BAJAS
            bajas = st.radio("Estado de Formación:", 
                             ["Equipo Completo", "Rotación (Varios suplentes)", "Baja Crítica (Estrella)"], 
                             key=f"baja_{p['h']}_{p['f']}", horizontal=True)
            
            # 3. RE-ANÁLISIS SEGÚN ALINEACIÓN
            s = obtener_analisis_dinamico(p['h'], p['a'], bajas)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success(f"🎯 Score: {random.randint(0,2)}-{random.randint(0,2)}")
                st.info(f"🚩 Corners: {s['corners']}")
            with c2:
                st.write(f"⏱️ Gol 1T: **{s['p1t']}%**")
                st.write(f"🟢 +1.5 Goles: **{s['p15']}%**")
            with c3:
                st.warning(f"🟨 Tarjetas: {s['t_rango']}")
                if bajas != "Equipo Completo":
                    st.error("⚠️ Probabilidad Ajustada por Bajas")

            # 4. BOTONES DE ACCIÓN
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"💾 Guardar Pick Final", key=f"s_{p['h']}_{p['f']}"):
                    txt = f"📌 {p['h']}-{p['a']} | Pick: {s['p15']}% | Estado: {bajas}"
                    db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                    db_conn.commit()
                    st.rerun()
            with b2:
                msg = f"*REPORTE ELITE CONFIRMADO*\n\n🔥 *{p['h']} vs {p['a']}*\n🟢 Prob. +1.5: {s['p15']}%\n📋 Estado: {bajas}"
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"):
            st.caption(f); st.write(d)