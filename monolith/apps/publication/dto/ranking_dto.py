from dataclasses import dataclass
from apps.users.user_dto import UserDTO
from apps.tournaments.dto.tournament_dto import TournamentDTO


@dataclass
class RankingDTO:
    id: int
    points: int
    wins: int
    losses: int
    sets_won: int
    sets_lost: int
    games_won: int
    games_lost: int
    position: int
    player: UserDTO
    tournament: TournamentDTO
