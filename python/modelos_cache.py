import os
import threading
import joblib

pasta_modelos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelos_treinados")

ligas_treinadas = {"CBLOL", "LCK", "LPL", "LEC", "LCS", "LCP", "GERAL"}

_cache_modelos = {}
_trava = threading.Lock()

def _carregar_do_disco(liga : str):
    caminho = os.path.join(pasta_modelos, f"modelo_{liga}.joblib")

    if not os.path.exists(caminho):
        print(f'AVISO: arquivo do modelo "{liga}" não encontrado em: {caminho}', flush = True)
        raise FileNotFoundError(f'O modelo "{liga}" não está disponível.')

    print(f'Carregando "{liga}" do disco...', flush = True)

    return joblib.load(caminho)

def buscar_modelos(liga : str = "GERAL"):
    liga = (liga or "GERAL").strip().upper()

    if liga not in ligas_treinadas:
        raise ValueError(f'Liga: "{liga:[20]}" não encontrada. Opções disponíveis: {sorted(ligas_treinadas)}')

    modelo = _cache_modelos.get(liga)
    if modelo is not None:
        return modelo

    with _trava:
        modelo = _cache_modelos.get(liga)
        if modelo is None:
            modelo = _carregar_do_disco(liga)
            _cache_modelos[liga] = modelo

    return modelo

def pre_carregar():
    carregadas = []

    for liga in sorted(ligas_treinadas):
        try:
            buscar_modelos(liga)
            carregadas.append(liga)
        except FileNotFoundError:
            print(f'AVISO: modelo "{liga}" não encontrado; a liga ficará indisponível.', flush = True)

    if not carregadas:
        raise RuntimeError(f"Nenhum modelo encontrado em: {pasta_modelos}")

    return carregadas

def ligas_carregadas():
    return sorted(_cache_modelos)
