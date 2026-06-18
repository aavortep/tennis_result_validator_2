from dataclasses import dataclass
from apps.users.user_dto import UserDTO
from apps.tournaments.dto.match_dto import MatchDTO


@dataclass
class ScoreDTO:
    id: int
    is_confirmed: bool
    confirmed_by: UserDTO
    match: MatchDTO
    submitted_by: UserDTO
    winner: UserDTO
