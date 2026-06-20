from dataclasses import dataclass
from apps.users.user_dto import UserDTO


@dataclass
class GlobalRankingDTO:
    id: int
    total_points: int
    total_wins: int
    total_losses: int
    tournaments_played: int
    tournaments_won: int
    position: int
    player: UserDTO
