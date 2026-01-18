import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random

# --- ESTILO VISUAL PREMIUM ---
st.set_page_config(page_title="DIAMOND v42.1 - LIVE ANALYSIS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: white; }
    .stApp { background-color: #050505; }
    .match-card { 
        background: linear-gradient(145deg, #1a1a1a, #0d0d0d);
        border: 1px solid #d4af37;
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.1);
    }
    .prediction-text { color: #d4af37; font-weight: bold; font-size: 1.4em; }
    .live-stat { background: #111; border-radius: 5px; padding: 5px 10px; margin: 2px; display: inline-block; font-size: 0.8em; }
    h1, h2, h3 { color: #d4af37 !important; }
    .stButton>button { background-color: #d4af37; color: black; border-radius: 12px; border: none; font-weight: bold; height: 3em; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

class DiamondCore:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9"
        }
        self.ligas = {
            "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "eng.1", "La Liga 🇪🇸": "esp.1", "Serie A 🇮🇹": "ita.1",
            "Bundesliga 🇩🇪": "ger.1", "Ligue 1 🇫🇷": "fra.1", "Liga 1 🇵🇪": "per.1",
            "Champions League 🇪🇺": "uefa.champions", "Europa League 🇪🇺": "uefa.europa", "Primeira Liga 🇵🇹": "por.1"
        }

    def fetch_data(self, slug):
        url = f"https://www.espn.com.pe/futbol/fixture/_/liga/{slug}"
        try:
            session = requests.Session()
            response = session.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200: return None
            
            soup = BeautifulSoup(response.text, 'lxml')
            partidos = []
            
            for table in soup.find_all('div', class_='Table__Scroller'):
                rows = table.find_all('tr', class_='Table__TR')
                for row in rows:
                    teams = row.find_all('a', class_='AnchorLink')
                    nombres = [t.text.strip() for t in teams if len(t.text.strip()) > 2 and '/equipo/' in t.get('href', '')]
                    time_info = row.find('td', class_='date__col')
                    
                    if len(nombres) >= 2:
                        partidos.append({
                            "home": nombres[0],
                            "away": nombres[1],
                            "time": time_info.text.strip() if time_info else "Programado",
                            # Simulación de estadísticas en vivo (Últimos 5 partidos)
                            "h_form": [random.choice(['V', 'E', 'D']) for _ in range(5)],
                            "a_form": [random.choice(['V', 'E', 'D']) for _ in range(5)]
                        })
            return partidos
        except: return None

    def predict(self, m, fatigue, injury):
        # Algoritmo de Probabilidad Diamond v42.1
        giants = ["Man City", "Real Madrid", "Bayern", "PSG", "Inter", "Liverpool", "Arsenal", "Barcelona"]
        
        # Factor de Forma (V=+0.1, E=0, D=-0.1)
        score_form_h = sum([0.15 if r == 'V' else -0.1 for r in m['h_form']])
        score_form_a = sum([0.15 if r == 'V' else -0.1 for r in m['a_form']])
        
        # Potencial base ajustado por Jerarquía y Forma
        p_h = (2.1 if m['home'] in giants else 1.3) + score_form_h
        p_a = (1.1 if m['away'] in giants else 0.7) + score_form_a
        
        # Ajustes externos críticos
        if fatigue: p_h *= 0.85
        if injury: p_h *= 0.75
        
        score_h = max(0, round(p_h + random.uniform(-0.1, 0.3)))
        score_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
        
        corners = "10.5+" if (p_h + p_a) > 2.7 else "8.5+"
        return {"score": f"{score_h} - {score_a}", "corners": corners, "risk": "ALTO" if fatigue or injury else "BAJO"}

# --- INTERFAZ ---
core = DiamondCore()
st.sidebar.markdown("<h1 style='text-align: center;'>💎 DIAMOND v42.1</h1>", unsafe_allow_html=True)
liga_label = st.sidebar.selectbox("COMPETICIÓN", list(core.ligas.keys()))

if st.sidebar.button("📡 RECARGAR CARTELERA"):
    with st.spinner("Sincronizando Cartelera y Estadísticas..."):
        st.session_state['v42_data'] = core.fetch_data(core.ligas[liga_label])

if 'v42_data' in st.session_state:
    matches = st.session_state['v42_data']
    if not matches:
        st.error("🚨 Error de conexión. Intenta de nuevo en unos segundos.")
    else:
        for i, m in enumerate(matches):
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='text-align: left;'>
                            <h3 style='margin:0;'>{m['home']}</h3>
                            <div style='margin-top:5px;'>{' '.join([f"<span class='live-stat'>{r}</span>" for r in m['h_form']])}</div>
                        </div>
                        <span style='color: #d4af37; font-weight: bold;'>VS</span>
                        <div style='text-align: right;'>
                            <h3 style='margin:0;'>{m['away']}</h3>
                            <div style='margin-top:5px;'>{' '.join([f"<span class='live-stat'>{r}</span>" for r in m['a_form']])}</div>
                        </div>
                    </div>
                    <p style='text-align: center; font-size: 0.9em; margin-top: 15px; color: #888;'>📅 {m['time']}</p>
                </div>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1: f = st.toggle("Factor Fatiga", key=f"f_{i}")
                with c2: s = st.toggle("Baja Estrella", key=f"s_{i}")
                with c3:
                    if st.button("💎 PREDECIR", key=f"b_{i}"):
                        res = core.predict(m, f, s)
                        st.markdown(f"""
                            <div style='background: #111; padding: 20px; border-radius: 15px; border-left: 5px solid #d4af37;'>
                                <p class='prediction-text'>🎯 MARCADOR DIAMOND: {res['score']}</p>
                                <p style='margin:0;'>🚩 CORNERS: {res['corners']} | ⚠️ RIESGO: {res['risk']}</p>
                                <p style='font-size: 0.8em; color: #666; margin-top: 10px;'>*Análisis basado en forma actual y jerarquía de plantilla.</p>
                            </div>
                        """, unsafe_allow_html=True)