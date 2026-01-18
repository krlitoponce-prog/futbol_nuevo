import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- CONFIGURACIÓN VISUAL (ESTILO DARK GOLD) ---
st.set_page_config(page_title="DIAMOND v41 - MASTER", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #d4af37; color: black; font-weight: bold; }
    .match-card { border: 1px solid #d4af37; padding: 20px; border-radius: 15px; background-color: #1a1c23; margin-bottom: 15px; }
    .stat-box { text-align: center; padding: 10px; border-radius: 8px; background: #262730; }
    </style>
    """, unsafe_allow_html=True)

class MasterScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
        self.ligas = {
            "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "eng.1", "La Liga 🇪🇸": "esp.1", "Serie A 🇮🇹": "ita.1",
            "Bundesliga 🇩🇪": "ger.1", "Ligue 1 🇫🇷": "fra.1", "Liga 1 🇵🇪": "per.1",
            "Champions League 🇪🇺": "uefa.champions", "Europa League 🇪🇺": "uefa.europa", "Primeira Liga 🇵🇹": "por.1"
        }

    def obtener_datos(self, slug):
        url = f"https://www.espn.com.pe/futbol/fixture/_/liga/{slug}"
        try:
            res = self.scraper.get(url, timeout=15)
            if res.status_code != 200: return None
            soup = BeautifulSoup(res.text, 'lxml')
            partidos = []
            
            for table in soup.select('.Table__TBODY'):
                for row in table.select('tr.Table__TR'):
                    teams = row.select('.Table__Team a')
                    status = row.select_one('.date__col')
                    if len(teams) >= 2:
                        partidos.append({
                            "home": teams[0].text.strip(),
                            "away": teams[1].text.strip(),
                            "info": status.text.strip() if status else "Próximamente"
                        })
            return partidos
        except: return None

# --- MOTOR DE PRONÓSTICO DE ALTA PRECISIÓN ---
def analizar_partido(h, a, f, e):
    # Diccionario de jerarquía para xG (Goles Esperados)
    tops = ["Real Madrid", "Man City", "Bayern", "PSG", "Inter", "Arsenal", "Barcelona", "Liverpool"]
    
    # Base de potencia
    pwr_h = 2.1 if h in tops else 1.4
    pwr_a = 1.3 if a in tops else 0.9
    
    # Aplicación estricta de factores externos
    if f: pwr_h *= 0.82  # Reducción por fatiga (Doble competición)
    if e: pwr_h *= 0.75  # Reducción por bajas de estrellas (Transfermarkt logic)
    
    g_h = round(pwr_h)
    g_a = round(pwr_a)
    
    # Cálculo de mercados secundarios
    corners = "10.5+" if (pwr_h + pwr_a) > 2.8 else "8.5+"
    tarjetas = "5-7" if f or e else "3-5"
    riesgo_roja = "ALTO" if f and e else "MEDIO"
    
    return {"score": f"{g_h} - {g_a}", "corners": corners, "cards": tarjetas, "roja": riesgo_roja}

# --- INTERFAZ PRINCIPAL ---
ms = MasterScraper()
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1053/1053915.png", width=100)
st.sidebar.title("DIAMOND ELITE v41")
liga_sel = st.sidebar.selectbox("SELECCIONAR COMPETICIÓN", list(ms.ligas.keys()))

if st.sidebar.button("🚀 ACTUALIZAR CARTELERA"):
    with st.spinner("Escaneando fuentes globales..."):
        resultados = ms.obtener_datos(ms.ligas[liga_sel])
        st.session_state['data_v41'] = resultados

if 'data_v41' in st.session_state:
    partidos = st.session_state['data_v41']
    if not partidos:
        st.error("⚠️ Error de conexión con la fuente. Intente actualizar nuevamente.")
    else:
        st.success(f"✅ {len(partidos)} partidos analizados con éxito.")
        
        for i, p in enumerate(partidos):
            with st.container():
                st.markdown(f"""<div class="match-card">
                    <h3 style='text-align: center; color: #d4af37;'>{p['home']} vs {p['away']}</h3>
                    <p style='text-align: center; font-size: 0.8em;'>{p['info']}</p>
                </div>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1: fatiga = st.checkbox("🏟️ Doble Torneo/Fatiga", key=f"f_{i}")
                with c2: bajas = st.checkbox("🚑 Bajas de Estrellas", key=f"b_{i}")
                with c3: 
                    if st.button("📊 ANALIZAR", key=f"btn_{i}"):
                        res = analizar_partido(p['home'], p['away'], fatiga, bajas)
                        st.markdown("---")
                        res_cols = st.columns(4)
                        res_cols[0].metric("🎯 MARCADOR", res['score'])
                        res_cols[1].metric("🚩 CORNERS", res['corners'])
                        res_cols[2].metric("🟨 TARJETAS", res['cards'])
                        res_cols[3].metric("🟥 RIESGO ROJA", res['roja'])