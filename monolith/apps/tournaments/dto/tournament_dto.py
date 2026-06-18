from dataclasses import dataclass
from apps.users.user_dto import UserDTO


@dataclass
class TournamentDTO:
    id: int
    name: str
    description: str
    start_date: str
    end_date: str
    location: str
    status: str
    players: list[UserDTO]
    referees: list[UserDTO]
