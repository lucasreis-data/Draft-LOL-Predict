# %% [markdown]
# <a href="https://colab.research.google.com/github/IGDeft/Cblol-Tigrinho/blob/main/CblolTigrinho.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# %%
import pandas as pd

tabela_2025 = pd.read_csv("2025_LoL_esports_match_data_from_OraclesElixir.csv")
tabela_2026 = pd.read_csv("2026_LoL_esports_match_data_from_OraclesElixir.csv")

tabela_2025["year"] = 2025
tabela_2026["year"] = 2026

tabela = pd.concat([tabela_2025, tabela_2026], ignore_index = True)

#display(tabela)

# %%
novos_nomes = {
    "LTA S": "CBLOL",
    "LTA N": "LCS"
}

tabela["league_unificada"] = tabela["league"].replace(novos_nomes)

print("Times 2025")
print(tabela['league'].unique())

print()
print(tabela.columns.tolist())
print()

print("Times 2026\n")
print(tabela_2026["league"].unique())


# %%
def obter_times_liga(lista_liga = "CBLOL", year = None):

  if lista_liga is None:
    return tabela['teamname'].unique()
  
  if isinstance(lista_liga, str):
    lista_liga = [lista_liga]
  
  todos_times = []

  for liga in lista_liga:
    filtro = tabela[tabela['league'] == liga]
    times_da_liga = filtro['teamname'].unique().tolist()
    todos_times.extend(times_da_liga)

  return sorted(list(set(todos_times)))


def obter_campeoes():
    campeoes = tabela['champion'].dropna().unique().tolist()
    return sorted(campeoes)


def obter_tabela_liga(lista_liga = None, year = None):
    
    df_ligas = tabela.copy()

    if year is not None:
        df_ligas = df_ligas[df_ligas["year"] == year]

    if lista_liga is not None:
        
        if isinstance(lista_liga, str):
            lista_liga = [lista_liga]
        df_ligas = df_ligas[df_ligas["league"].isin(lista_liga)]
        
    return df_ligas


def listar_todas_ligas():

  return sorted(tabela['league'].unique().tolist())

# %%
tabela_relev = [

    # Identificação Jogo

    'gameid', "split", "game", "patch", "date", "playoffs", "position",
    "result", "league", "year", "league_unificada",

    # Jogador/Time
    
    "playername", "teamname", "participantid", "playerid", "kills", "deaths",
    "assists", "teamkills", "teamdeaths", "earnedgoldshare", "damageshare",

    # Pick e Ban
    "ban1", "ban2", "ban3", "ban4", "ban5", "pick1", "pick2", "pick3", "pick4",
    'pick5', "firstPick", "champion", "side",

    # Objetivos

    "void_grubs", "towers", "turretplates", "dragons",

    # Ritmo de Jogo

    "firsttower", "firstblood", "firstdragon", "firstbaron", "firstherald",
    "gamelength", "csdiffat10", "xpdiffat10", "golddiffat10",
    "csdiffat15", "xpdiffat15", "golddiffat15",
    "team kpm", "ckpm", "cspm",
]

ligas_relev_2025 = ["LTA S", "LCK", "LPL", "LEC", "LTA N", "PCS", "VCS", "LJL", "LCP", "MSI", "EWC"]
ligas_relev_2026 = ["CBLOL", "LCK", "LPL", "LEC", "LCS", "VCS", "LJL", "LCP", "EWC"]
ligas_relev = list(set(ligas_relev_2025 + ligas_relev_2026))


tabela_filtrada = obter_tabela_liga(ligas_relev)
tabela_final = tabela_filtrada[tabela_relev].copy()

tabela_final["gamelength"] = pd.to_timedelta(tabela_final["gamelength"], unit = 's')
tabela_final["gamelength"] = (tabela_final["gamelength"] + pd.to_datetime("1970-01-01")).dt.strftime("%H:%M:%S")
tabela_final["teamname"] = tabela_final["teamname"].replace("Isurus Estral", "Isurus")


tabela_final["patch_num"] = ((tabela_final["patch"] * 100).round().fillna(0).astype(int))

#display(tabela_final)

# %%
def filtar_dados(liga = None, year = None):

    df_meta_liga = tabela_final.copy()

    if year is not None:
        df_meta_liga = df_meta_liga[df_meta_liga["year"] == year]
    
    if liga is not None:
        if isinstance(liga, str):
            liga = [liga]
        df_meta_liga = df_meta_liga[df_meta_liga["league_unificada"].isin(liga)]

    return df_meta_liga


print("Quantida de jogos por liga.")
jogos_por_liga = tabela_final.groupby("league")["gameid"].nunique()

print(jogos_por_liga.sort_values(ascending = False))

# %%
tabela_liga_ativa = filtar_dados(liga = "CBLOL", year = 2026)

def construir_df_meta(tabela_liga = None):

    if tabela_liga is None:
        tabela_liga = tabela_liga_ativa

    tabela_players_ativo = tabela_liga[tabela_liga["position"] != "team"]
    tabela_team_ativo = tabela_liga[tabela_liga["position"] == "team"]

    # Picks

    picks_liga = tabela_players_ativo["champion"].value_counts()
    print(picks_liga.head(40))

    # Bans

    bans_liga = pd.concat([
        tabela_team_ativo["ban1"],
        tabela_team_ativo['ban2'],
        tabela_team_ativo['ban3'],
        tabela_team_ativo['ban4'],
        tabela_team_ativo['ban5']
    ])

    print("-" * 20)
    print("\nBans\n")

    print(bans_liga.value_counts().head(20))

    total_jogos = tabela_team_ativo['gameid'].nunique()

    pick_rate = (picks_liga / total_jogos) * 100
    ban_rate = (bans_liga.value_counts()/ total_jogos) * 100

    print("-" * 20)
    print("\nPick Rate\n")
    print(pick_rate.head(20).round(2))

    print("-" * 20)
    print("\nBan Rate\n")
    print(ban_rate.head(20).round(2))

    df_meta_resultado = pd.DataFrame({
        "pick_rate" : pick_rate,
        "ban_rate" : ban_rate
    }).fillna(0)

    df_meta_resultado['presence'] = df_meta_resultado["pick_rate"] + df_meta_resultado["ban_rate"]
    df_meta_resultado = df_meta_resultado.sort_values(by = "presence", ascending = False)

    print("\n", df_meta_resultado.head(50).round(2))

    return df_meta_resultado


df_meta = construir_df_meta(tabela_liga_ativa)

# %%
def analisar_estrategias(nome_time, ano_analise = None):
    
    df_filtro = tabela_final[(tabela_final["teamname"] == nome_time) & (tabela_final["position"] == "team") & (tabela_final["year"] == ano_analise)]

    if df_filtro.empty:
        print(f"Time {nome_time} não encontrado para o ano de {ano_analise}")
        return None
    
    ids_todos = df_filtro["gameid"].unique()
    ids_fp = df_filtro[df_filtro["firstPick"] == 1]["gameid"].unique()
    ids_lp = df_filtro[df_filtro["firstPick"] == 0]["gameid"].unique()

    df_players_geral = tabela_final[(tabela_final["teamname"] == nome_time) & (tabela_final["year"] == ano_analise) & (tabela_final["position"] != "team")]
    df_players_fp = df_players_geral[df_players_geral["gameid"].isin(ids_fp)]
    df_players_lp = df_players_geral[df_players_geral["gameid"].isin(ids_lp)]

    df_adv_geral = tabela_final[(tabela_final["gameid"].isin(ids_todos) & (tabela_final["teamname"] != nome_time) & (tabela_final["position"] == "team"))]
    df_adv_fp = tabela_final[(tabela_final["gameid"].isin(ids_fp) & (tabela_final["teamname"] != nome_time) & (tabela_final["position"] == "team"))]
    df_adv_lp = tabela_final[(tabela_final["gameid"].isin(ids_lp) & (tabela_final["teamname"] != nome_time) & (tabela_final["position"] == "team"))]

    def processar_first_pick(df_contexto):

        df_fp = df_contexto[df_contexto["firstPick"] == 1]
        total_jogos_fp = len(df_fp)

        stats = df_fp["pick1"].value_counts()

        df_resumo_fp = pd.DataFrame({
            "champion": stats.index,
            "picks": stats.values,
            "pick_rate": (stats.values / total_jogos_fp * 100).round(1)
        }) 

        return df_resumo_fp.head(10).to_dict(orient = "records")


    def processar_picks(df_contexto):

        total_jogos = df_contexto["gameid"].nunique()

        if total_jogos == 0:
            return []
        
        stats = df_contexto.groupby("champion").agg(picks = ("champion", "count"), vitorias = ("result", "sum"))

        stats["pick_rate"] = (stats["picks"] / total_jogos * 100).round(1)
        stats["win_rate"] = (stats["vitorias"] / stats["picks"] * 100).round(1)
        stats.index.name = "champion"
        stats = stats.sort_values("picks", ascending = False).head(10)

        return stats.reset_index().to_dict(orient = "records")

    
    def processar_bans_fase1(df_contexto):

        total_jogos = len(df_contexto)

        if total_jogos == 0:
            return []
        
        bans_f1 = pd.concat([df_contexto["ban1"], df_contexto["ban2"], df_contexto["ban3"]]).value_counts()

        df_bans_fase1 = pd.DataFrame({
            "champion": bans_f1.index,
            "qtd": bans_f1.values,
            "rate": (bans_f1.values / total_jogos * 100).round(1)
        }).fillna(0)
        
        return df_bans_fase1.head(10).to_dict(orient = "records")


    def processar_bans_totais(df_contexto):

        total_jogos = len(df_contexto)

        if total_jogos == 0:
            return []

        cols_bans = [f"ban{i}" for i in range(1, 6)]
        bans_totais = pd.concat([df_contexto[col] for col in cols_bans]).value_counts()

        df_bans_totais = pd.DataFrame({
            "champion": bans_totais.index,
            "bans_totais": bans_totais.values,
            "rate": (bans_totais.values / total_jogos * 100).round(1)
        }).fillna(0)

        return df_bans_totais.sort_values("bans_totais", ascending=False).head(10).to_dict(orient="records")


    def montar_bloco(df_picks, df_filtro, df_adv, titulo, jogos):

        return {
            "titulo": titulo,
            "jogos": int(jogos),  
            "prioridade_fp": processar_first_pick(df_filtro),
            "picks": processar_picks(df_picks), 
            "bans_f1": processar_bans_fase1(df_filtro),
            "seus_bans": processar_bans_totais(df_filtro),
            "bans_adv_f1":processar_bans_fase1(df_adv),
            "bans_contra": processar_bans_totais(df_adv), 
        }
    

    def pick_jogador():

        if df_players_geral.empty:
            return {}
        
        last_game = df_filtro.sort_values("date", ascending = False)["gameid"].iloc[0]
        df_last_game = df_players_geral[df_players_geral["gameid"] == last_game]
        lineup_atual = df_last_game.set_index("position")["playername"].to_dict()

        resultado = {}

        for pos in ["top", "jng", "mid", "bot", "sup"]:
            df_pos = df_players_geral[df_players_geral["position"] == pos]
            
            if df_pos.empty:
                continue
            
            titular = lineup_atual.get(pos)
            players = []

            for player in df_pos["playername"].unique():

                df_player = df_pos[df_pos["playername"] == player]
                total =  df_player["gameid"].nunique()

                stats = df_player.groupby("champion").agg(
                    picks = ("champion", "count"),
                    vitorias = ("result", "sum")
                )

                stats["pick_rate"] = (stats["picks"] / total * 100).round(1)
                stats["win_rate"] = (stats["vitorias"] / stats["picks"] * 100).round(1)

                stats = stats.sort_values("picks", ascending = False).head(10)
                stats.index.name = "champion"
                
                players.append({
                    "player": player,
                    "jogos": int(total),
                    "titular": player == titular,
                    "picks": stats.reset_index().to_dict(orient = "records")
                })
            
            players.sort(key = lambda x: x["titular"], reverse = True)
            resultado[pos] = players

        return resultado


    return {
        "time": nome_time,
        "ano": ano_analise,
        "picks_jogador": pick_jogador(),
        "geral": montar_bloco(df_players_geral, df_filtro, df_adv_geral, "Geral", len(ids_todos)),
        "fp": montar_bloco(df_players_fp,df_filtro[df_filtro["firstPick"] == 1], df_adv_fp, "First Pick", len(ids_fp)),
        "lp": montar_bloco(df_players_lp, df_filtro[df_filtro["firstPick"] == 0], df_adv_lp, "Last Pick", len(ids_lp))
    }

# %%
def analisar_time_adv(nome_time, ano_analise = None):
    
    df_time = tabela_final[
        (tabela_final["teamname"] == nome_time) & (tabela_final["year"] == ano_analise) & (tabela_final["position"] == "team")
        ]

    if df_time.empty:

        print(f"Dados não encontrados para {nome_time} em {ano_analise}")
        return None
    
    ids_jogos = df_time["gameid"].unique()
    total_jogos = len(ids_jogos)

    df_adv = tabela_final[
        (tabela_final["gameid"].isin(ids_jogos)) & (tabela_final["teamname"] != nome_time) & (tabela_final["position"] == "team")
    ]

    bans_adv = pd.concat([df_adv[f"ban{i}"] for i in range(1, 6)]).value_counts()
    taxa_ban_adv = (bans_adv / total_jogos * 100).round(1)

    picks_reais = tabela_final[
        (tabela_final["teamname"] == nome_time) & (tabela_final["position"] != "team")
    ]["champion"].value_counts()

    taxa_pick = (picks_reais / total_jogos * 100).round(1)

    df_ameaca = pd.DataFrame({
        "%_Ban_Adv": taxa_ban_adv,
        "%_Pick_Real": taxa_pick
    }).fillna(0)

    df_ameaca["ameaca_oculta"] = df_ameaca["%_Ban_Adv"] - df_ameaca["%_Pick_Real"]

    return df_ameaca.sort_values("ameaca_oculta", ascending = False)


# %%
import numpy as np

tabela_final["patch_rank"] = tabela_final["patch_num"].rank(method = "dense")
patch_max = tabela_final["patch_rank"].max()

tabela_final["patch_peso"] = np.exp(- 0.05 * (patch_max - tabela_final["patch_rank"]))

# %%
def treinar_modelo(liga_ativa):
    
    from sklearn.ensemble import RandomForestClassifier

    peso_liga = tabela_ia["league_unificada"].map(pesos_base_liga).fillna(0.5)

    if liga_ativa is not None:
        filtro_liga = tabela_ia["league_unificada"] == liga_ativa
        peso_liga.loc[filtro_liga] *= bonus_liga_ativa

    peso_final = peso_liga * tabela_ia["patch_peso"]

    modelo = RandomForestClassifier(
        n_estimators = 150,
        min_samples_leaf = 12,
        max_depth = 20,
        max_leaf_nodes = 3000,
        random_state = 42
    )

    modelo.fit(X, y, sample_weight = peso_final.values)

    return modelo

# %%
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

liga_ativa = "CBLOL"

# Pesos

pesos_base_liga = {
    "LCK": 1.4, "LPL": 1.4, "LEC": 1.3, "CBLOL": 1.0, 
    "LCS": 1.0, "PCS": 0.9, "VCS": 0.9, "LJL": 0.9, 
    "LCP": 0.9, "MSI": 1.5, "EWC": 1.5,
}

bonus_liga_ativa = 2.5

tabela_final["peso_liga"] = tabela_final["league_unificada"].map(pesos_base_liga).fillna(0.5)

if liga_ativa is not None:
    tabela_final.loc[tabela_final["league_unificada"] == liga_ativa, "peso_liga"] *= bonus_liga_ativa

tabela_final["peso_final"] = tabela_final["peso_liga"] * tabela_final["patch_peso"]

tabela_ml_completa = tabela_final.copy()
tabela_ml = tabela_final[tabela_final["position"] != "team"].copy()

# Codificadores

cod_time = LabelEncoder()
cod_pos = LabelEncoder()
cod_camp = LabelEncoder()

todos_os_times = list(tabela_ml["teamname"].unique()) + ["Desconhecidos"]
todos_campeoes = pd.concat([tabela_ml["champion"], tabela_ml_completa[tabela_ml_completa["position"] == "team"][["ban1", "ban2", "ban3", "ban4", "ban5"]].melt()["value"]]).dropna().unique()

cod_time.fit(todos_os_times)
cod_camp.fit(todos_campeoes)

tabela_ml["teamname_num"] = cod_time.transform(tabela_ml["teamname"])
tabela_ml["position_num"] = cod_pos.fit_transform(tabela_ml["position"])
tabela_ml["champion_num"] = cod_camp.transform(tabela_ml["champion"])

# Mapeamento dos Times

def extrair_parceiros(row):
    lista = row["champion_num_list"]
    atual = row["champion_num"]
    teammates = sorted([champ for champ in lista if champ != atual])

    while len(teammates) < 4:
        teammates.append(-1)

    return pd.Series(teammates[:4])


def mapear_oponentes(df):
    resumo = df.groupby(["gameid", "teamname"])["champion_num"].apply(list).reset_index()
    resumo.columns = ["gameid", "teamname", "champ_list"]

    merged = resumo.merge(resumo, on = "gameid", suffixes = ("", "_adv"))
    merged = merged[merged["teamname"] != merged["teamname_adv"]]

    def preenchido(lst):
        lst = list(lst)
        while len (lst) < 5:
            lst.append(-1)
        return lst[:5]
    
    op_cols = pd.DataFrame(merged["champ_list_adv"].apply(preenchido).tolist(), index = merged.index)
    op_cols.columns = ["o1", "o2", "o3", "o4", "o5"]

    return pd.concat([merged[["gameid", "teamname"]], op_cols], axis = 1)

# Tabela IA

df_aliado = tabela_ml.groupby(["gameid", "teamname"])["champion_num"].apply(list).reset_index()
tabela_ia = pd.merge(tabela_ml, df_aliado, on = ["gameid", "teamname"], how = "left", suffixes = ("", "_list"))

tabela_ia[["p1", "p2", "p3", "p4"]] = tabela_ia.apply(extrair_parceiros, axis = 1)

df_inimigos = mapear_oponentes(tabela_ml)
tabela_ia = pd.merge(tabela_ia, df_inimigos, on = ["gameid", "teamname"], how = "left")

# Oponentes

tabela_times = tabela_ml_completa[tabela_ml_completa["position"] == "team"].copy()
tabela_times = tabela_times.drop_duplicates(subset = ["gameid", "teamname"])

df_confronto_ia = tabela_times.merge(tabela_times, on = "gameid", suffixes = ("_time", "_oponente"))
df_confronto_ia = df_confronto_ia[df_confronto_ia["teamname_time"] != df_confronto_ia["teamname_oponente"]]

df_relacao_oponente = df_confronto_ia[["gameid", "teamname_time", "teamname_oponente"]].rename(
    columns = {"teamname_time" : "teamname", "teamname_oponente" : "oponente"}
)

tabela_ia = pd.merge(tabela_ia, df_relacao_oponente, on = ["gameid", "teamname"], how = "left")
tabela_ia["oponente"] = tabela_ia["oponente"].fillna("Desconhecidos").astype(str)
tabela_ia["oponente_num"] = cod_time.transform(tabela_ia["oponente"])

tabela_ia = pd.merge(tabela_ia, df_meta, left_on = "champion", right_index = True, how = "left").fillna(0)

# Ordem Picks

mapa_posicao = {
    (1, 1) : 0, (1, 2) : 3, (1, 3): 4, (1, 4) : 7, (1, 5) : 8, # FP
    (0, 1) : 1, (0, 2) : 2, (0, 3) : 5, (0, 4) : 6, (0, 5) : 9 # LP
}

def reconstruir_ordem(tabela_times):
    colunas = ["gameid", "firstPick", "pick1", "pick2", "pick3", "pick4", "pick5"]

    long = tabela_times[colunas].melt(
        id_vars = ["gameid", "firstPick"],
        value_vars = ["pick1", "pick2", "pick3", "pick4", "pick5"],
        var_name = "pick_slot",
        value_name = "champion"
    ).dropna(subset = ["champion", "firstPick"])

    long["pick_slot"] = long["pick_slot"].str.replace("pick", "").astype(int)
    long["firstPick"] = long["firstPick"].astype(int)
    long["chave"] = list(zip(long["firstPick"], long["pick_slot"]))
    long["ordem_pick"] = long["chave"].map(mapa_posicao)

    return long[["gameid", "champion", "ordem_pick"]]


ordem_real = reconstruir_ordem(tabela_times)

# Validacões

linha_antes_picks = len(tabela_ia)
tabela_ia = tabela_ia.merge(ordem_real, on = ["gameid", "champion"], how = "left", indicator = True)
picks_nao_reconciliados = (tabela_ia["_merge"] == "left_only").sum()
taxa_perda_picks = picks_nao_reconciliados / linha_antes_picks

print(f"\nLinhas sem ordem de pick recostruida: {picks_nao_reconciliados} de {linha_antes_picks} ({taxa_perda_picks:.2f})")

if taxa_perda_picks > 0.02:
    raise ValueError(f"Taxa de perda no merge da ordem real ({taxa_perda_picks}) -> Aceitavel (0.02)")

tabela_ia = tabela_ia[tabela_ia["_merge"] == "both"].drop(columns = ["_merge"])
tabela_ia["ordem_pick"] = tabela_ia["ordem_pick"].astype(int)
tabela_ia["peso_final"] = tabela_ia["peso_final"].fillna(1.0)

ordem_picks = tabela_ia.set_index(["gameid", "champion_num"])["ordem_pick"].to_dict()

def oculto(linha):

    atual = linha["ordem_pick"]
    gameid = linha["gameid"]

    for p in ["p1", "p2", "p3", "p4"]:

        champ_num = linha[p]

        if champ_num != -1:
            ordem = ordem_picks.get((gameid, champ_num), 99)

            if ordem >= atual:
                linha[p] = -1
    
    for o in ["o1", "o2", "o3", "o4", "o5"]:

        champ_num = linha[o]

        if champ_num != -1:
            ordem = ordem_picks.get((gameid, champ_num), 99)
        
            if ordem >= atual:
                linha[o] = -1

    return linha

 
tabela_ia = tabela_ia.apply(oculto, axis = 1)

# Ordem Bans

mapa_ban = {
    (1, 1) : 0, (1, 2) : 2, (1, 3) : 4, (1, 4) : 7, (1, 5) : 9, # FP
    (0, 1): 1, (0, 2): 3, (0, 3) : 5, (0, 4) : 6, (0, 5) : 8 # LP
}

def reconstruir_ordem_ban(tabela_times):
    colunas = ["gameid", "firstPick", "ban1", "ban2", "ban3", "ban4", "ban5"]

    long = tabela_times[colunas].melt(
        id_vars = ["gameid", "firstPick"],
        value_vars = ["ban1", "ban2", "ban3", "ban4", "ban5"],
        var_name = "ban_slot",
        value_name = "champion"
    ).dropna(subset = ["champion", "firstPick"])

    long["ban_slot"] = long["ban_slot"].str.replace("ban", "").astype(int)
    long["firstPick"] = long["firstPick"].astype(int)
    long["chave"] = list(zip(long["firstPick"], long["ban_slot"]))
    long["ordem_ban"] = long["chave"].map(mapa_ban)

    return long[["gameid", "champion", "ordem_ban"]]


df_ordem_bans = reconstruir_ordem_ban(tabela_times)

# Validações

contagem_bans = df_ordem_bans.groupby("gameid").size()
n_jogos_10_bans = (contagem_bans == 10).sum()
n_jogos_incompletos = (contagem_bans != 10).sum()

print(f"Jogos com 10 bans completos: ({n_jogos_10_bans}) | Jogos com bans incompletos: {n_jogos_incompletos}") 

gameids_bans_completos = contagem_bans[contagem_bans == 10].index
df_ordem_bans = df_ordem_bans[df_ordem_bans["gameid"].isin(gameids_bans_completos)]

duplicados = df_ordem_bans.duplicated(subset = ["gameid", "ordem_ban"]).sum()

if duplicados > 0:
    raise ValueError(f"Duplicidade(s) encontrada(s) gameid + ordem_bans {duplicados}")
print(f"Duplicados: {duplicados}")

campeoes_desconhecidos = set(df_ordem_bans["champion"]) - set(cod_camp.classes_)

if campeoes_desconhecidos:
    raise ValueError(f"Não foi encontrado todos os campeões. Os personagens não encontrados fora ({campeoes_desconhecidos})")
print(f"Campeões não conhecidos: {len(campeoes_desconhecidos)}")

# Bans

df_ordem_bans["champion_num"] = cod_camp.transform(df_ordem_bans["champion"])

pivot_bans = df_ordem_bans.pivot(index = "gameid", columns = "ordem_ban", values = "champion_num")
pivot_bans.columns = ([f"b{c + 1}" for c in pivot_bans.columns])
pivot_bans = pivot_bans.reindex(columns = [f"b{i}" for i in range(1, 11)])
pivot_bans = pivot_bans.reset_index()

# Validações

linha_antes_bans = len(tabela_ia)
tabela_ia = tabela_ia.merge(pivot_bans, on = "gameid", how = "left", indicator = "_merge_bans")
bans_nao_reconciliados = (tabela_ia["_merge_bans"] == "left_only").sum()
taxa_perda_bans = bans_nao_reconciliados / linha_antes_bans

print(f"Linhas de bans não reconstruidas {bans_nao_reconciliados} de {linha_antes_bans} ({taxa_perda_bans:.2f}%)")

if taxa_perda_bans > 0.02:
    raise ValueError(f"Taxa de perda de {taxa_perda_bans} superior ao limita (0.02)")

tabela_ia = tabela_ia[tabela_ia["_merge_bans"] == "both"].drop(columns = ["_merge_bans"])

for i in range(1, 11):
    tabela_ia[f"b{i}"] = tabela_ia[f"b{i}"].astype(int)

visibilidade_bans = np.where(tabela_ia["ordem_pick"] < 6, 6, 10)

for i in range(1, 11):
    ordem_colunas_bans = i - 1
    tabela_ia[f"b{i}"] = np.where(ordem_colunas_bans < visibilidade_bans, tabela_ia[f"b{i}"], -1)

def audita_visibilidade_bans(df_ia, limiar):
    total_vazamentos = 0

    for i in range(1, 11):
        ordem_colunas_bans = i -1
        mascara_vazamento = (df_ia[f"b{i}"] != -1) & (ordem_colunas_bans >= limiar)
        n = mascara_vazamento.sum()

        if n > 0:
            print(f"Vazamento em b{i}: {n} casos")
            total_vazamentos += n

    if total_vazamentos > 0:
        raise ValueError(f"Foram encontrados {total_vazamentos} vazamentos nos bans.")
    
    print(f"Total de vazamentos encontrado nos bans: {total_vazamentos}")


audita_visibilidade_bans(tabela_ia, visibilidade_bans)

print("\nConferencia na ordem na ordem de pick/ban: ")

colunas_ban = [f"b{i}" for i in range(1, 11)]

print(tabela_ia[["gameid", "ordem_pick"] + colunas_ban].sample(10, random_state = 1).sort_values(["gameid", "ordem_pick"]))

# Treino IA

colunas_treino = [
    "teamname_num", "oponente_num", "position_num", "firstPick",
    "ordem_pick", "patch_num",
    "p1", "p2", "p3", "p4",
    "o1", "o2", "o3", "o4", "o5",
    "b1", "b2", "b3", "b4", "b5",
    "b6", "b7", "b8", "b9", "b10"
]

X = tabela_ia[colunas_treino]
y = tabela_ia["champion_num"]

# modelo_ia = RandomForestClassifier(
#     n_estimators = 150,
#     min_samples_leaf = 12,
#     max_depth = 20,
#     max_leaf_nodes = 3000,
#     random_state = 42
# )

# modelo_ia.fit(X, y, sample_weight = tabela_ia["peso_final"].values)

# print(f"IA treinada com sucesso! Liga ativa {liga_ativa} | Linhas de treino: {len(tabela_ia)}")

# %%
import os
import joblib

try:
    pasta_raiz = os.path.dirname(os.path.abspath(__file__))
except NameError:
    pasta_raiz = os.getcwd()

caminho_encoders = os.path.join(pasta_raiz, "modelos_treinados", "encoders.joblib")

if os.path.exists(caminho_encoders):
    encoders_salvo = joblib.load(caminho_encoders)

    classes_atuais = set(cod_camp.classes_)
    classes_salvas = set(encoders_salvo["cod_camp"].classes_)

    if classes_atuais != classes_salvas:
        print(f'\n\033[33mAVISO: Os campeões do CSV mudaram! Rode o "treino_ia.py" novamente para atualizar os modelos.\033[m')
        print("Diferença encontrada: ", classes_atuais.symmetric_difference(classes_salvas))

# %%
def calcular_decaimento(meia_vida_dias = 45):

    return np.log(2) / meia_vida_dias


def calcular_peso_tempo(df, colunas_time, taxa_decaimento):

    df = df.copy()

    df["ultima_data"] = df.groupby(colunas_time)["date"].transform("max")

    dias_passados = (df["ultima_data"] - df["date"]).dt.days
    df["peso_tempo"] = np.exp(- taxa_decaimento * dias_passados)

    return df


def confronto_valido(tabela_liga_ativa):

    df_times = tabela_liga_ativa[tabela_liga_ativa["position"] == "team"].copy()

    times_por_jogo = df_times.groupby("gameid")["teamname"].transform("nunique")
    jogos_validos = df_times[times_por_jogo == 2]

    confronto = jogos_validos.merge(jogos_validos, on = "gameid", suffixes = ("", "_adv"))
    confronto = confronto[confronto["teamname"] != confronto["teamname_adv"]]

    return confronto


def mapear_oponentes(tabela):

    confronto = confronto_valido(tabela)

    return confronto[["gameid", "teamname", "teamname_adv"]]


def ordernar_times_alfa(tabela):

    tabela = tabela.copy()

    primeiro_time_alfa = np.where(tabela["teamname"] < tabela["teamname_adv"], tabela["teamname"], tabela["teamname_adv"])
    segundo_time_alfa = np.where(tabela["teamname"] < tabela["teamname_adv"], tabela["teamname_adv"], tabela["teamname"])

    tabela["partida"] = primeiro_time_alfa + "|" + segundo_time_alfa

    return tabela


def processar_picks(tabela_liga_ativa, meia_vida_dias = 45):

    decaimento = calcular_decaimento(meia_vida_dias)

    jogadores = tabela_liga_ativa[tabela_liga_ativa["position"] != "team"].copy()
    jogadores["date"] = pd.to_datetime(jogadores["date"])

    jogadores_peso = calcular_peso_tempo(jogadores, "teamname", decaimento)

    peso_champ = jogadores_peso.groupby(["teamname", "champion"])["peso_tempo"].sum()
    peso_total_jogos = jogadores_peso.groupby("teamname")["peso_tempo"].sum()

    prioridade_historica = peso_champ.div(peso_total_jogos, level = "teamname")
    prioridade_historica = prioridade_historica.unstack(fill_value = 0).round(4)

    # Prioridade FP

    confronto = confronto_valido(tabela_liga_ativa)
    confronto_fp = confronto[confronto["firstPick"] == 1].copy() 

    confronto_fp["date"] = pd.to_datetime(confronto_fp["date"])

    confronto_fp = calcular_peso_tempo(confronto_fp, "teamname", decaimento)

    peso_champ_fp = confronto_fp.groupby(["teamname", "pick1"])["peso_tempo"].sum()
    peso_fp_time = confronto_fp.groupby("teamname")["peso_tempo"].sum()

    prioridade_p1 = peso_champ_fp.div(peso_fp_time, level = "teamname")
    prioridade_p1 = prioridade_p1.unstack(fill_value = 0).round(4)

    # Confronto direto

    mapa_adv = mapear_oponentes(tabela_liga_ativa)

    jogos_confronto = jogadores.merge(mapa_adv, on = ["gameid", "teamname"], how = "inner")
    jogos_confronto = ordernar_times_alfa(jogos_confronto)
    jogos_confronto = calcular_peso_tempo(jogos_confronto, "partida", decaimento)

    campeao_peso = jogos_confronto.groupby(["teamname", "teamname_adv", "champion"])["peso_tempo"].sum()
    confronto_total = jogos_confronto.groupby(["teamname", "teamname_adv"])["peso_tempo"].sum()

    jogos_contra_adv = confronto_total.to_dict()

    picks_confronto = {}
    taxa_camp = (campeao_peso / confronto_total).round(4)

    for (time, adv, champ), taxa in taxa_camp.items():
        duelo = (time, adv)

        if duelo not in picks_confronto:
            picks_confronto[duelo] = {}

        picks_confronto[duelo][champ] = taxa

    jogos_confronto_fp = ordernar_times_alfa(confronto_fp)
    jogos_confronto_fp = calcular_peso_tempo(jogos_confronto_fp, "partida", decaimento)

    campeao_fp_peso = jogos_confronto_fp.groupby(["teamname", "teamname_adv", "pick1"])["peso_tempo"].sum()
    tot_fp_confronto =  jogos_confronto_fp.groupby(["teamname", "teamname_adv"])["peso_tempo"].sum()

    total_fp_confronto = tot_fp_confronto.to_dict()

    picks_fp_confronto = {}
    taxa_camp_fp = (campeao_fp_peso / tot_fp_confronto).round(4)

    for (nome_time, nome_adv, champ), taxa in taxa_camp_fp.items():
        times = (nome_time, nome_adv)

        if times not in picks_fp_confronto:
            picks_fp_confronto[times] = {}

        picks_fp_confronto[times][champ] = taxa

    return {
        "prioridade_historica" : prioridade_historica,
        "prioridade_p1" : prioridade_p1,
        "jogos_contra_adv" : jogos_contra_adv,
        "picks_confronto" : picks_confronto,
        "total_fp_confronto" : total_fp_confronto,
        "picks_fp_confronto" : picks_fp_confronto
    }


# Prioridade bans_Fase1

def _contagem_bans_peso(df, alvo_cols, grupo_cols):

    if df.empty:
        return pd.Series(dtype = int)
    
    bans = df.melt(
        id_vars = grupo_cols + ["peso_tempo", "gameid"],
        value_vars = alvo_cols,
        value_name = "campeao_banido"
    ).dropna(subset = ["campeao_banido"])

    if bans.empty:
        return pd.Series(dtype = int)

    bans_time = grupo_cols + ["campeao_banido"]
    bans_peso = bans.groupby(bans_time)["peso_tempo"].sum()

    return bans_peso


def identificar_first_pick(bans_agrupados, valor_fp):

    if bans_agrupados.empty:
        return {}

    status_fp = bans_agrupados.index.get_level_values("firstPick")

    if valor_fp not in status_fp:
        return {}

    return bans_agrupados.xs(valor_fp, level = "firstPick").to_dict()


def processar_bans(tabela_liga_ativa, meia_vida_dias = 45):

    decaimento = calcular_decaimento(meia_vida_dias)

    jogos_time = confronto_valido(tabela_liga_ativa)
    jogos_time["date"] = pd.to_datetime(jogos_time["date"])
    jogos_time = calcular_peso_tempo(jogos_time, "teamname", decaimento)

    status_fp = ["teamname", "firstPick"]

    peso_por_grupo = jogos_time.groupby(status_fp)["peso_tempo"].sum()
    total_fp = identificar_first_pick(peso_por_grupo, 1)
    total_lp = identificar_first_pick(peso_por_grupo, 0)

    bans_time = _contagem_bans_peso(jogos_time, ["ban1", "ban2", "ban3"], status_fp)

    ban_fase1_fp = identificar_first_pick(bans_time, 1)
    ban_fase1_lp = identificar_first_pick(bans_time, 0)

    bans_adv = _contagem_bans_peso(jogos_time, ["ban1_adv", "ban2_adv", "ban3_adv", "ban4_adv", "ban5_adv"], status_fp)

    ban_contra_fp = identificar_first_pick(bans_adv, 1)
    ban_contra_lp = identificar_first_pick(bans_adv, 0)

    confronto = confronto_valido(tabela_liga_ativa)
    confronto_adv = ordernar_times_alfa(confronto)
    confronto_adv["date"] = pd.to_datetime(confronto_adv["date"])
    confronto_adv = calcular_peso_tempo(confronto_adv, "partida", decaimento)

    status_fp_jogo = ["teamname", "teamname_adv", "firstPick"]

    bans_confronto = _contagem_bans_peso(confronto_adv, ["ban1", "ban2", "ban3", "ban4", "ban5"], status_fp_jogo)
    peso_confronto = confronto_adv.groupby(status_fp_jogo)["peso_tempo"].sum()

    bans_vs_fp = {}
    bans_vs_lp = {}

    taxa_ban_vs = (bans_confronto / peso_confronto).round(4) 

    for (time, adv, fp_status, champ), taxa in taxa_ban_vs.items():
        duelo = (time, adv)

        if fp_status == 1:
            lado = bans_vs_fp
        else:
            lado = bans_vs_lp

        if duelo not in lado:
            lado[duelo] = {}

        lado[duelo][champ] = taxa

    jogos_vs_fp = {}
    jogos_vs_lp = {}

    for (nome_time, nome_adv, fp_status), jogos in peso_confronto.items():
        times = (nome_time, nome_adv)

        if fp_status == 1:
            lado_vs = jogos_vs_fp
        else:
            lado_vs = jogos_vs_lp

        lado_vs[times] = jogos

    return {
        "ban_fase1_fp" : ban_fase1_fp,
        "ban_fase1_lp" : ban_fase1_lp,
        "total_fp" : total_fp,
        "total_lp" : total_lp,
        "ban_contra_fp" : ban_contra_fp,
        "ban_contra_lp" : ban_contra_lp,
        "total_contra_fp" : dict(total_fp),
        "total_contra_lp" : dict(total_lp),
        "bans_vs_fp" : bans_vs_fp,
        "bans_vs_lp" : bans_vs_lp,
        "jogos_vs_fp": jogos_vs_fp,
        "jogos_vs_lp" : jogos_vs_lp
    }

picks_stats = processar_picks(tabela_liga_ativa)

prioridade_historica = picks_stats["prioridade_historica"]
prioridade_p1 = picks_stats["prioridade_p1"]
jogos_contra_adv = picks_stats["jogos_contra_adv"]
picks_confronto = picks_stats["picks_confronto"]
total_fp_confronto = picks_stats["total_fp_confronto"]
picks_fp_confronto = picks_stats["picks_fp_confronto"]

bans_stats = processar_bans(tabela_liga_ativa)

ban_fase1_fp = bans_stats["ban_fase1_fp"]
ban_fase1_lp = bans_stats["ban_fase1_lp"]
total_fp = bans_stats["total_fp"]
total_lp = bans_stats["total_lp"]
ban_contra_fp = bans_stats["ban_contra_fp"]
ban_contra_lp = bans_stats["ban_contra_lp"]
total_contra_fp = bans_stats["total_contra_fp"]
total_contra_lp = bans_stats["total_contra_lp"]
bans_vs_fp = bans_stats["bans_vs_fp"]
bans_vs_lp = bans_stats["bans_vs_lp"]
jogos_vs_fp = bans_stats["jogos_vs_fp"]
jogos_vs_lp = bans_stats["jogos_vs_lp"]

# %%
caminho_dados_draft = os.path.join(pasta_raiz, "modelos_treinados", "dados_draft.joblib")

if os.path.exists(caminho_dados_draft):
    print('\nCarregando "dados_draft.joblib" do disco...')

    dados_draft = joblib.load(caminho_dados_draft)

else:
    print(f'"dados_draft.joblib" não foi encontrado no disco. Calculando dados do draft...')

    import itertools

    dados_players_global = tabela_final[tabela_final["position"] != "team"]
    tabela_times_global = tabela_final[tabela_final["position"] == "team"]

    contagem_pares = {}
    contagem_exposicao = {}
    contagem_respostas = {}

    for (gameid, teamname), grupo in dados_players_global.groupby(["gameid", "teamname"]):
        champ = grupo["champion"].tolist()

        for i in range(len(champ)):
            for j in range(i + 1, len(champ)):
                par = tuple(sorted([champ[i], champ[j]]))
                contagem_pares[par] = contagem_pares.get(par, 0) + 1

    for gameid, jogo in dados_players_global.groupby("gameid"):
        times = jogo["teamname"].unique()

        if len(times) != 2:
            continue

        camp_t1 = jogo[jogo["teamname"] == times[0]]["champion"].tolist()
        camp_t2 = jogo[jogo["teamname"] == times[1]]["champion"].tolist()

        for picks_inimigo, picks_aliado in ([camp_t1, camp_t2], [camp_t2, camp_t1]):

            for inimigo in picks_inimigo:
                contagem_exposicao[inimigo] = contagem_exposicao.get(inimigo, 0) + 1

                for resposta in picks_aliado:
                    par = (inimigo, resposta)
                    contagem_respostas[par] = contagem_respostas.get(par, 0) + 1
        
    ban_fase2_por_pick = {}
    total_pick_fase2 = {}

    picks_por_time = dados_players_global.groupby(["gameid", "teamname"])["champion"].apply(list).to_dict()

    for gameid, jogo_team in tabela_times_global.groupby("gameid"):
        times = jogo_team["teamname"].unique()

        if len(times) != 2:
            continue

        for time in times:
            picks_time = picks_por_time.get((gameid, time), [])
            ban_fase2 = jogo_team[jogo_team["teamname"] == time][["ban4", "ban5"]].values.flatten().tolist()

            for pick in picks_time:
                total_pick_fase2[pick] = total_pick_fase2.get(pick, 0) + 1

                for ban in ban_fase2:
                    
                    if pd.notna(ban):
                        ban_fase2_por_pick[(pick, ban)] = ban_fase2_por_pick.get((pick, ban), 0) + 1

    matchup_vitorias = {}
    matchup_total = {}

    for game, jogo in dados_players_global.groupby("gameid"):
        times = jogo["teamname"].unique()

        if len(times) != 2:
            continue

        time_a, time_b = times[0], times[1]
        camp_a = jogo[jogo["teamname"] == time_a]
        camp_b = jogo[jogo["teamname"] == time_b]

        if camp_a.empty or camp_b.empty:
            continue

        champs_a = camp_a["champion"].tolist()
        champs_b = camp_b["champion"].tolist()
        result_a = camp_a["result"].iloc[0]

        for nome_a, nome_b in itertools.product(champs_a, champs_b):
            par_ab = (nome_a, nome_b)
            par_ba = (nome_b, nome_a)

            matchup_total[par_ab] = matchup_total.get(par_ab, 0) + 1
            matchup_total[par_ba] = matchup_total.get(par_ba, 0) + 1

            if result_a == 1:
                matchup_vitorias[par_ab] = matchup_vitorias.get(par_ab, 0) + 1
            else:
                matchup_vitorias[par_ba] = matchup_vitorias.get(par_ba, 0) + 1

    dados_draft = {
        "contagem_pares" : contagem_pares,
        "contagem_exposicao" : contagem_exposicao,
        "contagem_respostas" : contagem_respostas,
        "ban_fase2_por_pick" : ban_fase2_por_pick,
        "total_pick_fase2" : total_pick_fase2,
        "matchup_total" : matchup_total,
        "matchup_vitorias" : matchup_vitorias
    }

    joblib.dump(dados_draft, caminho_dados_draft)

    teste_dados_draft = joblib.load(caminho_dados_draft)

    assert(teste_dados_draft["contagem_pares"] == contagem_pares), 'Diferença em: "contagem_pares".'
    assert(teste_dados_draft["contagem_exposicao"] == contagem_exposicao), 'Diferença em: "contagem_exposicao".'
    assert(teste_dados_draft["contagem_respostas"] == contagem_respostas), 'Diferença em: "contagem_respostas".'
    assert(teste_dados_draft["ban_fase2_por_pick"] == ban_fase2_por_pick), 'Diferença em: "ban_fase2_por_pick".'
    assert(teste_dados_draft["total_pick_fase2"] == total_pick_fase2), 'Diferença em: "total_pick_fase2".'
    assert(teste_dados_draft["matchup_total"] == matchup_total), 'Diferença em: "matchup_total".'
    assert(teste_dados_draft["matchup_vitorias"] == matchup_vitorias), 'Diferença em: "matchup_vitorias".'

    print('\n\033[32mArquivo dados_draft.joblib gerado e validado em modelos_treinados!\033[m')

contagem_pares = dados_draft["contagem_pares"]
contagem_exposicao = dados_draft["contagem_exposicao"]
contagem_respostas = dados_draft["contagem_respostas"]
ban_fase2_por_pick = dados_draft["ban_fase2_por_pick"]
total_pick_fase2 = dados_draft["total_pick_fase2"]
matchup_total = dados_draft["matchup_total"]
matchup_vitorias = dados_draft["matchup_vitorias"]

# %%
import modelos_cache

limiar_flex = 0.10
minimo_exposicao = 3
limitar_ban_proprio = 0.03
patch_atual = int(tabela_final["patch_num"].max())


def gerar_Dna_Automatico(df_completo):
    contagem = df_completo.groupby(["champion", "position"]).size().unstack(fill_value = 0)
    dna_percentual = contagem.div(contagem.sum(axis = 1), axis = 0)
    return dna_percentual.to_dict(orient = "index")


dna_campeoes = gerar_Dna_Automatico(tabela_final)


def get_posicoes_ocupadas(lista_picks, dna_campeoes):
    candidatos = {}
    
    for pick in lista_picks:
        if pick not in dna_campeoes:
            continue

        for rota, pct in dna_campeoes[pick].items():
            if pct > limiar_flex:
                candidatos.setdefault(rota, []).append((pick, pct))

    rotas_ocupadas = {}
    picks_alocados = set()

    # Garantido não flex

    ordem = sorted(
        candidatos.items(),
        key = lambda x: max(p for _, p in x[1]),
        reverse = True
    )
    
    # Escolha de melhor pick por rota

    for rota, lista in ordem:
        list_ord = sorted(lista, key = lambda x: x[1], reverse = True)

        for camp, pct in list_ord:

            if camp not in picks_alocados:
                rotas_ocupadas[rota] = camp
                picks_alocados.add(camp)
                break

    return list(rotas_ocupadas.keys())    


def get_winrate(camp, contra):
    total = matchup_total.get((camp, contra), 0)
    if total < minimo_exposicao:
        return 0.5
    return matchup_vitorias.get((camp, contra), 0) / total


def get_threshold_counter(total_jogos):
    if total_jogos < 10:
        return 1.0
    elif total_jogos < 30:
        return 0.68
    elif total_jogos < 50:
        return 0.63
    elif total_jogos < 100:
        return 0.58
    else:
        return 0.55
    

def get_forca_counter(camp, meu_pick):
    total = matchup_total.get((camp, meu_pick), 0)
    threshold = get_threshold_counter(total)
    winrate = get_winrate(camp, meu_pick)

    if winrate <= threshold:
        return 0.0
    
    return min((winrate - threshold) / (1.0 -threshold), 1.0)


def preparar_bans(bansTime1, bansTime2, time_tem_p1_no_jogo):

    bans_time1 = list(bansTime1)
    bans_time2 = list(bansTime2)

    if time_tem_p1_no_jogo:
        bans_fp = bans_time1
        bans_lp = bans_time2
    else:
        bans_fp = bans_time2
        bans_lp = bans_time1

    ordem_banimentos = []

    for i in range(3):
        if i < len(bans_fp):
            ordem_banimentos.append(bans_fp[i])
        if i < len(bans_lp):
            ordem_banimentos.append(bans_lp[i])

    for i in range(3, 5):
        if i < len(bans_lp):
            ordem_banimentos.append(bans_lp[i])
        if i < len(bans_fp):
            ordem_banimentos.append(bans_fp[i])

    if len(ordem_banimentos) > 0:
        num_bans = cod_camp.transform(ordem_banimentos).tolist()
    else:
        num_bans = []

    while len(num_bans) < 10:
        num_bans.append(-1)

    return num_bans[:10]


def nota_contexto(nota_geral, nota_confronto_adv, qtd_jogos, k_credibilidade = 3, teto_confianca = 0.45):

    if qtd_jogos <= 0:
        return nota_geral

    confianca = qtd_jogos / (qtd_jogos + k_credibilidade)
    confianca = min(confianca, teto_confianca)

    nota_final = nota_geral * (1 - confianca) + nota_confronto_adv * confianca

    return nota_final


def sugeriPicks(time1, bansTime1, picksTime1, time2, bansTime2, picksTime2, picks_totais, time_tem_p1_no_jogo, retornar_lista = False, modelo = None):

    from random import choices

    global prioridade_historica, prioridade_p1, ban_contra_fp, ban_contra_lp, total_contra_fp, total_contra_lp, total_fp_confronto, picks_fp_confronto, jogos_contra_adv, picks_confronto

    if modelo is not None:
        modelo_usado = modelo
    else:
        modelo_usado = modelos_cache.buscar_modelos("GERAL")  # modelo_ia

    proibidos = list(bansTime1) + list(bansTime2) + list(picks_totais)

    rotas_ocupadas = get_posicoes_ocupadas(picksTime1, dna_campeoes)
    rotas_vagas = [r for r in ["top", "jng", "mid", "bot", "sup"] if r not in rotas_ocupadas]

    if not rotas_vagas:
        return "Time Completo"
    
    pool_do_time = tabela_liga_ativa[tabela_liga_ativa["teamname"] == time1]

    if time1 in prioridade_p1.index:
        serie_p1 = prioridade_p1.loc[time1]
        pool_p1_valido = set(serie_p1[serie_p1 > 0].index)

    else:
        pool_p1_valido = set()

    todos_camps_time = set(pool_do_time["champion"].unique())

    e_primeiro_pick_time = len(picksTime1) == 0
    id_time = cod_time.transform([time1])[0]
    id_opp = cod_time.transform([time2])[0]
    valor_posse_p1 = 1.0 if time_tem_p1_no_jogo else 0.0

    picks_time1_nums = cod_camp.transform(picksTime1).tolist() if len(picksTime1) > 0 else []

    while len(picks_time1_nums) < 4:
        picks_time1_nums.append(-1)
    
    picks_time2_nums = cod_camp.transform(picksTime2).tolist() if len(picksTime2) > 0 else []

    while len(picks_time2_nums) < 5:
        picks_time2_nums.append(-1)

    n_picks_feitos = len(picksTime1) + len(picksTime2)
    num_bans = preparar_bans(bansTime1, bansTime2, time_tem_p1_no_jogo)

    t = min(n_picks_feitos / 9.0, 1.0)

    peso_hist = 0.30
    peso_ia = 0.25
    peso_oportunidade = max(0.20 - (t * 0.20), 0.0)
    peso_sinergia = 0.08 + (t * 0.14)
    peso_counter = 0.17 + (t * 0.06)

    score_candidatos = []

    historico_contra = ban_contra_lp if time_tem_p1_no_jogo else ban_contra_fp
    total_contra_ctx = total_contra_lp if time_tem_p1_no_jogo else total_contra_fp

    for rota in rotas_vagas:
        id_rota = cod_pos.transform([rota])[0]
        camp_confort_time = set(pool_do_time[pool_do_time["position"] == rota]["champion"].unique())

        cenario = pd.DataFrame([[
            id_time, id_opp, id_rota, valor_posse_p1,
            n_picks_feitos, patch_atual,
            *picks_time1_nums, *picks_time2_nums,
            *num_bans
        ]], columns = colunas_treino)

        probs = modelo_usado.predict_proba(cenario)[0]
        campeoes_modelo = cod_camp.inverse_transform(modelo_usado.classes_)
        raking_ia = pd.Series(probs, index = campeoes_modelo)

        for camp in cod_camp.classes_:

            if camp in proibidos:
                continue
            if camp not in dna_campeoes:
                continue
            if dna_campeoes[camp].get(rota, 0) < limiar_flex:
                continue
            
            prio_ia = raking_ia.get(camp, 0)
            bonus_sinergia = 0
            bonus_counter= 0
            prio_hist = 0

            if camp in camp_confort_time:
                fator_pool = 1.00
            elif camp in todos_camps_time:
                fator_pool = 0.15
            else:
                fator_pool = 0.02          

            bonus_oportunidade = 0

            total_jogos_contra = total_contra_ctx.get(time1, 1)
            contagem_bans_contra = historico_contra.get((time1, camp), 0) + 1

            if total_jogos_contra > minimo_exposicao:
                taxa_ameaca = contagem_bans_contra / total_jogos_contra

                if taxa_ameaca > 0.30:
                    decaida = max(1.0 - (n_picks_feitos * 0.25), 0)
                    bonus_oportunidade = (taxa_ameaca * 0.40) * decaida

            if e_primeiro_pick_time and time_tem_p1_no_jogo:  
                if camp not in pool_p1_valido:
                    continue

                champs_geral_p1 = prioridade_p1.loc[time1].get(camp, 0)
                champ_confronto_p1 = picks_fp_confronto.get((time1, time2), {}).get(camp, 0)
                confronto_fp_total = total_fp_confronto.get((time1, time2), 0)
                prio_time = nota_contexto(champs_geral_p1, champ_confronto_p1, confronto_fp_total)
                prio_hist = prio_time

                score = ((prio_time * peso_hist) + (prio_ia * peso_ia) + (bonus_oportunidade * peso_oportunidade))

            else:
                prio_time = 0

                if time1 in prioridade_historica.index:
                    champs_geral = prioridade_historica.loc[time1].get(camp, 0)
                    champ_confronto = picks_confronto.get((time1, time2), {}).get(camp, 0)
                    qtd_jogos = jogos_contra_adv.get((time1, time2), 0)
                    prio_time = nota_contexto(champs_geral, champ_confronto, qtd_jogos)
                
                prio_hist = prio_time * fator_pool
                bonus_sinergia = 0
                bonus_counter = 0

                if picksTime1:
                    lista_sinergia = []

                    for aliado in picksTime1:
                        par = tuple(sorted([camp, aliado]))
                        n_juntos = contagem_pares.get(par, 0)
                        n_aliado = contagem_exposicao.get(aliado, 0)
                        
                        if n_aliado >= minimo_exposicao:
                            lista_sinergia.append(n_juntos / n_aliado)
                    
                    if lista_sinergia:
                        media_sinergia = sum(lista_sinergia) / len(lista_sinergia)
                        max_sinergia = max(lista_sinergia)
                        bonus_sinergia = (media_sinergia * 0.6) + (max_sinergia * 0.4)

                        bonus_dupla = 0.04 if max_sinergia >= 0.25 else 0
                        bonus_sinergia = min(bonus_sinergia + bonus_dupla, 0.30)
                    
                    bonus_sinergia *= fator_pool

                if picksTime2:
                    lista_forcas = []
                    lista_punicao = []
                    lista_resposta = []
                    lista_puni_resp = []

                    rotas_ocupadas_adv = get_posicoes_ocupadas(picksTime2, dna_campeoes)
                    adv_lane = None

                    if rota in rotas_ocupadas_adv:
                        maior_pct = -1

                        for inimigo in picksTime2:
                            if inimigo in dna_campeoes:
                                pct = dna_campeoes[inimigo].get(rota, 0)

                                if pct > limiar_flex and pct > maior_pct:
                                    maior_pct = pct
                                    adv_lane = inimigo

                    forca_lane = 0
                    punicao_lane = 0            

                    for inimigo in picksTime2:
                        
                        forca = get_forca_counter(camp, inimigo)
                        punicao = get_forca_counter(inimigo, camp)

                        if inimigo == adv_lane:
                            forca_lane = forca
                            punicao_lane = punicao
                        else:
                            lista_forcas.append(forca)
                            lista_punicao.append(punicao)

                        n_resposta = contagem_respostas.get((inimigo, camp), 0)
                        n_inimigo = contagem_exposicao.get(inimigo, 0)

                        lista_resposta.append(n_resposta / n_inimigo if n_inimigo > minimo_exposicao else 0)

                        n_punicao = contagem_respostas.get((camp, inimigo), 0)
                        n_team = contagem_exposicao.get(camp, 0)

                        lista_puni_resp.append(n_punicao / n_team if n_team > minimo_exposicao else 0)

                    if len(lista_forcas) > 0:
                        avg_forca = sum(lista_forcas) / len(lista_forcas)
                    else:
                        avg_forca = 0

                    if len(lista_punicao) > 0:
                        avg_punicao = sum(lista_punicao) / len(lista_punicao)
                    else:
                        avg_punicao = 0

                    if adv_lane:
                        balanco_positivo = (forca_lane * 0.6) + (avg_forca * 0.4)
                        balanco_negativo = (punicao_lane * 0.6) + (avg_punicao * 0.4)
                    else:
                        if len(lista_forcas) > 0:
                            max_forca = max(lista_forcas)
                        else:
                            max_forca = 0
                        if len(lista_punicao) > 0:
                            max_punicao = max(lista_punicao)
                        else:
                            max_punicao = 0
                        
                        balanco_positivo = (avg_forca * 0.6) + (max_forca * 0.4)
                        balanco_negativo = (avg_punicao * 0.6) + (max_punicao * 0.4)

                    score_matchup = min(balanco_positivo, 0.20) - min(balanco_negativo, 0.25)
                    
                    if len(lista_resposta) > 0:
                        resp_pos = sum(lista_resposta) / len(lista_resposta)
                    else:
                        resp_pos = 0
                    if len(lista_puni_resp) > 0:
                        resp_neg = sum(lista_puni_resp) / len(lista_puni_resp)
                    else:
                        resp_neg = 0
                    
                    score_resposta = max(min((resp_pos - resp_neg) * 2.5, 0.15), - 0.15)

                    bonus_counter_bruto = (score_matchup * 0.7) + (score_resposta * 0.3)
                    bonus_counter = bonus_counter_bruto * fator_pool

                score = (
                    (prio_hist * peso_hist) + (prio_ia * peso_ia) + (bonus_sinergia * peso_sinergia) +
                    (bonus_counter * peso_counter) + (bonus_oportunidade * peso_oportunidade)
                )

            score_candidatos.append((camp, score))

    if score_candidatos:
        score_candidatos.sort(key = lambda x: x[1], reverse = True)
        top3_picks = [camp for camp, score in score_candidatos[:3]]
        pesos = [score for camp, score in score_candidatos[:3]]

        if retornar_lista:
            return top3_picks
        else:
            return choices(top3_picks, weights = pesos, k = 1)[0]

    camps_disponiveis = [
        c for c in todos_camps_time if c not in proibidos and c in dna_campeoes
    ]

    if camps_disponiveis:
        return max(
            camps_disponiveis,
            key = lambda c: prioridade_historica.loc[time1].get(c, 0)
            if time1 in prioridade_historica.index else 0
        )

    return "Fallback"
    
         
def sugeriBans(time1, bansTime1, picksTime1, time2, bansTime2, picksTime2, picks, time_tem_p1_no_jogo, modelo = None):

    global prioridade_historica, ban_fase1_fp, ban_fase1_lp, total_fp, total_lp, ban_contra_fp, ban_contra_lp, total_contra_fp, total_contra_lp, bans_vs_fp, bans_vs_lp, jogos_vs_fp, jogos_vs_lp

    if modelo is not None:
        modelo_usado = modelo
    else:
        #print('\033[33m[Aviso] Nenhum modelo foi passado. Usando o modelo "Geral" do cache\033[m')
        modelo_usado = modelos_cache.buscar_modelos("GERAL") # modelo_ia

    proibidos = list(bansTime1 + bansTime2 + picks)

    rotas_vagas_adv = [r for r in ["top", "jng", "mid", "bot", "sup"] if r not in get_posicoes_ocupadas(picksTime2, dna_campeoes)]

    if not rotas_vagas_adv:
        return df_meta[~df_meta.index.isin(proibidos)].sort_values(by = "ban_rate", ascending = False).index[0]

    id_inimigo = cod_time.transform([time2])[0]
    id_aliado = cod_time.transform([time1])[0]
    posse_p1_adv = 0.0 if time_tem_p1_no_jogo else 1.0

    picks_time2_nums = cod_camp.transform(picksTime2).tolist() if len(picksTime2) > 0 else []

    while len(picks_time2_nums) < 4:
        picks_time2_nums.append(-1)
    
    picks_time1_nums = cod_camp.transform(picksTime1).tolist() if len(picksTime1) > 0 else []

    while len(picks_time1_nums) < 5:
        picks_time1_nums.append(-1)
    
    historico_aliado = ban_fase1_fp if time_tem_p1_no_jogo else ban_fase1_lp
    total_aliado_ctx = total_fp if time_tem_p1_no_jogo else total_lp
    bans_champ_vs = bans_vs_fp if time_tem_p1_no_jogo else bans_vs_lp
    bans_vs_adv = jogos_vs_fp if time_tem_p1_no_jogo else jogos_vs_lp

    historico_contra = ban_contra_lp if time_tem_p1_no_jogo else ban_contra_fp
    total_contra_ctx = total_contra_lp if time_tem_p1_no_jogo else total_contra_fp

    # Bans Fase 2

    score_ban_fase2 = {}

    if len(picksTime1) >= 3:

        for pick in picksTime1:
            total = total_pick_fase2.get(pick, 0)
            
            if total < minimo_exposicao:
                continue

            bans_do_pick = {
                ban: count for(p, ban), count in ban_fase2_por_pick.items()
                if p == pick
            }

            for ban, count in bans_do_pick.items():
                if ban in picksTime1:
                    continue

                taxa = count / total
                score_ban_fase2[ban] = score_ban_fase2.get(ban, 0) + taxa / len(picksTime1)
    
    # Counter 

    score_counter = {}

    if picksTime1:

        for camp in cod_camp.classes_:
            forca_total = 0      

            for meu_pick in picksTime1:
                forca_total += get_forca_counter(camp, meu_pick)

            score_counter[camp] = min(forca_total / len(picksTime1), 0.25)

    n_picks_feitos = len(picksTime2) + len(picksTime1)
    num_bans = preparar_bans(bansTime1, bansTime2, time_tem_p1_no_jogo)
    
    melhor_ban = None
    maior_perigo = -1

    for rota in rotas_vagas_adv:
        id_rota = cod_pos.transform([rota])[0]

        cenario_inimigo = pd.DataFrame([[
            id_inimigo, id_aliado, id_rota, posse_p1_adv,
            n_picks_feitos, patch_atual,
            *picks_time2_nums, *picks_time1_nums,
            *num_bans
        ]], columns = colunas_treino)

        probs = modelo_usado.predict_proba(cenario_inimigo)[0]
        campeoes_modelo = cod_camp.inverse_transform(modelo_usado.classes_)
        ranking_inimigo = pd.Series(probs, index = campeoes_modelo)

        for camp in cod_camp.classes_:

            if camp in proibidos or camp not in dna_campeoes:
                continue
            
            if dna_campeoes[camp].get(rota, 0) < limiar_flex:
                continue

            prio_inimigo = 0
            prio_aliado = 0

            if time2 in prioridade_historica.index:
                prio_inimigo = prioridade_historica.loc[time2].get(camp, 0)
            
            if time1 in prioridade_historica.index:
                prio_aliado = prioridade_historica.loc[time1].get(camp, 0)
                
            if prio_aliado > limitar_ban_proprio:
                continue
            
            pref_ia = ranking_inimigo.get(camp, 0)
            meta_ban = (df_meta.loc[camp, "ban_rate"] / 100) if camp in df_meta.index else 0

            total_jogos_aliado = total_aliado_ctx.get(time1, 1)
            contagem_bans = historico_aliado.get((time1, camp), 0)
            bonus_historico_aliado = 0

            if total_jogos_aliado > minimo_exposicao:
                nota_geral_ban = contagem_bans / total_jogos_aliado
                nota_bans_champ = bans_champ_vs.get((time1, time2), {}).get(camp, 0)
                bans_confronto = bans_vs_adv.get((time1, time2), 0) 
                bonus_historico_aliado = min(nota_contexto(nota_geral_ban, nota_bans_champ, bans_confronto), 0.25)
            
            bonus_ameaca_oculta = 0

            total_jogos_contra = total_contra_ctx.get(time2, 1)
            contagem_bans_contra = historico_contra.get((time2, camp), 0)

            if total_jogos_contra >= minimo_exposicao:
                bonus_ameaca_oculta = min(contagem_bans_contra / total_jogos_contra, 0.25)

            bonus_combo_adv = 0

            if picksTime2:

                for pick_adv in picksTime2:
                    par = tuple(sorted([camp, pick_adv]))
                    n_juntos = contagem_pares.get(par, 0)
                    n_pick = contagem_exposicao.get(pick_adv, 0)

                    if n_pick >= minimo_exposicao:
                        bonus_combo_adv += n_juntos / n_pick

                bonus_combo_adv = min(bonus_combo_adv / len(picksTime2), 0.25)

            bonus_counter_aliado = score_counter.get(camp, 0)

            bonus_fase2 = 0

            if len(picksTime1) >= 3:
                bonus_fase2 = min(score_ban_fase2.get(camp, 0), 0.25)
            
            if len(picksTime1) >= 3:

                score_perigo = (
                    (prio_inimigo * 0.32) + (pref_ia * 0.18) + (meta_ban * 0.05) +
                    (bonus_combo_adv * 0.12) + (bonus_counter_aliado * 0.14) + 
                    (bonus_fase2 * 0.15) + (bonus_ameaca_oculta * 0.02) 
                )

            else:

                peso_inimigo = 0.35 if not time_tem_p1_no_jogo else 0.30
                peso_historico = 0.15 if not time_tem_p1_no_jogo else 0.20

                score_perigo = (
                    (prio_inimigo * peso_inimigo) + (pref_ia * 0.15) + (meta_ban * 0.10) +
                    (bonus_historico_aliado * peso_historico) + (bonus_ameaca_oculta * 0.30)
                    
                )

            if score_perigo > maior_perigo:
                maior_perigo = score_perigo
                melhor_ban = camp

    if melhor_ban:
        return melhor_ban
    
    return df_meta[~df_meta.index.isin(proibidos)].sort_values(by = "ban_rate", ascending = False).index[0]


# %%
def ordemPicksBans(timeFP, timeLP, jogos, picks = None):

  if picks is None:
    picks = []

  picksFP, bansFP = [], []
  picksLP, bansLP = [], []

  bans = []

  for _ in range(3):
    ban = sugeriBans(timeFP, bansFP, picksFP, timeLP, bansLP, picksLP, picks, time_tem_p1_no_jogo = True)
    bans.append(ban)
    bansFP.append(ban)

    ban = sugeriBans(timeLP, bansLP, picksLP, timeFP, bansFP, picksFP, picks, time_tem_p1_no_jogo = False)
    bans.append(ban)
    bansLP.append(ban)

  ordem = [timeFP, timeLP, timeLP, timeFP, timeFP, timeLP]

  for time_atual in ordem:
    if time_atual == timeFP:
      champ = sugeriPicks(timeFP, bansFP, picksFP, timeLP, bansLP, picksLP, picks, time_tem_p1_no_jogo = True)
      picksFP.append(champ)
    else:
      champ = sugeriPicks(timeLP, bansLP, picksLP, timeFP, bansFP, picksFP, picks, time_tem_p1_no_jogo = False)
      picksLP.append(champ)

    picks.append(champ)

  for _ in range(2):
    ban = sugeriBans(timeLP, bansLP, picksLP, timeFP, bansFP, picksFP, picks, time_tem_p1_no_jogo = False)
    bans.append(ban)
    bansLP.append(ban)

    ban = sugeriBans(timeFP, bansFP, picksFP, timeLP, bansLP, picksLP, picks, time_tem_p1_no_jogo = True)
    bans.append(ban)
    bansFP.append(ban)

  ordem2 = [timeLP, timeFP, timeFP, timeLP]

  for time_atual in ordem2:

    if time_atual == timeFP:
      champ = sugeriPicks(timeFP, bansFP, picksFP, timeLP, bansLP, picksLP, picks, time_tem_p1_no_jogo = True)
      picksFP.append(champ)
    else:
      champ = sugeriPicks(timeLP, bansLP, picksLP, timeFP, bansFP, picksFP, picks, time_tem_p1_no_jogo = False)
      picksLP.append(champ)

    picks.append(champ)

  jogo_atual = [picksFP, bansFP, picksLP, bansLP]

  if jogos > 1:
    return [jogo_atual] + ordemPicksBans(timeLP, timeFP, jogos-1, picks)
  
  return [jogo_atual]

# %%
times_liga_ativa = tabela_liga_ativa["teamname"].unique()

print(times_liga_ativa)

# %%
time1 = "FURIA"
time2 = "RED Canids"

historico_fearless = []

resultado_serie = ordemPicksBans(time1, time2, 1)

for i, jogo in enumerate(resultado_serie):
    pFP, bFP, pLP, bLP = jogo

    picks_do_jogo = pFP + pLP
    historico_fearless.extend(picks_do_jogo)

    # Quem era FP nesse jogo? Alterna a cada jogo
    if i % 2 == 0:
        nome_fp, nome_lp = time1, time2
    else:
        nome_fp, nome_lp = time2, time1

    print(f"{'#'*2}  JOGO {i + 1}  {'#'*1}")

    print(f"🚫 BANS: {nome_fp}: {', '.join(bFP)} | {nome_lp}: {', '.join(bLP)}")

    print(f"{'='*16} ⚔️  COMPOSIÇÕES FINAIS ⚔️  {'='*16}")
    print(f"{nome_fp:<28} | {nome_lp:>28}")
    print("-" * 60)
    for j in range(5):
        c1 = pFP[j] if j < len(pFP) else "---"
        c2 = pLP[j] if j < len(pLP) else "---"
        print(f"P{j+1}: {c1:<24} | P{j+1}: {c2:>24}")
    print("-" * 60)

    if i > 0:
        usados_antes = historico_fearless[:-10]
        print(f"⚠️  FEARLESS (Já usados na série):")
        print(f"[{', '.join(usados_antes)}]")
        print("-" * 60)


