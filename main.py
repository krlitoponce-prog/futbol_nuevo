import requests
from datetime import datetime, timedelta

API_KEY = "517365d4936aa3145d7be8f954b7c13b"
URL_BASE = "https://v3.football.api-sports.io/"

LIGAS_PRIORITARIAS = {
    "Premier League": 39, "La Liga": 140, "Serie A": 135, 
    "Bundesliga": 78, "Ligue 1": 61, "Liga 1 Perú": 281,
    "Champions League": 2, "Europa League": 3, "Primeira Liga": 94
}

def obtener_datos_avanzados(fixture_id):
    headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': "v3.football.api-sports.io"}
    
    # 1. Obtener Alineaciones (Lineups)
    lineups = requests.get(f"{URL_BASE}fixtures/lineups?fixture={fixture_id}", headers=headers).json()
    
    # 2. Obtener Lesionados (Injuries)
    injuries = requests.get(f"{URL_BASE}injuries?fixture={fixture_id}", headers=headers).json()
    
    return lineups, injuries

def calcular_diamond_pro(home_id, away_id, fixture_id):
    # Simulamos la obtención de fatiga revisando el calendario
    # Si jugó hace < 3 días: mod_fatiga = 0.85
    mod_fatiga_h = 1.0 
    
    # Ajuste por Lesiones de Estrellas
    # Si un jugador con > 10 goles está en la lista de lesionados:
    mod_ataque_h = 0.78 # Reducción por ausencia de estrella
    
    # Aplicación de Poisson para Marcador Exacto
    # (Aquí se conecta con las stats históricas de la API)
    goles_esperados_h = 1.65 * mod_ataque_h * mod_fatiga_h
    goles_esperados_a = 1.10
    
    return round(goles_esperados_h), round(goles_esperados_a)