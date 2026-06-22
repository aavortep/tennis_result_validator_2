from dataclasses import dataclass
from .score_dto import ScoreDTO


@dataclass
class DisputeDTO:
    id: int
    reason: str
    status: str
    resolution_notes: str
    final_score: ScoreDTO
    match: int
    raised_by: int
    resolved_by: int
