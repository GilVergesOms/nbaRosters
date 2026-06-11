import json
import time
from datetime import datetime
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo

def calcular_edad(birthdate_str):
    """Calcula la edad a partir de una cadena de texto (ej: '1993-07-20T00:00:00')"""
    try:
        # La API suele devolverlo en formato ISO o con la T de tiempo
        fecha_nacimiento = datetime.strptime(birthdate_str.split('T')[0], "%Y-%m-%d")
        hoy = datetime.today()
        return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    except Exception:
        return "N/A"

def obtener_datos_nba():
    print("Iniciando la recolección completa de datos enriquecidos de la NBA...")
    
    jugadores_activos = players.get_active_players()
    total_jugadores = len(jugadores_activos)
    print(f"Se han encontrado {total_jugadores} jugadores activos en total.")
    
    equipos = {t['id']: t['full_name'] for t in teams.get_teams()}
    lista_juego = []
    
    for index, p in enumerate(jugadores_activos): 
        try:
            player_id = p['id']
            full_name = p['full_name']
            
            print(f"[{index + 1}/{total_jugadores}] Procesando: {full_name}...")
            
            # 1. Información biográfica y física
            info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_dict()
            result_common = info['resultSets'][0]['rowSet'][0]
            headers_common = info['resultSets'][0]['headers']
            
            # Mapeo rápido de índices para evitar errores si la API cambia el orden
            idx = lambda campo: headers_common.index(campo)
            
            team_id = result_common[idx('TEAM_ID')]
            
            if not team_id or team_id not in equipos:
                print(f" -> Saltado (Sin equipo activo o Agente Libre)")
                continue
                
            # Extraer fecha de nacimiento y calcular edad real
            birthdate = result_common[idx('BIRTHDATE')]
            edad = calcular_edad(birthdate)
            
            # Nuevos campos biográficos y físicos
            altura = result_common[idx('HEIGHT')]
            peso = result_common[idx('WEIGHT')]
            pais = result_common[idx('COUNTRY')]
            dorsal = result_common[idx('JERSEY')]
            experiencia = result_common[idx('SEASON_EXP')]
            universidad = result_common[idx('LAST_AFFILIATION')]
            
            # Datos del Draft
            draft_year = result_common[idx('DRAFT_YEAR')]
            draft_round = result_common[idx('DRAFT_ROUND')]
            draft_number = result_common[idx('DRAFT_NUMBER')]
            
            time.sleep(1)
            
            # 2. Estadísticas de la Temporada Actual
            stats = playercareerstats.PlayerCareerStats(player_id=player_id).get_dict()
            filas_stats = stats['resultSets'][0]['rowSet']
            headers_stats = stats['resultSets'][0]['headers']
            
            idx_s = lambda campo: headers_stats.index(campo)
            
            if filas_stats:
                ultima_temporada = filas_stats[-1]
                partidos = ultima_temporada[idx_s('GP')]
                temporada_texto = ultima_temporada[idx_s('SEASON_ID')]
                
                if partidos > 0:
                    # Promedios básicos
                    puntos = round(ultima_temporada[idx_s('PTS')] / partidos, 1)
                    rebotes = round(ultima_temporada[idx_s('REB')] / partidos, 1)
                    asistencias = round(ultima_temporada[idx_s('AST')] / partidos, 1)
                    minutos = round(ultima_temporada[idx_s('MIN')] / partidos, 1)
                    
                    # Nuevos promedios añadidos (Defensa y control)
                    robos = round(ultima_temporada[idx_s('STL')] / partidos, 1)
                    tapones = round(ultima_temporada[idx_s('BLK')] / partidos, 1)
                    perdidas = round(ultima_temporada[idx_s('TOV')] / partidos, 1)
                    
                    # Porcentajes directos de la API (vienen en formato 0.450 -> 45.0%)
                    fg_pct = round(ultima_temporada[idx_s('FG_PCT')] * 100, 1) if ultima_temporada[idx_s('FG_PCT')] else 0.0
                    fg3_pct = round(ultima_temporada[idx_s('FG3_PCT')] * 100, 1) if ultima_temporada[idx_s('FG3_PCT')] else 0.0
                    ft_pct = round(ultima_temporada[idx_s('FT_PCT')] * 100, 1) if ultima_temporada[idx_s('FT_PCT')] else 0.0
                else:
                    puntos = rebotes = asistencias = minutos = robos = tapones = perdidas = 0.0
                    fg_pct = fg3_pct = ft_pct = 0.0
            else:
                temporada_texto = "N/A"
                partidos = 0
                puntos = rebotes = asistencias = minutos = robos = tapones = perdidas = 0.0
                fg_pct = fg3_pct = ft_pct = 0.0

            # Guardamos la súper estructura
            jugador_data = {
                "id": player_id,
                "nombre": full_name,
                "equipo": equipos[team_id],
                "posicion": result_common[idx('POSITION')],
                "dorsal": dorsal,
                "edad": edad,
                "pais": pais,
                "perfil_fisico": {
                    "altura": altura, # Formato "6-11"
                    "peso_lbs": peso
                },
                "historial": {
                    "universidad_origen": universidad,
                    "experiencia_anos": experiencia,
                    "draft": {
                        "anio": draft_year,
                        "ronda": draft_round,
                        "numero": draft_number
                    }
                },
                "partidos_jugados": partidos,
                "temporada": temporada_texto,
                "foto": f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png",
                "stats": {
                    "PTS": puntos,
                    "REB": rebotes,
                    "AST": asistencias,
                    "MIN": minutos,
                    "STL": robos,
                    "BLK": tapones,
                    "TOV": perdidas,
                    "FG_PCT": fg_pct,
                    "FG3_PCT": fg3_pct,
                    "FT_PCT": ft_pct
                }
            }
            
            lista_juego.append(jugador_data)
            time.sleep(1.5)
            
        except Exception as e:
            print(f" -> Error crítico con el jugador {p['full_name']}: {e}")
            time.sleep(5)
            continue

    print(f"\nGuardando {len(lista_juego)} jugadores en 'jugadores_nba.json'...")
    with open('jugadores_nba.json', 'w', encoding='utf-8') as f:
        json.dump(lista_juego, f, indent=4, ensure_ascii=False)
        
    print("¡Base de datos optimizada y actualizada con éxito!")

if __name__ == "__main__":
    obtener_datos_nba()