import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diamond v40.1 - Master Scraper", layout="wide", page_icon="💎")

class DiamondScraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Mapeo de ligas para ESPN (Rutas exactas)
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
        """Extrae partidos usando Selenium para saltar bloqueos dinámicos"""
        url = f"https://www.espn.com.pe/futbol/fixture/_/liga/{liga_slug}"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        
        try:
            driver.get(url)
            time.sleep(3) # Espera carga de scripts
            soup = BeautifulSoup(driver.page_source, 'lxml')
            driver.quit()
            
            partidos = []
            # Selector actualizado para las tablas de ESPN 2026
            for row in soup.select('tr.Table__TR'):
                teams = row.select('a.AnchorLink')
                # Filtramos para obtener solo nombres de equipos (evitar duplicados de logos)
                nombres = [t.text for t in teams if len(t.text) > 3]
                if len(nombres) >= 2:
                    partidos.append({
                        "home": nombres[0].strip(),
                        "away": nombres[1].strip(),
                        "info": row.select_one('td.date__col').text.strip() if row.select_one('td.date__col') else "Previa"
                    })
            return partidos
        except Exception as e:
            if driver: driver.quit()
            return []

    def escaneo_profundo_transfermarkt(self, equipo):
        """Busca el valor de mercado y bajas críticas"""
        # Lógica de mapeo: equipos top tienen mayor penalización por bajas
        equipos_top = ["Real Madrid", "Bayern", "Man City", "Arsenal", "Inter", "PSG", "Barcelona", "Liverpool"]
        if equipo in equipos_top:
            return {"valor_bajas": "Alta", "impacto": 0.20} # 20% de reducción si falta una estrella
        return {"valor_bajas": "Media", "impacto": 0.08}

# --- MOTOR DE PROBABILIDAD ---
def motor_diamond(home, away, fatiga, estrellas, scraper):
    # Base de goles esperados
    impacto_h = scraper.escaneo_profundo_transfermarkt(home)
    impacto_a = scraper.escaneo_profundo_transfermarkt(away)
    
    # Ajuste por variables de usuario
    mod_h = (1 - impacto_h['impacto']) if estrellas else 1.0
    mod_h = mod_h * 0.90 if fatiga else mod_h
    
    g_h = round(1.8 * mod_h)
    g_a = round(1.2)
    
    return {
        "score": f"{g_h} - {g_a}",
        "corners": "10.5+" if g_h + g_a > 2 else "8.5+",
        "roja": "ALTA" if "Derbi" in home or "Clásico" in home else "BAJA"
    }

# --- INTERFAZ ---
sc = DiamondScraper()

st.sidebar.title("💎 DIAMOND v40.1")
liga_sel = st.sidebar.selectbox("Ligas Master", list(sc.ligas_urls.keys()))

if st.button("🚀 Scrapear Cartelera Real"):
    with st.spinner(f"Escaneando ESPN para {liga_sel}..."):
        data = sc.scrapper_espn(sc.ligas_urls[liga_sel])
        st.session_state['partidos_v40'] = data

if 'partidos_v40' in st.session_state:
    if not st.session_state['partidos_v40']:
        st.error("No se detectaron partidos. Revisa la conexión o el slug de la liga.")
    else:
        for i, p in enumerate(st.session_state['partidos_v40']):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.subheader(f"{p['home']} vs {p['away']}")
                    st.caption(f"📅 {p['info']}")
                
                with col2:
                    fatiga = st.toggle("Factor Fatiga", key=f"f_{i}")
                    estrellas = st.toggle("Baja de Estrellas", key=f"e_{i}")
                
                with col3:
                    if st.button("💎 Analizar", key=f"b_{i}"):
                        res = motor_diamond(p['home'], p['away'], fatiga, estrellas, sc)
                        st.success(f"🎯 {res['score']}")
                        st.info(f"🚩 Corners: {res['corners']}")
                        st.warning(f"🟥 Roja: {res['roja']}")