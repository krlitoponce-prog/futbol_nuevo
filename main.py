import streamlit as st
import sqlite3
import os
from datetime import datetime
import random
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v16", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v16.db')
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
    estrictos = ["Szymon Marciniak", "Michael Oliver", "Felix Zwayer", "Stéphanie Frappart", "Artur Soares"]
    es_duro = arb in estrictos
    return {
        "p15": p15, "p25": p25, "p1t": p1t, "c15": c15, "c25": c25,
        "corners": random.choice(["8.5+", "9.5+", "10.5+"]),
        "t_rango": "5-9" if es_duro else "2-5",
        "roja": "ALTO" if es_duro else "BAJO"
    }

# --- TODAS LAS LIGAS (JORNADAS COMPLETAS) ---
DATOS_REALES = {
    "Ligue 1 (Francia)": [
        {"h": "Mónaco", "a": "Lorient", "f": "Vie 16/1 1:00 p.m.", "arb": "Benoît Bastien"},
        {"h": "PSG", "a": "Lille", "f": "Vie 16/1 3:00 p.m.", "arb": "Clément Turpin"},
        {"h": "Lens", "a": "Auxerre", "f": "Sáb 17/1 11:00 a.m.", "arb": "Dechepy"},
        {"h": "Toulouse", "a": "Niza", "f": "Sáb 17/1 1:00 p.m.", "arb": "Angoula"},
        {"h": "Angers", "a": "Marsella", "f": "Sáb 17/1 3:05 p.m.", "arb": "Buquet"},
        {"h": "Estrasburgo", "a": "Metz", "f": "Dom 18/1 9:00 a.m.", "arb": "Pignard"},
        {"h": "Rennes", "a": "Le Havre", "f": "Dom 18/1 11:15 a.m.", "arb": "Stéphanie Frappart"},
        {"h": "Nantes", "a": "Paris FC", "f": "Dom 18/1 11:15 a.m.", "arb": "Millot"},
        {"h": "Lyon", "a": "Brest", "f": "Dom 18/1 2:45 p.m.", "arb": "Lissorgue"}
    ],
    "Primeira Liga (Portugal)": [
        {"h": "Sporting CP", "a": "Casa Pia", "f": "Vie 16/1 3:15 p.m.", "arb": "Claudio Pereira"},
        {"h": "Gil Vicente", "a": "Nacional", "f": "Sáb 17/1 10:30 a.m.", "arb": "Bértolo Nogueira"},
        {"h": "AVS", "a": "Arouca", "f": "Sáb 17/1 1:00 p.m.", "arb": "João Pinheiro"},
        {"h": "Alverca", "a": "Moreirense", "f": "Sáb 17/1 1:00 p.m.", "arb": "Branco Godinho"},
        {"h": "Rio Ave", "a": "Benfica", "f": "Sáb 17/1 3:30 p.m.", "arb": "Ruivo Pereira"},
        {"h": "Santa Clara", "a": "Famalicão", "f": "Dom 18/1 10:30 a.m.", "arb": "Dias Torres"},
        {"h": "Tondela", "a": "Braga", "f": "Dom 18/1 1:00 p.m.", "arb": "Correia"},
        {"h": "Guimarães", "a": "Oporto", "f": "Dom 18/1 3:30 p.m.", "arb": "Ferreira Gonçalves"},
        {"h": "Estrela", "a": "Estoril", "f": "Lun 19/1 3:15 p.m.", "arb": "Ramalho"}
    ],
    "UEFA Champions League": [
        {"h": "Kairat", "a": "Club Brujas", "f": "Mar 20/1 10:30 a.m.", "arb": "Felix Zwayer"},
        {"h": "Bodø/Glimt", "a": "Man. City", "f": "Mar 20/1 12:45 p.m.", "arb": "Michael Oliver"},
        {"h": "Inter", "a": "Arsenal", "f": "Mar 20/1 3:00 p.m.", "arb": "Danny Makkelie"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "Mar 20/1 3:00 p.m.", "arb": "Slavko Vincic"},
        {"h": "Slavia Praga", "a": "Barcelona", "f": "Mié 21/1 3:00 p.m.", "arb": "Davide Massa"},
        {"h": "Atalanta", "a": "Athletic", "f": "Mié 21/1 3:00 p.m.", "arb": "Felix Zwayer"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "Sáb 17/1 7:30 a.m.", "arb": "Michael Oliver"},
        {"h": "Chelsea", "a": "Brentford", "f": "Sáb 17/1 10:00 a.m.", "arb": "Anthony Taylor"},
        {"h": "Liverpool", "a": "Burnley", "f": "Sáb 17/1 10:00 a.m.", "arb": "Paul Tierney"},
        {"h": "Brighton", "a": "Bournemouth", "f": "Lun 19/1 3:00 p.m.", "arb": "Andrew Madley"}
    ],
    "Serie A (Italia)": [
        {"h": "Inter", "a": "Empoli", "f": "Dom 18/1 6:30 a.m.", "arb": "Davide Massa"},
        {"h": "Juventus", "a": "Milan", "f": "Dom 19/1 2:45 p.m.", "arb": "Daniele Orsato"},
        {"h": "Lazio", "a": "Napoli", "f": "Dom 19/1 2:45 p.m.", "arb": "Marco Guida"}
    ],
    "La Liga (España)": [
        {"h": "Real Madrid", "a": "Levante", "f": "Sáb 17/1 3:00 p.m.", "arb": "Alberola Rojas"},
        {"h": "Barcelona", "a": "Real Sociedad", "f": "Dom 18/1 3:00 p.m.", "arb": "Hernández Hernández"}
    ],
    "Liga 1 (Perú)": [
        {"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Kevin Ortega"},
        {"h": "Universitario", "a": "ADT", "f": "01/02", "arb": "Diego Haro"}
    ]
}

# --- INTERFAZ ---
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
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
                if st.button(f"💾 Guardar", key=f"s_{p['h']}_{p['f']}"):
                    txt = f"📌 {p['h']}-{p['a']} | Pick: {s['p15']}% | Cuota: {s['c15']}"
                    db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                    db_conn.commit()
                    st.rerun()
            with b2:
                msg = f"*REPORTE ELITE ⚽*\n\n🔥 *{p['h']} vs {p['a']}*\n🟢 Prob. +1.5: {s['p15']}%\n🎯 Marcador: {marcador}\n🚩 Corners: {s['corners']}"
                encoded_msg = urllib.parse.quote(msg)
                st.markdown(f'<a href="https://wa.me/?text={encoded_msg}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)

with col_cart:
    st.header("🛒 Carrito Permanente")
    cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
    for d, f in cursor.fetchall():
        with st.chat_message("user"):
            st.caption(f)
            st.write(d)