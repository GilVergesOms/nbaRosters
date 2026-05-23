import json
import time
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo

def obtener_datos_nba():
    print("Iniciando la recolección completa de datos de la NBA...")
    
    # 1. Obtener todos los jugadores activos
    jugadores_activos = players.get_active_players()
    total_jugadores = len(jugadores_activos)
    print(f"Se han encontrado {total_jugadores} jugadores activos en total.")
    
    # Diccionario para mapear ID de equipo a Nombre Completo
    equipos = {t['id']: t['full_name'] for t in teams.get_teams()}
    
    lista_juego = []
    
    # Recorremos la lista completa
    for index, p in enumerate(jugadores_activos): 
        try:
            player_id = p['id']
            full_name = p['full_name']
            
            print(f"[{index + 1}/{total_jugadores}] Procesando: {full_name}...")
            
            # 1. Obtener info detallada (Equipo actual y Posición)
            info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_dict()
            result_common = info['resultSets'][0]['rowSet'][0]
            headers_common = info['resultSets'][0]['headers']
            
            team_id = result_common[headers_common.index('TEAM_ID')]
            posicion = result_common[headers_common.index('POSITION')]
            
            # Si no tiene equipo actual (agente libre), lo saltamos
            if not team_id or team_id not in equipos:
                print(f" -> Saltado (Sin equipo activo o Agente Libre)")
                continue
                
            nombre_equipo = equipos[team_id]
            
            # EXTRAER EDAD (Blindado para evitar errores de definición)
            edad = "N/A"
            try:
                # Buscamos de forma dinámica el campo 'AGE' en las cabeceras
                if 'AGE' in headers_common:
                    idx_edad = headers_common.index('AGE')
                    if result_common[idx_edad] is not None:
                        edad = int(result_common[idx_edad])
            except Exception:
                edad = "N/A" # Si falla la conversión o no existe, ponemos por defecto
            
            # Pequeña pausa entre peticiones al mismo jugador
            time.sleep(1)
            
            # 2. Obtener Estadísticas de la Temporada Actual
            stats = playercareerstats.PlayerCareerStats(player_id=player_id).get_dict()
            filas_stats = stats['resultSets'][0]['rowSet']
            headers_stats = stats['resultSets'][0]['headers']
            
            if filas_stats:
                ultima_temporada = filas_stats[-1]
                partidos = ultima_temporada[headers_stats.index('GP')]
                temporada_texto = ultima_temporada[headers_stats.index('SEASON_ID')]
                
                if partidos > 0:
                    puntos = round(ultima_temporada[headers_stats.index('PTS')] / partidos, 1)
                    rebotes = round(ultima_temporada[headers_stats.index('REB')] / partidos, 1)
                    asistencias = round(ultima_temporada[headers_stats.index('AST')] / partidos, 1)
                    minutos = round(ultima_temporada[headers_stats.index('MIN')] / partidos, 1)
                else:
                    puntos, rebotes, asistencias, minutos = 0, 0, 0, 0
            else:
                temporada_texto = "N/A"
                partidos, puntos, rebotes, asistencias, minutos = 0, 0, 0, 0

            # Guardamos la estructura en la lista
            jugador_data = {
                "id": player_id,
                "nombre": full_name,
                "equipo": nombre_equipo,
                "posicion": posicion,
                "edad": edad,
                "partidos_jugados": partidos,
                "temporada": temporada_texto,
                "foto": f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png",
                "stats": {
                    "PTS": puntos,
                    "REB": rebotes,
                    "AST": asistencias,
                    "MIN": minutos
                }
            }
            
            lista_juego.append(jugador_data)
            
            # Pausa de seguridad reglamentaria para la API
            time.sleep(1.5)
            
        except Exception as e:
            print(f" -> Error crítico con el jugador {p['full_name']}: {e}")
            print("Esperando 5 segundos antes de continuar...")
            time.sleep(5)
            continue

    # Guardar todo en el JSON final
    print(f"\nGuardando {len(lista_juego)} jugadores en 'jugadores_nba.json'...")
    with open('jugadores_nba.json', 'w', encoding='utf-8') as f:
        json.dump(lista_juego, f, indent=4, ensure_ascii=False)
        
    print("¡Base de datos completa actualizada con éxito!")

if __name__ == "__main__":
    obtener_datos_nba()