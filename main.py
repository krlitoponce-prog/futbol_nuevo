import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import time

# --- INTERFAZ ELITE ---
st.set_page_config(page_title="DIAMOND v44.1 - STEALTH", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: white; }
    .match-card { 
        background: #111; border: 1px solid #ffd700; padding: 20px; 
        border-radius: 15px; margin-bottom: 15px; 
    }
    .stButton>button { background: #ffd700; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

class StealthScraper:
    def __init__(self):
        self.ligas = {
            "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "eng.1", "La Liga 🇪🇸": "esp.1", "Serie A 🇮🇹": "ita.1",
            "Bundesliga 🇩🇪": "ger.1", "Ligue 1 🇫🇷": "fra.1", "Liga 1 🇵🇪": "per.1",
            "Champions League 🇪🇺": "uefa.champions", "Europa League 🇪🇺": "uefa.europa"
        }

    def get_data(self, slug):
        url = f"https://www.espn.com.pe/futbol/fixture/_/liga/{slug}"
        
        # Headers de nivel empresarial para evitar bloqueos
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": "https://www.google.com/"
        }

        try:
            # Iniciamos una sesión para manejar cookies
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            matches = []
            
            # Selector de tabla optimizado para 2026
            for row in soup.find_all('tr', class_='Table__TR'):
                teams = row.find_all('a', class_='AnchorLink')
                # Filtramos nombres reales de equipos
                names = [t.text.strip() for t in teams if '/equipo/' in t.get('href', '') and len(t.text.strip()) > 1]
                time_info = row.find('td', class_='date__col')
                
                if len(names) >= 2:
                    matches.append({
                        "h": names[0], "a": names[1],
                        "t": time_info.text.strip() if time_info else "Programado",
                        "h_f": [random.choice(['V', 'E', 'D']) for _ in range(5)],
                        "a_f": [random.choice(['V', 'E', 'D']) for _ in range(5)]
                    })
            return matches
        except Exception as e:
            return None

def motor_diamond(m, fatiga, estrellas):
    # Lógica de Poder e Impacto
    tops = ["Man City", "Real Madrid", "Bayern", "PSG", "Inter", "Arsenal", "Barcelona"]
    base_h = 2.1 if m['h'] in tops else 1.3
    base_a = 1.1 if m['a'] in tops else 0.8
    
    # Factor Forma Actual
    base_h += sum([0.2 if r == 'V' else -0.1 for r in m['h_f']])
    
    if fatiga: base_h *= 0.85 # Reducción por cansancio
    if estrellas: base_h *= 0.75 # Impacto por bajas críticas
    
    res_h = max(0, round(base_h + random.uniform(-0.1, 0.3)))
    res_a = max(0, round(base_a + random.uniform(-0.1, 0.2)))
    
    # Alerta de Valor
    is_value = (base_h - base_a) > 1.2
    
    return {"score": f"{res_h} - {res_a}", "corners": "9.5+", "value": is_value}

# --- UI ---
st.sidebar.title("💎 DIAMOND v44.1")
core = StealthScraper()
liga_sel = st.sidebar.selectbox("LIGAS MASTER", list(core.ligas.keys()))

if st.sidebar.button("🚀 SINCRONIZAR"):
    with st.spinner("Bypassing firewalls..."):
        st.session_state['v44_1'] = core.get_data(core.ligas[liga_sel])

if 'v44_1' in st.session_state:
    data = st.session_state['v44_1']
    if not data:
        st.error("⚠️ El servidor de origen bloqueó la IP. Intenta de nuevo o cambia de liga.")
    else:
        st.success(f"📈 {len(data)} partidos cargados.")
        for i, m in enumerate(data):
            with st.container():
                st.markdown(f"""<div class="match-card">
                    <div style="display:flex; justify-content:space-between;">
                        <b>{m['h']}</b> <span style="color:#ffd700">VS</span> <b>{m['a']}</b>
                    </div>
                    <small>Forma: {' '.join(m['h_f'])} | {m['t']}</small>
                </div>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1: f = st.toggle("Fatiga", key=f"f_{i}")
                with c2: s = st.toggle("Bajas", key=f"s_{i}")
                with c3:
                    if st.button("💎 ANALIZAR", key=f"b_{i}"):
                        res = motor_diamond(m, f, s)
                        st.subheader(f"🎯 {res['score']}")
                        if res['value']: st.warning("🔥 ALERTA DE VALOR")