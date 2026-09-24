from fastapi import FastAPI, Body, Query, HTTPException
from draft import Fase, proxima_fase
import uvicorn 
import cblol
import uuid
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

sessions = {}

def obter_modelo_sessao(state):

    try:
        return modelos_cache.buscar_modelos(state.get("liga"))
    except(ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code = 400, detail = str(error))


# GET
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


@app.get("/acessar-sessao")
def acessar_jogo(sessionId: str = Query(...)):
    state = sessions[sessionId]
    return{
        "faseAtual": state["fase_atual"],
        "jogadorAtual": state["jogador_atual"],
        "bansPlayer": state["bans"]["player"],
        "bansIA": state["bans"]["ia"],
        "picksPlayer": state["picks"]["player"],
        "picksIA": state["picks"]["ia"],
        "fearless": state["fearless"]
    }


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

# POST

@app.post("/predict")
def predict(data: dict = Body(...)):
    time_a = data.get("timeA")
    time_b = data.get("timeB")
    jogos = data.get("quantidadeJogos")

    response = cblol.ordemPicksBans(time_a, time_b, jogos, [])

    return {"draft": response}


@app.post("/draft/iniciar")
def iniciar_draft(data: dict = Body(...)):
    session_id = str(uuid.uuid4())

    if data["isFirstPick"]:
        jogador_atual = "PLAYER"
    else:
        jogador_atual = "IA"

    sessions[session_id] = {
        "total_jogos": data["quantidadeJogos"],
        "is_first_pick": data["isFirstPick"],
        "time_user": data["timeUsuario"],
        "time_ia": data["timeIA"],
        "liga" : data.get("liga", "CBLOL"),
        "game_atual": 1,
        "fase_atual": Fase.BAN_1.value,
        "jogador_atual": jogador_atual,
        "bans": {"player": [], "ia": []},
        "picks": {"player": [], "ia": []},
        "fearless": []
    }
    return {"sessionId": session_id, "faseAtual": Fase.BAN_1.value, "jogadorAtual": jogador_atual}


@app.post("/draft/acao")
def acao_draft(data: dict = Body(...)):
    if data["sessionId"] not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    state = sessions[data["sessionId"]]
    modelo = obter_modelo_sessao(state)
    
    if data.get("champion"):
        champion = data["champion"]
        if champion in state["fearless"]:
            raise HTTPException(status_code=400, detail="champion ja escolhido")
            
        if champion in state["bans"]["player"]:
            raise HTTPException(status_code=400, detail="champion banido")    
            
        if champion in state["bans"]["ia"]:
            raise HTTPException(status_code=400, detail="champion banido")  

    is_ban = state["fase_atual"].startswith("BAN")

    if state["jogador_atual"] == "PLAYER":
        if data.get("champion"):
            champion = data["champion"]
            if is_ban:
                state["bans"]["player"].append(champion)
            else:
                state["picks"]["player"].append(champion)
                state["fearless"].append(champion)
        else:
            args = (
                 state["time_user"], state["bans"]["player"], state["picks"]["player"],state["time_ia"], state["bans"]["ia"], state["picks"]["ia"], state["fearless"], state["is_first_pick"]
                )
            if is_ban:
                champion = cblol.sugeriBans(*args, modelo = modelo)
                state["bans"]["player"].append(champion)
            else:
                champion = cblol.sugeriPicks(*args, modelo = modelo)
                state["picks"]["player"].append(champion)
                state["fearless"].append(champion)
    else:
        if data.get("champion"):
            champion = data["champion"]
        else:
            args = (
                state["time_ia"], state["bans"]["ia"], state["picks"]["ia"], state["time_user"], state["bans"]["player"], state["picks"]["player"], state["fearless"], not state["is_first_pick"]
                )
            if is_ban:
                champion = cblol.sugeriBans(*args, modelo = modelo)
            else:
                champion = cblol.sugeriPicks(*args, modelo = modelo)
        if is_ban:
            state["bans"]["ia"].append(champion)
        else:
            state["picks"]["ia"].append(champion)
            state["fearless"].append(champion)

    fase_atual = Fase(state["fase_atual"])
    proxima, jogador = proxima_fase(fase_atual, state["is_first_pick"])

    state["fase_atual"] = proxima.value
    state["jogador_atual"] = jogador
    tem_mais_jogos = True
    if state["game_atual"] == state["total_jogos"]:
        if proxima == Fase.FIM:
            tem_mais_jogos = False
    return{
        "sessionId": data["sessionId"],
        "faseAtual": state["fase_atual"],
        "jogadorAtual": state["jogador_atual"],
        "bansPlayer": state["bans"]["player"],
        "bansIA": state["bans"]["ia"],
        "picksPlayer": state["picks"]["player"],
        "picksIA": state["picks"]["ia"],
        "fearless": state["fearless"],
        "temMaisJogos": tem_mais_jogos
    }    


@app.post("/draft/novo-jogo")
def novo_jogo(data: dict = Body(...)):
    if data["sessionId"] not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    state = sessions[data["sessionId"]]

    if state["game_atual"]>= state["total_jogos"]:
        raise HTTPException(status_code=400, detail="Draft já finalizado")
    
    if not state["fase_atual"] == Fase.FIM.value:
        raise HTTPException(status_code=400, detail="Jogo não finalizado")
    
    if data["isFirstPick"]:
        jogador_atual = "PLAYER"
    else:
        jogador_atual = "IA"

    state["game_atual"] += 1
    state["is_first_pick"] = data["isFirstPick"]
    state["fase_atual"] = Fase.BAN_1.value
    state["jogador_atual"] = jogador_atual
    state["bans"] = {"player": [], "ia": []}
    state["picks"] = {"player": [], "ia": []}

    return{
        "faseAtual": state["fase_atual"],
        "gameAtual": state["game_atual"],
        "jogadorAtual": state["jogador_atual"]
    }


@app.get("/draft/sugestao")
def pedir_sugestao(sessionId: str = Query(...)):
    if sessionId not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    state = sessions[sessionId]
    modelo = obter_modelo_sessao(state)

    args = ( state["time_user"], state["bans"]["player"], state["picks"]["player"], state["time_ia"], state["bans"]["ia"], state["picks"]["ia"], state["fearless"], state["is_first_pick"])
    if state["fase_atual"].startswith("BAN") :
        champion = cblol.sugeriBans(*args, modelo = modelo)
    else:
        champion = cblol.sugeriPicks(*args, True, modelo = modelo)
    return{
        "champion": champion
    }


@app.get("/ligas/disponiveis")
def listar_ligas_treinadas():
    return {"ligas": sorted(modelos_cache.ligas_treinadas)}