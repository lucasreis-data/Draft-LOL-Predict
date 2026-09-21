import os
import joblib

pasta_modelos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelos_treinados")

ligas_treinadas = {"CBLOL", "LCK", "LPL", "LEC", "LCS", "LCP", "GERAL"}

_cache_modelos = {}

def buscar_modelos(liga : str = "GERAL"):
    liga = (liga or "GERAL").strip().upper()

    if liga not in ligas_treinadas:
        raise ValueError(f'Liga: "{liga}" não encontrada. Opções disponíveis: {ligas_treinadas}')

    if liga in _cache_modelos:
        return _cache_modelos[liga]

    caminho = os.path.join(pasta_modelos, f"modelo_{liga}.joblib")

    if not os.path.exists(caminho):
        raise FileNotFoundError(f'O modelo "{liga}" não foi encontrada em: {caminho}')

    print(f'Carregando "{liga}" no disco pela 1x...\n')

    modelo = joblib.load(caminho)
    _cache_modelos[liga] = modelo

    return modelo