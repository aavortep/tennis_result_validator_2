from dataclasses import dataclass
from .tournament_dto import TournamentDTO


@dataclass
class MatchDTO:
    id: int
    scheduled_time: str
    court: str
    round: str
    status: str
    player1: int
    player2: int
    referee: int
    tournament: TournamentDTO
    winner: int
