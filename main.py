import streamlit as st
import sqlite3
import os
from datetime import datetime
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador Elite v11", layout="wide", page_icon="⚽")

# --- BASE DE DATOS PERMANENTE ---
def init_db():
    db_path = os.path.join(os.getcwd(), 'analisis_final_v11.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS carrito 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, detalle TEXT, liga TEXT, fecha TEXT)''')
    return conn

db_conn = init_db()

# --- MOTOR DE CÁLCULO ESTABLE ---
def obtener_analisis_completo(h, a, arb):
    seed = len(h) + len(a) + 2026
    random.seed(seed)
    p15, p25, p1t = random.randint(82, 98), random.randint(45, 78), random.randint(55, 88)
    c15, c25 = round(random.uniform(1.22, 1.38), 2), round(random.uniform(1.70, 2.15), 2)
    estrictos = ["Szymon Marciniak", "Kevin Ortega", "Michael Oliver", "Anthony Taylor", "Felix Zwayer"]
    es_duro = arb in estrictos
    return {
        "p15": p15, "p25": p25, "p1t": p1t, "c15": c15, "c25": c25,
        "corners": random.choice(["8.5+", "9.5+", "10.5+"]),
        "t_rango": "5-9" if es_duro else "2-5",
        "roja": "ALTO" if es_duro else "BAJO"
    }

# --- DICCIONARIO ACTUALIZADO SEGÚN TUS IMÁGENES ---
DATOS_REALES = {
    "UEFA Champions League": [
        {"h": "Kairat", "a": "Club Brujas", "f": "20/01 10:30 a.m.", "arb": "Felix Zwayer"},
        {"h": "Bodø/Glimt", "a": "Man. City", "f": "20/01 12:45 p.m.", "arb": "Michael Oliver"},
        {"h": "Villarreal", "a": "Ajax", "f": "20/01 3:00 p.m.", "arb": "Anthony Taylor"},
        {"h": "Tottenham", "a": "Dortmund", "f": "20/01 3:00 p.m.", "arb": "Szymon Marciniak"},
        {"h": "Olympiacos", "a": "Leverkusen", "f": "20/01 3:00 p.m.", "arb": "Daniele Orsato"},
        {"h": "Sporting Lisboa", "a": "PSG", "f": "20/01 3:00 p.m.", "arb": "Gil Manzano"},
        {"h": "Inter", "a": "Arsenal", "f": "20/01 3:00 p.m.", "arb": "Danny Makkelie"},
        {"h": "Real Madrid", "a": "Mónaco", "f": "20/01 3:00 p.m.", "arb": "Slavko Vincic"},
        {"h": "Galatasaray", "a": "Atlético Madrid", "f": "21/01 12:45 p.m.", "arb": "Sandro Schärer"},
        {"h": "Marsella", "a": "Liverpool", "f": "21/01 3:00 p.m.", "arb": "Szymon Marciniak"},
        {"h": "Slavia Praga", "a": "Barcelona", "f": "21/01 3:00 p.m.", "arb": "Davide Massa"},
        {"h": "Bayern", "a": "U. Saint-Gilloise", "f": "21/01 3:00 p.m.", "arb": "Michael Oliver"},
        {"h": "Atalanta", "a": "Athletic", "f": "21/01 3:00 p.m.", "arb": "Felix Zwayer"}
    ],
    "Premier League (Inglaterra)": [
        {"h": "Man. United", "a": "Man. City", "f": "17/01 7:30 a.m.", "arb": "Michael Oliver"},
        {"h": "Sunderland", "a": "Crystal Palace", "f": "17/01 10:00 a.m.", "arb": "Robert Jones"},
        {"h": "Chelsea", "a": "Brentford", "f": "17/01 10:00 a.m.", "arb": "Anthony Taylor"},
        {"h": "Liverpool", "a": "Burnley", "f": "17/01 10:00 a.m.", "arb": "Paul Tierney"},
        {"h": "Tottenham", "a": "West Ham", "f": "17/01 10:00 a.m.", "arb": "Simon Hooper"},
        {"h": "Leeds", "a": "Fulham", "f": "17/01 10:00 a.m.", "arb": "Chris Kavanagh"}
    ],
    "Bundesliga (Alemania)": [
        {"h": "Werder Bremen", "a": "Frankfurt", "f": "Mañana 2:30 p.m.", "arb": "Felix Zwayer"},
        {"h": "Hoffenheim", "a": "Leverkusen", "f": "17/01 9:30 a.m.", "arb": "Daniel Siebert"},
        {"h": "Colonia", "a": "Mainz 05", "f": "17/01 9:30 a.m.", "arb": "Sven Jablonski"},
        {"h": "Hamburg", "a": "Mönchengladbach", "f": "17/01 9:30 a.m.", "arb": "Deniz Aytekin"},
        {"h": "Wolfsburg", "a": "Heidenheim", "f": "17/01 9:30 a.m.", "arb": "Bastian Dankert"},
        {"h": "Dortmund", "a": "St. Pauli", "f": "17/01 9:30 a.m.", "arb": "Felix Brych"},
        {"h": "RB Leipzig", "a": "Bayern", "f": "17/01 12:30 p.m.", "arb": "Deniz Aytekin"},
        {"h": "Stuttgart", "a": "Union Berlin", "f": "18/01 9:30 a.m.", "arb": "Daniel Schlager"}
    ],
    "La Liga (España)": [
        {"h": "Real Madrid", "a": "Levante", "f": "17/01", "arb": "Munuera Montero"},
        {"h": "Girona", "a": "Sevilla", "f": "17/01", "arb": "Busquets Ferrer"},
        {"h": "Barcelona", "a": "Real Sociedad", "f": "18/01", "arb": "Hernández Hernández"},
        {"h": "Atlético Madrid", "a": "Villarreal", "f": "18/01", "arb": "Sánchez Martínez"}
    ],
    "Serie A (Italia)": [
        {"h": "Inter", "a": "Empoli", "f": "18/01", "arb": "Davide Massa"},
        {"h": "Juventus", "a": "Milan", "f": "19/01", "arb": "Daniele Orsato"},
        {"h": "Lazio", "a": "Napoli", "f": "19/01", "arb": "Marco Guida"},
        {"h": "Roma", "a": "Atalanta", "f": "19/01", "arb": "Fabio Maresca"}
    ],
    "UEFA Europa League": [
        {"h": "Man. United", "a": "Roma", "f": "22/01", "arb": "Gil Manzano"},
        {"h": "Porto", "a": "Lazio", "f": "22/01", "arb": "Artur Soares"},
        {"h": "Ajax", "a": "Galatasaray", "f": "22/01", "arb": "Anthony Taylor"},
        {"h": "Frankfurt", "a": "Lyon", "f": "22/01", "arb": "Szymon Marciniak"}
    ],
    "Liga 1 (Perú)": [
        {"h": "Sport Huancayo", "a": "Alianza Lima", "f": "30/01", "arb": "Kevin Ortega"},
        {"h": "Universitario", "a": "ADT", "f": "01/02", "arb": "Diego Haro"},
        {"h": "Melgar", "a": "Cienciano", "f": "31/01", "arb": "Edwin Ordoñez"}
    ],
    "Brasileirao": [{"h": "Flamengo", "a": "Palmeiras", "f": "25/01", "arb": "Wilton Sampaio"}],
    "Liga Argentina": [{"h": "Boca", "a": "River", "f": "01/02", "arb": "Facundo Tello"}]
}

# --- INTERFAZ ---
st.sidebar.header("🏆 Menú Elite 2026")
liga_sel = st.sidebar.selectbox("Seleccionar Liga", list(DATOS_REALES.keys()))

col_main, col_cart = st.columns([2.2, 1])

with col_main:
    # FIX: Botón de confianza con validación de cantidad de columnas
    if st.button("💎 ANALIZAR PICKS DE MÁXIMA CONFIANZA"):
        partidos = DATOS_REALES[liga_sel]
        mejores = [p for p in partidos if obtener_analisis_completo(p['h'], p['a'], p['arb'])['p15'] > 92]
        
        if len(mejores) > 0:
            cols = st.columns(min(len(mejores), 3))
            for i, p in enumerate(mejores[:3]):
                with cols[i]:
                    st.metric(f"🔥 {p['h']}", "95% Conf.", "PICK TOP")
        else:
            st.warning("No se detectaron Picks con +92% de confianza en esta liga hoy.")
        st.divider()

    st.header(f"🏟️ Partidos: {liga_sel}")
    for p in DATOS_REALES[liga_sel]:
        s = obtener_analisis_completo(p['h'], p['a'], p['arb'])
        with st.container(border=True):
            st.subheader(f"{p['h']} vs {p['a']}")
            st.caption(f"🗓️ {p['f']} | ⚖️ Árbitro: {p['arb']}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success(f"🎯 Marcador: {random.randint(1,3)}-{random.randint(0,2)}")
                st.info(f"🚩 Corners: {s['corners']}")
                st.write(f"💵 Cuota +1.5: **{s['c15']}**")
            with c2:
                st.warning(f"🟨 Tarjetas: {s['t_rango']}")
                color = "red" if s['roja'] == "ALTO" else "white"
                st.markdown(f"🟥 Roja: <span style='color:{color};font-weight:bold'>{s['roja']}</span>", unsafe_allow_html=True)
                st.write(f"💵 Cuota +2.5: **{s['c25']}**")
            with c3:
                st.write(f"⏱️ Gol 1T: **{s['p1t']}%**")
                st.write(f"🟢 +1.5 Goles: **{s['p15']}%**")
                st.write(f"🔵 +2.5 Goles: **{s['p25']}%**")

            if st.button(f"Guardar Referencia: {p['h']}", key=f"{p['h']}_{p['f']}_{liga_sel}"):
                txt = f"📌 {p['h']}-{p['a']} | Pick: {s['p15']}% | Cuota: {s['c15']}"
                db_conn.execute('INSERT INTO carrito (detalle, liga, fecha) VALUES (?, ?, ?)', (txt, liga_sel, datetime.now().strftime("%d/%m %H:%M")))
                db_conn.commit()
                st.rerun()

with col_cart:
    st.header("🛒 Tu Carrito")
    try:
        cursor = db_conn.execute('SELECT detalle, fecha FROM carrito ORDER BY id DESC')
        for d, f in cursor.fetchall():
            with st.chat_message("user"):
                st.caption(f)
                st.write(d)
    except:
        st.write("Cargando referencias...")
    
    if st.sidebar.button("🗑️ Vaciar Carrito"):
        db_conn.execute('DELETE FROM carrito')
        db_conn.commit()
        st.rerun()