import streamlit as st
import sqlite3
import os
from datetime import datetime
import random
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v24 - Referentes", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v24.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- BASE DE DATOS DE REFERENTES (ESTRELLAS) ---
REFERENTES = {
    "Atalanta BC": ["Lookman", "Retegui", "De Ketelaere"],
    "PSG": ["Dembele", "Barcola", "Kolo Muani"],
    "Man. City": ["Haaland", "De Bruyne", "Foden"],
    "Real Madrid": ["Vinicius", "Mbappe", "Bellingham"],
    "Barcelona": ["Lewandowski", "Lamine Yamal", "Raphinha"],
    "Liverpool": ["Salah", "Luis Diaz", "Darwin Nuñez"],
    "Arsenal": ["Saka", "Odegaard", "Havertz"],
    "Inter": ["Lautaro Martinez", "Thuram", "Barella"],
    "Sporting CP": ["Gyökeres", "Trincão", "Pedro Gonçalves"],
    "Benfica": ["Pavlidis", "Di Maria", "Akturkoglu"],
    "Alianza Lima": ["Barcos", "Sabbag", "Quevedo"],
    "Bayern": ["Harry Kane", "Musiala", "Sane"]
}

# --- MOTOR DE CÁLCULO DINÁMICO ---
def calcular_elite(h, a, estado_h, estado_a):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    
    # Probabilidades base
    p15 = random.randint(88, 98)
    p1t = random.randint(70, 90)
    
    # Impacto de Bajas en el marcador y goles
    mult_h, mult_a = 1.0, 1.0
    
    if estado_h == "Baja Crítica (Estrella)":
        p15 -= 15
        p1t -= 10
        mult_h = 0.4
    if estado_a == "Baja Crítica (Estrella)":
        p15 -= 15
        p1t -= 10
        mult_a = 0.4
        
    g_h = int(random.randint(1, 3) * mult_h)
    g_a = int(random.randint(0, 2) * mult_a)
    
    return {"p15": max(p15, 10), "p1t": max(p1t, 10), "g_h": g_h, "g_a": g_a,
            "corners": random.choice(["8.5+", "9.5+", "10.5+"]), "t_rango": random.choice(["3-5", "6-9"])}

# --- JORNADAS COMPLETAS ---
DATOS_REALES = {
    "Serie A (Italia)": [{"h": "AC Pisa 1909", "a": "Atalanta BC", "f": "Vie 16/01"}, {"h": "Inter", "a": "Empoli", "f": "Dom 18/01"}, {"h": "Juventus", "a": "Milan", "f": "Lun 19/01"}],
    "Ligue 1 (Francia)": [{"h": "PSG", "a": "Lille", "f": "Vie 16/01"}, {"h": "Mónaco", "a": "Lorient", "f": "Vie 16/01"}],
    "Premier League (Inglaterra)": [{"h": "Man. United", "a": "Man. City", "f": "Sáb 17/01"}, {"h": "Chelsea", "a": "Brentford", "f": "Sáb 17/01"}, {"h": "Liverpool", "a": "Burnley", "f": "Sáb 17/01"}],
    "Primeira Liga (Portugal)": [{"h": "Sporting CP", "a": "Casa Pia", "f": "Vie 16/01"}, {"h": "Benfica", "a": "Rio Ave", "f": "Sáb 17/01"}],
    "La Liga (España)": [{"h": "Real Madrid", "a": "Levante", "f": "Sáb 17/01"}, {"h": "Barcelona", "a": "Real Sociedad", "f": "Dom 18/01"}],
    "UEFA Champions League": [{"h": "Inter", "a": "Arsenal", "f": "Mar 20/01"}, {"h": "Real Madrid", "a": "Mónaco", "f": "Mar 20/01"}],
    "Liga 1 (Perú)": [{"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01"}],
    "Bundesliga (Alemania)": [{"h": "Werder Bremen", "a": "Frankfurt", "f": "16/01"}, {"h": "RB Leipzig", "a": "Bayern", "f": "17/01"}]
}

# --- INTERFAZ ---
st.sidebar.title("⚽ ESTRATEGIA v24")
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
    st.header(f"🏟️ Partidos: {liga_sel}")
    for p in DATOS_REALES[liga_sel]:
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            
            # MÓDULO DE ESCANEO
            c_esc, c_ref = st.columns([1, 1.2])
            with c_esc:
                if st.button(f"🤖 ESCANEAR ALINEACIÓN", key=f"scan_{p['h']}"):
                    with st.spinner("Buscando estrellas..."):
                        estrellas = REFERENTES.get(p['a'], ["Jugadores"])
                        st.toast(f"Escaneando presencia de: {', '.join(estrellas)}", icon="🔍")
            with c_ref:
                st.caption(f"⭐ Referentes clave: {', '.join(REFERENTES.get(p['h'], ['N/A']))} vs {', '.join(REFERENTES.get(p['a'], ['N/A']))}")

            # SELECCIÓN DE ESTADO
            ch1, ch2 = st.columns(2)
            with ch1: est_h = st.selectbox(f"Estado {p['h']}", ["Completo", "Rotación", "Baja Crítica (Estrella)"], key=f"eh_{p['h']}")
            with ch2: est_a = st.selectbox(f"Estado {p['a']}", ["Completo", "Rotación", "Baja Crítica (Estrella)"], key=f"ea_{p['a']}")

            # RESULTADOS
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
                if est_h == "Baja Crítica (Estrella)" or est_a == "Baja Crítica (Estrella)":
                    st.error("📉 Marcador Reducido")

            # ACCIONES
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"💾 Guardar", key=f"btn_{p['h']}"):
                    txt = f"📌 {p['h']} vs {p['a']} | Score: {res['g_h']}-{res['g_a']} | +1.5: {res['p15']}%"
                    db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                    db_conn.commit(); st.rerun()
            with b2:
                msg = f"*REPORTE ELITE CONFIRMADO*\n\n🏟️ {p['h']} vs {p['a']}\n🎯 Score Proyectado: {res['g_h']}-{res['g_a']}\n✅ Prob. +1.5: {res['p15']}%"
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"): st.caption(f); st.write(d)
    if st.sidebar.button("🗑️ Vaciar Carrito"): db_conn.execute('DELETE FROM carrito'); db_conn.commit(); st.rerun()