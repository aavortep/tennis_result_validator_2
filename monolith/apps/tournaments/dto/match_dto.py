from dataclasses import dataclass
from apps.users.user_dto import UserDTO
from .tournament_dto import TournamentDTO


@dataclass
class MatchDTO:
    id: int
    scheduled_time: str
    court: str
    round: str
    status: str
    player1: UserDTO
    player2: UserDTO
    referee: UserDTO
    tournament: TournamentDTO
    winner: UserDTO
