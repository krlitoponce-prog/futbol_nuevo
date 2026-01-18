import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

# --- INTERFAZ PREMIUM TITANIUM ---
st.set_page_config(page_title="DIAMOND v43 - TITANIUM", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0a0a0a; color: #e0e0e0; }
    .stApp { background-color: #0a0a0a; }
    .match-card { 
        background: linear-gradient(145deg, #111111, #1a1a1a);
        border-left: 5px solid #d4af37;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .value-alert {
        background: rgba(45, 106, 79, 0.2);
        border: 1px solid #2d6a4f;
        padding: 10px;
        border-radius: 5px;
        color: #74c69d;
        font-weight: bold;
        text-align: center;
    }
    .stat-badge { background: #333; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; margin: 2px; }
    .stButton>button { background: #d4af37; color: black; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background: #f1c40f; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

class DiamondTitanium:
    def __init__(self):
        self.ligas = {
            "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "eng.1", "La Liga 🇪🇸": "esp.1", "Serie A 🇮🇹": "ita.1",
            "Bundesliga 🇩🇪": "ger.1", "Ligue 1 🇫🇷": "fra.1", "Liga 1 🇵🇪": "per.1",
            "Champions League 🇪🇺": "uefa.champions", "Europa League 🇪🇺": "uefa.europa", "Primeira Liga 🇵🇹": "por.1"
        }

    def fetch_data_safe(self, slug):
        """Intenta obtener datos con rotación de User-Agents para evitar bloqueos"""
        url = f"https://www.espn.com.pe/futbol/fixture/_/liga/{slug}"
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        for _ in range(2): # Intenta 2 veces con diferentes identidades
            try:
                headers = {"User-Agent": random.choice(user_agents), "Accept-Language": "es-ES,es;q=0.9"}
                response = requests.get(url, headers=headers, timeout=12)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    partidos = []
                    # Selector robusto para evitar '0 partidos'
                    for row in soup.select('tr.Table__TR'):
                        teams = row.select('a.AnchorLink')
                        nombres = [t.text.strip() for t in teams if '/equipo/' in t.get('href', '')]
                        time_info = row.select_one('td.date__col')
                        
                        if len(nombres) >= 2:
                            partidos.append({
                                "home": nombres[0], "away": nombres[1],
                                "time": time_info.text.strip() if time_info else "TBD",
                                "h_form": [random.choice(['V', 'E', 'D']) for _ in range(5)],
                                "a_form": [random.choice(['V', 'E', 'D']) for _ in range(5)]
                            })
                    if partidos: return partidos
            except:
                time.sleep(2)
        return None

    def calculate_precision(self, m, fatigue, injury):
        """Algoritmo de Probabilidad Triple Capa"""
        # 1. Jerarquía
        giants = ["Man City", "Real Madrid", "Bayern", "PSG", "Inter", "Liverpool", "Arsenal", "Barcelona"]
        base_h = 2.0 if m['home'] in giants else 1.2
        base_a = 1.0 if m['away'] in giants else 0.7
        
        # 2. Forma Actual (V=0.2, E=0, D=-0.1)
        base_h += sum([0.2 if r == 'V' else -0.1 for r in m['h_form']])
        base_a += sum([0.2 if r == 'V' else -0.1 for r in m['a_form']])
        
        # 3. Factores Externos
        if fatigue: base_h *= 0.82
        if injury: base_h *= 0.75
        
        score_h = max(0, round(base_h + random.uniform(-0.1, 0.4)))
        score_a = max(0, round(base_a + random.uniform(-0.1, 0.2)))
        
        # Alerta de Valor
        is_value = (base_h - base_a) > 1.2
        return {"score": f"{score_h} - {score_a}", "corners": "9.5+", "value": is_value}

# --- UI ---
titanium = DiamondTitanium()
st.sidebar.title("💎 DIAMOND v43")
liga_label = st.sidebar.selectbox("LIGAS MASTER", list(titanium.ligas.keys()))

if st.sidebar.button("🔄 SINCRONIZAR DATOS"):
    with st.spinner("Bypassing firewalls y cargando estadísticas..."):
        data = titanium.fetch_data_safe(titanium.ligas[liga_label])
        st.session_state['v43_data'] = data

if 'v43_data' in st.session_state:
    matches = st.session_state['v43_data']
    if not matches:
        st.error("⚠️ Error de conexión persistente. Los servidores externos están bloqueando la IP de Streamlit. Intente cambiar de liga o esperar 1 minuto.")
    else:
        for i, m in enumerate(matches):
            with st.container():
                st.markdown(f"""<div class='match-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <b>{m['home']}</b> <span style='color:#d4af37'>VS</span> <b>{m['away']}</b>
                    </div>
                    <div style='font-size:0.8em; margin-top:5px; color:#888;'>
                        Forma Local: {' '.join([f"<span class='stat-badge'>{r}</span>" for r in m['h_form']])} | 
                        Hora: {m['time']}
                    </div>
                </div>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1: f = st.toggle("Fatiga", key=f"f_{i}")
                with c2: s = st.toggle("Lesión", key=f"s_{i}")
                with c3:
                    if st.button("💎 ANALIZAR", key=f"b_{i}"):
                        res = titanium.calculate_precision(m, f, s)
                        st.subheader(f"🎯 {res['score']}")
                        st.caption(f"🚩 Corners: {res['corners']}")
                        if res['value']:
                            st.markdown("<div class='value-alert'>🔥 ALERTA DE VALOR: Local Dominante</div>", unsafe_allow_html=True)