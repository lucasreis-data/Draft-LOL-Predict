from pydantic import BaseModel

class DraftRequest(BaseModel):
    liga: str = "CBLOL"
    time_player: str
    bans_player: list[str] = []
    picks_player: list[str] = []
    time_ia: str
    bans_ia: list[str] = []
    picks_ia: list[str] = []
    fearless: list[str] = []
    is_first_pick: bool
    fase: str