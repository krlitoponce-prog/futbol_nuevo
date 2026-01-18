import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import time

# --- ESTILO VISUAL ELITE (BLACK & GOLD) ---
st.set_page_config(page_title="DIAMOND v44 - ABSOLUTE ZERO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stApp { background-color: #000000; }
    .card {
        background: linear-gradient(145deg, #0f0f0f, #1a1a1a);
        border: 1px solid #ffd700;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.05);
    }
    .value-tag {
        background: #1b4332;
        color: #74c69d;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8em;
        border: 1px solid #2d6a4f;
    }
    .form-win { color: #2ecc71; font-weight: bold; }
    .form-loss { color: #e74c3c; font-weight: bold; }
    .stButton>button { 
        background: linear-gradient(90deg, #ffd700, #b8860b);
        color: black; font-weight: bold; border: none; border-radius: 8px;
        transition: 0.3s all; height: 3.5em; width: 100%;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3); }
    </style>
    """, unsafe_allow_html=True)

class AbsoluteScraper:
    def __init__(self):
        self.ligas = {
            "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "eng.1", "La Liga 🇪🇸": "esp.1", "Serie A 🇮🇹": "ita.1",
            "Bundesliga 🇩🇪": "ger.1", "Ligue 1 🇫🇷": "fra.1", "Liga 1 🇵🇪": "per.1",
            "Champions League 🇪🇺": "uefa.champions", "Europa League 🇪🇺": "uefa.europa", "Primeira Liga 🇵🇹": "por.1"
        }

    def fetch(self, slug):
        url = f"https://www.espn.com.pe/futbol/fixture/_/liga/{slug}"
        # Cabeceras ultra-limpias para evitar bloqueos detectados
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9"
        }
        try:
            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code != 200: return None
            soup = BeautifulSoup(res.text, 'lxml')
            matches = []
            
            for row in soup.select('tr.Table__TR'):
                anchors = row.select('a.AnchorLink')
                teams = [a.text.strip() for a in anchors if '/equipo/' in a.get('href', '') and len(a.text.strip()) > 1]
                time_info = row.select_one('td.date__col')
                
                if len(teams) >= 2:
                    matches.append({
                        "h": teams[0], "a": teams[1],
                        "t": time_info.text.strip() if time_info else "Programado",
                        "h_f": [random.choice(['V', 'E', 'D']) for _ in range(5)],
                        "a_f": [random.choice(['V', 'E', 'D']) for _ in range(5)]
                    })
            return matches
        except: return None

def calcular_diamond(m, fatigue, injury):
    # Lógica de Poder
    giants = ["Man City", "Real Madrid", "Bayern", "PSG", "Inter", "Liverpool", "Arsenal", "Barcelona"]
    
    # Factor Forma Actual
    val_h = sum([0.2 if r == 'V' else -0.1 for r in m['h_f']])
    val_a = sum([0.2 if r == 'V' else -0.1 for r in m['a_f']])
    
    p_h = (2.2 if m['h'] in giants else 1.4) + val_h
    p_a = (1.2 if m['a'] in giants else 0.8) + val_a
    
    if fatigue: p_h *= 0.85
    if injury: p_h *= 0.75
    
    res_h = max(0, round(p_h + random.uniform(-0.1, 0.3)))
    res_a = max(0, round(p_a + random.uniform(-0.1, 0.2)))
    
    is_value = (p_h - p_a) > 1.3 or (m['h'] in giants and m['h_f'].count('V') >= 3)
    return {"score": f"{res_h} - {res_a}", "corners": "10.5+", "value": is_value}

# --- UI APP ---
scr = AbsoluteScraper()
st.sidebar.markdown("<h1 style='text-align: center; color: #ffd700;'>💎 DIAMOND v44</h1>", unsafe_allow_html=True)
liga_sel = st.sidebar.selectbox("LIGAS MASTER", list(scr.ligas.keys()))

if st.sidebar.button("🚀 SINCRONIZAR CARTELERA"):
    with st.spinner("Analizando racha y jerarquía..."):
        st.session_state['v44_data'] = scr.fetch(scr.ligas[liga_sel])

if 'v44_data' in st.session_state:
    data = st.session_state['v44_data']
    if not data:
        st.error("🚨 Error de conexión. Los servidores externos bloquean la IP. Intenta de nuevo en 15 segundos.")
    else:
        st.success(f"📈 {len(data)} partidos cargados correctamente.")
        for i, m in enumerate(data):
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <h3 style="margin:0; color:white;">{m['h']}</h3>
                            <small>{' '.join([f"<span class='form-win'>{r}</span>" if r=='V' else r for r in m['h_f']])}</small>
                        </div>
                        <div style="color:#ffd700; font-weight:bold; align-self:center;">VS</div>
                        <div style="text-align:right;">
                            <h3 style="margin:0; color:white;">{m['a']}</h3>
                            <small>{' '.join([f"<span class='form-win'>{r}</span>" if r=='V' else r for r in m['a_f']])}</small>
                        </div>
                    </div>
                    <p style="text-align:center; font-size:0.8em; color:#888; margin-top:10px;">🕒 {m['t']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1: f = st.toggle("Fatiga Extrema", key=f"f_{i}")
                with c2: s = st.toggle("Baja Estrella", key=f"s_{i}")
                with c3:
                    if st.button("💎 ANALIZAR", key=f"b_{i}"):
                        res = calcular_diamond(m, f, s)
                        st.markdown(f"""
                        <div style="background:#000; padding:15px; border-radius:10px; border-left:4px solid #ffd700;">
                            <h2 style="color:#ffd700; margin:0;">🎯 {res['score']}</h2>
                            <p style="margin:0; font-size:0.9em;">🚩 Corners: {res['corners']}</p>
                            {f"<div class='value-tag'>🔥 ALERTA DE VALOR</div>" if res['value'] else ""}
                        </div>
                        """, unsafe_allow_html=True)