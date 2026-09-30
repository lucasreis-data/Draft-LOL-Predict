from fastapi import FastAPI, Body, Query, HTTPException
from draft import DraftRequest
import uvicorn 
import cblol
import modelos_cache

# RETIRAR
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# RETIRAR 2

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

def obter_modelo_sessao(liga: str):
    try:
        return modelos_cache.buscar_modelos(liga)
    except(ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code = 400, detail = str(error))

@app.get("/")
def home():
    return {"status": "Python API is running"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=5000, reload=False)

@app.get("/ligas")
def listar_ligas():
    response = cblol.listar_todas_ligas()
    return {"ligas": response}

@app.get("/ligas/disponiveis")
def listar_ligas_disponiveis():
    return {"ligas": sorted(modelos_cache.ligas_treinadas)}

@app.get("/times")
def listar_times(
    ligas: list[str] = Query(None),
    year: int = Query(None),
):
    if not ligas:
        ligas = ["CBLOL"]
        
    return cblol.obter_times_liga(ligas, year)

@app.get("/campeoes")
def listar_campeoes():
    return cblol.obter_campeoes()


@app.get("/stats/draft")
def bans_analise(
    nome: str = Query(...), 
    ano: int = Query(None),
    split : list[str] = Query(None),
    patch : list[str] = Query(None)
    ):

    resultado = cblol.analisar_estrategias(nome, ano, split, patch)

    if resultado is None:
        raise HTTPException(status_code = 404, detail = f"Time {nome} não encontrado")
    return resultado


@app.get("/stats/filtros")
def filtros_disponiveis(
    ligas : list[str] = Query(None),
    year : int = Query(None),
    split : list[str] = Query(None)
):
    tabela_splits = cblol.filtar_dados(ligas, year)

    if split:
        tabela_patchs = cblol.filtar_dados(ligas, year, split)
    else:
        tabela_patchs = cblol.filtar_dados(ligas, year)

    splits_unicos = sorted(tabela_splits["split"].dropna().unique().tolist())
    patchs_unicos = sorted(tabela_patchs["patch_num"].dropna().unique())

    patchs_validos = []

    for p in patchs_unicos:
        if p > 0:
            patchs_validos.append(int(p))

    patchs_validos = sorted(patchs_validos, reverse = True)

    return {
        "splits" : splits_unicos,
        "patches" : patchs_validos
    }


@app.get("/stats/matchups-confronto")
def matchups_confronto(
    aliados : list[str] = Query(...),
    inimigos : list[str] = Query(...),
):
    return cblol.avaliar_confrontos(aliados, inimigos)


@app.get("/stats/campeoes")
def lista_campeoes_stats(
    ligas : list[str] = Query(None),
    year : int = Query(None),
    posicao : str = Query(None),
    split : list[str] = Query(None),
    patch : list[str] = Query(None)
):
    tabela_liga = cblol.filtar_dados(ligas, year, split, patch)
    
    return cblol.ranking_meta(tabela_liga, posicao)


@app.get("/stats/campeao")
def campeao_scout(
    campeao : str = Query(...),
    ligas : list[str] = Query(None),
    year : int = Query(None),
    split : list[str] = Query(None),
    patch : list[str] = Query(None)
):
    tabela_dados = cblol.filtar_dados(ligas, year, split, patch)
    stats = cblol.estatistica_campeao(campeao, tabela_dados)
    scout = cblol.scout_campeao(campeao, tabela_dados)

    if stats is None or scout is None:
        raise HTTPException(status_code = 404, detail = f"Campeão {campeao} sem dados suficientes")

    scout["stats"] = stats
    scout["top_players"] = cblol.top_player_camp(campeao, tabela_dados)

    return scout

@app.post("/predict")
def predict(data: dict = Body(...)):
    time_a = data.get("timeA")
    time_b = data.get("timeB")
    jogos = data.get("quantidadeJogos")

    response = cblol.ordemPicksBans(time_a, time_b, jogos, [])

    return {"draft": response}

@app.post("/draft/sugestao")
def pedir_sugestao(req: DraftRequest):

    modelo = obter_modelo_sessao(req.liga)

    args = ( req.time_player, req.bans_player, req.picks_player, req.time_ia, req.bans_ia, req.picks_ia, req.fearless, req.is_first_pick)
    if req.fase.startswith("BAN"):
        champion = cblol.sugeriBans(*args, modelo = modelo)
    else:
        champion = cblol.sugeriPicks(*args, True, modelo = modelo)
    return{"champion": champion}

@app.post("/draft/acao")
def acao(req: DraftRequest):
    modelo = obter_modelo_sessao(req.liga)
    if req.jogador_atual == "IA":
        args = (req.time_ia, req.bans_ia, req.picks_ia,
            req.time_player, req.bans_player, req.picks_player,
            req.fearless, not req.is_first_pick)
    else:
        args = (req.time_player, req.bans_player, req.picks_player,
            req.time_ia, req.bans_ia, req.picks_ia,
            req.fearless, req.is_first_pick)
    if req.fase.startswith("BAN"):
        champion = cblol.sugeriBans(*args, modelo = modelo)
    else: 
        champion = cblol.sugeriPicks(*args, modelo = modelo)
    return{"champion": champion}
