from dataclasses import dataclass
from apps.results.score_dto import ScoreDTO
from apps.tournaments.dto.match_dto import MatchDTO
from apps.users.user_dto import UserDTO


@dataclass
class DisputeDTO:
    id: int
    reason: str
    status: str
    resolution_notes: str
    final_score: ScoreDTO
    match: MatchDTO
    raised_by: UserDTO
    resolved_by: UserDTO
