import streamlit as st
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diamond v40.2 - Nube Master", layout="wide", page_icon="💎")

class DiamondScraper:
    def __init__(self):
        # cloudscraper ayuda a saltar protecciones sin usar Selenium
        self.scraper = cloudscraper.create_scraper()
        self.ligas_urls = {
            "Alemania 🇩🇪": "ger.1",
            "Inglaterra 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "eng.1",
            "Italia 🇮🇹": "ita.1",
            "Perú 🇵🇪": "per.1",
            "España 🇪🇸": "esp.1",
            "Portugal 🇵🇹": "por.1",
            "Francia 🇫🇷": "fra.1",
            "Champions League 🇪🇺": "uefa.champions",
            "Europa League 🇪🇺": "uefa.europa"
        }

    def scrapper_espn(self, liga_slug):
        """Versión ligera para Streamlit Cloud sin Selenium"""
        url = f"https://www.espn.com.pe/futbol/fixture/_/liga/{liga_slug}"
        try:
            response = self.scraper.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            partidos = []
            
            # Buscamos en las tablas de fixture de ESPN
            for table in soup.select('.Table__TBODY'):
                for row in table.select('tr.Table__TR'):
                    # Extraer equipos y estado
                    teams = row.select('.Table__Team a')
                    status = row.select_one('.date__col')
                    
                    if len(teams) >= 2:
                        partidos.append({
                            "home": teams[0].text.strip(),
                            "away": teams[1].text.strip(),
                            "info": status.text.strip() if status else "Previa"
                        })
            return partidos
        except Exception as e:
            st.error(f"Error de conexión: {str(e)}")
            return []

# --- MOTOR DE PROBABILIDAD (REDISEÑADO) ---
def motor_diamond(home, away, fatiga, estrellas):
    # Lógica de impacto basada en potencia de equipo
    base_h = 1.7 if any(x in home for x in ["City", "Real", "Bayern", "PSG", "Inter"]) else 1.2
    base_a = 1.0
    
    # Penalizaciones
    if fatiga: base_h *= 0.85
    if estrellas: base_h *= 0.80
    
    g_h = round(base_h + random.uniform(-0.3, 0.3))
    g_a = round(base_a + random.uniform(-0.2, 0.2))
    
    return {
        "score": f"{max(0, g_h)} - {max(0, g_a)}",
        "corners": "9.5+" if (g_h + g_a) > 2 else "8.5+",
        "roja": "ALTA" if fatiga or "Clásico" in home else "MEDIA"
    }

# --- INTERFAZ ---
sc = DiamondScraper()

st.sidebar.title("💎 DIAMOND v40.2")
st.sidebar.info("Modo: Nube (Sin Selenium)")
liga_sel = st.sidebar.selectbox("Ligas Master", list(sc.ligas_urls.keys()))

if st.button("🚀 Actualizar Cartelera"):
    with st.spinner(f"Buscando partidos de {liga_sel}..."):
        data = sc.scrapper_espn(sc.ligas_urls[liga_sel])
        st.session_state['partidos_v40_2'] = data

if 'partidos_v40_2' in st.session_state:
    partidos = st.session_state['partidos_v40_2']
    if not partidos:
        st.warning("No se encontraron partidos próximos en ESPN para esta liga.")
    else:
        st.success(f"Se detectaron {len(partidos)} partidos.")
        for i, p in enumerate(partidos):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.subheader(f"{p['home']} vs {p['away']}")
                    st.caption(f"📅 Estado: {p['info']}")
                
                with col2:
                    fatiga = st.checkbox("Factor Fatiga", key=f"f_{i}")
                    estrellas = st.checkbox("Baja Crítica", key=f"e_{i}")
                
                with col3:
                    if st.button("Analizar", key=f"b_{i}"):
                        res = motor_diamond(p['home'], p['away'], fatiga, estrellas)
                        st.subheader(f"🎯 {res['score']}")
                        st.write(f"🚩 Corners: {res['corners']}")
                        st.write(f"🟥 Roja: {res['roja']}")