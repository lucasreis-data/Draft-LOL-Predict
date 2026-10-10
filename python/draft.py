from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints

# Limites generosos (so barram payload absurdo; o uso normal fica muito abaixo deles).
Nome = Annotated[str, StringConstraints(max_length = 100)]
ListaCampeoes = Annotated[list[Nome], Field(max_length = 50)]
ListaFearless = Annotated[list[Nome], Field(max_length = 400)]

class DraftRequest(BaseModel):
    liga: Annotated[str, StringConstraints(max_length = 20)] = "CBLOL"
    jogador_atual: Annotated[str, StringConstraints(max_length = 10)] = "PLAYER"
    time_player: Nome
    bans_player: ListaCampeoes = []
    picks_player: ListaCampeoes = []
    time_ia: Nome
    bans_ia: ListaCampeoes = []
    picks_ia: ListaCampeoes = []
    fearless: ListaFearless = []
    is_first_pick: bool
    fase: Annotated[str, StringConstraints(max_length = 20)]