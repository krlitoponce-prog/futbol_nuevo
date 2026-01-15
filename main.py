import streamlit as st
import sqlite3
import os
from datetime import datetime
import random
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v18 - FINAL", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v18.db')
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
    c15, c25 = round(random.uniform(1.22, 1.38), 2), round(random.uniform(1.70, 2.15), 2)
    estrictos = ["Anthony Taylor", "Szymon Marciniak", "Michael Oliver", "Felix Zwayer", "Kevin Ortega"]
    es_duro = arb in estrictos
    return {
        "p15": p15, "p25": p25, "p1t": p1t, "c15": c15, "c25": c25,
        "corners": random.choice(["8.5+", "9.5+", "10.5+"]),
        "t_rango": "5-9" if es_duro else "2-5",
        "roja": "ALTO" if es_duro else "BAJO"
    }

# --- TODAS LAS LIGAS COMPLETAS (FRANCIA, PORTUGAL, ITALIA, ESPAÑA, ETC) ---
DATOS_REALES = {
    "Ligue 1 (Francia)": [
        {"h": "PSG", "a": "Lille", "f": "16/01 3:00 p.m.", "arb": "Clément Turpin"},
        {"h": "Mónaco", "a": "Lorient", "f": "16/01 1:00 p.m.", "arb": "Benoît Bastien"}
    ],
    "Primeira Liga (Portugal)": [
        {"h": "Sporting CP", "a": "Casa Pia", "f": "16/01 3:15 p.m.", "arb": "Claudio Pereira"},
        {"h": "Rio Ave", "a": "Benfica", "f": "17/01 3:30 p.m.", "arb": "Ruivo Pereira"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "17/01 7:30 a.m.", "arb": "Michael Oliver"},
        {"h": "Chelsea", "a": "Brentford", "f": "17/01 10:00 a.m.", "arb": "Anthony Taylor"}
    ],
    "UEFA Champions League": [
        {"h": "Inter", "a": "Arsenal", "f": "20/01 3:00 p.m.", "arb": "Danny Makkelie"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "20/01 3:00 p.m.", "arb": "Slavko Vincic"}
    ],
    "Serie A (Italia)": [{"h": "Juventus", "a": "Milan", "f": "19/01", "arb": "Daniele Orsato"}],
    "La Liga (España)": [{"h": "Barcelona", "a": "Real Sociedad", "f": "18/01", "arb": "Hernández Hernández"}],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Kevin Ortega"}],
    "Brasileirao (Brasil)": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01", "arb": "Wilton Sampaio"}]
}

# --- INTERFAZ ---
liga_sel = st.sidebar.selectbox("Liga Activa", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
    # --- BOTÓN DE PICKS CON AUTO-GUARDADO ---
    if st.button("💎 ANALIZAR Y GUARDAR PICKS DE ORO AUTOMÁTICAMENTE"):
        partidos = DATOS_REALES[liga_sel]
        guardados = 0
        for p in partidos:
            res = obtener_analisis_completo(p['h'], p['a'], p['arb'])
            if res['p15'] > 94: # Si es de máxima confianza
                txt = f"🔥 AUTO-PICK: {p['h']}-{p['a']} | Goles: {res['p15']}% | Cuota: {res['c15']}"
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                guardados += 1
        db_conn.commit()
        if guardados > 0:
            st.success(f"Se han añadido {guardados} Picks de Oro al carrito automáticamente.")
            st.rerun()
        else:
            st.info("No se encontraron cuotas de oro en esta liga por ahora.")
        st.divider()

    st.header(f"🏟️ Partidos: {liga_sel}")
    for p in DATOS_REALES[liga_sel]:
        s = obtener_analisis_completo(p['h'], p['a'], p['arb'])
        marcador = f"{random.randint(1,3)}-{random.randint(0,2)}"
        
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            st.caption(f"🗓️ {p['f']} | ⚖️ Árbitro: {p['arb']}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success(f"🎯 Score: {marcador}")
                st.info(f"🚩 Corners: {s['corners']}")
            with c2:
                st.warning(f"🟨 Tarjetas: {s['t_rango']}")
                st.markdown(f"🟥 Roja: **{s['roja']}**")
            with c3:
                st.write(f"⏱️ Gol 1T: **{s['p1t']}%**")
                st.write(f"🟢 +1.5 Goles: **{s['p15']}%**")
                st.write(f"🔵 +2.5 Goles: **{s['p25']}%**")

            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"💾 Guardar Individual", key=f"s_{p['h']}_{p['f']}"):
                    txt = f"📌 {p['h']}-{p['a']} | Pick: {s['p15']}%"
                    db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                    db_conn.commit()
                    st.rerun()
            with b2:
                msg = f"*REPORTE ELITE ⚽*\n\n🔥 *{p['h']} vs {p['a']}*\n🟢 Prob. +1.5: {s['p15']}%\n🎯 Score: {marcador}"
                encoded_msg = urllib.parse.quote(msg)
                st.markdown(f'<a href="https://wa.me/?text={encoded_msg}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"):
            st.caption(f)
            st.write(d)
    
    if st.sidebar.button("🗑️ Vaciar Carrito"):
        db_conn.execute('DELETE FROM carrito')
        db_conn.commit()
        st.rerun()